import json
import traceback
import PySimpleGUI as sg
import sys
from io import BytesIO

from numpy.core.fromnumeric import resize
import ui_screens
import logic
import logging
from PIL import ImageFont
import matplotlib.font_manager


class UIDiamondPainting:
    def __init__(self):
        self.logic = logic.DiamondPaintingGeneratorLogic()
        self.settings = sg.UserSettings()
        logging.basicConfig(level=logging.DEBUG)
        self.maxSize = 600
        self.srcImg = None
        self.scaledImg = None
        self.pixelImg = None
        self.diamondImg = None
        self.processedImg = None
        self.selectedFnt = None
        self.tableImage = None
        self.forcePixelGen = False
        self.variantList = {}
        self.UIValueList = {}
        self.evt = ""

        self.window = sg.Window(title="Diamond Painting Generator",
                                layout=ui_screens.layout, margins=(5, 5),
                                resizable=True)

        self.ignoreImportUIFields = ["Browse", "Menu", "0", "2", "1", "3", "tabLeft", "tabRight"]

    def evt_load(self):
        filename_load = sg.popup_get_file('Choose file to load', 'Load configuration',
                                          default_extension='*.diapac', no_window=True,
                                          file_types=(("Diamond Painting Configuration", ".diapac"),))
        json_loaded_values = json.load(open(filename_load, 'r'))
        self.UIValueList = json_loaded_values
        for val in self.UIValueList:
            if val not in self.ignoreImportUIFields:
                print("update ", val, " to ", self.UIValueList[val])
                self.window[val].update(self.UIValueList[val])
            else:
                print("ignoring ", val)

    def evt_save(self):
        filename_save = sg.popup_get_file('Choose file to save', 'Save configuration',
                                          default_extension='*.diapac', no_window=True, save_as=True,
                                          file_types=(("Diamond Painting Configuration", ".diapac"),))
        
        #save_window = sg.Window(title="Save as...", layout=[[sg.FileSaveAs(enable_events=True, key="SavePath")]])
        #evt2, value_list_save_window = save_window.read()
        #save_window.close()
        #print("Save dialog exited: ", evt2, " - ", value_list_save_window)
        #if evt2 == "SavePath":
            #json.dump(self.UIValueList, open(value_list_save_window["SavePath"], 'w'))
        f = open(filename_save, 'w')
        json.dump(self.UIValueList, f)
        f.close()
        sg.Popup("Saving was successful.")

    def evt_updateSliderTexts(self):
        # update texts beside sliders
        self.window["fontSizeDisplay"].update(value=int(self.UIValueList['fontSize']))
        self.window["diamondSizeDisplay"].update(value=int(self.UIValueList['diamondSize']))
        self.window["pixelSizeDisplay"].update(value=int(self.UIValueList['pixelSize']))
        self.window["colorAmountDisplay"].update(value=int(self.UIValueList['colorAmount']))
        self.window["spaceBetweenDisplay"].update(value=int(self.UIValueList['spaceBetween']))
        self.window["outlineWidthDisplay"].update(value=int(self.UIValueList['outlineWidth']))
        

    def evt_updateFont(self):
        self.variantList.clear()
        for f in matplotlib.font_manager.fontManager.ttflist:
            if f.name == self.UIValueList["fontSelect"]:
                self.window["fontName"].update(f.fname)
                self.UIValueList["fontName"] = f.fname
                font_name = "%s %s %s" % (f.name, f.style, str(f.weight))
                self.variantList[font_name] = f.fname
        self.window["fontVariant"].update(values=list(self.variantList))

    def evt_updateFontVariant(self):
        self.window["fontName"].update(self.variantList[self.UIValueList["fontVariant"]])
        self.UIValueList["fontName"] = (self.variantList[self.UIValueList["fontVariant"]])

    def evt_processInputImg(self):
        logging.info("Loading image: %s " % self.UIValueList["srcImg"])
        self.srcImg = self.logic.loadImage(self.UIValueList["srcImg"], -1)
        if self.UIValueList["alwaysRGB"]:
            self.srcImg = self.srcImg.convert("RGB")

        self.window["srcImgWidth"].update(value=self.srcImg.width)
        self.window["srcImgHeight"].update(value=self.srcImg.height)
        self.window["srcImgSizeRatio"].update(
            value=self.srcImg.width / self.srcImg.height)
        image_ratio = (self.srcImg.width / self.srcImg.height).as_integer_ratio()
        self.window["srcImgSizeRatioFraction"].update(
            value=str(image_ratio[0]) + "/" + str(image_ratio[1]))

        if self.UIValueList["srcImgResize"]:
            resize_fac = ui_screens.ui_constants.srcResizeSizes[self.UIValueList["srcImgResizePercent"]]
            if self.UIValueList["srcImgResizePercent"] == "Custom":
                resize_fac = self.UIValueList["srcImgCustomSizeRatio"]
                target_x = int(self.UIValueList["srcImgCustomWidth"])
                target_y = int(self.UIValueList["srcImgCustomHeight"])
            else:
                target_x = int(self.srcImg.width * resize_fac)
                target_y = int(self.srcImg.height * resize_fac)
            self.srcImg = self.srcImg.resize((target_x,target_y),
                                             ui_screens.ui_constants.rModeValues[self.UIValueList["rModeInput"]])
        self.forcePixelGen = True

        bio = BytesIO()
        self.srcImg.save(bio, format="PNG")
        self.window["previewImgInput"].update(data=bio.getvalue())
        self.pixelImg = self.srcImg

    def evt_processRGBA(self):
        logging.info("RGB(A) flag changed, processing...")
        if self.UIValueList["alwaysRGB"]:
            self.pixelImg = self.srcImg.convert("RGB")
        else:
            self.pixelImg = self.srcImg
        self.forcePixelGen = True

    def evt_updateFontPreview(self):
        self.selectedFnt = ImageFont.truetype(
            self.UIValueList["fontName"], int(self.UIValueList["fontSize"]))
        bio = BytesIO()
        self.logic.generateFontPreview(self.selectedFnt).save(bio, format="PNG")
        self.window["previewText"].update(data=bio.getvalue())

    def evt_processPixelImg(self):
        self.scaledImg = self.logic.pixelate(self.pixelImg, int(
            self.UIValueList["pixelSize"]), ui_screens.ui_constants.rModeValues[self.UIValueList["rMode"]])
        self.forcePixelGen = False
        self.processedImg = self.logic.convertImage(
            self.scaledImg, ui_screens.ui_constants.qModeValues[self.UIValueList["qMode"]],
            int(self.UIValueList["colorAmount"]))
        bio = BytesIO()
        self.processedImg.save(bio, format="PNG")
        self.window["previewImg"].update(data=bio.getvalue())
        self.window["alphaValue"].update(values=self.logic.possibleColorValuesForAlpha)
        self.window["alphaValue"].update(self.UIValueList["alphaValue"])

    def evt_generateDiamondPainting(self):
        self.diamondImg = self.logic.generateDiamondPainting(self.processedImg, self.UIValueList["diamondAlphabet"],
                                                             self.UIValueList["alphaValue"],
                                                             self.selectedFnt, int(self.UIValueList["diamondSize"]),
                                                             self.UIValueList["diamondShape"] == "Round",
                                                             int(self.UIValueList["spaceBetween"]),
                                                             int(self.UIValueList["outlineWidth"]))
        bio = BytesIO()
        self.diamondImg.save(bio, format="PNG")
        self.window["previewImgDiamond"].update(data=bio.getvalue())
        self.diamondImg.save("/tmp/diamondPainting.png", format="PNG", dpi=(96,96))
        self.tableImage = self.logic.generateTable(self.selectedFnt, self.UIValueList["diamondAlphabet"],
                                                   int(self.UIValueList["diamondSize"]),
                                                   self.UIValueList["alphaValue"])
        bio = BytesIO()
        self.tableImage.save(bio, format="PNG")
        self.window["previewImgTable"].update(data=bio.getvalue())

    def process_mainloop(self):
        try:
            # set variables
            self.forcePixelGen = False

            # wait for event
            evt, ui_values = self.window.read()
            self.UIValueList = ui_values
            self.evt = evt
            logging.debug(("Event: %s - Values: %s" % (evt, self.UIValueList)))

            # close event
            if evt == "Exit" or evt == sg.WIN_CLOSED:
                logging.info("Quitting...")
                return False

            if evt == "Save":
                self.evt_save()

            if evt == "Open":
                self.evt_load()
                self.evt_updateFont()
                self.evt_updateFontVariant()
                self.evt_updateFontPreview()
                self.evt_processInputImg()
                self.evt_processRGBA()
                self.evt_processPixelImg()
                self.evt_generateDiamondPainting()

            self.evt_updateSliderTexts()

            if evt == "tabLeft":
                #tabLeft
                pass
                
            # update font path/name
            if evt == "fontSelect":
                self.evt_updateFont()

            if evt == "fontVariant":
                self.evt_updateFontVariant()

            if evt == "srcImgCustomHeight" or evt == "srcImgCustomWidth":
                self.UIValueList["srcImgCustomSizeRatio"] = int(self.UIValueList["srcImgCustomHeight"]) / int(self.UIValueList["srcImgCustomWidth"])
                self.window["srcImgCustomSizeRatio"].update(value=self.UIValueList["srcImgCustomSizeRatio"])

            if evt == "srcImgResizePercent" and self.UIValueList["srcImgResizePercent"] == "Custom":
                self.window["srcImgCustom_Lbl1"].update(visible=True)
                self.window["srcImgCustomWidth"].update(visible=True)
                self.window["srcImgCustom_Lbl2"].update(visible=True)
                self.window["srcImgCustomHeight"].update(visible=True)
                self.window["srcImgCustom_Lbl3"].update(visible=True)
                self.window["srcImgCustomSizeRatio"].update(visible=True)

            # react on image load
            if (evt == "srcImg" or evt == "srcImgResize" or
                evt == "srcImgResizePercent" or
                evt == "srcImgResizeIgnoreRatio" or
                evt == "srcImgCustomWidth" or
                evt == "srcImgCustomHeight" or
                evt == "srcImgCustomSizeRatio" or
                evt == "rModeInput") and \
                    self.UIValueList["srcImg"] != "":
                self.evt_processInputImg()

            # font preview
            if evt == "fontSize" or evt == "fontSelect" or evt == "fontVariant":
                self.evt_updateFontPreview()

            # --- END IF NO SOURCE IMAGE LOADED ---
            if self.srcImg is None:
                logging.info("Source Image is empty, bailing...")
                return True

            # convert RGBA->RGB
            if evt == "alwaysRGB":
                self.evt_processRGBA()

            # resize canvas
            if (evt == "pixelSize" or evt == "rMode" or self.forcePixelGen) or (
                    evt == "alwaysRGB" or evt == "pixelSize" or evt == "qMode" or
                    evt == "rMode" or evt == "alphaValue" or evt == "colorAmount"):
                self.evt_processPixelImg()

            if evt == "generate":
                self.evt_generateDiamondPainting()

        except Exception as e:
            traceback.print_tb(sys.exc_info()[2])
            print(e)
            sg.PopupQuickMessage(e)
        return True
