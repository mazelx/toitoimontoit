import random
from scrapping_modules.search import Search
import unittest


class SearchTest(unittest.TestCase):

    """Test case utilisé pour tester les fonctions du module 'random'."""

    def setUp(self):
        """Initialisation des tests."""
        self.search = Search("")

    def test_similar(self):
        """Test le fonctionnement de la fonction 'random.choice'."""
        pass