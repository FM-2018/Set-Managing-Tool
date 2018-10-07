'''
Created on 27.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_many_msg, mock_assert_msg


mock_find_flaws_call_count = 0 # required for test_set_enormous_max_index_auto_fix_multi_indexes

class EnormousDict(dict):
    """A dummy class for a dictionary with more than 1000 files."""
    def __init__(self):
        pass
    
    def __len__(self):
        return 1234

mock_find_flaws = mock.MagicMock(name='find_flaws')
mock_change_index = mock.MagicMock(name='change_index')
mock_move_range = mock.MagicMock(name='move_range') 

@mock.patch('FileSet.FileSet.find_flaws', new=mock_find_flaws)
@mock.patch('FileSet.FileSet.change_index', new=mock_change_index)
@mock.patch('FileSet.FileSet.move_range', new=mock_move_range)
class FixTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_find_flaws.reset_mock()
        mock_change_index.reset_mock()
        mock_move_range.reset_mock()
        
        mock_find_flaws.side_effect = None
        mock_change_index.side_effect = None
        
    def test_flawless_file_set(self):
        """The FileSet should do nothing to a flawless set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                []
            )
        
        test_set.fix()
        
        mock_assert_msg(mock_find_flaws.assert_called_once, [], "The FileSet doesn't even try to find any flaws.")
        mock_assert_msg(mock_change_index.assert_not_called, [], "The FileSet tries to change indexes even though no operation is necessary.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to move ranges even though there is no reason to make any space.")
        
    def test_gap_in_middle(self):
        """The FileSet should be able to fix a single gap in the middle of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [(3, 4)],
                []
            )
        
        test_set.fix()
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [1, 1]),
                (mock_change_index.assert_any_call, [2, 2]),
                (mock_change_index.assert_any_call, [5, 3]),
                (mock_change_index.assert_any_call, [6, 4]),
                (mock_change_index.assert_any_call, [7, 5]),
                (mock_change_index.assert_any_call, [8, 6])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move the files correctly to close a gap in the middle.")
        self.assertEqual(mock_change_index.call_count, 7, "The FileSet tries to deal with multi-assigned indexes, even though that's not explicitly wished for.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to move ranges even though there is no reason to make any space.")
        
    def test_gap_at_front(self):
        """The FileSet should be able to gix a single gap at the front."""
        test_files = ['test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [(0, 1)],
                []
            )
        
        test_set.fix()
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [2, 0]),
                (mock_change_index.assert_any_call, [3, 1]),
                (mock_change_index.assert_any_call, [4, 2]),
                (mock_change_index.assert_any_call, [5, 3]),
                (mock_change_index.assert_any_call, [6, 4]),
                (mock_change_index.assert_any_call, [7, 5]),
                (mock_change_index.assert_any_call, [8, 6])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move the files correctly to close a gap at the front.")
        self.assertEqual(mock_change_index.call_count, 7, "The FileSet tries to deal with multi-assigned indexes, even though that's not explicitly wished for.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to move ranges even though there is no reason to make any space.")
        
    def test_gap_before_last_file(self):
        """The FileSet should be able to fix a single gap before the last file of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [(5, 7)],
                []
            )
        
        test_set.fix()
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [1, 1]),
                (mock_change_index.assert_any_call, [2, 2]),
                (mock_change_index.assert_any_call, [3, 3]),
                (mock_change_index.assert_any_call, [4, 4]),
                (mock_change_index.assert_any_call, [8, 5])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move the files correctly to close a gap in front of the last file.")
        self.assertEqual(mock_change_index.call_count, 6, "The FileSet tries to deal with multi-assigned indexes, even though that's not explicitly wished for.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to move ranges even though there is no reason to make any space.")
        
    def test_files_with_various_gaps(self):
        """The FileSet should be able to fix multiple gaps at once."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (5).jpg', 'test (6).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [(1, 1), (3, 4), (7, 7)],
                []
            )
        
        test_set.fix()
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [2, 1]),
                (mock_change_index.assert_any_call, [5, 2]),
                (mock_change_index.assert_any_call, [6, 3]),
                (mock_change_index.assert_any_call, [8, 4])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move the files correctly to close multiple gaps.")
        self.assertEqual(mock_change_index.call_count, 5, "The FileSet tries to deal with multi-assigned indexes, even though that's not explicitly wished for.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to move ranges even though there is no reason to make any space.")
        
    def test_multi_assigned_indexes_mode_preserve(self):
        """The FileSet should do nothing to multi-assigned indexes if it isn't explicitly told to (i.e. if fix_multi_idx isn't set to True)"""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (3).png', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                [(3, ['jpg', 'png'])]
            )
        
        test_set.fix()
        
        mock_assert_msg(mock_change_index.assert_not_called, [], "The FileSet tries to change indexes, even though there are no gaps and it isn't explicitly told to fix multi-assigned indexes.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to make space to fix the multi-assigned index even though it shouldn't even try to fix it.")
        
    def test_multi_assigned_indexes_mode_fix(self):
        """The FileSet should be able to fix a multi-assigned index in its middle if fix_multi_idx is set to True."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (3).png', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                [(3, ['jpg', 'png'])]
            )
        
        test_set.fix(True)
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(4, 5), 5], "The FileSet fails to correctly make space for the multi-assigned index to expand.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [3, 3, 'jpg']),
                (mock_change_index.assert_any_call, [3, 4, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the multi-assigned index.")
        self.assertEqual(mock_change_index.call_count, 2, "The FileSet tries to change even more indexes than the multi-assigned one.")
        
    def test_multi_assigned_index_at_end_fix(self):
        """The FileSet should be able to fix a multi_assigned index at the end of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (5).png']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                [(5, ['jpg', 'png'])]
            )
        
        test_set.fix(True)
        
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to make space for the multi-assigned index to expand even though that's unnecessary at the end.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [5, 5, 'jpg']),
                (mock_change_index.assert_any_call, [5, 6, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the multi-assigned index at the end of the set.")
        self.assertEqual(mock_change_index.call_count, 2, "The FileSet tries to change even more indexes than the multi-assigned one.")
        
    def test_multi_assigned_index_at_front_fix(self):
        """The FileSet should be able to fix a multi-assigned index at the front of the set."""
        test_files = ['test (0).jpg', 'test (0).png', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                [(0, ['jpg', 'png'])]
            )
        
        test_set.fix(True)
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(1, 5), 2], "The FileSet fails to make space for the multi-assigned index to expand if it's at the front.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0, 'jpg']),
                (mock_change_index.assert_any_call, [0, 1, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the multi-assigned index at the front of the set.")
        self.assertEqual(mock_change_index.call_count, 2, "The FileSet tries to change even more indexes than the multi-assigned one.")
        
    def test_multiple_multi_assigned_indexes_fix(self):
        """The FileSet should be able to fix multiple multi-assigned indexes (this will require the method to use an internal offset, since every fix moves the existing indexes a bit)."""
        #------------------------------------------------------------------------------ 
        # Make sure FileSet's max index is updated after mocked call of move_range 
        # or else this test fails due to the tested method's logic not working out        
        #------------------------------------------------------------------------------
        def mock_move_range_side_effect(range_tuple, to_position):
            left_range, _ = range_tuple
            
            move_amount = to_position - left_range
            test_set.max_index += move_amount
        mock_move_range.side_effect = mock_move_range_side_effect
        #------------------------------------------------------------------------------ 
        
        test_files = ['test (0).jpg', 'test (0).png', 'test (1).jpg', 'test (2).gif', 'test (2).jpg', 'test (2).png', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                [(0, ['jpg', 'png']), (2, ['gif', 'jpg', 'png'])]
            )
        
        test_set.fix(True)
        
        
        mock_assert_msg(mock_move_range.assert_any_call, [(3, 5), 5], "The FileSet fails to correctly make space for the first multi-assigned index if there are multiple of them.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [2, 2, 'gif']),
                (mock_change_index.assert_any_call, [2, 3, 'jpg']),
                (mock_change_index.assert_any_call, [2, 4, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the first multi-assigned index.")
        
        mock_assert_msg(mock_move_range.assert_any_call, [(1, 7), 2], "The FileSet fails to make space for the second multi-assigned index.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0, 'jpg']),
                (mock_change_index.assert_any_call, [0, 1, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the second multi-assigned index.")
        
        self.assertEqual(mock_change_index.call_count, 5, "The FileSet tries to change even more indexes than the multi-assigned ones.")
        
    def test_multi_assigned_index_in_middle_fix_file_types_wrong_order(self):
        """The FileSet should be able to correctly auto-fix a multi_assigned index which's file types aren't given in the correct order."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (3).png', 'test (3).mp4', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                [(3, ['png', 'jpg', 'mp4'])]
            )
        
        test_set.fix(True)
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(4, 5), 6], "The FileSet fails to correctly make space for the multi-assigned index to expand if the file_types are in the wrong order.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [3, 3, 'jpg']),
                (mock_change_index.assert_any_call, [3, 4, 'mp4']),
                (mock_change_index.assert_any_call, [3, 5, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the multi-assigned index if the file_types are in the wrong order.")

    def test_multi_assigned_indexes_fix_and_gaps(self):
        """The FileSet should be able to correctly auto-fix multi-assigned indexes and gaps both at once."""
        test_files = ['test (0).jpg', 'test (2).gif', 'test (2).png', 'test (3).jpg', 'test (6).jpg', 'test (7).gif', 'test (7).jpg', 'test (7).mp4']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [(1, 1), (4, 5)],
                [(2, ['gif', 'png']), (7, ['gif', 'jpg', 'mp4'])]
            )
        
        # TODO: test
        
        def mock_change_index_side_effect(f, t, _2=None):
            """Update the max index of the file set."""
            if t > test_set.max_index:
                test_set.max_index = t
            elif f == test_set.max_index:
                test_set.max_index = t
        mock_change_index.side_effect = mock_change_index_side_effect
        
        test_set.fix(True)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [2, 1]),
                (mock_change_index.assert_any_call, [3, 2]),
                (mock_change_index.assert_any_call, [6, 3]),
                (mock_change_index.assert_any_call, [7, 4])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly move the files in order to close multiple gaps in the middle in a set with multi-assigned indexes.")

        # move range shouldn't be called at this point, since this multi-assigned is at the end
        assertion_calls = [
                (mock_change_index.assert_any_call, [4, 4, 'gif']),
                (mock_change_index.assert_any_call, [4, 5, 'jpg']),
                (mock_change_index.assert_any_call, [4, 6, 'mp4'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to fix the multi-assigned index at the end with the correct index numbers if gaps were closed beforehand.")
        
        # here, move range has to be called
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 6), 3], "The FileSet fails to correctly make space for the multi-index expansion if gaps have been fixed before.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [1, 1, 'gif']),
                (mock_change_index.assert_any_call, [1, 2, 'png'])
            ]
        mock_assert_many_msg(assertion_calls,  "The FileSet fails to correctly expand the last multi-assigned index.")
    
    def test_set_enormous_max_index(self):
        """The FileSet should be able to fix itself even if it has a max index greater than 1000."""
        test_files = ['test (234).jpg', 'test (346).jpg', 'test (934).jpg', 'test (1038).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.side_effect = FileSet.TooManyFilesError()
        
        try:
            test_set.fix()
        except FileSet.TooManyFilesError:
            self.fail("The FileSet raises a TooManyFilesError even though it could have fixed the set of only four files.")
            
        assertion_calls = [
                (mock_change_index.assert_any_call, [234,  0]),
                (mock_change_index.assert_any_call, [346,  1]),
                (mock_change_index.assert_any_call, [934,  2]),
                (mock_change_index.assert_any_call, [1038, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to fix the gaps of a file set with a max_index above 1000.")
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to move ranges even though there is no reason to make any space.")
        
    def test_set_enormous_amount_of_files_no_multi_index_auto_fix(self):
        """Even if the file set contains more than 1000 files, the file set should fix possible gaps."""        
        test_set = FileSet(self.pattern, [])
        test_set.files = EnormousDict()
        test_set.max_index = 1234
        
        mock_find_flaws.side_effect = FileSet.TooManyFilesError()
        
        try:
            test_set.fix()
        except FileSet.TooManyFilesError:
            self.fail("The FileSet raises an exception when there's more than 1000 files, even though auto-fix multi-assigned indexes was not requested and thus there should be no problem.")
        
    def test_set_enormous_amount_of_files_auto_fix_multi_indexes(self):
        """The FileSet should raise an error if requested to fix multi-assigned indexes in a set of more than 1000 files."""
        test_set = FileSet(self.pattern, [])
        test_set.files = EnormousDict()
        test_set.max_index = 1234
        
        mock_find_flaws.side_effect = FileSet.TooManyFilesError()
        
        with self.assertRaises(FileSet.TooManyFilesError, msg="The FileSet fails to recognize when there are too many files to auto-fix multi-assigned indexes."):
            test_set.fix(True)
    
    def test_set_enormous_max_index_auto_fix_multi_indexes(self):
        """The FileSet should be able to fix both gaps and multi-assigned indexes in a file set with a max_index greater than 1000, but with less than 1000 files."""
        test_files = ['test (0).jpg', 'test (0).png', 'test (101).jpg', 'test (4444).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_find_flaws_side_effect():
            global mock_find_flaws_call_count
            
            if mock_find_flaws_call_count == 0:
                mock_find_flaws_call_count += 1
                test_set.max_index = 2
                raise FileSet.TooManyFilesError()
            elif mock_find_flaws_call_count == 1:
                flaws = (
                        [],
                        [(0, ['jpg', 'png'])]
                    )
                return flaws
        mock_find_flaws.side_effect = mock_find_flaws_side_effect
        
        try:
            test_set.fix(True)
        except FileSet.TooManyFilesError:
            self.fail("The FileSet raises a TooManyFilesError even though in actuality there are much less than 1000.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0]),
                (mock_change_index.assert_any_call, [101, 1]),
                (mock_change_index.assert_any_call, [4444, 2])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to fix the gaps of a file set with a max_index greater than 1000.")
        
        self.assertEqual(mock_find_flaws.call_count, 2, "The FileSet doesn't call find_flaws another time after fixing the gaps even though now there clearly are less than 1000 files.")
        
        mock_assert_msg(mock_move_range.assert_called_once_with, [(1, 2), 2], "The FileSet fails to make space for the expansion of the multi-assigned index after fixing the wide gaps of a file set with max_index > 1000.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0, 'jpg']),
                (mock_change_index.assert_any_call, [0, 1, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the multi-assigned index after having fixed a file set with a max_index greater than 1000.")
        
    def test_big_multi_assigned_real_world(self):
        """The FileSet should be able to correctly deal with a multi-assigned indexes of at least three files, given that change_index actively updates the file set's file list."""
        test_files = ['test (0).gif', 'test (0).jpg', 'test (0).png']
        test_set = FileSet(self.pattern, test_files)
        
        mock_find_flaws.return_value = (
                [],
                [(0, test_set.files[0])]
            )
        
        def mock_change_index_side_effect(f, t, ft):
            """If the index is actually changed, delete the given file type from the list. I.e. update the files list with every call!"""
            if ft is None:
                del test_set.files[f]
            elif f != t:
                types_list = test_set.files[f]
                types_list.remove(ft)
        mock_change_index.side_effect = mock_change_index_side_effect
        
        test_set.fix(True)
        
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to make space even though the multi-assigned index is at the end, making this unnecessary.")
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 0, 'gif']),
                (mock_change_index.assert_any_call, [0, 1, 'jpg']),
                (mock_change_index.assert_any_call, [0, 2, 'png'])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to correctly expand the multi-assigned index at the front of the set if there are real world side effects.")
        self.assertEqual(mock_change_index.call_count, 3, "The FileSet tries to change even more indexes than the multi-assigned one.")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()