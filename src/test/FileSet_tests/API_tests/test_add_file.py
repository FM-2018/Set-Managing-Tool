'''
Created on 27.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_many_msg, mock_assert_msg


mock_rename= mock.MagicMock(name='rename')
mock_isfile = mock.MagicMock(name='isfile')
mock_move_range = mock.MagicMock(name='move_range')

@mock.patch('FileSet.isfile', new=mock_isfile)
@mock.patch('FileSet.rename', new=mock_rename)
@mock.patch('FileSet.FileSet.move_range', new=mock_move_range)
class AddFileTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_rename.reset_mock()
        mock_isfile.reset_mock()
        mock_move_range.reset_mock()
    
    
    def test_insert_middle(self):
        """The FileSet should be able to insert a new file into itself."""    
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (1, 2))
        
        mock_assert_msg(mock_isfile.assert_called_once_with, [new_file], msg="The FileSet does not check whether the file even exists.")
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 3), 3], msg="The FileSet doesn't properly make space before adding the file.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (2).jpg'], msg="The FileSet doesn't correctly add the file.")
        
    def test_insert_beginning(self):
        """The FileSet should be able to insert a new file at its front."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (-1, 0))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(0, 3), 1], msg="The FileSet doesn't properly make space before adding the file to the beginning of the set.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (0).jpg'], msg="The FileSet doesn't correctly add the file to the beginning of the set.")
        
    def test_insert_before_last_file(self):
        """The FileSet should be able to insert a new file right before its last file."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (2, 3))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(3, 3), 4], msg="The FileSet doesn't properly move the last file of the set out of the way.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (3).jpg'], msg="The FileSet doesn't correctly add the file right before the formerly last one of the set.")
        
    def test_append_end(self):
        """The FileSet should be able to append a new file to its end."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (3, 4))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], msg="The FileSet tries to make space for a new file even though that's unnecessary to append the file to the end.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (4).jpg'], msg="The FileSet doesn't correctly add the file to the end of the set.")
        
        self.assertEqual(test_set.max_index, 4, "The add_file method has to update the max index itself when appending a file to the end and thus not calling move_range. This did not happen.")
        
    def test_append_far_end(self):
        """The FileSet should be able to append a new file to its far end, causing a gap."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (5, 6))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], msg="The FileSet tries to make space for a new file even though that's unnecessary to append the file to the end.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (6).jpg'], msg="The FileSet doesn't correctly put the file somewhere at the end of the set.")
        
        self.assertEqual(test_set.max_index, 6, "The add_file method has to update the max index itself when appending a file to the end and thus not calling move_range. This did not happen.")
        
    def test_add_into_gap(self):
        """The FileSet should be able to add a new file into a gap, thus not having to make extra space."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (0, 1))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], msg="The FileSet tries to make space for a new file even though there already is a gap for it to fit.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (1).jpg'], msg="The FileSet doesn't correctly put the file into the gap.")
        
        self.assertEqual(test_set.max_index, 4, "The add_file method changed the max index even though it's adding into a gap in the middle of the set.")
        
    def test_add_into_empty_set(self):
        """The FileSet should be able to add a new file if it's empty."""
        test_files = []
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (0, 1))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], msg="The FileSet tries to make space for a new file even though that's unnecessary.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (1).jpg'], msg="The FileSet doesn't correctly add the file.")
        
        self.assertEqual(test_set.max_index, 1, "The add_file method update the max index when adding a file to an empty set.")
        
    def test_file_does_not_exist(self):
        """The FileSet shoudl recognize when a file doesn't exist and raise an error accordingly."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = False
        
        with self.assertRaises(FileNotFoundError, msg="The FileSet fails to recognize when a file does not exist."):
            test_set.add_file(new_file, (1, 2))
        
        assertion_calls = [
                (mock_rename.assert_not_called, []),
                (mock_move_range.assert_not_called, [])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet has performed an action even though it shouldn't have after the error was raised.")
        
    def test_spot_wrong_order(self):
        """The FileSet should still add the file correctly even if the spot is given from higher to lower."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        test_set.add_file(new_file, (1, 0))
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(1, 3), 2], "The FileSet fails to make space for a new file if the spot is given in reverse order.")
        mock_assert_msg(mock_rename.assert_called_once_with, [new_file, 'test (1).jpg'], "The FileSet doesn't correctly add the file.")
    
    def test_invalid_spot(self):
        """The FileSet should recognize an inalid spot and raise an error."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        new_file = 'new_file.jpg'
        mock_isfile.return_value = True
        with self.assertRaises(ValueError, msg="The FileSet fails to recognize an invalid spot."):
            test_set.add_file(new_file, (5, 0))
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to make space even though the spot was invalid.")
        mock_assert_msg(mock_rename.assert_not_called, [], "The FileSet tries to rename a file even though the spot was invalid.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()