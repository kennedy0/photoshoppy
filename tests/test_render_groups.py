import os
import shutil
import sys
from typing import List

from photoshoppy.psd_file import PSDFile
from photoshoppy.psd_render.render import render_groups


THIS_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(THIS_DIR, "renders", "render_groups")
PSD_FILE_PATH = os.path.join(THIS_DIR, "psd_files", "rings.psd")


def main(files: List[str]):
    try:
        shutil.rmtree(OUTPUT_DIR)
    except OSError:
        pass

    try:
        os.makedirs(OUTPUT_DIR)
    except OSError:
        pass

    if not len(files):
        files = [PSD_FILE_PATH]

    for file in files:
        psd = PSDFile(file)
        print(f"rendering groups to {OUTPUT_DIR}")
        for group in psd.iter_groups():
            print(f"- {group.name} {'' if group.visible is True else '(Hidden)'}")
        render_groups(psd, OUTPUT_DIR, overwrite=True, skip_hidden_groups=False, render_masks=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
