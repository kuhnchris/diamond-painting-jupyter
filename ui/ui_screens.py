import PySimpleGUI as sg
import ui_constants

left_column = [
    [
        sg.Text("Source image", size=(25, 1)),
        sg.In(enable_events=True, key="srcImg"),
        sg.FileBrowse(file_types=ui_constants.file_types)
    ],
    [
        sg.Text("Source size", size=(25, 1)),
        sg.In(enable_events=False, key="srcImgWidth", size=(4, 1), disabled=True),
        sg.Text("x", size=(1, 1)),
        sg.In(enable_events=False, key="srcImgHeight", size=(4, 1), disabled=True),
        sg.Text("/", size=(1, 1)),
        sg.In(enable_events=False, key="srcImgSizeRatio", size=(6, 1), disabled=True),
        sg.Text("(", size=(1, 1)),
        sg.In(enable_events=False, key="srcImgSizeRatioFraction", size=(6, 1), disabled=True),
        sg.Text(")", size=(1, 1)),
    ],
    [
        sg.Text("Resize?", size=(25, 1)),
        sg.Checkbox(text="Yes", enable_events=True,
                    key="srcImgResize", default=False)
    ], [
        sg.Text("Size (%)", size=(25, 1)),
        sg.DropDown(list(ui_constants.srcResizeSizes.keys()),
                    "100%", enable_events=True, key="srcImgResizePercent", size=(15, 1))
    ],
    [
        sg.Text("Ignore ratio?", size=(25, 1), visible=False),
        sg.Checkbox(text="Yes", enable_events=True,
                    key="srcImgResizeIgnoreRatio", default=False, visible=False)
    ],
    [
        sg.Text("Custom size", size=(25, 1), visible=False),
        sg.In(enable_events=True, key="srcImgCustomWidth", size=(4, 1), disabled=False, visible=False),
        sg.Text("x", size=(1, 1), visible=False),
        sg.In(enable_events=True, key="srcImgCustomHeight", size=(4, 1), disabled=False, visible=False),
        sg.Text("/", size=(1, 1), visible=False),
        sg.In(enable_events=False, key="srcImgCustomSizeRatio", size=(6, 1), disabled=True, visible=False),
    ],
    [
        sg.Text("Resize Mode", size=(25, 1)),
        sg.DropDown(list(ui_constants.rModeValues.keys()), "Nearest",
                    enable_events=True, key="rModeInput", size=(15, 1))
    ],
]

left_column_pix = [
    [
        sg.Text("Ignore Alpha?", size=(25, 1)),
        sg.Checkbox(text="Yes", enable_events=True,
                    key="alwaysRGB", default=False)
    ],
    [
        sg.Text("Pixel size", size=(25, 1)),
        sg.Slider((1, 32), 8, orientation="h", enable_events=True,
                  key="pixelSize", resolution=1, disable_number_display=True),
        sg.Text("8", key="pixelSizeDisplay", size=(3, 1))
    ], [
        sg.Text("Amount of colors", size=(25, 1)),
        sg.Slider((1, 32), 8, orientation="h", enable_events=True,
                  key="colorAmount", resolution=1, disable_number_display=True),
        sg.Text("8", key="colorAmountDisplay", size=(3, 1))
    ], [
        sg.Text("Quantization Mode", size=(25, 1)),
        sg.DropDown(list(ui_constants.qModeValues.keys()),
                    "Fast Octree", enable_events=True, key="qMode", size=(15, 1))
    ], [
        sg.Text("Resize Mode", size=(25, 1)),
        sg.DropDown(list(ui_constants.rModeValues.keys()), "Nearest",
                    enable_events=True, key="rMode", size=(15, 1))
    ], [
        sg.Text("Color to treat as alpha channel", size=(25, 1)),
        sg.DropDown([], enable_events=True, key="alphaValue", size=(15, 1))
    ],
]

left_column_pageDGen = [
    [sg.Text("Usable characters", size=(25, 1)),
     sg.In(enable_events=True, key="diamondAlphabet",
           default_text="abcdefghijklmnopqrstuvwxyz1234567890!§$%&/()#+\\\"-.:"), ],
    [sg.Text("Font File", size=(25, 1)),
     sg.In(enable_events=True, key="fontName",
           default_text="NotoSans-Black.ttf", disabled=True)],
    [sg.Text("Font Family", size=(25, 1)),
     sg.DropDown(values=ui_constants.fontNames, enable_events=True, key="fontSelect")],
    [sg.Text("Font Variant", size=(25, 1)),
     sg.DropDown(values=ui_constants.fontVariants, enable_events=True, key="fontVariant",
                 size=(25, 1))],

    [sg.Text("Font Size", size=(25, 1)),
     sg.Slider((1, 64), 12, orientation="h", enable_events=True,
               key="fontSize", resolution=1, disable_number_display=True),
     sg.Text("12", key="fontSizeDisplay", size=(3, 1))],
    [sg.Text("Font Preview", size=(25, 1)),
     sg.Image(key="previewText")],
    [sg.Text("Diamond Size (in mm)", size=(25, 1)),
     sg.Slider((1, 64), 28, orientation="h", enable_events=True,
               key="diamondSize", resolution=1, disable_number_display=True),
     sg.Text("28", key="diamondSizeDisplay", size=(3, 1))],
    [sg.Text("Diamond Shape", size=(25, 1)),
     sg.DropDown(["Round", "Square"], default_value="Round",
                 key="diamondShape", enable_events=True)],
    [sg.Button(button_text="Generate", enable_events=True, key='generate')]
]

left_column_pageTable = [

]
left_column_pageCompose = [

]

tab1_left = sg.Tab("Input", left_column)
tab3_left = sg.Tab("Pixelation", left_column_pix)
tab2_left = sg.Tab("Processing", left_column_pageDGen)
tab4_left = sg.Tab("Color table", left_column_pageTable)
tab5_left = sg.Tab("Composition", left_column_pageCompose)

right_column_in = [
    [sg.Image(key="previewImgInput")],
]

right_column_pix = [
    [sg.Image(key="previewImg")],
]

right_column_dia = [
    [sg.Image(key="previewImgDiamond")],
]

right_column_tab = [
    [sg.Image(key="previewImgTable")],
]

right_column_com = [
    [sg.Image(key="previewImgComposition")],
]
tab1_right = sg.Tab("Preview (input)", right_column_in)
tab2_right = sg.Tab("Preview (pixel)", right_column_pix)
tab3_right = sg.Tab("Preview (diamonds)", right_column_dia)
tab4_right = sg.Tab("Preview (table)", right_column_tab)
tab5_right = sg.Tab("Preview (composition)", right_column_com)

menu = [['&File', ['&Open', '&Save', '---', 'E&xit']], ['&Help', '&About']]

layout = [
    [
        sg.Menu(menu, key="Menu"),
        sg.Column([[sg.TabGroup([[tab1_left, tab3_left, tab2_left, tab4_left, tab5_left]])]],
                  size=(650, 650), expand_y=True),
        sg.VSeperator(),
        sg.Column([[sg.TabGroup([[tab1_right, tab2_right, tab3_right, tab4_right, tab5_right]])]], size=(650, 650)),
    ]
]
