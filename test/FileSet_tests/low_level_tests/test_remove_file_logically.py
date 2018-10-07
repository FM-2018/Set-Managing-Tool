'''
Created on 29.09.2018

@author: FM
'''
import unittest
from FileSet import FileSet

class RemoveFileLogicallyTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    
    def test_remove_single_file_index(self):
        """The method should remove the entire index from the file set's files dictionary if it is assigned to only one file type."""
        test_files = ['test (0).jpg', 'test (1).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set._remove_file_logically(0, 'jpg')
        
        expected_files = {1: ['jpg']}
        self.assertEqual(test_set.files, expected_files, "The method fails to correctly remove the entire single-assigned index.")
        
    def test_remove_file_type_multi_assigned_index(self):
        """The method should remove only the according file type if the given index is multi-assigned."""
        test_files = ['test (0).jpg', 'test (0).png', 'test (0).mp4', 'test (1).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set._remove_file_logically(0, 'jpg')
        
        expected_files = {0: ['png', 'mp4'], 1: ['jpg']}
        self.assertEqual(test_set.files, expected_files, "The method fails to correctly remove only one file type from the multi-assigned index.")
        
    def test_index_unassigned(self):
        """The method should raise an error if the given index is unassigned."""
        test_files = []
        test_set = FileSet(self.pattern, test_files)
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The method fails to recognize when an index doesn't exist."):
            test_set._remove_file_logically(0, 'jpg')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()