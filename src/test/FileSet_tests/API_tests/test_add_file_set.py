'''
Created on 28.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_many_msg, mock_assert_msg


mock_move_range = mock.MagicMock(name='move_range')
mock_rename = mock.MagicMock(name='rename')
mock_add_logically = mock.MagicMock(name='_add_file_logically')
mock_remove_logically = mock.MagicMock(name='remove_file_logically')

@mock.patch('FileSet.FileSet.move_range', new=mock_move_range)
@mock.patch('FileSet.rename', new=mock_rename)
@mock.patch('FileSet.FileSet._add_file_logically', new=mock_add_logically)
@mock.patch('FileSet.FileSet._remove_file_logically', new=mock_remove_logically)
class AddFileSetTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_move_range.reset_mock()
        mock_rename.reset_mock()
        mock_add_logically.reset_mock()
        mock_remove_logically.reset_mock()
    
    
    def test_middle(self):
        """The FileSet should be able to add files into the middle of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 4], "The FileSet fails to make space for the new files.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (3).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the correct number of indexes that were actually added.")
        
    def test_front(self):
        """The FileSet should be able to add files to the front of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (-1, 0))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(0, 3), 2], "The FileSet fails to make space for the new files at the front.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (0).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (1).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files to the front.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [0, 'add']),
                (mock_add_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when adding to the front.")
        
    def test_end(self):
        """The FileSet should be able to append files to the end."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (3, 4))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet unnecessarily tries to make space when appending the files to the end.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (4).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (5).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically append the files to the end.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [4, 'add']),
                (mock_add_logically.assert_any_call, [5, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when appending to the end.")
        self.assertEqual(test_set.max_index, 5, "The FileSet fails to update the max_index when adding to the end of the set.")
        
    def test_far_end(self):
        """The FileSet should be able to append files to the far end of the set, causing a gap in between."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (5, 6))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet unnecessarily tries to make space when appending the files to the far end.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (6).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (7).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically append the files to the far end of the set.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [6, 'add']),
                (mock_add_logically.assert_any_call, [7, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when appending to the far end.")
        self.assertEqual(test_set.max_index, 7, "The FileSet fails to update the max_index when adding to the far end of the set.")
        
    def test_before_last_file(self):
        """The FileSet should be able to add files in front of the last file of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (2, 3))
        
        mock_assert_msg(mock_move_range.assert_called_with, [(3, 3), 5], "The FileSet fails to make space when adding the files right before the last file of the set.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (3).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (4).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files before the last file of the set.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [3, 'add']),
                (mock_add_logically.assert_any_call, [4, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when adding in front of the last file.")
        
    def test_wide_gap(self):
        """The FileSet should be able to add files into a wide gap without making extra space."""
        test_files = ['test (0).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet unnecessarily tries to make space when adding the files into a wide gap.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (3).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files into the wide gap.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when adding into a wide gap.")
        
    def test_fitting_gap(self):
        """The FileSet should be able to add files into a gap, filling it up completely without having to make extra space."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet unnecessarily tries to make space when adding the files into a perfectly fitting gap.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (3).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files into a perfectly fitting gap.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when adding into a perfectly fitting gap.")
        
    def test_too_small_gap(self):
        """The FileSet should be able to fill a small gap and automatically make the necessary extra-space if the amount of files requires it."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add', 'add (2).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(4, 5), 5], "The FileSet fails to make space for the added files when the gap is too small.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (3).add']),
                (mock_rename.assert_any_call, ['add (2).add', 'test (4).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files into a gap that had to be widened.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add']),
                (mock_add_logically.assert_any_call, [4, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add']),
                (mock_remove_logically.assert_any_call, [2, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 3, "The FileSet fails to return the number of indexes that were actually added when adding into a too-small gap.")
        
    def test_add_into_empty_set(self):
        """The FileSet should be able to add files even if it is empty."""
        test_files = []
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add', 'add (2).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (-1, 0))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet unnecessarily tries to make space when adding into an empty set.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (0).add']),
                (mock_rename.assert_any_call, ['add (1).add', 'test (1).add']),
                (mock_rename.assert_any_call, ['add (2).add', 'test (2).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files into a an empty FileSet.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [0, 'add']),
                (mock_add_logically.assert_any_call, [1, 'add']),
                (mock_add_logically.assert_any_call, [2, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add']),
                (mock_remove_logically.assert_any_call, [2, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 3, "The FileSet fails to return the number of indexes that were actually added when adding into an empty set.")
        self.assertEqual(test_set.max_index, 2, "The FileSet fails to update the max_index when adding into an empty file set.")
        
    def test_add_from_empty_set(self):
        """The FileSet should be able to add an empty FileSet."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = []
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet unnecessarily tries to make space when adding no files at all.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The FileSet tries to physically add files even though there are none.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The FileSet tries to logically add files even though there are none.")
        mock_assert_msg(mock_remove_logically.assert_not_called, [], "The FileSet tries to logically remove files from the foreign_file_set even though there are none.")
        self.assertEqual(amount_added, 0, "The FileSet fails to return the number of indexes that were actually added when adding an empty set.")
        
    def test_gap_in_foreign_add_all_indexes(self):
        """The FileSet should automatically ignore gaps in the foreign file set and add all files if add_indexes is set to 'ALL' (default)."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (2).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        try:
            amount_added = test_set.add_file_set(add_set, (1, 2))
        except FileSet.IndexUnassignedError as e:
            raise AssertionError(e.args, "The FileSet fails to add a FileSet with gaps, even though indexes='ALL' has been used.")
            
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 4], msg="The FileSet fails to make the correct space for the two files with a gap.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (2).add', 'test (3).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files with a gap into the FileSet.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [2, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when the files to be added contain gaps.")
        
    def test_gap_in_foreign_try_add_files_no_gap_handling(self):
        """The FileSet should raise an error if it finds a gap in one of the indexes it is requested to add and no gap-handling is specified."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (2).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The FileSet fails to recognize when a FileSet to be added contains gaps and thus fails to raise an error, even though no gap-handling option has been chosen.."):
            test_set.add_file_set(add_set, (1, 2), range(0, 2+1))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet moves a range despite having run into an error.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The FileSet physically adds files despite having run into an error.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The FileSet logically adds files despite having run into an error.")
        mock_assert_msg(mock_remove_logically, [], "The FileSet logically removes files from the foreign_file_set despite having run into an error.")
        
    def test_gap_in_foreign_add_files_strip_gaps(self): 
        """The FileSet should ignore gaps in the foreign FileSet if strip_gaps is set to True."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (2).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        try:
            amount_added = test_set.add_file_set(add_set, (1, 2), range(0, 2+1), strip_gaps=True)
        except FileSet.IndexUnassignedError as e:
            raise AssertionError(e.args, "The FileSet raises an exception when encountering a gap even though strip_gaps was set to True.")
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 4], "The FileSet fails to make space for the newly added files when the file set to be added from contains gaps and strip_gaps is set to True.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (2).add', 'test (3).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files from the foreign FileSet with gaps if strip_gaps is True.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [2, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when the files to be added contain gaps with strip_gaps set to True.")
    
    def test_wide_gap_in_foreign_add_files_strip_gaps(self):
        """The FileSet should still correctly strip all gaps in the foreign FileSet if strip_gaps is set to True, even if the gap is wider than just one."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (3).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        try:
            amount_added = test_set.add_file_set(add_set, (1, 2), range(0, 3+1), strip_gaps=True)
        except FileSet.IndexUnassignedError as e:
            raise AssertionError(e.args, "The FileSet raises an exception when encountering a gap even though strip_gaps was set to True.")
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 4], "The FileSet fails to make the correct amount of space for the newly added files when the file set to be added from contains wide gaps and strip_gaps is set to True.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (3).add', 'test (3).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files from the foreign FileSet with gaps if strip_gaps is True.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [3, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 2, "The FileSet fails to return the number of indexes that were actually added when the files to be added contain gaps with strip_gaps set to True.")
    
    def test_gap_in_foreign_add_files_preserve_gaps(self):
        """The FileSet should be able to preserve gaps if the corresponding keyword is set to True."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (2).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        try:
            amount_added = test_set.add_file_set(add_set, (1, 2), range(0, 2+1), preserve_gaps = True)
        except FileSet.IndexUnassignedError:
            self.fail("The FileSet raises an exception when encountering a gap even though preserve_gaps was set to True.")
            
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 5], "The FileSet fails to make space for the files and gaps when the latter are preserved.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (0).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (2).add', 'test (4).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to physically add the files and gaps from the foreign FileSet when the gaps are preserved.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [4, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [2, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 3, "The FileSet fails to return the correct number of indexes (files and gaps) that were actually added when the files to be added contain gaps.")
    
    def test_given_iterable_right_order(self):
        """The FileSet should preserve the order of the files as given in the add_indexes iterable."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add', 'add (2).add', 'add (3).add', 'add (4).add', 'add (5).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        amount_added = test_set.add_file_set(add_set, (1, 2), [1, 4, 2, 3, 5, 0])
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 8], "The FileSet fails to correctly make space for the files.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['add (1).add', 'test (2).add']),
                (mock_rename.assert_any_call, ['add (4).add', 'test (3).add']),
                (mock_rename.assert_any_call, ['add (2).add', 'test (4).add']),
                (mock_rename.assert_any_call, ['add (3).add', 'test (5).add']),
                (mock_rename.assert_any_call, ['add (5).add', 'test (6).add']),
                (mock_rename.assert_any_call, ['add (0).add', 'test (7).add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to add the given files in the correct order.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add']),
                (mock_add_logically.assert_any_call, [3, 'add']),
                (mock_add_logically.assert_any_call, [4, 'add']),
                (mock_add_logically.assert_any_call, [5, 'add']),
                (mock_add_logically.assert_any_call, [6, 'add']),
                (mock_add_logically.assert_any_call, [7, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically add the files.")
        assertion_calls = [
                (mock_remove_logically.assert_any_call, [0, 'add']),
                (mock_remove_logically.assert_any_call, [1, 'add']),
                (mock_remove_logically.assert_any_call, [2, 'add']),
                (mock_remove_logically.assert_any_call, [3, 'add']),
                (mock_remove_logically.assert_any_call, [4, 'add']),
                (mock_remove_logically.assert_any_call, [5, 'add'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to logically remove the files from the foreign file_set's file list.")
        self.assertEqual(amount_added, 6, "The FileSet fails to return the correct number of indexes that were actually added when adding by a given index iterable.")
        
    def test_try_invalid_iterator(self):
        """The FileSet should raise an error when the given iterator doesn't solely contain valid integers."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add', 'add (2).add', 'add (3).add', 'add (4).add', 'add (5).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        with self.assertRaises(TypeError, msg="The FileSet fails to raise an exception when an invalid index list is given."):
            test_set.add_file_set(add_set, (1, 2), [1, 4, '3', 7])
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet moves a range despite having run into an error.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The FileSet physically adds files despite having run into an error.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The FileSet logically adds files despite having run into an error.")
        mock_assert_msg(mock_remove_logically.assert_not_called, [], "The FileSet logically removes files from the foreign_file_set despite having run into an error.")
        
    def test_invalid_spot(self):
        """The FileSet should be able to recognize an invalid spot and raise an error accordingly."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (1).add', 'add (2).add', 'add (3).add', 'add (4).add', 'add (5).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        with self.assertRaises(ValueError, msg="The FileSet fails to recognize an invalid spot."):
            test_set.add_file_set(add_set, (3, 8))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to make space for files even though the spot is invalid.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The FileSet physically adds files despite having run into an error.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The FileSet logically adds files despite having run into an error.")
        mock_assert_msg(mock_remove_logically.assert_not_called, [], "The FileSet logically removes files from the foreign_file_set despite having run into an error.")
    
    def test_both_gap_handlers_chosen(self):
        """The FileSet should recognize and raise an error if both gap handling methods have been chosen at once."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        add_files = ['add (0).add', 'add (2).add']
        add_set = FileSet(('add (', ')'), add_files)
        
        with self.assertRaises(FileSet.ConflictingOptionsError, msg="The FileSet fails to raise an error if both gap-handling methods have been chosen."):
            test_set.add_file_set(add_set, (1, 2), range(0, 2+1), preserve_gaps = True, strip_gaps=True)
    
        mock_assert_msg(mock_rename.assert_not_called, [], "The FileSet physically adds files despite two chosen options conflicting.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet moves a range despite having run into an error.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The FileSet physically adds files despite having run into an error.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The FileSet logically adds files despite having run into an error.")
        mock_assert_msg(mock_remove_logically.assert_not_called, [], "The FileSet logically removes files from the foreign_file_set despite having run into an error.")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()