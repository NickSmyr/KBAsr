import unittest

from utils.seqmatch import blocks


class TestBlocks(unittest.TestCase):
    def test_blcks_no_initial_unmatched_no_trailing_unmatched(self):
        s1 = "My name is Nikos noice too mit you"
        s2 = "My aaaa Nikos nice to meet you"
        block_list, unmatched_idxs = blocks(s1,s2)
        self.assertEqual(block_list[0], ("My","My"))
        unmatched_blocks_true = [
            ("name is" , "aaaa"),
            ("noice too mit", "nice to meet")
        ]
        self.assertEqual(block_list[-1], ("you", "you"))
        self.unmatched_blocks_test(block_list, unmatched_blocks_true, unmatched_idxs)

    def test_blcks_initial_unmatched(self):
        s1 = "aa My name is Nikos noice too mit you"
        s2 = "My aaaa Nikos nice to meet you"
        block_list, unmatched_idxs = blocks(s1, s2)
        self.assertEqual(block_list[0], ("aa", ""))
        unmatched_blocks_true = [
            ("aa", ""),
            ("name is", "aaaa"),
            ("noice too mit", "nice to meet")
        ]
        self.unmatched_blocks_test(block_list, unmatched_blocks_true, unmatched_idxs)

    def test_blcks_trailing_unmatched(self):
        s1 = "aa My name is Nikos noice too mit you zo"
        s2 = "My aaaa Nikos nice to meet you zz"
        block_list, unmatched_idxs = blocks(s1, s2)
        self.assertEqual(block_list[-1], ("zo", "zz"))
        unmatched_blocks_true = [
            ("aa", ""),
            ("name is", "aaaa"),
            ("noice too mit", "nice to meet"),
            ("zo", "zz")
        ]
        self.unmatched_blocks_test(block_list, unmatched_blocks_true, unmatched_idxs)

    def test_blcks_no_matching_blocks(self):
        s1 = "aa zz"
        s2 = "bb cc"
        block_list, unmatched_idxs = blocks(s1, s2)
        # Assert only one block is present
        self.assertEqual(len(block_list),1)
        unmatched_blocks_true = [
            ("aa zz", "bb cc"),
        ]
        self.unmatched_blocks_test(block_list, unmatched_blocks_true, unmatched_idxs)

    def unmatched_blocks_test(self, block_list, unmatched_blocks_true, unmatched_idxs):
        """
        Test that the true given unmatched blocks are equal to the unmatched blocks in
        the outpt block list indexed by unmatched_idxs
        :param block_list:
        :param unmatched_blocks_true:
        :param unmatched_idxs:
        :return:
        """
        for i, idx in enumerate(unmatched_idxs):
            self.assertEqual(block_list[idx], unmatched_blocks_true[i])


if __name__ == '__main__':
    unittest.main()
