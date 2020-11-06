from typing import BinaryIO

from .layer_info_blocks import *
from .model import LayerInfo, TempLayerInfo
from photoshoppy.utilities.string import unpack_string


dispatch_table = {
    'SoCo': "Solid Color",
    'GdFl': "Gradient",
    'PtFl': "Pattern",
    'brit': "Brightness/Contrast",
    'levl': "Levels",
    'curv': "Curves",
    'expA': "Exposure",
    'vibA': "Vibrance",
    'hue ': "Old Hue/saturation, Photoshop 4.0",
    'hue2': "New Hue/saturation, Photoshop 5.0",
    'blnc': "Color Balance",
    'blwh': "Black and White",
    'phfl': "Photo Filter",
    'mixr': "Channel Mixer",
    'clrL': "Color Lookup",
    'nvrt': "Invert",
    'post': "Posterize",
    'thrs': "Threshold",
    'grdm': "Gradient Map",
    'selc': "Selective color",
    'lrFX': "Effects Layer",
    'TySh': "Type Tool (Old)",
    'tySh': "Type Tool",
    'luni': "Type Tool",
    'lyid': "Layer ID",
    'lfx2': "Object-based Effects Layer",
    'Patt': "Pattern",
    'Pat2': "Pattern 2",
    'Pat3': "Pattern 3",
    'Anno': "Annotations",
    'clbl': "Blend Clipping Elements",
    'infx': "Blend Interior Elements",
    'knko': "Knockout",
    'lspf': "Protection",
    'lclr': "Sheet Color",
    'fxrp': "Reference Point",
    'lsct': SectionDivider,
    'brst': "Channel Blending Restrictions",
    'vmsk': "Vector Mask",
    'vsms': "Vector Mask, Photoshop CS6",
    'ffxi': "Foreign Effect ID",
    'lnsr': "Layer Name Source",
    'shpa': "Pattern Data",
    'shmd': "Metadata",
    'lyvr': "Layer Version",
    'tsly': "Transparency Shapes Layer",
    'lmgm': "Layer Mask as Global Mask",
    'vmgm': "Vector Mask as Global Mask",
    'plLd': "Placed Layer",
    'lnkD': "Linked Layer",
    'lnk2': "Linked Layer",
    'lnk3': "Linked Layer",
    'CgEd': "Content Generator Extra Data",
    'Txt2': "Text Engine Data",
    'pths': "Unicode Path Name",
    'anFX': "Animation Effects",
    'FMsk': "Filter Mask",
    'SoLd': "Placed Layer Data",
    'vstk': "Vector Stroke Data",
    'vscg': "Vector Stroke Content Data",
    'sn2P': "Using Aligned Rendering",
    'vogk': "Vector Origination Data",
    'PxSc': "Pixel Source Data",
    'cinf': "Compositor Used",
    'PxSD': "Pixel Source Data",
    'artb': "Artboard Data",
    'artd': "Artboard Data",
    'abdd': "Artboard Data",
    'SoLE': "Smart Object Layer Data",
    'Mtrn': "Saving Merged Transparency",
    'Mt16': "Saving Merged Transparency",
    'Mt32': "Saving Merged Transparency",
    'LMsk': "User Mask",
    'FXid': "Filter Effects",
    'FEid': "Filter Effects",
}


def read_layer_info(file: BinaryIO) -> LayerInfo:
    unpack_string(file.read(4), length=4)  # Signature: 8BIM or 8B64
    key = unpack_string(file.read(4), length=4)
    layer_info_class = dispatch_table.get(key)  # type: LayerInfo
    if type(layer_info_class) == str:
        layer_info = TempLayerInfo(key, layer_info_class, file)
    else:
        layer_info = layer_info_class.read_section(file)
    return layer_info
