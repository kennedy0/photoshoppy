import os

from photoshoppy.models.errors import PSDReadError
from photoshoppy.psd_file import PSDFile


THIS_DIR = os.path.dirname(__file__)
PSD_FILES_DIR = os.path.join(THIS_DIR, "psd_files")


def main():
    for file in os.listdir(PSD_FILES_DIR):
        file_path = os.path.join(PSD_FILES_DIR, file)
        try:
            psd = PSDFile(file_path)
            psd.print_file_info()
        except PSDReadError:
            pass


if __name__ == "__main__":
    main()
