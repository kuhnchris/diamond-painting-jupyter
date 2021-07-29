
from PIL import Image, ImageFilter, ImageDraw, ImageDraw2, ImageFont, ImageOps
import matplotlib.pyplot as plt
import numpy as np
import tempfile
from io import BytesIO

possibleColorValuesForAlpha = []
srcImg = None

def loadImage(path, maxSize):
    srcImg = Image.open(path)
    if srcImg.width > maxSize:
        srcImg = srcImg.resize((maxSize, int(maxSize*(srcImg.height/srcImg.width))),0)
    return srcImg



def alphaProcess(piximg, alphabet, alphaColor):
    pixarr = np.array(piximg)
    pixpal = {}
    pixidx = 0

    for x in pixarr:
        for a in x:
            colStr = "#{:02x}{:02x}{:02x}|{:02x}".format(a[0],a[1],a[2],a[3])
            colour = "%0.2X%0.2X%0.2X" % (a[0], a[1], a[2])
            out = "?"
            if colStr in pixpal:
                out = pixpal[colStr]
            else:
                pixpal[colStr] = str(pixidx)
                pixidx = pixidx+1
                out = pixpal[colStr]
            out = alphabet[int(out)]
            if ( a[3] == 0 ) or ( colStr == alphaColor ):
                out = " "

#    def set_image_dpi_resize(image):
#        """
#        Rescaling image to 300dpi while resizing
#        :param image: An image
#        :return: A rescaled image
#        """
#        length_x, width_y = image.size
#        factor = min(1, float(1024.0 / length_x))
#        size = int(factor * length_x), int(factor * width_y)
#        image_resize = image.resize(size, Image.ANTIALIAS)
#        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='1.png')
#        temp_filename = temp_file.name
#        image_resize.save(temp_filename, dpi=(300, 300))
#        return temp_filename
def set_image_dpi_inMemory(image):
    length_x, width_y = image.size
    factor = min(1, float(1024.0 / length_x))
    size = int(factor * length_x), int(factor * width_y)
    image_resize = image.resize(size, Image.ANTIALIAS)
    return image_resize
    #bio = BytesIO()
    #image_resize.save(bio, format="PNG")
    #return bio.getvalue()

def generateDiamondPainting(piximg, alphabet, alphaColor, font, diamondSize, roundDiamonds):
    pixarr = np.array(piximg)
    pixpal = {}
    pixidx = 0
    
    newpix = Image.new('RGB',(piximg.size[0]*diamondSize,piximg.size[1]*diamondSize))

    newpixdc = ImageDraw.Draw(newpix)
    newpixdc.rectangle((0,0,piximg.size[0]*diamondSize,piximg.size[1]*diamondSize), fill=(255,255,255))

    xcnt = 0
    ycnt = 0
    for x in pixarr:
        xcnt = 0
        for a in x:
            colStr = "#{:02x}{:02x}{:02x}|{:02x}".format(a[0],a[1],a[2],a[3])        
            colour = "%0.2X%0.2X%0.2X" % (a[0], a[1], a[2])
            out = "?"
            if colour in pixpal:
                out = pixpal[colour]
            else:
                pixpal[colour] = str(pixidx)
                pixidx = pixidx+1
                out = pixpal[colour]
            out = alphabet[int(out)]

            if ( a[3] != 0 ) and ( colStr != alphaColor ):
                invcolor = (255-a[0],255-a[1],255-a[2])
                if roundDiamonds == True:
                    newpixdc.ellipse(((xcnt*diamondSize,ycnt*diamondSize),(xcnt*diamondSize+(diamondSize),ycnt*diamondSize+diamondSize)),(a[0],a[1],a[2]),(0,0,0))
                else:
                    newpixdc.rectangle(((xcnt*diamondSize,ycnt*diamondSize),(xcnt*diamondSize+(diamondSize),ycnt*diamondSize+diamondSize)),(a[0],a[1],a[2]),(0,0,0))
                newpixdc.text((xcnt*diamondSize+(diamondSize/2),ycnt*diamondSize+(diamondSize/2)),out,invcolor,font=font,anchor="mm")


            xcnt = xcnt + 1
        ycnt = ycnt + 1

    return set_image_dpi_inMemory(newpix)

def generateFontPreview(font):
    newpix = Image.new('RGB',(100,40))
    newpixdc = ImageDraw.Draw(newpix)
    newpixdc.rectangle((0,0,newpix.width, newpix.height), fill=(255,255,255))
    newpixdc.text((int(newpix.width/2), int(newpix.height/2)),"Example",(0,0,0),font=font,anchor="mm")
    return newpix

def pixelate(image, pixel_size, resizeMode):
    image = image.resize(
        (image.size[0] // pixel_size, image.size[1] // pixel_size),
        resizeMode
    ) 
    image = image.resize(
        (image.size[0] * pixel_size, image.size[1] * pixel_size),
        resizeMode
    )
    return image
 
def convertImage(inputImg, qmethod, colorAmount):
    #if param_fixedPalette.value:
    #    palettedata =  [255,255,255,93,143,241,233,136,56,239,148,84 ]
    #    while len(palettedata) < 768:
    #        palettedata.append(0)
    #        palettedata.append(0)
    #        palettedata.append(0)
    #    palimage = Image.new('P', (12, 12))
    #    palimage.putpalette(palettedata)
    #    piximg = piximg.quantize(method=param_quantMode.value, colors=u.value, dither=Image.NONE, palette=palimage)
    #else:
    piximg = inputImg.quantize(method=qmethod,dither=0,colors=colorAmount,kmeans=1)

    piximg = piximg.convert("RGBA")
    na = np.array(piximg) 
    colours, counts = np.unique(na.reshape(-1,4), axis=0, return_counts=1)    
    possibleColorValuesForAlpha.clear()
    possibleColorValuesForAlpha.append("None")
    for a in colours:
        colour = "%0.2X%0.2X%0.2X" % (a[0], a[1], a[2])
        colStr = "#{:02x}{:02x}{:02x}|{:02x}".format(a[0],a[1],a[2],a[3])
        possibleColorValuesForAlpha.append(colStr)
    return piximg
    