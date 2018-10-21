'''
Created on 21.10.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
import CLI
from test.testing_tools import mock_assert_msg

mock_enumerate_sets = mock.MagicMock(name="_enumerate_available_sets")

@mock.patch("CLI._enumerate_available_sets", new=mock_enumerate_sets)
class ChooseTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_set0 = FileSet(('set0', ''), [])
        cls.test_set1 = FileSet(('set1', ''), [])
        cls.test_set2 = FileSet(('set2', ''), [])
    
    def tearDown(self):
        mock_enumerate_sets.reset_mock()
        
        CLI.file_set_cache = []
        CLI.active_file_set = []
    
    
    def test_valid_existent_set_number(self):
        """The method should update the active file set if a valid set number is given."""
        test_args = ['choose', '1']
        
        CLI.file_set_cache = [self.test_set0, self.test_set1]
        
        CLI.choose(None, test_args)
        
        mock_assert_msg(mock_enumerate_sets.assert_not_called, [], "The method lists file sets even though a set number was supplied.")
        self.assertEqual(CLI.active_file_set, self.test_set1, "The method fails to select the correct file set given the cache set number.")
        
    def test_invalid_set_number(self):
        """The method should recognize and raise an error when the set number given is not a valid integer."""
        test_args = ['choose', '2a']
        
        CLI.file_set_cache = [self.test_set0, self.test_set1]
        
        with self.assertRaises(CLI.InputProcessingError, msg="The method fails to recognize when an invalid integer is given as the set number."):
            CLI.choose(None, test_args)
        
        mock_assert_msg(mock_enumerate_sets.assert_not_called, [], "The method lists file sets even though an error was raised.")
        
    def test_set_not_existent(self):
        "The method should recognize and raise an error when the given set number doesn't point to a FileSet."
        test_args = ['choose', '3']
        
        CLI.file_set_cache = [self.test_set0, self.test_set1]
        
        with self.assertRaises(CLI.CLIRuntimeError, msg="The method fails to recognize when a given file set number doesn't exist."):
            CLI.choose(None, test_args)
        
        mock_assert_msg(mock_enumerate_sets.assert_not_called, [], "The method lists file sets even though an error was raised.")
        
    def test_list_available_sets(self): 
        """The method should run _enumerate_available_sets if no number is given."""
        test_args = ['choose']
        
        CLI.file_set_cache = [self.test_set0, self.test_set1]
        
        CLI.choose(None, test_args)
        
        mock_assert_msg(mock_enumerate_sets.assert_called_once, [], "The method fails to call _enumerate_file_sets when no set number is given.")
        
    def test_too_many_arguments(self):
        """The method should recognize and raise an error if more than 2 arguments are given."""
        test_args = ['choose', '3', '4']
        
        CLI.file_set_cache = [self.test_set0, self.test_set1]
        
        with self.assertRaises(CLI.ArgumentAmountError, msg="The method fails to recognize when too many arguments are given."):
            CLI.choose(None, test_args)
        
        mock_assert_msg(mock_enumerate_sets.assert_not_called, [], "The method lists file sets even though an error was raised.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()