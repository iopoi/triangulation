
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

def points_to_polygon(l):
    # TODO - this will take in a list of points from
    # the app and turn them into a polygon data structure
    pass

def add_to_poly(p):
    # TODO - this will add a point to the polygon
    pass

