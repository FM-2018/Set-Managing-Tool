'''
Created on 28.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, KeywordArgTuple


def strip_gaps(boolean):
    return KeywordArgTuple('strip_gaps', boolean)

def preserve_gaps(boolean):
    return KeywordArgTuple('preserve_gaps', boolean)


mock_add_file_set = mock.MagicMock(name='add_file_set')
mock_remove_files = mock.MagicMock(name='remove_files')
mock_move_range = mock.MagicMock(name='move_range')
mock_order_index_range = mock.MagicMock(name='_order_index_range')

@mock.patch('FileSet.FileSet.add_file_set', new=mock_add_file_set)
@mock.patch('FileSet.FileSet.remove_files', new=mock_remove_files)
@mock.patch('FileSet.FileSet.move_range', new=mock_move_range)
@mock.patch('FileSet.FileSet._order_index_range', new=mock_order_index_range)
class SwitchFileRangesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def setUp(self):
        self.mock_add_file_set_runtime_call_count = 0
        self.mock_remove_files_runtime_call_count = 0
    
    def tearDown(self):
        mock_add_file_set.reset_mock()
        mock_remove_files.reset_mock()
        mock_move_range.reset_mock()
        mock_order_index_range.reset_mock()
        
        mock_add_file_set.side_effect = None
    
    
    def assert_correct_tmp_removal(self, expected_file_range_to_shift, expected_strip_gaps_bool, expected_preserve_gaps_bool, call_num=0):
        try:
            args, kwargs = mock_remove_files.call_args_list[call_num]
        except IndexError:
            raise AssertionError("The method remove_files was called LESS than {} times".format(call_num+1))
        actual_file_range_to_shift, _ = args
        actual_strip_gaps_bool = kwargs.get('strip_gaps', False)
        actual_preserve_gaps_bool = kwargs.get('preserve_gaps', False)
        actual_keep_gaps_in_set_bool = kwargs.get('keep_gaps_in_set', False)
        
        self.assertEqual(actual_file_range_to_shift, expected_file_range_to_shift, "The FileSet does not temporarily remove the correct files.")
        self.assertEqual(actual_strip_gaps_bool, expected_strip_gaps_bool, "The FileSet fails to temporarily remove the files with the correct gap-handling option.")
        self.assertEqual(actual_preserve_gaps_bool, expected_preserve_gaps_bool, "The FileSet fails to temporarily remove the files with the correct gap-handling option.")
        self.assertEqual(actual_keep_gaps_in_set_bool, True, "The FileSet fails to temporarily remove files in such a way that gaps are not closed.")
    
    def assert_correct_readd_call(self, expected_spot, expected_indexes, call_num=1):
        try:
            args, _ = mock_add_file_set.call_args_list[call_num]
        except IndexError:
            raise AssertionError("The method add_files was called LESS than {} times".format(call_num+1))
        _, actual_spot, actual_indexes = args
        
        self.assertEqual(actual_spot, expected_spot, "The FileSet fails to readd the temporarily removed files at the correct position.")
        self.assertEqual(actual_indexes, expected_indexes, "The FileSet fails to readd the correct files.")
    
    def make_mock_add_file_set_change_return_values(self, *args):
        def side_effect_method(_1, _2, _3, **_4):
            try:
                ret_val = args[self.mock_add_file_set_runtime_call_count]
                self.mock_add_file_set_runtime_call_count += 1
                return ret_val
            except KeyError:
                raise AssertionError("add_files called more often than expected")
            
        return side_effect_method
    
    def make_mock_remove_files_change_return_values(self, *args):
        def side_effect_method(_1, _2, **_3):
            try:
                ret_val = args[self.mock_remove_files_runtime_call_count]
                self.mock_remove_files_runtime_call_count += 1
                return ret_val
            except KeyError:
                raise AssertionError("remove_files called more often than expected")
        
        return side_effect_method
    
    #------------------------------------------------------------------------------ 
    # Test equal range sizes
    #------------------------------------------------------------------------------ 
    def test_equal_ranges_middle(self):
        """The FileSet should be able to switch two equal ranges."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.return_value = 2
        
        test_set.switch_file_ranges((1, 2), (4, 5))
        
        self.assert_correct_tmp_removal(range(4, 5+1), False, False)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(3, 3), 3], "The FileSet tries to move the file in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (3, 4), range(1, 2+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
        
    def test_equal_ranges_mid_to_end(self):
        """The FileSet should be able to switch two equal ranges from middle to end of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.return_value = 2
        
        test_set.switch_file_ranges((1, 2), (7, 8))
        
        self.assert_correct_tmp_removal(range(7, 8+1), False, False)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(3, 6), 3], "The FileSet tries to move the files in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (6, 7), range(1, 2+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
        
    def test_equal_ranges_mid_to_front(self):
        """The FileSet should be able to switch two equal ranges from middle to front of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.return_value = 2
        
        test_set.switch_file_ranges((0, 1), (5, 6))
        
        self.assert_correct_tmp_removal(range(5, 6+1), False, False)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 4), 2], "The FileSet tries to move the files in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (4, 5), range(0, 1+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((-1, 0), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
        
    def test_equal_ranges_front_to_end(self):
        """The FileSet should be able to switch two equal ranges from front to end of the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.return_value = 2
        
        test_set.switch_file_ranges((0, 1), (7, 8))
        
        self.assert_correct_tmp_removal(range(7, 8+1), False, False)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 6), 2], "The FileSet tries to move the files in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (6, 7), range(0, 1+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((-1, 0), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    def test_single_files(self):
        """The FileSet should be able to switch two single files with each other."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 0 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 1)
        mock_add_file_set.return_value = 1
        
        test_set.switch_file_ranges((1, 1), (3, 3))
        
        self.assert_correct_tmp_removal(range(3, 3+1), False, False)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(2, 2), 2], "The FileSet tries to move the files in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (2, 3), range(1, 1+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 0+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    #------------------------------------------------------------------------------ 
    # Test unequal range sizes
    #------------------------------------------------------------------------------ 
    def test_big_mid_left_small_mid_right(self):
        """The FileSet should be able to switch a bigger range on the left side and a smaller range on the right side."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
        
        test_set.switch_file_ranges((1, 3), (5, 6))
        
        self.assert_correct_tmp_removal(range(1, 3+1), False, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (0, 1), range(5, 6+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        mock_assert_msg(mock_move_range.assert_any_call, [(4, 4), 3], "The FileSet fails to adjust the files in between the two ranges correctly.")
        self.assert_correct_readd_call((3, 4), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    def test_small_mid_left_big_mid_right(self):
        """The FileSet should be able to switch a smaller range from the left side and a bigger range from the right side."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
        
        test_set.switch_file_ranges((1, 2), (5, 7))
        
        self.assert_correct_tmp_removal(range(5, 7+1), False, False)
        mock_assert_msg(mock_move_range.assert_any_call, [(3, 4), 4], "The FileSet fails to adjust the files in between the two ranges correctly.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (5, 6), range(1, 2+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
        
    def test_big_mid_small_end(self):
        """The FileSet should be able to switch a bigger range from the middle and a smaller range from the end."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
         
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
         
        test_set.switch_file_ranges((2, 4), (7, 8))
         
        self.assert_correct_tmp_removal(range(2, 4+1), False, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (1, 2), range(7, 8+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 4], "The FileSet fails to adjust the files in between the two ranges correctly.")
        self.assert_correct_readd_call((5, 6), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    def test_small_mid_big_end(self):
        """The FileSet should be able to switch a smaller range from the middle and a bigger range from the end."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
        
        test_set.switch_file_ranges((2, 3), (6, 8))
        
        self.assert_correct_tmp_removal(range(6, 8+1), False, False)
        mock_assert_msg(mock_move_range.assert_any_call, [(4, 5), 5], "The FileSet fails to adjust the files in between the two ranges correctly.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (6, 7), range(2, 3+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((1, 2), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    def test_small_mid_big_front(self):
        """The FileSet should be able to switch a smaller range from the middle and a bigger range from the front."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
         
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
         
        test_set.switch_file_ranges((0, 2), (4, 5))
         
        self.assert_correct_tmp_removal(range(0, 2+1), False, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(4, 5+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        mock_assert_msg(mock_move_range.assert_any_call, [(3, 3), 2], "The FileSet fails to adjust the files in between the two ranges correctly.")
        self.assert_correct_readd_call((2, 3), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
 
    def test_big_mid_small_front(self):
        """The FileSet should be able to switch a bigger range from the middle and a smaller range from the front."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
        
        test_set.switch_file_ranges((0, 1), (3, 5))
        
        self.assert_correct_tmp_removal(range(3, 5+1), False, False)
        mock_assert_msg(mock_move_range.assert_any_call, [(2, 2), 3], "The FileSet fails to adjust the files in between the two ranges correctly.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (3, 4), range(0, 1+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((-1, 0), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    #------------------------------------------------------------------------------ 
    # Test ranges with gaps / no gap-handling and preserve_gaps
    #------------------------------------------------------------------------------ 
    def test_equal_ranges_gaps_no_gap_handling(self):
        """The FileSet should be able to recognize gaps in the given ranges and raise an error if no gap-handling option is chosen."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        mock_remove_files.side_effect = FileSet.IndexUnassignedError("Index 5 does not exist.")
        
        with self.assertRaises(FileSet.IndexUnassignedError, msg="The FileSet fails to recognize and raise an error if it encounters gaps with no gap-handling option chosen."):
            test_set.switch_file_ranges((1, 2), (4, 5))
        
        self.assert_correct_tmp_removal(range(4, 5+1), False, False)
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The FileSet tries to move or re-add files even though an error was raised.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to close resulting gap-space or move an in between range even though an error was raised.")
    
    def test_equal_ranges_gaps_preserve_gaps(self):
        """The FileSet should be able to switch two ranges with gaps if gap-handling option preserve_gaps is chosen."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.return_value = 2
        
        test_set.switch_file_ranges((1, 2), (4, 5), preserve_gaps=True)
        
        self.assert_correct_tmp_removal(range(4, 5+1), False, True)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(3, 3), 3], "The FileSet tries to move the file in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (3, 4), range(1, 2+1), strip_gaps(False), preserve_gaps(True)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    #------------------------------------------------------------------------------ 
    # Test ranges with gaps / strip_gaps
    #------------------------------------------------------------------------------ 
    def test_big_mid_left_small_mid_right_gaps_strip_gaps(self):
        """The FileSet should be able to switch a bigger range on the left side and a smaller range on the right side if they contain gaps and gap-handling option strip_gaps is chosen."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(1, 2)
        
        test_set.switch_file_ranges((1, 3), (5, 6), strip_gaps=True)
        
        self.assert_correct_tmp_removal(range(1, 3+1), True, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (0, 1), range(5, 6+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        mock_assert_msg(mock_move_range.assert_any_call, [(4, 4), 2], "The FileSet fails to adjust the files in between the two ranges correctly.")
        self.assert_correct_readd_call((2, 3), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 5], "The FileSet fails to to close resulting gap-space.")
    
    def test_small_mid_left_big_mid_right_gaps_strip_gaps(self):
        """The FileSet should be able to switch a smaller range from the left side and a bigger range from the right side if they contain gaps and gap-handling option strip_gaps is chosen."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(1, 2)
        
        test_set.switch_file_ranges((1, 2), (5, 7), strip_gaps=True)
        
        self.assert_correct_tmp_removal(range(5, 7+1), True, False)
        mock_assert_msg(mock_move_range.assert_any_call, [(3, 4), 3], "The FileSet fails to adjust the files in between the two ranges correctly.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (4, 5), range(1, 2+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(8, 8), 6], "The FileSet fails to close resulting gap-space.")
    
    def test_big_mid_small_end_gaps_strip_gaps(self):
        """The FileSet should be able to switch a bigger range from the middle and a smaller range from the end if they contain gaps and gap-handling option strip_gaps is chosen."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(1, 2)
        
        test_set.switch_file_ranges((2, 4), (7, 8), strip_gaps=True)
        
        self.assert_correct_tmp_removal(range(2, 4+1), True, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (1, 2), range(7, 8+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        mock_assert_msg(mock_move_range.assert_any_call, [(5, 6), 3], "The FileSet fails to adjust the files in between the two ranges correctly.")
        self.assert_correct_readd_call((4, 5), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to to close resulting gap-space even though that's unnecessary when switching from/to the end.")
        self.assertEqual(test_set.max_index, 6, "The FileSet fails to update its max_index when switching from/to the end.")
    
    def test_small_mid_big_end_gaps_strip_gaps(self):
        """The FileSet should be able to switch a smaller range from the middle and a bigger range from the end if they contain gaps and gap-handling option strip_gaps is chosen."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(1, 2)
        
        test_set.switch_file_ranges((2, 3), (6, 8), strip_gaps=True)
        
        self.assert_correct_tmp_removal(range(6, 8+1), True, False)
        mock_assert_msg(mock_move_range.assert_any_call, [(4, 5), 4], "The FileSet fails to adjust the files in between the two ranges correctly.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (5, 6), range(2, 3+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((1, 2), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though that's unnecessary when switching from/to the end.")
        self.assertEqual(test_set.max_index, 6, "The FileSet fails to update its max_index when switching from/to the end.")
        
    def test_small_mid_big_front_gaps_strip_gaps(self):
        """The FileSet should be able to switch a smaller range from the middle and a bigger range from the front if they contain gaps and gap-handling option strip_gaps is chosen."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(1, 2)
        
        test_set.switch_file_ranges((0, 2), (4, 5), strip_gaps=True)
        
        self.assert_correct_tmp_removal(range(0, 2+1), True, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (-1, 0), range(4, 5+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        mock_assert_msg(mock_move_range.assert_any_call, [(3, 3), 1], "The FileSet fails to adjust the files in between the two ranges correctly.")
        self.assert_correct_readd_call((1, 2), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_any_call, [((6, 8)), 4], "The FileSet tries to close resulting gap-space even though that's unnecessary when switching from/to the end.")
 
    def test_big_mid_small_front_gaps_strip_gaps(self):
        """The FileSet should be able to switch a bigger range from the middle and a smaller range from the front if they contain gaps and gap-handling option strip_gaps is chosen."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(1, 2)
        
        test_set.switch_file_ranges((0, 1), (4, 6), strip_gaps=True)
        
        self.assert_correct_tmp_removal(range(4, 6+1), True, False)
        mock_assert_msg(mock_move_range.assert_any_call, [(2, 3), 2], "The FileSet fails to adjust the files in between the two ranges correctly.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (3, 4), range(0, 1+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((-1, 0), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 5], "The FileSet fails to close resulting gap-space.")
        
    def test_big_mid_left_small_mid_right_strip_gaps_big_actually_smaller(self):
        """The FileSet should be able to switch two file ranges if the one that was originally bigger turns out to be smaller after the gaps have been stripped."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 0 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 1)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 1)
        
        test_set.switch_file_ranges((1, 3), (5, 6), strip_gaps=True)
        
        self.assert_correct_tmp_removal(range(1, 3+1), True, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (0, 1), range(5, 6+1), strip_gaps(True), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        mock_assert_msg(mock_move_range.assert_any_call, [(4, 4), 3], "The FileSet fails to adjust the files in between the two ranges correctly.")
        self.assert_correct_readd_call((3, 4), range(0, 0+1))
        mock_assert_msg(mock_move_range.assert_called_with, [((7, 8)), 5], "The FileSet fails to close resulting gap-space.")
    
    def test_big_mid_right_small_mid_left_strip_gaps_big_actually_smaller(self):
        """The FileSet should be able to switch two file ranges if the one that was originally bigger turns out to be smaller after the gaps have been stripped."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
         
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set_first = FileSet(('tmp', ''), [])
        new_tmp_set_first.max_index = 0 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        new_tmp_set_second = FileSet(('tmp', ''), [])
        new_tmp_set_second.max_index = 2
        mock_remove_files.side_effect = self.make_mock_remove_files_change_return_values((new_tmp_set_first, 1), (new_tmp_set_second, 2))
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(1, 2)
         
        test_set.switch_file_ranges((1, 2), (4, 6), strip_gaps=True)
         
        self.assert_correct_tmp_removal(range(4, 6+1), True, False, call_num=0)
        ## special case; since actual removed big range is smaller, need to temporary remove smaller (now bigger) range as well
        self.assert_correct_tmp_removal(range(1, 2+1), True, False, call_num=1)
         
        mock_assert_msg(mock_move_range.assert_any_call, [(3, 3), 2], "The FileSet fails to adjust the files in between the two ranges correctly.")
        
        self.assert_correct_readd_call((0, 1), range(0, 0+1), call_num=0) # "greater" range
        self.assert_correct_readd_call((2, 3), range(1, 2+1), call_num=1) # "smaller" range
        
        mock_assert_msg(mock_move_range.assert_called_with, [(7, 8), 5], "The FileSet fails to close resulting gap-space.")
        
    #------------------------------------------------------------------------------ 
    # Test misc.
    #------------------------------------------------------------------------------ 
    def test_switch_adjacent_ranges_big_mid_left_small_mid_right(self):
        """The FileSet should be able to switch two ranges that are right next to each other."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
         
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
         
        test_set.switch_file_ranges((2, 4), (5, 6))
         
        self.assert_correct_tmp_removal(range(2, 4+1), False, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (1, 2), range(5, 6+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((3, 4), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to adjust an in between range even though there is none OR it tries to close resulting gap-space even though there is none .")
    
    def test_switch_adjacent_ranges_small_mid_left_big_mid_right(self):
        """The FileSet should be able to switch two ranges that are right next to each other."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        mock_order_index_range.side_effect = lambda t: t # simply return given range. For now we always input valid ones
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 2 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 3)
        mock_add_file_set.side_effect = self.make_mock_add_file_set_change_return_values(2, 3)
        
        test_set.switch_file_ranges((2, 3), (4, 6))
        self.assert_correct_tmp_removal(range(4, 6+1), False, False)
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (4, 5), range(2, 3+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((1, 2), range(0, 2+1))
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to adjust an in between range even though there is none OR it tries to close resulting gap-space even though there is none .")        
    
    def test_overlapping_ranges(self):
        """The FileSet should be able to recognize and raise an error if the two given ranges overlap each other."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        test_set.switch_file_ranges((1, 2), (4, 5))
        
        self.assert_correct_tmp_removal(range(4, 5+1), False, False)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(3, 3), 3], "The FileSet tries to move the file in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (3, 4), range(1, 2+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")
    
    def test_ranges_wrong_order(self):
        """The FileSet should be able to operate even if a range is given in the wrong order."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (3).jpg', 'test (4).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        with self.assertRaises(FileSet.OverlappingRangesError, msg="The FileSet fails to recognize and raise an error if the two ranges overlap each other."):
            test_set.switch_file_ranges((1, 2), (2, 3))
        
        with self.assertRaises(FileSet.OverlappingRangesError, msg="The FileSet fails to recognize and raise an error if the two ranges overlap each other."):
            test_set.switch_file_ranges((1, 3), (2, 4))
        
        with self.assertRaises(FileSet.OverlappingRangesError, msg="The FileSet fails to recognize and raise an error if the two ranges overlap each other."):
            test_set.switch_file_ranges((1, 6), (3, 4))
        
        mock_assert_msg(mock_remove_files.assert_not_called, [], "The FileSet tries to temporarily remove files even though an error was raised.")
        mock_assert_msg(mock_add_file_set.assert_not_called, [], "The FileSet tries to move or re-add files even though an error was raised.")
        mock_assert_msg(mock_move_range.assert_not_called, [], "The FileSet tries to close resulting gap-space or move an in between range even though an error was raised.")
        
        def mock_order_index_range_side_effect(t):
            if t == (2, 1):
                return (1, 2)
            elif t == (5, 4):
                return (4, 5)
        mock_order_index_range.side_effect = mock_order_index_range_side_effect
        new_tmp_set = FileSet(('tmp', ''), [])
        new_tmp_set.max_index = 1 # "update" tmp_set's max index after temporarily removing files into it by returning this dummy
        mock_remove_files.side_effect = lambda _1, _2, **_3: (new_tmp_set, 2)
        mock_add_file_set.return_value = 2
        
        test_set.switch_file_ranges((2, 1), (5, 4))
        
        self.assert_correct_tmp_removal(range(4, 5+1), False, False)
        mock_assert_msg(mock_move_range.assert_called_once_with, [(3, 3), 3], "The FileSet tries to move the file in between the two ranges even though the two are equal sized and have no gap-handling.")
        mock_assert_msg(mock_add_file_set.assert_any_call, [test_set, (3, 4), range(1, 2+1), strip_gaps(False), preserve_gaps(False)], "The FileSet fails to correctly move the other range to its destined position.")
        self.assert_correct_readd_call((0, 1), range(0, 1+1))
        mock_assert_msg(mock_move_range.assert_called_once, [], "The FileSet tries to close resulting gap-space even though there is none.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()