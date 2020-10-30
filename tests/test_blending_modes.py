import os
import shutil

from PIL import Image, ImageChops, ImageDraw

from photoshoppy.models.blend_mode.model import BlendMode, ALL_BLEND_MODES
from photoshoppy.psd_file import PSDFile
from photoshoppy.psd_render import render_utils

THIS_DIR = os.path.dirname(__file__)
BLENDING_MODES_DIR = os.path.join(THIS_DIR, "renders", "blending_modes")
FROM_PHOTOSHOP_DIR = os.path.join(BLENDING_MODES_DIR, "from_photoshop")
FROM_PHOTOSHOPPY_DIR = os.path.join(BLENDING_MODES_DIR, "from_photoshoppy")
SIDE_BY_SIDE_DIR = os.path.join(BLENDING_MODES_DIR, "side_by_side")
PSD_FILE_PATH = os.path.join(THIS_DIR, "psd_files", "lena.psd")

psd = PSDFile(PSD_FILE_PATH)


def clean_folder(path: str):
    if not os.path.isdir(path):
        return

    print(f"cleaning {path}")
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isfile(full_path):
            os.unlink(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)


def render_all_blending_modes():
    try:
        os.makedirs(FROM_PHOTOSHOPPY_DIR)
    except OSError:
        pass

    for blend in ALL_BLEND_MODES:
        file_name = blend.name.replace(" ", "_") + ".png"
        output_path = os.path.join(FROM_PHOTOSHOPPY_DIR, file_name)
        try:
            render_blending_mode(output_path, blend)
        except NotImplementedError:
            print(f"{blend.name} not implemented")


def render_blending_mode(file_path: str, blend: BlendMode):
    print(f"rendering {file_path}")
    fg = render_utils.layer_to_screen_space(psd.layer("colors"), psd)
    bg = render_utils.layer_to_screen_space(psd.layer("lena"), psd)
    image_data = blend.blend_fn(fg=fg, bg=bg, fg_opacity=1.0)
    image = Image.fromarray(image_data, mode="RGBA")
    image.save(file_path)


def render_comparisons():
    for file in os.listdir(FROM_PHOTOSHOPPY_DIR):
        output_image = os.path.join(FROM_PHOTOSHOPPY_DIR, file)
        photoshop_image = os.path.join(FROM_PHOTOSHOP_DIR, file)
        if os.path.isfile(photoshop_image):
            sbs_path = os.path.join(SIDE_BY_SIDE_DIR, file)
            render_sbs(sbs_path, left_image=photoshop_image, right_image=output_image)


def render_sbs(file_path: str, left_image: str, right_image: str):
    print(f"Rendering side-by-side: {file_path} ...")
    img_l = Image.open(left_image)
    img_r = Image.open(right_image)
    img_diff = ImageChops.difference(img_l.convert("RGB"), img_r.convert("RGB"))
    left_w, left_h = img_l.size
    right_w, right_h = img_r.size
    if left_w != right_w:
        raise RuntimeError("Images are not the same size")

    text_margin = 50
    header = text_margin * 2
    width = left_w * 3 + 2
    height = left_h + text_margin * 2

    img = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(img)

    img.paste(img_l, (0, header))
    img.paste(img_r, (left_w + 1, header))
    img.paste(img_diff, (left_w * 2 + 2, header))

    draw.text(((left_w * 0) + text_margin, text_margin), "From Photoshop")
    draw.text(((left_w * 1) + text_margin, text_margin), "From PhotoshopPy")
    draw.text(((left_w * 2) + text_margin, text_margin), "Difference")

    draw.line((left_w * 1 + 0, 0, left_w * 1 + 0, height), fill=(255, 255, 255))
    draw.line((left_w * 2 + 1, 0, left_w * 2 + 1, height), fill=(255, 255, 255))
    img.save(file_path)


def main():
    clean_folder(FROM_PHOTOSHOPPY_DIR)
    clean_folder(SIDE_BY_SIDE_DIR)
    render_all_blending_modes()
    render_comparisons()
    pass


if __name__ == "__main__":
    main()
