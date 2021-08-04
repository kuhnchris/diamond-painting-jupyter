from PIL import Image, ImageFilter, ImageDraw, ImageDraw2, ImageFont, ImageOps


import matplotlib.font_manager
possibleColorValuesForAlpha = []
qModeValues = {
    "Fast Octree": Image.FASTOCTREE, 
    "Max Coverage": Image.MAXCOVERAGE, 
    "Median Cut": Image.MEDIANCUT, 
    "libImageQuant": Image.LIBIMAGEQUANT
}
rModeValues = {
    "Nearest": Image.NEAREST, 
    "Box": Image.BOX, 
    "Bilinear": Image.BILINEAR, 
    "Hamming": Image.HAMMING, 
    "Bicubic": Image.BICUBIC, 
    "Lanczos": Image.LANCZOS
}

file_types = [("Image files", ".png .jpg .jpeg"),
              ("PNG", "*.png"),
              ("JPEG", "*.jpg;*.jpeg"),
              ("All files (*.*)", "*.*")]


fontNames = list(dict.fromkeys(
    sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])))

fontVariants = []

srcResizeSizes = {
    "100%": 1,
    "50%": 0.5,
    "25%": 0.25,
    "10%": 0.1,
    "200%": 2,
    "150%": 1.5,
    "125%": 1.25,
    "Custom": -1
}
