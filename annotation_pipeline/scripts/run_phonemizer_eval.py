from utils.phonemes import *
from utils.experiment_helpers import *
import pickle

# def phonemizer_eval(model_path, device=None, stub=None):
#     print("Stub is ", stub)
#     phonemizer = init_phonemizer(device, model_path)
#     phoneme_dict = read_phoneme_dict("./models/stress_lex_mtm.txt")
#     print("Preprocessing dict")
#     keys_order = list(phoneme_dict.keys())
#     # Downsample
#     keys_order = random.sample(keys_order, k=1000)
#     values_order = [phoneme_dict[k] for k in keys_order]
#     print("Running phonemizer")
#     count_correct = 0
#     outputs = []
#     pbar = tqdm(list(enumerate(keys_order)))
#     for i,k in pbar:
#         true_phonemes = "".join(phoneme_dict[k])
#         if not stub:
#             phon_output = phonemizer(k,"se")
#         else:
#             phon_output = "a-form"
#         outputs.append(phon_output)
#         if phon_output==true_phonemes:
#             count_correct += 1
#
#         if i % 10 == 0:
#             pbar.set_postfix_str(f"Accuracy: {count_correct / (i+1):.3f}")
#     output_dict = {k:v for k,v in zip(keys_order, outputs)}
#
#     return {
#         "accuracy" : count_correct / len(keys_order),
#         "output_dict" : output_dict
#     }


def phonemizer_eval(model_path, device=None, stub=None):
    print("Stub is ", stub)
    phonemizer = init_phonemizer(device, model_path)
    phoneme_dict = read_phoneme_dict("./models/stress_lex_mtm.txt")
    print("Preprocessing dict")
    keys_order = list(phoneme_dict.keys())
    # Downsample
    # keys_order = random.sample(keys_order, k=1000)
    values_order = [phoneme_dict[k] for k in keys_order]
    print("Running phonemizer")
    true_phonemes = ["".join(v) for v in values_order]
    count_correct = 0
    phone_output = phonemizer(keys_order, "se")
    for key, output, true in zip(keys_order, phone_output, true_phonemes):
        print("output ", output)
        print("true ", true)
        if output == true:
            count_correct += 1

    output_dict = {k: v for k, v in zip(keys_order, phone_output)}
    print("Count correct ", count_correct)
    print("Number of keys ", len(keys_order))

    return {
        "accuracy": count_correct / len(keys_order),
        "output_dict": output_dict,
    }


model_paths = [
    "models/deep-phonemizer-se.pt",
    "models/DeepPhon/winhome/Downloads/DeepPhon_to_send/best_model.pt",
    "models/DeepPhon/winhome/Downloads/DeepPhon_to_send/model_step_40k.pt",
]
kwargs = {"device": "cuda", "stub": False}
res = grid(phonemizer_eval, [model_paths], kwargs, stub=False)
print([(x[0], x[1]["accuracy"]) for x in res])
with open("output/phonemizer_eval_res", "wb") as f:
    pickle.dump(res, f)
