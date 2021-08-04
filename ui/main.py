import ui_logic

UI = ui_logic.UIDiamondPainting()
while True:
    if not UI.process_mainloop():
        break
