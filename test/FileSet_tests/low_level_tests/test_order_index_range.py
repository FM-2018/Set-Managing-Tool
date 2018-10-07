'''
Created on 27.08.2018

@author: FM
'''
import unittest
from FileSet import FileSet

class OrderIndexRangeTests(unittest.TestCase):

    def test_adjacent_right_order(self):
        """The method should pass back a correctly ordered range with adjacent numbers."""
        test_range = (1, 2)
        result_range = FileSet._order_index_range(test_range)
        
        self.assertEqual(result_range, (1, 2), "The method fails to return an already correctly ordered range.")
        
    def test_wide_right_order(self):
        """The method should pass back a correctly ordered range with non-adjacent numbers."""
        test_range = (2, 5)
        result_range = FileSet._order_index_range(test_range)
        
        self.assertEqual(result_range, (2, 5), "The method fails to return an already correctly ordered range.")
    
    def test_adjacent_false_order(self):
        """The method should order a falsely ordered range with adjacent numbers before returning it."""
        test_range = (2, 1)
        result_range = FileSet._order_index_range(test_range)
        
        self.assertEqual(result_range, (1, 2), "The method fails to order an incorrectly ordered range.")
    
    def test_wide_false_order(self):
        """The method should order a falsely ordered range with non-adjacent numbers before returning it."""
        test_range = (5, 2)
        result_range = FileSet._order_index_range(test_range)
        
        self.assertEqual(result_range, (2, 5), "The method fails to order an incorrectly ordered range.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()