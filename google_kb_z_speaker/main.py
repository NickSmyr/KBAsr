from difflib import SequenceMatcher
from functools import reduce

import Levenshtein
from jiwer import wer

from evaluate import error_idxs
from loadfile import extract_file_idxs_from_lines, get_fname_lines, transcriptions
import matplotlib.pyplot as plt

from phonemes import get_swedish_phonemes, init_phonemizer
from preprocess import preprocess_text, w2id, encode_txt, remove_punct


def fix_lines(model2speaker_lines):
    """
        MUTABLE operation Remove nonexisting in correct filenames in kb
        :return: the corrected lines
    """
    # Test which numbers are missing from the correct
    nums = {k : extract_file_idxs_from_lines(v) for k,v in model2speaker_lines.items()}

    # Create mappings from  file idxs to list idxs
    model2fi2li = {k : {fi: li for li, fi in enumerate(v)} for k, v in nums.items()}
    # Correct lines are subsets of the transcribed lines
    nums = {k: set(v) for k,v in nums.items()}
    assert nums["correct"] == nums["google"]
    assert len(nums["correct"] - nums["kb"]) == 0
    extra_idxs = nums["kb"] - nums["correct"]

    # Filter extra google,kb lines
    for fi in sorted(list(extra_idxs), reverse=True):
        # if idx < len(google_lines):
        #    del google_lines[idx]
        del model2speaker_lines["kb"][model2fi2li["kb"][fi]]

    assert file_lines_are_correct(model2speaker_lines)


def file_lines_are_correct(model2speaker_lines):

    nums = {k : extract_file_idxs_from_lines(v) for k,v in model2speaker_lines.items()}

    # Correct lines are subsets of the transcribed lines
    nums = {k: set(v) for k,v in nums.items()}
    return nums["correct"] == nums["google"] and nums["correct"] == nums["kb"]


# Return the clips where both models had the same output transcription
# and also the percentage of the total clips that had full agreement
def agreement_stats(bunches):
    """
    Returns percentages in order:
        agreement, correct google while incorrect kb, correct kb while incorrect google,
        incorrect agreement, correct agreement, disagreement but both incorrect
    :param bunches: A dict from model to model lines
    :param agreement: A function bunch -> bool
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

    bunch_list = [{k: bunches[k][i] for k in bunches} for i in range(len([x for x in bunches.values()][0]))]
    for bunch in bunch_list:
        t_c = bunch["correct"]
        t_g = bunch["google"]
        t_kb = bunch["kb"]
        total += 1
        if t_g == t_kb:
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

def get_lcs_str(bunch):
    splitted = {k: v.split(" ") for k, v in bunch.items()}
    s = SequenceMatcher(None, splitted["google"], splitted["kb"])
    lcs = " ".join([" ".join(splitted["google"][block.a:(block.a + block.size)]) for block in s.get_matching_blocks()
                    if block.size > 0])
    return lcs

def agreement_percentage(bunch):
    splitted = {k: v.split(" ") for k, v in bunch.items()}
    lcs = get_lcs_str(bunch)
    return len(lcs.split()) / max(len(splitted["google"]), len(splitted["kb"]))

def bunch_agrees(bunch, threshold):
    """
    Returns true if the bunch agrees with the given
    threshhold. let LCS be the words in the
    longest common subsequence of google and kb,
    then the bunch will agree if
        |LCS| / max(googlelen, max(kblen)
            >= threshhold
    :param bunch: Dict[model, str]
    :param threshold:float deciding the percentance cutoff
    :return: bool
    """
    perc_agr = agreement_percentage(bunch)
    return True if  perc_agr >= threshold else False

def filter_bunches(bunches,
                 agreement, kb_correct, g_correct):
    c,g,kb = [],[],[]
    bunch_list = [ {k : bunches[k][i] for k in bunches} for i in range(len([x for x in bunches.values()][0]))]
    for bunch in bunch_list:
        t_c = bunch["correct"]
        t_g = bunch["google"]
        t_kb = bunch["kb"]
        if t_g == t_kb:
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
    return {
        "correct": c,
        "google": g,
        "kb": kb
    }

def filter_bunches_only_on_agreement(bunches,agreement):

    c, g, kb = [], [], []
    bunch_list = [{k: bunches[k][i] for k in bunches} for i in range(len([x for x in bunches.values()][0]))]
    for bunch in bunch_list:
        t_c = bunch["correct"]
        t_g = bunch["google"]
        t_kb = bunch["kb"]
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

    return {
        "correct" : c,
        "google" : g,
        "kb" : kb
    }



if __name__ == '__main__':
    pass