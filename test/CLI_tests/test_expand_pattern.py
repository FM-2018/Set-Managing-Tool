'''
Created on 07.09.2018

@author: FM
'''
import unittest
from CLI import _expand_pattern, PatternExpansionError

class ExpandPatternTests(unittest.TestCase):
    
    def test_valid_pattern(self):
        """The CLI should be able to expand a valid pattern."""
        test_pattern = 'custom*set'
        
        pattern = _expand_pattern(test_pattern)
        
        self.assertEqual(pattern, ('custom', 'set'), "The CLI fails to expand a simple valid custom pattern.")
        
    def test_pattern_too_many_asterisks(self):
        """The CLI should raise an error if too many asterisks, i.e. index indicators have been entered."""
        test_pattern = 'my*custom*set'
        
        with self.assertRaises(PatternExpansionError, msg="The CLI fails to recognize an invalid pattern with too many asterisks."):
            _expand_pattern(test_pattern)
        
    def test_pattern_no_asterisk(self):
        """The CLI should raise an error if no asterisk, i.e. index indicator has been entered."""
        test_pattern = 'my_set'
        
        with self.assertRaises(PatternExpansionError, msg="The CLI fails to recognize an invalid pattern with no asterisk."):
            _expand_pattern(test_pattern)
        
    def test_escape_asterisk(self):
        """The CLI should enable the user to escape an asterisk with a backslash (\)."""
        test_pattern = r'my*custom\*set'
        
        try:
            pattern = _expand_pattern(test_pattern)
        except PatternExpansionError:
            self.fail("The CLI fails to escape an asterisk when it's preceded by a backslash (\).")
        
        self.assertEqual(pattern, ('my', 'custom*set'), "The CLI fails to correctly expand a pattern with an escaped asterisk.")
        
    def test_escape_backslash_asterisk(self):
        """The CLI should enable to escape a backslash (\) in front of an asterisk (*) with another backslash."""
        test_pattern = r'custom\\*set'
        
        try:
            pattern = _expand_pattern(test_pattern)
        except PatternExpansionError:
            self.fail("The CLI fails to escape an asterisk-preceding backslash when it's preceded by another backslash (\).")
        
        self.assertEqual(pattern, ('custom\\', 'set'), "The CLI fails to correctly expand a pattern with an escaped backslash.")
    
    def test_escape_backslash_before_asterisk(self):
        """The ClI should enable the user to escape a backslash right before an asterisk-escaping backslash."""
        test_pattern = r'cus*tom\\\*set'
        
        try:
            pattern = _expand_pattern(test_pattern)
        except PatternExpansionError:
            self.fail("The CLI fails to escape a backslash right before an asterisk-excaping backslash.")
        
        self.assertEqual(pattern, ('cus', 'tom\\*set'), "The CLI fails to correctly expand a pattern with an escaped backslash and escaped asterisk following each other.")
    
    ## TODO: make this file system dependent rather than OS dependent
    def test_pattern_invalid_characters_windows(self):
        """The CLI should raise an error if the pattern contains invalid characters for Windows."""
        
    def test_pattern_invalid_characters_mac(self):
        """The CLI should raise an error if the pattern contains invalid characters for Max OS."""

    def test_pattern_invalid_characters_linux(self):
        """The CLI should raise an error if the pattern contains invalid characters for Linux."""
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()