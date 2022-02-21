# this script is for making wordcloud

def create_cloud(text, bgcolor):
    """
    (text, str) -> cloud
    return the array of the word cloud for plt
    >>create_cloud('file.txt')
    cloud
    """
    cloud = wrc.WordCloud(width=3000, height=2000, \
                          random_state=1, background_color=bgcolor, colormap='hsv', \
                          collocations=False, stopwords=wrc.STOPWORDS).generate(text)
    return cloud
