import ui_logic

UI = ui_logic.UIDiamondPainting()
while True:
    if UI.process_mainloop() == False:
        break