import os
import subprocess
from typing import List

if os.name == "nt":
    import msvcrt
else:
    import termios

FILEBROWSER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")


def combine_pdfs(pdf_list: List[str]) -> None:
    # TODO converts 10 pages at a time to not monopolize the poor RAM
    # see https://stackoverflow.com/questions/3444645/merge-pdf-files
    # https://stackoverflow.com/questions/56471728/how-to-solve-memoryerror-using-python-3-7-pdf2image-library
    # We have to split the pdfs and combine it.
    # We cannot save all the images
    return


def explore(path):
    # explorer would choke on forward slashes
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, "/select,", os.path.normpath(path)])


def wait_key(prompt=None, end="\n"):
    """Wait for a key press on the console and return it as str type."""

    if prompt:
        print(prompt, end=end)

    result = None
    if os.name == "nt":
        result = msvcrt.getch()
    else:
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result if type(result) == str else result.decode("utf-8")


def add_this_arg(func):
    def wrapped(*args, **kwargs):
        return func(wrapped, *args, **kwargs)

    return wrapped
