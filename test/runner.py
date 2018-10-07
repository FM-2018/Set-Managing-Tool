'''
Created on 25.08.2018

@author: FM
'''
import unittest
import os
import sys


def list_available_start_dirs():
    """
    List all available directories along with a unique number.
    
    All directories and sub-directories, including the one this module resides in, are seen as available.
    
    @return: A list of 2-tuples containing the listed number along with the directory path.
    """
    print("\n## SELECT START DIRECTORY ##")
    
    start_path = None
    dir_path_dic = {}
    cache_dir_count = 0
    for i, dir_info in enumerate(os.walk(os.getcwd())):
        dir_path, _, _ = dir_info
        i -= cache_dir_count # make sure __pycache__ directories don't count
        
        if start_path is None: start_path = dir_path
        
        nest_count = 0
        split_path = dir_path
        while split_path != start_path:
            nest_count += 1
            split_path, _ = os.path.split(split_path)
        
        dir_name = os.path.basename(dir_path)
        if not  dir_name == '__pycache__': # skip __pycache__ directories
            print(str(i) + ' '*(nest_count*2+1) + dir_name)
            
            dir_path_dic.update( {i: dir_path} )
        else:
            cache_dir_count += 1
    
    return dir_path_dic
    
def ask_user_selection(dir_path_dic):
    """
    Ask the user for the starting directory they want to use to load tests from.
    
    @return: Path of the directory the user chose
    """
    max_selection_number = max(dir_path_dic.keys())
    
    dir_selection = input("\nWhich directory and sub-directories to load tests from? ")
    
    while True:
        try:
            dir_selection = int(dir_selection)
        except ValueError:
            dir_selection = input("The given choice is not a number. Try again: ")
            continue
            
        if dir_selection > max_selection_number:
            dir_selection = input("The given choice is too high. Try again: ")
            continue
        elif dir_selection < 0:
            dir_selection = input("The given choice is negative. Try again: ")        
            continue
        
        break
    
    return dir_path_dic[dir_selection]

def load_available_tests(start_dir_path):
    """Load/Import all the tests found in the given directory and its sub-directories."""
    for dir_path, _, files in os.walk(start_dir_path): 
        
        if not os.path.basename(dir_path) == '__pycache_': # skip __pycache__ directories
            sys.path.append(dir_path)
            
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    module_name = file[:-3] # slice away .py
                    
                    """
                    Mimic the behavior of import * as suggested by user2357112 on stackoverflow:
                    https://stackoverflow.com/questions/41990900/what-is-the-function-form-of-star-import-in-python-3/41991139#41991139
                    """
                    module = __import__(module_name, fromlist=['*'])
                    if hasattr(module, '__all__'):
                        all_names = module.__all__
                    else:
                        all_names = [name for name in dir(module) if not name.startswith('_')]
                    
                    globals().update({name: getattr(module, name) for name in all_names})


dir_path_dic = list_available_start_dirs()

start_dir_path = ask_user_selection(dir_path_dic)

load_available_tests(start_dir_path)

if __name__ == '__main__':
    unittest.main()