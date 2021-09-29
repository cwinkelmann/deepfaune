import PySimpleGUI as sg

sg.theme("Reddit")

species = ['daisy','iris','tulip']
prediction = []

left_col = [
    [sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
    #[sg.Spin([i for i in range(1,11)], initial_value=10, k='-SPIN-'), sg.Text('Spin')],
    [sg.Text('Threshold'), sg.Slider(range=(50,100), orientation='h', size=(10,20), change_submits=True, key='-THRESHOLD-')],
    [sg.Text('Progress bar'), sg.ProgressBar(100, orientation='h', size=(20, 20), border_width=4, key='progbar',bar_color=['Blue','White'])],
    [sg.Button('Run'), sg.B('Clear'), sg.Cancel()]
]
right_col=[
    [sg.Multiline(size=(50, 11), write_only=True, key="-ML_KEY-", reroute_stdout=True, echo_stdout_stderr=True, reroute_cprint=True)],
    [sg.Listbox(values=('value1', 'value2', 'value3'), size=(30, 2), key='-LIST-')],
    [sg.Table(values=prediction, headings=['Filename']+species, auto_size_columns=False, col_widths=[10, 10, 10], key='-RESULTS-')]
]

layout = [[sg.Column(left_col, element_justification='l' ),
           sg.Column(right_col, element_justification='l')]]
 
        
window =sg.Window("DeepFaune predition",layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-FOLDER-':
        folder = values['-FOLDER-']
        print(folder)
    elif event == '-THRESHOLD-':
        threshold = values['-THRESHOLD-']
        print(threshold)
    elif event == 'Run':
        sg.cprint('Running....', c='white on green', end='')
        sg.cprint('')
        for i in range(10):
            sg.cprint(i)
            import time
            time.sleep(1)
            window['progbar'].update_bar(100*(i+1)/10)        
            window.Element('-LIST-').Update(values=['new value 1', 'new value 2', 'new value 3'])
            prediction  = [["ttt","0.2","0.5","0.3"],["ddt","0.5","0.1","0.4"]]
            window.Element('-RESULTS-').Update(values=prediction)
        
window.close()  
