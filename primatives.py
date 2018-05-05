
# reimplementation of primitive methods from tri.c - http://cs.smith.edu/~jorourke/books/ftp.html

from operator import xor
from math import acos, sqrt, degrees
from time import sleep
from random import shuffle

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
        canvas.after(500, canvas.delete, remove_id)

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
    ids = []
    
    EarInit(polygon)
    
    polygon.temp_head = polygon.head
    
    print("\nnewpath\n")
    # Each step of outer loop removes one ear.
    
    while n > 3:
        print(n)
        
        v2 = polygon.temp_head
        debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="firebrick3", remove_id=debug_v2_id, flip=temp_flip)
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
                    id = canvas.create_line(v1.coord[X], flip*v1.coord[Y], v3.coord[X], flip*v3.coord[Y], fill="forest green")
                    ids.append(id)
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
            debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="firebrick3", remove_id=debug_v2_id, flip=temp_flip)

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
    # debug_v2_id
    canvas.after(1, canvas.delete, debug_v2_id)
    return diags, ids


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
        
        v2 = polygon.temp_head
        debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="firebrick3", remove_id=debug_v2_id, flip=temp_flip)
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
                id = None
                if canvas is not None:
                    id = canvas.create_line(v1.coord[X], flip * v1.coord[Y], v3.coord[X], flip * v3.coord[Y],
                                       fill="green3")
                yield((v1, v3), [id, debug_v2_id])
                
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
            debug_v2_id = draw_dot(canvas, v2.coord[X], v2.coord[Y], color="firebrick3", remove_id=debug_v2_id, flip=temp_flip)
        
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
    canvas.after(1, canvas.delete, debug_v2_id)
    yield True
    # return diags

def distance(a, b):
    return sqrt((b[X]-a[X])^2+((b[Y]-a[Y])^2))

def distance3(a, b, c):
    return distance(a, b)+distance(b, c)+distance(c, a)

# def angle(a, b, c):
#     vect1 = (a[X] - b[X], a[Y] - b[Y])
#     print(vect1)
#     vect2 = (c[X] - b[X], c[Y] - b[Y])
#     print(vect2)
#     dot = lambda v, w: v[X] * w[X] + v[Y] * w[Y]
#     norm = lambda v: sqrt(dot(v,v))
#     print(dot(vect1, vect2))
#     print(norm(vect1))
#     print(norm(vect2))
#     print(norm(vect1) * norm(vect2))
#     print(dot(vect1, vect2)/(norm(vect1)*norm(vect2)))
#     print(acos(dot(vect1, vect2) / (norm(vect1) * norm(vect2))))
#     print(math.degrees(acos(dot(vect1, vect2) / (norm(vect1) * norm(vect2)))))
#     return acos(dot(vect1, vect2) / (norm(vect1) * norm(vect2)))

# def angle(a, b, c):
#     vect1 = (a[X] - b[X], a[Y] - b[Y])
#     vect2 = (c[X] - b[X], c[Y] - b[Y])
#     dot = lambda v, w: v[X]*w[X]+v[Y]*w[Y]

def angle(a, b, c):
    if a == b or b == c or c == a:
        print("cannot calculate angle with repeat coordinates")
        raise ValueError
    if Collinear(a, b, c):
        return 0
    vect1 = (a[X] - b[X], a[Y] - b[Y])
    vect2 = (c[X] - b[X], c[Y] - b[Y])
    dot = lambda v, w: v[X] * w[X] + v[Y] * w[Y]
    norm = lambda v: sqrt(dot(v,v))
    return acos(dot(vect1, vect2) / (norm(vect1) * norm(vect2)))

def MWTriangulation(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    # this will maximizes the smallest angle during triangulation
    table = {}
    
    def mwt(i, j):
        id = canvas.create_line(i.coord[X], flip * i.coord[Y], j.coord[X], flip * j.coord[Y], fill="dark blue")
        canvas.after(1000, canvas.delete, id)
        # sleep(1)
        # table_id = tuple(sorted([i.index, j.index]))  # sorted is bad because ij has a direction different from ji
        table_id = tuple([i.index, j.index])
        print(table_id, table)

        # if table_id in [(3,1),(0,2)]:
        #     print("break")

        # check for the same point
        if i.index == j.index:
            # table[table_id] = 0
            # table[table_id] = 9999
            table[table_id] = (9999, -1)  # keep track of tuple, i don't think there is any
            print("### this should not happend ###")
            return table[table_id]
        
        # check if answer is pre-computed
        if table.get(table_id, None) is not None:
            return table[table_id]

        # if i.prev.index == j.next.index:
        #     # table[table_id] = 0
        #     table[table_id] = 9999
        #     return table[table_id]

        # get all points, k, in sight and left of line ij
        ks = []
        
        potential_list = []
        current = i.prev
        print(table_id, "- current list of potential in the loop")
        while current.index != j.index:
            potential_list.append(current)
            print(current.index, " - append to potential list")
            current = current.prev
            
        # for v in polygon.vertex_list:
        print(table_id, "- current list of ks")
        for v in potential_list:
            if v.index == i.index or v.index == j.index:
                continue
            temp1 = Left(i.coord, j.coord, v.coord)
            temp2 = Diagonal(i, v)
            temp3 = Diagonal(v, j)
            # temp4 = i.next.index == v.index or i.prev.index == v.index
            # temp5 = j.prev.index == v.index or j.next.index == v.index
            temp4 = i.prev.index == v.index
            temp5 = j.next.index == v.index
            # print("temp1", temp1)
            # print("temp2", temp2)
            # print("temp3", temp3)
            # print("temp4", temp4)
            # print("temp5", temp5)
            # if Left(i.coord, j.coord, v.coord) and Diagonal(i, v) and Diagonal(j, v):
            if temp1 and (temp2 or temp4) and (temp3 or temp5):
                ks.append(v)
                print(v.index, " - append to ks")
                # print("vertex", v.index, "appended")
            else:
                pass
                # print("vertex", v.index, "fail")
        print("final ks list:", ks)
        if len(ks) == 0:
            # table[table_id] = 0
            table[table_id] = (99999, -1)
            return table[table_id]
            # return table[table_id]  #return tuple
        else:
            # m = 0
            m = (0, -1)  # fake tuple
            for k in ks:
                a1 = angle(i.coord, j.coord, k.coord)
                a2 = angle(k.coord, i.coord, j.coord)
                a3 = angle(j.coord, k.coord, i.coord)
                # min_angle = min(a1,a2,a3)
                min_angle = (min(a1,a2,a3), k.index)
                # min_angle = (degrees(min(a1,a2,a3)), k.index)
                # min_angle = min(angle(i.coord, j.coord, k.coord),
                #                 angle(k.coord, i.coord, j.coord),
                #                 angle(j.coord, k.coord, i.coord))
                min_list = [min_angle]
                if i.prev.index != k.index:
                    m1 = mwt(i, k)
                    # m1 = mwt(i, k)[0]
                    min_list.append(m1)
                if k.index != j.next.index:
                    m2 = mwt(k, j)
                    # m2 = mwt(k, j)[0]
                    min_list.append(m2)
                print("min list", min_list)
                temp = min(min_list)
                # temp = min(min_list)  # keep track of k
                # temp = min(min_angle, m1, m2)
                # temp = min(min_angle, mwt(i, k), mwt(k, j))
                m = max(temp, m)
                # m = max(temp, m)  # keep track of k
            table[table_id] = m
            return table[table_id]
            # return table[table_id]  # return tuple

    mwt(polygon.head, polygon.head.next)
    
    # for vi in polygon.vertex_list:
    #     for vj in polygon.vertex_list:
    #         mwt(vi, vj)
    #         print(table)

    print(table)
    
    
    
    #
    # def mwt_print(i,j):
    #     table_id = tuple([i.index, j.index])
    #
    #     if i.index == j.index:
    #         print("### this should not happend ###")
    #         return
    #     print(i.index-1, table[table_id][1], j.index)
    #     mwt_print(i, i.polygon[table[table_id][1]])
    #     mwt_print(i.polygon[[table[table_id][1]+1]], j)

    # mwt_print(polygon.head, polygon.head.next)


    return table
    
    pass
    


# Data Structures to support predicates
class Polygon:
    
    def __init__(self):
        # the polygon starts with zero points
        self.head = None
        self.temp_head = None
        self.current = None
        self.vertex_list = []
        self.normal_vertex_list = []
        self.flipped_vertex_list = []
        self.flipped = False
        
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
            self.normal_vertex_list.append(v)
            self.flipped_vertex_list.append(v)
            v.set_index(0)
            v.set_prev(v)
            v.set_next(v)
            v.set_polygon(self)
        else:
            # set index
            v.set_index(len(self.vertex_list))
            # add to master list
            self.vertex_list.append(v)
            self.normal_vertex_list.append(v)
            self.flipped_vertex_list.insert(1, v)
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

    # def make_copy(self):
    #     c = Polygon()
    #     h = self.head
    def reset_order(self):
        # reverts polygon to original with original order
        v2 = None
        v1 = None
        v0 = None
        for i in [j for j in range(len(self.normal_vertex_list))] + [0, 1]:
            # 3 width sliding window
            v2 = v1
            v1 = v0
            v0 = self.normal_vertex_list[i]
    
            if v2 is not None:
                v1.next = v0
                v1.prev = v2
        
        self.vertex_list = self.normal_vertex_list
        self.flipped = False

    def flip_order(self):
        # reverts polygon to original with reversed order
        v2f = None
        v1f = None
        v0f = None
        v2 = None
        v1 = None
        v0 = None
        for i in [j for j in range(len(self.flipped_vertex_list))] + [0, 1]:
            # 3 width sliding window
            v2 = v1
            v1 = v0
            v0 = self.flipped_vertex_list[i]

            if v2 is not None:
                v1.next = v0
                v1.prev = v2
                v0.index = i
                self.vertex_list[i] = v0

            # if v2 is not None:
            #     v1.next = v0
            #     v1.prev = v2
            #     v0.index = i
                
        # self.vertex_list = self.flipped_vertex_list
        self.flipped = True


    # def flip_order(self):
    #     # reverts polygon to original with reversed order
    #     v2 = None
    #     v1 = None
    #     v0 = None
    #     for i in [1, 0] + [j for j in range(len(self.vertex_list)-1, -1, -1)]:
    #         # 3 width sliding window
    #         v2 = v1
    #         v1 = v0
    #         v0 = self.vertex_list[i]
    #
    #         if v2 is not None:
    #             v1.next = v0
    #             v1.prev = v2
    #
    #     self.flipped = True
        
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
    
    def __getitem__(self, item):
        return self.coord[item]
    
    def __str__(self):
        return str(self.index)
    
    def __int__(self):
        return int(self.index)

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
    
    def make_copy(self):
        c = Vertex(self.coord[X], self.coord[Y])
        c.index = self.index
        c.prev = self.prev
        c.next = self.next
        c.polygon = self.polygon
        c.ear = self.ear
        return c
    
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




class Table2D:
     def __init__(self):
         self.table = {}
     def __getitem__(self, i):
         d = self.table.get(i, None)
         if d is None:
             self.table[i] = {}
         return self.table[i]
     def __str__(self):
         s = "{"
         for k1, v1 in self.table.items():
             for k2, v2 in v1.items():
                 s += "("+str(k1)+", "+str(k2)+"): "+str(v2)+", "
         s += "}"
         return s

def MWTriangulation2(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
        
    final_diags = []
    ids = []
    
    f_table = Table2D()  # for i, j this contains the metric value
    k_table = Table2D()  # for i, j this contains the k that had the best metric value
    
    def mwt2(i, j):
        # TODO - draw something
        
        # check for same point
        if str(i) == str(j):
            # f_table[str(i)][str(j)] = 99999
            # k_table[str(i)][str(j)] = None
            print("i and j are the same")
            print("### this should not happend ###")
            return #
        
        # find all potential k's
        ks = []
        # loop around i.prev.prev. ... until j is reached
        current = i.prev  # starting point for loop
        while str(current) != str(j):  # end if current == j
            # check for i or j being the same as current
            if str(current) == str(i) or str(current) == str(j):
                continue
            check1 = Left(i, j, current)
            check2 = False
            check3 = False
            check4 = str(i.prev) == str(current)
            check5 = str(j.next) == str(current)
            if not check4:
                check2 = Diagonal(i, current)
            if not check5:
                check3 = Diagonal(current, j)
            if check1 and (check2 or check4) and (check3 or check5):
            # if Left(i, j, current) and \
            #     (str(i.prev) == str(current) or Diagonal(i, current)) \
            #     and (str(j.next) == str(current) or Diagonal(current, j)):
                ks.append(current)

            current = current.prev  # iterate to next vertex (, prev in this case)
        
        if len(ks) == 0:
            print("empty ks")
            print("### this should not happend ###")
            return
        
        metric = 0
        best_k = None
        for k in ks:
            # calculation for current k
            angle1 = angle(i.coord, j.coord, k.coord)
            angle2 = angle(k.coord, i.coord, j.coord)
            angle3 = angle(j.coord, k.coord, i.coord)
            min_angle = min(angle1, angle2, angle3)

            # min_list = [min_angle]
            if i.prev.index != k.index:
                mwt2(i, k)
            if k.index != j.next.index:
                mwt2(k, j)
            
            m1 = min_angle
            # m2 = f_table[i].get(k, 1000000)
            # m3 = f_table[k].get(j, 1000000)
            m2 = f_table[str(i)].get(str(k), 1000000)
            m3 = f_table[str(k)].get(str(j), 1000000)
            # temp = min(min_angle, f_table[i].get([k], 1000000), f_table[k].get([j], 1000000))
            smallest_angle= min(m1, m2, m3)
            if smallest_angle > metric:
                # if the minimum angle is larger with this k
                # then set the new metric and best_k
                metric = smallest_angle
                best_k = k
            
        f_table[str(i)][str(j)] = metric
        k_table[str(i)][str(j)] = str(best_k)
        # k_table[str(i)][str(j)] = best_k
        return
    
    length_of_poly = len(polygon.vertex_list)
    diags = []

    def draw_line_from_index(i, j):
        vi = polygon[i]
        vj = polygon[j]
        if canvas is not None:
            id = canvas.create_line(vi[X], flip * vi[Y], vj[X], flip * vj[Y], fill="dark green")
            ids.append(id)
        # diags.append((vi, vj))
    
    def mwt2_traverse(i, j):
        k = k_table[str(i)].get(str(j), None)
        if k is None:
            return
        is_adjacent = lambda x, y: (int(x)+1)%length_of_poly == int(y) or \
                                   (int(y)+1)%length_of_poly == int(x)
        # print(i, j, k)
        if not is_adjacent(i, k):
            print(i, k)
            diags.append((str(i), str(k)))
            draw_line_from_index(int(i), int(k))
        if not is_adjacent(k, j):
            print(k, j)
            diags.append((str(k), str(j)))
            draw_line_from_index(int(k), int(j))
        mwt2_traverse(i, k)
        mwt2_traverse(k, j)
        return
    

    mwt2(polygon.head, polygon.head.next)
    mwt2_traverse(polygon.head, polygon.head.next)#, first_call=True)
    print(diags)

    return ids


def MWTriangulation2b(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    final_diags = []
    ids = []
    
    f_table = Table2D()  # for i, j this contains the metric value
    k_table = Table2D()  # for i, j this contains the k that had the best metric value
    
    def mwt2b(i, j):
        # TODO - draw something
        
        # check for same point
        if str(i) == str(j):
            # f_table[str(i)][str(j)] = 99999
            # k_table[str(i)][str(j)] = None
            print("i and j are the same")
            print("### this should not happend ###")
            return  #
        
        pre_compute = k_table[str(i)].get(str(j), None)
        # print("pre_compute", i, j, pre_compute)
        if pre_compute is not None:
            # print(i, j, f_table[str(i)][str(j)], k_table[str(i)][str(j)])
            return
        
        # find all potential k's
        ks = []
        # loop around i.prev.prev. ... until j is reached
        current = i.prev  # starting point for loop
        while str(current) != str(j):  # end if current == j
            # check for i or j being the same as current
            if str(current) == str(i) or str(current) == str(j):
                continue
            check1 = Left(i, j, current)
            check2 = False
            check3 = False
            check4 = str(i.prev) == str(current)
            check5 = str(j.next) == str(current)
            if not check4:
                check2 = Diagonal(i, current)
            if not check5:
                check3 = Diagonal(current, j)
            if check1 and (check2 or check4) and (check3 or check5):
                # if Left(i, j, current) and \
                #     (str(i.prev) == str(current) or Diagonal(i, current)) \
                #     and (str(j.next) == str(current) or Diagonal(current, j)):
                ks.append(current)
            
            current = current.prev  # iterate to next vertex (, prev in this case)
        
        if len(ks) == 0:
            # print("empty ks")
            # print("### this should not happend ###")
            return
        
        # sort ks by min angle
        def minimum_angle(k):
            angle1 = angle(i.coord, j.coord, k.coord)
            angle2 = angle(k.coord, i.coord, j.coord)
            angle3 = angle(j.coord, k.coord, i.coord)
            min_angle = min(angle1, angle2, angle3)
            return min_angle
        
        # print(ks)
        # ks.sort(key=minimum_angle)
        # print(ks)
        # shuffle(ks)

        metric = 0
        best_k = None
        for k in ks:
            # calculation for current k
            angle1 = angle(i.coord, j.coord, k.coord)
            angle2 = angle(k.coord, i.coord, j.coord)
            angle3 = angle(j.coord, k.coord, i.coord)
            min_angle = min(angle1, angle2, angle3)
            
            # min_list = [min_angle]
            if i.prev.index != k.index:
                mwt2b(i, k)
            if k.index != j.next.index:
                mwt2b(k, j)
            
            m1 = min_angle
            # m2 = f_table[i].get(k, 1000000)
            # m3 = f_table[k].get(j, 1000000)
            m2 = f_table[str(i)].get(str(k), 1000000)
            m3 = f_table[str(k)].get(str(j), 1000000)
            # temp = min(min_angle, f_table[i].get([k], 1000000), f_table[k].get([j], 1000000))
            smallest_angle = min(m1, m2, m3)
            if smallest_angle > metric:
                # if the minimum angle is larger with this k
                # then set the new metric and best_k
                metric = smallest_angle
                best_k = k
        
        f_table[str(i)][str(j)] = metric
        k_table[str(i)][str(j)] = str(best_k)
        # k_table[str(i)][str(j)] = best_k
        return
    
    length_of_poly = len(polygon.vertex_list)
    diags = []
    
    def draw_line_from_index(i, j):
        vi = polygon[i]
        vj = polygon[j]
        if canvas is not None:
            id = canvas.create_line(vi[X], flip * vi[Y], vj[X], flip * vj[Y], fill="dodger blue")
            ids.append(id)
        # diags.append((vi, vj))
    
    def mwt2b_traverse(i, j):
        k = k_table[str(i)].get(str(j), None)
        if k is None:
            return
        is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
                                   (int(y) + 1) % length_of_poly == int(x)
        # print(i, j, k)
        if not is_adjacent(i, k):
            print(i, k)
            diags.append((str(i), str(k)))
            draw_line_from_index(int(i), int(k))
        if not is_adjacent(k, j):
            print(k, j)
            diags.append((str(k), str(j)))
            draw_line_from_index(int(k), int(j))
        mwt2b_traverse(i, k)
        mwt2b_traverse(k, j)
        return
    
    mwt2b(polygon.head, polygon.head.next)
    mwt2b_traverse(polygon.head, polygon.head.next)  # , first_call=True)
    print(diags)
    
    return ids

f_table = Table2D()  # for i, j this contains the metric value
k_table = Table2D()  # for i, j this contains the k that had the best metric value


def MWTriangulation2c_iter(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    final_diags = []
    ids = []
    
    # max_depth = 0
    f_table = Table2D()  # for i, j this contains the metric value
    k_table = Table2D()  # for i, j this contains the k that had the best metric value
    d_table = Table2D()  # for i, j stores the depth
    history = []
    pre_compute_list = []
    # optimal_triangulation_history = []
    
    # is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
    #                            (int(y) + 1) % length_of_poly == int(x)

    
    def mwt2b(i, j, depth=0, max_depth=0):
        # TODO - draw something
        max_depth = max(max_depth, depth)
        history.append((str(i), str(j), depth, 'traverse'))
        
        # def k_table_traverse(i=str(polygon.head) , j=str(polygon.head.next), length_of_poly=len(polygon.vertex_list)):
        #     k = k_table[i].get(j, None)
        #     if k is None:
        #         return []
        #     else:
        #         is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or (int(y) + 1) % length_of_poly == int(x)
        #         d = []
        #         if not is_adjacent(i, k):
        #             d.append((i, k))
        #         if not is_adjacent(k, j):
        #             d.append((k, j))
        #         return d + k_table_traverse(i, k) + k_table_traverse(k, j)

        # temp_historical_diags = k_table_traverse()
        # print("temp_historical_diags", temp_historical_diags)
        # optimal_triangulation_history.append(temp_historical_diags)
        
        # h_len = len(history)-1
        
        # check for same point
        if str(i) == str(j):
            # f_table[str(i)][str(j)] = 99999
            # k_table[str(i)][str(j)] = None
            print("i and j are the same")
            print("### this should not happen ###")
            # return  #
            return max_depth
        # elif is_adjacent(str(i), str(j)):
        #     print("i and j are adjacent")
        #     print("### this should not happen ###")
        #     # return  #
        #     return max_depth

        pre_compute = k_table[str(i)].get(str(j), None)
        print("pre_compute", i, j, pre_compute)
        if pre_compute is not None:
            print(i, j, f_table[str(i)][str(j)], k_table[str(i)][str(j)])
            pre_compute_list.append((str(i), str(j)))
            return max_depth

        # find all potential k's
        ks = []
        # loop around i.prev.prev. ... until j is reached
        current = i.prev  # starting point for loop
        while str(current) != str(j):  # end if current == j
            # check for i or j being the same as current
            if str(current) == str(i) or str(current) == str(j):
                continue
            check1 = Left(i, j, current)
            check2 = False
            check3 = False
            check4 = str(i.prev) == str(current)
            check5 = str(j.next) == str(current)
            if not check4:
                check2 = Diagonal(i, current)
            if not check5:
                check3 = Diagonal(current, j)
            if check1 and (check2 or check4) and (check3 or check5):
                # if Left(i, j, current) and \
                #     (str(i.prev) == str(current) or Diagonal(i, current)) \
                #     and (str(j.next) == str(current) or Diagonal(current, j)):
                ks.append(current)
            
            current = current.prev  # iterate to next vertex (, prev in this case)
        
        if len(ks) == 0:
            # print("empty ks")
            # print("### this should not happend ###")
            # return
            return max_depth

        # sort ks by min angle
        # def minimum_angle(k):
        #     angle1 = angle(i.coord, j.coord, k.coord)
        #     angle2 = angle(k.coord, i.coord, j.coord)
        #     angle3 = angle(j.coord, k.coord, i.coord)
        #     min_angle = min(angle1, angle2, angle3)
        #     return min_angle
        
        # print(ks)
        # ks.sort(key=minimum_angle)
        # print(ks)
        # shuffle(ks)
        
        metric = 0
        best_k = None
        for k in ks:
            # calculation for current k
            angle1 = angle(i.coord, j.coord, k.coord)
            angle2 = angle(k.coord, i.coord, j.coord)
            angle3 = angle(j.coord, k.coord, i.coord)
            min_angle = min(angle1, angle2, angle3)
            
            # min_list = [min_angle]
            md1md2 = []
            if i.prev.index != k.index:
                md1 = mwt2b(i, k, depth=depth+1, max_depth=max_depth)
                md1md2.append(md1)
            if k.index != j.next.index:
                md2 = mwt2b(k, j, depth=depth+1, max_depth=max_depth)
                md1md2.append(md2)
            max_depth = max([max_depth]+md1md2)
            m1 = min_angle
            # m2 = f_table[i].get(k, 1000000)
            # m3 = f_table[k].get(j, 1000000)
            m2 = f_table[str(i)].get(str(k), 1000000)
            m3 = f_table[str(k)].get(str(j), 1000000)
            # temp = min(min_angle, f_table[i].get([k], 1000000), f_table[k].get([j], 1000000))
            smallest_angle = min(m1, m2, m3)
            if smallest_angle > metric:
                # if the minimum angle is larger with this k
                # then set the new metric and best_k
                metric = smallest_angle
                best_k = k
        
        # history.insert(h_len, "best")
        f_table[str(i)][str(j)] = metric
        print("store best_k", i, j, best_k)
        k_table[str(i)][str(j)] = str(best_k)
        print("k_table", k_table)
        d_table[str(i)][str(j)] = min(d_table[str(i)].get(str(j), 9999), depth)
        history.append((str(i), str(j), depth, 'stored'))


        # d_table[str(i)][str(best_k)] = depth
        # d_table[str(best_k)][str(j)] = depth
        # k_table[str(i)][str(j)] = best_k
        # return
        return max_depth

    length_of_poly = len(polygon.vertex_list)
    diags = []
    

    max_depth = mwt2b(polygon.head, polygon.head.next)
    # mwt2c_traverse(polygon.head, polygon.head.next)  # , first_call=True)
    print(diags)
    
    return k_table, history, max_depth#, optimal_triangulation_history

mwt_ids = []
def draw_line_from_index(i, j, canvas, polygon, color="dark green", flip=True, arrow=False, width=2):
    from tkinter import LAST
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    vi = polygon[i]
    vj = polygon[j]
    if canvas is not None:
        if arrow:
            id = canvas.create_line(vi[X], flip * vi[Y], vj[X], flip * vj[Y], fill=color, arrow=LAST, width=width)
        else:
            id = canvas.create_line(vi[X], flip * vi[Y], vj[X], flip * vj[Y], fill=color)
        mwt_ids.append(id)
    return id
    # diags.append((vi, vj))

def mwt2c_traverse(i, j, polygon, canvas, first=False, table=None):
    print("mwt2c", i, j)
    if table is not None:
        k_table = table
    length_of_poly = len(polygon.vertex_list)
    k = k_table[str(i)].get(str(j), None)
    if k is not None:
    #     pass
    # else:
        is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
                                   (int(y) + 1) % length_of_poly == int(x)
        # print(i, j, k)
        id1, id2 = None, None
        if not is_adjacent(i, k):
            print(i, k)
            # diags.append((str(i), str(k)))
            id1 = draw_line_from_index(int(i), int(k), canvas, polygon)
            yield id1
        if not is_adjacent(k, j):
            print(k, j)
            # diags.append((str(k), str(j)))
            id2 = draw_line_from_index(int(k), int(j), canvas, polygon)
            yield id2
        mwt2c_traverse(i, k, polygon, canvas, table=table)
        mwt2c_traverse(k, j, polygon, canvas, table=table)
    if first:
        yield True
    # return

def mwt2d_traverse(start_i, start_j, polygon, canvas, table, history=None):
    # print("mwt2c", i, j)
    # if table is not None:
    #     k_table = table
    length_of_poly = len(polygon.vertex_list)

    is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
                               (int(y) + 1) % length_of_poly == int(x)

    i = start_i
    j = start_j
    
    # s = [(start_i, start_j)]
    # # do_while = True
    # while len(s) > 0:# or do_while:
    #     # do_while = False
    #     i, j = s.pop()
    #     k = table[str(i)].get(str(j), None)
    #     id4 = draw_line_from_index(int(i), int(j), canvas, polygon, color="blue")
    #
    #     if k is not None:
    #         id1, id2 = None, None
    #         if not is_adjacent(i, k):
    #             print(i, k)
    #             # diags.append((str(i), str(k)))
    #             id1 = draw_line_from_index(int(i), int(k), canvas, polygon, color="yellow")
    #             yield id1
    #         s.append((i, k))
    #         if not is_adjacent(k, j):
    #             print(k, j)
    #             # diags.append((str(k), str(j)))
    #             id2 = draw_line_from_index(int(k), int(j), canvas, polygon, color="yellow")
    #             yield id2
    #         s.append((k, j))
    #     else:
    #         print("no k", i, j)
    #         id3 = draw_line_from_index(int(i), int(j), canvas, polygon, color="green")
    #         yield id3
    # yield True


    if history is not None:
        for t in history:
            id1 = draw_line_from_index(int(t[X]), int(t[Y]), canvas, polygon, color="orange")
            yield id1


    # if k is not None:
    # #     pass
    # # else:
    #     is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
    #                                (int(y) + 1) % length_of_poly == int(x)
    #     # print(i, j, k)
    #     id1, id2 = None, None
    #     if not is_adjacent(i, k):
    #         print(i, k)
    #         # diags.append((str(i), str(k)))
    #         id1 = draw_line_from_index(int(i), int(k), canvas, polygon)
    #         yield id1
    #     if not is_adjacent(k, j):
    #         print(k, j)
    #         # diags.append((str(k), str(j)))
    #         id2 = draw_line_from_index(int(k), int(j), canvas, polygon)
    #         yield id2
    #     mwt2c_traverse(i, k, polygon, canvas, table=table)
    #     mwt2c_traverse(k, j, polygon, canvas, table=table)
    # if first:
    #     yield True
    # return


def mwt2e_traverse(start_i, start_j, polygon, canvas, table, history, depth=None): #, optimal_triangulation_history=None):
    # print("mwt2c", i, j)
    # if table is not None:
    #     k_table = table
    length_of_poly = len(polygon.vertex_list)
    
    is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
                               (int(y) + 1) % length_of_poly == int(x)
    
    i = start_i
    j = start_j
    
    # colors = None
    print("depth", depth)
    if depth is not None:
        colors = ['gray'+str(i) for i in range(int((100%(depth+2))/2), 100, int(100/(depth+2)))][1:-1]
        colors = [temp for temp in reversed(colors)]
        current_diags = [None for i in range(depth+1)]
    
    def paint_current_diags(current_diags, remove_ids=[]):
        for id in remove_ids:
            canvas.after(1, canvas.delete, id)
        ids = []
        for x in current_diags:
            if x is None:
                break
            else:
                i, j, d = x
                id = draw_line_from_index(int(i), int(j), canvas, polygon, color=colors[d], arrow=True)
                ids.append(id)
        return ids

    def k_table_traverse(i=str(polygon.head), j=str(polygon.head.next), length_of_poly=len(polygon.vertex_list)):
        k = table[i].get(j, None)
        if k is None:
            return []
        else:
            is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or (int(y) + 1) % length_of_poly == int(
                x)
            d = []
            if not is_adjacent(i, k):
                d.append((i, k))
            if not is_adjacent(k, j):
                d.append((k, j))
            return d + k_table_traverse(i, k) + k_table_traverse(k, j)
    
    def paint_current_stored_triangulation(current_diags, remove_ids=[], color="green"):
        for id in remove_ids:
            canvas.after(1, canvas.delete, id)
        ids = []
        for x in current_diags:
            if x is None:
                break
            else:
                i, j = x
                id = draw_line_from_index(int(i), int(j), canvas, polygon, color=color)
                ids.append(id)
        return ids
    
    # s = [(start_i, start_j)]
    # # do_while = True
    # while len(s) > 0:# or do_while:
    #     # do_while = False
    #     i, j = s.pop()
    #     k = table[str(i)].get(str(j), None)
    #     id4 = draw_line_from_index(int(i), int(j), canvas, polygon, color="blue")
    #
    #     if k is not None:
    #         id1, id2 = None, None
    #         if not is_adjacent(i, k):
    #             print(i, k)
    #             # diags.append((str(i), str(k)))
    #             id1 = draw_line_from_index(int(i), int(k), canvas, polygon, color="yellow")
    #             yield id1
    #         s.append((i, k))
    #         if not is_adjacent(k, j):
    #             print(k, j)
    #             # diags.append((str(k), str(j)))
    #             id2 = draw_line_from_index(int(k), int(j), canvas, polygon, color="yellow")
    #             yield id2
    #         s.append((k, j))
    #     else:
    #         print("no k", i, j)
    #         id3 = draw_line_from_index(int(i), int(j), canvas, polygon, color="green")
    #         yield id3
    # yield True
    
    diags = []

    # s = [(start_i, start_j)]
    # while len(s) > 0:
    #     i, j = s.pop()
    #     k = table[str(i)].get(str(j), None)
    #
    #     if k is not None:
    #         if not is_adjacent(i, k):
    #             print(i, k)
    #             diags.append((str(i), str(k), d_table[i].get(k, None)))
    #             # diags.append((str(i), str(k)))#, d_table[i].get(k, None)))
    #         s.append((i, k))
    #         if not is_adjacent(k, j):
    #             print(k, j)
    #             diags.append((str(k), str(j), d_table[k].get(j, None)))
    #             # diags.append((str(k), str(j)))#, d_table[k].get(j, None)))
    #         s.append((k, j))
    #     else:
    #         print("no k", i, j)
    
    id_temp = None
    temp_ids = []
    temp2_ids = []
    print("diags", diags)
    print("history", history)
    best = False
    for ind, x in enumerate(history):
        print("x", x)
        # print("oth", optimal_triangulation_history[ind])
        # if x == "best":
        #     best = True
        #     continue
        # i, j = x
        i, j, d, m = x
        
        print(ind, 'of', len(history))
        print('i:',i,'j:',j, 'd', d)
        if d >= 1: # shift to prevent the drawing of initial starting boundary edge i, j
            current_diags[d-1] = (i, j, d-1)
            current_diags[d] = None
        # print("best", best)
        print("")
        # if id_temp is not None:
        #     canvas.after(1, canvas.delete, id_temp)
        # id_temp = draw_line_from_index(int(i), int(j), canvas, polygon, color="orange")
        temp_ids = paint_current_diags(current_diags, remove_ids=temp_ids)
        # temp2_ids = paint_current_optimal_triangulation(optimal_triangulation_history[ind], remove_ids=temp2_ids)

        # r = id_temp
        r = temp_ids
        if m == 'stored':
            stored_diags = k_table_traverse(i, j)
            print("stored_diags", k_table_traverse(i, j))
            temp2_ids = paint_current_stored_triangulation(stored_diags, remove_ids=temp2_ids, color="turquoise2")
            r = temp2_ids
        # if (i, j) in diags:
        # # if best:
        #     r = draw_line_from_index(int(i), int(j), canvas, polygon, color="green")
        #     r = [r]

        #     best = False
        # yield r
        yield r
    if id_temp is not None:
        canvas.after(1, canvas.delete, id_temp)
    paint_current_diags([], remove_ids=temp_ids)
    temp2_ids = paint_current_stored_triangulation(k_table_traverse(), remove_ids=temp2_ids, color="DeepSkyBlue3")
    r = temp2_ids
    yield r
    # paint_current_optimal_triangulation(optimal_triangulation_history[ind], remove_ids=temp2_ids, color="blue")
    
    
    
    # s = [(start_i, start_j)]
    # # do_while = True
    # ids = []
    # while len(s) > 0:# or do_while:
    #     # do_while = False
    #     i, j = s.pop()
    #     k = table[str(i)].get(str(j), None)
    #     # id4 = draw_line_from_index(int(i), int(j), canvas, polygon, color="blue")
    #
    #     if k is not None:
    #         id1, id2 = None, None
    #         if not is_adjacent(i, k):
    #             print(i, k)
    #             # diags.append((str(i), str(k)))
    #             id1 = draw_line_from_index(int(i), int(k), canvas, polygon, color="green")
    #             ids.append(id1)
    #         s.append((i, k))
    #         if not is_adjacent(k, j):
    #             print(k, j)
    #             # diags.append((str(k), str(j)))
    #             id2 = draw_line_from_index(int(k), int(j), canvas, polygon, color="green")
    #             ids.append(id2)
    #         s.append((k, j))
    #     # else:
    #     #     print("no k", i, j)
    #     #     id3 = draw_line_from_index(int(i), int(j), canvas, polygon, color="green")
    #     #     yield id3
    # print("ids", ids)
    # yield ids
    
    
    yield True


