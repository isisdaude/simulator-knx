# import tkinter as tk
# from tkinter import ttk
# from tkinter.messagebox import showinfo
#
#
# class App(tk.Tk):
#     def __init__(self):
#         super().__init__()
#
#         # configure the root window
#         self.title('My Awesome App')
#         self.geometry('600x600')
#
#         self.ui_var = tk.StringVar()
#
#         # label
#         self.label = ttk.Label(self, text='Hello, Tkinter!')
#         self.label.pack()
#         self.entry = ttk.Entry(self, textvariable = self.ui_var, width = 60) #, font = ('calibre',10,'normal'), show = '*')
#         self.entry.pack()
#
#         # button
#         self.button = ttk.Button(self, text='Click Me')
#         self.button['command'] = self.button_clicked
#         self.button.pack()
#
#     def button_clicked(self):
#         self.user_input = self.ui_var.get()
#         showinfo(title='Information',
#                  message=self.user_input)
#
#
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()
