# Set-Managing-Tool
A tool that facilitates the creation and management of files following a numbered naming pattern

## Purpose
This tool is able to manage a set of files following a numbered naming pattern, mostly independent of file type/file extension.

Here's an example for a valid file set:
    
    test0.jar
    test1.jpg
    test2.mp3
    test3.gif

The `Set Managing Tool` is able to recognize, manage and manipulate such a set of files on the file name level.

Supported operations include renaming the set (i.e. changing its naming pattern), adding new files, removing existing files, moving files to a new position within the set and switching files' positions.  

### Flaws

The program is also able to deal with so-called "flaws". The following would be considered a flawed file set:

    test0.jpg
    test2.png
    test3.txt
    test3.tgz

Obviously, the set is lacking a file with the name `test1`, i.e. the index `1` is missing. Any range of unassigned indexes is called a *"gap"*.  
Additionally, the name `test3` exists two times, with two files of different types. Therefore, the index `3` is called a *"multi-assigned index"*.

Though not openly supporting them, the tool is able to work with file sets that contain such flaw, usually even trying to preserve them unless stated otherwise. Of course, the tool is also able to fix such flaws with the corresponding commands and options.

## Usage

NOTE: *This software is developed and maintained using Python 3.X. It has never been tested in Python 2.X.*

### API
The API consists mainly of the core of this project, found within the `FileSet.py`, containing the `FileSet` class of the same name.

Every major method has a PyDoc explaining its purpose, parameters, errors and quirks; therefore, it should be fairly easy to get things started. The classdocs contain a definition of some of the most frequently used terminology within the code.

### CLI
The CLI is meant to save the user some (if not much) typing in comparison to using the plain API in a Python shell. It rests in the `CLI.py` file.

As of now, the CLI needs to be launched within the same directory the `FileSet.py` and the file set to be managed reside in. There currently is no way to change directory.

One option to launch the command line interface is to open up a terminal emulator, navigate into the file set's directory and simply run `python CLI.py` or `python3 CLI.py`.  
Alternatively, if the `pyLauncher` or another opening command is registered accordingly, a double click onto the `CLI.py` file should suffice as well. 

For all further steps, running the command "help" within the CLI should give the necessary information.

### GUI
A GUI has not yet been created. But be patient, for it is already planned some time in the far, far future! 