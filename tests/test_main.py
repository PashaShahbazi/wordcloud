import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import get_wiki


class MainModuleTests(unittest.TestCase):
    def test_import_does_not_start_interactive_flow(self):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["MPLBACKEND"] = "Agg"

        result = subprocess.run(
            [sys.executable, "-c", "import main"],
            capture_output=True,
            env=environment,
            text=True,
            timeout=10,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_normalize_text_preserves_word_boundaries(self):
        import main

        text = "First line\nsecond line\r\n\n== Heading ==\nthird line"

        self.assertEqual(main.normalize_text(text), "First line second line third line")

    def test_read_text_file_uses_the_selected_path(self):
        import main

        with tempfile.TemporaryDirectory() as directory:
            text_path = Path(directory) / "sample text.txt"
            text_path.write_text("alpha\nbeta", encoding="utf-8")

            self.assertEqual(main.read_text_file(text_path), "alpha\nbeta")

    @patch("main.select_text_file", return_value="")
    @patch("builtins.input", return_value="f")
    def test_canceling_text_file_dialog_returns_cleanly(self, _input, _select):
        import main

        output = StringIO()
        with redirect_stdout(output):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("No text file was selected", output.getvalue())

    @patch("main.cw.create_cloud")
    @patch("main.select_save_path", return_value="")
    @patch("main.gw.wiki_get", return_value="Python text")
    @patch("builtins.input", side_effect=["w", "Python", "n", "white"])
    def test_canceling_save_dialog_stops_before_generation(
        self, _input, _wiki, _save, create_cloud
    ):
        import main

        output = StringIO()
        with redirect_stdout(output):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("No output file was selected", output.getvalue())
        create_cloud.assert_not_called()

    @patch("main.cw.create_cloud_mask")
    @patch("main.select_mask_file", return_value="")
    @patch("main.gw.wiki_get", return_value="Python text")
    @patch("builtins.input", side_effect=["w", "Python", "y", "white"])
    def test_canceling_mask_dialog_returns_cleanly(
        self, _input, _wiki, _mask, create_cloud_mask
    ):
        import main

        output = StringIO()
        with redirect_stdout(output):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("No mask image was selected", output.getvalue())
        create_cloud_mask.assert_not_called()

    def test_masked_flow_saves_to_filename_before_preview(self):
        import main

        events = []
        cloud = Mock()
        cloud.to_file.side_effect = lambda path: events.append(("save", path))
        opened_image = Mock()
        opened_image.__enter__ = Mock(return_value=opened_image)
        opened_image.__exit__ = Mock(return_value=False)
        opened_image.convert.return_value = "grayscale image"

        with (
            patch("builtins.input", side_effect=["w", "Python", "y", "white"]),
            patch("main.gw.wiki_get", return_value="Python text"),
            patch("main.select_mask_file", return_value="/tmp/mask.png"),
            patch("main.select_save_path", return_value="/tmp/cloud.png"),
            patch("main.Image.open", return_value=opened_image),
            patch("main.np.array", return_value="mask array"),
            patch("main.cw.create_cloud_mask", return_value=cloud),
            patch("main.plt.plot_cloud", side_effect=lambda _cloud: events.append(("plot", None))),
            patch("main.mat.show", side_effect=lambda: events.append(("show", None))),
        ):
            result = main.main()

        self.assertEqual(result, 0)
        self.assertEqual(
            events,
            [("save", "/tmp/cloud.png"), ("plot", None), ("show", None)],
        )

    @patch(
        "main.gw.wiki_get",
        side_effect=get_wiki.WikipediaLookupError(
            "Unable to retrieve Wikipedia content."
        ),
    )
    @patch("builtins.input", side_effect=["w", "Python"])
    def test_wikipedia_failure_is_reported_without_traceback(self, _input, _wiki):
        import main

        output = StringIO()
        with redirect_stdout(output):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("Unable to retrieve Wikipedia content", output.getvalue())

    @patch("main.gw.wiki_get", return_value="  \n\t")
    @patch("builtins.input", side_effect=["w", "Empty article"])
    def test_empty_source_text_is_reported_before_generation(self, _input, _wiki):
        import main

        output = StringIO()
        with redirect_stdout(output):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("did not contain any usable words", output.getvalue())

    @patch("main.cw.create_cloud", side_effect=ValueError("Invalid color"))
    @patch("main.select_save_path", return_value="/tmp/cloud.png")
    @patch("main.gw.wiki_get", return_value="Python text")
    @patch("builtins.input", side_effect=["w", "Python", "n", "not-a-color"])
    def test_generation_error_is_reported_without_traceback(
        self, _input, _wiki, _save, _create
    ):
        import main

        output = StringIO()
        with redirect_stdout(output):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("Error: Invalid color", output.getvalue())


if __name__ == "__main__":
    unittest.main()
