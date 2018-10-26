'''
Created on 26.10.2018

@author: fabian
'''
import unittest
import unittest.mock as mock
import CLI
from FileSet import FileSet
from test.testing_tools import mock_assert_msg


mock_fix = mock.MagicMock(name="FileSet.fix")

@mock.patch("FileSet.FileSet.fix", new=mock_fix)
class CliFixTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_set = FileSet(('test (', ')'), [])
    
    def tearDown(self):
        mock_fix.reset_mock()
        
        mock_fix.side_effect = None
    
    
    def test_normal_fix(self):
        """The method should perform a gap-only fix if no further arguments are given."""
        test_args = ['fix']
        
        CLI.fix(self.test_set, test_args)
        
        mock_assert_msg(mock_fix.assert_called_once_with, [], "The method fails to initiate a basic fix if no further arguments are given.")
        
    def test_full_fix(self):
        """The method should perform a complete fix if the additional keyword 'all' is given."""
        test_args = ['fix', 'all']
        
        CLI.fix(self.test_set, test_args)
        
        mock_assert_msg(mock_fix.assert_called_once_with, [True], "The method fails to initiate a full fix if the appropriate arguments are given.")
        
    def test_no_file_set_selected(self):
        """The method should recognize and raise an error if no file set is selected."""
        test_args = ['fix']
        
        with self.assertRaises(CLI.CLIRuntimeError, msg="The method fails to recognize when no file set is selected."):
            CLI.fix(None, test_args)
        
        mock_assert_msg(mock_fix.assert_not_called, [], "The method tries to perform a fix operation even though an error was raised.")
        
    def test_too_many_arguments(self):
        """The method should recognize and raise an error if too many arguments are given."""
        test_args = ['fix', 'all', 'now']
        
        with self.assertRaises(CLI.ArgumentAmountError, msg="The method fails to recognize when too many arguments are given."):
            CLI.fix(self.test_set, test_args)
        
        mock_assert_msg(mock_fix.assert_not_called, [], "The method tries to perform a fix operation even though an error was raised.")
    
    def test_invalid_second_argument(self):
        """The method should recognize and raise an error if the second given argument is not 'all'."""
        test_args = ['fix', 'arg']
        
        with self.assertRaises(CLI.InputProcessingError, msg="The method fails to recognize when an invalid second argument is given."):
            CLI.fix(self.test_set, test_args)
        
        mock_assert_msg(mock_fix.assert_not_called, [], "The method tries to perform a fix operation even though an error was raised.")
    
    def test_set_with_too_many_files(self):
        """The method should raise a CLIRuntimeError if the file set has too many files to perform 'fix all'."""
        test_args = ['fix', 'all']
        mock_fix.side_effect = FileSet.TooManyFilesError("Too many files.")
                
        with self.assertRaises(CLI.CLIRuntimeError, msg="The method fails to react correctly when the file set contains too many files to fix all."):
            CLI.fix(self.test_set, test_args)

        mock_assert_msg(mock_fix.assert_called_once_with, [True], "The method doesn't actually try to perform the fix operation.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()