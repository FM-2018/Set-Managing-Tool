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


mock_move_files = mock.MagicMock(name='move_files')

@mock.patch('FileSet.FileSet.move_files', new=mock_move_files)
class MoveFileTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        test_pattern = ('test (', ')')
        cls.test_set = FileSet(test_pattern, [])

    def tearDown(self):
        mock_move_files.reset_mock()
    
    
    def test_correct_argument_passing(self):
        """The move_file method should pass its argument to move_files, since it's just a special use case of that method."""
        self.test_set.move_file(1, (2, 3), True)
        
        mock_assert_msg(mock_move_files.assert_called_once_with, [(1, 1), (2, 3), preserve_gaps(True)], "The methods fails to call move_files with the correct arguments.")
        
    def test_default_allow_gaps_false(self):
        """The move_file method should not allow gaps by default."""
        self.test_set.move_file(1, (2, 3))
        
        mock_assert_msg(mock_move_files.assert_called_once_with, [(1, 1), (2, 3), preserve_gaps(False)], "The methods fails to call move_files with the correct arguments, including the correct default value for allow_gaps.")
    
    def test_invalid_single_index(self):
        """The move_file method should raise an error if it's called with anything other than an integer for a single index."""
        with self.assertRaises(TypeError, msg="The method fails to recognize when it's not given a single integer to move."):
            self.test_set.move_file((1, 2), (2, 3)) # an index range should cause an error
        
        mock_assert_msg(mock_move_files.assert_not_called, [], "The methods tries to move files even though an error was raised.")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()