from danbi import __version__
from unittest import TestCase

class TestVersion(TestCase):
    def test_version(self):
        assert __version__ == '0.1.0'
