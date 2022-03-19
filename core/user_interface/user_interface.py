import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo


class GraphicalUserInterface(tk.Tk):
    def __init__(self, loop, interval=1/120): #refresh fqz of the GUI is interval
        super().__init__()
        # root window
        self.title('KNX Simulator User Interface')
        self.geometry('300x300')

        self.ui_var = tk.StringVar() # tk variable name to identify the user input text

        self.label = ttk.Label(self, text="What do you want do to?", font=("Courier 22 bold"))
        self.label.pack()

        self.entry = ttk.Entry(self, textvariable = self.ui_var, width = 60)
        self.entry.pack()

        self.button = ttk.Button(self, text="Validate input")
        self.button['command'] = self.button_clicked
        self.button.pack()

        # async config
        self.loop = loop
        self.tasks = []
        #self.tasks.append(loop.create_task(self.button_clicked()))
        #self.tasks.append(loop.create_task(self.updater(interval))) #async function to refresh the GUI

    async def button_clicked(self):
        self.user_input = self.ui_var.get()
        showinfo(title='Information',
                 message=self.user_input)
