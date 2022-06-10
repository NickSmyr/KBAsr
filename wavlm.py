import torchaudio.functional as F
import torch
from datasets import load_dataset

# Import model and processor
from transformers import Wav2Vec2ProcessorWithLM, Wav2Vec2ForCTC

print("Init model")
model_name = 'viktor-enzell/wav2vec2-large-voxrex-swedish-4gram'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Wav2Vec2ForCTC.from_pretrained(model_name).to(device)
processor = Wav2Vec2ProcessorWithLM.from_pretrained(model_name)

# Import and process speech data
common_voice = load_dataset('common_voice', 'sv-SE', split='test[:1%]')

def speech_file_to_array(sample):
    # Convert speech file to array and downsample to 16 kHz
    sampling_rate = sample['audio']['sampling_rate']
    sample['speech'] = F.resample(torch.tensor(sample['audio']['array']), sampling_rate, 16_000)
    return sample

common_voice = common_voice.map(speech_file_to_array)

# Run inference
print("=========commonvoice speech===============")
print(type(common_voice['speech']))
print(type(common_voice['speech'][0]))
print(len(common_voice['speech'][0]))
print("=========commonvoice speech===============")
inputs = processor(common_voice['speech'], sampling_rate=16_000, return_tensors='pt', padding=True).to(device)

#print("inf")
with torch.no_grad():
    #print(inputs)
    logits = model(**inputs).logits

transcripts = processor.batch_decode(logits.cpu().numpy()).text