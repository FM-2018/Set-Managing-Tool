'''
Created on 11.09.2018

@author: FM
'''
import unittest
from FileSet import FileSet

class GetFilesListTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_pattern = ('test (', ')')
        cls.test_set = FileSet(test_pattern, [])
    
    def test_simple_files_list(self):
        """The FileSet should be able to return a simple list of jpeg files."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}
        
        expected_result = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        self.assertEqual(self.test_set.get_files_list(), expected_result, "The FileSet fails to return a list of the files it contains.")
    
    def test_files_list_with_gaps(self):
        """The FileSet should be able to return a list of jpeg files with gaps."""
        self.test_set.files = {0: ['jpg'], 2: ['jpg'], 3: ['jpg'], 6: ['jpg']}
        
        expected_result = ['test (0).jpg', 'test (2).jpg', 'test (3).jpg', 'test (6).jpg']
        self.assertEqual(self.test_set.get_files_list(), expected_result, "The FileSet fails to return a list of the files it contains if there are gaps.")
        
    def test_files_strange_extensions(self):
        """The FileSet should be able to return a list of files even if they have strange or no extension at all."""
        self.test_set.files = {0: ['jpg'], 1: [''], 2: ['tar.gz'], 3: ['gif']}
        
        expected_result = ['test (0).jpg', 'test (1)', 'test (2).tar.gz', 'test (3).gif']
        self.assertEqual(self.test_set.get_files_list(), expected_result, "The FileSet fails to return a list of the files it contains if there are strange or no file extensions.")
    
    def test_correct_order(self):
        """The FileSet should always return the list of files in adjacent order as dictated by their indexes."""
        self.test_set.files = {0: ['jpg'], 2: ['jpg'], 3: ['jpg'], 1: ['jpg']}
        
        expected_result = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        self.assertEqual(self.test_set.get_files_list(), expected_result, "The FileSet fails to return the list of the files it contains in the correct order.")
    
    def test_multi_assigned_indexes_correct_order(self):
        """The FileSet should return a list of multi-assigned indexes in alphabetical order determined by their extensions."""
        self.test_set.files = {0: ['jpg'], 1: ['gif', 'png'], 2: ['rar', 'jpg', 'mp4']}
        
        expected_result = ['test (0).jpg', 'test (1).gif', 'test (1).png', 'test (2).jpg', 'test (2).mp4', 'test (2).rar']
        self.assertEqual(self.test_set.get_files_list(), expected_result, "The FileSet fails to return a correctly ordered list of files it contains if there are multi-assigned indexes.")
        
    def test_empty_file_set(self):
        """The FileSet should return an empty list if it contains no files at all."""
        self.test_set.files = {}
        
        expected_result = []
        self.assertEqual(self.test_set.get_files_list(), expected_result, "The FileSet fails to return an empty list if it contains no files at all.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()