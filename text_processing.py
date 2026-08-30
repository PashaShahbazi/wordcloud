"""Shared text-cleaning helpers for WordCloud inputs."""

import re


def normalize_text(text):
    """Remove Wikipedia headings and normalize whitespace between words."""
    text = re.sub(r"==.*?==+", " ", text)
    return " ".join(text.split())
