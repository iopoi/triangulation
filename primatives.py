
# reimplementation of primitive methods from tri.c - http://cs.smith.edu/~jorourke/books/ftp.html

from operator import xor

X = 0
Y = 1

def Area2(a, b, c):
   return (b[X] - a[X]) * (c[Y] - a[Y]) - \
          (c[X] - a[X]) * (b[Y] - a[Y])

def AreaSign(a, b, c):
    area2 = (b[X]-a[X])*(c[Y]-a[Y]) - \
            (c[X]-a[X])*(b[Y]-a[Y])
    if area2 > 0.5:
        return  1
    elif area2 < -0.5:
        return -1
    else:
        return 0

def Collinear(a, b, c):
    return AreaSign(a, b, c) == 0

def Left(a, b, c):
   return AreaSign(a, b, c) > 0

def LeftOn(a, b, c):
   return AreaSign(a, b, c) >= 0

def IntersectProp(a, b, c, d):
    if Collinear(a, b, c) or \
        Collinear(a, b, d) or \
        Collinear(c, d, a) or \
        Collinear(c, d, b):
        return False
    
    return xor(Left(a, b, c), Left(a, b, d)) and \
           xor(Left(c, d, a), Left(c, d, b))

def	Between(a, b, c):
   if not Collinear(a, b, c):
      return False

   # If ab not vertical, check betweenness on x; else on y
   if a[X] != b[X]:
      return ((a[X] <= c[X]) and (c[X] <= b[X])) or \
             ((a[X] >= c[X]) and (c[X] >= b[X]))
   else:
      return ((a[Y] <= c[Y]) and (c[Y] <= b[Y])) or \
             ((a[Y] >= c[Y]) and (c[Y] >= b[Y]))

def	Intersect(a, b, c, d):
   if IntersectProp(a, b, c, d):
       return True
   elif Between(a, b, c) or \
       Between(a, b, d) or \
       Between(c, d, a) or \
       Between(c, d, b):
       return True
   else:
       return False

def Diagonalie(a, b):
    # For each edge(c, c1) of P
    # c = a.get_polygon().head
    c = a.get_polygon().temp_head  # TODO - testing this line
    c_index = c.index
    c1 = c.next
    while (c1.index != c_index):
        # Skip edges incident to a or b
        if (c.index != a.index) and (c1.index != a.index) and \
            (c.index != b.index) and (c1.index != b.index) and \
            Intersect(a.coord, b.coord, c.coord, c1.coord):
            return False
        c = c.next
        c1 = c.next
    return True

def InCone(a, b):
    # a0, a, a1 are consecutive vertices
    a1 = a.next
    a0 = a.prev

    # If a is a convex vertex ...
    if LeftOn(a.coord, a1.coord, a0.coord):
       return Left(a.coord, b.coord, a0.coord) and \
           Left(b.coord, a.coord, a1.coord)

    # Else a is reflex:
    return not (LeftOn(a.coord, b.coord, a1.coord) and \
               LeftOn(b.coord, a.coord, a0.coord))

def Diagonal(a, b):
    return InCone(a, b) and InCone(b, a) and Diagonalie(a, b)




def EarInit(polygon):
    # v0, v1, v2  -  three consecutive vertices
    
    # Initialize v1.ear for all vertices.
    # start at the head vertex and loop around
    v1 = polygon.get_head()
    start_index = v1.index
    # print("newpath\n")
    v2 = v1.next
    v0 = v1.prev
    v1.ear = Diagonal(v0, v2)
    v1 = v1.next
    while start_index != v1.index:
        v2 = v1.next
        v0 = v1.prev
        v1.ear = Diagonal( v0, v2 )
        v1 = v1.next
    # print("closepath stroke\n\n")


# /*---------------------------------------------------------------------
# Prints out n-3 diagonals (as pairs of integer indices)
# which form a triangulation of P.
# ---------------------------------------------------------------------*/

def draw_dot(canvas, x, y, remove_id=None, color="green", width=2, flip=False):
    if flip:
        flip = -1
    else:
        flip = 1
    # there is an option to remove a line
    if remove_id is not None:
        # canvas.after(1, canvas.delete, remove_id)
        canvas.after(300, canvas.delete, remove_id)

    id = canvas.create_oval(x - 5, flip*y - 5, x + 5, flip*y + 5, fill=color, outline=color, width=width)
    print("dot", id, color, "coord:", x, flip*y)
    return id


def Triangulate(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    print("counterclockwise check:", polygon.check_counter_clockwise())
    if not polygon.check_counter_clockwise():
        print("not clounterclockwise")
        return
    # v0, v1, v2, v3, v4  -  five consecutive vertices
    n = len(polygon.vertex_list) # number of vertices; shrinks to 3
    earfound = False # for debugging and error detection only
    
    print("head loop")
    polygon.head.print_loop()

    
    debug_v2_id = None
    
    diags = []

    EarInit(polygon)
    
    polygon.temp_head = polygon.head
    
    print("\nnewpath\n")
    # Each step of outer loop removes one ear.
    
    while n > 3:
        print(n)
        # Inner loop searches for an ear.
        # if n == 8:
        #     print("break")
        
        v2 = polygon.temp_head
        debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="red", remove_id=debug_v2_id, flip=temp_flip)
        earfound = False
        
        do_while_flag = True
        while (v2.index != polygon.temp_head.index) or do_while_flag:
            do_while_flag = False
            if v2.ear is True:
                earfound = True
                # Ear found. Fill variables.
                v3 = v2.next
                v4 = v3.next
                v1 = v2.prev
                v0 = v1.prev
            
                # (v1,v3) is a diagonal
                # PrintDiagonal( v1, v3 )
                print("diag", v1.coord, v3.coord)
                if canvas is not None:
                    canvas.create_line(v1.coord[X], flip*v1.coord[Y], v3.coord[X], flip*v3.coord[Y], fill="dark green")
                diags.append((v1, v3))
                
                # Update earity of diagonal endpoints
                v1.ear = Diagonal(v0, v3)
                v3.ear = Diagonal(v1, v4)
                
                # Cut off the ear v2
                v1.next = v3
                v3.prev = v1
                polygon.temp_head = v3	# In case the head was v2.
                n -= 1
                break  # out of inner loop; resume outer loop
                # end if ear found
            v2 = v2.next
            debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="red", remove_id=debug_v2_id, flip=temp_flip)

        print("debug - internal ploygon of size", n)
        polygon.temp_head.print_loop()

        if not earfound:
            i = None
            print("internal ploygon")
            v2.print_loop(canvas)
            # polygon.print_vertecies_iter()
            # print()
            print("%%Error in Triangulate:  No ear found.\n")
            # PrintPoly()
            print("showpage\n%%%%EOF\n")
            raise RuntimeError("Error in Triangulate:  No ear found.")
            
        
    # end outer while loop
    print("closepath stroke\n\n")
    return diags


def iter_Triangulate(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    print("counterclockwise check:", polygon.check_counter_clockwise())
    if not polygon.check_counter_clockwise():
        print("not clounterclockwise")
        return
    # v0, v1, v2, v3, v4  -  five consecutive vertices
    n = len(polygon.vertex_list)  # number of vertices; shrinks to 3
    earfound = False  # for debugging and error detection only
    
    print("head loop")
    polygon.head.print_loop()
    
    debug_v2_id = None
    
    # diags = []
    
    EarInit(polygon)
    
    polygon.temp_head = polygon.head
    
    print("\nnewpath\n")
    # Each step of outer loop removes one ear.
    
    while n > 3:
        print(n)
        # Inner loop searches for an ear.
        # if n == 8:
        #     print("break")
        
        v2 = polygon.temp_head
        debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="red", remove_id=debug_v2_id, flip=temp_flip)
        earfound = False
        
        do_while_flag = True
        while (v2.index != polygon.temp_head.index) or do_while_flag:
            do_while_flag = False
            if v2.ear is True:
                earfound = True
                # Ear found. Fill variables.
                v3 = v2.next
                v4 = v3.next
                v1 = v2.prev
                v0 = v1.prev
                
                # (v1,v3) is a diagonal
                # PrintDiagonal( v1, v3 )
                print("diag", v1.coord, v3.coord)
                if canvas is not None:
                    canvas.create_line(v1.coord[X], flip * v1.coord[Y], v3.coord[X], flip * v3.coord[Y],
                                       fill="dark green")
                yield((v1, v3))
                
                # Update earity of diagonal endpoints
                v1.ear = Diagonal(v0, v3)
                v3.ear = Diagonal(v1, v4)
                
                # Cut off the ear v2
                v1.next = v3
                v3.prev = v1
                polygon.temp_head = v3  # In case the head was v2.
                n -= 1
                break  # out of inner loop; resume outer loop
                # end if ear found
            v2 = v2.next
            debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="red", remove_id=debug_v2_id, flip=temp_flip)
        
        print("debug - internal ploygon of size", n)
        polygon.temp_head.print_loop()
        
        if not earfound:
            i = None
            print("internal ploygon")
            v2.print_loop(canvas)
            # polygon.print_vertecies_iter()
            # print()
            print("%%Error in Triangulate:  No ear found.\n")
            # PrintPoly()
            print("showpage\n%%%%EOF\n")
            raise RuntimeError("Error in Triangulate:  No ear found.")
    
    # end outer while loop
    print("closepath stroke\n\n")
    # return diags



# Data Structures to support predicates
class Polygon:
    
    def __init__(self):
        # the polygon starts with zero points
        self.head = None
        self.temp_head = None
        self.current = None
        self.vertex_list = []
        
    def get_head(self):
        return self.head
    
    def get_vertex(self, i):
        return self.vertex_list[i]
    
    def __getitem__(self, item):
        return self.vertex_list[item]
        
    def add_vertex(self, v):
        if len(self.vertex_list) < 1:
            self.head = v
            self.temp_head = v
            self.current = v
            self.vertex_list.append(v)
            v.set_index(0)
            v.set_prev(v)
            v.set_next(v)
            v.set_polygon(self)
        else:
            # set index
            v.set_index(len(self.vertex_list))
            # add to master list
            self.vertex_list.append(v)
            # set reference to polygon object
            v.set_polygon(self)

            current = self.current
            next = self.current.next
            new = v
            
            # set prev and next for new vertex
            new.set_prev(current)
            new.set_next(next)
            # connect old prev and next to new vertex
            current.set_next(new)
            next.set_prev(new)
            # set new current to new vertex
            self.current = new
        
    def print_polygon(self):
        print([v.index for v in self.vertex_list])
            # print(v.index)
    
    def print_vertecies_iter(self):
        v = self.head
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "head")
        v = v.next
        while(v.index != 0):
            print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear)
            v = v.next
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "should be head")

    def print_vertecies_temp_iter(self):
        v = self.temp_head
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "head")
        v = v.next
        while(v.index != 0):
            print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear)
            v = v.next
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "should be head")

    def check_counter_clockwise(self):
        current = self.head
        right_most = current
        current = current.next
        while(self.head is not current):
            print(current)
            if current.coord[X] > right_most.coord[X]:
                right_most = current
            elif current.coord[X] == right_most.coord[X] and current.coord[Y] > right_most.coord[Y]:
                right_most = current
            current = current.next
        return Left(right_most.prev.coord, right_most.coord, right_most.next.coord)
        # current = self
        # print(current, current.coord, current.index, "next:", current.next, "first", first_index, first)
        # if canvas is not None:
        #     draw_dot(canvas, current.coord[X], current.coord[Y], color="yellow", width=1, flip=True)
        # current = current.next
        # while (self is not current):
        #     print(current, current.coord, current.index, "next:", current.next, "first", first_index, first)
        #     if canvas is not None:
        #         draw_dot(canvas, current.coord[X], current.coord[Y], color="yellow", width=1, flip=True)
        #     current = current.next


class Vertex:
    
    def __init__(self, x, y, index=None, prev=None, next=None):
        self.index = index
        self.coord = (x,y)
        self.prev = prev
        self.next = next
        self.polygon = None
        self.ear = None
        
    def get_polygon(self):
        return self.polygon

    def set_index(self, i):
        self.index = i

    def set_prev(self, p):
        self.prev = p

    def set_next(self, n):
        self.next = n
    
    def set_polygon(self, poly):
        self.polygon = poly
        
    def set_ear(self, b):
        self.ear = b
        
    def print_loop(self, canvas=None):
        first = self
        # first_coord = first.coord
        first_index = first.index
        current = self
        print(current, current.coord, current.index, "next:", current.next, "first", first_index, first)
        if canvas is not None:
            draw_dot(canvas, current.coord[X], current.coord[Y], color="yellow", width=1, flip=True)
        current = current.next
        while(self is not current):
            print(current, current.coord, current.index, "next:", current.next, "first", first_index, first)
            if canvas is not None:
                draw_dot(canvas, current.coord[X], current.coord[Y], color="yellow", width=1, flip=True)
            current = current.next

    # def __str__(self):
    #     return "index:"+str(self.index)+", coord:"+str(self.coord)+", prev:"+str(self.prev)+", next:"+str(self.next)
    

def points_to_polygon(l):
    # takes a list of coordinates, input should be a simple chain
    # this method is mainly for testing predicates
    # TODO - this will take in a list of points from
    polygon = Polygon()
    for i in l:
        polygon.add_vertex(Vertex(i[X], i[Y]))
    return polygon


