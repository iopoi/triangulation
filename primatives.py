
# reimplementation of primitive methods from tri.c - http://cs.smith.edu/~jorourke/books/ftp.html

from operator import xor
from math import acos, sqrt, degrees
from tkinter import LAST

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
    # c = a.get_polygon().head  # this does not get modified during triangulate
    c = a.get_polygon().temp_head  # this does get modified during triangulate
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
    """this is used in Triangulate"""
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
        v1.ear = Diagonal(v0, v2)
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
        # 400ms is the visual delay to see the traversal to the next ear; 1ms is the default
        canvas.after(400, canvas.delete, remove_id)

    id = canvas.create_oval(x - 5, flip*y - 5, x + 5, flip*y + 5, fill=color, outline=color, width=width)
    # print("dot", id, color, "coord:", x, flip*y)  # debug
    return id


def Triangulate(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    print("check - counterclockwise =", polygon.check_counter_clockwise())
    if not polygon.check_counter_clockwise():
        print("not clounterclockwise - function returned")
        return
    # v0, v1, v2, v3, v4  -  five consecutive vertices
    v0, v1, v2, v3, v4 = None, None, None, None, None
    n = len(polygon.vertex_list) # number of vertices; shrinks to 3
    earfound = False # for debugging and error detection only
    
    # print("head loop")  # debug
    # polygon.head.print_loop()  # debug
    
    debug_v2_id = None
    
    diags = []
    ids = []
    
    EarInit(polygon)
    
    polygon.temp_head = polygon.head
    
    print("newpath")
    # Each step of outer loop removes one ear.
    
    while n > 3:
        # print('n =', n)  # debug
        
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
                # print("diag", v1.coord, v3.coord)  # debug
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

        # print("debug - internal ploygon of size", n)  # debug
        # polygon.temp_head.print_loop()  # debug

        if not earfound:
            i = None
            print("internal ploygon")
            print("v0", v0)
            print("v1", v1)
            print("v2", v2)
            print("v3", v3)
            print("v4", v4)
            print("print loop from v2 perspective")
            v2.print_loop(canvas)
            print("%%Error in Triangulate:  No ear found.\n")
            print("showpage\n%%%%EOF\n")
            raise RuntimeError("Error in Triangulate:  No ear found.")
    
    # end outer while loop
    print("closepath stroke")
    canvas.after(1, canvas.delete, debug_v2_id)  # delete debug_v2_id from canvas
    print([(str(temp[X]), str(temp[Y])) for temp in diags])  # debug
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
    v0, v1, v2, v3, v4 = None, None, None, None, None

    n = len(polygon.vertex_list)  # number of vertices; shrinks to 3
    earfound = False  # for debugging and error detection only
    
    # print("head loop")  # debug
    # polygon.head.print_loop()  # debug
    
    debug_v2_id = None
    
    # diags = []
    
    EarInit(polygon)
    
    polygon.temp_head = polygon.head
    
    print("newpath")
    # Each step of outer loop removes one ear.
    
    while n > 3:
        print('n =', n)
        
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
                print("ear", str(v2), "diag", str(v1), str(v3), " -  diag coords", v1.coord, v3.coord)
                id = None
                if canvas is not None:
                    id = canvas.create_line(v1.coord[X], flip * v1.coord[Y], v3.coord[X], flip * v3.coord[Y],
                                       fill="green3")
                # this is the stopping point for each iteration
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
        
        # print("debug - internal ploygon of size", n)  # debug
        # polygon.temp_head.print_loop()  # debug
        
        if not earfound:
            i = None
            print("internal ploygon")
            print("v0", v0)
            print("v1", v1)
            print("v2", v2)
            print("v3", v3)
            print("v4", v4)
            print("print loop from v2 perspective")
            v2.print_loop(canvas)
            print("%%Error in Triangulate:  No ear found.\n")
            print("showpage\n%%%%EOF\n")
            raise RuntimeError("Error in Triangulate:  No ear found.")
    
    # end outer while loop
    print("closepath stroke")
    canvas.after(1, canvas.delete, debug_v2_id)
    yield True
    # return diags


def distance(a, b):
    return sqrt((b[X]-a[X])^2+((b[Y]-a[Y])^2))

def distance3(a, b, c):
    return distance(a, b)+distance(b, c)+distance(c, a)

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


# Wrapper for a dict to be accessed like a 2d list
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

def MWTriangulation(polygon, canvas=None, flip=True):
    temp_flip = flip
    if flip:
        flip = -1
    else:
        flip = 1
    
    final_diags = []
    ids = []
    
    f_table = Table2D()  # for i, j this contains the metric value
    k_table = Table2D()  # for i, j this contains the k that had the best metric value
    
    def mwt(i, j):
        """this method does not return anything, it just modifies the tables"""
        # check for same point
        if str(i) == str(j):
            print("i and j are the same")
            print("### this should not happend ###")
            return
        
        pre_compute = k_table[str(i)].get(str(j), None)
        # print("pre_compute", i, j, pre_compute)  # debug
        if pre_compute is not None:
            # print(i, j, f_table[str(i)][str(j)], k_table[str(i)][str(j)])  # debug
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
                ks.append(current)
            
            current = current.prev  # iterate to next vertex (, prev in this case)
        
        if len(ks) == 0:
            # print("empty ks")
            # print("### this should not happened ###")
            # this means a polygon edge was reached
            return

        metric = 0
        best_k = None
        for k in ks:
            # calculation for current k
            angle1 = angle(i.coord, j.coord, k.coord)
            angle2 = angle(k.coord, i.coord, j.coord)
            angle3 = angle(j.coord, k.coord, i.coord)
            min_angle = min(angle1, angle2, angle3)
            
            if i.prev.index != k.index:
                mwt(i, k)
            if k.index != j.next.index:
                mwt(k, j)
            
            # after mwt2b the f_table should have answers, but if it doesn't a high value is used in place
            
            m1 = min_angle
            m2 = f_table[str(i)].get(str(k), 1000000)
            m3 = f_table[str(k)].get(str(j), 1000000)
            smallest_angle = min(m1, m2, m3)
            if smallest_angle > metric:
                # if the minimum angle is larger with this k
                # then set the new metric and best_k
                metric = smallest_angle
                best_k = k
        
        # store in the tables
        f_table[str(i)][str(j)] = metric
        k_table[str(i)][str(j)] = str(best_k)
        return
    
    length_of_poly = len(polygon.vertex_list)
    diags = []
    
    def draw_line_from_index(i, j):
        vi = polygon[i]
        vj = polygon[j]
        if canvas is not None:
            id = canvas.create_line(vi[X], flip * vi[Y], vj[X], flip * vj[Y], fill="dodger blue")
            ids.append(id)

    # define a function is_adjacent
    is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
                               (int(y) + 1) % length_of_poly == int(x)
    
    # the result of the mwt are in the table, which must be traversed to return/draw the answer
    def mwt_traverse(i, j):
        # the traversal mimics the recursion structure
        k = k_table[str(i)].get(str(j), None)
        if k is None:
            return

        if not is_adjacent(i, k):
            # print("diag", i, k)  # debug
            diags.append((str(i), str(k)))
            draw_line_from_index(int(i), int(k))
        if not is_adjacent(k, j):
            # print("diag", k, j)  # debug
            diags.append((str(k), str(j)))
            draw_line_from_index(int(k), int(j))
        mwt_traverse(i, k)
        mwt_traverse(k, j)
        return
    
    mwt(polygon.head, polygon.head.next)
    mwt_traverse(polygon.head, polygon.head.next)
    print(diags)  # final diags in the triangulation
    
    return ids

def MWTriangulation_iter(polygon, canvas=None, flip=True):
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
    
    def mwt(i, j, depth=0, max_depth=0):
        # this function returns the max_depth to aid in the visualization
        # this value does not help in filling out the tables or producing diagonals
        max_depth = max(max_depth, depth)
        history.append((str(i), str(j), depth, 'traverse'))
        
        # check for same point
        if str(i) == str(j):
            print("i and j are the same")
            print("### this should not happen ###")
            return max_depth
        
        pre_compute = k_table[str(i)].get(str(j), None)
        # print("pre_compute", i, j, pre_compute)  # debug
        if pre_compute is not None:
            # print(i, j, f_table[str(i)][str(j)], k_table[str(i)][str(j)])  # debug
            # this list helps for visualization
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
                ks.append(current)
            
            current = current.prev  # iterate to next vertex (, prev in this case)
        
        if len(ks) == 0:
            # print("empty ks")
            # print("### this should not happend ###")
            # this means a polygon edge was reached
            return max_depth
        
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
                md1 = mwt(i, k, depth=depth+1, max_depth=max_depth)
                md1md2.append(md1)
            if k.index != j.next.index:
                md2 = mwt(k, j, depth=depth+1, max_depth=max_depth)
                md1md2.append(md2)
            max_depth = max([max_depth]+md1md2)
            m1 = min_angle
            m2 = f_table[str(i)].get(str(k), 1000000)
            m3 = f_table[str(k)].get(str(j), 1000000)
            smallest_angle = min(m1, m2, m3)
            if smallest_angle > metric:
                # if the minimum angle is larger with this k
                # then set the new metric and best_k
                metric = smallest_angle
                best_k = k
        
        f_table[str(i)][str(j)] = metric
        # print("store best_k", i, j, best_k)  # debug
        k_table[str(i)][str(j)] = str(best_k)
        # print("k_table", k_table)  # debug
        d_table[str(i)][str(j)] = min(d_table[str(i)].get(str(j), 9999), depth)
        history.append((str(i), str(j), depth, 'stored'))

        return max_depth

    length_of_poly = len(polygon.vertex_list)
    diags = []
    
    max_depth = mwt(polygon.head, polygon.head.next)
    print(diags)
    
    return k_table, history, max_depth#, optimal_triangulation_history

mwt_ids = []
def draw_line_from_index(i, j, canvas, polygon, color="dark green", flip=True, arrow=False, width=2):
    """Draws line/arrow for MWT visualization"""
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

def MWTriangulation_iter_traverse(start_i, start_j, polygon, canvas, table, history, depth=None):

    length_of_poly = len(polygon.vertex_list)
    
    is_adjacent = lambda x, y: (int(x) + 1) % length_of_poly == int(y) or \
                               (int(y) + 1) % length_of_poly == int(x)
    
    i = start_i
    j = start_j
    
    print("depth", depth)
    if depth > 98:
        # the color pallet cannot be visualized past 98
        print("cannot visualize triangulation: depth exceeded")
        raise ValueError
    if depth is not None:
        # generate depth color pallet
        colors = ['gray'+str(i) for i in range(int((100%(depth+2))/2), 100, int(100/(depth+2)))][1:-1]
        colors = [temp for temp in reversed(colors)]
        current_diags = [None for i in range(depth+1)]  # depth + 1 is to get rid of common index error
    
    def paint_current_diags(current_diags, remove_ids=[]):
        """draws and removes groups of diagonals"""
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

    def k_table_traverse(i=str(polygon.head), j=str(polygon.head.next)):
        """traverses the k table to find the triangulation from the point i, j"""
        k = table[i].get(j, None)
        if k is None:
            return []
        else:
            d = []
            if not is_adjacent(i, k):
                d.append((i, k))
            if not is_adjacent(k, j):
                d.append((k, j))
            return d + k_table_traverse(i, k) + k_table_traverse(k, j)
    
    def paint_current_stored_triangulation(current_diags, remove_ids=[], color="green"):
        """draws and removes groups of diagonals from the stored triangulation"""
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
    
    temp_ids = []  # contains the ids of the current traversal
    temp2_ids = []  # contains the ids of the stored diagonals
    # print("history", history)  # debug
    for ind, x in enumerate(history):
        i, j, d, m = x
        
        print(ind, 'of', len(history))
        print('i:', i, 'j:', j, ' d:', d, 'm:', m, end='')
        if d >= 1: # shift to prevent the drawing of initial starting boundary edge i, j
            current_diags[d-1] = (i, j, d-1)
            current_diags[d] = None
        # print("")
        temp_ids = paint_current_diags(current_diags, remove_ids=temp_ids)

        r = temp_ids
        if m == 'stored':
            stored_diags = k_table_traverse(i, j)
            print(" - stored_diags", k_table_traverse(i, j))
            temp2_ids = paint_current_stored_triangulation(stored_diags, remove_ids=temp2_ids, color="turquoise2")
            r = temp2_ids
        else:
            # this prints a newline
            print("")
        
        yield r

    # removes the traversal
    paint_current_diags([], remove_ids=temp_ids)
    # paints the final triangulation
    temp2_ids = paint_current_stored_triangulation(k_table_traverse(), remove_ids=temp2_ids, color="DeepSkyBlue3")
    r = temp2_ids
    yield r
    
    yield True


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
        """goes through self.vertex_list"""
        print([v.index for v in self.vertex_list])
        # print(v.index)
    
    def print_vertecies_iter(self):
        """goes through loop starting from head"""
        v = self.head
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "head")
        v = v.next
        while (v.index != 0):
            print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear)
            v = v.next
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "should be head")
    
    def print_vertecies_temp_iter(self):
        """goes through loop starting from temp_head, this is safer because Triangulate reassigns pointers"""
        v = self.temp_head
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "head")
        v = v.next
        while (v.index != 0):
            print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear)
            v = v.next
        print(v, "i:", v.index, "coord:", v.coord, "ear", v.ear, "should be head")
    
    def check_counter_clockwise(self):
        """checks if vertex ordering is counterclockwise"""
        current = self.head
        right_most = current
        current = current.next
        while (self.head is not current):
            if current.coord[X] > right_most.coord[X]:
                right_most = current
            elif current.coord[X] == right_most.coord[X] and current.coord[Y] > right_most.coord[Y]:
                right_most = current
            current = current.next
        return Left(right_most.prev.coord, right_most.coord, right_most.next.coord)
    
    def reset_order(self):
        """reverts polygon to original with original order"""
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
        """reverts polygon to original with reversed order"""
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
        
        self.flipped = True


class Vertex:
    
    def __init__(self, x, y, index=None, prev=None, next=None):
        self.index = index
        self.coord = (x, y)
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
        """prints loop from the perspective of the vertex"""
        first = self
        # first_coord = first.coord
        first_index = first.index
        current = self
        print(current, current.coord, current.index, "next:", current.next, "first", first_index, first)
        ids = []  # keep track of ids from drawing
        if canvas is not None:
            id = draw_dot(canvas, current.coord[X], current.coord[Y], color="yellow", width=1, flip=True)
            ids.append(id)
        current = current.next
        while (self is not current):
            print(current, current.coord, current.index, "next:", current.next, "first", first_index, first)
            if canvas is not None:
                id = draw_dot(canvas, current.coord[X], current.coord[Y], color="yellow", width=1, flip=True)
                ids.append(id)
            current = current.next
        return ids
    
    def make_copy(self):
        c = Vertex(self.coord[X], self.coord[Y])
        c.index = self.index
        c.prev = self.prev
        c.next = self.next
        c.polygon = self.polygon
        c.ear = self.ear
        return c
    
def points_to_polygon(l):
    """takes in a list of 2D coordinates/tuples in a simple chain and returns a polygon"""
    polygon = Polygon()
    for i in l:
        polygon.add_vertex(Vertex(i[X], i[Y]))
    return polygon
