import os

from photoshoppy.psd_file import PSDFile
from photoshoppy.psd_render.render import render_psd


THIS_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(THIS_DIR, "renders", "render_psd")
PSD_FILE_PATH = os.path.join(THIS_DIR, "psd_files", "zig_zags.psd")
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, "zig_zags.png")


def main():
    try:
        os.makedirs(OUTPUT_DIR)
    except OSError:
        pass

    try:
        os.unlink(OUTPUT_FILE_PATH)
    except OSError:
        pass

    psd = PSDFile(PSD_FILE_PATH)
    print(f"rendering {OUTPUT_FILE_PATH}")
    render_psd(psd, OUTPUT_FILE_PATH, overwrite=True)


if __name__ == "__main__":
    main()
