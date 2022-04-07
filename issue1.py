""" Testing if incrementing seasons works
"""
from Environnement import Environnement
from MarketPlaceAgent import MarketPlaceAgent
from ProsumerAgent import ProsumerAgent

fridge= [[[1 for i in range(24)] ,24]]*7

washingMachine = [[[1 for i in range(24)],2],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0]]

TV = [[[1 for i in range(24)] ,4]]*5
TV.append([[0 for i in range(24)] ,0])
TV.append([[0 for i in range(24)] ,0])

jobs = [fridge]
Sjobs = [washingMachine,TV]

mdl = Environnement();
mrkt= MarketPlaceAgent(5,mdl,8,8)

# Producer Agent : fossil and solar
ag1 = ProsumerAgent(1,[1,0,0,1],False,mdl,1,1)
# Consumer Agent prefers green > renewable > prices
ag2 = ProsumerAgent(2,[0,0,0,0],True,mdl,2,2,jobs=jobs,Sjobs=Sjobs,weights=[0,0,1])

lagents= [ag1,ag2]

mdl.setup(lagents,mrkt,10,10,15)
mrkt.setup()
ag1.setup()
ag2.setup()
mdl.rweek()
mdl.rweek()
mdl.rweek()
mdl.rweek()
mdl.rweek()
mdl.rweek()
mdl.rweek()
mdl.rday()
