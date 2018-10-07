'''
Created on 07.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from CLI import list_files
from test.testing_tools import mock_assert_msg


mock_print = mock.MagicMock(name='print')

@mock.patch('CLI.print', new=mock_print)
class ListFilesTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_print.reset_mock()
        
    
    def test_flawless_set(self):
        """The CLI should be able to q the files of a flawless file set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        list_files(test_set, '')
        
        expected_print_list = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        expected_string = ', '.join(expected_print_list)
        mock_assert_msg(mock_print.assert_called_once_with, [expected_string], "The CLI fails to list the files of a flawless file set.")
        
    def test_gaps_in_set(self):
        """The CLI should be able to list the files of a file set and additionally mark its gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (4).jpg', 'test (6).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        list_files(test_set, '')
        
        expected_print_list = ['test (0).jpg', 'test (1).jpg', 'G', 'G', 'test (4).jpg', 'G', 'test (6).jpg']
        expected_string = ', '.join(expected_print_list)
        mock_assert_msg(mock_print.assert_called_once_with, [expected_string], "The CLI fails to list the files and gaps of a file set.")
        
    def test_multi_assigned_indexes(self):
        """The CLI should be able to list the files of a file set and additionally mark files that share a multi-assigned indexes."""
        test_files = ['test (0).jpg', 'test (1).gif', 'test (1).jpg', 'test (1).png', 'test (2).jpg', 'test (3).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        list_files(test_set, '')
        
        expected_print_list = ['test (0).jpg', '[//: test (1).gif', 'test (1).jpg', 'test (1).png :\\\\]', 'test (2).jpg', 'test (3).jpg']
        expected_string = ', '.join(expected_print_list)
        mock_assert_msg(mock_print.assert_called_once_with, [expected_string], "The CLI fails to list the files of a file set and mark those that share multi-assigned indexes .")
        
    def test_empty_set(self):
        """The CLI should recognize and inform the user when a file set contains no files at all."""
        test_files = [] 
        test_set = FileSet(self.pattern, test_files)
        
        list_files(test_set, '')
        
        expected_string = "The file set '{}' is empty.".format(str(test_set))
        mock_assert_msg(mock_print.assert_called_once_with, [expected_string], "The CLI fails to recognize an empty file set.")
        
    def test_gaps_and_multi_assigned(self):
        """The CLI should be able to deal with gaps and multi-assigned indexes both at once."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (4).jpg', 'test (5).jpg', 'test (5).png']
        test_set = FileSet(self.pattern, test_files)
        
        list_files(test_set, '')
        
        expected_print_list = ['test (0).jpg', 'test (1).jpg', 'G', 'G', 'test (4).jpg', '[//: test (5).jpg', 'test (5).png :\\\\]']
        expected_string = ', '.join(expected_print_list)
        mock_assert_msg(mock_print.assert_called_once_with, [expected_string], "The CLI fails to list the files and gaps of a file set while marking those that share multi-assigned indexes.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()