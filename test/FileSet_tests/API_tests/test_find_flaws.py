'''
Created on 27.08.2018

@author: FM
'''
import unittest
from FileSet import FileSet

class FindFlawsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pattern = ('test (', ')')
    
            
    def test_flawless_file_set(self):
        """The FileSet should manage find no flaws in a flawless set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        flaws = test_set.find_flaws()
        
        self.assertEqual(flaws, ([], []), "The FileSet finds flaws when it's actually flawless.")
        
    def test_1_sized_gaps_in_middle(self):
        """The FileSet should be able to find a 1-sized gap in the middle of the set."""
        test_files = ['test (0).jpg', 'test (2).jpg', 'test (3).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        flaws = test_set.find_flaws()
        
        self.assertEqual(flaws, ([(1, 1), (4, 4)], []), "The FileSet fails to find 1-sized gaps.")
        
    def test_gaps_in_middle(self):
        """The FileSet should be able to find multiple gaps within the set."""
        test_files = ['test (0).jpg', 'test (5).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        flaws = test_set.find_flaws()
        
        self.assertEqual(flaws, ([(1, 4), (6, 7)], []), "The FileSet fails to find bigger gaps.")
        
    def test_gap_at_front(self):
        """The FileSet should be able to find a gap at the front."""
        test_files = ['test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (6).jpg', 'test (7).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        flaws = test_set.find_flaws()
        
        self.assertEqual(flaws, ([(0, 1)], []), "The FileSet fails to find a gap at the front.")
        
    def test_multi_assigned_indexes(self):
        """The FileSet should be able to find multi-assigned indexes within the set."""
        test_files = ['test (0).jpg', 'test (1).jpg', 'test (1).png', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (5).png', 'test (5).mp4', 'test (6).jpg', 'test (7).jpg', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        flaws = test_set.find_flaws()
        
        self.assertEqual(flaws, ([], [(1, ['jpg', 'png']), (5, ['jpg', 'png', 'mp4'])]), "The FileSet fails to find multi-assigned indexes.")
        
    def test_multi_assigned_indexes_next_to_gap(self):
        """The FileSet should be able to find multi-assigned indexes next to a gap within the set."""
        test_files = ['test (1).jpg', 'test (1).png', 'test (2).jpg', 'test (3).jpg', 'test (4).jpg', 'test (5).jpg', 'test (5).png', 'test (5).mp4', 'test (8).jpg']
        test_set = FileSet(self.pattern, test_files)
        
        flaws = test_set.find_flaws()
        
        self.assertEqual(flaws, ([(0, 0), (6, 7)], [(1, ['jpg', 'png']), (5, ['jpg', 'png', 'mp4'])]), "The FileSet fails to find gaps and multi-assigned indexes next to each other.")
    
    def test_too_high_max_index(self):
        """The FileSet should raise an error if the file set has a max_index of above 1000."""
        test_files = ['test (100111).jpg']
        test_set = FileSet(self.pattern, test_files)

        with self.assertRaises(FileSet.TooManyFilesError, msg="The FileSet fails to recognize when there are just too many indexes to scan for flaws."):
            test_set.find_flaws()
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()