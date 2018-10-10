'''
Created on 05.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from CLI import move, CLIRuntimeError, SpotExpansionError,\
    RangeExpansionError, ArgumentAmountError, InputProcessingError
from test.testing_tools import mock_assert_msg, KeywordArgTuple


mock_expand_spot = mock.MagicMock(name='_expand_spot')
mock_expand_range = mock.MagicMock(name='_expand_range')
mock_move_files = mock.MagicMock(name='FileSet.move_files')

@mock.patch('CLI._expand_spot', new=mock_expand_spot)
@mock.patch('CLI._expand_range', new=mock_expand_range)
@mock.patch('FileSet.FileSet.move_files', new=mock_move_files)
class MoveTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_set = FileSet(('test (', ')'), [])
    
    def tearDown(self):
        mock_expand_spot.reset_mock()
        mock_expand_range.reset_mock()
        mock_move_files.reset_mock()
        
        mock_expand_range.side_effect = None
        mock_expand_spot.side_effect = None
    

    def test_valid_arguments(self):
        """The CLI should be able to perform a movement operation given valid arguments."""
        test_args = ['3-5', '>', '1/2']
        mock_expand_spot.return_value = (1, 2)
        mock_expand_range.return_value = (3, 5)
        
        move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_called_once_with, [(3, 5), (1, 2)], "The CLI fails to perform a movement operation with valid arguments.")
    
    def test_valid_single_file_range(self):
        """The CLI should be able to perform a movement operation given a single-file range."""
        test_args = ['3', '>', '1/2']
        mock_expand_spot.return_value = (1, 2)
        mock_expand_range.return_value = (3, 3)
        
        move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_called_once_with, [(3, 3), (1, 2)], "The CLI fails to perform a movement operation with a valid single-file range.")
        
    def test_invalid_range(self):
        """The CLI should recognize an invalid range and raise an error."""
        test_args = ['invalid_range', '>', '1/2']
        mock_expand_spot.return_value = (1, 2)
        mock_expand_range.side_effect = RangeExpansionError()
        
        with self.assertRaises(RangeExpansionError, msg="The CLI fails to recognize an invalid range."):
            move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_not_called, [], "The CLI attempts to perform a movement operation even though the range is invalid.")
        
    def test_invalid_spot(self):
        """The CLI should recognize an invalid spot and raise an error."""
        test_args = ['3-5', '>', 'invalid_spot']
        mock_expand_spot.side_effect = SpotExpansionError()
        mock_expand_range.return_value = (3, 5)
        
        with self.assertRaises(SpotExpansionError, msg="The CLI fails to recognize an invalid spot."):
            move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_not_called, [], "The CLI attempts to perform a movement operation even though the spot is invalid.")
        
    def test_no_active_file_set(self):
        """The CLI should be able to recognize and raise an error if no file set is selected to perform the action on."""
        test_args = ['3-5', '>', '1/2']
        mock_expand_spot.return_value = (1, 2)
        mock_expand_range.return_value = (3, 5)
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when there is no selected file set."):
            move(None, test_args)
        
        mock_assert_msg(mock_move_files.assert_not_called, [], "The CLI attempts to perform a movement operation even though no file set is selected.")
    
    def test_too_few_arguments(self):
        """The CLI should recognize and raise an error when too few arguments are given."""
        test_args = ['2-3', '>']
        mock_expand_range.return_value = (2, 3)
        
        with self.assertRaises(ArgumentAmountError, msg="The FileSet fails to recognize when too few arguments are given."):
            move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_not_called, [], "The CLI attempts to perform a switch operation even though there was an invalid number of arguments.")
        
    def test_too_many_arguments(self):
        """The CLI should recognize and raise an error when too many arguments are given."""
        test_args = ['2-3', '>', '4/5', 'x', 'y']
        mock_expand_range.return_value = (2, 3)
        mock_expand_spot.return_value = (4, 5)
        
        with self.assertRaises(ArgumentAmountError, msg="The FileSet fails to recognize when too many arguments are given."):
            move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_not_called, [], "The CLI attempts to perform a switch operation even though there was an invalid number of arguments.")
        
    def test_kwarg_strip_gaps(self):
        """The CLI should enable the user to choose strip_gaps as a gap handling method."""
        test_args = ['2-3', '>', '4/5', '-sg']
        mock_expand_range.return_value = (2, 3)
        mock_expand_spot.return_value = (4, 5)
        
        move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_called_once_with, [(2, 3), (4, 5), KeywordArgTuple('strip_gaps', True)], "The CLI fails to provide access to the gap-handling option strip_gaps.")
        
    def test_kwarg_preserve_gaps(self):
        """The CLI should enable the user to choose preserve_gaps as a gap handling method."""
        test_args = ['2-3', '>', '4/5', '-pg']
        mock_expand_range.return_value = (2, 3)
        mock_expand_spot.return_value = (4, 5)
        
        move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_called_once_with, [(2, 3), (4, 5), KeywordArgTuple('preserve_gaps', True)], "The CLI fails to provide access to the gap-handling option strip_gaps.")

    def test_invalid_kwarg_gap_handler(self):
        """The CLI should recognize and raise an error if an invalid gap-handling option was chosen."""
        test_args = ['2-3', '>', '4/5', '-xx']
        mock_expand_range.return_value = (2, 3)
        mock_expand_spot.return_value = (4, 5)
        
        with self.assertRaises(InputProcessingError, msg="The CLI fails to recognize and raise an error when an invalid gap-handling option was chosen"):
            move(self.test_set, test_args)
        
        mock_assert_msg(mock_move_files.assert_not_called, [], "The CLI tries to eprform an operation even though an error was raised.")
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()