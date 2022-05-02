from difflib import SequenceMatcher
from typing import List, Tuple


def blocks(s1: str, s2: str) -> Tuple[List[Tuple[str, str]], List[int]]:
    """
    Given two strings (containing words) it splits both strings into the same number of blocks,
    some block indexes will be matched meaning that if at index 2 s2 has block b2 and block b1
    then b1 == b2. Each block will be a string object
    :param s1:
    :param s2:
    :return: a list of pairs of blocks List[Tuple[str,str]] and a list of non matching block indexes:
            List[int]
    """
    s1 = s1.split()
    s2 = s2.split()
    s = SequenceMatcher(None, s1, s2)
    unmatched_block_idxs = []

    blocks_list = s.get_matching_blocks()[:-1]
    block_pairs = []
    # If blocks_list is empty then there are no matching blocks
    if len(blocks_list) == 0:
        return [(" ".join(s1), " ".join(s2))], [0]

    # If the block list does not start with 0 idxs on both, then there is an
    # unmatched block at the start

    # If the final block does not cover the sentence add the initial unmatched block
    if blocks_list[0].a != 0 or blocks_list[0].b != 0:
        start_idx_a = 0
        end_idx_a = blocks_list[0].a
        start_idx_b = 0
        end_idx_b = blocks_list[0].b
        block_pairs.append([s1[start_idx_a:end_idx_a], s2[start_idx_b:end_idx_b]])
        unmatched_block_idxs.append(len(block_pairs) - 1)

    for i in range(len(blocks_list) - 1):
        # Matched block
        start_idx_a = blocks_list[i].a
        end_idx_a = blocks_list[i].a + blocks_list[i].size
        start_idx_b = blocks_list[i].b
        end_idx_b = blocks_list[i].b + blocks_list[i].size
        block_pairs.append([s1[start_idx_a:end_idx_a], s2[start_idx_b:end_idx_b]])
        # Unmatched blocks
        start_idx_a = blocks_list[i].a + blocks_list[i].size
        end_idx_a = blocks_list[i + 1].a
        start_idx_b = blocks_list[i].b + blocks_list[i].size
        end_idx_b = blocks_list[i + 1].b
        block_pairs.append([s1[start_idx_a:end_idx_a], s2[start_idx_b:end_idx_b]])
        unmatched_block_idxs.append(len(block_pairs) - 1)

    # Add final block
    start_idx_a = blocks_list[-1].a
    end_idx_a = blocks_list[-1].a + blocks_list[-1].size
    start_idx_b = blocks_list[-1].b
    end_idx_b = blocks_list[-1].b + blocks_list[-1].size
    block_pairs.append([s1[start_idx_a:end_idx_a], s2[start_idx_b:end_idx_b]])

    # If the final block does not cover the sentence add the trailing unmatched block
    if end_idx_a != len(s1) or end_idx_b != len(s2):
        start_idx_a = blocks_list[-1].a + blocks_list[-1].size
        end_idx_a = len(s1)
        start_idx_b = blocks_list[-1].b + blocks_list[-1].size
        end_idx_b = len(s2)
        block_pairs.append([s1[start_idx_a:end_idx_a], s2[start_idx_b:end_idx_b]])
        unmatched_block_idxs.append(len(block_pairs) - 1)

    # Concatenate words within blocks
    block_pairs = [(" ".join(x1), " ".join(x2)) for x1, x2 in block_pairs]
    return block_pairs, unmatched_block_idxs
