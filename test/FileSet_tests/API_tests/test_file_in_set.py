'''
Created on 11.09.2018

@author: FM
'''
import unittest
from FileSet import FileSet


class FileInSetTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        test_pattern = ('test (', ')')
        cls.test_set = FileSet(test_pattern, [])
    

    def test_fitting_file_in_set(self):
        """The FileSet should return True and the file's index if the given file is currently in the set."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}
        test_file = 'test (1).jpg'
        
        expected_result = (True, 1)
        self.assertEqual(self.test_set.file_in_set(test_file), expected_result, "The FileSet fails to recognize a file that is in its set and return its index.")
        
    def test_fitting_file_not_in_set(self):
        """The FileSet should return False and the file's index if the given file is currently not in the set, but fits its pattern."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}
        test_file = 'test (4).jpg'
        
        expected_result = (False, 4)
        self.assertEqual(self.test_set.file_in_set(test_file), expected_result, "The FileSet fails to recognize a file that is not in the set though fits its pattern and return its index.")
        
    def test_fitting_file_in_set_multi_assigned_index(self):
        """The FileSet should return True and the file's index if the given file is currently in the set even if it's at a multi-assigned index."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg', 'png'], 2: ['jpg'], 3: ['jpg']}
        test_file = 'test (1).jpg'
        
        expected_result = (True, 1)
        self.assertEqual(self.test_set.file_in_set(test_file), expected_result, "The FileSet fails to recognize a file that is in the set return its index if it's at a multi-assigned index..")
        
    def test_fitting_file_not_in_set_though_index_assigned(self):
        """The FileSet should return False and the file's index if the given file is currently not in the set even though the index is (multi-)assigned."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg', 'png'], 2: ['jpg'], 3: ['jpg']}
        test_file = 'test (1).mp4'
        
        expected_result = (False, 1)
        self.assertEqual(self.test_set.file_in_set(test_file), expected_result, "The FileSet fails to recognize a file that is not in the set though fits its pattern and return its index if the index of the file is (multi-)assigned within the set.")
    
    def test_unfitting_file(self):
        """The FileSet should return False and None if the given file does not fit the set's pattern."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}
        test_file = 'un-fit (1).jpg'
        
        expected_result = (False, None)
        self.assertEqual(self.test_set.file_in_set(test_file), expected_result, "The FileSet fails to recognize a file that doesn't and shouldn't belong to the set.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()