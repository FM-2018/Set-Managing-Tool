'''
Created on 06.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
import CLI
from CLI import remove, CLIRuntimeError, ArgumentAmountError, default_remove_set,\
    InputProcessingError
from test.testing_tools import mock_assert_msg, KeywordArgTuple

mock_remove_files = mock.MagicMock(name='remove_files')
mock_expand_range = mock.MagicMock(name='_expand_range')

@mock.patch('FileSet.FileSet.remove_files', new=mock_remove_files)
@mock.patch('CLI._expand_range', new=mock_expand_range)
class RemoveTests(unittest.TestCase): 

    @classmethod
    def setUpClass(cls):
        cls.default_remove_set = FileSet(CLI.DEFAULT_REMOVE_PATTERN, [])
        cls.test_set = FileSet(
                ('test (', ')'), 
                ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 
                 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg', 'test (9).jpg'] 
            )
    
    def tearDown(self):
        mock_remove_files.reset_mock()
        mock_expand_range.reset_mock()
        
        mock_expand_range.side_effect = None
        
        CLI.file_set_cache = []
    
    
    def test_valid_operation(self):
        """The CLI should be able to perform a simple valid removal operation."""
        test_args = ['-', '2-3']
        mock_expand_range.return_value = (2, 3)
        CLI.default_remove_set = self.default_remove_set
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3], self.default_remove_set], "The CLI fails to perform a simple removal operation.")
        
    def test_valid_operation_multi_assigned_indexes(self):
        """The CLI should be able to deal with multi-assigned indexes in a removal operation."""
        test_args = ['-', '2-3']
        mock_expand_range.return_value = (2, 3)
        CLI.default_remove_set = self.default_remove_set
        
        test_set = FileSet(
                ('test (', ')'), 
                ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (2).png', 'test (3).jpg', 'test (4).jpg'] 
            )
        
        remove(test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3], self.default_remove_set], "The CLI fails to perform a removal operation if there are multi-assigned indexes.")
        
    def test_valid_operation_multiple_ranges(self):
        """The CLI should be able to perform a valid removal operation with numerous ranges given."""    
        test_args = ['-', '2-3', '5', '7-9']
        def mock_expand_range_side_effect(x):
            value_dic = {
                    '2-3': (2, 3),
                    '5': (5, 5),
                    '7-9': (7, 9)
                }
            
            return value_dic[x]
        mock_expand_range.side_effect = mock_expand_range_side_effect 
        CLI.default_remove_set = self.default_remove_set
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3, 5, 7, 8, 9], self.default_remove_set], "The CLI fails to perform a removal operation with multiple ranges given.")
        
    @mock.patch('CLI.FileSet.files_detected')
    @mock.patch('CLI._expand_pattern')
    def test_new_custom_remove_set(self, mock_expand_pattern, mock_files_detected):
        """The CLI should be able to remove the files into a new given custom remove set."""
        test_args = ['-', '-n', 'custom*set', '2-3']
        mock_expand_range.return_value = (2, 3)
        mock_expand_pattern.return_value = ('custom', 'set')
        CLI.default_remove_set = self.default_remove_set
        
        custom_remove_set = FileSet(('custom', 'set'), [])
        mock_files_detected.return_value = custom_remove_set
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_files_detected.assert_called_once_with, [('custom', 'set')], "The CLI doesn't actually try to properly create the new remove file set.") 
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3], custom_remove_set], "The CLI fails to remove files into a newly created file set.")
    
    @mock.patch('CLI.FileSet.files_detected')
    @mock.patch('CLI._expand_pattern')
    def test_new_custom_remove_set_already_exists(self, mock_expand_pattern, mock_files_detected):
        """The CLI should recognize and raise an error when a supposedly new custom remove set already exists."""
        test_args = ['-', '-n', 'custom*set', '2-3']
        mock_expand_range.return_value = (2, 3)
        mock_expand_pattern.return_value = ('custom', 'set')
        CLI.default_remove_set = self.default_remove_set
        
        custom_remove_set = FileSet(('custom', 'set'), [])
        mock_files_detected.return_value = custom_remove_set
        CLI.file_set_cache = [custom_remove_set] # set already exists
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when a supposedly new file set to remove files into already exists."):
            remove(self.test_set, test_args)
        
        mock_assert_msg(mock_files_detected.assert_not_called, [], "The CLI tries to create the new removed set even though it evidently already exists and an error was raised.") 
        mock_assert_msg(mock_remove_files.assert_not_called, [], "The CLI tries to remove files even though there was an error.")
        
    @mock.patch('CLI._expand_pattern')    
    def test_append_custom_remove_set(self, mock_expand_pattern):
        """The CLI should be able to remove the files into an existing given custom remove set."""
        test_args = ['-', '-a', 'custom*set', '2-3']
        mock_expand_range.return_value = (2, 3)
        mock_expand_pattern.return_value = ('custom', 'set')
        CLI.default_remove_set = self.default_remove_set
        
        custom_remove_set = FileSet(('custom', 'set'), [])
        CLI.file_set_cache = [custom_remove_set] # set already exists
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3], custom_remove_set], "The CLI fails to append the removed files to the existing custom remove set.")
    
    @mock.patch('CLI._expand_pattern')        
    def test_append_custom_remove_set_does_not_exist(self, mock_expand_pattern):
        """The CLI should be able to recognize and raise an error when a supposedly existing custom remove set can't be found."""
        test_args = ['-', '-a', 'custom*set', '2-3']
        mock_expand_range.return_value = (2, 3)
        mock_expand_pattern.return_value = ('custom', 'set')
        CLI.default_remove_set = self.default_remove_set
        
        CLI.file_set_cache = [] # file set cache stays empty, set doesn't exist
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when a remove set to append removed files to doesn't exist."):
            remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_not_called, [], "The CLI tries to append fails to a remove set even though the remove set can't be found.")
        
    def test_default_remove_set_is_active_set_no_other_set_given(self):
        """The CLI should be able to recognize and raise an error when the default remove set is selected to remove files from with no alternative sets to add the files into being given."""
        test_args = ['-', '2-3']
        mock_expand_range.return_value = (2, 3)
        CLI.default_remove_set = self.default_remove_set
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when the user tries to remove from the default remove set without specifying another file set to remove into."):
            remove(self.default_remove_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_not_called, [], "The CLI tries to perform a removal operation even though there is an unresolved error.")
    
    @mock.patch('CLI._expand_pattern')       
    def test_default_remove_set_is_active_other_set_is_given(self, mock_expand_pattern):
        """The CLI should be able to remove files from the default remove set if another file set to remove the files into is given."""
        test_args = ['-', '-a', 'custom*set', '1-2']
        mock_expand_range.return_value = (1, 2)
        mock_expand_pattern.return_value = ('custom', 'set')
        
        default_remove_set = FileSet(CLI.DEFAULT_REMOVE_PATTERN, ['RMVD1.jpg', 'RMVD2.jpg'])
        CLI.default_remove_set = default_remove_set
        
        custom_remove_set = FileSet(('custom', 'set'), [])
        CLI.file_set_cache = [custom_remove_set] # set already exists
        
        try:
            remove(default_remove_set, test_args)
        except CLIRuntimeError:
            self.fail("The CLI fails to perform a remove operation if it's removing from the default remove set even though a range to append the removed files to is given.")
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[1, 2], custom_remove_set], "The CLI fails to perform a removal operation from the default remove set to a given custom remove set.")
        
    def test_no_active_file_set(self):
        """The CLI should raise an error if there is no chosen file set."""
        test_args = ['-', '2-3']
        mock_expand_range.return_value = (2, 3)
        CLI.default_remove_set = self.default_remove_set
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when there is no active file set to perform the operation on."):
            remove(None, test_args)
        
        mock_assert_msg(mock_remove_files.assert_not_called, [], "The CLI tries to perform the removal operation even though there is no active file set.")
    
    @mock.patch('CLI.FileSet')
    def test_no_default_remove_set_created(self, mock_FileSet):
        """The CLI should automatically create the default remove set if it hasn't been created already."""
        test_args = ['-', '2-3']
        mock_expand_range.return_value = (2, 3)
        
        default_remove_set = FileSet(CLI.DEFAULT_REMOVE_PATTERN, [])
        CLI.default_remove_set = None
        mock_FileSet.return_value = default_remove_set
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_FileSet.assert_called_once_with, [CLI.DEFAULT_REMOVE_PATTERN, []], "The CLI fails to properly create the default remove set if it doesn't exist already.")
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3], default_remove_set], "The CLI fails to properly remove files if the remove set already contains files.")
    
    def test_remove_set_filled(self):
        """The CLI should be able to append files to the remove set even if it already contains files."""
        test_args = ['-', '2-3']
        mock_expand_range.return_value = (2, 3)
        
        default_remove_set = FileSet(CLI.DEFAULT_REMOVE_PATTERN, ['RMVD1.jpg', 'RMVD2.jpg'])
        CLI.default_remove_set = default_remove_set
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3], default_remove_set], "The CLI fails to properly remove files if the remove set already contains files.")
    
    def test_too_few_arguments(self):
        """The CLI should recognize and raise an error when too few arguments are given."""
        test_args = ['-']
        
        with self.assertRaises(ArgumentAmountError, msg="The FileSet fails to recognize when too few arguments are given."):
            remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_not_called, [], "The CLI attempts to perform a removal operation even though there was an invalid number of arguments.")
        
    def test_kwarg_strip_gaps(self):
        """The CLI should enable the user to choose strip_gaps as a gap handling method."""
        test_args = ['-', '2-3', '4-5', '-sg']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3, 4, 5], self.default_remove_set, KeywordArgTuple('strip_gaps', True)], "The CLI fails to provide access to the gap-handling option strip_gaps.")
        
    def test_kwarg_preserve_gaps(self):
        """The CLI should enable the user to choose preserve_gaps as a gap handling method."""
        test_args = ['-', '2-3', '4-5', '-pg']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_called_once_with, [[2, 3, 4, 5], self.default_remove_set, KeywordArgTuple('preserve_gaps', True)], "The CLI fails to provide access to the gap-handling option preserve_gaps.")

    def test_invalid_kwarg_gap_handler(self):
        """The CLI should recognize and raise an error if an invalid gap-handling option was chosen."""
        test_args = ['-', '2-3', '4-5', '-xx']
        mock_expand_range.side_effect = lambda x: (2, 3) if x.startswith('2') else (4, 5)
        
        with self.assertRaises(InputProcessingError, msg="The CLI fails to recognize and raise an error when an invalid gap-handling option was chosen"):
            remove(self.test_set, test_args)
        
        mock_assert_msg(mock_remove_files.assert_not_called, [], "The CLI tries to perform an operation even though an error was raised.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()