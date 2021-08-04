import json
import string
import traceback
import PySimpleGUI as sg
import sys
from io import BytesIO
import ui_screens
import logic
import logging
from PIL import ImageFont
import matplotlib.font_manager


settings = sg.UserSettings()
logging.basicConfig(level=logging.DEBUG)
maxSize = 600
srcImg = None
scaledImg = None
pixelImg = None
selectedFnt = None
window = sg.Window(title="Diamondificator",
                   layout=ui_screens.layout, margins=(5, 5))
while True:
    try:
        # set variables
        forceRepixel = False

        # wait for event
        evt, vals = window.read()
        logging.debug(("Event: %s - Values: %s" % (evt, vals)))

        # close event
        if evt == "Exit" or evt == sg.WIN_CLOSED:
            logging.info("Quitting...")
            break

        if evt == "Save":
            fnam = sg.popup_get_file('Where to save to?', 'Save configuration', default_extension='*.json')
            jsave = json.dump(vals,open(fnam,'w'))            
    
        if evt == "Open":
            fnam = sg.popup_get_file('Choose file to load', 'Load configuration', default_extension='*.json')
            jload = json.load(open(fnam,'r'))


        # update texts beside sliders
        window["fontSizeDisplay"].update(value=int(vals['fontSize']))
        window["diamondSizeDisplay"].update(value=int(vals['diamondSize']))
        window["pixelSizeDisplay"].update(value=int(vals['pixelSize']))
        window["colorAmountDisplay"].update(value=int(vals['colorAmount']))

        # update font path/name
        if evt == "fontSelect":
            variantList = {}
            for f in matplotlib.font_manager.fontManager.ttflist:
                if f.name == vals["fontSelect"]:
                    window["fontName"].update(f.fname)
                    vals["fontName"] = f.fname
                    fName = "%s %s %s" % (f.name,f.style,str(f.weight))
                    variantList[fName] = f.fname
            window["fontVariant"].update(values=list(variantList))

        if evt == "fontVariant":
            window["fontName"].update(variantList[vals["fontVariant"]])
            vals["fontName"] = (variantList[vals["fontVariant"]])
            
        # react on image load
        if (evt == "srcImg" or evt == "srcImgResize" or evt == "srcImgResizePercent" or evt == "srcImgResizeIgnoreRatio" or evt == "srcImgCustomWidth" or evt == "srcImgCustomHeight" or evt == "srcImgCustomSizeRation" or evt == "rModeInput") and vals["srcImg"] != "":
            logging.info("Loading image: %s " % vals["srcImg"])
            srcImg = logic.loadImage(vals["srcImg"], -1)
            if vals["alwaysRGB"]:
                srcImg = srcImg.convert("RGB")
            if vals["srcImgResize"]:
                resizeFac = ui_screens.ui_constants.srcResizeSizes[vals["srcImgResizePercent"]]
                srcImg = srcImg.resize((int(srcImg.width*resizeFac), int(srcImg.height * resizeFac)), ui_screens.ui_constants.rModeValues[vals["rModeInput"]])
            forceRepixel = True
            window["srcImgWidth"].update(value=srcImg.width)
            window["srcImgHeight"].update(value=srcImg.height)
            window["srcImgSizeRatio"].update(
                value=srcImg.width / srcImg.height)
            frac = (srcImg.width / srcImg.height).as_integer_ratio()
            window["srcImgSizeRatioFraction"].update(
                value=str(frac[0])+"/"+str(frac[1]))

            bio = BytesIO()
            srcImg.save(bio, format="PNG")
            window["previewImgInput"].update(data=bio.getvalue())
            pixelImg = srcImg

        # font preview
        if evt == "fontSize" or evt == "fontSelect" or evt == "fontVariant":
            selectedFnt = ImageFont.truetype(
                vals["fontName"], int(vals["fontSize"]))
            bio = BytesIO()
            logic.generateFontPreview(selectedFnt).save(bio, format="PNG")
            window["previewText"].update(data=bio.getvalue())

        # --- END IF NO SOURCE IMAGE LOADED ---
        if srcImg == None:
            logging.info("Source Image is empty, bailing...")
            continue
        
        "-- dont touch srcImg from here on!"

        # convert RGBA->RGB
        if evt == "alwaysRGB":
            logging.info("RGB(A) flag changed, processing...")
            if vals["alwaysRGB"]:
                pixelImg = srcImg.convert("RGB")
            else:
                pixelImg = srcImg
            forceRepixel = True

        # resize canvas
        if ( evt == "pixelSize" or evt == "rMode" or forceRepixel == True ):
            scaledImg = logic.pixelate(pixelImg, int(
                vals["pixelSize"]), ui_screens.ui_constants.rModeValues[vals["rMode"]])
            forceRepixel = False

        if evt == "alwaysRGB" or evt == "pixelSize" or evt == "qMode" or evt == "rMode" or evt == "alphaValue" or evt == "colorAmount":
            img = logic.convertImage(
                scaledImg, ui_screens.ui_constants.qModeValues[vals["qMode"]], int(vals["colorAmount"]))
            bio = BytesIO()
            img.save(bio, format="PNG")
            window["previewImg"].update(data=bio.getvalue())
            window["alphaValue"].update(values=logic.possibleColorValuesForAlpha)

        if evt == "generate":
            diamimg = logic.generateDiamondPainting(img, vals["diamondAlphabet"], vals["alphaValue"], selectedFnt, int(
                vals["diamondSize"]), vals["diamondShape"] == "Round")
            bio = BytesIO()
            diamimg.save(bio, format="PNG")
            window["previewImgDiamond"].update(data=bio.getvalue())
            diamimg.save("/tmp/diamondPainting.png", format="PNG")
            tabimg = logic.generateTable(selectedFnt, vals["diamondAlphabet"], int(vals["diamondSize"]))
            bio = BytesIO()
            tabimg.save(bio, format="PNG")
            window["previewImgTable"].update(data=bio.getvalue())



    except Exception as e:
        traceback.print_tb(sys.exc_info()[2])
        print(e)
        sg.PopupQuickMessage(e)

window.close()
