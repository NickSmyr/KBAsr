from functools import reduce

import Levenshtein
from jiwer import wer

from evaluate import error_idxs
from loadfile import extract_file_idxs_from_lines, get_fname_lines, transcriptions
import matplotlib.pyplot as plt

from phonemes import get_swedish_phonemes, init_phonemizer, preprocess_phonemes
from preprocess import preprocess_text, w2id, encode_txt, remove_punct


def fix_lines(correct_lines, google_lines, kb_lines):
    """
    MUTABLE operation Remove nonexisting in correct filenames in kb
    :return: the corrected lines
    """
    # Test which numbers are missing from the correct
    nums_c = extract_file_idxs_from_lines(correct_lines)
    nums_kb = extract_file_idxs_from_lines(kb_lines)
    nums_g = extract_file_idxs_from_lines(google_lines)

    # Create mappings from  file idxs to list idxs
    fi2li_c = {fi: li for li, fi in enumerate(nums_c)}
    fi2li_kb = {fi: li for li, fi in enumerate(nums_kb)}
    fi2li_g = {fi: li for li, fi in enumerate(nums_g)}
    # Correct lines are subsets of the transcribed lines
    nums_c = set(nums_c)
    nums_kb = set(nums_kb)
    nums_g = set(nums_g)
    assert nums_c == nums_g
    assert len(nums_c - nums_kb) == 0
    extra_idxs = nums_kb - nums_c

    # Filter extra google,kb lines
    for fi in sorted(list(extra_idxs), reverse=True):
        # if idx < len(google_lines):
        #    del google_lines[idx]
        del kb_lines[fi2li_kb[fi]]

    assert file_lines_are_correct(correct_lines, google_lines, kb_lines)


def file_lines_are_correct(correct_lines, google_lines, kb_lines):
    nums_c = extract_file_idxs_from_lines(correct_lines)
    nums_kb = extract_file_idxs_from_lines(kb_lines)
    nums_g = extract_file_idxs_from_lines(google_lines)

    # Correct lines are subsets of the transcribed lines
    nums_c = set(nums_c)
    nums_kb = set(nums_kb)
    nums_g = set(nums_g)
    return nums_c == nums_g and nums_c == nums_kb

def visualize():
    # Levenshtein op[1] insert at x means it is inserted before array element arr[x]
    str1 = '120346'
    str2 = '012345'
    for x in Levenshtein.editops(str2, str1):
        print(x)
    print(Levenshtein.distance(str1, str2))
    print(Levenshtein.distance(str2, str1))
    speakers = ["z21", "z20", "z28", "z29" ]

    google_fnames = [ f"transcriptions/{s}.googleasr"  for s in speakers]
    correct_fnames = [f"transcriptions/{s}.correct" for s in speakers]
    kb_fnames = [f"transcriptions/{s}.kb" for s in speakers]

    google_lines_unp = [get_fname_lines(fname) for fname in google_fnames]
    correct_lines_unp = [get_fname_lines(fname) for fname in correct_fnames]
    kb_lines_unp = [get_fname_lines(fname) for fname in kb_fnames]

    [fix_lines(*model) for model in zip(correct_lines_unp, google_lines_unp, kb_lines_unp)]

    google_lines = reduce(lambda x,y : x + y, google_lines_unp)
    correct_lines = reduce(lambda x,y : x + y, correct_lines_unp )
    kb_lines = reduce(lambda x,y : x + y, kb_lines_unp)

    google_lines = transcriptions(google_lines)
    correct_lines = transcriptions(correct_lines)
    kb_lines = transcriptions(kb_lines)

    google_lines = [preprocess_text(x) for x in google_lines]
    correct_lines = [preprocess_text(x) for x in correct_lines]
    kb_lines = [preprocess_text(x) for x in kb_lines]

    correct_lines, google_lines, kb_lines = filter_lines(correct_lines, google_lines,
                                                          kb_lines, agreement=False, kb_correct=False, g_correct=False)

    idx = 43
    size = 10
    plt.text(0.0, 0.0, google_lines[idx], size=size, rotation=0,
             ha="center", va="center",
             bbox=dict(boxstyle="round",
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )

    plt.text(0, -2.5, kb_lines[idx], size=size, rotation=0,
             ha="center", va="center",
             bbox=dict(boxstyle="round",
                       ec=(153/255, 51/255, 0/255),
                       fc=(255/255, 153/255, 102/255),
                       )
             )
    plt.text(0, -5, correct_lines[idx], size=size, rotation=0,
             ha="center", va="center",
             bbox=dict(boxstyle="round",
                       ec=(42 / 255, 162 / 255, 42 / 255),
                       fc=(133 / 255, 224 / 255, 133 / 255),
                       )
             )
    print("Idxs of google ", error_idxs(correct_lines[idx],
                                        google_lines[idx]))
    print("Idxs of KB ", error_idxs(correct_lines[idx],
                                    kb_lines[idx]))

    #txt = " ".join([google_lines[idx], correct_lines[idx], kb_lines[idx]])
    txt = "one three one"
    src_txt = "one two three two one"
    print("txt " , txt)
    mapping = w2id(txt + " " + src_txt)
    print("Mapping ", mapping)
    encoded_txt = encode_txt(txt, mapping)
    print("Encoded txt " , encoded_txt)
    print(Levenshtein.editops(encode_txt(src_txt, mapping), encoded_txt))

    plt.ylim(-10, 10)
    plt.xlim(-10, 10)
    plt.show()

# Return the clips where both models had the same output transcription
# and also the percentage of the total clips that had full agreement
def percentage_of_agreement(correct_lines, google_lines, kb_lines):
    """
    Returns percentages in order:
        agreement, correct google while incorrect kb, correct kb while incorrect google,
        incorrect agreement, correct agreement, disagreement but both incorrect
    :param correct_lines:
    :param google_lines:
    :param kb_lines:
    :return: count_agreement, g_correct_kb_not, kb_correct_g_not, agreement_not_correct, agreement_correct
    ,both_incorrect_disagreement
    """
    total = 0
    count_agreement = 0
    count_disagreement = 0
    g_correct_kb_not = 0
    kb_correct_g_not = 0
    agreement_not_correct = 0
    agreement_correct = 0
    both_incorrect_disagreement = 0

    for t_c, t_g, t_kb in zip(correct_lines, google_lines, kb_lines):
        total += 1
        if (t_g == t_kb):
            count_agreement += 1
            if (t_g == t_c):
                agreement_correct += 1
            else:
                agreement_not_correct+=1
        else:
            count_disagreement += 1
            if (t_g == t_c):
                g_correct_kb_not += 1
            elif (t_kb == t_c):
                kb_correct_g_not += 1
            else:
                both_incorrect_disagreement += 1

    agreement_not_correct /= count_agreement
    agreement_correct /= count_agreement


    g_correct_kb_not /= count_disagreement
    kb_correct_g_not /= count_disagreement
    both_incorrect_disagreement /= count_disagreement

    count_agreement /= total
    return  count_agreement, g_correct_kb_not, kb_correct_g_not, agreement_not_correct, agreement_correct,\
            both_incorrect_disagreement

def filter_lines(correct_lines, google_lines, kb_lines,
                 agreement, kb_correct, g_correct):
    c,g,kb = [],[],[]
    for t_c, t_g, t_kb in zip(correct_lines, google_lines, kb_lines):
        if (t_g == t_kb):
            if (t_g == t_c):
                if agreement and g_correct and kb_correct:
                    c.append(t_c)
                    g.append(t_g)
                    kb.append(t_kb)
            else:
                if agreement and not g_correct and not kb_correct:
                    c.append(t_c)
                    g.append(t_g)
                    kb.append(t_kb)
        else:
            if (t_g == t_c):
                if not agreement and g_correct and not kb_correct:
                    c.append(t_c)
                    g.append(t_g)
                    kb.append(t_kb)
            elif (t_kb == t_c):
                if not agreement and not g_correct and kb_correct:
                    c.append(t_c)
                    g.append(t_g)
                    kb.append(t_kb)
            else:
                if not agreement and not g_correct and not kb_correct:
                    c.append(t_c)
                    g.append(t_g)
                    kb.append(t_kb)
    return c, g,kb

def filter_lines_only_on_agreement(correct_lines, google_lines, kb_lines,
                 agreement):
    c, g, kb = [], [], []
    for t_c, t_g, t_kb in zip(correct_lines, google_lines, kb_lines):
        if (t_g == t_kb):
            if agreement:
                c.append(t_c)
                g.append(t_g)
                kb.append(t_kb)
        else:
            if not agreement:
                c.append(t_c)
                g.append(t_g)
                kb.append(t_kb)

    return c, g, kb

def multispeaker_eval():
    """
    Evaluate but for all speakers (concatenating lines
    """
    # Speaker
    speakers = ["z21", "z20", "z28", "z29" ]

    google_fnames = [ f"transcriptions/{s}.googleasr"  for s in speakers]
    correct_fnames = [f"transcriptions/{s}.correct" for s in speakers]
    kb_fnames = [f"transcriptions/{s}.kb" for s in speakers]

    google_lines = [get_fname_lines(fname) for fname in google_fnames]
    correct_lines = [get_fname_lines(fname) for fname in correct_fnames]
    kb_lines = [get_fname_lines(fname) for fname in kb_fnames]

    [fix_lines(*model) for model in zip(correct_lines, google_lines, kb_lines)]

    google_lines = reduce(lambda x,y : x + y, google_lines)
    correct_lines = reduce(lambda x,y : x + y, correct_lines )
    kb_lines = reduce(lambda x,y : x + y, kb_lines)

    google_lines = transcriptions(google_lines)
    correct_lines = transcriptions(correct_lines)
    kb_lines = transcriptions(kb_lines)

    google_lines = [preprocess_text(x) for x in google_lines]
    correct_lines = [preprocess_text(x) for x in correct_lines]
    kb_lines = [preprocess_text(x) for x in kb_lines]


    phonemizer = init_phonemizer("cuda", "./models/deep-phonemizer-se.pt")
    google_lines = [preprocess_phonemes(get_swedish_phonemes(x, phonemizer))
                    for x in google_lines]
    correct_lines = [preprocess_phonemes(get_swedish_phonemes(x, phonemizer))
                     for x in correct_lines]
    kb_lines = [preprocess_phonemes(get_swedish_phonemes(x, phonemizer))
                for x in kb_lines]

    filter = {
        "agreement" : False,
        "kb_correct" : False,
        "g_correct" : False
    }
    #correct_lines, google_lines, kb_lines = filter_lines(correct_lines,google_lines,
    #                                                     kb_lines,**filter)
    #correct_lines, google_lines, kb_lines = filter_lines_only_on_agreement(correct_lines, google_lines,
    #                                                                       kb_lines, filter["agreement"])
    print("====== Builtin WER =======")
    print("Google WER : ", wer(correct_lines, google_lines))
    print("KB WER : ", wer(correct_lines, kb_lines))
    print("====== Agreement =======")

    print("====== Error indexes =======")
    kei = 0
    oei = 0
    gei = 0
    tei = 0

    for c_l, g_l, kb_l in zip(correct_lines, google_lines, kb_lines):
        g_s = set(error_idxs(c_l, g_l))
        k_s = set(error_idxs(c_l, kb_l))

        gei += len(g_s)
        kei += len(k_s)
        oei += len(g_s & k_s)
        tei += len(g_s | k_s)

    error_index_overlap = oei / tei
    print("Error index overlap ", error_index_overlap)

    agreement, g_correct_kb_not, kb_correct_g_not, agreement_not_correct, agreement_correct,\
    both_incorrect_disagreement =\
        percentage_of_agreement(correct_lines, google_lines, kb_lines)
    print("Agreement ", agreement)
    print("g_correct_kb_not " , g_correct_kb_not)
    print("kb_correct_g_not ", kb_correct_g_not)
    print("agreement_not_correct ", agreement_not_correct)
    print("agreement_correct ", agreement_correct)
    print("both_incorrect_disagreement ", both_incorrect_disagreement)


def evaluate(speaker):
    print("Running for speaker " + speaker)

    correct_fname = f"transcriptions/{speaker}.correct"
    google_fname = f"transcriptions/{speaker}.googleasr"
    kb_fname = f"transcriptions/{speaker}.kb"

    correct_lines = get_fname_lines(correct_fname)
    google_lines = get_fname_lines(google_fname)
    kb_lines = get_fname_lines(kb_fname)

    fix_lines(correct_lines, google_lines, kb_lines)

    google_lines = transcriptions(google_lines)
    correct_lines = transcriptions(correct_lines)
    kb_lines = transcriptions(kb_lines)

    google_lines = [preprocess_text(x) for x in google_lines]
    correct_lines = [preprocess_text(x) for x in correct_lines]
    kb_lines = [preprocess_text(x) for x in kb_lines]

    print("====== Evaluating =======")
    print(google_lines)
    print(correct_lines)
    print(kb_lines)
    print("====== WERs =======")
    print("Google WER : ", wer(correct_lines, google_lines))
    print("KB WER : ", wer(correct_lines, kb_lines))



if __name__ == '__main__':
    multispeaker_eval()