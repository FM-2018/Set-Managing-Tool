'''
Created on 26.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_scandir_gen

mock_scandir = mock.MagicMock(name='scandir')
@mock.patch('FileSet.scandir', new=mock_scandir)
class FilesDetectedInitializerTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_scandir.reset_mock()
    
    
    def test_simple_coherent_file_set(self):
        """The FileSet should be able to detect its files if they are coherent."""
        test_files = [('test (0).jpg', True), ('test (1).jpg', True), ('test (2).jpg', True), ('test (3).jpg', True)]
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}, "The FileSet fails to auto-detect and compile the files.")
        
    def test_multi_assigned_indexes(self):
        """The FileSet should be able to detect its files even if there are multi-assigned indexes."""
        test_files = [('test (0).jpg', True), ('test (1).jpg', True), ('test (2).jpg', True), ('test (2).png', True), ('test (3).jpg', True)]
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {0: ['jpg'], 1: ['jpg'], 2: ['jpg', 'png'], 3: ['jpg']}, "The FileSet fails to correctly identify multi-assigned indexes.")
        
    def test_dirt_files(self):
        """The FileSet should be able to detect its files even if there are unrelated files in the directory."""
        test_files = [('dirt16.mp4', True), ('test (0).jpg', True), ('tLfaqi60.m4a', True), ('test (1).jpg', True), ('test (2).jpg', True), 
                      ('dirt54.gif', True), ('test (3).jpg', True), ('test (4).jpg', True), ('test (5).jpg', True)] 
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg'], 4: ['jpg'], 5: ['jpg']}, "The FileSet fails to filter files that do not belong to it.")
        
    def test_empty_directory(self):
        """The FileSet should be able to deal with being created in an empty directory and thus finding no files."""
        test_files = []
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {}, "The FileSet fails when instructed to look for files in an empty directory.")
        
    def test_no_fitting_files(self):
        """The FileSet should find no fitting files if there indeed are only unrelated files in the directory."""
        test_files = [('this.mp3', True), ('is', True), ('a.test', True)]
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {}, "The FileSet falsely identifies files in a directory which doesn't contain fitting files at all.")
        
    def test_directories(self):
        """The FileSet should disregard directories, be they fitting to the pattern or not."""
        test_files = [('test (0).jpg', True), ('test (1).jpg', True), ('test (2).jpg', True), ('folder', False), ('test (3).jpg', True), ('test (4)', False)]
        mock_scandir.return_value = mock_scandir_gen(test_files)
         
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}, "The FileSet fails to correctly auto-detect its files if there are directories (that fit its pattern).")
    
    def test_multi_extension_files(self):
        """The FileSet should be able to auto-detect and deal with multi-extension files (e.g. tar.gz)."""
        test_files = [('test (0).jpg', True), ('test (1).jp.g', True), ('test (2).tar.gz', True), ('test (3).a.b.c.d.e', True)]
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {0: ['jpg'], 1: ['jp.g'], 2: ['tar.gz'], 3: ['a.b.c.d.e']}, "The FileSet fails to auto-detect and process files with a multi-extension.")
        
    def test_no_extension_files(self):
        """The FileSet should be able to auto-detect and deal with files that don't have an extension."""
        test_files = [('test (0).jpg', True), ('test (1)', True), ('test (2).jpg', True), ('test (2)', True)]
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        test_set = FileSet.files_detected(self.pattern)
        self.assertEqual(test_set.files, {0: ['jpg'], 1: [''], 2: ['jpg', '']}, "The FileSet fails to auto-detect and process files that do not have a file extension.")
    
    def test_find_extension_pattern_containing_dots(self):
        """The FileSet should be able to find the correct file extensions given that the pattern contains dots."""
        test_files = [('.this.that0.jpg', True), ('.this.that1.jpg.gz', True), ('.this.that2', True), ('.this.that3.png', True)]
        mock_scandir.return_value = mock_scandir_gen(test_files) 
        
        pattern = ('.this.that', '')
        test_set = FileSet.files_detected(pattern)
        
        self.assertEqual(test_set.files, {0: ['jpg'], 1: ['jpg.gz'], 2: [''], 3: ['png']}, "The FileSet fails to find the correct file extensions if the pattern contains dots and the files are auto-detected.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()