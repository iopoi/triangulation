from tkinter import *
from primatives import *


class App:
    
    # init the UI
    def __init__(self, main):
        self.main = main
        main.title("Triangulation")
        
        self.C = Canvas(main, width=400, height=400)
        self.C.grid(row=0, column=0)
        
        self.draw_line_prev = None
        self.motion_line_id = None
        self.finish_dot_id = None
        self.finish_polygon = False
        
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
    
    def draw_dot(self, x, y, remove_id=None, color="green", width=2):
        # there is an option to remove a line
        if remove_id is not None:
            self.C.after(1, self.C.delete, remove_id)
        
        id = self.C.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline=color, width=width)
        print("dot", id)
        return id
    
    def cursor_in_range(self, target, cursor, range=10):
        return (target[X] - range < cursor[X]) and \
               cursor[X] < (target[X] + range) and \
               (target[Y] - range) < cursor[Y] and \
               cursor[Y] < (target[Y] + range)
    
    def click(self, event):
        
        if self.finish_polygon is True:
            return
        
        x, y = event.x, event.y
        print('click {}, {}'.format(x, y))
        
        # check for validity
        self.simple_chain.append((x, y))
        
        first_coord = self.simple_chain[0]
        if self.cursor_in_range(first_coord, (x, y)) and len(self.simple_chain) > 2:
            # if final click of polygon
            x, y = first_coord
            self.finish_polygon = True
            # remove guiding visualizations
            if self.finish_dot_id is not None:
                self.C.after(1, self.C.delete, self.finish_dot_id)
                self.finish_dot_id = None
            if self.motion_line_id is not None:
                self.C.after(1, self.C.delete, self.motion_line_id)
                self.motion_line_id = None
        
        if self.draw_line_prev is None:
            # this is for the first point of the first line
            self.draw_line_prev = (x, y)
        else:
            self.draw_line(self.draw_line_prev[0], self.draw_line_prev[1], x, y)
            self.draw_line_prev = (x, y)
        
        print(self.simple_chain)
    
    def motion(self, event):
        print(self.finish_polygon)
        if self.finish_polygon is True:
            return
        
        x, y = event.x, event.y
        self.motion_line_id = self.draw_line(self.draw_line_prev[0], \
                                             self.draw_line_prev[1], \
                                             x, y, color="blue", \
                                             remove_id=self.motion_line_id)
        
        first_coord = self.simple_chain[0]
        print("first_coord", first_coord)
        # if (first_coord[X]-10 < x) and x < (first_coord[X]+10) and (first_coord[Y]-10) < y and y < (first_coord[
        # Y]+10):
        if self.cursor_in_range(first_coord, (x, y)):
            self.finish_dot_id = self.draw_dot(first_coord[X], \
                                               first_coord[Y], \
                                               remove_id=self.finish_dot_id)
        else:
            if self.finish_dot_id is not None:
                self.C.after(1, self.C.delete, self.finish_dot_id)
                self.finish_dot_id = None
        
        print('move  {}, {}'.format(x, y))


main = Tk()
my_gui = App(main)
main.mainloop()

