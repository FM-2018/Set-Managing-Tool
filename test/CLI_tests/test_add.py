'''
Created on 05.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
import CLI
from CLI import add, CLIError, CLIRuntimeError, SpotExpansionError,\
    InputProcessingError
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, mock_assert_many_msg


mock_add_files = mock.MagicMock(name='FileSet.add_files')
mock_add_file_set = mock.MagicMock(name='FileSet.add_file_set')
mock_expand_spot = mock.MagicMock(name='_expand_spot')
mock_isfile = mock.MagicMock(name='os.path.isfile')

@mock.patch('FileSet.FileSet.add_files', new=mock_add_files)
@mock.patch('FileSet.FileSet.add_file_set', new=mock_add_file_set)
@mock.patch('CLI._expand_spot', new=mock_expand_spot)
@mock.patch('CLI.os.path.isfile', new=mock_isfile)
class AddTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_set = FileSet(('test (', ')'), [])
    
    def tearDown(self):
        mock_expand_spot.reset_mock()
        mock_isfile.reset_mock()
        mock_add_files.reset_mock()
        mock_add_file_set.reset_mock()
        
        mock_isfile.side_effect = None
        mock_expand_spot.side_effect = None
    
    
    def test_valid_operation(self):
        """The CLI should be able to perform a simple, valid add-operation."""
        test_args = ['+', 'file.jpg', '3/4']
        mock_expand_spot.return_value = (3, 4)
        mock_isfile.return_value = True
        CLI.file_set_cache = []
        
        try:
            add(self.test_set, test_args)
        except CLIError:
            self.fail("The CLI raised an error during a fully valid operation.")
        
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The CLI tries to add files from a FileSet even though the file doesn't belong to one.")
        mock_assert_msg(mock_add_files.assert_called_once_with, [['file.jpg'], (3, 4)], "The CLI fails to perform a simple add operation.")
    
    def test_valid_operation_multiple_files(self):
        """The CLI should be able to add multiple files at once if there are numerous names given."""
        test_args = ['+', 'file1.jpg', 'file2.jpg', 'file3.jpg', '4/5']
        mock_expand_spot.return_value = (4, 5)
        mock_isfile.return_value = True
        CLI.file_set_cache = []
        
        add(self.test_set, test_args)
        
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The CLI tries to add files from a FileSet even though none of the files belong to one.")
        mock_assert_msg(mock_add_files.assert_called_once_with, [['file1.jpg', 'file2.jpg', 'file3.jpg'], (4, 5)], "The CLI fails to add multiple files in a single operation.")
        
    def test_file_not_found(self):
        """The CLI should raise a CLIRuntimeError if the given file is not found."""
        test_args = ['+', 'unreal', '1/2']
        mock_expand_spot.return_value = (1, 2)
        mock_isfile.return_value = False
        CLI.file_set_cache = []
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when a file to be added doesn't actually exist."):
            add(self.test_set, test_args)
        
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The CLI performs an operation even though the file to be added doesn't exist.")
        mock_assert_msg(mock_add_files.assert_not_called, [], "The CLI tries to perform an operation even though the file to be added doesn't exist.")
        
    def test_one_file_of_multiple_not_found(self):
        """The CLI should raise a CLIRuntimeError if one or more of the given files is not found. It should perform NO operation apart from that."""
        test_args = ['+', 'real1.jpg', 'unreal', 'real2.jpg', '1/2']
        mock_expand_spot.return_value = (1, 2)
        mock_isfile.side_effect = lambda x: x != 'unreal'
        CLI.file_set_cache = []
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to recognize when one of the files to be added doesn't actually exist."):
            add(self.test_set, test_args)
        
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The CLI performs an operation even though one of the files to be added doesn't exist.")
        mock_assert_msg(mock_add_files.assert_not_called, [], "The CLI performs an operation even though one of the files to be added doesn't exist.")
        
    def test_no_file_set(self):
        """The CLI should raise a CLIRuntimeError if no file set has been selected to perform the operation on."""
        test_args = ['+', 'file.jpg', '3/4']
        mock_expand_spot.return_value = (3, 4)
        mock_isfile.return_value = True
        CLI.file_set_cache = []
        
        with self.assertRaises(CLIRuntimeError, msg="The CLI fails to raise an exception when no file set has been selected."):
            add(None, test_args)
        
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The CLI performs an operation even though there is no file set to perform it on.")
        mock_assert_msg(mock_add_files.assert_not_called, [], "The CLI tries to perform an operation even though there is no file set to perform it on.")
    
    def test_invalid_spot(self):
        """The CLI should check the spot for validity and raise an exception if the spot is invalid."""
        test_args = ['+', 'file.jpg', '3/4']
        mock_expand_spot.side_effect = SpotExpansionError()
        mock_isfile.return_value = True
        CLI.file_set_cache = []
         
        with self.assertRaises(InputProcessingError, msg="The CLI fails to recognize an invalid spot."):
            add(self.test_set, test_args)
            
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The CLI performs an operation even though the given spot is invalid.")
        mock_assert_msg(mock_add_files.assert_not_called, [], "The CLI tries to perform an operation even though the given spot is invalid.")
        
    @mock.patch('FileSet.FileSet.file_in_set')
    def test_file_already_in_other_set(self, mock_file_in_set):
        """The CLI should check whether the files to be added are present in another set and remove them if necessary."""
        test_args = ['+', 'set1.jpg', '3/4']
        mock_expand_spot.return_value = (3, 4)
        mock_isfile.return_value = True
        mock_file_in_set.return_value = (True, 1)
        
        other_test_set = FileSet(('set', ''), ['set1.jpg'])
        CLI.file_set_cache = [other_test_set]
        
        add(self.test_set, test_args)
        
        mock_assert_msg(mock_add_file_set.assert_called_once_with, [other_test_set, (3, 4), [1]], "The CLI fails to correctly add the file if it already is in another file set.")
        mock_assert_msg(mock_add_files.assert_called_once_with, [[], (4, 5)], "The CLI tries to add a file conventionally, even though it required special treatment due to being in a known FileSet.")
    
    def test_files_in_set_and_uncategorized_mixed(self):
        """The CLI should be able to deal with a mixture of files in a set and non-categorized files both at once."""
        test_args = ['+', 'set1.jpg', 'file.png', 'otherSet0.gif', 'nextFile.jpg', 'otherSet1.jpg', '1/2']
        mock_expand_spot.return_value = (1, 2)
        mock_isfile.return_value = (True)
        
        def mock_file_in_set_set_one(file):
            if file == 'set1.jpg':
                return (True, 1)
            else:
                return (False, None)
        def mock_file_in_set_set_two(file):
            if file == 'otherSet0.gif':
                return (True, 0)
            elif file == 'otherSet1.jpg':
                return (True, 1)
            else:
                return (False, None)
            
        other_test_set_one = FileSet(('set', ''), ['set1.jpg'])
        other_test_set_two = FileSet(('otherSet', ''), ['otherSet0.gif', 'otherSet1.jpg'])
        other_test_set_one.file_in_set = mock_file_in_set_set_one
        other_test_set_two.file_in_set = mock_file_in_set_set_two
        CLI.file_set_cache = [other_test_set_one, other_test_set_two]
        
        add(self.test_set, test_args)
        
        assertion_calls = [
                (mock_add_file_set.assert_any_call, [other_test_set_one, (1, 2), [1]]),
                (mock_add_file_set.assert_any_call, [other_test_set_two, (2, 3), [0]]),
                (mock_add_file_set.assert_any_call, [other_test_set_two, (3, 4), [1]])
            ]
        mock_assert_many_msg(assertion_calls, "The CLI fails to correctly identify and add the files which already belong to another set.")
        mock_assert_msg(mock_add_files.assert_called_once_with, [['file.png', 'nextFile.jpg'], (4, 5)], "The CLI fails to correctly identify and add the files which don't belong to any other set.")        
    
    @mock.patch('FileSet.FileSet.file_in_set')
    def test_file_aready_in_other_set_multi_assigned_index(self, mock_file_in_set):
        """The CLI should detect if a file to be added is present in another set and remove it in case, preserving the other files if it is a multi-assigned index in that set."""
        ## TODO: how to realize keeping multi assigned indexes intact?
#         test_args = ['+', '3/4', 'set1.jpg']
#         mock_expand_spot.return_value = (3, 4)
#         mock_isfile.return_value = True
#         mock_file_in_set.return_value = (True, 1)
#         
#         other_test_set = FileSet(('set', ''), ['set1.jpg', 'set1.png'])
#         CLI.file_set_cache = [other_test_set]
#         
#         add(self.test_set, test_args)
#         mock_assert_msg(mock_add_file.assert_called_once_with, ['set1.jpg', (3, 4)], "The CLI doesn't actually try to add the file.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()