# Module containing level0 text processing functions
import string


def preprocess_text(txt : str):
    """
    Most commong text preprocessing, input is first cleared of
    punctutation and then lowercased
    :param txt: the input text
    :return: preprocessed text
    """
    intermediate = remove_punct(txt).lower()
    return " ".join(intermediate.split())


def w2id(txt : str):
    """
    Creates a mapping from words to identifiers within the txt
    Example "one two three two" becomes {chr(0): "one:, chr(1):
        "two", chr(2): "three"}
    :param txt: total strng text
    :return: dict mapping
    """
    return {v: chr(i) for i,v in enumerate(set(txt.split()))}


def encode_txt(txt : str, w2id):
    """
    Encodes the given text according to the mapping w2i. txt
    must have been used while creating the w2id
    :param txt: the string to encode
    :param w2i: word to number mapping
    :return:
    """
    return "".join([w2id[x] for x in txt.split()])


def remove_punct(s : str):
    return s.translate(str.maketrans('', '', string.punctuation))