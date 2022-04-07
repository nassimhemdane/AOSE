import random

from Environnement import Environnement
from MarketPlaceAgent import MarketPlaceAgent
from ProsumerAgent import *



job= [[[0,0] + [1 for i in range(20)] + [0,0] ,15],
        [[0,0] + [1 for i in range(20)] + [0,0] ,15],
        [[0,0] + [1 for i in range(18)] + [0,0,0,0] ,10],
        [[1 for i in range(24)] ,24],
        [[0,0] + [1 for i in range(20)] + [0,0] ,15],
        [[0,0] + [1 for i in range(20)] + [0,0] ,15],
        [[0,0] + [1 for i in range(20)] + [0,0] ,15]
       ]
job2= [[[0,0] + [1 for i in range(20)] + [0,0] ,15],
        [[0,0] + [1 for i in range(20)] + [0,0] ,0],
        [[0,0] + [1 for i in range(18)] + [0,0,0,0] ,0],
        [[1 for i in range(24)] ,0],
        [[0,0] + [1 for i in range(20)] + [0,0] ,0],
        [[0,0] + [1 for i in range(20)] + [0,0] ,0],
        [[0,0] + [1 for i in range(20)] + [0,0] ,0]
       ]

machinealaver = [[[1 for i in range(24)],2],
[[1 for i in range(24)],0],
[[1 for i in range(24)],0],
[[1 for i in range(24)],0],
[[1 for i in range(24)],0],
[[1 for i in range(24)],0],
[[1 for i in range(24)],0]

                 ]
jobs=[job]
Sjobs=[job2]
mdl = Environnement();
mrkt= MarketPlaceAgent(5,mdl,8,8)
ag1 = ProsumerAgent(1,[0,0,0,0],True,mdl,0,0,jobs=jobs,Sjobs=Sjobs,weights=[1,0,0])
ag2 = ProsumerAgent(2,[0,1,1,0],True,mdl,1,1,jobs=jobs,Sjobs=Sjobs,weights=[1,0,0])
ag3 = ProsumerAgent(3,[0,1,1,0],False,mdl,2,2,jobs=jobs,Sjobs=Sjobs,weights=[1,0,0])
ag4 = ProsumerAgent(4,[0,0,0,0],False,mdl,3,3,jobs=jobs,Sjobs=Sjobs,weights=[1,0,0])

lagents= [ag1,ag2,ag3,ag4]

mdl.setup(lagents,mrkt,10,10,15)
mrkt.setup()
ag1.setup()
ag2.setup()
ag3.setup()
ag4.setup()
mdl.rweek()

