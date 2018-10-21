'''
Created on 21.10.2018

@author: FM
'''
import unittest
from FileSet import FileSet
import unittest.mock as mock
import CLI
from test.testing_tools import mock_assert_msg


mock_expand_pattern = mock.MagicMock(name="_expand_pattern")
mock_files_detected = mock.MagicMock(name="FileSet.files_detected")

@mock.patch("CLI._expand_pattern", new=mock_expand_pattern)
@mock.patch("CLI.FileSet.files_detected", new=mock_files_detected)
class CreateTests(unittest.TestCase):
    
    def tearDown(self):
        mock_expand_pattern.reset_mock()
        mock_files_detected.reset_mock()
        
        mock_expand_pattern.side_effect = None
        mock_expand_pattern.return_value = None
        

    def test_too_many_arguments(self):
        """The method should recognize and raise an error if too many arguments are given."""
        test_args = ['create', 'new*pattern', 'another']
        
        with self.assertRaises(CLI.ArgumentAmountError, msg="The method fails to recognize and raise an error when too many arguments are given."):
            CLI.create(test_args)
        
        mock_assert_msg(mock_files_detected.assert_not_called, [], "The method creates a file set even though an error was raised.")
    
    def test_too_few_arguments(self):
        """The method should recognize and raise an error if too few arguments are given."""
        test_args = ['create']
        
        with self.assertRaises(CLI.ArgumentAmountError, msg="The method fails to recognize and raise an error when too few arguments are given."):
            CLI.create(test_args)
        
        mock_assert_msg(mock_files_detected.assert_not_called, [], "The method creates a file set even though an error was raised.")
    
    def test_invalid_pattern(self):
        """The method should recognize and raise an error if the given pattern is invalid."""
        test_args = ['create', 'new']
        
        mock_expand_pattern.side_effect = CLI.PatternExpansionError("Pattern expansion failed")
        
        with self.assertRaises(CLI.InputProcessingError, msg="The method fails to recognize and raise an error when too few arguments are given."):
            CLI.create(test_args)
        
        mock_assert_msg(mock_files_detected.assert_not_called, [], "The method creates a file set even though an error was raised.")
    
    def test_create_new_set(self):
        """The method should recognize when it's safe to create the new file set and then actually perform this action to return it."""
        test_args = ['create', 'new*pattern']
        mock_expand_pattern.return_value = ('new', 'pattern')
        
        CLI.file_set_cache = []
        
        new_set = FileSet(('new', 'pattern'), [])
        mock_files_detected.return_value = new_set
        
        new_active_set = CLI.create(test_args)
        
        mock_assert_msg(mock_files_detected.assert_called_once_with, [('new', 'pattern')], "The method fails to create a new file set correctly.")
        self.assertEqual(new_active_set, new_set, "The method fails to return the newly created file set.")
        
    def test_set_already_exists(self):
        """The method should select and return the existent file set if one with the same pattern exists within the file_set_cache."""
        test_args = ['create', 'new*pattern']
        mock_expand_pattern.return_value = ('new', 'pattern')
        
        existing_set = FileSet(('new', 'pattern'), [])
        CLI.file_set_cache = [existing_set]
        
        new_active_set = CLI.create(test_args)
        
        mock_assert_msg(mock_files_detected.assert_not_called, [], "The method tries to create a new file set, even though one with the same pattern already exists.")
        self.assertEqual(new_active_set, existing_set, "The method fails to return the already existent file set.")
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()