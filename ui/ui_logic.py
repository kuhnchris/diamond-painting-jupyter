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

class UIDiamondPainting:
    def __init__(self):
        self.settings = sg.UserSettings()
        logging.basicConfig(level=logging.DEBUG)
        self.maxSize = 600
        self.srcImg = None
        self.scaledImg = None
        self.pixelImg = None
        self.processedImg = None
        self.selectedFnt = None
        self.forceRepixel = False
        self.variantList = {}
        self.vals = {}

        self.window = sg.Window(title="Diamondificator",
                        layout=ui_screens.layout, margins=(5, 5))

        self.IGNORE_VALS = ["Browse","Menu", "0","2","1","3"]

    def evt_load(self, evt, vals):
        fnam = sg.popup_get_file('Choose file to load', 'Load configuration', default_extension='*.json', no_window=True)
        jload = json.load(open(fnam,'r'))
        vals = jload
        for val in vals:
            if not val in self.IGNORE_VALS:
                print("update ",val," to ", vals[val])
                self.window[val].update(vals[val])
            else:
                print("ignoring ",val)

    def evt_save(self,evt, vals):
        saveWin = sg.Window(title="Save as...",layout=[[sg.FileSaveAs(enable_events=True, key="SavePath")]])
        evt2, vals2 = saveWin.read()
        saveWin.close()
        print("Save dialog exited: ",evt2," - ",vals2)
        if evt2 == "SavePath":
            jsave = json.dump(vals,open(vals2["SavePath"],'w'))            
            sg.Popup("Saving was successful.")

    def evt_updateSliderTexts(self, evt, vals):
        # update texts beside sliders
        self.window["fontSizeDisplay"].update(value=int(vals['fontSize']))
        self.window["diamondSizeDisplay"].update(value=int(vals['diamondSize']))
        self.window["pixelSizeDisplay"].update(value=int(vals['pixelSize']))
        self.window["colorAmountDisplay"].update(value=int(vals['colorAmount']))

    def evt_updateFont(self, evt, vals):
        for f in matplotlib.font_manager.fontManager.ttflist:
            if f.name == vals["fontSelect"]:
                self.window["fontName"].update(f.fname)
                vals["fontName"] = f.fname
                fName = "%s %s %s" % (f.name,f.style,str(f.weight))
                self.variantList[fName] = f.fname
        self.window["fontVariant"].update(values=list(self.variantList))

    def evt_updateFontVariant(self, evt, vals):
        self.window["fontName"].update(self.variantList[vals["fontVariant"]])
        vals["fontName"] = (self.variantList[vals["fontVariant"]])

    def evt_processInputImg(self, evt, vals):
        logging.info("Loading image: %s " % vals["srcImg"])
        self.srcImg = logic.loadImage(vals["srcImg"], -1)
        if vals["alwaysRGB"]:
            self.srcImg = self.srcImg.convert("RGB")
        if vals["srcImgResize"]:
            resizeFac = ui_screens.ui_constants.srcResizeSizes[vals["srcImgResizePercent"]]
            self.srcImg = self.srcImg.resize((int(self.srcImg.width*resizeFac), int(self.srcImg.height * resizeFac)), ui_screens.ui_constants.rModeValues[vals["rModeInput"]])
        forceRepixel = True
        self.window["srcImgWidth"].update(value=self.srcImg.width)
        self.window["srcImgHeight"].update(value=self.srcImg.height)
        self.window["srcImgSizeRatio"].update(
            value=self.srcImg.width / self.srcImg.height)
        frac = (self.srcImg.width / self.srcImg.height).as_integer_ratio()
        self.window["srcImgSizeRatioFraction"].update(
            value=str(frac[0])+"/"+str(frac[1]))

        bio = BytesIO()
        self.srcImg.save(bio, format="PNG")
        self.window["previewImgInput"].update(data=bio.getvalue())
        self.pixelImg = self.srcImg

    def evt_processRGBA(self, evt, vals):
        logging.info("RGB(A) flag changed, processing...")
        if vals["alwaysRGB"]:
            self.pixelImg = self.srcImg.convert("RGB")
        else:
            self.pixelImg = self.srcImg
        self.forceRepixel = True


    def evt_updateFontPreview(self, evt, vals):
        self.selectedFnt = ImageFont.truetype(
                    vals["fontName"], int(vals["fontSize"]))
        bio = BytesIO()
        logic.generateFontPreview(self.selectedFnt).save(bio, format="PNG")
        self.window["previewText"].update(data=bio.getvalue())

    def evt_processPixelImg(self,evt, vals):
        self.scaledImg = logic.pixelate(self.pixelImg, int(
                    vals["pixelSize"]), ui_screens.ui_constants.rModeValues[vals["rMode"]])
        self.forceRepixel = False
        self.processedImg = logic.convertImage(
            self.scaledImg, ui_screens.ui_constants.qModeValues[vals["qMode"]], int(vals["colorAmount"]))
        bio = BytesIO()
        self.processedImg.save(bio, format="PNG")
        self.window["previewImg"].update(data=bio.getvalue())
        self.window["alphaValue"].update(values=logic.possibleColorValuesForAlpha)

    def evt_generateDiamondPainting(self, evt, vals):
        self.diamimg = logic.generateDiamondPainting(self.processedImg, vals["diamondAlphabet"], vals["alphaValue"], self.selectedFnt, int(            vals["diamondSize"]), vals["diamondShape"] == "Round")
        bio = BytesIO()
        self.diamimg.save(bio, format="PNG")
        self.window["previewImgDiamond"].update(data=bio.getvalue())
        self.diamimg.save("/tmp/diamondPainting.png", format="PNG")
        tabimg = logic.generateTable(self.selectedFnt, vals["diamondAlphabet"], int(vals["diamondSize"]))
        bio = BytesIO()
        tabimg.save(bio, format="PNG")
        self.window["previewImgTable"].update(data=bio.getvalue())

    def process_mainloop(self):
        try:
            # set variables
            forceRepixel = False

            # wait for event
            evt, vals = self.window.read()
            logging.debug(("Event: %s - Values: %s" % (evt, vals)))
            
            # close event
            if evt == "Exit" or evt == sg.WIN_CLOSED:
                logging.info("Quitting...")
                return False

            if evt == "Save":
                self.evt_save(evt, vals)
        
            if evt == "Open":
                self.evt_load(evt, vals)
                self.evt_updateFont(evt,vals)
                self.evt_updateFontVariant(evt,vals)
                self.evt_updateFontPreview(evt,vals)
                self.evt_processInputImg(evt,vals)
                self.evt_processRGBA(evt, vals)
                self.evt_processPixelImg(evt,vals)
                self.evt_generateDiamondPainting(evt, vals)

            self.evt_updateSliderTexts(evt, vals)

            # update font path/name
            if evt == "fontSelect":
                self.evt_updateFont(evt,vals)

            if evt == "fontVariant":
                self.evt_updateFontVariant(evt, vals)

            # react on image load
            if (evt == "srcImg" or evt == "srcImgResize" or evt == "srcImgResizePercent" or evt == "srcImgResizeIgnoreRatio" or evt == "srcImgCustomWidth" or evt == "srcImgCustomHeight" or evt == "srcImgCustomSizeRation" or evt == "rModeInput") and vals["srcImg"] != "":
                self.evt_processInputImg(evt, vals)

            # font preview
            if evt == "fontSize" or evt == "fontSelect" or evt == "fontVariant":
                self.evt_updateFontPreview(evt, vals)

            # --- END IF NO SOURCE IMAGE LOADED ---
            if self.srcImg == None:
                logging.info("Source Image is empty, bailing...")
                return True

            # convert RGBA->RGB
            if evt == "alwaysRGB":
                self.evt_processRGBA(evt, vals)

            # resize canvas
            if ( evt == "pixelSize" or evt == "rMode" or forceRepixel == True ) or ( evt == "alwaysRGB" or evt == "pixelSize" or evt == "qMode" or evt == "rMode" or evt == "alphaValue" or evt == "colorAmount" ):
                self.evt_processPixelImg(evt,vals)
                
            if evt == "generate":
                self.evt_generateDiamondPainting(evt, vals)

        except Exception as e:
            traceback.print_tb(sys.exc_info()[2])
            print(e)
            sg.PopupQuickMessage(e)
        return True