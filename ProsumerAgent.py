import math
import random

from mesa import Agent, Model
from transitions import Machine, State
import numpy as np


class ProsumerAgent(Agent):
    """An agent with fixed initial wealth."""
    Astates = ["InitP", "prices_sent", "got_Pvalidation", "outP",
               "InitC", "ask_for_prices", "got_prices_tables", "sent_purchase", "got_Cvalidation", "outC",
               "Init", "out"]
    BaseWind= [-1,0.7,0.6,0.55,0.5,0.45,0.4,0.35,0.3,-1]
    BaseNuclear = [0.15 for i in range(6)] + [0.2 for i in range(16)] + [0.15 for i in range(2)]
    FossilePrices=[0.3,0.4,0.5]
    PriceVariance= [-0.05,0,0.05]

    SpecialU={0:(1,1),1:(0,0),2:(1,0),3:(0,0)}



    def change_prices(self):
        random.shuffle(ProsumerAgent.FossilePrices)
        self.fossile_price =ProsumerAgent.FossilePrices[0]
        random.shuffle(ProsumerAgent.PriceVariance)
        self.table_wind = [-1] + [ProsumerAgent.BaseWind[i] + ProsumerAgent.PriceVariance[0] for i in range(1,9)] + [-1]
        random.shuffle(ProsumerAgent.PriceVariance)
        self.nuclear_price = [ProsumerAgent.BaseNuclear[i] + ProsumerAgent.PriceVariance[0] for i in range(24)]
        random.shuffle(ProsumerAgent.FossilePrices)
        self.solar_price = [([-1 for i in range(4+j)]+[ProsumerAgent.FossilePrices[0] for i in range(18-2*j)]+ [-1 for i in range(2+j)]) for j in range(6)]


    def __init__(self, unique_id,producer_table,is_cons ,model,x,y, weights= [0.8,0.1,0.1], treshold=0.7,
                 fossileprice=0.4,jobs=[],table_wind=BaseWind,Sjobs=[],
                 nuclear_price=([0.15 for i in range(6)] + [0.2 for i in range(16)] + [0.15 for i in range(2)]),
                 solar_price=[([-1 for i in range(4+j)]+[0.4 for i in range(18-2*j)]+ [-1 for i in range(2+j)]) for j in range(6)]):
        super().__init__(unique_id, model)
        self.is_consumerr = is_cons
        self.producer_table= producer_table
        self.is_producing=False
        self.is_consuming=False
        self.x = x
        self.y = y
        #inbox
        self.inbox = {}
        self.inboxit ={}


        #consumer attributes
        self.weights = weights
        self.treshold= treshold
        self.jobs =jobs
        self.Sjobs = Sjobs
        self.bSjobs = Sjobs

        #producer attributes
        self.fossile_price= fossileprice
        self.table_wind=table_wind
        self.nuclear_price = nuclear_price
        self.solar_price = solar_price


        #Overall machine
        self.machine = Machine(model=self, states=ProsumerAgent.Astates, initial="Init")
        self.machine.add_transition("Step", "Init", "InitP",
                                     conditions=["is_producer"], after=["run_producer"])
        self.machine.add_transition("Step", "Init", "InitC",
                                     conditions=["is_consumer"], after =["run_consumer"])
        self.machine.add_transition("Step","Init","out")


        #Producer machine
        
        self.machine.add_transition("Step","InitP","prices_sent",conditions=["producing_time"],after=["send_prices"])
        self.machine.add_transition("Step","prices_sent","got_Pvalidation",
                                     conditions=["producing_time","got_Pvalidationf"])
        self.machine.add_transition("Step","got_Pvalidation","outP",conditions=["producing_time"])
        self.machine.add_transition("Step", "outP", "InitC",
                                    conditions=["is_consumer"],after =["run_consumer"])
        self.machine.add_transition("Step","outP","out")

        #Consumer machine
        
        self.machine.add_transition("Step", "InitC", "ask_for_prices", conditions=["consuming_time"],
                                     after=["ask_prices"])
        self.machine.add_transition("Step", "ask_for_prices", "got_prices_tables",
                                     conditions=["consuming_time","got_pricesf"])
        self.machine.add_transition("Step", "got_prices_tables", "sent_purchase",
                                     conditions=["consuming_time"],after=["purchase"])
        self.machine.add_transition("Step", "sent_purchase", "got_Cvalidation",
                                     conditions=["consuming_time","got_Cvalidationf"])
        self.machine.add_transition("Step", "got_Cvalidation", "outC", conditions=["consuming_time"])
        self.machine.add_transition("Step", "outC", "out")

        self.machine.add_transition("Step", "out", "out")



    def setup(self):
        self.inbox[self.model.marketplaceID]=[]
        self.inboxit[self.model.marketplaceID]=0
        #marketplace
        self.market=[]
        self.got_Pvalidation=False
        self.got_Cvalidation=False
        self.got_prices=False

    def read_mails(self):
        if (self.inboxit[self.model.marketplaceID] < len(self.inbox[self.model.marketplaceID])):
            self.atomic_response(self.inbox[self.model.marketplaceID][self.inboxit[self.model.marketplaceID]])
            self.inboxit[self.model.marketplaceID]+=1


    def atomic_response(self,message):
        if(message[0]== "ok_prices"):
            self.got_Pvalidation=True
        if(message[0] == "ok_purchase"):
            self.got_Cvalidation =True
        if(message[0]== "prices"):
            self.market=message[1]
            self.got_prices=True


    def get_id(self):
        return self.unique_id

    @property
    def got_Cvalidationf(self):
        return self.got_Cvalidation

    @property
    def got_pricesf(self):
        if not self.got_prices:
            self.ask_prices()
        else:
            return True

    def transform_market(self):
        self.Umarket=[]
        for i in self.market:
            utilites=[]
            for k in i[1]:
                utilites.append(self.convex_utility(k,ProsumerAgent.SpecialU[i[2]][0],ProsumerAgent.SpecialU[i[2]][1]))
            self.Umarket.append(utilites)
        return self.Umarket

    def convex_utility(self, price, is_green, is_renewable):
        if(price>0):
            return self.weights[0]*price + self.weights[1]*is_green + self.weights[2]*is_renewable
        else:
            return -1


    @property
    def got_Pvalidationf(self):
        return self.got_Pvalidation

    @property
    def producer_phase_finished(self):
        return self.state== "out"
    @property
    def consumer_phase_finished(self):
        return self.machine.get_state() == "out"


    @property
    def producing_time(self):
        return self.is_producing

    @property
    def consuming_time(self):
        return self.is_consuming

    @property
    def is_producer(self):
        for i in self.producer_table:
            if i==1 :
                return True
        return False

    @property
    def is_consumer(self):
        return self.is_consumerr

    def get_out(self):
        self.is_consuming=False
        self.is_producing=False

    def purchase(self):
        purchase=[]
        self.Umarket=self.transform_market()
        optimal_prices =self.optimal_price_rep()
        for k in range(len(self.jobs)):
            purchase.append(self.intelligent_purchase_wt(optimal_prices,self.jobs[k][self.model.day]))
        for k2 in range(len(self.Sjobs)):
            buy =  self.intelligent_purchase_wt(optimal_prices,self.Sjobs[k2][self.model.day])
            if(self.model.day<6):
                self.Sjobs[k2][self.model.day+1][1]+=self.Sjobs[k2][self.model.day][1]-len(buy)
            purchase.append(buy)
        print("purchase",purchase)
        self.model.send(self.unique_id,self.model.marketplaceID,("purchase",purchase))

    def ask_prices(self):
        self.model.send(self.unique_id,self.model.marketplaceID,("ask_prices",None))

    def send_prices(self):
        prices_list =[]
        if(self.producer_table[0]==1):
            prices_list.append(([self.fossile_price for i in range(24)],0))
        if(self.producer_table[1]==1):
            wind_pred =self.model.wind_pred
            prices_wind=[]
            for wp in wind_pred:
                prices_wind.append(self.table_wind[wp])
            prices_list.append((prices_wind,1))
        if(self.producer_table[2]==1):
            prices_list.append((self.nuclear_price, 2))
        if(self.producer_table[3]==1):
            prices_list.append((self.solar_price[self.model.season], 3))
        self.model.send(self.unique_id, self.model.marketplaceID, ("prices", prices_list))


    def run_consumer(self):
        self.is_consuming=True
        self.is_producing=False
    def run_producer(self):
        self.is_consuming =False
        self.is_producing=True
    def step(self):
        self.read_mails()
        self.Step()
        self.Umarket = self.transform_market()

        #if (self.unique_id == 1):
            #for i in self.Umarket:
             #   print("umarket: ", i)
            #print("optimal_prices: ", self.optimal_price_rep())
            #print("day1 buy: ", self.intelligent_purchase_wt(self.optimal_price_rep(),self.jobs[0][0]))
            #print(str(self.unique_id) + ": inbox :" + str(self.inbox) + ":step: " + self.state)
            #print(self.model.hour)
    def intelligent_purchase(self,optimalP,job):
        buy=[]
        j_list=[]
        for i in range(job[1]):
            actmin=math.inf
            jactmin=0
            act=(0,0)
            for j in range(len(optimalP)):
                if(job[0][j]==1 and (j not in j_list)):
                        if(optimalP[j][1]<actmin and optimalP[j][1]>0 ):
                            actmin=optimalP[j][1]
                            act = optimalP[j]
                            jactmin=j
            buy.append((jactmin,act[0]))
            j_list.append(jactmin)
        return buy

    def intelligent_purchase(self,optimalP,job):
        buy=[]
        j_list=[]
        for i in range(job[1]):
            actmin=math.inf
            jactmin=0
            act=(0,0)
            for j in range(len(optimalP)):
                if(job[0][j]==1 and (j not in j_list)):
                        if(optimalP[j][1]<actmin and optimalP[j][1]>0 ):
                            actmin=optimalP[j][1]
                            act = optimalP[j]
                            jactmin=j
            buy.append((jactmin,act[0]))
            j_list.append(jactmin)
        return buy

    def intelligent_purchase(self,optimalP,job):
        buy=[]
        j_list=[]
        for i in range(job[1]):
            actmin=math.inf
            jactmin=0
            act=(0,0)
            for j in range(len(optimalP)):
                if(job[0][j]==1 and (j not in j_list)):
                        if(optimalP[j][1]<actmin and optimalP[j][1]>0 ):
                            actmin=optimalP[j][1]
                            act = optimalP[j]
                            jactmin=j
            buy.append((jactmin,act[0]))
            j_list.append(jactmin)
        return buy

    def intelligent_purchase(self,optimalP,job):
        buy=[]
        j_list=[]
        for i in range(job[1]):
            actmin=math.inf
            jactmin=0
            act=(0,0)
            took = False
            for j in range(len(optimalP)):
                if(job[0][j]==1 and (j not in j_list)):
                        if(optimalP[j][1]<actmin and optimalP[j][1]>0 ):
                            actmin=optimalP[j][1]
                            act = optimalP[j]
                            took = True
                            jactmin=j
            if (took):
                buy.append((jactmin, act[0]))
                j_list.append(jactmin)
        return buy

    def intelligent_purchase_wt(self,optimalP,job):
        buy=[]
        j_list=[]
        for i in range(job[1]):
            actmin=math.inf
            jactmin=0
            act=(0,0)
            took = False
            for j in range(len(optimalP)):
                if(job[0][j]==1 and (j not in j_list)):
                        if(optimalP[j][1]<actmin and  optimalP[j][1]>0 and
                                (optimalP[j][1]<self.treshold or self.model.day==6)):
                            actmin=optimalP[j][1]
                            took=True
                            act = optimalP[j]
                            jactmin=j
            if(took):
                buy.append((jactmin,act[0]))
                j_list.append(jactmin)
        return buy

    def reset_week(self):
        self.Sjobs = self.bSjobs
        pass

    def reset_day(self):
        self.setup()
        self.change_prices()
        self.is_producing = False
        self.is_consuming = False
        self.machine.set_state("Init")
        self.market=[]

    def optimal_price_rep(self):
        optimal_prices=[]
        for i in range(24):
            umin=math.inf
            imin=0
            for j in range(len(self.Umarket)):
                if(self.Umarket[j][i]>0 and self.Umarket[j][i]<umin):
                    umin=self.Umarket[j][i]
                    imin=j
            optimal_prices.append((imin,umin))
        return optimal_prices


