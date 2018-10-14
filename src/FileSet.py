'''
Created on 16.06.2018

@author: FM
'''
from os import getcwd, rename, scandir
from os.path import isfile
import re


# TODO: check patterns and add_file/remove_file inputs for forbidden characters | may not be useful, since Linux allows basically everything
# TODO: working directory/path management
# TODO: add check so change_index doesn't change into negative numbers?
# TODO: give warning when multi-assigned indexes are detected at compilation time
# TODO: Refactor KeyError Try/Except statements when deleting and instead use pop
# TODO: Add append_file and append_files ? If yes, use for move and switch operations
# TODO: use dict.get() method where appropriate to get key
# TODO: implement close_gap method
# TODO: polish FileSet and remove unnecessary variables etc
# TODO: implement find_pattersn in FileSet instead of CLI?
# TODO: write a proper classdoc
# TODO: extra object for a files dictionary with useful methods?
# TODO: rework documentation; reflect errors, parameters and special traits
# TODO: add method add_file_sets to optimize addition from multiple sets at once
# TODO: add method "rename" to change file set pattern
class FileSet():
    """
    A class that unites multiple files following a naming pattern into a file set.
    
    # TERMINOLOGY #
    pattern:               A 2-tuple containing the strings to the left and to the right of a running index (excluding file extensions)
    spot:                  A 2-tuple consisting of two adjacent indexes, representing the spot in between them
    file:                  A string representing the name of a file with its file extension. (e.g.: "file1.jpg")
    logically:             Performing an operation on the logical level, e.g. updating the FileSet's internal files dictionary
    physically:            Performing an operation on the physical level, e.g. renaming a file that currently belongs to a FileSet
    unassigned index:      An index that is not used by any file
    gap:                   An unassigned index within the set (meaning that it is smaller than the file set's max_index) 
    multi-assigned index:  An index that is used by more than one file
    """
    type_regex = re.compile(r"(?<!^)\.(.+)$")
    INDEX_INDICATOR = '*'
    
    
    #===========================================================================
    # Custom Errors
    #===========================================================================
    
    class FileSetError(Exception):
        """Base class for FileSet errors."""
    
    class FileCollisionError(FileSetError):
        """Raised when files are attempted to be renamed to file names that already exist."""
    
    class RangeExpansionError(FileSetError):
        """Raised when a given raw (i.e. string) range is invalid."""
    
    class IndexAssignedError(FileSetError):
        """Raised when a file is attempted to be assigned to an index that's already taken by another file within the FileSet."""
    
    class IndexUnassignedError(FileSetError):
        """Raised when a reference to a file is attempted with an index that is not assigned within the set."""
    
    class FileAmbiguityError(FileSetError):
        """Raised in high-level methods when an index represents multiple files at once."""
    
    class NameInputError(FileSetError):
        """Raised when an input name (e.g. a file name or pattern) is invalid, usually due to invalid characters."""
    
    class TypeUnassignedError(FileSetError):
        """Raised when a file_type is suppoed to be moved/changed in index even though it doesn't exist at this position."""
    
    class TooManyFilesError(FileSetError):
        """Raised by find_flaws if a file set with a very high max_index contains too great gaps which would require too long to find.""" 
        
    class ConflictingOptionsError(FileSetError):
        """Raised when a method is called with conflicting options."""
        
    class FileNotFoundError(FileSetError):
        """Raised when a given file name or path could not be found."""
    
    class OverlappingRangesError(FileSetError):
        """Raised during a switch operation if the given ranges overlap."""
    
    #===========================================================================
    # Initialization Methods
    #===========================================================================
    
    def __init__(self, pattern, file_list, **kwargs):
        """
        Create a FileSet object.
        
        @param pattern: The pattern the FileSet should follow in the form of a 2-tuple containing the strings on the left and on the right side of the running index.
        @param file_list: The list of files that the file set contains. Maybe be a list of file name strings, or a compiled list of files if files_list_compiled is specified as True.
        @param **kwargs: Keyword arguments:
            - fitting_file_regex: an already compiled regular expression to match fitting files of the set against.
            - file_list_compiled: a boolean stating whether the given file_list is raw or compiled (default: False; file_list will be compiled automatically)
        """        
        self.pattern = pattern
        
        self.fitting_file_regex = kwargs.get('fitting_file_regex', None)
        if self.fitting_file_regex is None:
            left_pattern, right_pattern = pattern
            self.fitting_file_regex = re.compile("{}(\d+){}(?:\.(.+))?$".format(re.escape(left_pattern), re.escape(right_pattern)))
        
        file_list_compiled = kwargs.get('file_list_compiled', False)
        if file_list_compiled:
            self.files = file_list
        else:
            self.files = self._compile_files(file_list)
        
        self.max_index = self._find_max_index()
    
    def __len__(self):
        """Return the amount of files contained in the set."""
        amount_of_files = 0
        for types_list in self.files.values():
            amount_of_files += len(types_list)
        
        return amount_of_files
    
    def __repr__(self):
        """Print the files of the file set in adjacent order."""
        files_list = self.get_files_list()
        left_pattern, right_pattern = self.pattern
        
        return "<{}*{}: {}>".format(left_pattern, right_pattern, files_list)
        
    def __str__(self):
        """Print the pattern of the file set."""
        left_pattern, right_pattern = self.pattern
        return "{}{}{}".format(left_pattern, self.INDEX_INDICATOR, right_pattern)
    
    @classmethod
    def files_detected(cls, pattern):
        """Return a FileSet object, whereas the files are automatically detected within the current working directory based on the given pattern."""
        left_pattern, right_pattern = pattern
        fitting_file_regex = re.compile(r"{}(\d+){}(?:\.(.+))?$".format(re.escape(left_pattern), re.escape(right_pattern)))
        
        compiled_file_list = cls._find_files(fitting_file_regex)
        
        return cls(pattern, compiled_file_list, fitting_file_regex=fitting_file_regex, file_list_compiled=True)
    
    @staticmethod 
    def _find_files(fitting_file_regex):
        """
        Find the files fitting the given fitting_file_regex and return them as a compiled file list.
        
        @param fitting_file_regex: The compiled regular expression to match files against
        
        @return: The compiled file list
        """
        compiled_files = {}
        for entry in scandir(getcwd()):
            if entry.is_file():
                match = fitting_file_regex.match(entry.name)
                if match:
                    ## Compile this file
                    index = int(match.group(1))
                    file_type = match.group(2)
                    if file_type is None:
                        file_type = ''
                    
                    if index in compiled_files.keys():
                        compiled_files[index].append(file_type)
                    else:
                        compiled_files.update({index: [file_type]})
        
        return compiled_files
    
    def _find_max_index(self):
        """
        Find the highest assigned index of the file set.
        
        @return: The highest index in the set. If the FileSet is empty (i.e. has no files), -1 will be returned.
        """
        assigned_indexes = self.files.keys()
        
        try:
            return max(assigned_indexes)
        except ValueError:
            return -1
        
    def _compile_files(self, file_list):
        """
        Compile the given file list into a lightweight, computer-readable form.
        
        @param file_list: The list of files (name.file_type) to be compiled
        
        @return: The compiled file list
        """
        compiled_files = {}
        for file in file_list:
            match = self.fitting_file_regex.match(file)
            index = int(match.group(1))
            file_type = match.group(2)
            if file_type is None:
                file_type = ''
            
            self._add_type_to_files_dict(compiled_files, index, file_type)
        
        return compiled_files
    
    #===========================================================================
    # Low level / Internal Procedures
    #===========================================================================
    @staticmethod
    def _add_type_to_files_dict(files_dict, index, file_type):
        """
        Add a file specified by its index and file type to the given files_dict.
        
        @param files_dict: The dictionary to which to add the file
        @param index: The index of the file
        @param file_type: The file type of the file
        """
        if index in files_dict.keys():
                files_dict[index].append(file_type)
        else:
            files_dict.update({index: [file_type]})
    
    def _add_file_logically(self, index, file_type):
        """
        Add a file specified by its index and file type to the FileSet's files dictionary.
        
        @param files_dict: The dictionary to which to add the file
        @param index: The index of the file
        """
        FileSet._add_type_to_files_dict(self.files, index, file_type)
        if index > self.max_index:
            self.max_index = index
        
    def _remove_file_logically(self, index, file_type):
        """
        Remove a given file specified by its index and file type from the FileSet's files dictionary.
        
        @param index: The index of the file
        @param file_type: The file type of the file
        
        @raise IndexUnassignedError: The given index was never assigned in the first place
        """
        file_types_at_index = self.files.get(index, None)
        if file_types_at_index is None:
            raise FileSet.IndexUnassignedError(self, index, "The index '{}' is not assigned in the file set '{}'.".format(index, str(self)))
        elif len(file_types_at_index) == 1:
            self.files.pop(index) # remove entire index
            if index == self.max_index:
                self.max_index = self._find_max_index()
        else:
            file_types_at_index.remove(file_type) # only remove this type from index file_type list, since there are more types assigned
        
    
    def _get_name(self, index, file_type, pattern=None):
        if pattern is not None:
            left_pattern, right_pattern = pattern
        else:
            left_pattern, right_pattern = self.pattern
        
        if file_type == '':
            return "{}{}{}".format(left_pattern, index, right_pattern)
        else:
            return "{}{}{}.{}".format(left_pattern, index, right_pattern, file_type)
    
    @staticmethod
    def _get_file_type(file_name):
        match = FileSet.type_regex.search(file_name)
        if match is None:
            return '' # file has no extension!
        else:
            return match.group(1) # return extension without .
    
    @staticmethod
    def _order_index_range(index_range):
        """
        Make sure an index_range is ordered from lower to higher.
        
        @return: The ordered index_range
        """ 
        range_left, range_right = index_range
        
        if range_right < range_left: index_range = (range_right, range_left)
        
        return index_range
    
    @staticmethod
    def _check_and_order_spot(spot):
        """
        Make sure a spot consists of adjacent indexes and is ordered from lower to higher.
        
        @raise ValueError: The given spot is invalid (i.e. indexes are not adjacent)
        
        @return: The ordered spot
        """
        left_spot, right_spot = FileSet._order_index_range(spot) # actually, it just orders any 2-tuple's integers from higher to lower
        
        if left_spot < -1:
            raise ValueError(spot, left_spot, "The value {} for the left side of the spot {} is too low.".format(left_spot, spot))
        if right_spot-left_spot != 1:
            raise ValueError(spot, "The 'spot' {} does not actually define a spot in between two adjacent indexes.".format(spot))
        
        return (left_spot, right_spot)
    
    def change_index(self, old_index, new_index, file_type=None):
        """
        Change the index of a file within the FileSet.
        
        The max_index of the FileSet is automatically updated if necessary.
        If the index is multi-assigned, all the files are moved accordingly.
        
        @param old_index: The current index of the file(s)
        @param new_index: The target index of the file(s)
        @param file_type: A string stating the specific file_type that should be moved to the new index, as opposed to all file_types under the old_index (e.g. 'png')
        
        @raise IndexUnassignedError: The given old_index is not assigned at all
        @raise IndexAssignedError: The given new_index is already assigned
        """
        if old_index == new_index: return # don't do anything when the index shouldn't actually be changed
        
        fitting_files_types = self.files.pop(old_index, None)
        
        if fitting_files_types is None: 
            raise FileSet.IndexUnassignedError(old_index, "The index {} has not been assigned within the FileSet".format(old_index))
        if new_index in self.files.keys():
            self.files.update({old_index: fitting_files_types})
            raise FileSet.IndexAssignedError(new_index, old_index, "The index {} is already assigned. Can't move file with index {} to it.".format(new_index, old_index))
        
        ## Preparation in case a specific file_type was specified
        if not file_type is None:
            try:
                fitting_files_types.remove(file_type)
            except ValueError:
                raise FileSet.TypeUnassignedError(old_index, file_type, "The file type {} is not assigned at the index {}.".format(file_type, old_index))
            
            ## Readd the leftover fitting_files_types, because they won't be moved in this case
            self.files.update({old_index: fitting_files_types})
            
            ## Override them now so only this type will be changed
            fitting_files_types = [file_type]
        
        for file_type in fitting_files_types:
            old_name = self._get_name(old_index, file_type)
            new_name = self._get_name(new_index, file_type)
            
            rename(old_name, new_name)
        
        self.files.update({new_index: fitting_files_types})
        if new_index > self.max_index: 
            self.max_index = new_index
        elif old_index == self.max_index:
            self.max_index = self._find_max_index()

    
    def move_range(self, index_range, new_start_pos):
        """
        Move a range of files by their index to a given position.
        
        The whole range is moved to the new position, therefore assuming there is enough space in the gap it is being moved into.
        If the operation does make the range collide with existing files, an exception is raised.
        The range will not collide with existing files if it contains a gap that ends up allowing the existing files to have their space.
        
        @param index_range: The index range to be moved
        @param new_start_pos: The index that the first file of the range is going to have after the operation. 
        
        @raise FileCollisionError: The range turns out to collide with another file 
        """
        left_bound, right_bound = self._order_index_range(index_range)
        amount = new_start_pos - left_bound
        
        change_log = []
        try:
            ## Check movement direction to avoid internal collisions
            if amount > 0: 
                ## UP: move files from left to right
                for i in range(right_bound, left_bound-1, -1):
                    f = i
                    t = i + amount
                    try:
                        self.change_index(f, t)
                        change_log.append((f, t))
                    except FileSet.IndexUnassignedError:
                        pass
            elif amount < 0:
                ## DOWN: move files from right to left
                for i in range(left_bound, right_bound+1, 1):
                    f = i
                    t = i + amount
                    try:
                        self.change_index(f, t)
                        change_log.append((f, t))
                    except FileSet.IndexUnassignedError:
                        pass
        except FileSet.IndexAssignedError as e:
            ## Moved range collides with a file! Undo operations..
            for action in reversed(change_log):
                t, f = action
                self.change_index(f, t)
            
            from_idx = e.args[0]
            to_idx = e.args[1]
            raise FileSet.FileCollisionError(from_idx, to_idx, "The range can not be moved: the file with the index {} can not be moved since the index {} already exists.".format(from_idx, to_idx))
    
    #===========================================================================
    # High level / API Procedures
    #===========================================================================
    def change_pattern(self, new_pattern):
        """
        Rename all of the files contained in the file set using the given new pattern, effectively changing the pattern of the set.
        
        @param new_pattern: The new pattern to be used
        """
        for index in self.files.keys():
            for file_type in self.files[index]:
                old_name = self._get_name(index, file_type)
                new_name = self._get_name(index, file_type, new_pattern)
                
                rename(old_name, new_name) # change name physically
        
        # update pattern after successful rename
        self.pattern = new_pattern
    
    def update(self):
        """Re-read the files in the directory and update the files list. This is useful e.g. when another software has physically added or deleted files to/from the file set."""
        self.files = self._find_files(self.fitting_file_regex)
         
    def file_in_set(self, file_name):
        """
        Check whether a file name is currently in this file set.
        
        @return: 2-tuple containing:
            - a boolean stating whether the file currently is in this set (this may be False even if the file fits the set!)
            - the index of the file (None if the file doesn't match the file set's pattern)
        """
        file_match = self.fitting_file_regex.match(file_name)
        if file_match:
            index = int(file_match.group(1))
            file_type = file_match.group(2)
            if index in self.files and file_type in self.files[index]:
                return (True, index)
            else:
                return (False, index)
        else:
            return (False, None)
    
    def get_files_list(self):
        """Return the list of file names the set currently contains in adjacent order (multi-assigned indexes are ordered alphabetically)."""
        indexes_list = list(self.files.keys())
        indexes_list.sort()
        
        files_list = []
        for index in indexes_list:
            file_types = self.files[index]
            file_types.sort()
            for file_type in file_types:
                file_name = self._get_name(index, file_type)
                files_list.append(file_name)
        
        return files_list
    
    def add_file(self, new_file, spot):
        """
        Add a file to the FileSet at the specified index. If the file belongs to another file set, that set will NOT be updated automatically.
        
        @param new_file: The path to the new file; may be relative or absolute.
        @param spot: The spot at which the file should be added
        
        @raise FileNotFoundError: The given file name does not exist or is not a file
        """
        if not isfile(new_file): raise FileNotFoundError(new_file, "The file '{}' does not exist or is not a file.".format(new_file))
        
        _, insert_index = self._check_and_order_spot(spot)
        
        if (insert_index <= self.max_index) and (insert_index in self.files.keys()):
            self.move_range((insert_index, self.max_index), insert_index+1)
        elif insert_index > self.max_index:
            self.max_index = insert_index
        
        file_type = self._get_file_type(new_file)
        
        new_name = self._get_name(insert_index, file_type)
        rename(new_file, new_name) # physically add file
        
        self.files.update({insert_index: [file_type]}) # logically add file 
    
    def add_files(self, file_names, spot, ignore_unfound_files=False): # TODO: add tests for this
        """
        Add a list of files to the FileSet given their names. This is the preferred method for adding multiple files that don't belong to a set just yet.
          
        The files are added in the order they are given in the file_names list.
        WARNING: If one of the given files does already belong to a file set, this set will NOT automatically be updated. For this, you should use add_file_set instead.
          
        @param file_names: The list of file names to add to the FileSet object
        @param spot: The spot at which the added sequence of files is going to start
        @param ignore_unfound_files: If set to True, file names that aren't found simply won't be added to the set. Otherwise, an error is raised when a file isn't found. (default: False)
        
        @raise ValueError: The given spot is invalid
        @raise FileNotFoundError: One or more of the given file_names do not exist and ignore_unfound_files is set to False
        """
        ## Do nothing if no files are given
        if len(file_names) == 0:
            return
        
        ## Check whether files exist; raise error or remove them if applicable
        files_to_add = []
        for file in file_names:
            if isfile(file):
                files_to_add.append(file)
            elif ignore_unfound_files:
                pass
            else:
                raise FileSet.FileNotFoundError()
          
        _, new_pos = self._check_and_order_spot(spot)
         
        if new_pos <= self.max_index:
            ## Make space for addition into file set
            self.move_range((new_pos, self.max_index), new_pos + len(files_to_add))
        else:
            ## Files are appended. Manually update max_index
            self.max_index = new_pos + len(file_names)-1
         
        ## Add physically and logically
        for i, file in enumerate(files_to_add):
            file_type = self._get_file_type(file)
            index = new_pos + i
            new_name = self._get_name(index, file_type)
             
            rename(file, new_name) # add physically
            self._add_file_logically(index, file_type) # add logically
            
    
    def add_file_set(self, foreign_file_set, spot, add_indexes='ALL', **kwargs):
        """
        Add a set of files to the FileSet. This is the preferred method for adding multiple files at once.
        
        The files of the foreign FileSet are added into this FileSet in the same order as their add_indexes dictate.
        
        If the area to the right of the spot is a gap, that gap will be filled as much as possible.
        In case not all files fit into this gap, additional space will be made.
        
        If there are multiple files with the same index in the foreign_file_set, they will also have the same index in this FileSet.
        Therefore, the right order of files is guaranteed.
        
        If an iterable for add_indexes is given, only they will be added to the set while being removed from the foreign_file_set.
        This may cause the foreign_file_set to become incoherent as gaps are not automatically closed after this operation. 
                
        @param foreign_file_set: The FileSet object which's files are to be added to this FileSet
        @param spot: The spot at which the added sequence of files is going to start
        @param add_indexes: An iterable of indexes of the foreign_file_set which shall be added. The order of them is being followed. (Default: 'ALL', the whole FileSet will be added)
        Keyword arguments:
        @param strip_gaps: If set to True, all gaps within the given iterable will be removed during the operation, leaving only the existing files to be added; as opposed to raising an error when encountering them.
        @param preserve_gaps: If set to True, all gaps within the given iterable will be preserved by the operation; as opposed to raising an error when encountering them.
        
        @raise IndexUnassignedError: The given iterable of indexes points to gaps and no gap-handling option has been chosen
        @raise TypeError: The iterable given for add_indexes does not just contain valid integers
        @raise ConflictingOptionsError: Both strip_gaps and preserve_gaps are set to True.
        
        @return: The count of indexes that were actually added. (if preserve_gaps is chosen, gaps will be included in this count)
        """
        # TODO: allow list of file/path names
        if add_indexes == 'ALL': 
            add_indexes = [*foreign_file_set.files.keys()]
        else:
            ## Check index input for validity
            given_add_indexes = list(add_indexes) # necessary since generators don't support item deletion
            add_indexes = []
            
            for i, index in enumerate(given_add_indexes):
                ## Check whether index is actually a valid integer
                if not type(index) is int: raise TypeError(index, "'{}' is not a valid index.".format(index))
                
                ## Check whether index is actually in foreign_file_set. If not: if strict raise error, else just remove index from list
                if not index in foreign_file_set.files:
                    strip_gaps = kwargs.get('strip_gaps', False)
                    preserve_gaps = kwargs.get('preserve_gaps', False)
                    
                    if strip_gaps and preserve_gaps:
                        raise FileSet.ConflictingOptionsError("Both strip_gaps and preserve_gaps were set to True, even though you have to decide for one.")
                    
                    if strip_gaps: 
                        pass # skip this index altogether
                    elif preserve_gaps:
                        add_indexes.append(index) # add index to index list nevertheless. It will be recognized as a gap and skipped later on    
                    else: 
                        foreign_left_pattern, foreign_right_pattern = foreign_file_set.pattern
                        raise FileSet.IndexUnassignedError(index, foreign_file_set, "The index {} is unassigned in the foreign FileSet {}{}{} and thus can't be added to this FileSet.".format(index, foreign_left_pattern, FileSet.INDEX_INDICATOR, foreign_right_pattern))
                else:
                    ## Index exists. Add to add_indexes list so it will be added later on
                    add_indexes.append(index)
        
        ## Find minimum index that is assigned in this insert domain. Required to check whether/where to move range to make space
        _, new_pos = self._check_and_order_spot(spot)
        
        insert_domain_left = new_pos
        insert_domain_right = new_pos+len(add_indexes)-1
        
        min_assigned_index_in_insert_domain = None
        for index in self.files:
            if insert_domain_left <= index <= insert_domain_right:
                if min_assigned_index_in_insert_domain is None or index < min_assigned_index_in_insert_domain: 
                    min_assigned_index_in_insert_domain = index
        
        ## Move range if necessary
        if not min_assigned_index_in_insert_domain is None:
            self.move_range((min_assigned_index_in_insert_domain, self.max_index), insert_domain_right+1)
        elif insert_domain_right > self.max_index:
            # If move range isn't called to do the job, update index in case that will be necessary
            self.max_index = insert_domain_right
        
        ## Finally add the files
        foreign_left_pattern, foreign_right_pattern = foreign_file_set.pattern
        added_index_count = 0
        for i, old_index in enumerate(add_indexes):
            new_index = new_pos+i
            file_types = foreign_file_set.files.get(old_index)
            if file_types is None:
                added_index_count += 1
                pass
            else:
                for file_type in file_types[:]: # shallow copy to avoid issues with logical removal within loop
                    old_name = "{}{}{}.{}".format(foreign_left_pattern, old_index, foreign_right_pattern, file_type)
                    new_name = self._get_name(new_index, file_type)
                    
                    rename(old_name, new_name)
                    
                    self._add_file_logically(new_index, file_type)
                    foreign_file_set._remove_file_logically(old_index, file_type)
                added_index_count += 1
        
        return added_index_count
    
    def remove_file(self, index, removed_file_set=None):
        """
        Remove the file with the given index from the FileSet.
        
        If the given index is multi-assigned, both of the files will be removed, though they will be assigned an index each.
        The resulting gap is automatically closed.
        The right order of files is not guaranteed for multi-assigned indexes.
        
        @param index: The index of the file
        @param removed_file_set: An optional FileSet object to append the removed file to (default: None)
        
        @raise IndexUnassignedError: The given index does not exist within the FileSet
        
        @return: A FileSet object containing the removed files (pattern: removed\i); if a removed_file_set is specified, this FileSet will be returned
        """
        DEFAULT_REMOVE_PATTERN = ('removed', '')
        
        if not index in self.files: raise FileSet.IndexUnassignedError(index, "The index {} does not exist within this FileSet".format(index))
        
        if removed_file_set is None: removed_file_set = FileSet.files_detected(DEFAULT_REMOVE_PATTERN)
        
        file_types = self.files[index]
        for i, file_type in enumerate(file_types):
            file_name = self._get_name(index, file_type)
            
            removed_file_set.add_file(file_name, removed_file_set.max_index + i + 1)
            
        del self.files[index]
        
        if index < self.max_index:
            self.move_range((index+1, self.max_index), index)
        else:
            self.max_index -= 1
            
        return removed_file_set
        
    def remove_files(self, index_iterable, removed_file_set=None, **kwargs):
        """
        Remove files within a given index range from the FileSet. This is the preferred method for removing multiple files at once.
        
        The right order of files might not be preserved for multi-assigned indexes.
        
        @param index_iterable: An iterable of indexes which shall be removed from the set.
        @param removed_file_set: An optional FileSet object to append the removed files to (default: None)
        Keyword Arguments:
        @param strip_gaps: If set to True, all gaps within the given iterable will be removed during the operation, leaving only the existing files to be removed; as opposed to raising an error when encountering them.
        @param preserve_gaps: If set to True, all gaps within the given iterable will be preserved by the operation and thus added to the to remove INTO; as opposed to raising an error when encountering them. (not to be confused with keep_gaps_in_set!)
        @param keep_gaps_in_set: If set to True, gaps within the file set that is removed FROM will not be fixed. (not to be confused with preserve_gaps!) (default: False)
        
        @raise IndexUnassignedError: The given index iterable contains gaps and no gap-handling option has been chosen
        @raise TypeError: The given index iterable does not only contain valid integers
        @raise ConflictingOptionsError: Both strip_gaps and preserve_gaps are set to True
        
        @return: A 2-tuple consisting of the following:
            - A FileSet object containing the removed files; if a removed_file_set was specified, this FileSet is returned with the files appended
            - The count of indexes that were actually removed from the FileSet (if preserve_gaps is chosen, gaps will be included in this count)
        """
        DEFAULT_REMOVE_PATTERN = ('removed', '')
                    
        if removed_file_set is None:
            removed_file_set = FileSet.files_detected(DEFAULT_REMOVE_PATTERN)
        
        try:
            removed_index_count = removed_file_set.add_file_set(self, (removed_file_set.max_index, removed_file_set.max_index+1), index_iterable, strip_gaps=kwargs.get('strip_gaps', False), preserve_gaps=kwargs.get('preserve_gaps', False))
        except FileSet.IndexUnassignedError as e:
            ## Add files won't change anything if it runs into this error, thus things are safe
            raise FileSet.IndexUnassignedError(e.args[0], "The file with the index {} does not exist and thus can't be removed.".format(e.args[0]))
        
        ## Files could have been removed from virtually anywhere. This file set might have become a swiss cheese. Fix all gaps now.
        if not kwargs.get('keep_gaps_in_set', False):
            still_existing_indexes = list(self.files.keys())
            still_existing_indexes.sort()
            for i in range(len(still_existing_indexes)):
                current_existing_index = still_existing_indexes[i]
                self.change_index(current_existing_index, i)
            
        return removed_file_set, removed_index_count
    
    def move_file(self, current_index, spot, allow_gap=False):
        """
        Move a file to a new position.
        
        For a multi-assigned index, all files will be moved accordingly.
        
        @param current_index: The current index of the file
        @param spot: A tuple of two adjacent indexes to move the file in between
        @param allow_gap: If set to True, allow movement of a gap instead of a file. Else, raise an IndexUnassignedError upon encountering a gap. (Default: False)
        
        @raise IndexUnassignedError: The given current_index is not assigned and mode strict is used
        """
        if type(current_index) is int:
            self.move_files((current_index, current_index), spot, preserve_gaps=allow_gap)
        else:
            raise TypeError(current_index, "The index '{}' is not an integer.".format(current_index))
    
    def move_files(self, index_range, spot, **kwargs):
        """
        Move a range of files to a new position.
        
        For multi-assigned indexes, all files will be moved accordingly.
        To choose the spot at the very beginning of the set, simply use (-1, 0).
        If an index of the spot is actually covered by the range, no files will be moved, since that means that they are already in place. (e.g: range=(2, 4), spot=(3, 4))
        
        @param index_range: The inclusive range of indexes which shall be moved to the new position
        @param spot: A tuple of two adjacent indexes to move the files in between
        Keyword Arguments:
        @param strip_gaps: If set to True, all gaps within the given index range will be removed during the operation, leaving only the existing files to be moved; as opposed to raising an error when encountering them.
        @param preserve_gaps: If set to True, all gaps within the given index range will be preserved by the operation; as opposed to raising an error when encountering them.
        
        @raise ValueError: A supplied indexes is negative (or below -1) or the given spot is invalid
        @raise IndexUnassignedError: The supplied index_range contains gaps and no gap-handling option has been chosen
        @raise ConflictingOptionsError: Both strip_gaps and preserve_gaps are set to True
        """
        left_range, right_range = self._order_index_range(index_range)
        left_spot, right_spot = self._check_and_order_spot(spot)
        
        for i in [left_range, right_range, right_spot]:
            if i < 0: raise ValueError(i, "The index {} is negative, but this may only be possible for the left_spot.")
        
        if left_spot in range(left_range, right_range+1) or right_spot in range(left_range, right_range+1):
            ## If the left or the right spot are part of the given range, that means it already is in the right position 
            ## and no movement operation is necessary. Thus terminate this method.
            return 
        
        tmp_set = FileSet.files_detected(('tmp', ''))
        
        indexes_to_move = range(left_range, right_range+1)
        tmp_insert_pos = tmp_set.max_index+1
        removed_indexes_count = tmp_set.add_file_set(self, (tmp_insert_pos-1, tmp_insert_pos), indexes_to_move, strip_gaps=kwargs.get('strip_gaps', False), preserve_gaps=kwargs.get('preserve_gaps', False))
        
        if right_range < left_spot:
            ## MOVE UP
            range_to_move = (right_range+1, left_spot)
            to_position = left_range
            self.move_range(range_to_move, to_position)
            
            readd_position = left_range + (left_spot - right_range) # add directly after range we just moved down to make space
            self.add_file_set(tmp_set, (readd_position-1, readd_position), range(tmp_insert_pos, tmp_insert_pos+removed_indexes_count), preserve_gaps=True)
            
            ## Close resulting gap in case there were gaps in index_range; but only if NOT moving to the END of the set!
            if right_spot <= self.max_index:
                range_to_move = (right_spot, self.max_index)
                to_position = readd_position + removed_indexes_count
                self.move_range(range_to_move, to_position)
            
        elif left_range > right_spot:
            ## MOVE DOWN
            range_to_move = (right_spot, left_range-1)
            to_position = left_spot + removed_indexes_count + 1 # make resulting gap exactly fitting for re-add files
            self.move_range(range_to_move, to_position)
            
            readd_position = left_spot + 1 # add directly after left_spot
            self.add_file_set(tmp_set, (readd_position-1, readd_position), range(tmp_insert_pos, tmp_insert_pos+removed_indexes_count), preserve_gaps=True)
            
            ## Close resulting gap in case there were gaps in index_range; but only if NOT moving from the END of the set
            if right_range < self.max_index:
                range_to_move = (right_range + 1, self.max_index)
                to_position = to_position + (left_range-1 - right_spot + 1)
                self.move_range(range_to_move, to_position)
            
            
    def switch_files(self, index1, index2, allow_gaps=False):
        """
        Switch the position of two files.
        
        @param index1: The current index of the first file
        @param index2: The current index of the second file 
        @param allow_gaps: If set to True, allow switching files AND gaps. Else, raise an IndexUnassignedError upon encountering a gap. (Default: False)
        """
        if type(index1) is not int:
            raise TypeError(index1, "The index '{}' is not an integer.".format(index1))
        elif type(index2) is not int:
            raise TypeError(index2, "The index '{}' is not an integer.".format(index2))
        
        self.switch_file_ranges((index1, index1), (index2, index2), preserve_gaps=allow_gaps)
    
    def switch_file_ranges(self, index_range1, index_range2, **kwargs):
        """
        Switch the positions of two file ranges. They do not have to be equal in size.
        
        @param index_range1: The index range of the first sequence of files
        @param index_range2: The index range of the second sequence of files
        Keyword Arguments:
        @param strip_gaps: If set to True, all gaps within the given index ranges will be removed during the operation, leaving only the existing files to be switched; as opposed to raising an error when encountering them.
        @param preserve_gaps: If set to True, all gaps within the given index ranges will be preserved by the operation; as opposed to raising an error when encountering them.
        
        @raise ConflictingOptionsError: Both strip_gaps and preserve_gaps are set to True
        @raise OverlappingRangesError: The given index ranges are overlapping each other 
        @raise IndexUnassignedError: The given index ranges contain gaps and no gap-handling option is chosen
        """
        strip_gaps = kwargs.get('strip_gaps', False)
        preserve_gaps = kwargs.get('preserve_gaps', False)
        original_max_index = self.max_index
        
        left_range1, right_range1 = self._order_index_range(index_range1)
        left_range2, right_range2 = self._order_index_range(index_range2)
        
        ## If the two ranges overlap, raise an error
        if (left_range1 <= left_range2 <= right_range1) or (left_range2 <= right_range1 <= right_range2):
            raise FileSet.OverlappingRangesError(index_range1, index_range2, "The ranges '{}' and '{}' are overlapping each other and thus can't be switched.".format(index_range1, index_range2))
        
        range1 = (left_range1, right_range1)
        range2 = (left_range2, right_range2)
        
        ## Acquire information about the given ranges (which one is on the left, which one is greater)
        if left_range1 < left_range2:
            leftmost_range = range1
            rightmost_range = range2
            in_between_range = (right_range1+1, left_range2-1)
        else:
            leftmost_range = range2
            rightmost_range = range1
            in_between_range = (right_range2+1, left_range1-1)
        
        left_in_between_range, right_in_between_range = in_between_range
        in_between_range_width = right_in_between_range - left_in_between_range + 1
        if left_in_between_range > right_in_between_range:
            ## Invalid; this means there isn't actually any more indexes between the two given ranges
            in_between_range = None
        
        if (right_range1 - left_range1) > (right_range2 - left_range2):
            greater_range = range1
            smaller_range = range2
        else:
            greater_range = range2
            smaller_range = range1
        
        ## Perform action
        tmp_set = FileSet.files_detected(('tmp', ''))
        
        shift_files_range = range(greater_range[0], greater_range[1]+1)
        
        tmp_set, amount_shifted = self.remove_files(shift_files_range, tmp_set, strip_gaps=strip_gaps, preserve_gaps=preserve_gaps, keep_gaps_in_set=True)
        shifted_files_indexes_in_tmp_set = range(tmp_set.max_index-amount_shifted+1, tmp_set.max_index+1)
        
        if greater_range is leftmost_range:
            move_other_range_spot = (leftmost_range[0]-1, leftmost_range[0])
            range_to_move = range(smaller_range[0], smaller_range[1]+1)
            ## Actually, the files are only moved by the usage of this operation. 
            #  Using add_file_set is required instead of move_range in order to
            #  ensure that possibly occurring gaps are correctly dealt with.
            ## This "hack" of self-addition only works because there is free space
            #  at the re-addition spot. Therefore, a call of move_range
            #  to make space is not required and add-indexes aren't unknowingly changed.
            moved_files_amount = self.add_file_set(self, move_other_range_spot, range_to_move, strip_gaps=strip_gaps, preserve_gaps=preserve_gaps)
            
            next_unassigned_index = leftmost_range[0] + moved_files_amount
            
            if in_between_range is not None:
                self.move_range(in_between_range, next_unassigned_index)
                next_unassigned_index += in_between_range_width
            
            readd_spot = (next_unassigned_index-1, next_unassigned_index)
            amount_readded = self.add_file_set(tmp_set, readd_spot, shifted_files_indexes_in_tmp_set)
            
            ## Fix possible gap caused by possible gap stripping and/or update max_index
            next_index = next_unassigned_index + amount_readded
            if rightmost_range[1] >= original_max_index:
                self.max_index = next_index - 1
            elif next_index < rightmost_range[1]+1:
                range_to_move = (rightmost_range[1]+1, self.max_index)
                self.move_range(range_to_move, next_index)
        
        elif greater_range is rightmost_range:
            smaller_range_width = smaller_range[1] - smaller_range[0] + 1
            if not (amount_shifted < smaller_range_width) or in_between_range is None:
                if in_between_range is not None:
                    to_position = leftmost_range[0] + amount_shifted # + amount of files which will actually be readded later on
                    self.move_range(in_between_range, to_position)
                    next_unassigned_index = to_position + in_between_range_width
                else:
                    next_unassigned_index = leftmost_range[0] + amount_shifted
                
                move_other_range_spot = (next_unassigned_index-1, next_unassigned_index)
                range_to_move = range(smaller_range[0], smaller_range[1]+1)
                ## Actually, the files are only moved by the usage of this operation. 
                #  Using add_file_set is required instead of move_range in order to
                #  ensure that possibly occurring gaps are correctly dealt with.
                ## This "hack" of self-addition only works because there is free space
                #  at the re-addition spot. Therefore, a call of move_range
                #  to make space is not required and add-indexes aren't unknowingly changed.
                moved_files_amount = self.add_file_set(self, move_other_range_spot, range_to_move, strip_gaps=strip_gaps, preserve_gaps=preserve_gaps)
                
                readd_spot = (leftmost_range[0]-1, leftmost_range[0])
                self.add_file_set(tmp_set, readd_spot, shifted_files_indexes_in_tmp_set)
            else:
                ## Special case. Actual temporarily removed bigger range is smaller than width of supposedly smaller range. (This may occur because of strip_gaps)
                ## If there is an in_between_range, not handling this special case will lead to a range collision. Otherwise, the normal part of the algorithm will work.
                range_to_shift = range(smaller_range[0], smaller_range[1]+1)
                tmp_set, amount_shifted_smaller = self.remove_files(range_to_shift, tmp_set, strip_gaps=strip_gaps, preserve_gaps=preserve_gaps, keep_gaps_in_set=True)
                shifted_files_smaller_indexes_in_tmp_set = range(tmp_set.max_index-amount_shifted_smaller+1, tmp_set.max_index+1)
                
                ## Shift in between range
                to_position = leftmost_range[0] + amount_shifted # + amount of files from expectedly greater range that will be readded later on
                self.move_range(in_between_range, to_position)
                next_unassigned_index = to_position + in_between_range_width
                
                ## Readd both ranges
                readd_spot = (leftmost_range[0]-1, leftmost_range[0])
                self.add_file_set(tmp_set, readd_spot, shifted_files_indexes_in_tmp_set) # greater range
                readd_spot = (next_unassigned_index-1, next_unassigned_index)
                moved_files_amount = self.add_file_set(tmp_set, readd_spot, shifted_files_smaller_indexes_in_tmp_set) # smaller range
            
            ## Fix possible gap caused by possible gap stripping and/or update max_index
            next_index = next_unassigned_index + moved_files_amount
            if rightmost_range[1] >= original_max_index:
                self.max_index = next_index - 1
            elif next_index < rightmost_range[1]+1:
                range_to_move = (rightmost_range[1]+1, self.max_index)
                self.move_range(range_to_move, next_index)
        
    def find_flaws(self):
        """
        Scan the FileSet for gaps and multi_assigned indexes and return a tuple listing both of them in distinct lists.
        
        @raise TooManyFilesError: The max_index of the file set is greater than 1000.
        
        @return: A 2-tuple containing the list of gap ranges and the list of multi_assigned_index 2-tuples, which in turn contain the index and the file types.
        """
        if (self.max_index > 1000):
            raise FileSet.TooManyFilesError(self, "The file set has a maximum index of {}. It would take too long to scan it for flaws.".format(self.max_index))
        
        gap_list = []
        multi_assigned_list = []
        in_gap = False
        for i in range(0, self.max_index+1): # scan all indexes in the set
            file_types = self.files.get(i)
            
            ## Gaps
            if file_types is None:
                if not in_gap:
                    gap_left_bound = i
                    in_gap = True
            else:
                if in_gap:
                    gap_right_bound = i-1
                    gap_list.append((gap_left_bound, gap_right_bound))
                    in_gap = False
            
                ## Multi-assigned indexes
                if len(file_types) > 1: multi_assigned_list.append((i, file_types))
            
        return (gap_list, multi_assigned_list)        
        
    def fix(self, fix_multi_idx=False):
        """
        Close gaps and optionally resolve multi-assigned indexes.
        
        Gaps within the FileSet (not assigned indexes) are closed automatically.
        If preserve_multi_idx is True, multi-assigned indexes are resolved automatically and a change log regarding them will be returned.
        If the file set contains more than 1000 files, it will still be attempted to close possible gaps. This may take very long if there really are many files in the set.
        
        @raise TooManyFilesError: The file set contains more than 1000 files and fix_multi_idx is set to True.
        
        @param fix_multi_idx: If False, the FileSet will only fix its gaps. If this is set to True, multi-assigned indexes will be resolved by alphabetical order (Default: False)
        """
        try:
            gap_list, multi_assigned_list = self.find_flaws()
            flaw_detection_failed = False
        except FileSet.TooManyFilesError:
            flaw_detection_failed = True
            gap_list = True
            multi_assigned_list = []
        
        ## Close all gaps
        if gap_list:
            existing_indexes = list(self.files.keys())
            existing_indexes.sort()
            for i in range(len(existing_indexes)):
                current_existing_index = existing_indexes[i]
                self.change_index(current_existing_index, i)
                
                ## Update if it's a multi_assigned index for later use
                for j in range(len(multi_assigned_list)):
                    multi_idx, types = multi_assigned_list[j]
                    if current_existing_index == multi_idx:
                        multi_assigned_list[j] = (i, types)
        
        ## Automatically fix multi-assigned indexes if specified
        if fix_multi_idx:
            
            if flaw_detection_failed:
                if self.max_index > 1000:
                    raise FileSet.TooManyFilesError(self, "Automatically fixing multi-assigned indexes is not supported for file sets with more than 1000 files. This set contains {} files.".format(self.max_index))
                else:
                    _, multi_assigned_list = self.find_flaws()
            
            for index, file_types in reversed(multi_assigned_list): # reversed, so multi-assigned indexes don't change (iterate greater to lower)
                ## Make space for the index expansion
                if index != self.max_index:
                    extra_required_space = len(file_types) - 1
                    range_to_move = (index+1, self.max_index)
                    to_position = index+1 + extra_required_space
                    self.move_range(range_to_move, to_position)
                
                ## Move the files to their new indexes based on type
                file_types.sort()
                file_types = file_types[:] # copy the list to prevent changes during runtime when indexes are changed
                for i, file_type in enumerate(file_types):
                    new_index = index + i
                    
                    self.change_index(index, new_index, file_type)
            
    
    def __add__(self, other):
        """
        Add the file or files to this FileSet.
        
        If other is a string, it is seen as a file/path to a file and is attempted to be appended.
        If other is a FileSet object, all of its files are appended to this FileSet.
        
        @param other: Either a string representing a file path, or a FileSet object
        
        @raise FileNotFoundError: A string that does not represent an existing valid file is given
        
        @return: self as the updated FileSet with the new file(s) added
        """
        # TODO: add add
    
    