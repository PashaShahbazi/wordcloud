""" this file is just for search and get wikipedia
information about the name from user """
import wikipedia

WIKIPEDIA_USER_AGENT = (
    "wordcloud-learning-project/1.0 "
    "(https://github.com/PashaShahbazi/wordcloud)"
)


class WikipediaLookupError(RuntimeError):
    """Raised when Wikipedia content cannot be retrieved for the user."""


def wiki_get(subject):
    """
    (str) --> str
    return the string text from wikipedia
    >>>wiki_get('name_subject')
    str text
    """
    wikipedia.set_user_agent(WIKIPEDIA_USER_AGENT)
    try:
        return wikipedia.page(subject, auto_suggest=False).content
    except wikipedia.exceptions.DisambiguationError as error:
        choices = ", ".join(error.options[:3])
        raise WikipediaLookupError(
            f"The Wikipedia subject '{subject}' is ambiguous. Try: {choices}."
        ) from error
    except wikipedia.exceptions.PageError as error:
        raise WikipediaLookupError(
            f"No Wikipedia page was found for '{subject}'."
        ) from error
    except Exception as error:
        raise WikipediaLookupError(
            "Unable to retrieve Wikipedia content. Check your connection and try again."
        ) from error
