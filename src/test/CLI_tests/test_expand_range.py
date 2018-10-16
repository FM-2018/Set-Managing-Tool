'''
Created on 24.08.2018

@author: FM
'''
import unittest
from CLI import _expand_range, RangeExpansionError


class ExpandRangeTests(unittest.TestCase):

    def test_expand_valid_range(self):
        """The CLI should be able to process a valid range."""
        self.assertEqual(_expand_range('1-3'), (1, 3), "The CLI fails to expand a valid range into a range tuple.")
    
    def test_expand_valid_range_reverse_order(self):
        """The CLI should be able to correctly process a range even if it's given in reverse order."""
        self.assertEqual(_expand_range('3-2'), (2, 3), "The CLI doesn't return the bounds of the expanded range in the correct order.")
    
    def test_single_integer_range(self):
        """The CLI should turn a single integer into an according range."""
        self.assertEqual(_expand_range('4'), (4, 4), "The CLI doesn't convert single integers into a range.")
    
    def test_invalid_integer_range(self):
        """The CLI should be able to recognize a range containing invalid integers and raise an error accordingly."""
        with self.assertRaises(RangeExpansionError, msg="The CLI fails to recognize an invalid range with invalid integers."):
            _expand_range('a4-3')
    
    def test_invalid_too_many_integers_range(self):
        """The CLI should be able to recognize a range with too many integers and raise an error."""
        with self.assertRaises(RangeExpansionError, msg="The CLI fails to recognize an invalid range with too many integers."):
            _expand_range('1-2-3')
        
    def test_invalid_range_separator(self):
        """The CLI should be able to recognize an invalid range separator and raise an error accordingly."""
        with self.assertRaises(RangeExpansionError, msg="The CLI fails to recognize a range with an invalid separator."):
            _expand_range('5/6')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()