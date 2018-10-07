'''
Created on 28.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, KeywordArgTuple


def preserve_gaps(boolean):
    return KeywordArgTuple('preserve_gaps', boolean)

def strip_gaps(boolean):
    return KeywordArgTuple('strip_gaps', boolean)


mock_files_detected = mock.MagicMock(name='files_detected')
mock_add_file_set = mock.MagicMock(name='add_files')
mock_move_range = mock.MagicMock(name='move_range')

@mock.patch('FileSet.FileSet.files_detected', new=mock_files_detected)
@mock.patch('FileSet.FileSet.add_file_set', new=mock_add_file_set)
@mock.patch('FileSet.FileSet.move_range', new=mock_move_range)
class MoveFilesTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_files_detected.reset_mock()
        mock_add_file_set.reset_mock()
        mock_move_range.reset_mock()
    
    def check_readd_call(self, expected_readd_pos, expected_index_range):
        """Convenience method for testing re-addition of files using an add_files call."""
        call_tuple_args, call_tuple_kwargs = tuple(mock_add_file_set.call_args)
        used_file_set, used_readd_pos, used_index_range = call_tuple_args
        
        self.assertEqual(used_file_set.pattern, ('tmp', ''), "The FileSet uses a wrong FileSet pattern to remove/readd the files.")     
        self.assertEqual(used_readd_pos, (expected_readd_pos-1, expected_readd_pos), "The FileSet re-adds the files at the wrong position.")
        self.assertEqual(used_index_range, expected_index_range, "The FileSet doesn't correctly re-add the right files from the tmp file set.")  
        self.assertEqual(call_tuple_kwargs['preserve_gaps'], True, "The FileSet doesn't re-add files with the options preserve_gaps=True")
    
    def test_move_middle_to_middle(self):
        """The FileSet should be able to move a range of files from middle to middle."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (6, 7))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 7], "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
                
    def test_move_middle_to_end(self):
        """The FileSet should be able to move a range of files from middle to end."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (8, 9))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving to the end of the set.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 8), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(6, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet attempts to close possibly resulting gap space, even though that's unnecessary when moving to the end.")
        
    def test_move_middle_to_front(self):
        """The FileSet should be able to move a range of files from middle to front."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (-1, 0))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving to the front of the set.")
        mock_assert_msg(mock_move_range.assert_any_call, [(0, 1), 3], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(0, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(5, 8), 5], "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
        
    def test_move_middle_to_before_last_file(self):
        """The FileSet should be able to move a range of files from middle to in front of the last file of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (7, 8))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving before the last file of the set.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 7), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(5, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(8, 8), 8], "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
        
    def test_move_front_to_middle(self):
        """The FileSet should be able to move a range of files from front to middle."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((0, 1), (3, 4))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(0, 1+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving from the front to the middle.")
        mock_assert_msg(mock_move_range.assert_any_call, [(2, 3), 0], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(2, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(4, 8), 4], "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
        
    def test_move_end_to_middle(self):
        """The FileSet should be able to move a range of files from end to middle."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((7, 8), (3, 4))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(7, 8+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving from the end to the middle.")
        mock_assert_msg(mock_move_range.assert_any_call, [(4, 6), 6], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close possibly resulting gap-space even though that's unnecessary when moving from the end.")
        
    def test_move_end_to_front(self):
        """The FileSet should be able to move a range of files from end to front."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((7, 8), (-1, 0))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(7, 8+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving from the end to the front.")
        mock_assert_msg(mock_move_range.assert_any_call, [(0, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(0, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close possibly resulting gap-space even though that's unnecessary when moving from the end.")
        
    def test_move_front_to_end(self):
        """The FileSet should be able to move a range of files from front to end."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((0, 2), (8, 9))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(0, 2+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving from the front to the end.")
        mock_assert_msg(mock_move_range.assert_any_call, [(3, 8), 0], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(6, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close possibly resulting gap-space even though that's unnecessary when moving to the end.")
        
    def test_move_middle_to_far_end(self):
        """The FileSet should be able to move a range of files from middle to the far end of the set, causing a gap."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (10, 11))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving from the middle to the far end.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 10), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(8, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close possibly resulting gap-space even though that's unnecessary when moving to the end.")
        
    def test_move_single_file_range(self):
        """The FileSet should be able to move a range that contains only a single file, i.e. follows the scheme: (n, n)."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 1
        
        test_set.move_files((4, 4), (6, 7))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(4, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving a single-file range.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 4], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(6, range(0, 0+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 7],  "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
        
    def test_move_range_with_gaps_middle_to_middle_strip_gaps(self):
        """The FileSet should be able to move a range with gaps from middle to middle, stripping the gaps in the process."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((2, 4), (6, 7), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps, stripping the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 6],  "The FileSet doesn't correctly close resulting gap-space.")
        
    def test_move_range_with_gaps_middle_to_middle_preserve_gaps(self):
        """The FileSet should be able to move a range with gaps from middle to middle, stripping the gaps in the process."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (6, 7), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps, preserving the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 7],  "The FileSet doesn't correctly close resulting gap-space.")
        
    def test_move_range_with_gaps_middle_to_end_strip_gaps(self):
        """The FileSet should be able to move a range with gaps from middle to end when stripping the gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((2, 4), (8, 9), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps to the end, stripping the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 8), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(6, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none when moving to the end.")
        
    def test_move_range_with_gaps_middle_to_end_preserve_gaps(self):
        """The FileSet should be able to move a range with gaps from middle to end when preserving the gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (8, 9), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps to the end, presering the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 8), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(6, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none when moving to the end.")
        
    def test_move_range_with_gaps_middle_to_front_strip_gaps(self):
        """The FileSet should be able to move a range with gaps from middle to front when stripping the gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((2, 4), (-1, 0), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps to the front, stripping the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(0, 1), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(0, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(5, 8), 4],  "The FileSet doesn't correctly close resulting gap-space.")

    def test_move_range_with_gaps_middle_to_front_preserve_gaps(self):
        """The FileSet should be able to move a range with gaps from middle to front when preserving the gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (-1, 0), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps to the front, preserving the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(0, 1), 3], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(0, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(5, 8), 5],  "The FileSet doesn't correctly close resulting gap-space.")

    def test_move_range_with_gaps_end_to_front_strip_gaps(self):
        """The FileSet should be able to move a range with gaps from end to front when stripping the gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((7, 9), (-1, 0), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(7, 9+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps from the end to the front, stripping the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(0, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(0, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [],  "The FileSet tries to close resulting gap-space even though there is none when moving from the end.")
    
    def test_move_range_with_gaps_end_to_front_preserve_gaps(self):
        """The FileSet should be able to move a range with gaps from end to front when preserving the gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((7, 9), (-1, 0), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(7, 9+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps from the end to the front, preserving the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(0, 6), 3], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(0, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [],  "The FileSet tries to close resulting gap-space even though there is none when moving from the end.")
    
    def test_move_range_with_gaps_front_to_end(self):
        """The FileSet should be able to move a range with gaps from front to end when stripping the gaps.."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 1
        
        test_set.move_files((0, 1), (8, 9), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(0, 1+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps from the front to the end, stripping the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(2, 8), 0], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(7, range(0, 0+1))
        mock_assert_msg(mock_move_range.assert_called_once, [],  "The FileSet tries to close resulting gap-space even though there is none when moving to the end.")
        
    def test_move_range_with_gaps_front_to_end_preserve_gaps(self):
        """The FileSet should be able to move a range with gaps from front to end when preserving the gaps."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 2
        
        test_set.move_files((0, 1), (8, 9), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(0, 1+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to temporarily remove the correct files when moving a range with gaps from the front to the end, preserving the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(2, 8), 0], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(7, range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [],  "The FileSet tries to close resulting gap-space even though there is none when moving to the end.")
        
    def test_move_empty_range_upwards_strip_gaps(self):
        """The FileSet should be able to move an empty range upwards when stripping the gaps.."""
        test_files = ['test (0).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 0
        
        test_set.move_files((2, 4), (6, 7), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving an empty range upwards, stripping the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(0, 0))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 4],  "The FileSet fails to close the resulting gap-space.")
    
    def test_move_empty_range_updwards_preserve_gaps(self):
        """The FileSet should be able to move an empty range upwards when preserving the gaps."""
        test_files = ['test (0).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (6, 7), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to temporarily remove the correct files when moving an empty range upwards, preserving the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 7],  "The FileSet fails to close the resulting gap-space.")
        
    def test_move_empty_range_downwards_strip_gaps(self):
        """The FileSet should be able to move an empty range downwards, effectively closing the gap with option strip_gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 0
        
        test_set.move_files((2, 4), (0, 1), strip_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files when moving an empty range downwards, stripping the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(1, 1), 1], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(1, range(0, 0))
        mock_assert_msg(mock_move_range.assert_called_with, [(5, 8), 2],  "The FileSet fails to close the resulting gap-space.")
    
    def test_move_empty_range_downwards_preserve_gaps(self):
        """The FileSet should be able to move an empty range downwards when preserving the gaps."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (0, 1), preserve_gaps=True)
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to temporarily remove the correct files when moving an empty range downwards, preserving the gaps.")
        mock_assert_msg(mock_move_range.assert_any_call, [(1, 1), 4], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(1, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(5, 8), 5],  "The FileSet fails to close the resulting gap-space.")
        
    def test_move_if_already_tmp_files(self):
        """The FileSet should be able to move the files correctly even if there already are files following the tmp-files pattern."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), ['tmp1.png'])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (6, 7))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (1, 2), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files into the tmp FileSet if there already are tmp files.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(2, 4+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 7], "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
        
    def test_invalid_indexes_range(self):
        """The FileSet should recognize invalid (negative) indexes in the range and raise an error."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 1
        
        with self.assertRaises(ValueError, msg="The FileSet fails to recognize an invalid index in the range."):
            test_set.move_files((-2, 0), (6, 7))
        
    def test_invalid_indexes_spot(self):
        """The FileSet should recognize invalid (negative) indexes in the spot and raise an error accordingly."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        with self.assertRaises(ValueError, msg="The FileSet fails to recognize an invalid index in the spot."):
            test_set.move_files((2, 4), (-6, -7))
    
    def test_negative_one_in_spot(self):
        """The FileSet should see the usage of -1 as the left_spot in a spot as valid."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        try:
            test_set.move_files((2, 4), (-1, 0))
        except ValueError:
            self.fail("The FileSet sees a -1 in the spot as invalid, even though it is perfectly valid as the left_spot.")
        
    def test_invalid_spot(self):
        """The FileSet should recognize an invalid spot which's indexes are not adjacent and raise an error."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        with self.assertRaises(ValueError, msg="The FileSet fails to recognize an invalid spot."):
            test_set.move_files((2, 4), (5, 8))
        
    def test_range_wrong_order(self):
        """The FileSet should be able to deal with a valid range that's given from higher to lower."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((4, 2), (6, 7))
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files if the range is in the wrong order.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(4, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 7], "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
    
    def test_spot_wrong_order(self):
        """The FileSet should be able to deal with a valid spot that's given from higher to lower."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        try:
            test_set.move_files((2, 4), (6, 5))
        except ValueError:
            self.fail("The FileSet fails to deal with a spot that's given from higher to lower.")
        
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(2, 4+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to temporarily remove the correct files if the spot is in the wrong order.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 5), 2], "The FileSet fails to make space to readd the removed files into their destined position.")
        self.check_readd_call(3, range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(6, 8), 6], "The FileSet doesn't correctly attempt to close possibly resulting gap-space.")
        
    def test_spot_in_range(self):
        """The FileSet should do nothing when the given spot is actually covered by the range."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_files_detected.return_value = FileSet(('tmp', ''), [])
        mock_add_file_set.return_value = 3
        
        test_set.move_files((2, 4), (3, 4))
        
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The FileSet temporarily removes files or tries to add removed files even though no operation is necessary.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet makes space to readd removed files or tries to close gaps even though no operation is necessary.")
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()