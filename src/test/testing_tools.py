'''
Methods that facilitate testing with mocks by enabling the usage of a failure message.

Created on 27.08.2018

@author: FM
'''
from collections import namedtuple
import types # get access to types such as function or method)

## TODO: create class MockAssertionError and implement a string method for better readability

class InvalidMockMethodError(Exception):
    """Raised when a passed mock_method is not actually a method."""


#------------------------------------------------------------------------------
# Generator that allows mocking os.scandir()
#------------------------------------------------------------------------------ 
class _MockedEntry():
    def __init__(self, name, is_file_bool):
        self.name = name
        
        self.is_file = (lambda: is_file_bool) # is_file is expected to be a function, thus lambda

def mock_scandir_gen(entry_file_tuples):
    """
    Return an iterator that can be used as a scandir mock's return value.
    
    @param entry_file_tuple: 
    """
    for entry_name, is_file_bool in entry_file_tuples:
        yield _MockedEntry(entry_name, is_file_bool)
#------------------------------------------------------------------------------ 


#------------------------------------------------------------------------------ 
# Class required to perform mock assertions with keyword arguments
#------------------------------------------------------------------------------ 
KeywordArgTuple = namedtuple('KeywordArgTuple', 'key value')

def _split_args_and_kwargs(argument_list):
    """Split the given list of arguments into a list of plain arguments and a dictionary of keyword arguments."""
    kwargs = {}
    args = []
    for arg in argument_list:
        if type(arg) is KeywordArgTuple:
            key, value = arg
            kwargs.update({key: value})
        else:
            args.append(arg)
    
    return args, kwargs
#------------------------------------------------------------------------------ 


#------------------------------------------------------------------------------ 
# Procedures that allow performing mock assertions and 
# print a unittest-like message upon failure
#------------------------------------------------------------------------------ 
def mock_assert_msg(mock_method, given_args, msg):
    """
    Use a mock assertion method and print a certain message upon failure.
    
    @param mock_method: The mock assertion method
    @param given_args: A list of arguments to call the mock_method with. Keyword arguments need to be wrapped in a KeywordArgTuple
    @param msg: The message to display upon failure
    """
    
    if not isinstance(mock_method, types.MethodType):
        raise InvalidMockMethodError("The given method '{}' is not a method.".format(mock_method))
    
    args, kwargs = _split_args_and_kwargs(given_args)
    
    try:
        mock_method(*args, **kwargs)
    except AssertionError as e:
        raise AssertionError(e.args, msg)

def mock_assert_many_msg(calls, msg):
    """
    Use one or more mock assertions methods and print a certain message upon failure of one or more of the assertions.
    
    @param calls: An iterable of 'calls', i.e. tuples containing (mock_method, given_args) as explained in mock_assert_msg.
    @param msg: The message to display upon failure of at least one of the assertions
    """
    try:
        for call in calls:
            mock_method, given_args = call
            
            if not isinstance(mock_method, types.MethodType):
                raise InvalidMockMethodError("The given method '{}' is not a method.".format(mock_method))
            
            args, kwargs = _split_args_and_kwargs(given_args)
            mock_method(*args, **kwargs)
    except AssertionError as e:
        raise AssertionError(e.args, msg)
#------------------------------------------------------------------------------ 