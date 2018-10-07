'''
Created on 25.08.2018

@author: FM
'''
import unittest
from FileSet import FileSet


class StandardInitalizerTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    
    def test_initialization(self):
        """The initializer should be able to create a FileSet object."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg']
        
        try:
            test_set = FileSet(self.pattern, test_files)
        except TypeError:
            self.fail("The FileSet fails to take the given file list at all") 
        
        self.assertEqual(test_set.pattern, self.pattern, "The pattern returned by the object is not the same as the one it was created with.")
        
        self.assertTrue(test_set.fitting_file_regex.match("test (3).png"),      "The FileSet's pattern RegEx fails to match a fitting file")
        self.assertTrue(test_set.fitting_file_regex.match("test (3).png.tgz"),  "The FileSet's pattern RegEx fails to match a fitting file")
        self.assertTrue(test_set.fitting_file_regex.match("test (3)"),          "The FileSet's pattern RegEx fails to match a fitting file")
        
    def test_initialize_empty_set(self):
        """The initializer should be able to create a FileSet object with no files."""
        test_set = FileSet(self.pattern, [])
        
        self.assertEqual(test_set.pattern, self.pattern, "The created FileSet object does not contain the correct pattern.")
        self.assertEqual(test_set.files, {}, "The file list of the set is not empty.")
    
    def test_initialize_compiled_files(self):
        """The Initializor should be able to create a FileSet object given a compiled list of files."""
        test_files = {1: ['jpg'], 2: ['png']}
        test_set = FileSet(self.pattern, test_files, file_list_compiled=True)
        
        self.assertEqual(test_set.pattern, self.pattern, "The created FileSet object does not contain the correct pattern.")
        self.assertEqual(test_set.files, test_files, "The created FileSet object does not contain the correct file list.")
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()