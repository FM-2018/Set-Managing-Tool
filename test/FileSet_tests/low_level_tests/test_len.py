'''
Created on 04.10.2018

@author: FM
'''
import unittest
from FileSet import FileSet


class LenTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    
    def test_one_file(self):
        """The FileSet should return 1 if it contains only one file."""
        test_files = ['test (1).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        self.assertEqual(len(test_set), 1, "The FileSet fails to return its correct len if it contains only one file.")
    
    def test_multiple_files(self):
        """The FileSet should return the correct number if it contains multiple files."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        self.assertEqual(len(test_set), 3, "The FileSet fails to return its correct len if it contains multiple files.")
    
    def test_multiple_files_multi_assigned_index(self):
        """The FileSet should return the correct number if it has a multi-assigned index."""
        test_files = ['test (0).jpg', 'test (0).png', 'test (1).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        self.assertEqual(len(test_set), 3, "The FileSet fails to return its correct len if it contains multiple files and a multi-assigned-index.")
        
    def test_no_files(self):
        """The FileSet should return 0 if it contains no files."""
        test_files = []
        test_set = FileSet(self.pattern, test_files)
        
        self.assertEqual(len(test_set), 0, "The FileSet fails to return its correct len if it contains no files at all.")  

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()