import constants as const
import numpy
inst_callback = None


class Piece(object):
    def __init__(self, index_, primary_side_):
        self.index = index_
        self.orientation = 0
        self.primary_side = primary_side_


class Edge(Piece):
    def __init__(self, index_, primary_side_, secondary_side_):
        Piece.__init__(self, index_, primary_side_)
        self.secondary_side = secondary_side_


class Corner(Piece):
    def __init__(self, index_, primary_side_, top_side_, side_side_):
        Piece.__init__(self, index_, primary_side_)
        self.top_side = top_side_
        self.side_side = side_side_


Edges = dict()
Corners = dict()
Middle = dict()

Corners[0] = Corner(1, const.GREEN, const.YELLOW, const.PINK) #  |625|1
Corners[1] = Corner(2, const.GREEN, const.PINK, const.WHITE) #   |654|2
Corners[2] = Corner(3, const.GREEN, const.WHITE, const.RED) #    |643|3
Corners[3] = Corner(4, const.GREEN, const.RED, const.YELLOW) #   |632|4
Corners[4] = Corner(5, const.BLUE, const.PINK, const.YELLOW) #   |152|5
Corners[5] = Corner(6, const.BLUE, const.WHITE, const.PINK) #    |145|6
Corners[6] = Corner(7, const.BLUE, const.RED, const.WHITE) #     |134|7
Corners[7] = Corner(8, const.BLUE, const.YELLOW, const.RED) #    |123|8

Edges[0] = Edge(1, const.YELLOW, const.GREEN) #  |26|1
Edges[1] = Edge(2, const.PINK, const.GREEN) #    |56|2
Edges[2] = Edge(3, const.WHITE, const.GREEN) #   |46|3
Edges[3] = Edge(4, const.RED, const.GREEN) #     |36|4
Edges[4] = Edge(5, const.PINK, const.YELLOW) #   |52|5
Edges[5] = Edge(6, const.PINK, const.WHITE) #    |54|6
Edges[6] = Edge(7, const.RED, const.WHITE) #     |34|7
Edges[7] = Edge(8, const.RED, const.YELLOW) #    |32|8
Edges[8] = Edge(9, const.YELLOW, const.BLUE) #   |21|9
Edges[9] = Edge(10, const.PINK, const.BLUE) #   |51|10
Edges[10] = Edge(11, const.WHITE, const.BLUE) #  |41|11
Edges[11] = Edge(12, const.RED, const.BLUE) #    |31|12


Middle[0] = Piece(1, const.BLUE)
Middle[1] = Piece(2, const.YELLOW)
Middle[2] = Piece(3, const.RED)
Middle[3] = Piece(4, const.WHITE)
Middle[4] = Piece(5, const.PINK)
Middle[5] = Piece(6, const.GREEN)

state3D = numpy.zeros((3, 3, 3), Piece)
stateC = numpy.zeros(8, Corner)
stateE = numpy.zeros(12, Edge)


state3D[0][1][1] = Middle[1], (2, )
state3D[1][0][1] = Middle[5], (6, )
state3D[1][1][0] = Middle[2], (3, )
state3D[1][1][1] = Piece(0, None), (0, )
state3D[1][1][2] = Middle[4], (5, )
state3D[1][2][1] = Middle[0], (1, )
state3D[2][1][1] = Middle[3], (4, )


def windup():
    global state3D
    global stateC
    global stateE  # that's heck weird, but i don't think it can be done any other way i'm going for layers


    state3D[0][0][0] = stateC[3], (6, 3, 2)
    state3D[0][0][1] = stateE[0], (2, 6)
    state3D[0][0][2] = stateC[0], (6, 2, 5)

    state3D[0][1][0] = stateE[7], (3, 2)
    #  te3D[0][1][1] = Middle[1], ()
    state3D[0][1][2] = stateE[4], (5, 2)

    state3D[0][2][0] = stateC[7], (1, 2, 3)
    state3D[0][2][1] = stateE[8], (2, 1)
    state3D[0][2][2] = stateC[4], (1, 5, 2)

# --------------------------------------

    state3D[1][0][0] = stateE[3], (3, 6)
    #  te3D[1][0][1] = Middle[5], ()
    state3D[1][0][2] = stateE[1], (5, 6)

    #  te3D[1][1][0] = Middle[2], ()
    #  te3D[1][1][1] = Piece(0, None)
    #  te3D[1][1][2] = Middle[4], ()

    state3D[1][2][0] = stateE[11], (3, 1)
    #  te3D[1][2][1] = Middle[0], ()
    state3D[1][2][2] = stateE[9], (5, 1)

# ------------------------------------------

    state3D[2][0][0] = stateC[2], (6, 4, 3)
    state3D[2][0][1] = stateE[2], (4, 6)
    state3D[2][0][2] = stateC[1], (6, 5, 4)

    state3D[2][1][0] = stateE[6], (3, 4)
    #  te3D[2][1][1] = Middle[3], ()
    state3D[2][1][2] = stateE[5], (5, 4)

    state3D[2][2][0] = stateC[6], (1, 3, 4)
    state3D[2][2][1] = stateE[10], (4, 1)
    state3D[2][2][2] = stateC[5], (1, 4, 5)


def intake(data):
    global stateC
    global stateE
    global state3D

    config = data[:31]
    corn_perm_s = list(config[:8])
    corn_ornt_s = list(config[8:16])
    edge_perm_s = list(config[16:28])
    edge_ornt_s = list(format(int(config[28:], 16), "0>12b"))

    corn_perm_i = []
    corn_ornt_i = []
    edge_perm_i = []
    edge_ornt_i = []

    for item in corn_perm_s:
        corn_perm_i.append(int(item))
    for item in corn_ornt_s:
        corn_ornt_i.append(int(item))
    for item in edge_perm_s:
        edge_perm_i.append(int(item, 16))
    for item in edge_ornt_s:
        edge_ornt_i.append(int(item))

    for i, item in enumerate(corn_perm_i):
        stateC[i] = Corners[item-1]
        stateC[i].orientation = corn_ornt_i[i]
    for i, item in enumerate(edge_perm_i):
        stateE[i] = Edges[item-1]
        stateE[i].orientation = edge_ornt_i[i]

    windup()
    if inst_callback is not None:
        inst_callback(state3D)
