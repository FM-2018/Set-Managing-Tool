'''
Useful methods to generate static lists of files for writing FileSet tests (to be used in the Python shell)

Created on 25.08.2018

@author: FM
'''
import os
import random
from tkinter import Tk
import re

file_types = ['jpg', 'png', 'gif', 'mp4', 'pdf', 'm4a']
pattern = ('test (', ')') 

def _format_and_clip(file_list):
    # TODO: add Linux and OSX compatibility
    files_string = ", ".join(file_list)    
    list_string = "[" + files_string + "]"
    os.system("echo {} | clip".format(list_string))
    
def _gen_type(use_rnd_types):
    global file_types
    
    if use_rnd_types:
        type_index = random.randint(0, len(file_types)-1)
        return file_types[type_index]
    else:
        return 'jpg'
    
def _get_rnd_name():
    type_id = random.randint(0, 1)
    
    if type_id == 0:
        ## Name is gibberish
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
        name = []
        for _ in range(random.randint(3, 16)):
            char_index = random.randint(0, len(alphabet)-1)
            name.append(alphabet[char_index])
        name = "".join(name)
    elif type_id == 1:
        ## Name is one of a set with a random index.
        index = random.randint(0, 100)
        name = "dirt{}".format(index)
    
    return name

def gen_files(pattern, max_index, use_rnd_types=False):
    """
    Generate a list of files and copy to clipboard (Only Windows).
    
    @param pattern: The naming pattern the files shall follow as a pattern tuple
    @param max_index: The highest index of the file set
    @param use_rnd_types: Randomize types from a list corresponding to the default file_types list of the FileSet class (default: False, only use jpg)
    """
    left_pattern, right_pattern = pattern
    
    file_list = []
    for i in range(max_index+1):
        file_type = _gen_type(use_rnd_types)
        file = "'{}{}{}.{}'".format(left_pattern, i, right_pattern, file_type)
        file_list.append(file)
        
    _format_and_clip(file_list)
    
def gen_files_with_gaps(pattern, max_index, gap_list, use_rnd_types=False):
    """
    Generate a list of files with gaps in the specified places and copy to clipboard (Only Windows).
    
    @param pattern: The naming pattern the files shall follow as a pattern tuple
    @param max_index: The highest index of the file set
    @param gap_list: A list of indexes which shall be left unassigned
    @param use_rnd_types: Randomize types from a list corresponding to the default file_types list of the FileSet class (default: False, only use jpg)
    """
    left_pattern, right_pattern = pattern
    
    file_list = []
    for i in range(max_index+1):
        file_type = _gen_type(use_rnd_types)
        if not i in gap_list:
            file = "'{}{}{}.{}'".format(left_pattern, i, right_pattern, file_type)
            file_list.append(file)
    
    _format_and_clip(file_list)

def gen_dirty_files(pattern, max_index, dirt_amount, use_rnd_types=False):
    """
    Generate a list of files with unrelated files instead at the specified indexes and copy to clipboard (Only Windows).
    
    This is a two-way operation. First, the full, dirty list of files is copied to the clipboard. After another user input, the clean list of files is copied.
    
    @param pattern: The naming pattern the files shall follow as a pattern tuple
    @param max_index: The highest index of the file set
    @param dirt_amount: The amount of unrelated files which shall be created
    @param use_rnd_types: Randomize types from a list corresponding to the default file_types list of the FileSet class (default: False, only use jpg)
    """
    left_pattern, right_pattern = pattern
    
    file_list = []
    clean_list = []
    dirt_count = 0
    for i in range(max_index+1):
        random_int = random.randint(0, max_index)
        
        ## Generate dirt files with a certain chance so that by average, the right amount of them will be created, but never more than dirt_amount specifies
        while random_int < dirt_amount and dirt_count < dirt_amount:
            file_type = _gen_type(True)
            name = _get_rnd_name()
            file_list.append("'{}.{}'".format(name, file_type))
            dirt_count += 1
            ## Give another chance, so that two dirt files may follow each other; but halve the chances
            random_int = random.randint(0, max_index)*2
        
        file_type = _gen_type(use_rnd_types)
        clean_list.append("'{}{}{}.{}'".format(left_pattern, i, right_pattern, file_type))
        file_list.append("'{}{}{}.{}'".format(left_pattern, i, right_pattern, file_type))
            
    ## If not all dirt files have been generated yet, put them here at the end of the list
    while dirt_count < dirt_amount:
        file_type = _gen_type(True)
        name = _get_rnd_name()
        file_list.append("{}.{}".format(name, type))
        dirt_count += 1
    
    _format_and_clip(file_list)
    
    input(">>>>> CLEAN LIST READY. PRESS ANY KEY")
    
    _format_and_clip(clean_list)

def gen_dirty_files_with_gaps(pattern, max_index, dirt_amount, gap_list, use_rnd_types=False):
    """
    Generate a list of files with gaps and/or unrelated files at the specified indexes and copy to clipboard (Only Windows).
    
    This is a two-way operation. First, the full, dirty list of files is copied to the clipboard. After another user input, the clean list of files, but still with the gaps, is copied.
    
    @param pattern: The naming pattern the files shall follow as a pattern tuple
    @param max_index: The highest index of the file set
    @param dirt_list: A list of indexes which shall be skipped and instead cause an unrelated file to be created
    @param use_rnd_types: Randomize types from a list corresponding to the default file_types list of the FileSet class (default: False, only use jpg)
    """
    left_pattern, right_pattern = pattern
    
    file_list = []
    clean_list = []
    dirt_count = 0
    for i in range(max_index+1):
        random_int = random.randint(0, max_index)
        
        ## Generate dirt files with a certain chance so that by average, the right amount of them will be created, but never more than dirt_amount specifies
        while random_int < dirt_amount and dirt_count < dirt_amount:
            file_type = _gen_type(True)
            name = _get_rnd_name()
            file_list.append("'{}.{}'".format(name, file_type))
            dirt_count += 1
            ## Give another chance, so that two dirt files may follow each other; but halve the chances
            random_int = random.randint(0, max_index)*2
        
        if not i in gap_list:
            file_type = _gen_type(use_rnd_types)
            clean_list.append("'{}{}{}.{}'".format(left_pattern, i, right_pattern, file_type))
            file_list.append("'{}{}{}.{}'".format(left_pattern, i, right_pattern, file_type))
            
    ## If not all dirt files have been generated yet, put them here at the end of the list
    while dirt_count < dirt_amount:
        file_type = _gen_type(True)
        name = _get_rnd_name()
        file_list.append("{}.{}".format(name, type))
        dirt_count += 1
    
    _format_and_clip(file_list)
    
    input(">>>>> CLEAN LIST READY. PRESS ANY KEY")
    
    _format_and_clip(clean_list)

def conv_files_to_mock_scandir():
    """Convert the list of files that's been created by one of the above methods to a list of tuples for the mock_scandir_gen from testing_tools.py."""
    list_string = Tk().clipboard_get()
    
    mock_scandir_string = re.sub(r"('[^']+')", r"(\1, True)", list_string)
    
    os.system("echo {} | clip".format(mock_scandir_string))