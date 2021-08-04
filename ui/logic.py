
from PIL import Image, ImageFilter, ImageDraw, ImageDraw2, ImageFont, ImageOps
import matplotlib.pyplot as plt
import numpy as np
import tempfile
from io import BytesIO

possibleColorValuesForAlpha = []
srcImg = None

def loadImage(path, maxSize):
    srcImg = Image.open(path)
    if srcImg.width > maxSize and maxSize > 0:
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

def generateLetterImage(letter, color, roundShape, diamondSize,font):
    newpix = Image.new('RGBA',(diamondSize,diamondSize))
    newpixdc = ImageDraw.Draw(newpix)
    newpixdc.rectangle((0,0,diamondSize,diamondSize), fill=(255,255,255))
    invcolor = (255-color[0],255-color[1],255-color[2])
    if roundShape == True:
        newpixdc.ellipse(((0,0),(diamondSize,diamondSize)),(color[0],color[1],color[2]),(0,0,0))
    else:
        newpixdc.rectangle(((0,0),(diamondSize,diamondSize)),(color[0],color[1],color[2]),(0,0,0))
    newpixdc.text((0+(diamondSize/2),0+(diamondSize/2)),letter,invcolor,font=font,anchor="mm")
    return newpix
    
pixpal = {}
alphabetPregen = {}
def generateDiamondPainting(piximg, alphabet, alphaColor, font, diamondSize, roundDiamonds):
    pixarr = np.array(piximg)
    #pixpal = {}
    pixpal.clear()
    pixidx = 0
    
    newpix = Image.new('RGB',(piximg.size[0]*diamondSize,piximg.size[1]*diamondSize))

    newpixdc = ImageDraw.Draw(newpix)
    newpixdc.rectangle((0,0,piximg.size[0]*diamondSize,piximg.size[1]*diamondSize), fill=(255,255,255))

    #alphabetPregen = {}
    alphabetPregen.clear()
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

            if out in alphabetPregen:
                outImg = alphabetPregen[out]
            else:
                alphabetPregen[out] = generateLetterImage(out,a,roundDiamonds,diamondSize,font)
                outImg = alphabetPregen[out]

            if ( a[3] != 0 ) and ( colStr != alphaColor ):
                #newpix.paste(outImg,box=(xcnt*diamondSize,ycnt*diamondSize,xcnt*diamondSize+diamondSize,ycnt*diamondSize+diamondSize))
                newpix.paste(outImg,box=(xcnt*diamondSize,ycnt*diamondSize))

            xcnt = xcnt + 1
        ycnt = ycnt + 1

    return set_image_dpi_inMemory(newpix)

def autocrop(image):
    image_data = np.asarray(image)
    image_data_bw = image_data.max(axis=2)
    non_empty_columns = np.where(image_data_bw.min(axis=0)<255)[0]
    non_empty_rows = np.where(image_data_bw.min(axis=1)<255)[0]
    cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

    image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]

    new_image = Image.fromarray(image_data_new)
    return new_image


def generateTable(fnt, alphabet, diamShapSize):
    tabDim = (1000,1000)
    newpix = Image.new('RGBA',tabDim)
    newpixdc = ImageDraw.Draw(newpix)
    newpixdc.rectangle((0,0,tabDim[0],tabDim[1]), fill=(255,255,255))

    xWidth = 200
    xLeft = diamShapSize + 5
    yPos = 0
    yHeight = diamShapSize + 5

    newpixdc.rectangle((0,yPos,xWidth,yPos+yHeight),fill=None,outline=(0,0,0))
    newpixdc.rectangle((0,yPos,xLeft,yPos+yHeight),fill=None,outline=(0,0,0))
    newpixdc.text((10,10),"@",(0,0,0),font=fnt,anchor="mm")
    newpixdc.text((xLeft+4,10),"Color Code",(0,0,0),font=fnt,anchor="lm")

    yPos = yPos + yHeight
    for colour in pixpal:
        a=(int(colour[0:2],16),int(colour[2:4],16),int(colour[4:6],16))
        invcolor = (255-a[0],255-a[1],255-a[2])
        newpixdc.rectangle((0,yPos,xWidth,yPos+yHeight),fill=None,outline=(0,0,0))
        newpixdc.rectangle((0,yPos,xLeft,yPos+yHeight),fill="#"+colour,outline=(0,0,0))
        #newpixdc.text((10,yPos+yHeight/2),pixlit[int(pixpal[colour])],invcolor,font=fnt,anchor="mm")

        out = pixpal[colour]
        out = alphabet[int(out)]

        if out in alphabetPregen:
            outImg = alphabetPregen[out]
        newpix.paste(outImg,box=(0,int(yPos)))

        newpixdc.text((xLeft+4,yPos+yHeight/2),"#"+colour,(0,0,0),font=fnt,anchor="lm")
        yPos = yPos + yHeight
    newpix = autocrop(newpix)
    return newpix

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
    