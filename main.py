"""Generate a word cloud from a text file or Wikipedia article."""

import re
from pathlib import Path

import matplotlib.pyplot as mat
import numpy as np
from PIL import Image

import create_wordcloud as cw
import get_wiki as gw
import make_plot as plt


def normalize_text(text):
    """Remove Wikipedia headings and normalize whitespace between words."""
    text = re.sub(r"==.*?==+", " ", text)
    return " ".join(text.split())


def read_text_file(path):
    """Read a user-selected UTF-8 text file."""
    with Path(path).open("r", encoding="utf-8") as text_file:
        return text_file.read()


def select_text_file():
    """Open the platform file picker and return a text-file path."""
    from tkinter.filedialog import askopenfilename

    return askopenfilename(
        title="Choose a text file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )


def select_mask_file():
    """Open the platform file picker and return a mask-image path."""
    from tkinter.filedialog import askopenfilename

    return askopenfilename(
        title="Choose a black and white mask image",
        filetypes=[("PNG image", "*.png"), ("All files", "*.*")],
    )


def select_save_path():
    """Open the platform file picker and return an output filename."""
    from tkinter.filedialog import asksaveasfilename

    return asksaveasfilename(
        title="Save the word cloud",
        defaultextension=".png",
        filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg;*.jpeg")],
    )


def main():
    """Run the original interactive WordCloud workflow."""
    wiki_or_file = input(
        "Do you have a text file or do you want to search about a subject?"
        "\nenter f for file or w for Wikipedia--> "
    )
    try:
        if wiki_or_file.lower() == "f":
            text_path = select_text_file()
            if not text_path:
                print("No text file was selected.")
                return 1
            text = read_text_file(text_path)
        elif wiki_or_file.lower() == "w":
            wiki = input("Enter your subject--> ")
            text = gw.wiki_get(wiki)
        else:
            print("Your answer is unknown")
            return 1
    except (OSError, UnicodeError, ImportError, gw.WikipediaLookupError) as error:
        print(f"Error: {error}")
        return 1

    text = normalize_text(text)
    if not text:
        print("Error: The selected source did not contain any usable words.")
        return 1

    mask_or_not = input(
        "Do you want the text to be in a specific photo? "
        "\nThe rule is that the photo must be black and white and in PNG format-->(y/n)"
    )
    background_color = input("What color do you want for back grand -->")
    try:
        if mask_or_not.lower() == "n":
            print("Please wait.....")
            save_path = select_save_path()
            if not save_path:
                print("No output file was selected.")
                return 1
            cloud = cw.create_cloud(text, bgcolor=background_color)
            cloud.to_file(save_path)
            plt.plot_cloud(cloud)
            mat.show()
            print("word cloud created!")
        elif mask_or_not.lower() == "y":
            mask_path = select_mask_file()
            if not mask_path:
                print("No mask image was selected.")
                return 1
            with Image.open(mask_path) as image:
                mask = np.array(image.convert("L"))
            save_path = select_save_path()
            if not save_path:
                print("No output file was selected.")
                return 1
            print("Please wait.....")
            cloud = cw.create_cloud_mask(
                text=text, bgcolor=background_color, mask=mask
            )
            cloud.to_file(save_path)
            plt.plot_cloud(cloud)
            mat.show()
            print("word cloud created!")
        else:
            print("Your answer is unknown")
            return 1
    except (OSError, ValueError, ImportError) as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
