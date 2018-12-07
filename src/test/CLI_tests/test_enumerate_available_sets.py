'''
Created on 07.12.2018

@author: FM
'''
import unittest
import CLI
from FileSet import FileSet
import unittest.mock as mock
from test.testing_tools import mock_assert_msg, mock_assert_many_msg

mock_print = mock.MagicMock(name='print')


@mock.patch("CLI.print", new=mock_print)
class TestEnumerateAvailableSets(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')

    def tearDown(self):
        mock_print.reset_mock()

    def test_no_sets(self):
        """The method should notify the user if no file sets are available."""
        CLI.file_set_cache = []
        
        CLI._enumerate_available_sets()
        
        mock_assert_msg(mock_print.assert_called_once_with, ["No file sets have been found in this directory."], 
                        "The method fails to notify the user if no file sets are available.")
        
    def test_one_set(self):
        """The method should list the set if only a single one has been found."""
        test_set = FileSet(self.pattern, [])
        
        CLI.file_set_cache = [test_set]
        
        CLI._enumerate_available_sets()
        
        mock_assert_msg(mock_print.assert_called_once_with, [0, '\t', str(test_set)], 
                        "The method fails to list a single available file set.")
        
    def test_multiple_sets(self):
        """The method should list all the sets if multiple of them have been found."""
        test_set1 = FileSet(self.pattern, [])
        test_set2 = FileSet(('second', ''), [])
        test_set3 = FileSet(('x', 'y'), [])
        
        CLI.file_set_cache = [test_set1, test_set2, test_set3]
        
        CLI._enumerate_available_sets()
        
        assertion_calls = [
                (mock_print.assert_any_call, [0, '\t', str(test_set1)]),
                (mock_print.assert_any_call, [1, '\t', str(test_set2)]),
                (mock_print.assert_any_call, [2, '\t', str(test_set3)])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to list all of the multiple available file sets.")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
