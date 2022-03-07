from typing import Union, List

from dp.phonemizer import Phonemizer
from dp.model import model, predictor
import torch
import sys 
# this model needs a download of the model.
## Please download this model and put it in the following folder.
## https://public-asai-dl-models.s3.eu-central-1.amazonaws.com/DeepPhonemizer/en_us_cmudict_ipa_forward.pt
## The model assumes that the model is stored in the current folder.
def read_phoneme_dict(dict_path):
    """
    Reads a file containing a mapping between
    swedish words and their phonemes
    :param dict_path:
    :return:
    """
    mapping = {}
    with open(dict_path, "r", encoding="ISO-8859-1") as f:
        for line in f.readlines():
            splitted = line.split()
            if len(splitted) == 0:
                continue
            word = splitted[0]
            phonemes = splitted[1:]
            mapping[word] = phonemes
    return mapping


def get_swedish_phonemes(texts: Union[str, List[str]], phonemizer, include_stress_marks=True):
    """
    Get swedish phonemes, Text must be lowercased
    :param text: The text to phonemize either one example str or a list of strings
    :param phonemizer: The model created with init_phonemizer
    :return: a list of the swedish phonemes
    """
    only_one_text = False
    if type(texts) == str:
        texts = [texts]
        only_one_text = True

    stress_marks = set()
    stress_marks.update(["\'", "\"", "`"])

    phoneme_dict = read_phoneme_dict("models/stress_lex_mtm.txt")
    phonemes = phonemizer(texts, 'se', batch_size=50)

    phonemized_texts = []

    for ti, phonemes_i in zip(texts, phonemes):
        words = ti.split()
        word_idx = 0

        all_phonemes = []
        curr_word_phonemes = []

        for i, ph in enumerate(phonemes_i):
            # Skip stress marks
            if ph in stress_marks and not include_stress_marks:
                continue
            if ph == ' ':
                # end of word
                # If there is a phoneme for this word in the dict use that
                if words[word_idx] in phoneme_dict:
                    all_phonemes.append(phoneme_dict[words[word_idx]])
                # Otherwise, use the model's phoneme output
                else:
                    all_phonemes.append(curr_word_phonemes)
                word_idx += 1
                curr_word_phonemes = []
                continue

            if ph not in '23:_ ':
                # End of phoneme
                # result = result + ph + ' '
                curr_word_phonemes.append(ph)
            elif ph != ' ':
                # There are some cases where 23: can be output
                # when there are unrecognized words (eg. 30 -> 2)
                if len(curr_word_phonemes) == 0:
                    curr_word_phonemes.append(ph)
                else:
                    # Append character to last phoneme
                    # result = result[:-1] + ph + ' '
                    curr_word_phonemes[-1] += ph

        # TODO This upper if was not needed during the unbatched experiments
        if len(words) == 0:
            phonemized_texts.append("")
        else:
            # Add the final phoneme-word
            if words[word_idx] in phoneme_dict:
                all_phonemes.append(phoneme_dict[words[word_idx]])
            # Otherwise, use the models phoneme output
            else:
                all_phonemes.append(curr_word_phonemes)
            phonemized_texts.append(" _ ".join([" ".join(x) for x in all_phonemes]))

    return phonemized_texts[0] if only_one_text else phonemized_texts

def preprocess_phonemes(phoneme_str):
    """
    Transforms a phoneme str eg "j ' a2: _ h ' e2: t ë r _ n ' i k å s"
    to more like a txt str "j'a2: h'e2:tër n'ikås"
    :param phoneme_str:
    :return:
    """
    return " ".join(phoneme_str.replace(" ", "").split("_"))


def init_phonemizer(device, model_path, stress_marks=True):
    if stress_marks:
        transformer = model.ForwardTransformer(55, 55,
                                               d_fft=1024, d_model=512,
                                               dropout=0.1, heads=4, layers=6)
    else:
        transformer = model.ForwardTransformer(55, 52,
                                               d_fft=1024, d_model=512,
                                               dropout=0.1, heads=4, layers=6)

    checkpoint = torch.load(model_path, map_location=device)
    transformer.load_state_dict(checkpoint['model'])
    preprocessor = checkpoint['preprocessor']

    pred = predictor.Predictor(transformer, preprocessor)
    phoneme_dict = checkpoint['phoneme_dict']
    phonemizer = Phonemizer(pred, phoneme_dict)

    return phonemizer

if __name__ == '__main__':
    phonemizer = init_phonemizer("cuda", "./models/deep-phonemizer-se.pt",
                                 stress_marks=True)
    txt = [
        "jag heter nikos",
        "hallå nikos trevligt att träffas"
        ]
    print(get_swedish_phonemes(txt, phonemizer))
