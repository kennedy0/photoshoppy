from typing import Callable

import numpy as np

from .compositing import *


def blend(blend_fn: Callable) -> np.array:
    """ Decorator function for handling blend modes. """
    def bm(fg: np.array, bg: np.array, mask: np.array or None, fg_opacity: float):
        # Normalize uint8 numbers to a 0-1 floating point range.
        fg = uint8_to_float(fg)
        bg = uint8_to_float(bg)

        if mask is not None:
            mask = uint8_to_float(mask)
        else:
            mask = np.ones((fg.shape[0], fg.shape[1]), dtype=np.float64)

        def over(src_rgba, dst_rgba):
            """ Porter/Duff Over operator, using the blend mode for the "both" color.
            This was super helpful: http://ssp.impulsetrain.com/porterduff.html
            """
            src_rgb = src_rgba[:, :, :3]
            dst_rgb = dst_rgba[:, :, :3]
            src_alpha = src_rgba[:, :, 3] * fg_opacity * mask
            dst_alpha = dst_rgba[:, :, 3]

            src = src_rgb
            dst = dst_rgb
            both = blend_fn(src_rgb, dst_rgb)

            # Area of coverage
            area_src = src_alpha * (1 - dst_alpha)
            area_dst = dst_alpha * (1 - src_alpha)
            area_both = src_alpha * dst_alpha

            # Result rgb is effectively a blend + premultiplication
            result_rgb = area_src[:, :, None] * src + area_dst[:, :, None] * dst + area_both[:, :, None] * both
            result_alpha = area_src + area_dst + area_both

            # Combine / unpremultiply result
            result = np.dstack([result_rgb, result_alpha])
            result = unpremultiply(result)
            return result

        color = over(fg, bg)

        return float_to_uint8(color)

    return bm


@blend
def blend_pass_through(fg: np.array, bg: np.array) -> np.array:
    raise NotImplementedError


@blend
def blend_normal(fg: np.array, bg: np.array) -> np.array:
    return fg


def blend_dissolve(fg: np.array, bg: np.array, fg_opacity: float, mask) -> np.array:
    """ Dissolve is weird, so it does not use the blend decorator. """
    raise NotImplementedError
    # Normalize uint8 numbers to a 0-1 floating point range.
    fg = uint8_to_float(fg)
    bg = uint8_to_float(bg)

    # Separate rgb and alpha channels
    fg_rgb = fg[:, :, :3]
    bg_rgb = bg[:, :, :3]
    fg_alpha = fg[:, :, 3]
    bg_alpha = bg[:, :, 3]

    # Scale fg alpha by layer opacity
    # ToDo: Scale by fill, too
    fg_alpha *= fg_opacity

    # Create random alpha mask
    dissolve_mask = np.random.rand(fg_alpha.shape[0], fg_alpha.shape[1])
    dissolve_alpha = np.where(fg_alpha > dissolve_mask, 1, 0)

    # Calculate alpha
    alpha = dissolve_alpha + bg_alpha - (dissolve_alpha * bg_alpha)

    # Composite new fg over bg
    rgb = alpha_blend(fg_rgb, bg_rgb, dissolve_alpha, bg_alpha)
    rgba = np.dstack([rgb, alpha])

    # Convert back to uint8
    color = float_to_uint8(rgba)
    return color


@blend
def blend_darken(fg: np.array, bg: np.array) -> np.array:
    return np.minimum(fg, bg)


@blend
def blend_multiply(fg: np.array, bg: np.array) -> np.array:
    return fg * bg


@blend
def blend_color_burn(fg: np.array, bg: np.array) -> np.array:
    with IgnoreNumpyErrors():
        color_burn = 1 - clamp((1 - bg) / fg)
        color = np.where(bg == 1, bg,
                         np.where(fg == 0, fg, color_burn))
    return color


@blend
def blend_linear_burn(fg: np.array, bg: np.array) -> np.array:
    linear_burn = fg + bg - 1
    color = np.where(fg + bg < 1, 0, linear_burn)
    return color


@blend
def blend_darker_color(fg: np.array, bg: np.array) -> np.array:
    mask = get_luminosity(fg) < get_luminosity(bg)
    color = np.where(mask[:, :, None], fg, bg)
    return color


@blend
def blend_lighten(fg: np.array, bg: np.array) -> np.array:
    return np.maximum(fg, bg)


@blend
def blend_screen(fg: np.array, bg: np.array) -> np.array:
    return 1 - ((1 - bg) * (1 - fg))


@blend
def blend_color_dodge(fg: np.array, bg: np.array) -> np.array:
    with IgnoreNumpyErrors():
        color_dodge = clamp(bg / (1 - fg))
        color = np.where(bg == 0, 0,
                         np.where(fg == 1, 1, color_dodge))
    return color


@blend
def blend_linear_dodge(fg: np.array, bg: np.array) -> np.array:
    return clamp(fg + bg)


@blend
def blend_lighter_color(fg: np.array, bg: np.array) -> np.array:
    mask = get_luminosity(fg) > get_luminosity(bg)
    color = np.where(mask[:, :, None], fg, bg)
    return color


@blend
def blend_overlay(fg: np.array, bg: np.array) -> np.array:
    multiply = 2 * fg * bg
    screen = 1 - (2 * ((1 - fg) * (1 - bg)))
    color = np.where(bg < 0.5, multiply, screen)
    return color


@blend
def blend_soft_light(fg: np.array, bg: np.array) -> np.array:
    dark = bg - (1 - 2 * fg) * bg * (1 - bg)
    light = bg + (2 * fg - 1) * ((4 * bg) * (4 * bg + 1) * (bg - 1) + 7 * bg)
    light_less = bg + (2 * fg - 1) * (np.power(bg, 0.5) - bg)
    color = np.where(fg <= 0.5, dark,
                     np.where(bg <= 0.25, light, light_less))
    return color


@blend
def blend_hard_light(fg: np.array, bg: np.array) -> np.array:
    multiply = 2 * fg * bg
    screen = 1 - (2 * ((1 - fg) * (1 - bg)))
    color = np.where(fg <= 0.5, multiply, screen)

    return color


@blend
def blend_vivid_light(fg: np.array, bg: np.array) -> np.array:
    # Scale FG to cover half ranges
    burn_fg = clamp(2 * fg)
    dodge_fg = clamp(2 * (fg - 0.5))

    with IgnoreNumpyErrors():
        color_burn = 1 - clamp((1 - bg) / burn_fg)
        color_dodge = bg / (1 - dodge_fg)

        color = np.where(fg == 1, fg,
                         np.where(fg == 0, fg,
                                  np.where(fg <= 0.5, clamp(color_burn), clamp(color_dodge))))
    return color


@blend
def blend_linear_light(fg: np.array, bg: np.array) -> np.array:
    # Scale FG to cover half ranges
    burn_fg = clamp(2 * fg)
    dodge_fg = clamp(2 * (fg - 0.5))

    with IgnoreNumpyErrors():
        linear_burn = burn_fg + bg - 1
        linear_dodge = clamp(dodge_fg + bg)

        color = np.where(fg <= 0.5, clamp(linear_burn), clamp(linear_dodge))

    return color


@blend
def blend_pin_light(fg: np.array, bg: np.array) -> np.array:
    # Scale FG to cover half ranges
    darken_fg = clamp(2 * fg)
    lighten_fg = clamp(2 * (fg - 0.5))

    with IgnoreNumpyErrors():
        darken = np.minimum(darken_fg, bg)
        lighten = np.maximum(lighten_fg, bg)
        color = np.where(fg <= 0.5, clamp(darken), clamp(lighten))

    return color


@blend
def blend_hard_mix(fg: np.array, bg: np.array) -> np.array:
    # ToDo: This isn't a perfect match
    # This method yields false-positives that Photoshop would otherwise ignore
    fg2 = np.round(fg, 3)
    bg2 = np.round(bg, 3)
    color = np.where(bg == 0, 0,
                     np.where(fg2 + bg2 >= 1, 1, 0))
    return color


@blend
def blend_difference(fg: np.array, bg: np.array) -> np.array:
    return np.abs(fg - bg)


@blend
def blend_exclusion(fg: np.array, bg: np.array) -> np.array:
    return clamp((fg + bg) - (2 * fg * bg))


@blend
def blend_subtract(fg: np.array, bg: np.array) -> np.array:
    return clamp(bg - fg)


@blend
def blend_divide(fg: np.array, bg: np.array) -> np.array:
    with IgnoreNumpyErrors():
        color = np.where(bg == 0, 0,
                         np.where(fg == 0, 1, clamp(bg / fg)))
    return color


@blend
def blend_hue(fg: np.array, bg: np.array) -> np.array:
    return set_luminosity(set_saturation(fg, get_saturation(bg)), get_luminosity(bg))


@blend
def blend_saturation(fg: np.array, bg: np.array) -> np.array:
    return set_luminosity(set_saturation(bg, get_saturation(fg)), get_luminosity(bg))


@blend
def blend_color(fg: np.array, bg: np.array) -> np.array:
    return set_luminosity(fg, get_luminosity(bg))


@blend
def blend_luminosity(fg: np.array, bg: np.array) -> np.array:
    return set_luminosity(bg, get_luminosity(fg))

