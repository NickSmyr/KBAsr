from difflib import SequenceMatcher
from functools import partial
from statistics import mean
from typing import Dict, List, Union, Tuple

from jiwer import wer

from utils.evaluate import error_idxs
from google_kb_z_speaker.main import get_lcs_str, filter_bunches_only_on_agreement, filter_bunches, agreement_stats, \
    bunch_agrees
from google_kb_z_speaker.preprocessing import get_swedish_phonemes_z, singular_phonemes_preprocess
from utils.phonemes import init_phonemizer
from utils.seqmatch import blocks

import numpy as np


def preprocess(bunches, phonemizer, _filter, phoneme_words, singular_phonemes, preprocess_hook, stress_marks):
    if phoneme_words:
        bunches = get_swedish_phonemes_z(bunches, phonemizer, stress_marks=stress_marks)
        # TODO backwards compatibility break
        #bunches = {k: [process_phonemizer_output(x) for x in v] for k, v in bunches.items()}

    if singular_phonemes:
        bunches = get_swedish_phonemes_z(bunches, phonemizer, stress_marks=stress_marks)
        bunches = singular_phonemes_preprocess(bunches)

    if preprocess_hook is not None:
        preprocess_hook(**locals())

    if _filter is not None:
        if len(_filter) == 1 and "agreement" in _filter:
            bunches = filter_bunches_only_on_agreement(bunches, _filter["agreement"])
        else:
            bunches = filter_bunches(bunches, **_filter)

    return {
        "bunches": bunches
    }


def google_kb_wer(bunches):
    return {
        "google_wer": wer(bunches["correct"], bunches["google"]),
        "kb_wer": wer(bunches["correct"], bunches["kb"]),
    }


def sentence_lengths(bunches):
    return {k + "-avg-length": mean([len(x.split(" ")) for x in v]) for k, v in bunches.items()}


def eoi(bunches):
    kei = 0
    oei = 0
    gei = 0
    tei = 0

    for c_l, g_l, kb_l in zip(bunches["correct"], bunches["google"], bunches["kb"]):
        g_s = set(error_idxs(c_l, g_l))
        k_s = set(error_idxs(c_l, kb_l))

        gei += len(g_s)
        kei += len(k_s)
        oei += len(g_s & k_s)
        tei += len(g_s | k_s)

    error_index_overlap = oei / tei

    return {"error_index_overlap": error_index_overlap}


def lcs_percentage(bunches):
    lcses = []

    for c_l, g_l, kb_l in zip(bunches["correct"], bunches["google"], bunches["kb"]):
        total_length_before = len(g_l.split(" ")) + len(kb_l.split(" "))
        words_set = set(g_l.split(" ") + kb_l.split(" "))
        w2char = {x: chr(i) for i, x in enumerate(words_set)}
        g_l_enc = "".join([w2char[w] for w in g_l.split(" ")])
        kb_l_enc = "".join([w2char[w] for w in kb_l.split(" ")])
        assert total_length_before == (len(g_l_enc) + len(kb_l_enc))

        s = SequenceMatcher(None, g_l_enc, kb_l_enc)
        lcs = ''.join([g_l_enc[block.a:(block.a + block.size)] for block in s.get_matching_blocks()])
        lcses.append(len(lcs) / len(c_l.split(" ")))

    return {"lcs-mean": mean(lcses)}


def agreement_stats_experiment(bunches):
    agreement, g_correct_kb_not, kb_correct_g_not, agreement_not_correct, agreement_correct, \
    both_incorrect_disagreement = agreement_stats(bunches)

    return {
        "agreement": agreement,
        "g_correct_kb_not ": g_correct_kb_not,
        "kb_correct_g_not ": kb_correct_g_not,
        "agreement_not_correct": agreement_not_correct,
        "both_incorrect_disagreement": both_incorrect_disagreement,
    }


def parameterized_agreement(bunches, phonemizer_path, _filter=None, phoneme_words=None, singular_phonemes=None,
                            preprocess_hook=None, stress_marks=None, trusted_model=None, threshold_range=None):
    """
    Trusted model: Which model to fall back to when there is no agreement
    """
    phonemizer = init_phonemizer("cuda", phonemizer_path, stress_marks)
    bunches = preprocess(bunches, phonemizer, _filter, phoneme_words, singular_phonemes, preprocess_hook,
                         stress_marks)["bunches"]
    threshold_levels = np.linspace(*threshold_range)
    # bunches : DL
    wers = []
    agreement_ratios = []

    for t in threshold_levels:
        agreement_func = partial(bunch_agrees, threshold=t)
        bunch_list = [{k: bunches[k][i] for k in bunches} for i in range(len([x for x in bunches.values()][0]))]
        preds = []
        corrects = []
        count_agreement = 0
        for bunch in bunch_list:
            if agreement_func(bunch):
                preds.append(get_lcs_str(bunch))
                corrects.append(bunch["correct"])
                count_agreement += 1

        wers.append(wer(corrects, preds))
        agreement_ratios.append(count_agreement / len(bunches["correct"]))

    return {
        "agreement_wers": wers,
        "threshold_levels": threshold_levels,
        "agreement_ratios": agreement_ratios,
    }


def meval(bunches,phonemizer_path , _filter=None, phoneme_words=None, singular_phonemes=None, preprocess_hook=None, stress_marks=None):
    phonemizer = init_phonemizer("cuda", phonemizer_path, stress_marks)
    bunches = preprocess(bunches,phonemizer, _filter, phoneme_words, singular_phonemes, preprocess_hook, stress_marks)["bunches"]
    res = {**google_kb_wer(bunches), **sentence_lengths(bunches), **lcs_percentage(bunches)}
    if _filter is None:
        return {**agreement_stats_experiment(bunches), **res, **eoi(bunches)}
    else:
        return {**res}


def ensemble(phonemizer, ratio_threshold, bunches=None, use_phonemizer=None, save_ensemble_output=None):
    ensemble_outputs = get_ensemble_output(bunches, phonemizer, ratio_threshold, use_phonemizer)
    res = {**google_kb_wer(bunches), "ensemble-wer": wer(bunches["correct"], ensemble_outputs)}
    if save_ensemble_output:
        res = {**res, "ensemble_output" : ensemble_outputs}
    return res



def get_ensemble_output(bunches : Union[Dict[str, str], Dict[str, List[str]]], phonemizer, ratio_threshold: float,
                        use_phonemizer : bool):
    """
    Return the ensemble output
    :param bunches: either a single bunch or all the bunches (model2transcriptions)
    :return:
    """
    only_one_example = False
    if type(bunches[list(bunches.keys())[0]]) == str:
        bunches = { k:[v] for k,v in bunches.items()}
        only_one_example = True

    bunch_list = [{k: bunches[k][i] for k in bunches} for i in range(len([x for x in bunches.values()][0]))]

    block_list_unmatched_idxs_tuple_list : List[Tuple[List[Tuple[str,str]], List[int]]] = [
        blocks(bunch["google"], bunch["kb"]) for bunch in bunch_list
    ]
    selected_blocks = []
    # In order to optimize the gpu usage we need to only do 1 call to the phonemizer
    # For this we need to flatten all the unmatched block pairs and generate a locator (i,ii)
    # So we can recover the phonemized pairs when we have example_index (i), and block_index(ii)

    # By using this vectorization we can achieve 12x speedup

    # Here unmatched block pair index is the index of one unmatched block pair inside the flattened array
    # of all unmatched blocks
    unmatched_blocks : List[str] = []
    locator2unmatched_block_pair_index = {}

    for i,p in enumerate(block_list_unmatched_idxs_tuple_list):
        block_list, unmatched_idxs = p
        for ii, pp in enumerate(block_list):
            # Add unmatched plock pair to array
            if ii in unmatched_idxs:
                unmatched_blocks.append(pp[0])
                unmatched_blocks.append(pp[1])
                locator2unmatched_block_pair_index[(i,ii)] = (len(unmatched_blocks) - 2, len(unmatched_blocks) - 1)

    if use_phonemizer:
        phonemized_unmatched_blocks = phonemizer(unmatched_blocks, "se")
    else:
        phonemized_unmatched_blocks = None

    ensemble_output = []
    for i,block_list_unmatched_idxs_tuple in enumerate(block_list_unmatched_idxs_tuple_list):
        block_list, unmatched_idxs = block_list_unmatched_idxs_tuple
        selected_blocks = []
        for ii, p in enumerate(block_list):
            if ii in unmatched_idxs:
                if use_phonemizer:
                    phonemized_block_pair_idxs = locator2unmatched_block_pair_index[(i,ii)]
                    phonemized_block_pair = phonemized_unmatched_blocks[phonemized_block_pair_idxs[0]],\
                                            phonemized_unmatched_blocks[phonemized_block_pair_idxs[1]],
                    ratio = SequenceMatcher(None, phonemized_block_pair[0], phonemized_block_pair[1]).ratio()
                else:
                    ratio = SequenceMatcher(None, p[0], p[1]).ratio()
                if ratio > ratio_threshold:
                    # There is large similarity choose google
                    selected_blocks.append(p[0])
                else:
                    # Very dissimilar choose kb
                    selected_blocks.append(p[1])
            else:
                selected_blocks.append(p[1])
        ensemble_output.append(" ".join(selected_blocks))

    return ensemble_output[0] if only_one_example else ensemble_output

def get_kb_google_unmatched_blocks(bunch):
    block_list, unmatched_idxs = blocks(bunch["google"], bunch["kb"])
    return [x for i,x in enumerate(block_list) if i in unmatched_idxs]
