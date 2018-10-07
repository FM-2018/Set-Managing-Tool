'''
Created on 27.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_many_msg, mock_assert_msg


mock_move_range = mock.MagicMock(name='move_range')
mock_add_file = mock.MagicMock(name='add_file')

@mock.patch('FileSet.FileSet.move_range', new=mock_move_range)
@mock.patch('FileSet.FileSet.add_file', new=mock_add_file)
class RemoveFileTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_move_range.reset_mock()
        mock_add_file.reset_mock()
    
    
    def test_remove_middle(self):
        """The FileSet should be able to remove a file in the middle of the set."""
        test_files = ['test (0).mp4', 'test (1).jpg', 'test (2).png', 'test (3).gif']
        test_set = FileSet(self.pattern, test_files)
        
        removed_file_set = test_set.remove_file(1)
        
        mock_assert_msg(mock_add_file.assert_called_once_with, ['test (1).jpg', 0], "The FileSet fails to remove the file into the removed_file_set.")
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 1], msg="The FileSet fails to close the resulting gap from the remove operation.")
        
        self.assertEqual(removed_file_set.pattern, ('removed', ''), "The default pattern of the removed_file_set is incorrect.")
        
    def test_remove_last(self):
        """The FileSet should be able to remove the last file of the set."""
        test_files = ['test (0).mp4', 'test (1).jpg', 'test (2).png', 'test (3).gif']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.remove_file(3)
        
        mock_assert_msg(mock_add_file.assert_called_once_with, ['test (3).gif', 0], msg="The FileSet fails to physically remove the file if it's at the end of the set.")
        mock_assert_msg(mock_move_range.assert_not_called, [], msg="The FileSet tries to close a gap when there is none after the operation.")
        self.assertEqual(test_set.max_index, 2, "The FileSet fails to update its max_index after removing the last file of the set.")
    
    def test_remove_second_last(self):
        """The FileSet should be able to remove the file right before the last file of the set."""
        test_files = ['test (0).mp4', 'test (1).jpg', 'test (2).png', 'test (3).gif']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.remove_file(2)
        
        mock_assert_msg(mock_add_file.assert_called_once_with, ['test (2).png', 0], msg="The FileSet fails to physically remove the file if it's right before the last file of the set.")
        mock_assert_msg(mock_move_range.assert_called_once_with, [(3, 3), 2], msg="The FileSet fails to close a gap when removing the second last file of the set.")
        
    def test_remove_first(self):
        """"The FileSet should be able to remove the first file of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.remove_file(0)
        
        mock_assert_msg(mock_add_file.assert_called_once_with, ['test (0).jpg', 0], msg="The FileSet fails to actually remove the file if it's at the front of the set.")
        mock_assert_msg(mock_move_range.assert_called_once_with, [(1, 3), 0], msg="The FileSet fails to close the gap after removing a file from the front.")
        
    def test_multi_assigned_index(self):
        """"The FileSet should be able to remove a multi-assigned index and append its files to the removed_file_set with separate indexes."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (1).png', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.remove_file(1)
        
        assertion_calls = [
                (mock_add_file.assert_any_call, ['test (1).jpg', 0]),
                (mock_add_file.assert_any_call, ['test (1).png', 1])
            ]
        mock_assert_many_msg(assertion_calls, msg="The FileSet fails to remove all files correctly if it's a multi-assigned index.")
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 1], msg="The FileSet fails to close the gap after removing a multi-assigned index.")
        
    def test_try_remove_gap(self):
        """The FileSet should raise an error when tasked to remove a gap."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The FileSet fails to recognize when an index to be removed is unassigned."):
            test_set.remove_file(2)
        
    def test_remove_into_given_empty_file_set(self):
        """The FileSet should manage to add a removed file into a given empty file set."""
        removed_file_set = FileSet(('CustomRemoved (', ')'), [])
        
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg)', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.remove_file(1, removed_file_set)
        
        mock_assert_msg(mock_add_file.assert_called_once_with, ['test (1).jpg', 0], msg="The FileSet fails to properly remove the file into another FileSet.")
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 1], msg="The FileSet fails to close the resulting gap from the remove operation when removing into another FileSet.")
        
        self.assertEqual(removed_file_set.pattern, ('CustomRemoved (', ')'), "The default pattern of the removed_file_set is incorrect.")
        
    def test_remove_into_given_filled_file_set(self):
        """The FileSet should append the removed file to a given filled FileSet."""
        removed_file_set = FileSet(('CustomRemoved (', ')'), ['CustomRemoved (0).jpg', 'CustomRemoved (3).png'])
        
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg)', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.remove_file(1, removed_file_set)
        
        mock_assert_msg(mock_add_file.assert_called_once_with, ['test (1).jpg', 4], msg="The FileSet fails to properly remove and append the file into another FileSet.")
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 1], msg="The FileSet fails to close the resulting gap from the remove operation when removing into another FileSet.")
        
        self.assertEqual(removed_file_set.pattern, ('CustomRemoved (', ')'), "The set pattern of the removed_file_set is not the same as demanded.")
        
    def test_remove_multi_assigned_into_given_filled_file_set(self):
        """"The FileSet should append the files of a multi-assigned index to a given filled FileSet."""
        removed_file_set = FileSet(('CustomRemoved (', ')'), ['CustomRemoved (0).jpg', 'CustomRemoved (3).png'])
        
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (1).png', 'test (2).jpg)', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.remove_file(1, removed_file_set)
        
        assertion_calls = [
                (mock_add_file.assert_any_call, ['test (1).jpg', 4]),
                (mock_add_file.assert_any_call, ['test (1).png', 5])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to append a removed multi-assigned index to a given removed_file_set.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()