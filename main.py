"""This main script is for generating a word cloud from the
word you search for on Wikipedia or a text in a "txt" format that you have prepared yourself.
"""
# Import needed packages
from tkinter.filedialog import askopenfile, asksaveasfile
import re
import numpy as np
import wordcloud

import get_wiki as gw
import get_wiki as w
import create_wordcloud as cw
import matplotlib.pyplot as mat
import make_plot
from PIL import Image

wiki_or_file = input('Do you have a text file or do you want to search about a subject?\
\nenter f for file or w for Wikipedia--> ')
if wiki_or_file.lower() == 'f':
    text = askopenfile(mode='r', title='Where is your file txt')
    text = re.findall("[a-z A-Z]:.*t", str(text))
    # making text str type
    text1 = open(text[0]).readlines()
    text = ''
    for i in text1:
        text += i
elif wiki_or_file.lower() == 'w':
    wiki = input('Enter your subject--> ')
    text = gw.wiki_get(wiki)
else:
    print('Your answer is unknown')
    quit()
text = re.sub(r'==.*?==+', '', text)
text = text.replace('\n', '')
mask_or_not = input('Do you want the text to be in a specific photo? \nThe rule is that the photo \
must be black and white and in PNG format-->(y/n)')
background_color = input('What color do you want for back grand -->')
if mask_or_not.lower() == 'n':
    pass
elif mask_or_not.lower() == 'y':
    pass
else:
    pass