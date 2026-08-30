# this script is for making wordcloud
import wordcloud as wrc


def _validate_text(text):
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")


def create_cloud(text, bgcolor, width=3000, height=2000):
    """
    (text, str) -> cloud
    return the array of the word cloud for plt
    >>create_cloud('file.txt')
    cloud
    """
    _validate_text(text)
    cloud = wrc.WordCloud(
        width=width,
        height=height,
        random_state=1,
        background_color=bgcolor,
        colormap="hsv",
        collocations=False,
        stopwords=wrc.STOPWORDS,
    ).generate(text)
    return cloud


def create_cloud_mask(text, bgcolor, mask):
    """
    (text, str, array) -> mask_cloud
    return the array of the word cloud for plt
    >>create_cloud('file.txt')
    arr
    """
    _validate_text(text)
    cloud = wrc.WordCloud(
        width=3000,
        height=2000,
        random_state=1,
        background_color=bgcolor,
        colormap="hsv",
        collocations=False,
        stopwords=wrc.STOPWORDS,
        mask=mask,
    ).generate(text)
    return cloud
