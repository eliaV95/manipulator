#
#
#


from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QPoint, Qt
from pose import *

COLOR_MAP = { 'red' : QtGui.QColor(255,0,0),
              'green' : QtGui.QColor(0,255,0),
              'blue' : QtGui.QColor(0,0,255)}

class Block:

    WIDTH = 0.03
    HEIGHT = 0.02
    GAP = 0.01

    def __init__(self, uColor):
        self.__color = uColor
        self.__pose = Pose()
        self.__w = Pose.pixel_scale(Block.WIDTH)
        self.__h = Pose.pixel_scale(Block.HEIGHT)
        self.cell_matrix = [0,0]
        
    def get_pose(self):
        return self.__pose.get_pose()

    def set_pose(self, x, y, a):
        self.__pose.set_pose(x,y,a)

    def get_color(self):
        return self.__color
    
    def get_cell(self):
        return self.cell_matrix
    
    #setta le coordinate della cella dove si trova il blocco
    def set_cell(self, block_array):
        self.cell_matrix[0] = block_array[0]
        self.cell_matrix[1] = block_array[1]
    
    def get_cell_by_pixel(self, x, y):
        #conversione da coordinate x, y (pixel) a posizione cella
        row = int(((y-5)/40) ) 
        col = int(((x)/40) )
        """
        self.debug_counter = getattr(self, 'debug_counter', 0)  # inizializza solo se non esiste
        if self.debug_counter < 10:  # Limita a 10 stampe
            print(f"Calcolo cella per pixel: x={x}, y={y} -> col={col+1}, row={row+1}")
            self.debug_counter += 1
        """    
        return col, row
    """
    def get_cell_by_pixel(self, x, y):
        # Dimensione della cella in pixel
        cell_size = 40
        # Calcolo della riga e colonna dalla posizione in pixel
        col = int(((x // cell_size))+0.5)  # Colonna calcolata dividendo la coordinata x
        row = int(((y-5)// cell_size)+0.5)  # Riga calcolata dividendo la coordinata y
        print(f"Calcolo cella per pixel: x={x}, y={y}, col={col}, row={row}")  # Debug
        return col-1, row-1   # Considera 1-based se necessario per l'indice
    """

    def paint(self, qp):
        qp.setPen(QtCore.Qt.black)
        qp.setBrush(COLOR_MAP[self.__color])

        x, y, a = self.__pose.get_pose()

        t = QtGui.QTransform()
        t.translate(x + self.__w/2, y - self.__h/2)
        t.rotate(-self.__pose.get_a())
        t.translate(-(x + self.__w/2), -(y - self.__h/2))

        qp.setTransform(t)
        #qp.drawRect(x, y - self.__h, self.__w, self.__h)
        point1 = QPoint(x, y - self.__h)
        point2 = QPoint(x + self.__w, y - self.__h)
        point4 = QPoint(x + (self.__w/3), y)
        point3 = QPoint(x + (self.__w/3) + self.__w, y)
        parallelepiped = [point1, point2, point3, point4]
        qp.drawPolygon(*parallelepiped)


