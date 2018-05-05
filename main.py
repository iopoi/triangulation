
from tkinter import *
from primatives import *

class App:
    
    # init the UI
    def __init__(self, main):
        self.main = main
        main.title("Triangulation")
        
        # state variables
        self.draw_line_prev = None  # used to draw lines in polygon
        self.motion_line_id = None  # used to display polygon creating guiding line
        self.finish_dot_id = None  # used to flash the finishing point of the polygon
        self.finish_polygon = False  # flag for when polygon is complete
        
        self.triangulated = False  # flag for complete triangulation
        self.triangulation_draw_ids = []  # contains id's of the visual elements of the triangulation
        self.polygon_draw_ids = []  # contains id's of the visual elements of the polygon
        
        self.iterT = None  # stores iter methods for iter_triangulate
        self.iterMWT = None  # stores iter methods for mwt_triangualtion_iter
        
        # GUI elements/widgets
        self.width = 700
        self.height = 500
        self.C = Canvas(main, width=self.width, height=self.height)
        self.R1 = Button(main, text="reset polygon", command=self.reset_polygon)
        self.R1.grid(row=0, column=0)
        self.R2 = Button(main, text="reset triangulation", command=self.reset_triangulation)
        self.R2.grid(row=0, column=1)
        self.T = Button(main, text="triangulate", command=self.triangulate)
        self.T.grid(row=0, column=2)
        self.TI = Button(main, text="iter_triangulate", command=self.iter_triangulate)
        self.TI.grid(row=0, column=3)
        self.M = Button(main, text="mwt triangulation", command=self.mwt_triangualtion)
        self.M.grid(row=0, column=4)
        self.MI = Button(main, text="mwt triangulation iter", command=self.mwt_triangualtion_iter)
        self.MI.grid(row=0, column=5)
        self.C.grid(row=1, column=0, columnspan=6)
        
        # data structures
        self.polygon = Polygon()
        
        # key/mouse bindings
        main.bind('<Button 1>', self.click)
        main.bind('<Motion>', self.motion)


    # reset methods - active on button click
    
    def reset_triangulation(self):
        # reset polygon
        self.polygon.reset_order()
        if not self.polygon.check_counter_clockwise():
            self.polygon.flip_order()
        self.polygon.temp_head = self.polygon.head
    
        # get rid of all lines and dots
        for id in self.triangulation_draw_ids:
            self.C.after(1, self.C.delete, id)
    
        self.triangulation_draw_ids = []
    
        self.iterT = None
        self.iterMWT = None
    
        self.triangulated = False
    
        pass

    def reset_polygon(self):
    
        self.reset_triangulation()
    
        # get rid of all lines and dots
        for id in self.polygon_draw_ids + [self.motion_line_id, self.finish_dot_id]:
            self.C.after(1, self.C.delete, id)
    
        self.polygon_draw_ids = []
    
        self.draw_line_prev = None
        self.motion_line_id = None
        self.finish_dot_id = None
        self.finish_polygon = None
    
        self.polygon = Polygon()
    
        pass
    
    
    # triangulation methods - active on button click
    
    def triangulate(self):
        """Draws triangulation on the canvas"""
        if self.iterT is not None:
            print("cannot triangulate during iter triangulation")
            return
        
        if self.triangulated:
            print("already triangulated")
            return
        
        if self.finish_polygon is True:
            diags, ids = Triangulate(self.polygon, canvas=self.C, flip=True)
            # print(diags)  # debug
            self.triangulated = True
            # keep track of drawn items
            self.triangulation_draw_ids += ids
        return
        
    def iter_triangulate(self):
        """Iteratively draws triangulation on the canvas"""
        if self.triangulated:
            print("already triangulated")
            return
        
        # set iterator if it is None, this should be the first step in iteration
        if self.iterT is None and self.finish_polygon is True:
            self.iterT = iter_Triangulate(self.polygon, canvas=self.C, flip=True)
            print(self.iterT)
        
        # each step
        r = self.iterT.__next__()
        if r is True:
            # finished triangulation
            self.triangulated = True
            return r
        else:
            # keep track of drawn items
            self.triangulation_draw_ids += r[1]
        
        return r
    
    def mwt_triangualtion(self):
        """Draws minimum angle triangulation on the canvas"""
        if self.triangulated:
            print("already triangulated")
            return
        
        if self.finish_polygon is True:
            ids = MWTriangulation2b(self.polygon, canvas=self.C, flip=True)
            # keep track of drawn items
            self.triangulation_draw_ids += ids
            self.triangulated = True
        return
    
    def mwt_triangualtion_iter(self):
        """Iteratively draws minimum angle triangulation on the canvas"""
        if self.triangulated:
            print("already triangulated")
            return
        
        # set iterator if it is None, this should be the first step in iteration
        if self.iterMWT is None and self.finish_polygon is True:
            table, history, max_depth = MWTriangulation2c_iter(self.polygon, canvas=self.C, flip=True)
            self.iterMWT = mwt2e_traverse(self.polygon.head, self.polygon.head.next,
                                          self.polygon, self.C, table, history=history, depth=max_depth)
        
        # each step
        r = self.iterMWT.__next__()
        if r is True:
            # finished triangulation
            self.triangulated = True
            return r
        else:
            # keep track of drawn items
            self.triangulation_draw_ids = self.triangulation_draw_ids + r
            # self.triangulation_draw_ids.append(r)
        
        return r
    
    
    # draw methods for App class
    
    def draw_line(self, x1, y1, x2, y2, remove_id=None, color="black", flip=False):
        """draws line segment (x1,y1), (x2, y2)
           there is an option to remove a line
        """
        if flip:
            y1 *= -1
            y2 *= -1
        
        if remove_id is not None:
            self.C.after(1, self.C.delete, remove_id)
        
        id = self.C.create_line(x1, y1, x2, y2, fill=color)
        return id
    
    def draw_dot(self, x, y, remove_id=None, color="green", width=2, flip=False):
        """draws a dot at (x ,y)
           there is an option to remove a dot
        """
        if flip:
            y *= -1
        
        if remove_id is not None:
            self.C.after(1, self.C.delete, remove_id)
        
        id = self.C.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline=color, width=width)
        # print("dot", id)
        return id
    
    def cursor_in_range(self, target, cursor, range=10):
        """returns True if cursor is in range of a dot"""
        return (target[X] - range < cursor[X]) and \
               cursor[X] < (target[X] + range) and \
               (target[Y] - range) < cursor[Y] and \
               cursor[Y] < (target[Y] + range)
    
    # method bound to cursor click on the canvas
    def click(self, event, flip=True):
        if flip:
            flip = -1
        else:
            flip = 1
        x, y = event.x, flip * event.y
        
        # does not draw if polygon had been completed
        click_string_debug = 'click {}, {}'.format(x, y)
        if self.finish_polygon is True:
            click_string_debug = 'post polygon ' + click_string_debug
            return
        print(click_string_debug)
        
        # if new line intersects with the existing polygon then do not add to the polygon
        intersect = False
        for i in range(len(self.polygon.vertex_list) - 1):
            if IntersectProp(self.polygon.vertex_list[i], self.polygon.vertex_list[i + 1], \
                             (self.draw_line_prev[0], self.draw_line_prev[1]), (x, y)):
                intersect = True
                break
        
        current_polygon_len = len(self.polygon.vertex_list)
        if current_polygon_len == 0:
            # first point in the polygon
            self.polygon.add_vertex(Vertex(x, y))
        else:
            # next point in the polygon
            
            # do nothing if there is an intersection
            if intersect:
                print("intersection")
                return
            
            first_vertex = self.polygon.get_head()
            # check for final click of polygon
            if self.cursor_in_range(first_vertex, (x, y)) and len(
                self.polygon.vertex_list) > 2:
                
                x, y = first_vertex[X], first_vertex[Y]
                self.finish_polygon = True
                
                # self.polygon.head.print_loop()  # debug
                # print([str(i) for i in self.polygon.vertex_list])  # debug
                # print([str(i) for i in self.polygon.flipped_vertex_list])  # debug
                
                # if polygon is not counterclockwise then reverse the point order
                # print("finished polygon")
                # print("is counterclockwise", self.polygon.check_counter_clockwise())  # debug
                if not self.polygon.check_counter_clockwise():
                    print("not counter clockwise")
                    print("reversing point order now")
                    self.polygon.flip_order()
                    # print("post order flip")  # debug
                    # print("vertex list")  # debug
                    # print([str(i) for i in self.polygon.vertex_list])  # debug
                    # print("flipped vertex list")  # debug
                    # print([str(i) for i in self.polygon.flipped_vertex_list])  # debug
                    print("new vertex ording")
                    self.polygon.head.print_loop()  # debug
                    print("safety check - is counterclockwise = ", self.polygon.check_counter_clockwise())
                
                # remove guiding visualizations for polygon drawing
                if self.finish_dot_id is not None:
                    self.C.after(1, self.C.delete, self.finish_dot_id)
                    self.finish_dot_id = None
                if self.motion_line_id is not None:
                    self.C.after(1, self.C.delete, self.motion_line_id)
                    self.motion_line_id = None
            else:
                # not first or last point or intersecting line
                self.polygon.add_vertex(Vertex(x, y))

        # draw line on canvas
        if self.draw_line_prev is None:
            # this is for the first point of the first line
            self.draw_line_prev = (x, y)
        else:
            id = self.draw_line(self.draw_line_prev[0], self.draw_line_prev[1],
                                x, y, flip=True, color="#240031")
            self.polygon_draw_ids.append(id)
            self.draw_line_prev = (x, y)
        
        # self.polygon.print_polygon()  # debug
        # self.polygon.print_vertecies_iter()  # debug
    
    # method bound to cursor motion on the canvas
    def motion(self, event, flip=True):
        if flip:
            flip = -1
        else:
            flip = 1

        if self.finish_polygon is True:
            return
        
        x, y = event.x, event.y

        # check for intersection
        intersect = False
        for i in range(len(self.polygon.vertex_list) - 1):
            if IntersectProp(self.polygon.vertex_list[i], self.polygon.vertex_list[i + 1], \
                             (self.draw_line_prev[0], self.draw_line_prev[1]), (x, flip * y)):
                intersect = True
                break
        # if line intersects the existing polygon the guiding line turns red
        if intersect:
            motion_line_color = "red"
        else:
            motion_line_color = "blue"
        
        # draw new guiding line and remove old guiding line
        if self.draw_line_prev is not None:
            self.motion_line_id = self.draw_line(self.draw_line_prev[0], \
                                                 flip * self.draw_line_prev[1], \
                                                 x, y, color=motion_line_color, \
                                                 remove_id=self.motion_line_id, flip=False)

        # if cursor is in range of the finish point then it adds or removes a green dot on tbe finish point
        first_coord = self.polygon.head
        if first_coord is not None and self.cursor_in_range((first_coord[X], flip * first_coord[Y]), (x, y)):
            self.finish_dot_id = self.draw_dot(first_coord[X], \
                                               first_coord[Y], \
                                               remove_id=self.finish_dot_id, flip=True)
        else:
            if self.finish_dot_id is not None:
                self.C.after(1, self.C.delete, self.finish_dot_id)
                self.finish_dot_id = None

main = Tk()
my_gui = App(main)
main.mainloop()
