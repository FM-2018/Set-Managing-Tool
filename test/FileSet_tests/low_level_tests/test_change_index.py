'''
Created on 27.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, mock_assert_many_msg


mock_rename = mock.MagicMock()

@mock.patch('FileSet.rename', new=mock_rename)
class ChangeIndexTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_rename.reset_mock()
    
    
    def test_middle_to_end(self):
        """The FileSet should be able to change the index of a file to a free position at the end of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        
        test_set = FileSet(self.pattern, test_files)
        test_set.change_index(1, 4)
        
        result_files = {0: ['jpg'], 2: ['jpg'], 3: ['jpg'], 4: ['jpg']}
        mock_assert_msg(mock_rename.assert_called_with, ['test (1).jpg', 'test (4).jpg'], msg="The FileSet doesn't actually rename the file properly.")
        self.assertEqual(test_set.files, result_files, "The FileSet fails to change a file's index.")
        self.assertEqual(test_set.max_index, 4, "The FileSet fails to update its max_index after a change_index operation that makes it necessary.")
         
    def test_middle_to_middle(self):
        """The FileSet should be able to change the index of a file to a free position at the beginning of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg']
        
        test_set = FileSet(self.pattern, test_files)
        test_set.change_index(1, 2)
         
        result_files = {0: ['jpg'], 2: ['jpg'], 3: ['jpg'], 4: ['jpg']}
        mock_assert_msg(mock_rename.assert_called_with, ['test (1).jpg', 'test (2).jpg'], msg="The FileSet doesn't rename the file properly.")
        self.assertEqual(test_set.files, result_files, "The FileSet fails to change a file's index in the middle of the set.")
         
    def test_multi_assigned_index(self):
        """The FileSet should be able to change the index of files even if this index is multi-assigned."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (2).png', 'test (3).jpg'] 
         
        test_set = FileSet(self.pattern, test_files)
        test_set.change_index(2, 4)
        
        result_files = {0: ['jpg'], 1: ['jpg'], 3: ['jpg'], 4: ['jpg', 'png']}
        
        assertion_calls = [
                (mock_rename.assert_any_call , ['test (2).jpg', 'test (4).jpg']),
                (mock_rename.assert_any_call , ['test (2).png', 'test (4).png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet does not correctly rename both of the files of the multi-assigned index.")
        self.assertEqual(test_set.files, result_files, "The FileSet fails to operate correctly when dealing with a multi-assigned index.")
          
    def test_index_unassigned_far_up(self):
        """The FileSet should recognize an unassigned index that's far out of bounds of the set and raise an error."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (2).png', 'test (3).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The FilsSet fails to stop when the given file's index does not exist."):
            test_set.change_index(12, 2)
            
    def test_index_unassigned_inside(self):
        """The FileSet should recognize an unassigned index within the set and raise an error."""
        test_files = ['test (0).jpg', 'test (3).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The FilsSet fails to stop when the given file's index does not exist."):
            test_set.change_index(1, 2)
         
    def test_to_index_assigned(self):
        """The FileSet should recognize when an index the file is supposed to be moved to is already assigned and raise an error."""
        test_files = ['test (0).jpg', 'test (3).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        with self.assertRaises(FileSet.IndexAssignedError, msg="The FileSet fails to stop when a file's index is attempted to be set to an already assigned one."):
            test_set.change_index(0, 3)
        
    def test_from_to_same_index(self):
        """The FileSet should do nothing when a file is requested to be moved to the same index it already has."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        
        test_set = FileSet(self.pattern, test_files)
        try:
            test_set.change_index(1, 1)
        except FileSet.IndexAssignedError:
            self.fail("The FileSet doesn't recognize when an index is changed to itself, in which case nothing should happen.")
        
        result_files = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}
        mock_assert_msg(mock_rename.assert_not_called, [], msg="The FileSet tries to rename a file that's already in the right place.")
        self.assertEqual(test_set.files, result_files, "The FileSet unnecessarily changes the file's index.")
        self.assertEqual(test_set.max_index, 3, "The FileSet unnecessarily changes the max_index.")
        
    def test_multi_assigned_specify_specific_type(self):
        """The FileSet should be able to only move the file with the given file_type when dealing with a multi-assigned index.""" 
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (2).png', 'test (3).jpg'] 
         
        test_set = FileSet(self.pattern, test_files)
        test_set.change_index(2, 4, 'png')
        
        result_files = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg'], 4: ['png']}
        
        assertion_calls = [
                (mock_rename.assert_called_once_with , ['test (2).png', 'test (4).png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet does not correctly rename only the single files of the multi-assigned index when the file type is stated.")
        self.assertEqual(test_set.files, result_files, "The FileSet fails to update its logical file list accordingly when only moving a single type of the multi-assigned index.")
        self.assertEqual(test_set.max_index, 4, "The FileSet fails to update its max_index when only moving one type of a multi-assigned index.")
        
    def test_multi_assigned_specified_type_does_not_exist(self):
        """The FileSet should recognize when a requested file_type does not exist in the (multi-)assigned index."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg'] 
         
        test_set = FileSet(self.pattern, test_files)
        with self.assertRaises(FileSet.TypeUnassignedError, msg="The FileSet fails to recognize when a type to be moved is not actually assigned."):
            test_set.change_index(2, 4, 'png')
    
    def test_change_max_index_downwards(self):
        """The FileSet should recognize and update the max index correctly if it is moved downwards."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (3).jpg']
        
        test_set = FileSet(self.pattern, test_files)
        test_set.change_index(3, 1)
        
        self.assertEqual(test_set.max_index, 2, "The FileSet fails to update to the correct max index.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()