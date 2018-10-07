'''
Created on 11.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, KeywordArgTuple


def preserve_gaps(boolean):
    return KeywordArgTuple('preserve_gaps', boolean)


mock_switch_file_ranges = mock.MagicMock(name='switch_file_ranges')

@mock.patch('FileSet.FileSet.switch_file_ranges', new=mock_switch_file_ranges)
class SwitchFilesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_pattern = ('test (', ')')
        cls.test_set = FileSet(test_pattern, [])
        
    def tearDown(self):
        mock_switch_file_ranges.reset_mock()
    
    
    def test_correct_argument_passing(self):
        """The switch_files method should pass its arguments to switch_file_ranges, since it's actually just a special use case of that method."""
        self.test_set.switch_files(1, 2, True)
        
        mock_assert_msg(mock_switch_file_ranges.assert_called_once_with, [(1, 1), (2, 2), preserve_gaps(True)], "The method fails to pass the correct arguments to switch_file_ranges.") 
        
    def test_default_strict_true(self):
        """The switch_files method should use allow_gaps=False by default."""
        self.test_set.switch_files(1, 2)
        
        mock_assert_msg(mock_switch_file_ranges.assert_called_once_with, [(1, 1), (2, 2), preserve_gaps(False)], "The method fails to pass the correct arguments along with True for mode strict as the default argument to switch_file_ranges.")
    
    def test_invalid_single_index(self):
        """The switch_files method should raise an error if the given indexes to switch aren't single integers."""
        with self.assertRaises(TypeError, msg="The method fails to recognize an invalid single index."):
            self.test_set.switch_files((1, 2), 6)
            
        with self.assertRaises(TypeError, msg="The method fails to recognize an invalid single index if it's given as the second one."):
            self.test_set.switch_files(1, (3, 4))
            
        mock_assert_msg(mock_switch_file_ranges.assert_not_called, [], "The method tries to switch files even though it has run into an error.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()