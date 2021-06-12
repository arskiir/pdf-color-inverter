import io
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List

try:
    import img2pdf
    import PIL.ImageOps
    from pdf2image import convert_from_path, pdfinfo_from_path
    from PIL import Image
except ImportError:
    print("Installing dependencies")
    os.system("pip install -r requirements.txt")
    os.execv(sys.argv[0], sys.argv)

from utils import add_this_arg, explore, wait_key

MAIN_FILE_PATH = os.path.abspath(__file__)
MAIN_FILE_DIR = os.path.dirname(MAIN_FILE_PATH)

POPPLER_PATH = os.path.join(
    MAIN_FILE_DIR, "dependencies\\poppler-21.03.0\\Library\\bin"
)


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

    for pdf in pdf_paths:
        images_file_names: str = invert_pdf(pdf, output_dir, dpi)
        for file in images_file_names:
            os.remove(file)

    # if wait_key("Press F to open the output folder.").lower() == "f":
    #     explore(output_dir)


def ask_for_inversion_mode():
    dpi = 100
    selected_choice = wait_key(
        "1: First time inverting (3x the size to preserve quality).\n2: Subsequent inverting (the size is roughly the same).\n3: Quality comes first (6x the size)\n(1, 2)?: ",
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

    info = pdfinfo_from_path(pdf_path, poppler_path=POPPLER_PATH)
    images_file_names = save_extracted_images_from_pdf(pdf_path, dpi, file_name, info)
    new_file_abspath = create_output_dir(file_name, output_dir)

    print(">> Merging images back to pdf, this may take a while.")

    merge_images_to_pdf(new_file_abspath, images_file_names)
    report_after_finished(info, new_file_abspath)

    return images_file_names


def save_extracted_images_from_pdf(pdf_path, dpi, file_name, info):
    images_file_names = []
    maxPages = info["Pages"]
    count = 0
    pages_converted_once = 10
    for page in range(1, maxPages + 1, pages_converted_once):
        images: List[Image.Image] = convert_pdf_to_images(
            pdf_path,
            dpi,
            first_page=page,
            last_page=min(page + pages_converted_once - 1, maxPages),
        )
        number_of_images = len(images)
        for i, img in enumerate(images, count + 1):
            img_file_name = f"{file_name.replace('.pdf', '')} {i} (will be removed).png"
            PIL.ImageOps.invert(img).save(img_file_name, "PNG")
            images_file_names.append(img_file_name)
        count += number_of_images
        print(f"> inverted {count}/{maxPages} images")
    return images_file_names


def merge_images_to_pdf(new_file_abspath, images_file_names):
    with open(new_file_abspath, "wb") as f:
        f.write(img2pdf.convert(images_file_names))


def report_after_finished(info, new_file_abspath):
    print(">>> " + new_file_abspath)
    new_file_size = os.stat(new_file_abspath).st_size
    print(
        f">>> {new_file_size/int(info['File size'].split()[0]) * 100:.0f}% increased in file size\n"
    )


def create_output_dir(file_name, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    new_file_abspath = os.path.join(output_dir, file_name)
    return new_file_abspath


def convert_pdf_to_images(
    file_path: str, dpi: int, first_page: int, last_page: int
) -> List[Image.Image]:
    return convert_from_path(
        file_path,
        dpi=dpi,
        poppler_path=POPPLER_PATH,
        thread_count=4,
        first_page=first_page,
        last_page=last_page,
    )


def prompt_file_path() -> List[str]:
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilenames(
        title="Select the PDF file(s)", filetypes=[("PDF Files", "*.pdf")]
    )


if __name__ == "__main__":
    main()
