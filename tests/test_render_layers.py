import os
import shutil

from photoshoppy.psd_file import PSDFile
from photoshoppy.psd_render.render import render_layers


THIS_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(THIS_DIR, "renders", "render_layers")
PSD_FILE_PATH = os.path.join(THIS_DIR, "psd_files", "zig_zags.psd")


def main():
    try:
        shutil.rmtree(OUTPUT_DIR)
    except OSError:
        pass

    try:
        os.makedirs(OUTPUT_DIR)
    except OSError:
        pass

    psd = PSDFile(PSD_FILE_PATH)
    print(f"rendering layers to {OUTPUT_DIR}")
    for layer in psd.layers:
        print(f"- {layer.name} {'' if layer.visible is True else '(Hidden)'}")
    render_layers(psd, OUTPUT_DIR, overwrite=True, skip_hidden_layers=False)


if __name__ == "__main__":
    main()
