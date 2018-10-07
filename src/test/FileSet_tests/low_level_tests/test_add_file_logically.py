'''
Created on 29.09.2018

@author: FM
'''
import unittest
from FileSet import FileSet

class AddFileLogicallyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    
    def test_add_new_index(self):
        """The method should be able to register a new index if the given one is not assigned already."""
        test_files = []
        test_set = FileSet(self.pattern, test_files)
        
        test_set._add_file_logically(1, 'png')
        
        expected_files = {1: ['png']}
        self.assertEqual(test_set.files, expected_files, "The FileSet fails to correctly add a file if its index is not already assigned.")
        
    def test_add_existing_index(self):
        """The method should be able to add the file to the file types list if the given index is already assigned."""
        test_files = ['test (1).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set._add_file_logically(1, 'mp4')
        
        expected_files = {1: ['jpg', 'mp4']}
        self.assertEqual(test_set.files, expected_files, "The FileSet fails to correctly add a file if its index is not already assigned.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()