'''
Created on 14.10.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
import CLI
from test.testing_tools import mock_assert_msg


mock_change_pattern = mock.MagicMock(name="change_pattern")
mock_expand_pattern = mock.MagicMock(name="_expand_pattern")

@mock.patch('FileSet.FileSet.change_pattern', new=mock_change_pattern)
@mock.patch("CLI._expand_pattern", new=mock_expand_pattern)
class RenameTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.normal_pattern = ('test (', ')')
        cls.new_pattern = ('new', '')
        cls.test_set = FileSet(cls.normal_pattern, [])
    
    def tearDown(self):
        mock_change_pattern.reset_mock()
        
        mock_expand_pattern.side_effect = None
        
        CLI.file_set_cache = []
        
    
    def test_valid_arguments(self):
        """The method should correctly perform its operation if its given valid arguments."""
        test_args = ['rename', 'new*']
        mock_expand_pattern.return_value = self.new_pattern
        
        CLI.rename(self.test_set, test_args)
        
        mock_assert_msg(mock_change_pattern.assert_called_once_with, [self.new_pattern], "The method fails to perform the change_pattern operation correctly.")
    
    def test_invalid_pattern(self):
        """The method should recognize and raise an error if it is given an invalid pattern."""
        test_args = ['rename', 'newInvalid']
        mock_expand_pattern.side_effect = CLI.PatternExpansionError("Invalid pattern")
        
        with self.assertRaises(CLI.PatternExpansionError, msg="The method fails to recognize and raise an error if given an invalid pattern."):
            CLI.rename(self.test_set, test_args)
        
        mock_assert_msg(mock_change_pattern.assert_not_called, [], "The method tries to perform an operation even though an error was raised.")
    
    def test_no_file_set_selected(self):
        """The method should recognize and raise an error if no file set was selected / i.e. the file set is passed as None."""
        test_args = ['rename', 'new*']
        mock_expand_pattern.return_value = self.new_pattern
        
        with self.assertRaises(CLI.CLIRuntimeError, msg="The method fails to recognize and raise an error if no file set is selected."):
            CLI.rename(None, test_args)
        
        mock_assert_msg(mock_change_pattern.assert_not_called, [], "The method tries to perform an operation even though an error was raised.")
        
    def test_too_few_arguments(self):
        """The method should recognize and raise an error if it is given too few arguments."""
        test_args = ['rename']
        
        with self.assertRaises(CLI.ArgumentAmountError, msg="The method fails to recognize and raise an error if too few arguments are given."):
            CLI.rename(self.test_set, test_args)
        
        mock_assert_msg(mock_change_pattern.assert_not_called, [], "The method tries to perform an operation even though an error was raised.")
        
    def test_too_many_arguments(self):
        """The method should recognize and raise an error if it is given too many arguments."""
        test_args = ['rename', 'new*', 'extra']
        mock_expand_pattern.return_value = self.new_pattern
        
        with self.assertRaises(CLI.ArgumentAmountError, msg="The method fails to recognize and raise an error if too many arguments are given."):
            CLI.rename(self.test_set, test_args)
        
        mock_assert_msg(mock_change_pattern.assert_not_called, [], "The method tries to perform an operation even though an error was raised.")
    
    def test_set_same_pattern_already_exists(self):
        """The method should recognize and raise an error if a file set with the same pattern is already registered in the file_set_cache."""
        test_args = ['rename', 'new*']
        mock_expand_pattern.return_value = self.new_pattern
        
        new_set = FileSet(('new', ''), [])
        CLI.file_set_cache = [new_set]
        
        with self.assertRaises(CLI.CLIRuntimeError, msg="The metod fails to recognize and raise an error if a file set with the new pattern already exists."):
            CLI.rename(self.test_set, test_args)
        
        mock_assert_msg(mock_change_pattern.assert_not_called, [], "The method tries to perform an operation even though an error was raised.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()