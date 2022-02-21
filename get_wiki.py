""" this file is just for search and get wikipedia
information about the name from user """
import wikipedia


def wiki_get(subject):
    """
    (str) --> str
    return the string text from wikipedia
    >>>wiki_get('name_subject')
    str text
    """
    return wikipedia.page(subject).content
