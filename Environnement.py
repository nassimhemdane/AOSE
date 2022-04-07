import random

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import time


class Environnement(Model):
    """A model with some number of agents."""

    def __init__(self):
        pass


    def setup(self,nb_agents,nb_consumers,nb_producers , width, height):
        self.num_agents = nb_agents
        self.nb_consumers = nb_consumers
        self.nb_producers= nb_producers
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running=True

        self.day=0
        self.hour=0
        self.season=0
        self.max_season=5
        self.wind=4
        self.windlist=[str(i*10)+"-"+str(i+1)+"km/h" for i in range(10)]


    def setup(self,Lagents,marketPlace,width,height,step_per_hour=10):
        self.num_agents = len(Lagents)
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.marketplaceID= marketPlace.get_id()
        self.day = 0
        self.vday=0
        self.hour = 0
        self.season = 0
        self.max_season = 6
        self.wind = 4
        self.step_per_hour=step_per_hour
        self.windlist = [str(i * 10) + "-" + str(i + 1) + "km/h" for i in range(10)]
        self.reset_wind()
        self.addinglist=[]
        self.deletinglist=[]

        # Create agents
        for a in Lagents:
            self.schedule.add(a)
            # Add the agent to a random grid cell
            self.grid.place_agent(a, (a.x, a.y))
        self.schedule.add(marketPlace)
        self.grid.place_agent(marketPlace, (marketPlace.x, marketPlace.y))

        self.datacollector = DataCollector(
        )

    def random_change(self,x):
        if(random.random()>0.5):
            if(x<len(self.windlist)-1):
                return x+1
            else:
                return x
        else:
            if(x>0):
                return x-1
            else:
                return x
    def reset_wind(self):
        self.wind_pred = []
        lastW=self.wind
        for i in range(24):
            lastW=self.random_change(lastW)
            self.wind_pred.append(lastW)

    def send(self,sender_id,receiver_id,content):
        if(sender_id in self.get_agent(receiver_id).inbox.keys()):
            self.get_agent(receiver_id).inbox[sender_id].append(content)
        else:
            self.get_agent(receiver_id).inbox[sender_id]=[content]

    def get_agent(self,id):
        for i in self.schedule.agents:
            if(i.get_id()==id):
                return i
        return None

    def actualize_week(self):
        self.day=0
        if(self.season<self.max_season):
            self.season+=1
        else:
            self.season=0
        for i in self.schedule.agents:
            if(i.get_id() != self.marketplaceID):
                i.reset_week()

    def embody_changes(self):
        for i in self.addinglist:
            self.schedule.add(i[0])
            self.grid.place_agent(i[0],i[1],i[2])
        for i in self.deletinglist:
            self.schedule.remove(i)
            self.grid.remove_agent(i)

    def actualize_day(self):
        self.hour= 0
        self.reset_wind()
        self.embody_changes()
        self.addinglist=[]
        self.deletinglist=[]
        for i in self.schedule.agents:
            i.reset_day()
        pass

    def actualize_hour(self):
        pass

    def run(self,steps=10):
        for i in range(steps):
            self.rweek()

    def rweek(self):
        for i in range(7):
            self.rday()
        self.season+=1
        self.actualize_week()

    def rhour(self):
        for i in range(self.step_per_hour):
           self.step()
        self.actualize_hour()
        self.hour+=1


    def rday(self):
        for j in range(24):
            self.rhour()
            time.sleep(0)
        self.day+=1
        self.vday+=1
        self.actualize_day()

    def step(self):
        self.schedule.step()

    def add_agent(self,agent,x,y):
        self.addinglist.append((agent,x,y))

    def delete_agent(self,agent):
        self.deletinglist.append(agent)


