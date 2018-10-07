'''
Created on 27.08.2018

@author: FM
'''
import unittest
import unittest.mock as mock
from FileSet import FileSet
from test.testing_tools import mock_assert_msg, mock_assert_many_msg 


mock_change_index = mock.MagicMock(name='change_index')
@mock.patch('FileSet.FileSet.change_index', new=mock_change_index)
class MoveRangeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
    def tearDown(self):
        mock_change_index.reset_mock()
        mock_change_index.side_effect = None
    
    
    def test_beginning_to_end(self):
        """The FileSet should be able to move a range."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        test_set.move_range((0, 2), 7)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 7]),
                (mock_change_index.assert_any_call, [1, 8]),
                (mock_change_index.assert_any_call, [2, 9])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move a range from the beginning to the end of the set.")
        
    def test_dont_move_with_amount_0(self):
        """The FileSet should do nothing if the range isn't actually to be moved."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        test_set.move_range((0, 2), 0)
        
        mock_assert_msg(mock_change_index.assert_not_called, [], "The FileSet tries to move a range when in actuality it's moved by an amount of 0.")
        
    def test_move_into_big_gap(self):
        """The FileSet should be able to move a range into a gap within the set that has more than enough space for it."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (10).jpg', 'test (11).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        test_set.move_range((0, 2), 6)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 6]),
                (mock_change_index.assert_any_call, [1, 7]),
                (mock_change_index.assert_any_call, [2, 8])
            ]    
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move a range into the middle of a big gap which surrounds it in spaces.")
        
    def test_move_into_perfectly_fitting_gap(self):
        """The FileSet should be able to move a range into a range that has the exact same size."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (7).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        test_set.move_range((0, 2), 4)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 4]),
                (mock_change_index.assert_any_call, [1, 5]),
                (mock_change_index.assert_any_call, [2, 6])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move a range into a gap of exactly the same size.")
        
    def test_move_into_too_small_gap(self):
        """The FileSet should recognize when moving a range into a gap that is too tight and raise an error after undoing its operation."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        def mock_change_index_side_effect(f, t):
            if t == 4: raise FileSet.IndexAssignedError(t, f, "Index Assigned.")
        mock_change_index.side_effect = mock_change_index_side_effect
        
        with self.assertRaises(FileSet.FileCollisionError, msg="The FileSet fails to recognize when a range will collide with other files by being moved into a tight gap."):
            test_set.move_range((6, 8), 2)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [6, 2]),
                (mock_change_index.assert_any_call, [7, 3]),
                (mock_change_index.assert_any_call, [8, 4])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet doesn't actually try to move the range into the tight gap.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [3, 7]),
                (mock_change_index.assert_any_call, [2, 6])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to undo its operations after detecting a collision when being moved into the too-tight gap.")
        
    def test_move_range_downwards(self):
        """The FileSet should be able to move a range downwards."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        test_set.move_range((7, 8), 2)
        
        assertion_calls = [
            (mock_change_index.assert_any_call, [7, 2]),
            (mock_change_index.assert_any_call, [8, 3])
        ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move the range downwards.")
        
    def test_move_upwards_implicit_self_collision(self):
        """The FileSet should be able to move a range downwards, even if its new position will overlap with its old position. (i.e. in this case, the current 2 will be moved to the current 3, which is assigned at the moment)"""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        try:
            test_set.move_range((2, 3), 3)
        except FileSet.IndexAssignedError:
            self.fail("The FileSet can't move a range upwards if its new leftmost position is included in it, causing a file to seemingly 'collide' with the range's old position.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [3, 4]),
                (mock_change_index.assert_called_with, [2, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to actually move the range if there is an implicit self-collision.")
        
    def test_move_downwards_implicit_self_collision(self):
        """The FileSet should be able to move a range downwards, even if its new position will overlap with its old position. (i.e. in this case, the current 3 will be moved to the current 2, which is assigned at the moment)"""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        try:
            test_set.move_range((2, 3), 1)
        except FileSet.IndexAssignedError:
            self.fail("The FileSet can't move a range downwards if its new position causes a file to seemingly 'collide' with the range's old position.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [2, 1]),
                (mock_change_index.assert_called_with, [3, 2])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to actually move the range if there is an implicit self-collision.")
        
    def test_move_range_with_gaps_upwards(self):
        """The FileSet should be able to move a range with gaps upwards, preserving the gaps."""
        test_files = ['test (0).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_change_index_side_effect(f, _):
            if f in [1, 2]:
                raise FileSet.IndexUnassignedError()
        mock_change_index.side_effect = mock_change_index_side_effect
        
        try:
            test_set.move_range((0, 4), 6)
        except FileSet.IndexUnassignedError:
            self.fail("The FileSet fails to move a range upwards if it contains gaps as it doesn't handle the IndexUnassignedError.")
            
        assertion_calls = [
                (mock_change_index.assert_any_call, [4, 10]),
                (mock_change_index.assert_any_call, [3, 9]),
                (mock_change_index.assert_called_with, [0, 6])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move a range upwards if it contains gaps.")
    
    def test_move_range_with_gaps_downwards(self):
        """The FileSet should be able to move a range with gaps downwards, preserving the gaps."""
        test_files = ['test (3).jpg', 'test (4).jpg', 'test (7).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_change_index_side_effect(f, _):
            if f in [0, 1, 5, 6]:
                raise FileSet.IndexUnassignedError()
        mock_change_index.side_effect = mock_change_index_side_effect
        
        try:
            test_set.move_range((3, 7), 0)
        except FileSet.IndexUnassignedError:
            self.fail("The FileSet fails to move a range downwards if it contains gaps as it doesn't handle the IndexUnassignedError.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [3, 0]),
                (mock_change_index.assert_any_call, [4, 1]),
                (mock_change_index.assert_called_with, [7, 4])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move a range downwards if it contains gaps.")
        
    def test_move_gap(self):
        """The FileSet should do nothing when instructed to move a gap and ignore the IndexUnassignedErrors."""
        test_files = ['test (0).jpg', 'test (4).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_change_index_side_effect(f, t):
            raise FileSet.IndexUnassignedError(f, "Index unassigned.")
        mock_change_index.side_effect = mock_change_index_side_effect
        
        try:
            test_set.move_range((1, 3), 5)
        except FileSet.IndexUnassignedError:
            self.fail("The FileSet fails to ignore the IndexUnassignedError and thus the gaps.")
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [3, 7]),
                (mock_change_index.assert_any_call, [2, 6]),
                (mock_change_index.assert_any_call, [1, 5])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet doesn't even try to move the range if it is an entire gap.")
        
    def test_collision_with_files(self):
        """THe FileSet should recognize when the moved range collides with existing files and undo its operation."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_change_index_side_effect(f, t):
            if t == 3: raise FileSet.IndexAssignedError(f, t, "Index assigned.")
        mock_change_index.side_effect = mock_change_index_side_effect
        
        with self.assertRaises(FileSet.FileCollisionError, msg="The FileSet fails to recognize when a file is colliding due to the movement operation."):
            test_set.move_range((1, 2), 3)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [2, 4]),
                (mock_change_index.assert_any_call, [1, 3])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet does not actually try to move the range.")
        
        mock_assert_msg(mock_change_index.assert_any_call, [4, 2], "The FileSet does not properly undo its operations after discovering a file collision.")
        
    def test_move_gap_onto_files(self):
        """The FileSet should NOT find a collision when moving a gap onto other files."""
        test_files = ['test (0).jpg', 'test (4).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        def mock_change_index_side_effect(f, t):
            raise FileSet.IndexUnassignedError(f, t, "Index does not exist.")
        mock_change_index.side_effect = mock_change_index_side_effect
        
        test_set.move_range((1, 2), 4)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [2, 5]),
                (mock_change_index.assert_any_call, [1, 4])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet does not actually try to move the range.")
        
        with self.assertRaises(AssertionError, msg="The FileSet tries to undo its operation even though there shouldn't be a problem."):
            ## This assertion should fail, since the call should NOT exist!
            mock_assert_msg(mock_change_index.assert_any_call(5, 2))
        
    def test_range_wrong_order(self):
        """The FileSet should still move the range correctly even if the range is given from higher to lower."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg'] 
        test_set = FileSet(self.pattern, test_files)
        
        test_set.move_range((2, 0), 7)
        
        assertion_calls = [
                (mock_change_index.assert_any_call, [0, 7]),
                (mock_change_index.assert_any_call, [1, 8]),
                (mock_change_index.assert_any_call, [2, 9])
            ]
        mock_assert_many_msg(assertion_calls, "The FileSet fails to move a range from the beginning to the end of the set if the range is given in the wrong order.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()