import unittest
from unittest.mock import patch

import get_wiki


class WikipediaTests(unittest.TestCase):
    @patch("get_wiki.wikipedia.set_user_agent")
    @patch("get_wiki.wikipedia.page")
    def test_lookup_uses_compliant_user_agent(self, page, set_user_agent):
        page.return_value.content = "Python content"

        get_wiki.wiki_get("Python")

        set_user_agent.assert_called_once_with(get_wiki.WIKIPEDIA_USER_AGENT)
        page.assert_called_once_with("Python", auto_suggest=False)

    @patch("get_wiki.wikipedia.page")
    def test_success_returns_page_content(self, page):
        page.return_value.content = "Python is a programming language."

        self.assertEqual(
            get_wiki.wiki_get("Python"), "Python is a programming language."
        )

    @patch("get_wiki.wikipedia.page")
    def test_network_or_api_failure_has_user_friendly_error(self, page):
        page.side_effect = RuntimeError("connection failed")

        with self.assertRaisesRegex(
            get_wiki.WikipediaLookupError, "Unable to retrieve Wikipedia content"
        ):
            get_wiki.wiki_get("python")

    @patch("get_wiki.wikipedia.page")
    def test_disambiguation_lists_a_few_choices(self, page):
        page.side_effect = get_wiki.wikipedia.exceptions.DisambiguationError(
            "python", ["Python", "Python language", "Pythonidae", "Monty Python"]
        )

        with self.assertRaisesRegex(
            get_wiki.WikipediaLookupError,
            "ambiguous.*Python, Python language, Pythonidae",
        ):
            get_wiki.wiki_get("python")

    @patch("get_wiki.wikipedia.page")
    def test_page_not_found_has_user_friendly_error(self, page):
        page.side_effect = get_wiki.wikipedia.exceptions.PageError("missing")

        with self.assertRaisesRegex(
            get_wiki.WikipediaLookupError, "No Wikipedia page was found"
        ):
            get_wiki.wiki_get("missing")


if __name__ == "__main__":
    unittest.main()
