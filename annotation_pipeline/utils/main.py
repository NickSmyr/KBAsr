import re
import librosa
import torch
import torchaudio

from tqdm.auto import tqdm
import os

from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

import soundfile as sf

language_dict = {
    "Swedish": "KBLab/wav2vec2-large-voxrex-swedish",
    "English": "jonatasgrosman/wav2vec2-large-xlsr-53-english",
    "Russian": "jonatasgrosman/wav2vec2-large-xlsr-53-russian",
    "Spanish": "facebook/wav2vec2-large-xlsr-53-spanish",
    "French": "facebook/wav2vec2-large-xlsr-53-french",
    "Persian": "m3hrdadfi/wav2vec2-large-xlsr-persian",
    "Dutch": "facebook/wav2vec2-large-xlsr-53-dutch",
    "Portugese": "facebook/wav2vec2-large-xlsr-53-portuguese",
    "Chinese": "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
    "German": "jonatasgrosman/wav2vec2-large-xlsr-53-german",
    "Greek": "lighteternal/wav2vec2-large-xlsr-53-greek",
    "Hindi": "theainerd/Wav2Vec2-large-xlsr-hindi",
    "Italian": "jonatasgrosman/wav2vec2-large-xlsr-53-italian",
    "Turkish": "cahya/wav2vec2-base-turkish-artificial-cv",
    "Vietnamese": "leduytan93/Fine-Tune-XLSR-Wav2Vec2-Speech2Text-Vietnamese",
    "Catalan": "ccoreilly/wav2vec2-large-100k-voxpopuli-catala",
    "Japanese": "vumichien/wav2vec2-large-xlsr-japanese-hiragana",
    "Tamil": "vumichien/wav2vec2-large-xlsr-japanese-hiragana",
    "Indonesian": "indonesian-nlp/wav2vec2-large-xlsr-indonesian",
    "Dhivevi": "shahukareem/wav2vec2-large-xlsr-53-dhivehi",
    "Polish": "jonatasgrosman/wav2vec2-large-xlsr-53-polish",
    "Thai": "sakares/wav2vec2-large-xlsr-thai-demo",
    "Hebrew": "imvladikon/wav2vec2-large-xlsr-53-hebrew",
    "Mongolian": "sammy786/wav2vec2-large-xlsr-mongolian",
    "Czech": "arampacha/wav2vec2-large-xlsr-czech",
    "Icelandic": "m3hrdadfi/wav2vec2-large-xlsr-icelandic",
    "Irish": "jimregan/wav2vec2-large-xlsr-irish-basic",
    "Kinyarwanda": "lucio/wav2vec2-large-xlsr-kinyarwanda",
    "Lithuanian": "DeividasM/wav2vec2-large-xlsr-53-lithuanian",
    "Hungarian": "jonatasgrosman/wav2vec2-large-xlsr-53-hungarian",
    "Finnish": "aapot/wav2vec2-large-xlsr-53-finnish",
}


class Pipeline:
    def __init__(self, processor, model):
        self.processor = processor
        self.model = model


class ConversionError(Exception):
    pass


def change_sample_rate(audio_path, new_sample_rate=16000):
    audio_to_resample, sr = librosa.load(audio_path)
    resampled_audio = librosa.resample(audio_to_resample, sr, new_sample_rate)
    resampled_tensor = torch.tensor([resampled_audio])
    return resampled_tensor


def convert_to_wav(audio_path):
    path = audio_path.split("/")
    filename = path[-1].split(".")[0]
    audio, sr = librosa.load(audio_path)
    wav_path = f"{filename}.wav"
    sf.write(wav_path, audio, sr, subtype="PCM_24")
    return wav_path


def transcribe_from_audio_path(
    audio_path,
    check_language=False,
    classify_emotion=False,
    model="",
    pipeline=None,
    cuda=True,
):
    converted = False

    device = "cpu"
    if torch.cuda.is_available() and cuda:
        device = "cuda"

    if audio_path[-4:] != ".wav":
        try:
            audio_path = convert_to_wav(audio_path)
            converted = True
        except:
            raise ConversionError(f"Could not convert {audio_path} to wav")

    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        # resample to 16000 Hz
        waveform = change_sample_rate(audio_path)
        sample_rate = 16000

    if converted:
        os.remove(audio_path)

    if pipeline == None:
        print("Using model ", model)
        processor = Wav2Vec2Processor.from_pretrained(model)
        model = Wav2Vec2ForCTC.from_pretrained(model)
    else:
        processor = pipeline.processor
        model = pipeline.model

    model = model.to(device)
    waveform = waveform.to(device)
    with torch.no_grad():
        # logits = model(chunk.to("cuda")).logits
        logits = model(waveform).logits

    pred_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(pred_ids)
    # get_word_timestamps(transcription[0], pred_ids, chunk, sample_length)
    # print(transcription)
    return transcription[0], processor, model


def transcribe_directory_of_wav_files(dir, output_file, cuda=True, model_type=None):
    """
    Output a file with first column being the filename and second
    column the transcription from TMH
    :param dir: string path
    :param output_file: output file path str
    :return:
    """
    filenames2transcriptions = {}
    directory = dir
    pipeline = None

    for file in tqdm(list(os.listdir(directory))):
        filename = file
        if filename.endswith(".wav"):
            complete_filename = os.path.join(directory, filename)
            print("Transcribing file ", complete_filename)
            transcription, processor, model = transcribe_from_audio_path(
                complete_filename,
                pipeline=pipeline,
                cuda=cuda,
                model=model_type,
            )
            if processor != None:
                pipeline = Pipeline(processor, model)
            filenames2transcriptions[filename] = transcription

    ret_lines = []
    for k, v in filenames2transcriptions.items():
        ret_lines.append(k + "\t" + v + "\n")

    pat = re.compile("file_(\d+)\.wav")
    lines = sorted(ret_lines, key=lambda x: int(pat.search(x).groups()[0]))

    with open(output_file, "w") as f:
        f.writelines(lines)


def transcribe_directory_of_wav_files_return_file_lines(dir, cuda: bool, model_type):
    """
    Output a file with first column being the filename and second
    column the transcription from TMH
    :param dir: string path
    :param output_file: output file path str
    :return:
    """
    filenames2transcriptions = {}
    directory = dir
    pipeline = None
    ret_lines = []

    pbar = tqdm(list(os.listdir(directory)))
    for file in pbar:
        filename = file
        if filename.endswith(".wav"):
            complete_filename = os.path.join(directory, filename)
            pbar.set_postfix_str(filename)
            transcription, processor, model = transcribe_from_audio_path(
                complete_filename,
                model=model_type,
                pipeline=pipeline,
                cuda=cuda,
            )
            if processor != None:
                pipeline = Pipeline(processor, model)
            filenames2transcriptions[filename] = transcription

    for k, v in filenames2transcriptions.items():
        ret_lines.append(k + "\t" + v + "\n")

    pat = re.compile("file_(\d+)\.wav")
    lines = sorted(ret_lines, key=lambda x: int(pat.search(x).groups()[0]))
    return lines


if __name__ == "__main__":
    model_types = [
        "KBLab/wav2vec2-large-voxrex-swedish",
        "birgermoell/lm-swedish",
    ]
    res = transcribe_directory_of_wav_files_return_file_lines(
        "/data/sisters/maggan_dialogue/z29",
        True,
        model_type="birgermoell/lm-swedish",
    )
    print(res)
