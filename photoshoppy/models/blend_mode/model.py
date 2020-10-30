from __future__ import annotations
from typing import Callable

from photoshoppy.psd_render import blend_modes


class BlendMode:
    def __init__(self, key: str, name: str, blend_fn: Callable):
        self._key = key
        self._name = name
        self._blend_fn = blend_fn

    @property
    def key(self) -> str:
        return self._key

    @property
    def name(self) -> str:
        return self._name

    @property
    def blend_fn(self) -> Callable:
        return self._blend_fn

    @classmethod
    def from_key(cls, key: str) -> BlendMode:
        for blend_mode in ALL_BLEND_MODES:
            if blend_mode.key == key:
                return blend_mode

        raise RuntimeError(f"Could not determine blend mode from key: {key}")

    @classmethod
    def from_name(cls, name: str) -> BlendMode:
        for blend_mode in ALL_BLEND_MODES:
            if blend_mode.name == name:
                return blend_mode

        raise RuntimeError(f"Could not determine blend mode from name: {name}")


PassThrough = BlendMode("pass", "pass through", blend_modes.blend_pass_through)

Normal = BlendMode("norm", "normal", blend_modes.blend_normal)
Dissolve = BlendMode("diss", "dissolve", blend_modes.blend_dissolve)

Darken = BlendMode("dark", "darken", blend_modes.blend_darken)
Multiply = BlendMode("mul ", "multiply", blend_modes.blend_multiply)
ColorBurn = BlendMode("idiv", "color burn", blend_modes.blend_color_burn)
LinearBurn = BlendMode("lbrn", "linear burn", blend_modes.blend_linear_burn)
DarkerColor = BlendMode("dkCl", "darker color", blend_modes.blend_darker_color)

Lighten = BlendMode("lite", "lighten", blend_modes.blend_lighten)
Screen = BlendMode("scrn", "screen", blend_modes.blend_screen)
ColorDodge = BlendMode("div ", "color dodge", blend_modes.blend_color_dodge)
LinearDodge = BlendMode("lddg", "linear dodge", blend_modes.blend_linear_dodge)
LighterColor = BlendMode("lgCl", "lighter color", blend_modes.blend_lighter_color)

Overlay = BlendMode("over", "overlay", blend_modes.blend_overlay)
SoftLight = BlendMode("sLit", "soft light", blend_modes.blend_soft_light)
HardLight = BlendMode("hLit", "hard light", blend_modes.blend_hard_light)
VividLight = BlendMode("vLit", "vivid light", blend_modes.blend_vivid_light)
LinearLight = BlendMode("lLit", "linear light", blend_modes.blend_linear_light)
PinLight = BlendMode("pLit", "pin light", blend_modes.blend_pin_light)
HardMix = BlendMode("hMix", "hard mix", blend_modes.blend_hard_mix)

Difference = BlendMode("diff", "difference", blend_modes.blend_difference)
Exclusion = BlendMode("smud", "exclusion", blend_modes.blend_exclusion)
Subtract = BlendMode("fsub", "subtract", blend_modes.blend_subtract)
Divide = BlendMode("fdiv", "divide", blend_modes.blend_divide)

Hue = BlendMode("hue ", "hue", blend_modes.blend_hue)
Saturation = BlendMode("sat ", "saturation", blend_modes.blend_saturation)
Color = BlendMode("colr", "color", blend_modes.blend_color)
Luminosity = BlendMode("lum ", "luminosity", blend_modes.blend_luminosity)

ALL_BLEND_MODES = (PassThrough,
                   Normal, Dissolve,
                   Darken, Multiply, ColorBurn, LinearBurn, DarkerColor,
                   Lighten, Screen, ColorDodge, LinearDodge, LighterColor,
                   Overlay, SoftLight, HardLight, VividLight, LinearLight, PinLight, HardMix,
                   Difference, Exclusion, Subtract, Divide,
                   Hue, Saturation, Color, Luminosity)
