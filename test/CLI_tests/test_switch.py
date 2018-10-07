'''
Created on 05.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from CLI import switch, RangeExpansionError, CLIRuntimeError
from FileSet import FileSet
from test.testing_tools import mock_assert_msg


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
                raise RangeExpansionError()
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

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()