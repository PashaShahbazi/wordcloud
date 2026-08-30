import unittest

from text_processing import normalize_text


class TextProcessingTests(unittest.TestCase):
    def test_normalize_text_preserves_word_boundaries(self):
        text = "First line\nsecond line\r\n\n== Heading ==\nthird line"

        self.assertEqual(normalize_text(text), "First line second line third line")


if __name__ == "__main__":
    unittest.main()
