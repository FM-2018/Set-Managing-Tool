'''
Created on 24.08.2018

@author: FM
'''
import math
import os
import re
import shlex
import shutil

from FileSet import FileSet

## TODO: path and directory management
DEFAULT_REMOVE_PATTERN = ('RMVD', '')
INVALID_CHARS_REGEX = re.compile('[' + re.escape(r'\/:*?"<>|') + ']')
INDEX_INDICATOR = FileSet.INDEX_INDICATOR
file_set_cache = [] # a list of file sets in this directory (reset upon directory change)
active_file_set = None
default_remove_set = None # the file set into which files shall be removed
split_pattern_regex = re.compile(r'(?<!\\)(\\\\)*' + re.escape(FileSet.INDEX_INDICATOR))

class CLIError(Exception):
    """Base exception for CLI errors."""
    def __init__(self, *args):
        super().__init__(*args)
        self.msg = args[-1]
    
    def __str__(self):
        return self.msg

class InputProcessingError(CLIError):
    """Raised when the user arguments can't be processed as expected due to being invalid."""
    pass

class RangeExpansionError(InputProcessingError):
    """Raised when a range expansion fails for whatever reason."""
    pass

class SpotExpansionError(InputProcessingError):
    """Raised when a spot expansion fails for whatever reason."""
    pass

class PatternExpansionError(InputProcessingError):
    """Raised when a pattern expansion fails for whatever reason."""
    pass

class CLIRuntimeError(CLIError):
    """Raised when an exception occurs during runtime."""
    pass

class TerminateProgram(CLIError):
    """Raised to inform callers once the program should be terminated cleanly."""
    
class ArgumentAmountError(CLIError):
    """Raised when there is an invalid number of arguments supplied."""

#===============================================================================
# Methods powering the commands and operators
#===============================================================================

#------------------------------------------------------------------------------ 
# Commands
#------------------------------------------------------------------------------ 
def list_files(file_set, _):
    """Print a list of files in the FileSet and mark gaps as well as multi-assigned indexes."""
    ## TODO: use colored output for multi-assigned indexes and gaps for better readability; or print flaws in bold?
    if file_set is None:
        raise CLIRuntimeError("No file set has been selected!")
    
    gaps, multi_indexes = file_set.find_flaws()
    
    ## Format gaps and multi-assigned indexes into list and dictionary
    gap_index_list = []
    for gap in gaps:
        left_gap, right_gap = gap
        gap_index_list += list(range(left_gap, right_gap+1))
    multi_index_dic = {}
    for index, file_types in multi_indexes:
        multi_index_dic.update({index: file_types})
        
    files_list = file_set.get_files_list()
    
    ## Collect files, gaps, and multi-assigned indexes
    print_list = []
    multi_idx_offset = 0
    gap_offset = 0
    for i in range(file_set.max_index+1):
        multi_types = multi_index_dic.get(i)
        if multi_types is not None:
            for j in range(len(multi_types)):
                if j == 0:
                    print_list.append('[//: '  + files_list[i+multi_idx_offset-gap_offset+j])
                elif j == len(multi_types)-1:
                    print_list.append(files_list[i+multi_idx_offset-gap_offset+j] + ' :\\\\]')
                else:
                    print_list.append(files_list[i+multi_idx_offset-gap_offset+j])
            multi_idx_offset += len(multi_types)-1
        
        elif i in gap_index_list:
            print_list.append('G')
            gap_offset += 1
        
        else:
            print_list.append(files_list[i+multi_idx_offset-gap_offset])
    
    ## Print results
    if len(print_list) != 0:
        print(', '.join(print_list))
    else:
        print("The file set '{}' is empty.".format(str(file_set)))

def choose(_, user_args):
    """Choose the file set with the given number (2nd argument), or, if no number is supplied, list all available cached file sets."""
    if len(user_args) > 2:
        raise ArgumentAmountError("Choose takes 1 to 2 arguments. You supplied {}. Usage: choose [SET_NUMBER]".format(len(user_args)))
    elif len(user_args) == 1: # only typed 'choose'
        _enumerate_available_sets()
    else:
        try:
            num = int(user_args[1])
        except ValueError:
            raise InputProcessingError("The number '%s' is not a valid integer." % user_args[1])
        
        ## Select file set from cache
        try:
            global active_file_set
            active_file_set = file_set_cache[num]
        except IndexError:
            raise CLIRuntimeError("There is no file set with the number %s!" % num)

def _enumerate_available_sets():
    """List the file sets in file_set_cache along with a unique number to reference each of them."""
    global file_set_cache
    
    if len(file_set_cache) == 0:
        print('No file sets have been found in this directory.')
    else:
        for i, file_set in enumerate(file_set_cache):
            print(i, '\t', str(file_set))

def create(user_args):
    """
    Create a new file set with the supplied pattern or choose an existing one if one with the same pattern already exists.
    
    Expected user arguments: create PATTERN
    
    @return: The new or existing file set having the given pattern
    """
    if len(user_args) < 2 or len(user_args) > 2:
        raise ArgumentAmountError("create expects exactly 2 arguments. You supplied {}. Usage: create PATTERN".format(len(user_args)-1))
    
    pattern = _expand_pattern(user_args[1])
    
    global file_set_cache
    new_file_set = None
    for file_set in file_set_cache:
        if file_set.pattern == pattern:
            new_file_set = file_set
            break 
    
    if new_file_set is None:
        new_file_set = FileSet.files_detected(pattern)
        
    file_set_cache.append(new_file_set)
    return new_file_set

def rename(file_set, user_args):
    """Rename / change the pattern of the currently selected file set."""
    global file_set_cache
    
    if file_set is None:
        raise CLIRuntimeError("No file set has been selected!")
    
    args_len = len(user_args)
    if args_len != 2:
        raise ArgumentAmountError("Rename expects exactly 2 arguments. You supplied {}. Usage: rename NEW_PATTERN".format(args_len))
    
    new_pattern = _expand_pattern(user_args[1])
    
    ## Check whether such a pattern is already used by a known file set. If yes, can't rename!
    for cached_file_set in file_set_cache:
        if cached_file_set.pattern == new_pattern:
            raise CLIRuntimeError("There already is a file set with the pattern '{}'!".format(new_pattern))
    
    file_set.change_pattern(new_pattern)

def print_help(_1, _2):
    """Print the usage and commands of this CLI."""
    
    DESC = "Create, manipulate and manage file sets."
    print(DESC)
    print()
    
    print('## TERMINOLOGY ##')
    PATTERN = ('Pattern: File*Set', 'The naming pattern for the files of a file set. The running index is indicated using an asterisk (*).')
    RANGE = ('Range: n-m', 'A range of indexes separated by a dash. The indexes specify the according files of the file set.')
    SPOT = ('Spot: n/m', 'Two adjacent indexes separated by a slash. The spot is considered to be right in between those two indexes.')
    _print_elements(PATTERN, RANGE, SPOT)
    print()
    
    print('## COMMANDS ##')
    CREATE =    ('create SET_PATTERN',  'Create a file set with the supplied pattern. If a FileSet with this pattern already exists, select it.')
    CHOOSE =    ('choose [SET_NUMBER]', 'Choose the file set with the supplied number. If no number is supplied, all auto-detected and known file_sets will be listed to choose from. In case this fails to bring up the FileSet you are looking for, you can still select it by using: "create PATTERN"')
    RENAME =    ('rename NEW_PATTERN'),'Rename / change the pattern of the currently selected file set.'
    LIST =      ('list',                'List all files currently in the set in adjacent order')
    EXIT =      ('exit',                'Exit the current file set. If no file set is selected, terminate the program.')
    TERMINATE = ('terminate',           'Terminate the program.')
    _print_elements(CREATE, CHOOSE, RENAME, LIST, EXIT, TERMINATE)
    print()
    
    print('## OPERATIONS ##')
    ADD =       ('+ FILE_NAME [FILE_NAME [..]] SPOT',    'Add one or more files to the currently selected file set. If the file name contains spaces, it needs to be surrounded by quotes.')
    REMOVE =    ('- [-n NEW_SET_PATTERN | -a EXISTING_SET_PATTERN] INDEXES [INDEXES [..]] [-pg|-sg]',
                                                      'Remove one or more files from the currently selected file set based on their indexes. They may be given as a range or as a single integer. If NEW_SET_NAME is supplied, the files will be appended to a file set of this pattern.')
    MOVE =      ('INDEXES > SPOT [-pg|-sg]',          'Move one or more files to the specified position. The files may be specified as a range of indexes or as a single integer. The positions is expected as a spot.')
    SWITCH =    ('INDEXES ~ INDEXES [-pg|-sg]',       'Switch two files or file ranges with each other. The files may be specified as a range of indexes or as a single integer.')
    _print_elements(ADD, REMOVE, MOVE, SWITCH)
    print()
    
def _print_elements(*elements, target_distance=32):
    """
    Format and print the supplied element 2-tuples.
    
    Every element is a tuple consisting of command/usage and description.
    The descriptions are separated from the commands using tab spaces.
    The description is word-wrapped at about 50 characters.
    Additional lines for a single descriptions are indented with a space.
    
    @param *elements: The supplied tuples to be formatted and printed
    @param target_distance: Target distance of the description from the beginning of the line (default: 32)
    """
    TAB_LENGTH = 8 # one tab character may take the space of up to 8 normal characters
    
    for element in elements:
        cmd, desc = element
        
        cmd_length = len(cmd)
        leftover_distance = target_distance-cmd_length
        if leftover_distance > 4:
            required_tabs = math.ceil(leftover_distance/TAB_LENGTH)
            separator = '\t'*required_tabs
        else:
            separator = '\n\t\t\t\t'
        
        desc_lines = []
        leftover_desc = desc
        while len(leftover_desc) > 50:
            next_space = None
            for i in range(40, len(leftover_desc)):
                if leftover_desc[i] == ' ': 
                    next_space = i
                    break
            
            if next_space is not None:
                wrapped_desc = leftover_desc[:next_space]
                leftover_desc = leftover_desc[next_space+1:]
                
                desc_lines.append(wrapped_desc)
            else:
                ## TODO: instead of appending too long line, search for space in before 40 and break there
                break # append this line even though it is too long
        desc_lines.append(leftover_desc)
        
        desc = ('\n' + '\t'*math.ceil(target_distance/TAB_LENGTH) + '  ').join(desc_lines)
        
        print(cmd, desc, sep=separator)

def fix(file_set, user_args):
    """
    Automatically fix flaws in the file set (primarily gaps).
    
    If 'fix all' is used, also automatically fix multi-assigned indexes.
    
    @raise InputProcessingError: The user input is invalid
    """ 
    if file_set is None:
        raise CLIRuntimeError("No file set has been selected!")
    
    if len(user_args) == 1:
        file_set.fix()
    elif len(user_args) == 2:
        if user_args[1] == 'all':
            try:
                file_set.fix(True)
            except FileSet.TooManyFilesError as e:
                raise CLIRuntimeError(*e.args)
        else:
            raise InputProcessingError(user_args, "The command '{} {}' can't be understood. Did you mean to put: 'fix all'?".format(user_args[0], user_args[1]))
    else:
        raise InputProcessingError(user_args, "Fix takes zero to one argument(s). You supplied {}.".format(len(user_args)-1))
        

#------------------------------------------------------------------------------ 
# Operations
#------------------------------------------------------------------------------
def _get_gap_handling_kwarg(chosen_option):
    """
    Return a dictionary representing the gap-handling keyword argument to pass to the FileSet's method.
    
    @raise InputProcessingError: The given option is not a valid gap handling option
    """ 
    options = {
            '-sg': {'strip_gaps': True},
            '-pg': {'preserve_gaps': True}
        }
    
    try:
        return options[chosen_option]
    except KeyError:
        raise InputProcessingError("The option '{}' is not a valid gap-handling option.".format(chosen_option))

def add(file_set, user_args):
    """
    Validate the user input and add the specified file(s).
    
    Expected user arguments: + NAME+ SPOT
    
    @raise CLIRuntimeError: The given file set is None OR one of the given files does not exist
    @raise SpotExpansionError: The given spot is invalid
    @raise RuntimeError: The user input is valid, but leads to an invalid operation 
    """
    if file_set is None:
        raise CLIRuntimeError("No file set has been selected!")
    
    ## Process Arguments
    args_len = len(user_args)
    if args_len < 3:
        raise ArgumentAmountError("Add expects at least 3 arguments. You supplied {}. Usage: + NAME+ SPOT".format(args_len))
    else:
        left_spot, right_spot = _expand_spot(user_args[-1]) # last argument
        file_names = user_args[1:-1] # second to before-last argument
    
    for file_name in file_names:
        if not os.path.isfile(file_name):
            raise CLIRuntimeError("The file '%s' does not exist." % file_name)
    
    ## PERFORM ACTION ##
    ## Deal with files that come from a file set first, one by one
    spot_offset = 0
    non_organized_file_names = []
    for file_name in file_names:
        foreign_file_set = None
        foreign_file_index = None
        for cached_file_set in file_set_cache:
            file_is_in_set, index = cached_file_set.file_in_set(file_name)
            if file_is_in_set:
                foreign_file_set = cached_file_set
                foreign_file_index = index
                break
        
        if foreign_file_set is not None:
            new_spot = (left_spot+spot_offset, right_spot+spot_offset)
            file_set.add_file_set(foreign_file_set, new_spot, [foreign_file_index])
            spot_offset += 1 # spot for next addition has to be further to the right. Since only 1 file is added here, offset increases by 1
        else:
            non_organized_file_names.append(file_name)
    
    ## Add all leftover, unorganized files in bulk (i.e., files which don't belong to a known FileSet)
    new_spot = (left_spot+spot_offset, right_spot+spot_offset)
    file_set.add_files(non_organized_file_names, new_spot)

def remove(file_set, user_args):
    """
    Validate the user input and remove the file(s) with the specified index(es).
    
    Gaps within the index ranges are ignored.
    
    Expected user arguments: - [-n|-a PATTERN] RANGE+ [-pg|-sg]
    
    @raise InputProcessingError: The user input is invalid (i.e. an invalid gap handling option has been given)
    @raise ArgumentAmountError: An invalid number of arguments is given
    @raise CLIRuntimeError: The given file set is None OR option -n or -a is used inappropriately
    @raise PatternExpansionError: The pattern given to option -n or -a is invalid
    @raise RangeExpansionError: One or more of the given ranges are invalid 
    """
    ## TODO: what if user enters same integer twice or has overlapping ranges?
    global default_remove_set
    global file_set_cache
    
    if file_set is None:
        raise CLIRuntimeError("No file set has been selected!")
    
    if len(user_args) < 2:
        raise ArgumentAmountError("Remove expects at least 2 arguments. You supplied {}.".format(len(user_args)))
    
    ## Determine which set to remove the files into.
    # Either create a new one, append to an existing one, or append to the default remove set if no option is given.
    if user_args[1] == '-n':
        optional_arg_one_set = True
        pattern_string = user_args[2]
        pattern = _expand_pattern(pattern_string)
        
        for cached_file_set in file_set_cache:
            if cached_file_set.pattern == pattern:
                ## If file set already exists, raise error
                raise CLIRuntimeError(pattern_string, "There already is a file set with the pattern '{}'. Try -a instead!".format(pattern_string))
            
        remove_set = FileSet.files_detected(pattern)
        file_set_cache.append(remove_set)
        
    elif user_args[1] == '-a':
        optional_arg_one_set = True
        pattern_string = user_args[2]
        pattern = _expand_pattern(pattern_string)
        ## Search for file set with this pattern in file_set_cache
        remove_set = None
        for cached_file_set in file_set_cache:
            if cached_file_set.pattern == pattern:
                remove_set = cached_file_set
                break 
        
        if remove_set is None: ## If no fitting set has been found, raise error
            raise CLIRuntimeError(pattern_string, "No existing file set has been found with the pattern '{}'. Try -n instead!".format(pattern_string))
        
    else:
        optional_arg_one_set = False
        if default_remove_set is not None:
            remove_set = default_remove_set
        else:
            # NOTE: this is only safe if the DEFAULT_REMOVE_PATTERN can automatically be detected by detect_file_sets.
            # Else, FileSet.files_detected might be a better choice
            # TODO: dynamically resolve this default_remove_pattern detection issue?
            remove_set = FileSet(DEFAULT_REMOVE_PATTERN, [])
            default_remove_set = remove_set
            file_set_cache.append(remove_set)
        
        if file_set == default_remove_set:
            raise CLIRuntimeError(remove_set, "If you want to remove from the file set that files are usually removed into ('{}')," + 
                "you need to specify another one to add the removed files to using -n or -a.".format(remove_set.pattern))
        
    ## Check last argument in case it is a gap-handling option
    last_arg = user_args[-1]
    if last_arg.startswith('-'):
        gap_hndlng_kwarg = _get_gap_handling_kwarg(last_arg)
        last_optional_arg_set = True
    else:
        gap_hndlng_kwarg = {} # no gap handling
        last_optional_arg_set = False
    
    ## Find indexes to remove
    if not optional_arg_one_set:
        if last_optional_arg_set:
            index_ranges = user_args[1:-1]
        else:
            index_ranges = user_args[1:]
    else:
        if last_optional_arg_set:
            index_ranges = user_args[3:-1]
        else:
            index_ranges = user_args[3:]
    
    index_list = []
    for index_range in index_ranges:
        left_range, right_range = _expand_range(index_range)
        new_indexes = list(range(left_range, right_range+1))
        index_list += new_indexes
    
    ## Removal operation
    try:
        file_set.remove_files(index_list, remove_set, **gap_hndlng_kwarg)
    except FileSet.IndexUnassignedError as e:
        raise CLIRuntimeError(e.args[0], "The file set does not have a file with the index {}.".format(e.args[0]))
    
def move(file_set, user_args):
    """
    Validate the user input and move the specified file(s). Gaps in the given range are stripped by this operation.
    
    Expected user arguments: RANGE > SPOT [-pg|-sg]
    
    @raise InputProcessingError: The user input is invalid (i.e. an invalid gap handling option has been given) 
    @raise ArgumentAmountError: An invalid number of arguments is given
    @raise CLIRuntimeError: The given file set is None
    @raise RangeExpansionError: The given range is invalid
    @raise SpotExpansionError: The given spot is invalid
    """
    if file_set is None:
        raise CLIRuntimeError("No file set has been selected!")
    
    args_len = len(user_args)
    if args_len < 3:
        raise ArgumentAmountError("Move expects 3 to 4 arguments. You supplied {}.".format(args_len))
    else:
        index_range = _expand_range(user_args[0])
        spot = _expand_spot(user_args[2])
        if args_len == 4:
            option = user_args[3]
            
            gap_hndlng_kwarg = _get_gap_handling_kwarg(option)
        elif args_len > 4:
            raise ArgumentAmountError("Move expects 3 to 4 arguments. You supplied {}.".format(args_len))
        else:
            gap_hndlng_kwarg = {} # no gap handling selected
    
    file_set.move_files(index_range, spot, **gap_hndlng_kwarg)
    

def switch(file_set, user_args):
    """
    Validate the user input and switch the specified files or file ranges.
    
    Expected user arguments: RANGE ~ RANGE [-pg|-sg]
    
    @raise InputProcessingError: The user input is invalid (i.e. an invalid gap handling option has been given)
    @raise ArgumentAmountError: An invalid number of arguments is given
    @raise CLIRuntimeError: The given file set is None
    @raise RangeExpansionError: One or both of the given ranges is/are invalid
    """
    if file_set is None:
        raise CLIRuntimeError("No file set has been selected!")
    
    args_len = len(user_args)
    if args_len < 3:
        raise ArgumentAmountError("Switch expects 3 to 4 arguments. You supplied {}.".format(args_len))
    else:
        range1 = _expand_range(user_args[0])
        range2 = _expand_range(user_args[2])
        if args_len == 4:
            option = user_args[3]
            
            gap_hndlng_kwarg = _get_gap_handling_kwarg(option)
        elif args_len > 4:
            raise ArgumentAmountError("Switch expects 3 to 4 arguments. You supplied {}.".format(args_len))
        else:
            gap_hndlng_kwarg = {} # no gap handling selected
    
    file_set.switch_file_ranges(range1, range2, **gap_hndlng_kwarg)

#===============================================================================
# Methods used for input processing
#===============================================================================

def _expand_pattern(raw_pattern):
    """
    Try to convert a user-input pattern string to a computer-readable pattern tuple.
    
    The index indicator can be escaped by preceding it with a backslash.
    An backslash can be escaped by preceding it with another backslash.
    Single backslashes that do not precede an index indicator aren't modified.
    """
    global split_pattern_regex
    global INDEX_INDICATOR
    
    try:
        left_pattern, backslashes, right_pattern = split_pattern_regex.split(raw_pattern)
        if backslashes is not None:
            left_pattern += backslashes
        
        ## Escape backslashes that are escaped by leading backslash and escape index indicator formally
        left_pattern = left_pattern.replace('\\\\', '\\').replace('\\' + INDEX_INDICATOR, INDEX_INDICATOR)
        right_pattern = right_pattern.replace('\\\\', '\\').replace('\\' + INDEX_INDICATOR, INDEX_INDICATOR)
    except ValueError:
        raise PatternExpansionError(raw_pattern, "The pattern '{}' is invalid. It has to contain exactly one un-escaped asterisk (*)!".format(raw_pattern))
    
    ## TODO: check for invalid characters in pattern names. Maybe rather use a whitelist dependent on File Systems?
    
    return left_pattern, right_pattern


def _expand_spot(raw_spot):
    """
    Try to convert a user-input spot into a computer-readable one, i.e. a tuple.
    
    @raise SpotExpansionError: The range is invalid due to having too many/few integers, containing invalid integers, or the integers not being adjacent.
    """
    try:
        raw_left_spot, raw_right_spot = raw_spot.split('/')
    except ValueError:
        raise SpotExpansionError(raw_spot, "The spot '{}' is invalid. Supply two adjacent integers separated by a slash (/).".format(raw_spot))
    
    try:
        left_spot = int(raw_left_spot)
    except ValueError:
        raise SpotExpansionError(raw_spot, raw_left_spot, "The integer '{}' in the given spot '{}' is invalid.".format(raw_left_spot, raw_spot))
    try:
        right_spot = int(raw_right_spot)
    except ValueError:
        raise SpotExpansionError(raw_spot, raw_right_spot, "The integer '{}' in the given spot '{}' is invalid.".format(raw_right_spot, raw_spot))
    
    if left_spot == right_spot-1:
        return left_spot, right_spot
    elif right_spot == left_spot-1:
        return right_spot, left_spot
    else:
        raise SpotExpansionError(raw_spot, "The spot '{}' is invalid, since the supplied integers are not adjacent.".format(raw_spot))
    
def _expand_range(raw_index_range):
    """
    Try to convert a usually user-input range into a computer-readable one, i.e. a tuple.
    
    If only a single integer is given, it is converted into a range as well (e.g. 4 becomes 4-4)
    
    @param raw_index_range: The range to be converted
    
    @return: The converted range as a named tuple, ordered by smaller to bigger integer
    
    @raise RangeExpansionError: The input range is invalid
    """
    try:
        ## In case only one number is given, convert the string to range
        int1 = int(raw_index_range)
        int2 = int1
    except ValueError:
        ## Otherwise, try to expand raw range string
        integers = tuple(raw_index_range.split("-"))
        try:
            int1, int2 = integers
        except ValueError:
            raise RangeExpansionError(integers, raw_index_range, "The range '{}' is invalid. Supply two integers separated by a dash (-).")
        
        try:
            int1 = int(int1)
        except ValueError:
            raise RangeExpansionError(int1, raw_index_range, "The boundary '{}' of the range '{}' is not a valid integer.".format(int1, raw_index_range))
        try:
            int2 = int(int2)
        except ValueError:
            raise RangeExpansionError(int1, raw_index_range, "The boundary '{}' of the range '{}' is not a valid integer.".format(int1, raw_index_range))
    
    if int2 < int1:
        return (int2, int1)
    else:
        return (int1, int2)

def check_contains_invalid_chars(string):
    """
    Check whether a string contains characters that are invalid for file names.
    
    Invalid characters are: \ / : * ? " < > |
    
    @param string: The string to be checked
    
    @return: A boolean stating whether there are invalid characters (True) or not (False)
    """
    global INVALID_CHARS_REGEX
    
    # TODO: add feature to show which characters are invalid. For instance by iterating over list instead of regex
    # TODO: make OS dependent. Windows has more invalid chars than UNIX
    if INVALID_CHARS_REGEX.search(string):
        return True
    else:
        return False

#===============================================================================
# Runtime methods
#===============================================================================

def detect_file_sets():
    """
    Detect valid file sets in the current directory and cache them. This only includes file sets which's running index is the last integer in its name.
    
    Everything before the first period (.) will be considered the name of the file which determines the detected pattern, 
    while everything after is considered the file extension. (periods at the front are ignored, since they indicate hidden files/patterns)
    """
    pattern_files_dic = {}
    for entry in os.scandir(os.getcwd()):
        if entry.is_file():
            plain_name = re.sub(r"(?<!^)\..+$", "", entry.name) # remove file extension(s), i.e. everything after first dot (except if dot is at the front, indicating a hidden pattern)
            
            try:
                left_pattern, right_pattern = re.split(r"\d+(?!.*\d)", plain_name)
            except ValueError: 
                ## No split occurred; thus the current file doesn't follow a pattern. Skip it.
                continue
            
            pattern = left_pattern, right_pattern
            fitting_files = pattern_files_dic.get(pattern, None)
            if fitting_files is None:
                pattern_files_dic.update({pattern: [entry.name]})
            else:
                fitting_files.append(entry.name)
    
    global file_set_cache
    global default_remove_set
    global DEFAULT_REMOVE_PATTERN
    file_set_cache = [] # initialize/clear cache before updating
    for pattern, files in pattern_files_dic.items():
        new_set = FileSet(pattern, files)
        file_set_cache.append(new_set)
        if pattern == DEFAULT_REMOVE_PATTERN:
            default_remove_set = new_set

def _execute(method, *args):
    """Execute a method and handle CLI-related exceptions by printing their message to the user."""
    try:
        method(*args)
    except CLIError as e:
        print(str(e))

def determine_and_perform_action(args_list):
    """
    Perform an action determined by the given list of command line arguments.
    
    @param args_list: The list of arguments that were given on the command line (or were generated programmatically)
    
    @raise TerminateProgram: The determined action is to terminate the program cleanly
    """
    global active_file_set
    
    ## Action dictionaries; used to translate keywords to commands/actions
    action_dictionary_lv1 = {
            'help':     print_help, 
            'choose':   choose,
            '+':        add,
            '-':        remove,
            'fix':      fix,
            'list':     list_files,
            'rename':   rename
        }
    action_dictionary_lv2 = {
            '>': move,
            '~': switch
        }
    
    
    ## Check first argument of args_list for possibly being the keyword
    if len(args_list) == 0:
        ## No arguments were given at all. Ignore.
        return
    else:
        command_or_operand = args_list[0]

    
    if command_or_operand == 'terminate':
        raise TerminateProgram("Terminate")

    #------------------------------------------------------------------------------
    # Actions that may modify the active_file_set cannot feasibly be contained within
    # an action_dictionary. Therefore, they are checked in separate if statements.
    #------------------------------------------------------------------------------ 
    
    if command_or_operand == 'exit':
        if active_file_set is not None:
            ## Exit current file set
            active_file_set = None
            return
        else:
            ## Exit entire program
            raise TerminateProgram("Terminate")
    
    
    if command_or_operand == 'create':
        active_file_set = create(args_list)
        return
    
    #------------------------------------------------------------------------------ 
    # All other actions are contained in the action_dictionaries.
    #------------------------------------------------------------------------------ 
    
    ## Keyword is found as first element of the list
    action = action_dictionary_lv1.get(command_or_operand)
    if action is not None:
        _execute(action, active_file_set, args_list)
        return
    
    ## Keyword is found as second element of the list (if there is one)
    if len(args_list) >= 2:
        operand = args_list[1]
        action = action_dictionary_lv2.get(operand)
        if action is not None:
            _execute(action, active_file_set, args_list)
            return
    
    ## This statement is only reached if none of the above options applied
    print("The given command or operation could not be resolved.")
    
    
def main():
    ## SETUP
    print("Entering CLI non-stop mode..")    
    detect_file_sets()
    global active_file_set
    print("Type 'help' for a list of commands.")
    
    while True:
        if active_file_set is None:
            active_file_set_string = ''
        else:
            active_file_set_string = "'" + str(active_file_set) + "'"
        
        raw_user_input_string = input('%s> ' % active_file_set_string)
        user_input_string = raw_user_input_string.strip() # strip leading and trailing whitespace
        user_args_string_list = shlex.split(user_input_string) # split arguments, preserving spaces in quotes
        
        try:
            determine_and_perform_action(user_args_string_list)
        except TerminateProgram:
            break
    
    ## TEARDOWN FOR TERMINATION
    shutil.rmtree('__pycache__')
    print("Terminated.")
    exit()

if __name__ == '__main__':
    main()