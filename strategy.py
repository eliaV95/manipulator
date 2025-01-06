#
#
#
import sys
import math

sys.path.insert(0, "D:\Download\phidias-master\lib")

from phidias.Types import *
from phidias.Main import *
from phidias.Lib import *
from phidias.Agent import *

# beliefs interpreted by the robot
class go_to(Belief): pass
class generate_blocks(Belief): pass
class scan_blocks(Belief): pass
class target(SingletonBelief): pass
class block_gen(Belief): pass
class mark(Belief): pass
class size(SingletonBelief): pass
#class sizec(SingletonBelief): pass
#class sizer(SingletonBelief): pass
class lastPos(SingletonBelief): pass
class numBlocks(SingletonBelief): pass
class candidate(SingletonBelief): pass
class marked_path(Belief): pass

#procedures
class pick(Procedure): pass
class obstacle(Procedure): pass
class generate_matrix(Procedure): pass
class nf1(Procedure): pass
class do_mark(Procedure): pass
class plan(Procedure): pass
class path(Procedure): pass
class generate_candidate(Procedure): pass
class select_candidate(Procedure): pass
class save_path(Procedure): pass
class show_map(Procedure): pass
class go(Procedure): pass
class gen_block(Procedure): pass
class scan(Procedure): pass
class generate(Procedure): pass

#reactors
class color(Reactor): pass  #colore del blocco
class restart(Reactor): pass
class set_block(Reactor): pass
class set_obs(Reactor): pass
class _scan(Reactor): pass
class _target(Reactor): pass
class trashed(Reactor): pass
class remove_block(Reactor): pass

class compute_distance(Action):
    def execute(self, xs, ys, x, y, d):
        distance = math.hypot(xs() - x(), ys() - y())
        d(distance)

class distance_less(ActiveBelief):
    def evaluate(self, xs, ys, x, y, d):
        distance = math.hypot(xs() - x(), ys() - y())
        return distance < d()
        
def_vars('X','Y','A','_A','D', 'W', 'C', 'N', 'M', 'x_obs', 'y_obs', 'x_b', 'y_b', 'w', 'h', 'XP', 'XM', 'YP', 'YM', 'XS', 'YS', 'XE', 'YE', 'XC', 'YC', 'DC', 'DS','last_X', 'last_Y')

# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------
class main(Agent):
    def main(self):
        # commands
        gen_block(N) >> [ +generate_blocks(N, 1)[{'to': 'robot@127.0.0.1:6566'}] ]
        gen_block(N, C) >> [ +generate_blocks(N,C)[{'to': 'robot@127.0.0.1:6566'}] ]
        scan(X, Y) >> [ +scan_blocks(X, Y)[{'to': 'robot@127.0.0.1:6566'}] ]
        save_path(X, Y) >> [ +marked_path(X,Y)[{'to': 'robot@127.0.0.1:6566'}]]

        generate(0) >> [show_line("Non puoi aggiungere 0 blocchi.")]
        generate() >> [show_line("Inserisci un  numero di blocchi da inserire.")]
        generate(N) / (numBlocks(W) & gt(W,0)) >> [ gen_block(N), +size(10), generate_matrix(), -numBlocks(W), "W= W + N", +numBlocks(W)]
        generate(N) >> [ gen_block(N), +size(10), generate_matrix(), +numBlocks(N)]
        generate(N,C) / (numBlocks(W) & gt(W,0)) >> [ gen_block(N,C), +size(10), generate_matrix(), -numBlocks(W), "W= W + N", +numBlocks(W)]

        pick() >> [show_line("pick() started!"), scan(3,8)]
        +_scan(XE, YE, XS, YS)[{'from':_A}] >> [ show_line("Start: ", XS, " ", YS," - End: ", XE, " ", YE), path(XS, YS, XE, YE) ]
        +_target(XE, YE)[{'from':_A}] >> [ +target(XE, YE) ]
        
        +set_block(x_b,y_b, C)[{'from':_A}] >> [ +block_gen(x_b,y_b, C)]
        +set_obs(x_obs,y_obs,w,h)[{'from':_A}] >> [ obstacle(x_obs,y_obs, w, h)]
        +remove_block(x_b, y_b, C)[{'from':_A}] >> [ show_line("cancello il blocco da kb "), -block_gen(x_b,y_b, C)]
        
        +color(C)[{'from':_A}]  >> [ show_line("Il colore del blocco e': ", C)]  
        +restart(X, Y)[{'from':_A}] / numBlocks(N) >> [ generate(N, 0), scan(X, Y) ]
        +trashed(C)[{'from':_A}]  >> [ show_line("Blocco di colore ", C , " cestinato.")]  
        
        
# NF1
        obstacle(XS, YS, XE, YE)  >> [ obstacle(XS, YS, XS, YS, XE, YE) ]
        obstacle(X, Y, XS, YS, XE, YE) / gt(Y, YE) >> [ ]
        obstacle(X, Y, XS, YS, XE, YE) / gt(X, XE) >> [ "Y = Y + 1", obstacle(XS, Y, XS, YS, XE, YE) ]
        obstacle(X, Y, XS, YS, XE, YE) / mark(X, Y, D) >> \
        [
            -mark(X, Y, D),
            "X = X + 1",
            obstacle(X, Y, XS, YS, XE, YE)
        ]

        generate_matrix() / size(N) >> [ generate_matrix(N, N), show_line("Generazione mappa") ]

        generate_matrix(0, Y) >> []
        generate_matrix(X, 0) / size(N) >> [ "X=X-1", generate_matrix(X, N) ]
        generate_matrix(X, Y) / mark(X, Y, D) >> [ -mark(X, Y, D), +mark(X,Y,0), "Y=Y-1", generate_matrix(X,Y) ]
        generate_matrix(X, Y) >> [ +mark(X,Y,0), "Y=Y-1", generate_matrix(X,Y) ]

        show_map() / size(N) >> [ show_line(""), show_map(1, 1, N, N) ]

        show_map(X, Y, XE, YE) / gt(Y,YE) >> [ show_line("") ]
        show_map(X, Y, XE, YE) / gt(X, XE) >> [ "Y=Y+1", show_line(""), show_map(1, Y, XE, YE) ]
        show_map(X, Y, XE, YE) / mark(X, Y, -1) >> [ show(" ** |"), "X=X+1", show_map(X, Y, XE, YE)]
        show_map(X, Y, XE, YE) / mark(X, Y, D) >> [ show_fmt("%3d |", D), "X=X+1", show_map(X, Y, XE, YE) ]
        show_map(X, Y, XE, YE) >> [ show("XXXX|"), "X=X+1", show_map(X,Y,XE,YE) ]

        path(XS, YS, XE, YE) / mark(XE, YE, 0) >> \
        [
            -mark(XE, YE, 0), +mark(XE, YE, -1),
            nf1(XE, YE),
            show_map(),
            plan(XS, YS, XE, YE)
        ]

        #nf1 esegue la marcatura (numeretti)
        nf1(X,Y) / (mark(X, Y, D) & lt(D, 0))>> \
        [
            -mark(X, Y, D),
            "D = -D",
            +mark(X, Y, D),
            "D = D + 1",
            "XP = X + 1", "XM = X - 1",
            "YP = Y + 1", "YM = Y - 1",
            do_mark(XP, Y, D),
            do_mark(XM, Y, D),
            do_mark(X, YP, D),
            do_mark(X, YM, D),
            nf1(XP, Y),
            nf1(XM, Y),
            nf1(X, YP),
            nf1(X, YM)
        ]

        do_mark(X, Y, D) / mark(X, Y, 0) >> [ -mark(X, Y, 0), "D = -D", +mark(X, Y, D) ]
        do_mark(X, Y, D) / (mark(X, Y, DS) & lt(D, DS)) >> [ -mark(X, Y, DS), "D = -D", +mark(X, Y, D) ]
        plan(XE, YE, XE, YE) / (mark(XE, YE, D) & target(X, Y))>> [
                                                    save_path(-1, -1),
                                                    #show_line("Ultimo Nodo a ritroso ", XE, ",", YE), 
                                                    -mark(XE, YE, D), 
                                                    +mark(XE, YE, -1),
                                                    show_map() ]#fine
        
        plan(XS, YS, XE, YE) / mark(XE, YE, D) >> \
        [
            "XP = XE + 1", "XM = XE - 1",
            "YP = YE + 1", "YM = YE - 1",
              
            generate_candidate(XS, YS, XP, YE),#destra
            generate_candidate(XS, YS, XM, YE),#sinistra
            generate_candidate(XS, YS, XE, YP),#giu
            generate_candidate(XS, YS, XE, YM),#su
            select_candidate(XS, YS, XE, YE)
        ]

        #controlla che il vicino è uguale e la distanza è più piccola rispetto a posizione finale
        generate_candidate(XS, YS, X, Y) / (candidate(XC, YC, DC, DS) & mark(X, Y, D) & eq(D, DC) & distance_less(XS, YS, X, Y, DS)) >> \
        [
            compute_distance(XS, YS, X, Y, DS),
            +candidate(X, Y, D, DS)
        ]
        
        generate_candidate(XS, YS, X, Y) / (candidate(XC, YC, DC, DS) & mark(X, Y, D) & gt(D, DC) & distance_less(XS, YS, X, Y, DS)) >> \
        [
            compute_distance(XS, YS, X, Y, DS),
            +candidate(X, Y, D, DS)
        ]
        
        generate_candidate(XS, YS, X, Y) / candidate(XC, YC, DC, DS)  >>  \
        [
        ]
        
        generate_candidate(XS, YS, X, Y) / (mark(X, Y, D) & gt(D, 0)) >> \
        [
            "DS = 0",
            compute_distance(XS, YS, X, Y, DS),
            +candidate(X, Y, D, DS)
        ]



        select_candidate(XS, YS, XE, YE) / (candidate(XC, YC, DC, DS) & mark(XE, YE, D))  >> \
        [
            -candidate(XC, YC, DC, DS),
            -mark(XE, YE, D),
            +mark(XE, YE, -1), # mark as path node
            save_path(XE, YE),
            +lastPos(XE,YE),
            plan(XS, YS, XC, YC)
        ]

        



ag = main()
ag.start()

PHIDIAS.run_net(globals(), 'http')
PHIDIAS.shell(globals())

