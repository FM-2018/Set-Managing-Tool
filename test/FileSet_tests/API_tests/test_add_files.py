'''
Created on 29.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, mock_assert_many_msg


mock_isfile = mock.MagicMock(name='isfile')
mock_check_spot = mock.MagicMock(name='_check_and_order_spot')
mock_move_range = mock.MagicMock(name='move_range')
mock_rename = mock.MagicMock(name='rename')
mock_add_logically = mock.MagicMock(name='_add_file_logically')

@mock.patch('FileSet.isfile', new=mock_isfile)
@mock.patch('FileSet.FileSet._check_and_order_spot', new=mock_check_spot)
@mock.patch('FileSet.FileSet.move_range', new=mock_move_range)
@mock.patch('FileSet.rename', new=mock_rename)
@mock.patch('FileSet.FileSet._add_file_logically', new=mock_add_logically)
class AddFilesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_isfile.reset_mock()
        mock_check_spot.reset_mock()
        mock_move_range.reset_mock()
        mock_rename.reset_mock()
        mock_add_logically.reset_mock()
        
        mock_isfile.side_effect = None
        mock_check_spot.side_effect = None
    
    
    def test_add_single_file(self):
        """The method should be able to add a single file."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file.add']
        
        mock_isfile.return_value = True
        mock_check_spot.return_value = (1, 2)
        
        test_set.add_files(files_to_add, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 3], "The method fails to make space for the single file to be added.")
        mock_assert_msg(mock_rename.assert_called_once_with, ['new_file.add', 'test (2).add'], "The method fails to physically add the file.")
        mock_assert_msg(mock_add_logically.assert_called_once_with, [2, 'add'], "The method fails to logically add the file.")
        
    def test_add_multiple_files(self):
        """The method should be able to add multiple files at once."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file1.add1', 'new_file2.add2', 'another_file.add3']
        
        mock_isfile.return_value = True
        mock_check_spot.return_value = (1, 2)
        
        test_set.add_files(files_to_add, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 5], "The method fails to make space for the files to be added.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['new_file1.add1', 'test (2).add1']),
                (mock_rename.assert_any_call, ['new_file2.add2', 'test (3).add2']),
                (mock_rename.assert_any_call, ['another_file.add3', 'test (4).add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to physically add the files.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add1']),
                (mock_add_logically.assert_any_call, [3, 'add2']),
                (mock_add_logically.assert_any_call, [4, 'add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to logically add the files.")
        
    def test_append_files(self):
        """The method should be able to append files to the end of the set and update the max_index accordingly."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file1.add1', 'new_file2.add2', 'another_file.add3']
        
        mock_isfile.return_value = True
        mock_check_spot.return_value = (3, 4)
        
        test_set.add_files(files_to_add, (3, 4))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The method tries to make space for the files to be added even though that's unnecessary when appending to the end.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['new_file1.add1', 'test (4).add1']),
                (mock_rename.assert_any_call, ['new_file2.add2', 'test (5).add2']),
                (mock_rename.assert_any_call, ['another_file.add3', 'test (6).add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to physically add the files.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [4, 'add1']),
                (mock_add_logically.assert_any_call, [5, 'add2']),
                (mock_add_logically.assert_any_call, [6, 'add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to logically add the files.")
        
        self.assertEqual(test_set.max_index, 6, "The method fails to update the max_index if the files are being appended to the end.")
        
    def test_append_files_far_end(self):
        """The method should be able to append files to the far end of the set, leaving a gap and updating the max_index accordingly."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file1.add1', 'new_file2.add2', 'another_file.add3']
        
        mock_isfile.return_value = True
        mock_check_spot.return_value = (5, 6)
        
        test_set.add_files(files_to_add, (5, 6))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The method tries to make space for the files to be added even though that's unnecessary when appending to the far end.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['new_file1.add1', 'test (6).add1']),
                (mock_rename.assert_any_call, ['new_file2.add2', 'test (7).add2']),
                (mock_rename.assert_any_call, ['another_file.add3', 'test (8).add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to physically add the files.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [6, 'add1']),
                (mock_add_logically.assert_any_call, [7, 'add2']),
                (mock_add_logically.assert_any_call, [8, 'add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to logically add the files.")
        
        self.assertEqual(test_set.max_index, 8, "The method fails to update the max_index if the files are being appended to the far end.")
        
    def test_non_existent_files_normal_mode(self):
        """By default, the method should raise an error when one of the files does not exist."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file1.add1', 'not_existent', 'another_file.add3']
        
        mock_isfile.side_effect = lambda f: not (f == 'not_existent') 
        mock_check_spot.return_value = (1, 2)
        
        with self.assertRaises(FileSet.FileNotFoundError, msg="The method fails to recognize invalid/not existent files."):
            test_set.add_files(files_to_add, (1, 2), ignore_unfound_files=False)
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The method performs an operation even though an error was raised.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The method performs an operation even though an error was raised.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The method performs an operation even though an error was raised.")
    
    def test_non_existent_files_ignore_mode(self):
        """When ignore_unfound_files=True, the method should ignore non-existent files and add the rest flawlessly."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
         
        files_to_add = ['new_file1.add1', 'not_existent', 'another_file.add3']
         
        mock_isfile.side_effect = lambda f: not (f == 'not_existent')
        mock_check_spot.return_value = (1, 2)
         
        try:
            test_set.add_files(files_to_add, (1, 2), ignore_unfound_files=True)
        except FileSet.FileNotFoundError:
            self.fail("The method raises a FileNotFoundError even though ignore_unfound_files was set to True.")
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 4], "The method fails to make space for the files to be added.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['new_file1.add1', 'test (2).add1']),
                (mock_rename.assert_any_call, ['another_file.add3', 'test (3).add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to physically add the files.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add1']),
                (mock_add_logically.assert_any_call, [3, 'add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to logically add the files.")
        
    def test_empty_file_set(self):
        """The method should be able to add files into an empty file set."""
        test_files = []
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file1.add1', 'new_file2.add2', 'another_file.add3']
        
        mock_isfile.return_value = True
        mock_check_spot.return_value = (-1, 0)
        
        test_set.add_files(files_to_add, (-1, 0))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The method tries to make space for the files to be added even though that's unnecessary for an empty file set.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['new_file1.add1', 'test (0).add1']),
                (mock_rename.assert_any_call, ['new_file2.add2', 'test (1).add2']),
                (mock_rename.assert_any_call, ['another_file.add3', 'test (2).add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to physically add the files.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [0, 'add1']),
                (mock_add_logically.assert_any_call, [1, 'add2']),
                (mock_add_logically.assert_any_call, [2, 'add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to logically add the files.")
        
        self.assertEqual(test_set.max_index, 2, "The method fails to update the max_index when adding files into an empty file set.")
    
    def test_spot_wrong_order(self):
        """The method should be able to operate correctly even if the spot is given from higher to lower."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file1.add1', 'new_file2.add2', 'another_file.add3']
        
        mock_isfile.return_value = True
        mock_check_spot.return_value = (1, 2)
        
        test_set.add_files(files_to_add, (2, 1))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 5], "The method fails to make space for the files to be added.")
        assertion_calls = [
                (mock_rename.assert_any_call, ['new_file1.add1', 'test (2).add1']),
                (mock_rename.assert_any_call, ['new_file2.add2', 'test (3).add2']),
                (mock_rename.assert_any_call, ['another_file.add3', 'test (4).add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to physically add the files.")
        assertion_calls = [
                (mock_add_logically.assert_any_call, [2, 'add1']),
                (mock_add_logically.assert_any_call, [3, 'add2']),
                (mock_add_logically.assert_any_call, [4, 'add3'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to logically add the files.")
    
    def test_invalid_spot(self):
        """The method should recognize and raise an error when the given spot is invalid."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = ['new_file1.add1', 'new_file2.add2', 'another_file.add3']
        
        mock_isfile.return_value = True 
        mock_check_spot.side_effect = ValueError()
        
        with self.assertRaises(ValueError, msg="The method fails to recognize an invalid spot."):
            test_set.add_files(files_to_add, ('a', 'b'))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The method performs an operation even though an error was raised.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The method performs an operation even though an error was raised.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The method performs an operation even though an error was raised.")
    
    def test_add_no_files(self):
        """The method should do nothing if no files to be added are given."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        files_to_add = []
        
        mock_check_spot.return_value = (1, 2)
        
        test_set.add_files(files_to_add, (1, 2))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The method performs an operation even though the list of files to be added is empty.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The method performs an operation even though the list of files to be added is empty.")
        mock_assert_msg(mock_add_logically.assert_not_called, [], "The method performs an operation even though the list of files to be added is empty.")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()