import os
import sys
from typing import List

from photoshoppy.psd_file import PSDFile
from photoshoppy.psd_render.render import render_psd


THIS_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(THIS_DIR, "renders", "render_psd")
PSD_FILE_PATH = os.path.join(THIS_DIR, "psd_files", "zig_zags.psd")
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, "zig_zags.png")


def main(files: List[str]):
    try:
        os.makedirs(OUTPUT_DIR)
    except OSError:
        pass

    try:
        os.unlink(OUTPUT_FILE_PATH)
    except OSError:
        pass

    if not len(files):
        files = [PSD_FILE_PATH]

    for file in files:
        psd = PSDFile(file)
        output_file_name = os.path.splitext(os.path.basename(file))[0] + ".png"
        output_file_path = os.path.join(OUTPUT_DIR, output_file_name)
        print(f"rendering {output_file_path}")
        render_psd(psd, output_file_path, overwrite=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
