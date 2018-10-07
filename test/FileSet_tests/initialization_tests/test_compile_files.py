'''
Created on 25.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet


mock_find_max_index = mock.MagicMock(name='_find_max_index')
@mock.patch('FileSet.FileSet._find_max_index', new=mock_find_max_index)
class CompileFilesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_find_max_index.reset_mock()
    
    
    def test_simple_coherent_file_set(self):
        """The FileSet should be able to compile a coherent list of files."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        mock_find_max_index.return_value = 3
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile a list of files.")
        
    def test_files_with_gaps(self):
        """The FileSet should be able to deal with gaps by not adding them to the files dictionary."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (3).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        mock_find_max_index.return_value = 8
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {0: ['jpg'], 2: ['jpg'], 3: ['jpg'], 6: ['jpg'], 7: ['jpg'], 8: ['jpg']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile a list of files if it contains gaps.")
        
    def test_empty_file_set(self):
        """The FileSet should be able to deal with an empty list of files."""
        test_files = []
        mock_find_max_index.return_value = -1
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile an empty list of files.")
        
    def test_various_file_types(self):
        """The FileSet should be able to deal with various file types."""
        test_files = ['test (0).mp4', 'test (1).pdf', 'test (2).png', 'test (3).m4a', 'test (4).pdf', 'test (5).gif', 'test (6).gif', 'test (7).m4a', 'test (8).gif']
        mock_find_max_index.return_value = 8
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {0: ['mp4'], 1: ['pdf'], 2: ['png'], 3: ['m4a'], 4: ['pdf'], 5: ['gif'], 6: ['gif'], 7: ['m4a'], 8: ['gif']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile a list of files with various file types.")
        
    def test_multi_assigned_indexes(self):
        """The FileSet should be able to process multi-assigned indexes."""
        test_files = ['test (0).pdf', 'test (1).jpg', 'test (2).mp4', 'test (2).mp3', 'test (2).png', 'test (3).mp4', 'test (4).pdf', 'test (4).bmp', 'test (5).m4a']
        mock_find_max_index.return_value = 5
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {0: ['pdf'], 1: ['jpg'], 2: ['mp4', 'mp3', 'png'], 3: ['mp4'], 4: ['pdf', 'bmp'], 5: ['m4a']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile a list of files if there are multi-assigned indexes.")
        
    def test_compile_shuffled_indexes(self):
        """The FileSet should be able to deal with a list of files even if the files are in incorrect order."""
        test_files = ['test (5).png', 'test (2).jpg', 'test (8).mp4', 'test (4).jpg', 'test (0).png', 'test (2).png']
        mock_find_max_index.return_value = 8
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {5: ['png'], 2: ['jpg', 'png'], 8: ['mp4'], 4: ['jpg'], 0: ['png']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile a list of files if the indexes are in a random order.")
        
    def test_multi_extension_files(self):
        """The Fileset should be able to compile files even if they have a multi-extension (e.g. .tar.gz)."""
        test_files = ['test (0).jpg', 'test (1).j.p.g', 'test (2).sync.tx', 'test (3).tar.gz']
        mock_find_max_index.return_value = 3
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {0: ['jpg'], 1: ['j.p.g'], 2: ['sync.tx'], 3: ['tar.gz']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile a list of files if there are files with multi-extensions.")
        
    def test_no_extension_files(self):
        """The FileSet should be able to compile files even if they have no extension at all."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (2)', 'test (3).jpg']
        mock_find_max_index.return_value = 3
        
        test_set = FileSet(self.pattern, test_files)
        
        result_dic = {0: ['jpg'], 2: ['jpg', ''], 3: ['jpg']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to compile a list of files if there are files with no extension at all.")
    
    def test_find_extension_pattern_containing_dots(self):
        """The FileSet should be able to compile files and find their correct file extensions if the given pattern contains dots."""
        test_files = ['.this.that0.jpg', '.this.that1.jp.g', '.this.that2.tar.gz', '.this.that3']
        mock_find_max_index.return_value = 3
        
        pattern = ('.this.that', '')
        test_set = FileSet(pattern, test_files) 
        
        result_dic = {0: ['jpg'], 1: ['jp.g'], 2: ['tar.gz'], 3: ['']}
        self.assertEqual(test_set.files, result_dic, "The FileSet fails to correctly compile files if the pattern contains dots.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()