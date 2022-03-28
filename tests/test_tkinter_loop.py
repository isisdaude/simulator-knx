from tkinter import *
from tkinter import ttk
import time, datetime

import tkinter as tk
from tkinter import ttk
import time, datetime


class DigitalClock(tk.Tk):
    def __init__(self):
        super().__init__()

        self.start_time = time.time()
        # configure the root window
        self.title('Digital Clock')
        self.resizable(0, 0)
        self.geometry('250x80')
        self['bg'] = 'black'

        # change the background color to black
        self.style = ttk.Style(self)
        self.style.configure(
            'TLabel',
            background='black',
            foreground='red')

        # label
        self.label = ttk.Label(
            self,
            text=self.time_string(),
            font=('Digital-7', 40))

        self.label.pack(expand=True)

        # schedule an update every 1 second
        self.label.after(1000, self.update)

    def time_string(self):
        sim_time = time.time() - self.start_time
        str_sim_time = str(datetime.timedelta(seconds=sim_time))
        return str_sim_time

    def update(self):
        """ update the label every 1 second """

        self.label.configure(text=self.time_string())

        # schedule another timer
        self.label.after(1000, self.update)


if __name__ == "__main__":
    clock = DigitalClock()
    clock.mainloop()

# # Here, we are creating our class, Window, and inheriting from the Frame
# # class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
# class Window(Frame):
#
#     # Define settings upon initialization. Here you can specify
#     def __init__(self, master=None):
#         self.start_time = time.time()
#
#         # parameters that you want to send through the Frame class.
#         Frame.__init__(self, master)
#
#         #reference to the master widget, which is the tk window
#         self.master = master
#
#         #with that, we want to then run init_window, which doesn't yet exist
#         self.init_window()
#
#     #Creation of init_window
#     def init_window(self):
#
#         # changing the title of our master widget
#         self.master.title("Simulation Time")
#
#         # allowing the widget to take the full space of the root window
#         self.pack(fill=BOTH, expand=True)
#
#         # creating a button instance
#         quitButton = Button(self, text="Stop",command=self.client_exit)
#
#         # placing the button on my window
#         quitButton.place(x=180, y=250)
#
#         self.after(1, self.update_time) # to update time displayed
#
#     def update_time(self):
#         sim_time = time.time() - self.start_time
#         str_sim_time = str(datetime.timedelta(seconds=sim_time))
#         self.columnconfig(text=str_sim_time)
#
#
#     def client_exit(self):
#         exit()
#
# # root window created. Here, that would be the only window, but
# # you can later have windows within windows.
# root = Tk()
#
# root.geometry("400x300")
#
# #creation of an instance
# app = Window(root)
#
# #mainloop
# root.mainloop()
#
#
#
#
#
#
#
