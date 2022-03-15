import random

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

def phonemizer_eval(model_path, device=None, stub=True):
    phonemizer = init_phonemizer(device, model_path)
    phoneme_dict = read_phoneme_dict("./models/stress_lex_mtm.txt")
    print("Preprocessing dict")
    keys_order = list(phoneme_dict.keys())
    # Downsample
    values_order = [phoneme_dict[k] for k in keys_order]
    print("Running phonemizer")
    count_correct = 0
    outputs = []
    pbar = tqdm(list(enumerate(keys_order)))
    for i,k in pbar:
        true_phonemes = "".join(phoneme_dict[k])
        if not stub:
            phon_output = phonemizer(k,"se")
        else:
            phon_output = "aa"
        outputs.append(phon_output)
        if phon_output==true_phonemes:
            count_correct += 1

        if i % 2000 == 0:
            pbar.set_postfix_str(f"Accuracy: {count_correct / len(keys_order):.3f}")

    return {
        "accuracy" : count_correct / len(keys_order),
        "outputs" : outputs
    }


model_paths = [
        'models/deep-phonemizer-se.pt',
            'models/DeepPhon/winhome/Downloads/DeepPhon_to_send/best_model.pt',
            'models/DeepPhon/winhome/Downloads/DeepPhon_to_send/model_step_40k.pt',
            
]
res = grid(phonemizer_eval, model_paths, device="cuda", stub=False)
print([(x[0],x[1]["accuracy"]) for x in res])
with open("output/phonemizer_eval_res", "wb") as f:
    pickle.dump(res,f)