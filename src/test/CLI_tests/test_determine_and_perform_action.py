'''
Created on 03.10.2018

@author: FM
'''
import unittest
import unittest.mock as mock
import CLI
from CLI import determine_and_perform_action
from test.testing_tools import mock_assert_msg
from FileSet import FileSet


mock_add = mock.MagicMock(name='add')
mock_remove = mock.MagicMock(name='remove')
mock_move = mock.MagicMock(name='move')
mock_switch = mock.MagicMock(name='switch')

mock_list_files = mock.MagicMock(name='list_files')
mock_choose = mock.MagicMock(name='choose')
mock_rename = mock.MagicMock(name='rename')
mock_create = mock.MagicMock(name='create')
mock_help = mock.MagicMock(name='print_help')
mock_fix = mock.MagicMock(name='fix')

mock_print = mock.MagicMock(name='print')

registered_mocks = [mock_add, mock_remove, mock_move, mock_switch, 
                    mock_list_files, mock_choose, mock_rename,
                    mock_create, mock_help, mock_fix, mock_print]


def _assert_only_this_mock_called(expectedly_called_mock, expected_call_args):
    """Convenience method for asserting whether a given mock has been called, while all others should not have been called."""
    global registered_mocks
    
    for mock in registered_mocks:
        if mock is expectedly_called_mock:
            mock_assert_msg(mock.assert_called_once_with, [*expected_call_args], "The method fails to perform the expected action.")
        else:
            mock_assert_msg(mock.assert_not_called, [], "The method performs a wrong action.") 


@mock.patch('CLI.add', new=mock_add)
@mock.patch('CLI.remove', new=mock_remove)
@mock.patch('CLI.move', new=mock_move)
@mock.patch('CLI.switch', new=mock_switch)
@mock.patch('CLI.list_files', new=mock_list_files)
@mock.patch('CLI.choose', new=mock_choose)
@mock.patch('CLI.rename', new=mock_rename)
@mock.patch('CLI.create', new=mock_create)
@mock.patch('CLI.print_help', new=mock_help)
@mock.patch('CLI.fix', new=mock_fix)
@mock.patch('CLI.print', new=mock_print)
class DetermineAndPerformActionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pattern = ('test (', ')')
        cls.active_file_set_dummy = FileSet(pattern, [])
    
    def setUp(self):
        CLI.active_file_set = self.active_file_set_dummy
    
    def tearDown(self):
        mock_add.reset_mock()
        mock_remove.reset_mock()
        mock_move.reset_mock()
        mock_switch.reset_mock()
        
        mock_list_files.reset_mock()
        mock_choose.reset_mock()
        mock_rename.reset_mock()
        mock_create.reset_mock()
        mock_help.reset_mock()
        mock_fix.reset_mock()
        
        mock_print.reset_mock()
        
    
    def test_call_add(self):
        """The method should correctly call only the add method and pass the given arguments to it."""
        args_list = ['+', 'new_file', '1/2']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_add, [self.active_file_set_dummy, args_list])
        
    def test_call_remove(self):
        """The method should correctly call only the remove method and pass the given arguments to it."""
        args_list = ['-', '1', '3-4']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_remove, [self.active_file_set_dummy, args_list])
    
    def test_call_move(self):
        """The method should correctly call only the move method and pass the given arguments to it."""
        args_list = ['1-3', '>', '4/5']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_move, [self.active_file_set_dummy, args_list])
        
    def test_call_switch(self):
        """The method should correctly call only the switch method and pass the given arguments to it."""
        args_list = ['3', '~', '4']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_switch, [self.active_file_set_dummy, args_list])
    
    def test_call_list_files(self):
        """The method should correctly call only the list_files method and pass the given arguments to it."""
        args_list = ['list']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_list_files, [self.active_file_set_dummy, args_list])
    
    def test_call_choose(self):
        """The method should correctly call only the choose method and pass the given arguments to it."""
        args_list = ['choose', '0']
         
        determine_and_perform_action(args_list)
         
        _assert_only_this_mock_called(mock_choose, [self.active_file_set_dummy, args_list])
        
    def test_call_rename(self):
        """The method should correctly call only the rename method and pass the given arguments to it."""
        args_list = ['rename', 'new*name']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_rename, [self.active_file_set_dummy, args_list])

    def test_call_create(self):
        """The method should correctly call only the create method and pass the given arguments to it."""
        args_list = ['create', 'File*Set']
         
        determine_and_perform_action(args_list)
         
        _assert_only_this_mock_called(mock_create, [args_list])
        
    def test_call_print_help(self):
        """The method should correctly call only the print_help method and pass the given arguments to it."""
        args_list = ['help', 'me']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_help, [self.active_file_set_dummy, args_list])
        
    def test_call_fix(self):
        """The method should correctly call only the fix method and pass the given arguments to it."""
        args_list = ['fix', 'all']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_fix, [self.active_file_set_dummy, args_list])
    
    def test_no_action_applies(self):
        """The method should print an according message if no correct action could be determined by the given arguments."""
        args_list = ['gib', 'ber', 'ish']
        
        determine_and_perform_action(args_list)
        
        _assert_only_this_mock_called(mock_print, ['The given command or operation could not be resolved.'])
    
    def test_no_arguments_given(self):  
        """The method should do nothing if an empty list of arguments was given."""
        args_list = []
        
        determine_and_perform_action(args_list)
        
        ## Make a new mock that is unregistered in the global list. That way, it will never be
        ## checked whether it was actually ever called. It will only be checked whether
        ## all of the registered once have NOT been called.
        _assert_only_this_mock_called(mock.MagicMock(), [])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()