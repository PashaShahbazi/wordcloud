""" this script is for making plot for the wordcloud """
import matplotlib.pyplot as plt


def plot_cloud(cloud):
    # set figure size
    plt.figure(figsize=(50, 30))
    # display image
    plt.imshow(cloud)
    plt.axis('off')
