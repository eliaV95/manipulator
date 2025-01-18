#
#
#
import math
import random
from block import *

COLOR_SET = [ 'red',
                'green',
                'blue']

class World:

    FLOOR_LEVEL = -0.058

    def __init__(self, ui):
        self.__blocks = [ ]
        self.__printed_blocks = [ ]
        self.ui = ui
    """
    def new_block(self, N, block_array):
        if(len(self.__blocks) > 6 or len(self.__blocks) + N > 6):
            print("Wrong value, there are only ", 6 - len(self.__blocks), " free positions")
            return
        for i in range(N):
            col = int(random.uniform(0,3))
            b = Block(COLOR_NAMES[col])
            position = True
            while position:
                pos = int(random.uniform(0, len(block_array)))
                if not self.position_busy(block_array[pos][0], block_array[pos][1]): 
                    b.set_pose(block_array[pos][0], block_array[pos][1], 0)
                    b.set_cell(b.get_cell_by_pixel(block_array[pos][0], block_array[pos][1]))
                    position = False 
            self.__blocks.append(b)
            self.__printed_blocks.append(b)    
    """
    def new_block(self, N, block_array):
        if len(self.__blocks) > 6 or len(self.__blocks) + N > 6:
            print(f"Valore errato: ci sono solo {6 - len(self.__blocks)} posizioni libere.")
            return

        for i in range(N):
            col = int(random.uniform(0, 3))
            b = Block(COLOR_SET[col])
            position = True
            while position:
                pos = int(random.uniform(0, len(block_array)))
                print(f"Prova posizione: {block_array[pos]}")  # Debug della posizione selezionata
                if not self.position_busy(block_array[pos][0], block_array[pos][1]): 
                    b.set_pose(block_array[pos][0], block_array[pos][1], 0)
                    b.set_cell(b.get_cell_by_pixel(block_array[pos][0], block_array[pos][1]))
                    print(f"Blocco creato con posa: {b.get_pose()}")  # Debug della posa impostata
                    print(f"Blocco associato alla cella: {b.get_cell()}")  # Debug della cella associata
                    position = False
                else:
                    print(f"Posizione occupata: {block_array[pos]}")  # Debug per posizione già occupata
                
            self.__blocks.append(b)
            self.__printed_blocks.append(b)

        # Debug finale per verificare tutti i blocchi creati
        print("Elenco dei blocchi nel mondo:")
        for i, block in enumerate(self.__blocks):
            block_pose = block.get_pose()
            print(f"Blocco {i + 1}: Colore = {block.get_color()}, Pose = {block_pose}, Cella = {block.get_cell()}")

    def sort_blocks(self):
        tmp__blocks = []
        for color in range(3):
            for block in self.__blocks:             
                if str(color) == block.get_color():
                    tmp__blocks.append(block)
        
        self.__blocks = tmp__blocks
        self.__printed_blocks = tmp__blocks
        
    def remove_blocks(self):
        self.__blocks = [ ]
        self.__printed_blocks = [ ]
        print("All blocks are removed")
        
    def grab_last_block(self):
        #rimuove il blocco che e' stato appena cestinato
        self.__printed_blocks = self.__printed_blocks[1:]
    
    def count_blocks(self):
        return len(self.__blocks)

    def position_busy(self, block_array_x, block_array_y):
        for b in self.__blocks:
            (x,y,a) = b.get_pose()
            if ((block_array_x == x)and(block_array_y == y)):
                return True
        return False
    
    def get_blocks(self):
        return self.__blocks

    def paint(self, qp):
        for b in self.__printed_blocks:
            b.paint(qp)
        qp.setPen(QtGui.QColor(217,95,14))
        #y = Pose.xy_to_pixel(0, World.FLOOR_LEVEL)[1]
        y = 366
        qp.drawLine(50, y+50, 450, y+50)
        qp.drawLine(50, y+51, 450, y+51)

