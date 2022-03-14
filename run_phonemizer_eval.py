from loadfile import *
from phonemes import *
from preprocess import *
from evaluate import *
from google_kb_z_speaker.main import *
from tqdm.auto import tqdm
from experiment_helpers import *
from functools import partial
import numpy as np
import pickle

def phonemizer_eval(model_path, device=None):
    phonemizer = init_phonemizer(device, model_path)
    phoneme_dict = read_phoneme_dict("./models/stress_lex_mtm.txt")
    print("Preprocessing dict")
    keys_order = list(phoneme_dict.keys())
    # Downsample
    values_order = [phoneme_dict[k] for k in keys_order]
    print("Running phonemizer")
    count_correct = 0
    for k in tqdm(phoneme_dict.keys()):
        phon_output = phonemizer(k,"se")
        if phon_output==k:
            count_correct += 1
    return {
        "accuracy" : count_correct / len(keys_order),
    }


model_paths = [
        'models/deep-phonemizer-se.pt',
            'models/DeepPhon/winhome/Downloads/DeepPhon_to_send/best_model.pt',
            'models/DeepPhon/winhome/Downloads/DeepPhon_to_send/model_step_40k.pt',
            
]
res = grid(phonemizer_eval, model_paths, device="cuda")
print(res)
with open("output/phonemizer_eval_res") as f:
    pickle.dump(res,f)