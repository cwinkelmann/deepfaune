import sys
import os
curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

from predictTools import txt_classes

import PySimpleGUI as sg
sg.ChangeLookAndFeel('Reddit')
sg.LOOK_AND_FEEL_TABLE["Reddit"]["BORDER"]=0
LANG = 'fr'

listCB = []
lineCB = []
sorted_txt_classes_lang = sorted(txt_classes[LANG])
for k in range(0,len(sorted_txt_classes_lang )):
    lineCB = lineCB+[sg.CB(sorted_txt_classes_lang[k], key=sorted_txt_classes_lang[k],
                           size=(12, 1), default=True)]
    if k%3:
        listCB = listCB+[lineCB]
        lineCB = []

if lineCB:
    listCB = listCB+[lineCB]
    
layout = [[sg.Frame('Flags', listCB, font='Any 12', title_color='blue')], 
     [sg.Button("OK", key='-OK-')]]
window = sg.Window('Machine Learning Front End',
                   layout, font=("Helvetica", 12))

forbiddenclasses = []
while True:
    event, values = window.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-OK-':
        for label in sorted_txt_classes_lang:
            print(label, values[label])
            if not values[label]:
                forbiddenclasses += [label]
window.close()


prediction = np.random.sample((4,len(txt_classes[LANG])))

idxforbidden = [idx for idx in range(0,len(txt_classes[LANG])) if txt_classes[LANG][idx] in forbiddenclasses]
pred = prediction[k,]
if np.argmax(pred) in idxforbidden:
    print("Unknown")
    
if(max(pred)>=self.threshold):
    self.predictedclass_base[k] = txt_classesempty_lang[-idxforbidden][np.argmax(pred)]
