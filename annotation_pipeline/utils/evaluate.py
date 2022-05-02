import Levenshtein

from utils.preprocess import w2id, encode_txt


def error_idxs(correct: str, target: str):
    """
    Returns the indexes of the words of correct that
    the target transcription has gotten wrong

    :param correct: unencoded str
    :param target: unencoded str
    :return: list of idxs
    """
    mapping = w2id(correct + " " + target)
    correct_encoded = encode_txt(correct, mapping)
    target_encoded = encode_txt(target, mapping)
    return_idxs = []

    for editop, idx1, idx2 in Levenshtein.editops(correct_encoded, target_encoded):
        if editop == "insert":
            idx = idx1 - 1 if idx1 > 0 else 0
        elif editop == "delete":
            idx = idx1
        elif editop == "replace":
            idx = idx1
        else:
            raise RuntimeError("Unexpected behaviour of editops")
        return_idxs.append(idx)

    return return_idxs
