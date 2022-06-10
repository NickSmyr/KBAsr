import os
import re
from abc import ABC, abstractmethod
from collections import defaultdict

import numpy as np
from typing import Union, List

from torch.utils.data import Dataset, default_collate, DataLoader
from tqdm.auto import tqdm

import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, Wav2Vec2ProcessorWithLM

from utils.main import convert_to_wav, ConversionError, change_sample_rate
import os



ASR_MODELS = [
    "KBLab/wav2vec2-large-voxrex-swedish", # Regular Swe-Wav2Vec no LM
    "birgermoell/lm-swedish", # Birgers Wav2Vec with LM
    "viktor-enzell/wav2vec2-large-voxrex-swedish-4gram" # Wav2Vec with LM
]

BATCH_SIZE=50

def asr_model_factory(model_id : str, device, batch_size):
    if model_id == ASR_MODELS[0]:
        return TranscriberNoLM(model_id, device, batch_size)
    else:
        return TranscriberLM(model_id, device, batch_size)

def transcribe_from_dir_path(dir, output_file, device, model_id, batch_size):
    """
    Transcribe a directory containing wav files ( does not recurse).

    Filenames must be labeled file_xxx.wav

    """
    filenames2transcriptions = {}

    transcriber = FileTranscriber(asr_model_factory(model_id, device, batch_size))
    filenames = []
    for file in tqdm(list(os.listdir(dir))):
        filename = file
        if filename.endswith(".wav"):
            complete_filename = os.path.join(dir, filename)
            filenames.append(complete_filename)

    transcriptions = transcriber.transcribe(filenames)

    ret_lines = []
    for k, v in zip(filenames, transcriptions):
        ret_lines.append(k + "\t" + v + "\n")

    pat = re.compile("file_(\d+)\.wav")
    lines = sorted(ret_lines, key=lambda x: int(pat.search(x).groups()[0]))

    with open(output_file, "w") as f:
        f.writelines(lines)


class FileTranscriber(ABC):
    """File Transcriber (Strategy pattern)"""
    def __init__(self, transcriber : "WaveformTranscriber"):
        self.transcriber = transcriber
        self.sample_rate = transcriber.sample_rate

    def _wavify_and_resample(self, audio_paths : Union[str, List[str]]) -> torch.Tensor:
        """
        Convert to wav format and resample to the transcribers accepted sample rate
        """
        audio_paths = [audio_paths] if not isinstance(audio_paths, list) \
            else audio_paths
        converted = False
        waveforms = []
        for audio_path in audio_paths:
            if audio_path[-4:] != ".wav":
                try:
                    audio_path = convert_to_wav(audio_path)
                    converted = True
                except:
                    raise ConversionError(f"Could not convert {audio_path} to wav")

            waveform, sample_rate = torchaudio.load(audio_path)
            waveform = np.array(waveform)[0]
            if sample_rate != self.sample_rate:
                # resample to 16000 Hz
                waveform = change_sample_rate(audio_path)

            if converted:
                os.remove(audio_path)

            waveforms.append(waveform)

        return waveforms[0] if len(waveforms) ==1 else waveforms

    def transcribe(self, audiopaths : Union[str, List[str]]):
        waveforms = self._wavify_and_resample(audiopaths)
        return self.transcriber.transcribe(waveforms)

class WaveformTranscriber(ABC):
    def __init__(self, huggingface_model, huggingface_processor, sample_rate, device,
                 batch_size):
        self.model = huggingface_model
        self.processor = huggingface_processor
        self.sample_rate = sample_rate
        self.device = device
        self.batch_size = batch_size

    @abstractmethod
    def transcribe(self, waveforms: Union[np.ndarray, List[np.ndarray]]) -> Union[
        str, List[str]]:
        pass

class TranscriberNoLM(WaveformTranscriber):
    def __init__(self, huggingface_id : str, device, batch_size):
        super(TranscriberNoLM, self).__init__(
            huggingface_model=Wav2Vec2ForCTC.from_pretrained(huggingface_id).to(device),
            huggingface_processor=Wav2Vec2Processor.from_pretrained(huggingface_id),
            sample_rate=16000,
            device=device,
            batch_size=batch_size
        )
        self.model_id = huggingface_id

    def transcribe(self, waveforms: Union[np.ndarray, List[np.ndarray]]) -> Union[
        str, List[str]]:

        inputs = self.processor(waveforms, sampling_rate=self.sample_rate,
                                   return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            logits = batched_hugging_face_inference(self.batch_size, inputs, self.model)

        pred_ids = torch.argmax(logits, dim=-1)
        transcriptions = self.processor.batch_decode(pred_ids)
        return transcriptions[0] if len(transcriptions) == 1 else transcriptions


class TranscriberLM(WaveformTranscriber):
    def __init__(self, huggingface_id: str, device, batch_size):
        super(TranscriberLM, self).__init__(
            huggingface_model=Wav2Vec2ForCTC.from_pretrained(huggingface_id).to(device),
            huggingface_processor=Wav2Vec2ProcessorWithLM.from_pretrained(huggingface_id),
            sample_rate=16000,
            device=device,
            batch_size=batch_size
        )
        self.model_id = huggingface_id

    def transcribe(self, waveforms: Union[np.ndarray, List[np.ndarray]]) -> Union[
        str, List[str]]:

        inputs = self.processor(waveforms, sampling_rate=self.sample_rate,
                                return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            logits = batched_hugging_face_inference(self.batch_size, inputs, self.model,
                                                    True if self.device=="cuda" else
                                                    False)

        transcriptions = self.processor.batch_decode(logits.cpu().numpy()).text
        transcriptions = [x.lower() for x in transcriptions]
        return transcriptions[0] if len(transcriptions) == 1 else transcriptions



def batched_hugging_face_inference(batch_size, inputs, model, pin_memory):
    """
    Class that makes an inference happen batched for hugging face models (inputs are
    dicts)
    """
    dataloader = DataLoader(HuggingFaceInferenceDataset(inputs),
                                     batch_size=batch_size,
                                     collate_fn=huggingface_collate_fn,
                                     pin_memory=pin_memory)
    outputs = []
    for batch in tqdm(dataloader):
        curr_out = model(**batch).logits
        outputs.extend(curr_out)

    return outputs

class HuggingFaceInferenceDataset(Dataset):
    """
    Converts the outputs of a huggingface processor to a torch Dataset
    """
    def __init__(self, inputs):
        self.inputs = inputs

    def __getitem__(self, item):
        return { k:v for k,v in self.inputs.items()}

    def __len__(self):
        return len(self.inputs[list(self.inputs.keys())[0]])

def huggingface_collate_fn(data : list):
    lists = defaultdict(lambda : [])
    for example in data:
        for k,v in example.items():
            lists[k].append(v)

    return { k : default_collate(v) for k,v in lists.items()}


