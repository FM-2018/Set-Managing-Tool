'''
Created on 12.10.2018

@author: fabian
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, mock_assert_many_msg

mock_rename = mock.MagicMock(name='rename')

@mock.patch('FileSet.rename', new=mock_rename)
class ChangePatternTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.default_pattern = ('test (', ')')
        cls.test_set = FileSet(cls.default_pattern, [])
        
        cls.new_pattern = ('new', '')
    
    def tearDown(self):
        mock_rename.reset_mock()
        
        self.test_set.pattern = self.default_pattern
    
    
    def test_simple_set(self):
        """The method should be able to rename all files of a continuous file set and update the file set's pattern."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg'], 2: ['jpg'], 3: ['jpg']}
         
        self.test_set.change_pattern(self.new_pattern)
         
        assertion_calls = [
                (mock_rename.assert_any_call, ['test (0).jpg', 'new0.jpg']),
                (mock_rename.assert_any_call, ['test (1).jpg', 'new1.jpg']),
                (mock_rename.assert_any_call, ['test (2).jpg', 'new2.jpg']),
                (mock_rename.assert_any_call, ['test (3).jpg', 'new3.jpg'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to correctly rename the files.")
        self.assertEqual(self.test_set.pattern, self.new_pattern, "The method fails to update the file set's pattern.")
         
    def test_no_files(self):
        """The method should be able to deal with a file set that contains no files and update the file set's pattern."""
        self.test_set.files = {}
         
        self.test_set.change_pattern(self.new_pattern)
         
        mock_assert_msg(mock_rename.assert_not_called, [], "The method tries to rename files even though there are none.")
        self.assertEqual(self.test_set.pattern, self.new_pattern, "The method fails to update the file set's pattern.")
     
    def test_set_with_gaps(self):
        """The method should be able to rename all files of a file set with gaps and update the file set's pattern."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg'], 3: ['jpg'], 6: ['jpg']}
         
        self.test_set.change_pattern(self.new_pattern)
         
        assertion_calls = [
                (mock_rename.assert_any_call, ['test (0).jpg', 'new0.jpg']),
                (mock_rename.assert_any_call, ['test (1).jpg', 'new1.jpg']),
                (mock_rename.assert_any_call, ['test (3).jpg', 'new3.jpg']),
                (mock_rename.assert_any_call, ['test (6).jpg', 'new6.jpg'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to correctly rename the files.")
        self.assertEqual(self.test_set.pattern, self.new_pattern, "The method fails to update the file set's pattern.")
         
    def test_multi_assigned_indexes(self):
        """The method should be able to rename all files of a file set that has multi-assigned indexes and update the file set's pattern."""
        self.test_set.files = {0: ['jpg'], 1: ['jpg', 'png', 'mp4'], 2: ['jpg']}
         
        self.test_set.change_pattern(self.new_pattern)
         
        assertion_calls = [
                (mock_rename.assert_any_call, ['test (0).jpg', 'new0.jpg']),
                (mock_rename.assert_any_call, ['test (1).jpg', 'new1.jpg']),
                (mock_rename.assert_any_call, ['test (1).png', 'new1.png']),
                (mock_rename.assert_any_call, ['test (1).mp4', 'new1.mp4']),
                (mock_rename.assert_any_call, ['test (2).jpg', 'new2.jpg'])
            ]
        mock_assert_many_msg(assertion_calls, "The method fails to correctly rename the files.")
        self.assertEqual(self.test_set.pattern, self.new_pattern, "The method fails to update the file set's pattern.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()