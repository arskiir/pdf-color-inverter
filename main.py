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
    # os.execv(sys.argv[0], sys.argv)

from utils import explore, wait_key

MAIN_FILE_PATH = os.path.abspath(__file__)
MAIN_FILE_DIR = os.path.dirname(MAIN_FILE_PATH)


def main():
    dpi = 200
    # if (
    #     input(
    #         "First time inverting, enter 1.\nInverting *back* to original color, enter 2."
    #     )
    #     == "1"
    # ):
    #     dpi = 200
    #     input(
    #         "WARNING.\n"
    #         "This converts pdf to pdf of *images*, meaning you can no longer interact with texts.\n"
    #         "Enter any key to continue.\n"
    #     )

    pdf_paths = prompt_file_path()
    targeted_file_dir = os.path.dirname(pdf_paths[0])
    os.chdir(targeted_file_dir)
    output_dir = os.path.join(targeted_file_dir, "inverted pdf(s)")
    print(f"---------> Inverting {len(pdf_paths)} pdf file(s).\n")

    # TODO use thread here
    for path in pdf_paths:
        invert_pdf(path, targeted_file_dir, output_dir, dpi)

    explore(targeted_file_dir)


def invert_pdf(pdf_path: str, targeted_file_dir: str, output_dir: str, dpi: int):
    _, file_name = os.path.split(pdf_path)
    print(f'=> Inverting "{file_name}"')
    print(">> Converting to images, this may take a while.")

    images = convert_pdf_to_images(pdf_path, dpi)
    new_file_name = file_name.split(".pdf")[0] + " (inverted).pdf"
    images_bytes = invert_images(images)
    print(">> Converting images back to pdf, this may take a while.")
    convert_images_to_pdf(images_bytes, new_file_name, output_dir)

    print(">>> " + os.path.join(targeted_file_dir, new_file_name) + "\n")


def convert_images_to_pdf(
    images_bytes: List[bytes], new_file_name: str, output_dir: str
):
    """Inverts Pillow Images and save them as a single PDF

    Args:
        images (list[bytes]): list of Pillow Images as bytes waiting to be inverted
        new_file_name (str): The new name of the output file
        output_dir (str): the output directory path
    """

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    new_file_abspath = os.path.join(output_dir, new_file_name)
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
        img.save(buffer, format="png")
        return buffer.getvalue()


def convert_pdf_to_images(file_path: str, dpi: int) -> List[Image.Image]:
    poppler_path = os.path.join(
        MAIN_FILE_DIR, "dependencies\\poppler-21.03.0\\Library\\bin"
    )
    return convert_from_path(
        file_path,
        dpi=200,
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
