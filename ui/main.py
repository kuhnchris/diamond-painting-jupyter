import string
import PySimpleGUI as sg
import sys
from io import BytesIO
import ui_screens
import logic
import logging
from PIL import ImageFont
import matplotlib.font_manager

logging.basicConfig(level=logging.DEBUG)
maxSize = 600
srcImg = None
scaledImg = None
selectedFnt = None
window = sg.Window(title="Diamondificator", layout=ui_screens.layout, margins=(5, 5))
while True:
    try:
        #set variables
        forceRepixel = False

        # wait for event
        evt, vals = window.read()
        logging.debug(("Event: %s - Values: %s" % (evt, vals)))
        
        # close event
        if evt == "Exit" or evt == sg.WIN_CLOSED:
            logging.info("Quitting...")
            break
 
        # update texts beside sliders
        window["fontSizeDisplay"].update(value=int(vals['fontSize']))
        window["diamondSizeDisplay"].update(value=int(vals['diamondSize']))
        window["pixelSizeDisplay"].update(value=int(vals['pixelSize']))
        window["colorAmountDisplay"].update(value=int(vals['colorAmount']))

        # update font path/name
        if evt == "fontSelect":
            for f in matplotlib.font_manager.fontManager.ttflist:
                if f.name == vals["fontSelect"]:
                    window["fontName"].update(f.fname)
                    vals["fontName"] = f.fname
 
        # react on image load
        if evt == "srcImg":
            logging.info("Loading image: %s " % vals["srcImg"])
            srcImg = logic.loadImage(vals["srcImg"],maxSize)
            if vals["alwaysRGB"]:
                srcImg = srcImg.convert("RGB")
            forceRepixel = True

        # font preview        
        if evt == "fontSize" or evt == "fontSelect":
            selectedFnt = ImageFont.truetype(vals["fontName"], int(vals["fontSize"]))
            bio = BytesIO()
            logic.generateFontPreview(selectedFnt).save(bio, format="PNG")
            window["previewText"].update(data=bio.getvalue())

        # --- END IF NO SOURCE IMAGE LOADED ---
        if srcImg == None:
            logging.info("Source Image is empty, bailing...")
            continue
        
        # convert RGBA->RGB
        if evt == "alwaysRGB":
            logging.info("RGB(A) flag changed, processing...")
            if vals["alwaysRGB"]:
                srcImg = srcImg.convert("RGB")
            else:
                srcImg = logic.loadImage(vals["srcImg"],maxSize)
            forceRepixel = True
        
        # resize canvas
        if evt == "pixelSize" or evt == "rMode" or forceRepixel == True:
            scaledImg = logic.pixelate(srcImg, int(vals["pixelSize"]),ui_screens.ui_constants.rModeValues[vals["rMode"]])
            forceRepixel = False

        img = logic.convertImage(scaledImg,ui_screens.ui_constants.qModeValues[vals["qMode"]],int(vals["colorAmount"]))        
        if evt == "generate":
            img = logic.generateDiamondPainting(img,vals["diamondAlphabet"],vals["alphaValue"],selectedFnt,int(vals["diamondSize"]),vals["diamondShape"]=="Round")

        bio = BytesIO()
        img.save(bio, format="PNG")
        window["previewImg"].update(data=bio.getvalue())
        window["alphaValue"].update(values=logic.possibleColorValuesForAlpha)

    except Exception as e:
        print(sys.exc_info()[0])
        sg.PopupQuickMessage(e)

window.close()