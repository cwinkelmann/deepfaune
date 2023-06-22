import PySimpleGUI as sg


def get_scaling():
    # called before window created
    root = sg.tk.Tk()
    scaling = root.winfo_fpixels('1i')/72
    root.destroy()
    return scaling


scaling = get_scaling()
width, height = sg.Window.get_screen_size()


window = sg.Window("test", layout=[[]], finalize=True, size=(int(0.9*width),int(0.9*height))) # 0.9 because linux menu bar on the bottom 

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    print(event, values)
window.close()
