'''
Created on 24.08.2018

@author: FM
'''
import unittest
from CLI import check_contains_invalid_chars

class ContainsInvalidCharsTests(unittest.TestCase):


    def test_valid_name(self):
        """The CLI should be able to recognize a string without invalid characters."""
        test_string = "hello"
        self.assertFalse(check_contains_invalid_chars(test_string), "The CLI finds invalid characters in a name when there actually are none.")
        
    def test_strange_but_valid_name(self):
        """The CLI should be able to recognize a string without invalid characters, even if it looks peculiar.""" 
        test_string = "t,e.s,t.mp3"
        self.assertFalse(check_contains_invalid_chars(test_string), "The CLI finds invalid characters in a name when there actually are none.")
        
    def test_invalid_name(self):
        """The CLI should be able to recognize a string with an invalid character."""
        test_string = "?.txt"
        self.assertTrue(check_contains_invalid_chars(test_string), "The FileSet fails to find invalid characters in a file name or pattern.")
        
    def test_very_invalid_name(self):
        """The CLI should be able to recognize a string with multiple invalid characters."""
        test_string = "https://www.star*star>>.com"
        self.assertTrue(check_contains_invalid_chars(test_string), "The FileSet fails to find invalid characters in a file name or pattern.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()