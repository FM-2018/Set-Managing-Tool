'''
Created on 05.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from CLI import switch, RangeExpansionError, CLIRuntimeError, ArgumentAmountError,\
    InputProcessingError
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, KeywordArgTuple


mock_expand_range = mock.MagicMock(name='_expand_range')
mock_switch_file_ranges = mock.MagicMock(name='FileSet.switch_file_ranges')

@mock.patch('CLI._expand_range', new=mock_expand_range)
@mock.patch('FileSet.FileSet.switch_file_ranges', new=mock_switch_file_ranges)
class SwitchTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_set = FileSet(('test (', ')'), [])
    
    def tearDown(self):
        mock_expand_range.reset_mock()
        mock_switch_file_ranges.reset_mock()
    
    
    def test_valid_ranges(self):
        """The CLI should be able to perform a valid switch operation."""
        test_args = ['2-3', '~', '4-5']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_called_once_with, [(2, 3), (4, 5)], "The CLI fails to perform a switch operation with two valid file ranges.")
        
    def test_single_int_ranges(self):
        """The CLI should be able to process ranges that are given as single integers."""
        test_args = ['2', '~', '4']
        mock_expand_range.side_effect = lambda x: (2, 2) if x == '2' else (4, 4)
        
        switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_called_once_with, [(2, 2), (4, 4)], "The CLI fails to perform a switch operation with two valid single-file ranges.")
        
    def test_invalid_range(self):
        """The CLI should be able to recognize an invalid range and raise and error."""
        test_args = ['2', '~', 'not_a_range']
        def mock_expand_range_side_effect(x):
            if x == 2:
                return (2, 2)
            else:
                raise RangeExpansionError("invalid range 'not a range'")
        mock_expand_range.side_effect = mock_expand_range_side_effect
        
        with self.assertRaises(RangeExpansionError, msg="The CLI fails to recognize an invalid range in the switch operation."):
            switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_not_called, [], "The CLI attempts to perform a switch operation even though a range is invalid.")
        
    def test_no_active_file_set(self):
        """The CLI should recognize when no file set is selected and raise an error."""
        test_args = ['2-3', '~', '4-5']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when no file set has been selected."):
            switch(None, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_not_called, [], "The CLI attempts to perform a switch operation even though no file set is selected.")
    
    def test_too_few_arguments(self):
        """The CLI should recognize and raise an error when too few arguments are given."""
        test_args = ['2-3', '~']
        mock_expand_range.side_effect = lambda x: (2, 3)
        
        with self.assertRaises(ArgumentAmountError, msg="The FileSet fails to recognize when too few arguments are given."):
            switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_not_called, [], "The CLI attempts to perform a switch operation even though there was an invalid number of arguments.")
        
    def test_too_many_arguments(self):
        """The CLI should recognize and raise an error when too many arguments are given."""
        test_args = ['2-3', '~', '4-5', 'x', 'y']
        mock_expand_range.side_effect = lambda x: (2, 3)
        
        with self.assertRaises(ArgumentAmountError, msg="The FileSet fails to recognize when too many arguments are given."):
            switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_not_called, [], "The CLI attempts to perform a switch operation even though there was an invalid number of arguments.")
        
    def test_kwarg_strip_gaps(self):
        """The CLI should enable the user to choose strip_gaps as a gap handling method."""
        test_args = ['2-3', '~', '4-5', '-sg']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_called_once_with, [(2, 3), (4, 5), KeywordArgTuple('strip_gaps', True)], "The CLI fails to provide access to the gap-handling option strip_gaps.")
        
    def test_kwarg_preserve_gaps(self):
        """The CLI should enable the user to choose preserve_gaps as a gap handling method."""
        test_args = ['2-3', '~', '4-5', '-pg']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_called_once_with, [(2, 3), (4, 5), KeywordArgTuple('preserve_gaps', True)], "The CLI fails to provide access to the gap-handling option strip_gaps.")

    def test_invalid_kwarg_gap_handler(self):
        """The CLI should recognize and raise an error if an invalid gap-handling option was chosen."""
        test_args = ['2-3', '~', '4-5', '-xx']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        with self.assertRaises(InputProcessingError, msg="The CLI fails to recognize and raise an error when an invalid gap-handling option was chosen"):
            switch(self.test_set, test_args)
        
        mock_assert_msg(mock_switch_file_ranges.assert_not_called, [], "The CLI tries to eprform an operation even though an error was raised.")
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()