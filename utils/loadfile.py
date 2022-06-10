# Level 1 functions, file loading and preprocessing
# These functions deal with files that are in the format
# file_x1.wav transcription transcription
# file_x2.wav transcription transcription
# ...
# file_xn.wav transcription transcription

import re
from uuid import uuid4

import soundfile


def extract_file_idxs_from_lines(lines):
    pat = re.compile(r"file_(\d+)\.wav")
    return [int(pat.search(x).groups()[0]) for x in lines]


def sequence_of_transcriptions(lines):
    """
    Return a list of strings , each string being the transcripitons
    of each file in order
    :param lines: lines of a chunk transcription file
    :return: one string which is the total concatenated transcription
    """
    splitted = [x.split() for x in lines]
    concat = [" ".join(x[1:]) for x in splitted]
    return " ".join(concat)


def transcriptions(lines):
    """
    Return a list of transcriptions from the given lines of
    a chunk transcription file
    :param lines: lines of a chunk transcription file
    :return: list of strings
    """
    splitted = [x.split() for x in lines]
    concat = [" ".join(x[1:]) for x in splitted]
    return concat


def get_fname_lines(fname):
    with open(fname, "r", encoding="UTF-8") as f:
        lines = f.readlines()
    return lines

def get_audiofile_sr(fname):
    with open(fname, "r") as f:
        _ , sr = soundfile.read(fname)
    return sr


def generate_unique_tmp_filename() -> str:
    return "/tmp/" + uuid4().hex