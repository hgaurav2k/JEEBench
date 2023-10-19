from collections import OrderedDict
from tkinter import *
from tkinter import ttk
import json
import numpy as np
import matplotlib
import copy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime 
import os 
matplotlib.use('pgf')

paper_buttons = []
question_buttons = []
active_paper = None
active_question = None
paper_frame = None
q_list_frame = None
q_frame = None
sb = None
# attributes_to_fill = ['GPT3_extract', 'GPT3.5_extract', 'GPT4_extract', ]
attributes_to_fill = ['GPT3_CoT_exam_extract', 'GPT3.5_exam_extract', 'GPT4_exam_extract', ]
q_sub_frames = OrderedDict({
    'question_frame': None,
    'gold_frame': None,
    'GPT3_frame': None,
    'GPT3.5_frame': None,
    'GPT4_frame': None,
    'button_frame': None
})
question_text_box = None
edited_question_text_box = None

def rgb(r, g, b):
    return "#%s%s%s" % tuple([hex(c)[2:].rjust(2, "0") for c in (r, g, b)])


def change_question_text(idx):
    '''
    This function renders the question tab. When the save/flag button is
    pressed, the whole dataset is resaved and fetched again. 
    '''
    global q_sub_frames, q_frame, active_paper, active_question
    active_question = idx
    print("Active paper:", active_paper, "\tActive question:", active_question)
    questions = json.load(open('responses.json'))
    for q in questions:
        if q['description'] == active_paper and q['index'] == idx:
            question = q
            break  
    # for widget in q_sub_frames.values():
    #     if widget:
    #         widget.destroy()
    for widget in q_frame.winfo_children():
        if widget:
            widget.destroy()
    
    textboxes = OrderedDict({
        'question': {
            'label': 'Question',
            'editable': False, 
            'subframe': 'question_frame',
            'textbox': None,
        }, 
        'question_edited': {
            'label': 'Edited question',
            'editable': True,
            'subframe': 'question_frame',
            'textbox': None,
        },
        'question_type': {
            'label': 'Question type',
            'editable': True,
            'subframe': 'gold_frame',
            'textbox': None
        },
        'gold': {
            'label': 'Gold',
            'editable': True,
            'subframe': 'gold_frame',
            'textbox': None,
        }, 
        'GPT3_CoT_exam_response':    {
            'label': 'GPT3 response',
            'editable': False,
            'subframe': 'GPT3_frame',
            'textbox': None,
        }, 
        'GPT3_CoT_exam_extract':     {
            'label': 'GPT3 extract',
            'editable': True,
            'subframe': 'GPT3_frame',
            'textbox': None,
        },  
        'GPT3.5_exam_response':  {
            'label': 'GPT3.5 response',
            'editable': False,
            'subframe': 'GPT3.5_frame',
            'textbox': None,
        },
        'GPT3.5_exam_extract':   {
            'label': 'GPT3.5 extract',
            'editable': True,
            'subframe': 'GPT3.5_frame',
            'textbox': None,
        },
        'GPT4_exam_response':    {
            'label': 'GPT4 response',
            'editable': False,
            'subframe': 'GPT4_frame',
            'textbox': None,
        },
        'GPT4_exam_extract':     {
            'label': 'GPT4 extract',
            'editable': True,
            'subframe': 'GPT4_frame',
            'textbox': None,
        }
    })

    for sub_frame in q_sub_frames:
        q_sub_frames[sub_frame] = Frame(q_frame)
        
    for key in textboxes:
        sub_sub_frame = Frame(q_sub_frames[textboxes[key]['subframe']])
        sub_sub_frame.pack(side=LEFT)
        Label(sub_sub_frame, text=textboxes[key]['label']).pack(side=TOP)
        if textboxes[key]['subframe'] == 'gold_frame':
            text_box = Text(sub_sub_frame, height=2, width=60, highlightbackground="black", highlightthickness=1)
        else:
            text_box = Text(sub_sub_frame, height=7, width=60, highlightbackground="black", highlightthickness=1)
        
        if "GPT" in key and "response" in key:
            if key == "GPT3_CoT_exam_response":
                if question[key] != "":
                    text_box.insert(END, question[key]["choices"][0]["text"])
            else:
                if question[key] != "":
                    text_box.insert(END, question[key]["choices"][0]["message"]["content"])
        else:
            text_box.insert(END, question[key])
        text_box.pack(side=TOP)
        if not textboxes[key]['editable']:
            text_box.configure(state='disabled')
        textboxes[key]['textbox'] = text_box
    curr_q = Frame(q_frame)
    label = Label(curr_q, text=f"Current Question: {active_question}")
    label.pack(side=TOP)
    
    def save_state():
        global questions
        updated_question = copy.deepcopy(question)
        for textbox in textboxes.keys():
            if textboxes[textbox]['editable']:
                updated_question[textbox] = textboxes[textbox]['textbox'].get("1.0",'end-1c')
        for i, q in enumerate(questions):
            if q['index'] == updated_question['index'] and q['description'] == updated_question['description']:
                questions[i] = updated_question
        with open('responses.json', 'w') as outfile:
            json.dump(questions, outfile, indent=4)
            print(f"Saving changes to Q {q['index']} from {active_paper}]")
        change_questions(active_paper, delete_q_frame=False)

    
    save_button =  Button(q_sub_frames['button_frame'], text="SAVE", bg="#00FF00", command=save_state)
    save_button.pack(side=LEFT)
    
    for sub_frame in q_sub_frames:
        q_sub_frames[sub_frame].pack(side=TOP)

    curr_q.pack(side=TOP)


def question_button_command(idx):
    return lambda: change_question_text(idx)




def change_questions(paper, delete_q_frame=True):
    '''
    Respnsible for updating the list of questions in 2 cases:
      1.  Someone annotates, then the color of buttons should change.
      2.  If someone changes the paper, then the list of questions should change. 
          In this case, the q_frame should also be deleted. Therefore, the flag
          for delete_q_frame has been provided.  
    '''
    global active_paper, active_question, question_buttons, question_text_box, q_list_frame, sb, root
    
    questions = json.load(open('responses.json'))
    
    active_paper = paper
    current_questions = list(sorted([q for q in questions if q['description'] == active_paper], key=lambda x: int(x['index'])))

    if delete_q_frame:
        if q_frame:
            for widget in q_frame.winfo_children():
                widget.destroy()
    if q_list_frame:
        for button in question_buttons:
            button.destroy()
            
        for widget in q_list_frame.winfo_children():
            widget.destroy()
            
    question_buttons = []
    
    for i, q in enumerate(current_questions):
        text = f"Question {q['index']}"
        filled_count = 0
        for att in attributes_to_fill:
            if att in q:
                if q[att] != '':
                    filled_count += 1
            
        if q['finalized']:
            col = rgb(0, int(filled_count/len(attributes_to_fill)*128)+127, 0)
        else:
            col = rgb(0,0,255)
        if str(i) == active_question:
            col = rgb(25, 25, 100)
        button = Button(q_list_frame, text=text, bg=col, command=question_button_command(int(q['index'])))
        button.pack(side=TOP, fill='x')
        q_list_frame.insert("end", "\n")
    
        question_buttons.append(button)
    
    
        
def paper_button_command(paper):
    return lambda: change_questions(paper)


    
def main():
    global paper_buttons, question_buttons, active_paper, paper_frame, q_list_frame, q_frame, questions, sb, root
    root = Tk()
    root.option_add( "*font", "helvetica 12 bold" )
    root.title('Annotate')
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    
    questions = json.load(open('responses.json'))
    
    now = datetime.now().strftime("%d-%m-%Y-H:%M:%S")
    bkp_name = f"backup/responses-{now}.json"
    if not os.path.exists('backup'):
        os.makedirs('backup')
    json.dump(questions, open(bkp_name, 'w'), indent=4)
    print('starting dataset backed up to', bkp_name)

    papers = list(sorted(np.unique([q['description'] for q in questions])))
    active_paper = papers[0]
    
    # This frame has the list of papers to annotate
    paper_frame = Frame(root, highlightbackground="black", highlightthickness=1)
    paper_frame.pack(side=LEFT)

    for paper in papers:
        button = Button(paper_frame, text=paper, fg="green", command=paper_button_command(paper))
        button.pack(side=TOP)
        paper_buttons.append(button)
    

    vscrollbar = Scrollbar(root)
    c = Canvas(root,background = "#D2D2D2",yscrollcommand=vscrollbar.set, width=32, highlightbackground="black", highlightthickness=1)
    vscrollbar.config(command=c.yview)
    

    # This frame has the list of questions to annotate for the active paper
    # Text in Tkinter is scrollable unlike a Frame.
    q_list_frame = Text(c)
    q_list_frame.pack(side="left", fill='y')
    vscrollbar.pack(side=LEFT, fill=Y) 
    c.pack(side="left", fill="both", expand=True)
    c.create_window(0,0,window=q_list_frame, anchor='nw')
    change_questions(active_paper)
    root.update()
    c.config(scrollregion=c.bbox("all"))

    
    
    # This frame has the details of the question to be annotated
    q_frame = Frame(root, highlightbackground="black", highlightthickness=1)
    q_frame.pack(side=LEFT, expand=1, fill = 'both')
    
    
    root.mainloop()

if __name__ == '__main__':
    main()