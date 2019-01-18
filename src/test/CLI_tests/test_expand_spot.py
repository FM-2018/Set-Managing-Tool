'''
Created on 01.09.2018

@author: FM
'''
import unittest
from CLI import _expand_spot, SpotExpansionError


class ExpandSpotTests(unittest.TestCase):


    def test_valid_spot(self):
        """The CLI should be able to expand a valid spot."""
        result_spot = _expand_spot('5/6')
        
        self.assertEqual(result_spot, (5, 6), "The CLI fails to process a valid spot.")
        
    def test_valid_spot_reverse_order(self):
        """The CLI should be able to expand a valid spot that's given from higher to lower."""
        result_spot = _expand_spot('6/5')
        
        self.assertEqual(result_spot, (5, 6), "The CLI fails to process a valid spot that's given in reverse order.")
    
    def test_invalid_spot(self):
        """The CLI should be able to recognize an invalid a spot which's indexes aren't adjacent and raise an error."""
        with self.assertRaises(SpotExpansionError, msg="The CLI fails to recognize an invalid spot."):
            _expand_spot('5/8')
    
    def test_invalid_int_spot(self):
        """The CLI should be able to recognize a spot containing invalid integers (i.e. letters)"""
        with self.assertRaises(SpotExpansionError, msg="The CLI fails to recognize a spot containing invalid integers."):
            _expand_spot('5/d5')
            
        with self.assertRaises(SpotExpansionError, msg="The CLI fails to recognize a spot containing invalid integers."):
            _expand_spot('a4/5')
    
    def test_invalid_spot_separator(self):
        """The CLI should be able to recognize an invalid spot separator and raise an error accordingly."""
        with self.assertRaises(SpotExpansionError, msg="The CLI fails to deal with a spot that has an invalid spot separator."):
            _expand_spot('5-6')
    
    def test_single_integer_spot(self):
        """The CLI should be able to recognize a single-integer spot and raise an error accordingly."""
        with self.assertRaises(SpotExpansionError, msg="The CLI fails to deal with a spot that's given only as a single integer."):
            _expand_spot('5') 
    
    def test_same_integer_spot(self):
        """The CLI should raise an error when the spot contains the same integer twice, i.e. 'n/n'."""
        with self.assertRaises(SpotExpansionError, msg="The CLI fails to deal with a spot that contains the same integer twice."):
            _expand_spot('5/5')
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()