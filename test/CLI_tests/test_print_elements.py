'''
Created on 01.09.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from CLI import _print_elements
from test.testing_tools import mock_assert_msg, mock_assert_many_msg, KeywordArgTuple

mock_print = mock.MagicMock(name='print')

@mock.patch('CLI.print', new=mock_print)
class PrintElementsTests(unittest.TestCase):
    
    def tearDown(self):
        mock_print.reset_mock()
    
    
    def test_single_short_command(self):
        """The method should be able to print the help text of a single short command with a short description."""
        CMD = ('command', 'a test command')
        
        _print_elements(CMD)
        
        mock_assert_msg(mock_print.assert_called_once_with, ['command', 'a test command', KeywordArgTuple(key='sep', value='\t\t\t\t')], "The CLI help method fails to print a command along with its description.")
        
    def test_multiple_short_commands(self):
        """The method should be able to print the help text of multiple short commands with a short description each."""
        CMD1 = ('first command', 'a test command')
        CMD2 = ('second command', 'another test command')
        
        _print_elements(CMD1, CMD2)
        
        assertion_calls = [
                (mock_print.assert_any_call, ['first command', 'a test command', KeywordArgTuple(key='sep', value='\t\t\t')]),
                (mock_print.assert_called_with, ['second command', 'another test command', KeywordArgTuple(key='sep', value='\t\t\t')])
            ]
        
        mock_assert_many_msg(assertion_calls, "The CLI help method fails to print multiple short commands at once.")
    
    def test_long_desc(self):
        """The method should be able to print the help text of a short command with a long description that requires appropriate word-wrap. Additional lines should be indented with two spaces."""
        CMD = ('my command', 'This is a test command that serves no particular purpose in a production environment and in fact is not even implemented, yet it is quite useful for being used as a test dummy.')
        
        _print_elements(CMD)
        
        expected_wrapped_desc = ''.join([
                "This is a test command that serves no particular",     '\n\t\t\t\t', 
                '  ', "purpose in a production environment and in",     '\n\t\t\t\t',
                '  ', "fact is not even implemented, yet it is quite",  '\n\t\t\t\t',
                '  ', "useful for being used as a test dummy."
            ])
        mock_assert_msg(mock_print.assert_called_once_with, ['my command', expected_wrapped_desc, KeywordArgTuple(key='sep', value='\t\t\t')], "The CLI help method fails to properly format and print a command with a long description.")
    
    def test_long_cmd(self):        
        """The method should put the description onto a new line if the command is too long."""
        CMD = ('insanely LONG COMMAND [--with MANY] OPTIONS', 'command description')
        
        _print_elements(CMD)
        
        mock_assert_msg(mock_print.assert_called_once_with, ['insanely LONG COMMAND [--with MANY] OPTIONS', 'command description', KeywordArgTuple(key='sep', value='\n\t\t\t\t')], "The CLI help method fails to properly print a very long command.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()