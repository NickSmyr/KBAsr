from typing import Union, List

from dp.model.predictor import Predictor
from dp.phonemizer import Phonemizer
from dp.model import model, predictor
import torch
import sys


# this model needs a download of the model.
## Please download this model and put it in the following folder.
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


def unravel_phonemes(texts: Union[str, List[str]]):
    """
    :param texts: output of get_swedish_phonemes
    :return: splitted output on whitespace and underscore
    """
    only_one_text = False
    if type(texts) == str:
        texts = [texts]
        only_one_text = True

    res = [x.replace("_", "").split() for x in texts]
    return res[0] if only_one_text else res


def phonemizer_wrapper(
    phonemizer: Phonemizer,
    phoneme_dict=None,
    include_stress_marks=None,
    batch_size=8,
) -> Phonemizer:
    def phonemizer_to_return(texts: Union[str, List[str]], lang):
        only_one_text = False
        if type(texts) == str:
            texts = [texts]
            only_one_text = True
        phonemized_texts = phonemizer(texts, lang, batch_size=batch_size)

        # Mapping non OOV words to their phoneme lists
        if phoneme_dict:
            splitted_phonemes = [x.split() for x in phonemized_texts]
            splitted_texts = [x.split() for x in texts]

            final_texts = []
            for phoneme_word_list, word_list in zip(splitted_phonemes, splitted_texts):
                # TODO fix this
                if len(phoneme_word_list) == len(word_list):
                    final_phoneme_words = []
                    for phoneme_word, word in zip(phoneme_word_list, word_list):
                        if word in phoneme_dict:
                            final_phoneme_words.append("".join(phoneme_dict[word]))
                        else:
                            final_phoneme_words.append(phoneme_word)
                    final_texts.append(" ".join(final_phoneme_words))
                else:
                    print(
                        "A critical phonemizer regularity was violated with "
                        "the input sequence being: " + str(word_list),
                        "phonemizer output has not been processed",
                        file=sys.stderr,
                    )
                    final_texts.append(" ".join(phoneme_word_list))

            phonemized_texts = final_texts

        # Removing stress marks
        if not include_stress_marks:
            stress_marks = set()
            stress_marks.update(["'", '"', "`"])
            phonemized_texts = [
                x.translate({ord(c): None for c in stress_marks})
                for x in phonemized_texts
            ]

        # Return result
        return phonemized_texts[0] if only_one_text else phonemized_texts

    return phonemizer_to_return


def get_swedish_phonemes(
    texts: Union[str, List[str]],
    phonemizer,
    phoneme_dict_path,
    include_stress_marks=True,
    use_dict=False,
    batch_size=50,
):
    """
    Get swedish phonemes, Text must be lowercased :param text: The text to
    phonemize either one example str or a list of strings :param phonemizer:
    The model created with init_phonemizer :param use_dict: True if the
    phonemes must first be generated from the dictionary provided :param
    phoneme_dict_path: A path to a dictionary mapping words to list of
    phonemes :return: The phonemes for each text each of which is a List[
    str] and total returned object is Union[List[str], List[List[str]]
    """
    only_one_text = False
    if type(texts) == str:
        texts = [texts]
        only_one_text = True

    stress_marks = set()
    stress_marks.update(["'", '"', "`"])

    phoneme_dict = read_phoneme_dict(phoneme_dict_path)
    phonemes = phonemizer(texts, "se", batch_size=batch_size)

    phonemized_texts = []

    print("Desplitting phonemes and removing stress marks")
    for ti, phonemes_i in zip(texts, phonemes):
        words = ti.split()
        word_idx = 0

        all_phonemes = []
        curr_word_phonemes = []

        for i, ph in enumerate(phonemes_i):
            # Skip stress marks
            if ph in stress_marks and not include_stress_marks:
                continue
            if ph == " ":
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

            if ph not in "23:_ ":
                # End of phoneme
                # result = result + ph + ' '
                curr_word_phonemes.append(ph)
            elif ph != " ":
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


def init_phonemizer(device, model_path, stress_marks=True):
    try:
        if stress_marks:
            transformer = model.ForwardTransformer(
                55, 55, d_fft=1024, d_model=512, dropout=0.1, heads=4, layers=6
            )
        else:
            transformer = model.ForwardTransformer(
                55, 52, d_fft=1024, d_model=512, dropout=0.1, heads=4, layers=6
            )

        checkpoint = torch.load(model_path, map_location=device)
        transformer.load_state_dict(checkpoint["model"])
        preprocessor = checkpoint["preprocessor"]

        pred = predictor.Predictor(transformer, preprocessor)
        phoneme_dict = checkpoint["phoneme_dict"]
        phonemizer = Phonemizer(pred, phoneme_dict)

        return phonemizer

    except Exception as e1:
        pass
    # Try the second model architecture
    try:

        checkpoint = torch.load(model_path, map_location=device)
        preprocessor = checkpoint["preprocessor"]

        transformer = model.AutoregressiveTransformer(
            52,
            77,
            d_fft=1024,
            d_model=512,
            dropout=0.1,
            heads=4,
            encoder_layers=4,
            decoder_layers=4,
            end_index=preprocessor.phoneme_tokenizer.end_index,
        )
        checkpoint = torch.load(model_path, map_location=device)
        preprocessor = checkpoint["preprocessor"]

        transformer.load_state_dict(checkpoint["model"])

        pred = predictor.Predictor(transformer, preprocessor)
        phonemizer = Phonemizer(pred, None)

        return phonemizer

    except Exception as e:
        print(
            "Could not find a suitable model architecture for the phonemizer at model path:"
            f"{model_path}",
            file=sys.stderr,
        )
        raise e


if __name__ == "__main__":
    phonemizer = init_phonemizer(
        "cuda", "./models/deep-phonemizer-se.pt", stress_marks=True
    )
    txt = ["jag heter nikos", "hallå nikos trevligt att träffas"]
    print(get_swedish_phonemes(txt, phonemizer))
