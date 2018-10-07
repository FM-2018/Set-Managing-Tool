'''
Created on 25.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet


mock_compile_files = mock.MagicMock(name='_compile_files')
@mock.patch('FileSet.FileSet._compile_files', new=mock_compile_files)
class FindMaxIndexTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')        
    
    def tearDown(self):
        mock_compile_files.reset_mock()
    
    
    def test_simple_coherent_file_set(self):
        """The FileSet should be able to find its max_index in this simple case."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 
                     'test (7).jpg', 'test (8).jpg', 'test (9).jpg', 'test (10).jpg', 'test (11).jpg', 'test (12).jpg'] 
        mock_compile_files.return_value = {0: 'jpg', 1: 'jpg', 2: 'jpg', 3: 'jpg', 4: 'jpg', 5: 'jpg', 6: 'jpg', 
                                           7: 'jpg', 8: 'jpg', 9: 'jpg', 10: 'jpg', 11: 'jpg', 12: 'jpg'}
        
        test_set = FileSet(self.pattern, test_files)
        self.assertEqual(test_set.max_index, 12, "max_index isn't correctly determined for a simple, coherent list of files.")
        
    def test_gaps(self):
        """The FileSet should be able to find its max_index even if there are gaps."""
        test_files = ['test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (7).jpg']
        mock_compile_files.return_value = {1: 'jpg', 3: 'jpg', 4: 'jpg', 7: 'jpg'}
        
        test_set = FileSet(self.pattern, test_files)
        self.assertEqual(test_set.max_index, 7, "max_index isn't correctly determined when there are gaps in the file set.")
        
    def test_empty_file_list(self):
        """The FileSet should set its max_index to -1 if there are no files currently in the set."""
        test_files = []
        mock_compile_files.return_value = {}
        
        test_set = FileSet(self.pattern, test_files)
        self.assertEqual(test_set.max_index, -1, "max_index isn't set to -1 when the file set is empty.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()