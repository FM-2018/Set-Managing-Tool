'''
Created on 02.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from test.testing_tools import mock_scandir_gen, mock_assert_msg, mock_assert_many_msg
import CLI
from CLI import detect_file_sets

mock_scandir = mock.MagicMock(name='scandir')
mock_FileSet = mock.MagicMock(name='FileSet')

@mock.patch('CLI.os.scandir', new=mock_scandir)
@mock.patch('CLI.FileSet', new=mock_FileSet)
class DetectFileSetsTests(unittest.TestCase): #TODO: this doesn't actually test whether the FileSets are really packed into the file_set_cache in the end. Only whether they're correctly created
    
    def tearDown(self):
        mock_scandir.reset_mock()
        mock_FileSet.reset_mock()
    
    
    def test_simple_set_alone(self):
        """The CLI should be able to recognize and create a simple file set sitting alone in the directory."""
        test_files = [('test (0).jpg', True), ('test (1).jpg', True), ('test (2).jpg', True), ('test (3).jpg', True), ('test (4).jpg', True)]
        
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        detect_file_sets()
        
        mock_assert_msg(
                mock_FileSet.assert_called_once_with, 
                [('test (', ')'), ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg']],
                "The CLI fails to find a lonely file set in a directory."""
            )
    
    def test_simple_set_dirt_files(self):
        """The CLI should be able to recognize and create a simple file set even if it's surrounded in unrelated files."""
        test_files = [('TEPPYZGM.png', True), ('test (0).gif', True), ('dirt.gif', True), ('test (1).mp4', True), ('VzC.pdf', True), ('test (2).pdf', True),
                      ('dirt.m4a', True), ('test (3).gif', True), ('test (4).m4a', True), ('test (5).jpg', True), ('test (6).m4a', True), ('test (7).mp4', True)]
        
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        detect_file_sets()
        
        mock_assert_msg(
                mock_FileSet.assert_called_once_with, 
                [('test (', ')'), ['test (0).gif', 'test (1).mp4', 'test (2).pdf', 'test (3).gif', 'test (4).m4a', 'test (5).jpg', 'test (6).m4a', 'test (7).mp4']],
                "The CLI fails to find the correct files and the correct file set if there are dirt files around."
            )
    
    def test_various_sets(self):
        """The CLI should be able to recognize and create all available file sets in the directory."""
        test_files = [('TEPPYZG09M.png', True), ('test (0).gif', True), ('dirt41.gif', True), ('test (1).mp4', True), ('V57zC.pdf', True), ('test (2).pdf', True),
                      ('dirt90.m4a', True), ('test (3).gif', True), ('test (4).m4a', True), ('test (5).jpg', True), ('test (6).m4a', True), ('test (7).mp4', True)]  
        
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        detect_file_sets()
        
        assertion_calls = [
                (mock_FileSet.assert_any_call, [('test (', ')'),    ['test (0).gif', 'test (1).mp4', 'test (2).pdf', 'test (3).gif', 'test (4).m4a', 'test (5).jpg', 'test (6).m4a', 'test (7).mp4']]),
                (mock_FileSet.assert_any_call, [('TEPPYZG', 'M'),   ['TEPPYZG09M.png']]),
                (mock_FileSet.assert_any_call, [('dirt', ''),       ['dirt41.gif', 'dirt90.m4a']]),
                (mock_FileSet.assert_any_call, [('V', 'zC'),        ['V57zC.pdf']])
            ]
        mock_assert_many_msg(assertion_calls, "The CLI fails to find all existent FileSets in a directory.")
    
    def test_multi_extension_types(self):
        """The CLI should correctly identify a set's pattern even if it's files contain multiple extensions (e.g. .tar.gz)."""
        test_files = [('test (0).mp4', True), ('test (1).png', True), ('test (2).gif', True), ('test (3).tar.gz', True), ('test (4).p.n.g', True), ('test (5).jp.gz', True)]
        
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        detect_file_sets()
        
        mock_assert_msg(
                mock_FileSet.assert_called_once_with,
                [('test (', ')'), ['test (0).mp4', 'test (1).png', 'test (2).gif', 'test (3).tar.gz', 'test (4).p.n.g', 'test (5).jp.gz']],
                "The CLI fails to deal with files that have a multi-extension."
            )
        
    def test_hidden_file_set(self):
        """The CLI should correctly identify a hidden set that starts with a dot."""
        test_files = [('.hidden0.jpg', True), ('.hidden1.jpg', True), ('.hidden2.jpg', True), ('.hidden3.jpg', True), ('.hidden4.jpg', True)]
        
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        detect_file_sets()
        
        mock_assert_msg(
                mock_FileSet.assert_called_once_with,
                [('.hidden', ''), ['.hidden0.jpg', '.hidden1.jpg', '.hidden2.jpg', '.hidden3.jpg', '.hidden4.jpg']],
                "The CLI fails to detect and create a hidden file set (i.e. one which's pattern starts with a dot)."
            )
        
    def test_detect_remove_file_set(self):
        """The CLI should correctly identify a file set that is used for the remove operation by default and set it as a global attribute accordingly."""
        test_files = [('test (0).jpg', True), ('test (1).jpg', True), ('test (2).jpg', True), ('test (3).jpg', True), 
                      ('RMVD0.jpg', True), ('RMVD1.jpg', True), ('RMVD2.jpg', True), ('RMVD3.jpg', True)]
        
        mock_scandir.return_value = mock_scandir_gen(test_files)
        
        detect_file_sets() 
        
        assertion_calls = [
                (mock_FileSet.assert_any_call, [('test (', ')'), ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']]),
                (mock_FileSet.assert_any_call, [('RMVD', ''), ['RMVD0.jpg', 'RMVD1.jpg', 'RMVD2.jpg', 'RMVD3.jpg']])
            ]
        mock_assert_many_msg(assertion_calls, "The CLI fails to recognize and create the two file sets.")
        
        self.assertNotEqual(CLI.default_remove_set, None, "The CLI fails to recognize and set the default remove set after stumbling upon it.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()