import io
import os
import sys
import tkinter as tk
from tkinter import filedialog
from typing import List

try:
    import img2pdf
    import PIL.ImageOps
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError:
    print("Installing dependencies")
    os.system("pip install -r requirements.txt")
    os.execv(sys.argv[0], sys.argv)

from utils import explore, wait_key

MAIN_FILE_PATH = os.path.abspath(__file__)
MAIN_FILE_DIR = os.path.dirname(MAIN_FILE_PATH)

# TODO converts 10 pages at a time to not monopolize the poor RAM

def main():
    os.system("title PDF-ColorInverter")
    print(
        "Disclaimer.\n"
        "The output pdf will be a pdf of images only.\n"
        "The texts and other things will become uninteractive.\n"
        'Not recommended to "chain" the inversion as file sizes will get bigger and bigger.\n'
    )
    dpi = ask_for_inversion_mode()
    pdf_paths = prompt_file_path()
    targeted_file_dir = os.path.dirname(pdf_paths[0])
    os.chdir(targeted_file_dir)
    output_dir = os.path.join(os.getcwd(), "inverted pdf(s)")
    print(f"---------> Inverting {len(pdf_paths)} pdf file(s).\n")

    # TODO use thread here
    for pdf in pdf_paths:
        invert_pdf(pdf, output_dir, dpi)

    if wait_key("Press F to open the output folder.").lower() == "f":
        explore(output_dir)


def ask_for_inversion_mode():
    dpi = 100
    selected_choice = wait_key(
        "1: First time inverting (3x the size to preserve quality).\n2: Subsequent inverting (the size is roughly the same).\n3: HigH QuaLIty IS mY thinG. yolo\n(1, 2)?: ",
        end="",
    )
    print(selected_choice + "\n")
    if selected_choice == "1":
        dpi = 200
    elif selected_choice == "3":
        dpi = 300
    return dpi


def invert_pdf(pdf_path: str, output_dir: str, dpi: int):
    _, file_name = os.path.split(pdf_path)
    print(f'=> Inverting "{file_name}"')
    print(">> Converting to images, this may take a while.")

    images: List[Image.Image] = convert_pdf_to_images(pdf_path, dpi)
    images_bytes = invert_images(images)
    print(">> Converting images back to pdf, this may take a while.")
    convert_images_to_pdf(images_bytes, file_name, output_dir)

    print(">>> " + os.path.join(output_dir, file_name) + "\n")


def convert_images_to_pdf(
    images_bytes: List[bytes], file_name: str, output_dir: str
):
    """Inverts Pillow Images and save them as a single PDF

    Args:
        images (list[bytes]): list of Pillow Images as bytes waiting to be inverted
        file_name (str): The new name of the output file
        output_dir (str): the output directory path
    """

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    new_file_abspath = os.path.join(output_dir, file_name)
    with open(new_file_abspath, "wb") as f:
        f.write(img2pdf.convert(images_bytes))


def invert_images(images: List[Image.Image]):
    """Inverts color of the images and converts them to bytes

    Args:
        images (List[Image.Image]): list of PIL images

    Returns:
        List[bytes]: list of bytes of inverted images
    """

    images_bytes = []
    number_of_images = len(images)

    # TODO use thread here, we can store the bytes results from threads in a dict then use a loop to only append them to images_bytes list
    for i, image in enumerate(images, 1):
        inverted_image = PIL.ImageOps.invert(image)  # 300-dpi A4 size
        print(f"> inverted {i}/{number_of_images} images")
        images_bytes.append(get_bytes(inverted_image))
    return images_bytes


def get_bytes(img: Image.Image):
    with io.BytesIO() as buffer:
        img.save(
            buffer,
            format="png",
        )
        return buffer.getvalue()


def convert_pdf_to_images(file_path: str, dpi: int) -> List[Image.Image]:
    poppler_path = os.path.join(
        MAIN_FILE_DIR, "dependencies\\poppler-21.03.0\\Library\\bin"
    )
    return convert_from_path(
        file_path,
        dpi=dpi,
        poppler_path=poppler_path,
        thread_count=4,
    )


def prompt_file_path() -> List[str]:
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilenames(
        title="Select the PDF file(s)", filetypes=[("PDF Files", "*.pdf")]
    )


if __name__ == "__main__":
    main()
