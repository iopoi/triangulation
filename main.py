from tkinter import *
from primatives import *


class App:
    
    # init the UI
    def __init__(self, main):
        self.main = main
        main.title("Triangulation")
        
        # state variables
        self.draw_line_prev = None
        self.motion_line_id = None
        self.finish_dot_id = None
        self.finish_polygon = False
        
        self.triangulated = False
        
        self.iterT = None
        
        # GUI elements/widgets
        self.width = 700
        self.height = 500
        self.C = Canvas(main, width=self.width, height=self.height)
        self.B = Button(main, text="triangulate", command=self.triangulate)
        self.B.grid(row=0, column=0)
        self.A1 = Button(main, text="start_iter_triangulate", command=self.start_iter_triangulate)
        self.A1.grid(row=0, column=1)
        self.A2 = Button(main, text="iter_triangulate", command=self.iter_triangulate)
        self.A2.grid(row=0, column=2)
        self.C.grid(row=1, column=0, columnspan=3)

        # data structures
        self.simple_chain = []
        self.polygon = Polygon()
        
        # key/mouse bindings
        main.bind('<Button 1>', self.click)
        main.bind('<Motion>', self.motion)
    
    def triangulate(self):
        print("finish_polygon", self.finish_polygon)
        if self.finish_polygon is True:
            diags = Triangulate(self.polygon, canvas=self.C, flip=True)
            print(diags)
            self.triangulated = True
        
        return
    
    def start_iter_triangulate(self):
        print("finish_polygon", self.finish_polygon)
        if self.finish_polygon is True:
            self.iterT = iter_Triangulate(self.polygon, canvas=self.C, flip=True)
            print(self.iterT)
    
    def iter_triangulate(self):
        r = self.iterT.__next__()
        print("diag", r)
        # self.triangulated = True
        return r
    
    def draw_line(self, x1, y1, x2, y2, remove_id=None, color="black", flip=False):
        # there is an option to remove a line
        if flip:
            y1 *= -1
            y2 *= -1
        
        if remove_id is not None:
            self.C.after(1, self.C.delete, remove_id)
        
        id = self.C.create_line(x1, y1, x2, y2, fill=color)
        print("line", id)
        return id
    
    def draw_dot(self, x, y, remove_id=None, color="green", width=2, flip=False):
        # there is an option to remove a line
        if flip:
            y *= -1
        
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
    
    def click(self, event, flip=True):
        if flip:
            flip = -1
        else:
            flip = 1
        # x, y = event.x, event.y
        x, y = event.x, flip * event.y
        
        if self.finish_polygon is True:
            print('post polygon click {}, {}'.format(x, y))
            return
        
        print('click {}, {}'.format(x, y))
        
        current_polygon_len = len(self.polygon.vertex_list)
        if current_polygon_len == 0:
            self.simple_chain.append((x, y))
            self.polygon.add_vertex(Vertex(x, y))
        else:
            first_coord = self.simple_chain[0]
            first_vertex = self.polygon.get_head()
            if self.cursor_in_range(first_coord, (x, y)) and len(
                self.simple_chain) > 2:  # and current_polygon_len != 0:
                # if final click of polygon
                x, y = first_coord
                self.finish_polygon = True
                print("finished polygon")
                print(self.polygon.check_counter_clockwise())
                # remove guiding visualizations
                if self.finish_dot_id is not None:
                    self.C.after(1, self.C.delete, self.finish_dot_id)
                    self.finish_dot_id = None
                if self.motion_line_id is not None:
                    self.C.after(1, self.C.delete, self.motion_line_id)
                    self.motion_line_id = None
            else:
                self.simple_chain.append((x, y))
                self.polygon.add_vertex(Vertex(x, y))
        
        if self.draw_line_prev is None:
            # this is for the first point of the first line
            self.draw_line_prev = (x, y)
        else:
            self.draw_line(self.draw_line_prev[0], self.draw_line_prev[1], x, y, flip=True)
            self.draw_line_prev = (x, y)
        
        print(self.simple_chain)
        self.polygon.print_polygon()
        self.polygon.print_vertecies_iter()
    
    def motion(self, event, flip=True):
        if flip:
            flip = -1
        else:
            flip = 1
        # print(self.finish_polygon)
        if self.finish_polygon is True:
            return

        x, y = event.x, event.y
        self.motion_line_id = self.draw_line(self.draw_line_prev[0], \
                                             flip * self.draw_line_prev[1], \
                                             x, y, color="blue", \
                                             remove_id=self.motion_line_id, flip=False)

        first_coord = self.simple_chain[0]
        print("first_coord", first_coord)
        if self.cursor_in_range((first_coord[X], flip * first_coord[Y]), (x, y)):
            self.finish_dot_id = self.draw_dot(first_coord[X], \
                                               first_coord[Y], \
                                               remove_id=self.finish_dot_id, flip=True)
        else:
            if self.finish_dot_id is not None:
                self.C.after(1, self.C.delete, self.finish_dot_id)
                self.finish_dot_id = None
        
        print('move  {}, {}'.format(x, y))
        
main = Tk()
my_gui = App(main)
main.mainloop()

