import random
import numpy as np

random.seed(1)

# global variables
rid = 1
nid = 0
aid = 0
pid = 0

# sim param
Num_Steps = 100             #; % Number of iterations/time-steps that the simulation goes through.
NonPr = 300.0               #; % The robot system=s starting quantity of nonprintable components.
Printable = 100.0           #; % The robot system’s starting quantity of printable components.
Materials = 50.0            #; % The robot system’s starting quantity of raw printing materials.
Env_Materials = 500.0       #; % The environment’s quantity of collectable raw printing materials.
BaseCost_NonPr = 1          #; % Base robot cost of nonprintable components.
PrintCost_NonPr = 1         #; % Print capability cost of nonprintable components.
AssembleCost_NonPr = 1      #; % Assemble capability cost of nonprintable components.
BaseCost_Pr = 2             #; % Base robot cost of printable components.
PrintCost_Pr = 2            #; % Print capability cost of printable components.
AssembleCost_Pr = 2         #; % Assemble capability cost of printable components.
BaseCost_Time = 2           #; % Base robot cost of build time (in time-steps).
PrintCost_Time = 2          #; % Print capability cost of build time (in time-steps).
AssembleCost_Time = 2       #; % Assemble capability cost of build time (in time-steps).
Print_Efficiency = 1.0      #; % Factor that scales raw printing materials to printable components.
Print_Amount = 1.0          #; % Amount of raw materials converted per print task.
Collect_Amount = 1.0        #; % Raw printing materials per collecting robot per timestep.
QualityThreshold = 0.5      #; % Robots with a quality below this are non-functional.
Quality_incr_Chance = 5.0   #; % Chance that a new robot’s build quality will increase.
Quality_incr_Lower = 0.01   #; % Lower bound for quality increase amount.
Quality_incr_Upper = 0.05   #; % Upper bound for quality increase amount.
Quality_decr_Chance = 50.0  #; % Chance that a new robot s build quality will decrease.
Quality_decr_Lower = 0.01   #; % Lower bound for quality decrease amount.
Quality_decr_Upper = 0.25   #; % Upper bound for quality decrease amount.
RiskAmount_Collect = 1.0    #; % Risk chance for the collect task type.
RiskAmount_Assemble = 0.1   #; % Risk chance for the assemble task type.
RiskAmount_Print = 0.1      #; % Risk chance for the print task type.
RiskQuality_Modifier = 5.0  #; % Multiplier for impact of quality defects on risk amount.
RiskFactory_Modifier = 0.1  #; % Multiplier for impact of factory-made robots on risk amount

# [replicator,normal,assembler,printer]
cost_Pr = [6,2,4,4]         #; % Total cost printable
cost_NonPr = [3,1,2,2]      #; % Total cost nonprintable

class Simstep:
    def __init__(self):
        self.t = 0
        # materials in a time step
        self.Printable = 0
        self.NonPr = 0
        self.Materials = 0
        self.Env_Materials = 0
        self.numIdle = 0

        # total number of bots
        self.numReplicator = 0
        self.numNormal = 0
        self.numAssembler = 0
        self.numPrinter = 0

        # number of bots working
        self.numCollecting = 0
        self.numPrinting = 0
        self.numAssembling = 0

t = Simstep()

# basically a list of robots in a config (currently named SRRS)
# class SRRS:
#   def __init__(self):
#       self.robots = dict()
#   def insert(self,robot):
#       self.robots[robot.get_robot_id()] = robot

# robot object
class Robot:
    def __init__(self,type,build_qual,id):
        self.type = type
        self.current_task = "idle"
        self.id = self.type[0]+str(id)
        self.build_qual = round(build_qual,2)
        
        if(self.type == "Replicator"):
            self.tasks = ["Collect","Print","Assemble"]
        if(self.type == "Normal"):
            self.tasks = ["Collect"]
        if(self.type == "Assembler"):
            self.tasks = ["Collect","Assemble"]
        if(self.type == "Printer"):
            self.tasks = ["Collect","Print"]
        self.num_tasks = len(self.tasks)

        if(self.current_task == "idle"):
            self.tasks_dur = 0
        # if(self.current_task == "collecting"):
        #   self.tasks_dur = 1
        # if(self.current_task == "assembling"):
        #   self.tasks_dur = 2
        # if(self.current_task == "printing"):
        #   self.tasks_dur = 2

    def __str__(self):
        return str(self.type)+" "+str(self.build_qual)+" "+str(self.num_tasks)+" "+str(self.id)

    def set_task(self,tasktype):
        self.current_task = tasktype

    def get_robot_id(self):
        return self.id

# print current resources
def printResources():
    print(NonPr,Printable,Materials,Env_Materials)

# task functions
# collecting
def collecting(robot):
    global Materials, Env_Materials, Collect_Amount
    if robot.current_task == "idle":
        robot.set_task = "collecting"
        robot.tasks_dur = 1
    Materials = Materials + Collect_Amount
    Env_Materials = Env_Materials - Collect_Amount

# build robot task - assembler and replicator
# assemble task
def assemble(builder,tobuild):
    global rid,nid,aid,pid,Printable,NonPr
    if builder.current_task == "idle":
        builder.set_task = "assembling"
        builder.tasks_dur = AssembleCost_Time

    if(builder.type=="Assembler" or builder.type=="Replicator"):
        if(tobuild == "Replicator"):
            i=0
            rid = rid+1
            robotid = rid
        if(tobuild == "Normal"):
            i=1
            nid = nid+1
            robotid = nid
        if(tobuild == "Assembler"):
            i=2
            aid = aid+1
            robotid = aid
        if(tobuild == "Printer"):
            i=3
            pid = pid+1
            robotid = pid

        # subtract resources
        Printable = Printable - cost_Pr[i]
        NonPr = NonPr - cost_NonPr[i]

        # new robot
        newRobot = Robot(tobuild,random.uniform(0, 1),robotid)
        return newRobot
    else:
        return None

# printing
def printing(robot):
    global Print_Efficiency, Print_Amount, Materials, Printable
    if robot.current_task == "idle":
        robot.set_task = "printing"
        robot.tasks_dur = PrintCost_Time
    Materials = Materials - (Print_Efficiency*Print_Amount)
    Printable = Printable + (Print_Efficiency*Print_Amount)

# main()

init_build_qual = random.uniform(0, 1)
robot = Robot("Replicator",init_build_qual,rid)

# commence tasks
printResources()
collecting(robot)
printing(robot)
printResources()