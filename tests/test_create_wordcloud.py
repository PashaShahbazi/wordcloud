import unittest

import numpy as np

import create_wordcloud


class CreateWordCloudTests(unittest.TestCase):
    def test_basic_cloud_generation_uses_known_text(self):
        cloud = create_wordcloud.create_cloud(
            "python learning python word cloud", "white"
        )

        self.assertIn("python", cloud.words_)
        self.assertIn("word", cloud.words_)

    def test_empty_text_is_rejected_with_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Text cannot be empty"):
            create_wordcloud.create_cloud("   \n\t", "white")

    def test_masked_cloud_generation_uses_generated_mask(self):
        mask = np.zeros((120, 120), dtype=np.uint8)

        cloud = create_wordcloud.create_cloud_mask(
            "python cloud masked example words", "white", mask
        )

        self.assertEqual(cloud.mask.shape, (120, 120))
        self.assertIn("python", cloud.words_)


if __name__ == "__main__":
    unittest.main()
