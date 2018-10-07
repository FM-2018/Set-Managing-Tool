'''
NOTE: logical removal of files is handled by the internally utilized function add_files. Therefore, it does not need to, nor can it be tested here.

Created on 27.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, KeywordArgTuple,\
    mock_assert_many_msg


def strip_gaps(boolean):
    return KeywordArgTuple('strip_gaps', boolean)

def preserve_gaps(boolean):
    return KeywordArgTuple('preserve_gaps', boolean)


mock_change_index = mock.MagicMock(name='change_index')
mock_add_file_set = mock.MagicMock(name='add_files')

@mock.patch('FileSet.FileSet.change_index', new=mock_change_index)
@mock.patch('FileSet.FileSet.add_file_set', new=mock_add_file_set)
class RemoveFilesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_change_index.reset_mock()
        mock_add_file_set.reset_mock()
        
        mock_change_index.side_effect = None
        mock_add_file_set.side_effect = None
    
    @staticmethod
    def _mock_add_files_side_effect_remove_files(file_set, _2, index_iterable, **kwargs):
        """Mock the logical behavior of add_files on the given file_set argument."""
        preserve_gaps = kwargs.get('preserve_gaps', False)
        strip_gaps = kwargs.get('strip_gaps', False)
        
        if preserve_gaps and strip_gaps:
            raise FileSet.ConflictingOptionsError()
        elif preserve_gaps or strip_gaps:
            for index in index_iterable:
                file_set.files.pop(index, None)
        else:
            for index in index_iterable:
                removal_result = file_set.files.pop(index, None)
                if removal_result is None:
                    raise FileSet.IndexUnassignedError(index, "The index {} is unassigned and thus can't be added to the set.".format(index))
    
    
    def test_range_middle(self):
        """The FileSet should be able to remove a range from the middle of the set."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        removed_file_set, _ = test_set.remove_files(range(2, 4+1))
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to remove the range of files into the removed_file_set.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [1, 1]),
                (mock_change_index.assert_any_call, [5, 2]),
                (mock_change_index.assert_any_call, [6, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to close resulting gaps when removing multiple files from the middle.")
         
        self.assertEqual(removed_file_set.pattern, ('removed', ''), "The default pattern of the removed_file_set is incorrect.")
        
    def test_range_end(self):
        """The FileSet should be able to remove a range from the end of the set."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        test_set.remove_files(range(4, 6+1))
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(4, 6+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to remove a range of files if they are at the end of the set.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [1, 1]),
                (mock_change_index.assert_any_call, [2, 2]),
                (mock_change_index.assert_any_call, [3, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing files from the end.")
        
    def test_range_beginning(self):
        """The FileSet should be able to remove a range from the beginning of the set."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        test_set.remove_files(range(0, 1+1))
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(0, 1+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to remove a range of files if they are at the beginning of the set.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [2, 0]),
                (mock_change_index.assert_any_call, [3, 1]),
                (mock_change_index.assert_any_call, [4, 2]),
                (mock_change_index.assert_any_call, [5, 3]),
                (mock_change_index.assert_any_call, [6, 4])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing files from the front.")
        
    def test_1_length_range(self):
        """The FileSet should be able to remove a range that contains only one file / follows the scheme: (n, n)."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        test_set.remove_files(range(2, 2+1))
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(2, 2+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to remove a range of files if they are at the end of the set.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [1, 1]),
                (mock_change_index.assert_any_call, [3, 2]),
                (mock_change_index.assert_any_call, [4, 3]),
                (mock_change_index.assert_any_call, [5, 4]),
                (mock_change_index.assert_any_call, [6, 5])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing a single file range from the middle.")
        
    def test_range_with_multi_assigned_indexes(self):
        """The FileSet should be able to remove a range with multi-assigned indexes."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (2).png', 'test (3).gif', 'test (3).jpg', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        test_set.remove_files(range(2, 4+1))
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to remove a range of files if there are multi-assigned indexes.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [1, 1]),
                (mock_change_index.assert_any_call, [5, 2]),
                (mock_change_index.assert_any_call, [6, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when there are multi-assigned indexes.")
        
    def test_try_remove_fully_unassigned_range_no_gap_handling(self):
        """The FileSet should recognize an empty range and raise an error if no gap-handling option is chosen."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The FileSet fails to recognize an empty range when removing with no gap-handling option chosen."):
            test_set.remove_files(range(3, 5+1))
        
    def test_remove_fully_unassigned_range_strip_gaps(self):
        """The FileSet should simply fix the gap when removing a fully unassigned range of files with strip_gaps=True."""
        test_files = ['test (0).png', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        test_set.remove_files(range(1, 3+1), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(1, 3+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to try removing the range of files/gaps into the removed_file_set.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [4, 1]),
                (mock_change_index.assert_any_call, [5, 2]),
                (mock_change_index.assert_any_call, [6, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing a fully unassigned range from the middle, stripping the gaps.")
    
    def test_remove_fully_unassigned_range_preserve_gaps(self):
        """The FileSet should try to 'remove' the empty range of gaps into the removed file set if preserve_gaps=True, effectively just fixing the gap in the original file set."""
        test_files = ['test (0).png', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        test_set.remove_files(range(1, 3+1), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(1, 3+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to try removing the range of files/gaps into the removed_file_set.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [4, 1]),
                (mock_change_index.assert_any_call, [5, 2]),
                (mock_change_index.assert_any_call, [6, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing a fully unassigned range from the middle, preserving the gaps.")
        
    def test_try_remove_partly_unassigned_range_no_gap_handling(self):
        """The FileSet should recognize a range that contains gaps and raise an error if no gap-handling option is chosen."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The FileSet fails to recognize gaps and raise an error when removing with no gap-handling method chosen."):
            test_set.remove_files(range(0, 3+1))
            
    def test_try_remove_partly_unassigned_range_strip_gaps(self):
        """The FileSet should be able to correctly remove a range that contains gaps and strip its gaps if strip_gaps=True."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_add_files_side_effect(file_set, _2, index_iterable, **kwargs):
            self._mock_add_files_side_effect_remove_files(file_set, _2, index_iterable, preserve_gaps=kwargs.get('preserve_gaps', False), strip_gaps=kwargs.get('strip_gaps', False))
            return 2
        mock_add_file_set.side_effect = mock_add_files_side_effect

        try:
            _, amount_removed = test_set.remove_files(range(0, 3+1), strip_gaps=True)
        except FileSet.IndexUnassignedError:
            self.fail("The FileSet raises an IndexUnassignedError even though a gap-handling option has been chosen.")
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(0, 3+1), strip_gaps(True), preserve_gaps(False)], "The FileSet did not actually try to remove the files.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [6, 0])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing a partly unassigned range from the middle, stripping the gaps.")
        self.assertEqual(amount_removed, 2, "The FileSet fails to return the correct amount of indexes it has removed if strip_gaps=True.")
        
    def test_try_remove_partly_unassigned_range_preserve_gaps(self):
        """The FileSet should be able to correctly remove a range that contains gaps if preserve_gaps=True."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_add_files_side_effect(file_set, _2, index_iterable, **kwargs):
            self._mock_add_files_side_effect_remove_files(file_set, _2, index_iterable, preserve_gaps=kwargs.get('preserve_gaps', False), strip_gaps=kwargs.get('strip_gaps', False))
            return 4
        mock_add_file_set.side_effect = mock_add_files_side_effect
        
        try:
            _, amount_removed = test_set.remove_files(range(0, 3+1), preserve_gaps=True)
        except FileSet.IndexUnassignedError:
            self.fail("The FileSet raises an IndexUnassignedError even though a gap-handling option has been chosen.")
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(0, 3+1), strip_gaps(False), preserve_gaps(True)], "The FileSet did not actually try to remove the files.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [6, 0])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing a partly unassigned range from the middle, preserving the gaps.")
        self.assertEqual(amount_removed, 4, "The FileSet fails to return the correct amount of indexes it has removed if preserve_gaps=True")
        
    def test_remove_range_into_existing_empty_file_set(self):
        """The FileSet should be able to remove a range of files into an existing FileSet that is empty."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        removed_set_pattern = ('CustomRemoved (', ')') 
        removed_file_set = FileSet(removed_set_pattern, [])
        
        returned_removed_file_set, _ = test_set.remove_files(range(1, 3+1), removed_file_set)
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(1, 3+1), strip_gaps(False), preserve_gaps(False)], "The FileSet does not actually try to remove the files into a given FileSet object.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [4, 1]),
                (mock_change_index.assert_any_call, [5, 2]),
                (mock_change_index.assert_any_call, [6, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing a range of files into an existing empty file set.")
        self.assertEqual(returned_removed_file_set.pattern, removed_set_pattern, "The FileSet fails to return the given removed_file_set after the operation.")
        
    def test_remove_range_into_existing_filled_file_set(self):
        """The FileSet should be able to remove a range of files into an existing FileSet that already contains files."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        removed_set_pattern = ('CustomRemoved (', ')') 
        removed_file_set = FileSet(removed_set_pattern, ['CustomRemoved (0).jpg', 'CustomRemoved (3).png'])
        
        test_set.remove_files(range(1, 3+1), removed_file_set)
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (3, 4), range(1, 3+1), strip_gaps(False), preserve_gaps(False)], "The FileSet does not correctly append the removed files to the given FileSet object if it already contains files.")
    
    def test_remove_keep_gaps_in_set(self):
        """The FileSet should be able to remove a range of files without closing the resulting gap if keep_gaps_in_set=True."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        removed_file_set, _ = test_set.remove_files(range(2, 4+1), keep_gaps_in_set=True)
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to remove the range of files into the removed_file_set.")
        mock_assert_msg(mock_change_index.assert_not_called, [], "The FileSet tries to close the resulting removal gap even though that is explicitly NOT wished for.")
        
        self.assertEqual(removed_file_set.pattern, ('removed', ''), "The default pattern of the removed_file_set is incorrect.")
    
    def test_generic_index_iterable(self):
        """The FileSet should be able to remove files given any valid index iterable."""
        test_files = ['test (0).png', 'test (1).jpg', 'test (2).gif', 'test (3).m4a', 'test (4).m4a', 'test (5).pdf', 'test (6).gif']
        test_set = FileSet(self.pattern, test_files)
        
        mock_add_file_set.side_effect = self._mock_add_files_side_effect_remove_files
        
        remove_indexes = [4, 3, 1, 5] # 1, 3, 4, 5
        removed_file_set, _ = test_set.remove_files(remove_indexes)
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [test_set, (-1, 0), remove_indexes, strip_gaps(False), preserve_gaps(False)], "The FileSet fails to remove the range of files into the removed_file_set if a generic index iterable is given.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [2, 1]),
                (mock_change_index.assert_any_call, [6, 2])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly attempt closing resulting gaps when removing using a generic index iterable.")
        
        self.assertEqual(removed_file_set.pattern, ('removed', ''), "The default pattern of the removed_file_set is incorrect when given a generic index iterable.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()