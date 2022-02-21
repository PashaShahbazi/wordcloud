"""This main script is for generating a word cloud from the
word you search for on Wikipedia or a text in a "txt" format that you have prepared yourself.
"""
# Import needed packages
from tkinter.filedialog import askopenfile, asksaveasfile
import re
import numpy as np
import wordcloud
import make_plot
import get_wiki as gw
import get_wiki as w
import create_wordcloud as cw
import matplotlib.pyplot as mat
import make_plot as plt
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
    print('Please wait.....')
    # get the path of return image with tkinter
    save_path = asksaveasfile(title='Where you want to save?')
    save_path = save_path + '.jpg'
    # create the wordcloud from script create_wordcloud.py
    cloud = cw.create_cloud(text, bgcolor=background_color)
    # create plot from word cloud
    plt.plot_cloud(cloud)
    mat.show()
    # creat the image from word could
    # save imag of the word cloud in save path
    cloud.to_file(save_path.name)
    print('word cloud created!')
elif mask_or_not.lower() == 'y':
    # ask for image path for open it for wordcloud
    image = Image.open(askopenfile(title='Where the image you want to use').name)
    mask = np.array(image)
    save_path = asksaveasfile(title='Where you want to save?')
    print('Please wait.....')
    cloud = cw.create_cloud_mask(text=text, bgcolor=background_color, mask=mask)
    plt.plot_cloud(cloud)
    mat.show()
    cloud.to_file(save_path)
    print('word cloud created!')
else:
    pass
