#!/usr/bin/env python
# coding: utf-8

# In[3]:


import bs4
import csv
import requests
import numpy as np
import time


# ## Data Collection

# In[8]:


# Web-Scraping relevant data
data = []

# Looping over multiple pages of players
for page in range(1, 26):

    # soupifying data to be parsed
    response = requests.get('https://www.futbin.com/players?page='+str(page)+'&version=gold_rare')
    soup = bs4.BeautifulSoup(response.text,'html.parser')
    
    # two types of players, player_tr_1 and player_tr_2 (not sure why)
    p = soup.findAll('tr','player_tr_1') + soup.findAll('tr','player_tr_2')
    
    # extracting necessary information
    for p in p :
        tds = p.findAll('td')
        name = tds[0].text.strip()
        rating = tds[1].text.strip()
        position = tds[2].text.strip()
        clubs = p.find('span', 'players_club_nation').findAll('a')
        # club = clubs[0]['data-original-title'].strip()
        nation = clubs[1]['data-original-title'].strip()
        league = clubs[2]['data-original-title'].strip()
        data.append([name, int(rating), position, nation, league])   
    time.sleep(3)


# In[223]:


dblen = len(data)
dblen


# In[10]:


# Adjusting player positions to 4-4-2 formation
for i in range(0, dblen):
    
    if data[i][2] == "LW" or data[i][2] == "LF" :
        data[i][2] = "LM"
    
    if data[i][2] == "RW" or data[i][2] == "RF" :
        data[i][2] = "RM"
    
    if data[i][2] == "CAM" or data[i][2] == "CDM" :
        data[i][2] = "CM"
        
    if data[i][2] == "CF" :
        data[i][2] = "ST"
    
    if data[i][2] == "LWB" :
        data[i][2] = "LB"

    if data[i][2] == "RWB" :
        data[i][2] = "RB"
    


# ## Data Parsing

# In[11]:


# Finding Timo Werner, Ilkay Gündogan, and Matts Hummels in Dataset
WernerID = 0
GundoganID = 0
HummelsID = 0

for i in range(0, dblen) :
    if data[i][0] == 'Timo Werner' :
        WernerID = i
    if data[i][0] == 'Ilkay Gündogan' :
        GundoganID = i
    if data[i][0] == 'Mats Hummels' :
        HummelsID = i
        
print(WernerID, GundoganID, HummelsID)


# In[12]:


# Create positions dependency table (if players can actually share a link)
poscoef = np.zeros((dblen, dblen), dtype = np.int)

for i in range(0, dblen) :
        for j in range(0, dblen) :

                if data[i][2] == 'RM' :
                    if data[j][2] == 'RB':
                        poscoef[i][j] = 1
                    
                if data[i][2] == 'RM' :
                    if (j == WernerID or j == GundoganID) :
                        poscoef[i][j] = 1
                
                if data[i][2] == 'RB' :
                    if data[j][2] == 'RM' :
                        poscoef[i][j] = 1
                
                if data[i][2] == 'RB' :
                    if j == HummelsID :
                        poscoef[i][j] = 1

                if data[i][2] == 'ST' and i != WernerID :
                    if (data[j][2] == 'CM' or data[j][2] == 'LM') :
                        poscoef[i][j] = 1
                
                if data[i][2] == 'ST' and i != WernerID :
                    if j == WernerID :
                        poscoef[i][j] = 1

                if data[i][2] == 'CM' and i != GundoganID :
                    if (data[j][2] == 'ST' or data[j][2] == 'LM' or data[j][2] == 'CB') and not (j in [WernerID, HummelsID]) :
                        poscoef[i][j] = 1
                
                if data[i][2] == 'CM' and i != GundoganID :
                    if j == GundoganID :
                        poscoef[i][j] = 1

                if data[i][2] == 'LM' :
                    if (data[j][2] == 'CM' or data[j][2] == 'ST' or data[j][2] == 'LB') and not (j in [WernerID, GundoganID]):
                        poscoef[i][j] = 1

                if data[i][2] == 'LB' :
                    if (data[j][2] == 'CB' or data[j][2] == 'LM') and j != HummelsID:
                        poscoef[i][j] = 1
                  

                if data[i][2] == 'CB' and i != HummelsID : 
                    if (data[j][2] == 'CM' or data[j][2] == 'LB' or data[j][2] == 'GK') and j != GundoganID:
                        poscoef[i][j] = 1
                        
                if data[i][2] == 'CB' and i != HummelsID :
                    if j == HummelsID :
                        poscoef[i][j] = 1

                if data[i][2] == 'GK' :
                    if data[j][2] == 'CB' : 
                        poscoef[i][j] = 1
                        
                if i == WernerID :
                    if (data[j][2] == 'RM' or data[j][2] == 'ST') and not (j in [WernerID, GundoganID]) :
                        poscoef[i][j] = 1
                
                if i == GundoganID :
                    if (data[j][2] == 'CM' or data[j][2] == 'RM') :
                        poscoef[i][j] = 1
                
                if i == HummelsID :
                    if (data[j][2] == 'CB' or data[j][2] == 'GK' or data[j][2] == 'RB') :
                        poscoef[i][j] = 1
                        
                    

poscoef


# In[13]:


# Creating chemistry dependency table (chemistry links)
chemcoef = -1 * np.ones( (dblen, dblen), dtype=np.int)

for i in range(dblen) :
    for j in range(dblen) :
        
        if data[i][3] == data[j][3] :
            chemcoef[i][j] += 1
        if data[i][4] == data[j][4] :
            chemcoef[i][j] += 1
chemcoef


# In[14]:


chempos = chemcoef*poscoef
chempos


# In[49]:


ST = [0] * dblen
LM = [0] * dblen
CM = [0] * dblen
RM = [0] * dblen
LB = [0] * dblen
CB = [0] * dblen
RB = [0] * dblen
GK = [0] * dblen

def pos_constraint_assign(i) :
    pos = data[i][2]
    cons = globals()[pos]
    cons[i] = 1
    return ()

for i in range(dblen) :
    pos_constraint_assign(i)


# In[18]:


data[6]


# In[19]:


# Coefficients for objective function
objcoef = [0] * 750
for i in range(0, dblen) :
    objcoef[i] = data[i][1]


# ## Model Implementation

# In[196]:


import pyomo.environ as pe
import pyomo.opt as po
# (be sure to download all the relevant dependencies for the solver of choice, 
# they can be found on the Mindtpy 2018 paper in this instance with some debugging from stackoverflow)
# due to some errors with compatibility on Windows, I depreciated ipopt to 3.11 as opposed to the most recent 3.13
# I am unsure how this project will run with ipopt 3.13, as several depreciations have since been made.
# In particular, look out for the global variable definition conversion when defining the chemistry constraints, 
# tutorials using Mindtpy.ipopt 3.11 would define variables in this way, but I did not find any that did it with
# ipopt.3.13 - they do it in another way using list iteration. (to be fair global variable conversion is very janky
# and is bad coding practices, but at this point it works so no complaints from me)
# this was a very difficult and annoying to figure out :)
# Also note that this project was created on a jupyter notebook - running it on a standard Python application led to 
# strange interactions. I believe this to be due to the fact that Pyomo was created primarily for notebook functionality
# be sure to only run each cell once, or else Pyomo gets confused as information is overwritten. If accidently ran more 
# than once, restart from the line below onwards.


# In[202]:


model = pe.ConcreteModel()


# In[203]:


model.N = pe.RangeSet(1,dblen)


# In[204]:


solver = po.SolverFactory('ipopt')


# In[205]:


# Creating Dictionaries for the Pyomo Interpreter

obj_coef_d = {}
ST_cons_d = {}
RM_cons_d = {}
CM_cons_d = {}
LM_cons_d = {}
RB_cons_d = {}
CB_cons_d = {}
LB_cons_d = {}
GK_cons_d = {}
Gundogan_d = {}
Hummels_d = {}
Werner_d = {}

for i in range(1, dblen + 1):
    # Objective Coefficients
    obj_coef_d[i] = objcoef[i - 1]
    
    # Position Constraints Coefficients
    ST_cons_d[i] = ST[i - 1]
    RM_cons_d[i] = RM[i - 1]
    CM_cons_d[i] = CM[i - 1]
    LM_cons_d[i] = LM[i - 1]
    LB_cons_d[i] = LB[i - 1]
    RB_cons_d[i] = RB[i - 1]
    CB_cons_d[i] = CB[i - 1]
    GK_cons_d[i] = GK[i - 1]
    
    # Including Werner, Hummels, Gundogan Coefficients
    if i == (WernerID + 1) :
        Werner_d[i] = 1
    else :
        Werner_d[i] = 0
    if i == (GundoganID + 1) :
        Gundogan_d[i] = 1
    else :
        Gundogan_d[i] = 0
    if i == (HummelsID + 1) :
        Hummels_d[i] = 1
    else :
        Hummels_d[i] = 0
    


# In[206]:


# Initializing Parameters

model.obj_c = pe.Param(model.N, initialize = obj_coef_d)

model.ST_c = pe.Param(model.N, initialize = ST_cons_d)
model.GK_c = pe.Param(model.N, initialize = GK_cons_d)
model.LM_c = pe.Param(model.N, initialize = LM_cons_d)
model.CM_c = pe.Param(model.N, initialize = CM_cons_d)
model.RM_c = pe.Param(model.N, initialize = RM_cons_d)
model.CB_c = pe.Param(model.N, initialize = CB_cons_d)
model.LB_c = pe.Param(model.N, initialize = LB_cons_d)
model.RB_c = pe.Param(model.N, initialize = RB_cons_d)

model.Gundogan_c = pe.Param(model.N, initialize = Gundogan_d)
model.Hummels_c = pe.Param(model.N, initialize = Hummels_d)
model.Werner_c = pe.Param(model.N, initialize = Werner_d)


# In[207]:


model.zero = pe.Param(initialize = 0)
model.twoST = pe.Param(initialize = 2)
model.twoCM = pe.Param(initialize = 2)
model.twoCB = pe.Param(initialize = 2)
model.oneRM = pe.Param(initialize = 1)
model.oneLM = pe.Param(initialize = 1)
model.oneRB = pe.Param(initialize = 1)
model.oneLB = pe.Param(initialize = 1)
model.oneGK = pe.Param(initialize = 1)

model.oneWerner = pe.Param(initialize = 1)
model.oneGundogan = pe.Param(initialize = 1)
model.oneHummels = pe.Param(initialize = 1)


# In[208]:


# Creating the actual variables & the objective function
model.X = pe.Var(model.N, domain=pe.Binary)


# In[209]:


obj_expr = sum(model.obj_c[i] * model.X[i] for i in model.N)
model.obj = pe.Objective(sense=pe.maximize, expr = obj_expr)


# In[210]:


ST_cons_lhs = sum(model.ST_c[i] * model.X[i] for i in model.N)
model.ST_cons = pe.Constraint(expr = (ST_cons_lhs == model.twoST))

CM_cons_lhs = sum(model.CM_c[i] * model.X[i] for i in model.N)
model.CM_cons = pe.Constraint(expr = (CM_cons_lhs == model.twoCM))

CB_cons_lhs = sum(model.CB_c[i] * model.X[i] for i in model.N)
model.CB_cons = pe.Constraint(expr = (CB_cons_lhs == model.twoCM))

RM_cons_lhs = sum(model.RM_c[i] * model.X[i] for i in model.N)
model.RM_cons = pe.Constraint(expr = (RM_cons_lhs == model.oneRM))

LM_cons_lhs = sum(model.LM_c[i] * model.X[i] for i in model.N)
model.LM_cons = pe.Constraint(expr = (LM_cons_lhs == model.oneLM))

LB_cons_lhs = sum(model.LB_c[i] * model.X[i] for i in model.N)
model.LB_cons = pe.Constraint(expr = (LB_cons_lhs == model.oneLB))

RB_cons_lhs = sum(model.RB_c[i] * model.X[i] for i in model.N)
model.RB_cons = pe.Constraint(expr = (RB_cons_lhs == model.oneRB))

GK_cons_lhs = sum(model.GK_c[i] * model.X[i] for i in model.N)
model.GK_cons = pe.Constraint(expr = (GK_cons_lhs == model.oneGK))

Werner_cons_lhs = sum(model.Werner_c[i] * model.X[i] for i in model.N)
model.Werner_cons = pe.Constraint(expr = (Werner_cons_lhs == model.oneWerner))

Gundogan_cons_lhs = sum(model.Gundogan_c[i] * model.X[i] for i in model.N)
model.Gundogan_cons = pe.Constraint(expr = (Gundogan_cons_lhs == model.oneGundogan))

Hummels_cons_lhs = sum(model.Hummels_c[i] * model.X[i] for i in model.N)
model.Hummels_cons = pe.Constraint(expr = (Hummels_cons_lhs == model.oneGundogan))


# In[194]:


# Adding the chemistry constraints 

for i in range(1, dblen + 1):
    setattr(model, "cons_" + str(i), 
            pe.Constraint(expr =  model.X[i] * sum(chempos[i - 1][j - 1] * model.X[j] for j in model.N) 
                          == pe.Param(initialize = 0) ))


# In[211]:


result = solver.solve(model)


# In[225]:


print('Chosen Players:')
for i in model.N:
        if(pe.value(model.X[i])> 0.99):
            print(data[i - 1][0])
print()
print('Objective Value:', pe.value(model.obj))

