from dp.phonemizer import Phonemizer
from dp.model import model, predictor
import torch
import sys 
# this model needs a download of the model.
## Please download this model and put it in the following folder.
## https://public-asai-dl-models.s3.eu-central-1.amazonaws.com/DeepPhonemizer/en_us_cmudict_ipa_forward.pt
## The model assumes that the model is stored in the current folder.
def get_swedish_phonemes(text, phonemizer):
    """
    Get swedish phnems
    :param text: The text to phonemize
    :param phonemizer: The model created with init_phonemizer
    :return: a list of the swedish phonemes
    """
    phonemes = phonemizer(text, 'se')
    result = ''
    stress_marks = set()
    stress_marks.update(["\'", "\"", "`"])
    for i, ph in enumerate(phonemes):
        # Skip stress marks
        if ph in stress_marks:
            continue
        if ph == ' ':
            result = result + '_ '
        if ph not in '23:_ ':
            result = result + ph + ' '
        elif ph != ' ':
            result = result[:-1] + ph + ' ' 
    return result

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
    txt = "Jag heter Nikos"
    print(get_swedish_phonemes(txt, phonemizer))

