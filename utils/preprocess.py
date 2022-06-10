# Module containing level0 text processing functions
import string


def preprocess_text(txt: str):
    """
    Most commong text preprocessing, input is first cleared of
    punctutation and then lowercased
    :param txt: the input text
    :return: preprocessed text
    """
    intermediate = remove_punct(txt).lower()
    return " ".join(intermediate.split())


def w2id(txt: str):
    """
    Creates a mapping from words to identifiers within the txt
    Example "one two three two" becomes {chr(0): "one:, chr(1):
        "two", chr(2): "three"}
    :param txt: total strng text
    :return: dict mapping
    """
    return {v: chr(i) for i, v in enumerate(set(txt.split()))}


def encode_txt(txt: str, mapping):
    """
    Encodes the given text according to the mapping w2i. txt
    must have been used while creating the w2id
    :param txt: the string to encode
    :param mapping: word to number mapping
    :return:
    """
    return "".join([mapping[x] for x in txt.split()])


def decode_txt(txt: str, mapping):
    """
    Decodes the encoded text created with encode_txt
     according to the mapping w2i.
    :param txt: the string to encode
    :param mapping: word to number mapping
    :return:
    """
    id2w = {v: k for k, v in mapping.items()}
    return " ".join([id2w[x] for x in txt])


def remove_punct(s: str):
    """
    Removes punctuationg from the str
    :param s: the string to remove punctuation
    :return: unpunctuated string
    """
    return s.translate(str.maketrans("", "", string.punctuation))


def calculate_num_samples_for_seconds(sample_rate_hz: int, seconds: float) -> int:
    """
    Returns the number of samples to create an audio file with the specified
    duration given the sample rate
    """
    return int(sample_rate_hz * seconds)