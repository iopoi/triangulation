
from tkinter import *

class App:
    
    # init the UI
    def __init__(self, main):
        self.main = main
        main.title("Traingulation")
        
        self.C = Canvas(main, width=400, height=400)
        self.C.grid(row=0, column=0)
        
        self.draw_line_prev = None
        self.motion_line_id = None
        
        # data structure
        self.simple_chain = []
        
        main.bind('<Button 1>', self.click)
        main.bind('<Motion>', self.motion)
    
    def draw_line(self, x1, y1, x2, y2, remove_id=None, color="black"):
        # there is an option to remove a line
        if remove_id is not None:
            self.C.after(1, self.C.delete, remove_id)
        
        id = self.C.create_line(x1, y1, x2, y2, fill=color)
        print("line", id)
        return id
    
    def click(self, event):
        x, y = event.x, event.y
        print('click {}, {}'.format(x, y))
        
        # check for validity
        self.simple_chain.append((x, y))
        
        if self.draw_line_prev is None:
            # this is for the first point of the first line
            self.draw_line_prev = (x, y)
        else:
            self.draw_line(self.draw_line_prev[0], self.draw_line_prev[1], x, y)
            self.draw_line_prev = (x, y)
        
        print(self.simple_chain)
    
    def motion(self, event):
        x, y = event.x, event.y
        self.motion_line_id = self.draw_line(self.draw_line_prev[0], \
                                             self.draw_line_prev[1], \
                                             x, y, color="blue", \
                                             remove_id=self.motion_line_id)
        print('move  {}, {}'.format(x, y))


main = Tk()
my_gui = App(main)
main.mainloop()





