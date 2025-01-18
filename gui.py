#
#
#

import sys
import math
import random
import numpy as np

#
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap, QTransform, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^ use these for Qt5
#
#

#from PyQt4 import QtGui, QtCore

from arm import *
from arm_painters import *
from telemetry import *
from world import *
from phidias_interface import *

COLOR_SET = [ 'red',
                'green',
                'blue']
                
COLOR_NUM = { "red" : "0",
              "green" : "1",
              "blue" : "2"}  

COLOR_NUM1 = { "0" : "red",
              "1" : "green",
              "2" : "blue"}              
              

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.rc = 10
        self.position_matrix = np.zeros((self.rc, self.rc, 2))
        self.setPositionMatrix()
           
        #self.table_widget.setGeometry(50, 50, 850, 450)  # Posizione e dimensione della tabella
     
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 600, 500)
        self.setWindowTitle('Progetto Elia Vacanti')
        
        
        
        self.scan_blocks_mode = True
        self.grabbed = False
        
        self.current_pos_x = 2
        self.current_pos_y = 7
        self.current_man_pos_x = 0
        self.current_man_pos_y = 0 
        self.current_index_pos = 0
        self.blocks_array = []
        self.marked_array = []
        self.drawCandidateBlocks()
        
        self.obstacles_matrix = []
        self.obstacles_cell_position = []
        self.setObstacle()
        self.set_obstacles_cell_position()
        
        self.path = [ ]
        self.threshold = 0.2 #0.5 #0.2 # 20cm
        self.current_point_index = 0
        self.path_completed = False
        self.x_target_path = 0
        self.y_target_path = 0
        
        
        self.show()
        
        

        self.delta_t = 1e-2 # 10ms of time-tick
        self.t = 0

        self.trajectory_data = [ ]
        self.target_trajectory_data = [ ]

        self.use_profile = False
        self.use_trajectory = True
        self.use_angle_interpolation = False

        self.trajectory = Trajectory3(1.0, 1.5, 1.5)

        self.arm = ThreeJointsArm(self.trajectory, self.use_profile)
        self.painter = ThreeJointsArmPainter(self.arm)

        target_x = 0.065 #0.24 #0.27 cestino 319p # 114p iniziali, 0.065 pos metri iniziale   0.095
        target_y = 0.01 #0.12 #0.05 #0.21 cestino 124p # 314p iniziali, 0.02 pos metri iniziale   -0.035
        target_alpha = -90
        self.grid_cell_size = 1
        self.grid_cell_size_x = 0.00083 #0.01
        self.grid_cell_size_y = 0.00055

        self.arm.set_target_xy_a(target_x, target_y, target_alpha)

        self.world = World(self)

        self.telemetry = Telemetry()

        self._timer_painter = QtCore.QTimer(self)
        self._timer_painter.timeout.connect(self.go)
        self._timer_painter.start(self.delta_t * 1000)
        self.notification = False

        self._timer_sensor = QtCore.QTimer(self)
        #self._timer_sensor.timeout.connect(self.send_pos)
        self._timer_sensor.start(500)

        self._from = None
    
    def pixel_to_m(self, x, y):
        return (abs(50 - x) / 1000, (320 - y) / 1000)
        
    def m_to_pixel(self, mx, my):
        return (50 + (mx * 1000), 320 - (my * 1000)) 

    """
    def to_pixel(self):
        return (Pose.x_center + self.__x * 1000, Pose.y_center - self.__y * 1000)
    
    def to_cm(self):
        return (Pose.x_center + self.__x / 1000, Pose.y_center - self.__y / 1000)
    
    """
    
    def set_block_cell_position(self):
        """
        self.blocks_array.append([1,9])
        self.blocks_array.append([2,8])
        self.blocks_array.append([1,7])
        self.blocks_array.append([2,7])
        """
        self.blocks_array.append([2,9])
        self.blocks_array.append([1,9])
        self.blocks_array.append([0,9])
        self.blocks_array.append([3,9])
        self.blocks_array.append([4,9])
        self.blocks_array.append([5,9])
        self.blocks_array.append([7,9])
        self.blocks_array.append([9,9])
        self.blocks_array.append([6,9])
        self.blocks_array.append([8,9])
        
    def set_from(self, _from):
        self._from = _from

    def setPositionMatrix(self):
        col = row = 50
        #intervallo_orizzontale = 900 / 12  
        intervallo = 400 / self.rc
        for i in range(self.rc):
            for j in range(self.rc):
                self.position_matrix[i][j] = (col, row)
                row += intervallo
            row = 50
            col += intervallo
        print("#### Matrice settata")
    
    def setObstacle(self):
        #obstacles_matrix is an array with the pixels coordinates used to paint the obstacles on screen
        
        self.obstacles_matrix.append([self.position_matrix[6][4][0] , self.position_matrix[6][4][1] +5, 60, 10])
    
    def drawCandidateBlocks(self):
        #blocks_array is an array with the pixels coordinates used to paint the blocks on screen
        """
        self.blocks_array.append([self.position_matrix[1][9][0] , self.position_matrix[1][9][1] +5, 40, 40]) #usare questo per prendere le coordinate cm come nell'ostacolo
        self.blocks_array.append([self.position_matrix[1][8][0] , self.position_matrix[2][8][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[1][7][0] , self.position_matrix[1][7][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[2][7][0] , self.position_matrix[2][7][1] +5, 40, 40])
        """
        self.blocks_array.append([self.position_matrix[2][9][0] , self.position_matrix[2][9][1] +5, 40, 40]) #usare questo per prendere le coordinate cm come nell'ostacolo
        self.blocks_array.append([self.position_matrix[1][9][0] , self.position_matrix[1][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[0][9][0] , self.position_matrix[0][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[3][9][0] , self.position_matrix[3][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[4][9][0] , self.position_matrix[4][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[5][9][0] , self.position_matrix[5][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[7][9][0] , self.position_matrix[7][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[9][9][0] , self.position_matrix[9][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[6][9][0] , self.position_matrix[6][9][1] +5, 40, 40])
        self.blocks_array.append([self.position_matrix[8][9][0] , self.position_matrix[8][9][1] +5, 40, 40])
        
    
    def set_obstacles_cell_position(self):
        #obstacles_cell_position is an array with the cells coordinates of obstacles
        self.obstacles_cell_position.append([6,4])
    
    def generate_blocks(self, N, check):
        if self._from is not None:
            if check == 1:
                self.world.new_block(N, self.blocks_array)
                self.set_block(check)
                self.set_obs() 
            else:
                self.set_block(check)
                self.set_obs()
    
    def set_block(self, check):
        if self._from is not None:
            #print(len(self.world.get_blocks()))
            for i in range(len(self.world.get_blocks())):
                if check == 1:
                    Messaging.send_belief(self._from, 'set_block', [self.world.get_blocks()[i].get_pose()[0],self.world.get_blocks()[i].get_pose()[1],self.world.get_blocks()[i].get_color()], 'robot')
                Messaging.send_belief(self._from, 'set_obs', [self.world.get_blocks()[i].get_cell()[0], self.world.get_blocks()[i].get_cell()[1], self.world.get_blocks()[i].get_cell()[0], self.world.get_blocks()[i].get_cell()[1]], 'robot')
    
    def set_obs(self):
        if self._from is not None:
            for i in range(len(self.obstacles_cell_position)):
                Messaging.send_belief(self._from, 'set_obs', [self.obstacles_cell_position[i][0] +1, self.obstacles_cell_position[i][1]+1, self.obstacles_cell_position[i][0]+1, self.obstacles_cell_position[i][1]+1 ], 'robot')
    
    def add_new_pathpoint(self, x, y):
        print(f"Adding new path point: ({x}, {y})")
        print(f"Coordinate in pixel aggiunte: ({self.current_man_pos_x}, {self.current_man_pos_y})")

        if self.current_point_index >= len(self.path):
            start_path = True
        else:
            start_path = False

        self.path.append( (x, y) )
        if start_path:
            (x, y) = self.path[self.current_point_index]
            print(f"Nuovo punto aggiunto al percorso: ({x}, {y})")
            #self.autopilot.x_target = x 
            #self.autopilot.z_target = y
            metri_x, metri_y = self.pixel_to_m(x, y)
            self.arm.set_target_xy_a(metri_x, metri_y, -90)
            print(f"Target set to: ({metri_x}, {metri_y})")
            #self.arm.set_target_xy_a(x, y, -90)
            self.path_completed = False
            
    def run_path(self, delta_t):
        if self.current_point_index < len(self.path):
            self.debug_counter = getattr(self, 'debug_counter', 0)  # inizializza solo se non esiste
            if self.debug_counter < 1:  # Limita a 10 stampe
                print(f"Indice attuale: {self.current_point_index}, Punto attuale: {self.path[self.current_point_index]}")
                self.debug_counter += 1
            #print(f"Indice attuale: {self.current_point_index}, Punto attuale: {self.path[self.current_point_index]}")
            (x, y) = self.path[self.current_point_index]
            p = self.arm.get_pose()
            self.debug_counter1 = getattr(self, 'debug_counter', 0)  # inizializza solo se non esiste
            if self.debug_counter1 < 1:  # Limita a 10 stampe
                print(f"Coordinata target: ({x}, {y}), Posizione attuale: ({p[1][0]}, {p[1][1]})")
                self.debug_counter1 += 1
            #print(f"Coordinata target: ({x}, {y}), Posizione attuale: ({p[1][0]}, {p[1][1]})")

            current_x, current_y = p[1][0], p[1][1]
            metri_x, metri_y = self.pixel_to_m(x, y)
            d = math.sqrt((metri_x - current_x)**2 + (metri_y - current_y)**2)
            print(f"Distanza calcolata: {d}, Soglia: {self.threshold}")

            if d < self.threshold:
                print(f"Punto raggiunto: ({x}, {y}), Distanza: {d:.2f}")
                self.current_point_index += 1
                if self.current_point_index < len(self.path):
                    (x, y) = self.path[self.current_point_index]
                    print(f"Nuovo target impostato: ({x}, {y})")
                    metri_x, metri_y = self.pixel_to_m(x, y)
                    self.arm.set_target_xy_a(metri_x, metri_y, -90)
                    print(f"Nuovo target impostato metri: ({metri_x:.2f}, {metri_y:.2f})")
                else:
                    self.path_completed = True
        self.arm.evaluate_trajectory(self.delta_t)        
    """
    def run_path(self, delta_t):
        
        if self.current_point_index < len(self.path):
            
            print(f"Indice attuale: {self.current_point_index}, Punto attuale: {self.path[self.current_point_index]}")
            (x, y) = self.path[self.current_point_index]
            p = self.arm.get_pose()
            print(f"Coordinata target: ({x}, {y}), Posizione attuale: ({p[1][0]}, {p[1][1]})")
            #current_x = self.autopilot.quadrotor.x
            #current_z = self.autopilot.quadrotor.z
            current_x = p[1][0]
            current_y = p[1][1]
            #metri_x = x * self.grid_cell_size
            #metri_y = y * self.grid_cell_size
            #print(f"Movimento da ({current_x:.2f}, {current_y:.2f}) a ({metri_x:.2f}, {metri_y:.2f})")
            d = math.sqrt ( (x - current_x)**2 + (y - current_y)**2 )
            #d = math.sqrt ( (metri_x - current_x)**2 + (metri_y - current_y)**2 )
            print(f"Distanza calcolata: {d}, Soglia: {self.threshold}")
            if d < self.threshold:
                print(f"Punto raggiunto: ({x}, {y}), Distanza: {d:.2f}")
                self.current_point_index = self.current_point_index + 1
                if self.current_point_index < len(self.path):
                    (x, y) = self.path[self.current_point_index]
                    #self.autopilot.x_target = x
                    #self.autopilot.z_target = z
                    self.arm.set_target_xy_a(x, y, -90)
                    #self.arm.set_target_xy_a(x/1000, y/1000, -90)
                    #metri_x = x * self.grid_cell_size
                    #metri_y = y * self.grid_cell_size
                    #self.arm.set_target_xy_a(metri_x, metri_y, -90)
                    #self.arm.set_target_xy_a(pixel_x / 1000, pixel_y / 1000, -90)
                    #print(f"Target originale: ({x}, {y}), In metri: ({metri_x:.2f}, {metri_y:.2f}), Posizione attuale: ({current_x:.2f}, {current_y:.2f})")
                else:
                    self.path_completed = True

        #self.autopilot.run(delta_t)
        self.arm.evaluate_trajectory(self.delta_t)
    """
    def scan_blocks(self, current_pos_pixel_x, current_pos_pixel_y): #da adattare
        if self._from is not None:
            if self.grabbed:
                x = 7 #2  627
                y = 3 #13 78
                print("Mi muovo sul cestino in posizione: ", x," ", y," Posizione corrente: ", current_pos_pixel_x," ", current_pos_pixel_y)
                self.world.grab_last_block()
                Messaging.send_belief(self._from, '_target', [x, y], 'robot')
                Messaging.send_belief(self._from, '_scan', [x, y, current_pos_pixel_x, current_pos_pixel_y ], 'robot')
                return
            
            if self.grabbed == False and self.current_index_pos > len(self.world.get_blocks())-1:
                x = 2 #7
                y = 7 #14
                print("Mi muovo sulla posizione iniziale: ", x," ", y," Posizione corrente: ", current_pos_pixel_x," ", current_pos_pixel_y)
                Messaging.send_belief(self._from, '_target', [x, y], 'robot')
                Messaging.send_belief(self._from, '_scan', [x, y, current_pos_pixel_x, current_pos_pixel_y ], 'robot')
                #reset di tutti i parametri
                self.current_index_pos = 0
                self.scan_blocks_mode = True #modalità del robot
                return
            
            if(self.current_index_pos <= len(self.world.get_blocks())-1):
                x, y = self.world.get_blocks()[self.current_index_pos].get_cell_by_pixel(self.world.get_blocks()[self.current_index_pos].get_pose()[0], self.world.get_blocks()[self.current_index_pos].get_pose()[1])
                print("Mi muovo sul blocco di posizione: ", x," ", y-1," Posizione corrente: ", current_pos_pixel_x," ", current_pos_pixel_y)
                Messaging.send_belief(self._from, '_target', [x, y-1], 'robot')
                Messaging.send_belief(self._from, '_scan', [x, y-1, current_pos_pixel_x, current_pos_pixel_y ], 'robot')
            
    def marked_path(self, x, y):
        print(f"Ricevuto punto per il percorso: ({x}, {y})")
        if self._from is not None:
            if (x == -1 and y == -1):
                self.go_to(self.marked_array)
            else:
                #self.marked_array.append([x, y])
                self.marked_array.append([self.position_matrix[x][y-1][0] +15, self.position_matrix[x][y-1][1], 40, 40])
    
    def go_to(self, marked_array):
        print(f"Array marcato ricevuto: {marked_array}")
        self.marked_array.reverse() #nf1 salva il path al contrario
        self.marked_array.insert(0,[self.current_pos_x, self.current_pos_y])
        
        for i in range(len(self.marked_array)-1):
            self.debug_counter5 = getattr(self, 'debug_counter', 0)  # inizializza solo se non esiste
            if self.debug_counter5 < 1:
                if i==0:
                    i+=1
                self.debug_counter5 += 1
           
            (x, y) = self.marked_array[i][0], self.marked_array[i][1]
            self.debug_counter2 = getattr(self, 'debug_counter', 0)  # inizializza solo se non esiste
            if self.debug_counter2 < 1:  # Limita a 10 stampe
                print(f"x e y marked: ({x}, {y})")
                self.debug_counter2 += 1
            #print(f"x e y marked: ({x}, {y})")
            
            #if i > 0:
            metri_x, metri_y = self.pixel_to_m(x, y)
            self.arm.set_target_xy_a(metri_x, metri_y, -90)
            self.current_pos_x = self.marked_array[-1][0]
            self.current_pos_y = self.marked_array[-1][1]
            self.add_new_pathpoint(x, y)
        self.marked_array = []    
        """
        count_x = self.current_man_pos_x
        count_y = self.current_man_pos_y
        
        for i in range(len(self.marked_array)-1):
            if self.marked_array[i][0] == self.marked_array[i+1][0]:
                if self.marked_array[i][1] == self.marked_array[i-1][1] and i != 0:
                    self.current_man_pos_x = count_x
                    self.add_new_pathpoint(self.current_man_pos_x,self.current_man_pos_y)
                    
                if self.marked_array[i][1] > self.marked_array[i+1][1]:
                    count_y -= 1 #count_y += 1
                    
                if self.marked_array[i][1] < self.marked_array[i+1][1]:
                    count_x += 1 #count_y -= 1
                    
            if self.marked_array[i][1] == self.marked_array[i+1][1]:
                if self.marked_array[i][0] == self.marked_array[i-1][0] and i != 0:
                    self.current_man_pos_y = count_y
                    self.add_new_pathpoint(self.current_man_pos_x, self.current_man_pos_y)
                    
                if self.marked_array[i][0] > self.marked_array[i+1][0]:
                    count_x += 1 #count_x -= 1
                    
                if self.marked_array[i][0] < self.marked_array[i+1][0]:
                    count_y -= 1 #count_x += 1
                    
        self.current_man_pos_x = count_x
        self.current_man_pos_y = count_y
        self.current_pos_x = self.marked_array[-1][0]
        self.current_pos_y = self.marked_array[-1][1]
        
        self.add_new_pathpoint(self.current_man_pos_x, self.current_man_pos_y)
        self.marked_array = []   
    
    
    def go_to(self,target_x, target_y, target_alpha):
        self.notification = False
        self.arm.set_target_xy_a(target_x, target_y, target_alpha)
 
    def notify_target_got(self):
        self.notification = True
        if self._from is not None:
            Messaging.send_belief(self._from, 'target_got', [], 'robot')
    
    def send_pos(self):
        if self._from is not None:
            p = self.arm.get_pose_xy_a().get_pose()
            Messaging.send_belief(self._from, 'pose', [p[0], p[1], math.degrees(p[2])], 'robot')

    def sense_distance(self):
        if self._from is not None:
            d = self.world.sense_distance()
            if d is None:
                params = []
            else:
                params = [d]
            Messaging.send_belief(self._from, 'distance', params, 'robot')

    def sense_color(self):
        if self._from is not None:
            d = self.world.sense_color()
            if d is None:
                params = []
            else:
                params = [d]
            Messaging.send_belief(self._from, 'color', params, 'robot')
    """
    def go(self):
        #self.telemetry.gather(self.delta_t, self.arm.element_3_model.w, self.arm.element_3_control.w_target)
        #if self.t > 8:
        #    self.telemetry.show()
        #    sys.exit(0)
        """
        if self.trajectory.target_got:
            if not(self.notification):
                self.notify_target_got()
        """
        self.run_path(self.delta_t)     #ULTIMA MODIFICA
        
        #self.arm.evaluate_trajectory(self.delta_t)

        #p = self.arm.get_pose()
        #self.trajectory_data.append(p[-1])
        #if self.use_trajectory:
        #    self.target_trajectory_data.append( (self.arm.trajectory_x, self.arm.trajectory_y) )
        self.t += self.delta_t
        self.update() # repaint window

    def check_final_pos(self, x, y): #da aggiornare
        self.debug_counter3 = getattr(self, 'debug_counter', 0)  # inizializza solo se non esiste
        if self.debug_counter3 < 1:  # Limita a 10 stampe
            print(f"x e y checked pos att: ({x}, {y})")
            self.debug_counter3 += 1
        #print(f"x e y checked: ({x}, {y})")
        if(len(self.world.get_blocks()) == 0):
            return
        #GRAB
        if self.grabbed:
            final_x = 627 #100  627  600
            final_y = 78 #1300 -100   78   200
        elif(self.current_index_pos > len(self.world.get_blocks())-1):
            final_x = 607 #7   607  2
            final_y = 97 #14  97   7
        else:
            final_x = int(self.world.get_blocks()[self.current_index_pos].get_pose()[0])
            final_y = int(self.world.get_blocks()[self.current_index_pos].get_pose()[1] - 100)
        self.debug_counter4 = getattr(self, 'debug_counter', 0)  # inizializza solo se non esiste
        if self.debug_counter4 < 1:  # Limita a 10 stampe
            print(f"x e y final: ({final_x}, {final_y})") 
            self.debug_counter4 += 1
        #print(f"x e y final: ({final_x}, {final_y})")    
        
        #SCAN
        if self.scan_blocks_mode == True: 
            x1, y1 = self.world.get_blocks()[self.current_index_pos].get_cell_by_pixel(self.world.get_blocks()[self.current_index_pos].get_pose()[0], self.world.get_blocks()[self.current_index_pos].get_pose()[1])
	    #se è in prossimità del blocco
            if((int(x) >= final_x - 20 and int(x) <= final_x + 20) and (int(y) >= final_y - 60 and int(y) <= final_y + 60)):
                #scan colore
                Messaging.send_belief(self._from, 'color', [COLOR_NUM[str(self.world.get_blocks()[self.current_index_pos].get_color())] ], 'robot') #legge il colore del blocco
                if self.current_index_pos < len(self.world.get_blocks())-1: #se i blocchi non sono stati scansionati tutti
                    self.marked_array = []
                    Messaging.send_belief(self._from, 'restart', [x1, y1-1], 'robot') #riavvia la ricerca del path con nf1
                    self.current_index_pos += 1
                else:
                    self.current_index_pos = 0  #reset indice della lettura dei blocchi
                    self.world.sort_blocks()    #riordina i blocchi in base ai colori dopo lo scan
                    self.scan_blocks_mode = False    #passa in modalità grab	 
                           
	            #primo grab
                    print("Modalita' grab.")
                    x1_, y1_ = self.world.get_blocks()[self.current_index_pos].get_cell_by_pixel(self.world.get_blocks()[self.current_index_pos].get_pose()[0], self.world.get_blocks()[self.current_index_pos].get_pose()[1])
                    if(x1_ == x1 and y1_ == y1):
                        self.grabbed = True
                        Messaging.send_belief(self._from, 'restart', [x1_, y1_-1], 'robot') #riavvia la ricerca del path
                    else:
                        Messaging.send_belief(self._from, 'restart', [x1, y1-1], 'robot') #riavvia la ricerca del path
	         
        else: #in modalità grab
            
            if((int(x) >= final_x - 20 and int(x) <= final_x + 20) and (int(y) >= final_y - 60 and int(y) <= final_y + 60)): #quando è in prossimità del punto
                if final_x == 627 and final_y == 78: #se il robot si trova sul cestino 600 200

                    self.grabbed = False
                    #qui operazione di release
                    print("Rilascio il cubo di colore: ", COLOR_NUM[str(self.world.get_blocks()[self.current_index_pos].get_color())])
                    Messaging.send_belief(self._from, 'remove_block', [self.world.get_blocks()[self.current_index_pos].get_pose()[0], self.world.get_blocks()[self.current_index_pos].get_pose()[1], self.world.get_blocks()[self.current_index_pos].get_color()], 'robot')
                    Messaging.send_belief(self._from, 'trashed', [COLOR_NUM[str(self.world.get_blocks()[self.current_index_pos].get_color())]], 'robot')
                    
                    #si avvia verso il prossimo grab
                    x1, y1 = self.world.get_blocks()[self.current_index_pos].get_cell_by_pixel(self.world.get_blocks()[self.current_index_pos].get_pose()[0], self.world.get_blocks()[self.current_index_pos].get_pose()[1])
                    self.current_index_pos += 1
                    
                    if self.current_index_pos > len(self.world.get_blocks())-1: #se tutti i blocchi sono stati grabbati
                        self.world.remove_blocks()
                        self.marked_array = []
                        Messaging.send_belief(self._from, 'restart', [7, 3], 'robot') #ritorna nella posizione iniziale
                    else:
                        self.marked_array = []
                        #si riparte dal cestino al prossimo blocco da grabbare
                        Messaging.send_belief(self._from, 'restart', [7, 3], 'robot') #riavvia la ricerca del path
                        
                else: #si trova su un blocco
                    if self.grabbed != True:
                       x1, y1 = self.world.get_blocks()[self.current_index_pos].get_cell_by_pixel(self.world.get_blocks()[self.current_index_pos].get_pose()[0], self.world.get_blocks()[self.current_index_pos].get_pose()[1])
                       self.grabbed = True
                       self.marked_array = []
                       Messaging.send_belief(self._from, 'restart', [x1, y1-1], 'robot') #Si avvia verso il cestino

    """
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QColor(255,255,255))
        qp.setBrush(QtGui.QColor(255,255,255))
        qp.drawRect(event.rect())

        qp.setPen(QtCore.Qt.black)
        qp.drawRect(50, 50, 900, 500)
        #qp.drawLine(50, 500, 900, 500)
        #qp.drawLine(50, 500, 50, 50)
        #qp.drawLine(50, 50, 900, 50)
        #qp.drawLine(900, 50, 900, 500)
        

        qp.setPen(QtCore.Qt.black)
        self.painter.paint(qp, self.t)
        self.world.paint(qp)

        qp.end()
    """
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
    
    # Imposta il colore per il rettangolo
        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(event.rect())  # Disegna il rettangolo di base (finestra)

    # Disegna il rettangolo principale di 900x500px
        qp.setPen(QtCore.Qt.black)
        qp.drawRect(50, 50, 400, 400)
        
        
        """
        qp.setPen(QPen(QtGui.QColor(217,95,14), 5, Qt.SolidLine))
        qp.setBrush(QBrush(QtGui.QColor(217,95,14)))
        qp.drawRect(384, 250, 60, 10)
        
        qp.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        qp.setBrush(QBrush(Qt.black, Qt.DiagCrossPattern))
        qp.drawRect(394,195, 40, 50)
        """
        #posizione cestino(riga2, colonna 4)
        
        
        #qp.setPen(QtCore.Qt.black)
        #self.painter.paint(qp, self.t)
        #self.world.paint(qp)
        x, y, w, h = self.obstacles_matrix[0]
        #print(f"coord obs: ({x}, {y})")
        #metri_x, metri_y = self.pixel_to_m(x, y)
        #self.arm.set_target_xy_a(metri_x, metri_y, -90)
        #print(f"Nuovo target impostato: ({metri_x:.2f}, {metri_y:.2f})")
        qp.setPen(QPen(QtGui.QColor(217,95,14), 5, Qt.SolidLine))
        qp.setBrush(QBrush(QtGui.QColor(217,95,14)))
        qp.drawRect(x,y,w,h)
        
        qp.setPen(QPen(Qt.red, 5, Qt.SolidLine))
        qp.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
        qp.drawRect(x,y,w,h)
        
        qp.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        qp.setBrush(QBrush(Qt.black, Qt.DiagCrossPattern))
        qp.drawRect(x+10,y-55,w-20,h+40)
        
        """
        for i in range(len(self.obstacles_matrix)):
            x, y, w, h = self.obstacles_matrix[i]
            qp.drawRect(x,y,w,h)
        """
        
        #qp.end()
    
        p = self.arm.get_pose() #provare a utilizzare solo questi valori senza trasformazioni
        #self.m_to_pixel(p[1][0], p[1][1])
        pxx, pxy = self.m_to_pixel(p[1][0], p[1][1])
        #print(f"Posizione pixel: ({int(pxx)}, {int(pxy)}), Posizione attuale: ({p[1][0]}, {p[1][1]})")
        #x_man_pos = int(math.ceil(600 + (p[1][0] * 100))) #600
        #y_man_pos = int(100 - (p[1][1] * 100 )) #1300
        #self.check_final_pos(x_man_pos, y_man_pos)
        self.check_final_pos(int(pxx), int(pxy))
        """
        for i in range(4):
            #self.blocks_array.append([self.position_matrix[2][9][0] , self.position_matrix[2][9][1] +5, 40, 40])
            #self.blocks_array.append([self.position_matrix[1][9][0] , self.position_matrix[1][9][1] +5, 40, 40])
            #self.blocks_array.append([self.position_matrix[0][9][0] , self.position_matrix[0][9][1] +5, 40, 40])
            #self.blocks_array.append([self.position_matrix[3][9][0] , self.position_matrix[3][9][1] +5, 40, 40])
            x, y, w, h = self.blocks_array[i]
            print(f"coord first blocks: ({x}, {y}, {i})")
            metx, mety = self.pixel_to_m(x, y)
            print(f"coord mt first blocks: ({metx}, {mety}, {i})")
            px, py = self.m_to_pixel(metx, mety)
            print(f"coord px first blocks: ({px}, {py}, {i})")
        """    
    # Aggiungi il codice per visualizzare la matrice
    # Ogni posizione (col, row) della matrice sarà rappresentata da un piccolo cerchio
        for i in range(self.rc):  #  righe
            for j in range(self.rc):  #  colonne
                col, row = self.position_matrix[i][j]  # Ottieni la posizione (col, row)
                
            # Disegna un piccolo cerchio in ogni posizione della matrice
                qp.setBrush(QtGui.QColor(0, 0, 255))  # Colore per i punti
                qp.drawEllipse(col, row, 10, 10)  # Cerchio di 10px di diametro

            # Se vuoi visualizzare le coordinate come testo invece del cerchio
            # qp.setFont(QFont('Arial', 6))
            # qp.setPen(QColor(0, 0, 0))  # Colore del testo
            # qp.drawText(col, row, f"({col}, {row})")
    
    # Dipingi anche altre informazioni (ad esempio l'animazione del braccio)
        qp.setPen(QtCore.Qt.black)
        self.painter.paint(qp, self.t)
        self.world.paint(qp)

        qp.end()
    

def main():
    
    
    app = QApplication(sys.argv)
    ex = MainWindow()
    
    
    start_message_server_http(ex)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

