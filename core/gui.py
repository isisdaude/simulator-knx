import pyglet
from time import time




class Rectangle(object):
    '''Draws a rectangle into a batch.'''
    def __init__(self, x1, y1, x2, y2, batch):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', [100, 200, 120, 100] * 4)
        )

class TextWidget(object): # text box object (widget)
    def __init__(self, text, x, y, width, batch):
        background = pyglet.graphics.OrderedGroup(0)
        foreground = pyglet.graphics.OrderedGroup(1)
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
            dict(color=(0, 0, 0, 255)) # black
        )

        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.rectangle = Rectangle(x - pad, y - pad,
                                   x + width + pad, y + height + pad, batch)
        # self.text_label = pyglet.text.Label('', x=x, y=y, batch=batch)

    def hit_test(self, x, y): # to check if mouse click is inside a text box
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)



class GUIWindow(pyglet.window.Window):
    def __init__(self):
        super(GUIWindow, self).__init__(800, 600, caption='KNX Simulation Window', resizable=True)
        self.batch = pyglet.graphics.Batch() #

        self.command_label = pyglet.text.Label('Enter your command',
                                  font_name='Times New Roman',
                                  font_size=36,
                                  x=300, y=500,
                                  anchor_x='center', anchor_y='center')
        self.simtime_label = pyglet.text.Label("Simulation Time: 0", # init the simulation time display
                                  font_name='Times New Roman',
                                  font_size=36,
                                  x=self.width//2, y=self.height//2,
                                  anchor_x='center', anchor_y='center')
        # self.start_time = time()
        self.widgets = [
            TextWidget('text1', 200, 100, 100, self.batch),
            TextWidget('text2', 200, 60, 100, self.batch),
        ]
        self.text_cursor = self.get_system_mouse_cursor('text')
        self.focus = None
        self.set_focus(self.widgets[0])
        self.typein = '' # store the text typed by the user



    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)
        print("focus: \n", focus)

    def on_draw(self):
        # sim_time = time() - self.start_time
        self.clear()
        self.command_label.draw()
        self.simtime_label.draw()
        self.batch.draw()
        self.push_handlers(self.focus.caret)

    def on_mouse_motion(self, x, y, dx, dy): # change cursor when mouse is over text box
        for widget in self.widgets:
            if widget.hit_test(x, y): # hit_test to check text boxes, can be other elements
                self.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                self.set_focus(widget)
                break
        else:
            self.set_focus(None)

    # def on_activate(self): # When the window is created or the user click on it
    #     print("window activated\n")
    #     self.label = pyglet.text.Label("Window activated",
    #                               font_name='Times New Roman',
    #                               font_size=36,
    #                               x=window.width//4, y=window.height//4,
    #                               anchor_x='center', anchor_y='center')

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)
            self.typein += text
            self.focus.text_label.text = self.typein

        print("on text\n")

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                dir = -1
            else:
                dir = 1

            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                dir = 0

            self.set_focus(self.widgets[(i + dir) % len(self.widgets)])

        elif symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

        else: # if user writes something
            # if self.focus:
            #     letter_label = pyglet.text.Label(str(symbol), # init the simulation time display
            #                               font_name='Times New Roman',
            #                               font_size=10,
            #                               x=self.focus.layout.x, y=self.focus.layout.y,
            #                               anchor_x='center', anchor_y='center',
            #                               batch = self.batch)

            print("symbol: \n", symbol)
            print("modifiers: \n", modifiers)


    # def on_resize(self, width, height):
    #     print("Window is resized\n")




start_time = time()

def update_window(dt, window):
    sim_time = time() - start_time
    window.simtime_label = pyglet.text.Label("Simulation Time: {:.2f}".format(sim_time),
                              font_name='Times New Roman',
                              font_size=36,
                              x=window.width//2, y=window.height//2,
                              anchor_x='center', anchor_y='center')

    # dtt = pyglet.clock.tick()
    print(f"doing update at {sim_time} \n")
    # print(f"FPS is {pyglet.clock.get_fps()}")

    #window.set_caption(f"Simulation time: {current_time}")

if __name__ == '__main__':
    window = GUIWindow()
    pyglet.clock.schedule_interval(update_window, 2, window)
    pyglet.app.run()

# pyglet.clock.schedule_interval(update, 1)
#pyglet.clock.schedule(update)  ## schedule to run the fct at the highest frequency possible
# Dismiss the dialog after 5 seconds.
#pyglet.clock.schedule_once(dismiss_dialog, 5.0)  ## for one-shot events
#pyglet.clock.unschedule(update)  ## to remove the fct from the scheduler list

# pyglet.app.run()

print("pyglet is finished\n")
