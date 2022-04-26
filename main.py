import random
import numpy as np

import matplotlib.pyplot as plt
import sys
from matplotlib.patches import Rectangle

timesteps = 70
fig, ax = plt.subplots()
plt.title("SRRS")
plt.xlabel("time")
plt.ylabel("Number of robots")
plt.grid(axis='y')

random.seed()

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

class Sim:
    def __init__(self,t):
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
        self.prev_task = "idle"
        self.id = self.type[0]+str(id)
        self.build_qual = round(build_qual,2)
        self.factory_made = True
        
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
        return str(self.id)+" "+str(self.build_qual)

    def set_curr_task(self,tasktype):
        self.current_task = tasktype
    def set_prev_task(self,tasktype):
        self.prev_task = tasktype
    def set_task_dur(self,task_dur):
        self.tasks_dur = task_dur

    def get_robot_id(self):
        return self.id
    def get_buid_qual(self):
        return self.build_qual
    def get_curr_task(self):
        return self.current_task
    def get_prev_task(self):
        return self.prev_task
    def get_task_dur(self):
        return self.tasks_dur



# print current resources
def printResources():
    print(NonPr,Printable,Materials,Env_Materials)

# task functions

def collecting(robot):
    robot.set_curr_task("collecting")
    robot.set_task_dur(1)

# collecting
def collect(robot):
    global Materials, Env_Materials, Collect_Amount
    if (Env_Materials - Collect_Amount > 0):
        # if robot.current_task == "idle":
        
        Materials = Materials + Collect_Amount
        Env_Materials = Env_Materials - Collect_Amount
        return True
    else:
        return False

# build robot task - assembler and replicator
# assemble task

def assembling(robot,tobuild):
    global rid,nid,aid,pid,Printable,NonPr,Quality_incr_Chance,Quality_incr_Lower, Quality_incr_Upper
    

    robot.set_curr_task("assembling")
    robot.set_task_dur(AssembleCost_Time)

    if(robot.type=="Assembler" or robot.type=="Replicator"):
        if(tobuild == "Replicator"):
            i=0
            
        if(tobuild == "Normal"):
            i=1
            
        if(tobuild == "Assembler"):
            i=2
            
        if(tobuild == "Printer"):
            i=3
            
    if Printable - cost_Pr[i] >= 0 and NonPr - cost_NonPr[i] >= 0:
        # subtract resources
        Printable = Printable - cost_Pr[i]
        NonPr = NonPr - cost_NonPr[i]
        #numbeingbuilt += 1
        return True
    else:
        return False

        

def assemble(builder,tobuild):
    global rid,nid,aid,pid,Printable,NonPr,Quality_incr_Chance,Quality_incr_Lower, Quality_incr_Upper
    
    # if builder.current_task == "idle":
    # builder.set_curr_task("assembling")
    # builder.set_task_dur(AssembleCost_Time)

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

        AssemblerQuality = builder.get_buid_qual()
        # robot's build quality     
        rand = round(random.uniform(0,1),2)
        if rand > round((1.0 - Quality_incr_Chance/100),2):
            RobotQuality = AssemblerQuality + random.uniform(Quality_incr_Lower, Quality_incr_Upper)
        elif rand < Quality_decr_Chance :
            RobotQuality = AssemblerQuality - random.uniform(Quality_decr_Lower, Quality_decr_Upper)
        else :
            RobotQuality = AssemblerQuality
    
        newRobot = Robot(tobuild,RobotQuality,robotid)
        return newRobot
    else:
        return None

# printing
def printing(robot):
    global Print_Efficiency, Print_Amount, Materials, Printable
    if Materials - (Print_Efficiency*Print_Amount) > 0:
        # if robot.current_task == "idle":
        robot.set_curr_task("printing")
        # robot.tasks_dur = PrintCost_Time
        robot.set_task_dur(PrintCost_Time)
        Materials = Materials - (Print_Efficiency*Print_Amount)
        Printable = Printable + (Print_Efficiency*Print_Amount)
    else:
        pass

def main():
    numbeingbuilt = 0
    init_build_qual = random.uniform(0.85, 0.95)
    robot = Robot("Replicator",init_build_qual,rid)

    # commence tasks
    # collecting(robot)
    # printing(robot)
    # newRobot = assemble(robot,"Normal")
    # print(robot)
    # print(newRobot)

    robotlist = [robot]

    listPrintable = [100.0]
    listNonPr = [300.0]
    listMaterials = [50.0]
    listEnv_Materials = [500.0]

    listnumIdle = []
    # total number of bots
    listnumReplicator = []
    listnumNormal = []
    listnumAssembler = []
    listnumPrinter = []
    for i in range(len(robotlist)):
        n_idle = 0
        n_replicator = 0
        n_normal = 0
        n_assembler = 0
        n_printer = 0
        
        if robotlist[i].current_task=="idle":
            n_idle = n_idle+1
        listnumIdle.append(n_idle)
        
        if(robotlist[i].type== "Replicator"):
            n_replicator += 1;
        listnumReplicator.append(n_replicator)

        if(robotlist[i].type== "Normal"):
            n_normal += 1;
        listnumNormal.append(n_normal)
        
        if(robotlist[i].type== "Assembler"):
            n_assembler += 1;
        listnumAssembler.append(n_assembler)
        
        if(robotlist[i].type== "Printer"):
            n_printer += 1;
        listnumPrinter.append(n_printer)
        

    # number of bots working
    listnumCollecting = []
    listnumPrinting = []
    listnumAssembling = []


    check = 0
    # use lists
    tcoordslist = []
    rcoordslist = []
    for t in range(0,timesteps):
        numbeingbuilt = 0
        for i in range(len(robotlist)):
            #print(t,len(robotlist),robotlist[i].id,robotlist[i].current_task,robotlist[i].tasks_dur)
            # if(robotlist[i].current_task=="idle"):
            if(robotlist[i].current_task=="idle"):
                if(robotlist[i].type == "Replicator"):
                    canAssemble = assembling(robotlist[i],"Normal")
                elif(robotlist[i].type == "Normal"):
                    canCollect = collect(robotlist[i])
                    if canCollect:
                        collecting(robotlist[i])

            else:
                if(robotlist[i].tasks_dur - 1 != 0):
                # if(robotlist[i].current_task != "idle"):
                    robotlist[i].set_task_dur(robotlist[i].tasks_dur - 1)
                elif(robotlist[i].tasks_dur - 1 == 0 and robotlist[i].type == "Replicator"):
                    canAssemble = assembling(robotlist[i],"Normal")
                    # print(canAssemble)
                    if(robotlist[i].get_curr_task()=="assembling" and canAssemble):
                        newbot = assemble(robotlist[i],"Normal")
                        if newbot:
                            if(newbot.type == "Normal"):
                                canCollect = collect(newbot)
                                if canCollect:
                                    collecting(newbot)
                            robotlist.append(newbot)
                        robotlist[i].set_prev_task(robotlist[i].current_task)

                elif(robotlist[i].tasks_dur == 0 and robotlist[i].type == "Normal"):
                    canCollect = collect(robotlist[i])
                    if(canCollect):
                        collecting(robotlist[i])
                    else:
                        robotlist[i].set_curr_task=="idle"

                    # else make print tasks? canPrint()?

                else:
                    # print("HAHAHAH")
                    robotlist[i].set_task_dur(0)
                    if(robotlist[i].get_curr_task()=="assembling"):
                        newbot = assemble(robotlist[i],"Normal")
                        if newbot:
                            robotlist.append(newbot)

                    robotlist[i].set_prev_task(robotlist[i].current_task)

                    # robotlist[i].set_tasks_dur(0)
                    robotlist[i].set_curr_task("idle")

            # if(robotlist[i].current_task == "assembling"):
            #   numbeingbuilt = numbeingbuilt+1



        #ax.add_patch(Rectangle((t-0.4, 0), 0.8, numbeingbuilt)) # replace 1 with numbeingbuilt
        

        print("="*20)


        c_flag = 0
        p_flag = 0
        a_flag = 0
        i_flag = 0
        for i in robotlist:
            if i.current_task=="collecting":
                c_flag+=1
            if i.current_task=="printing":
                p_flag+=1
            if i.current_task=="assembling":
                a_flag+=1
            if i.current_task=="idle":
                i_flag+=1

        listnumCollecting.append(c_flag)
        listnumPrinting.append(p_flag)
        listnumAssembling.append(a_flag)
    
        # print(t,":",len(robotlist),"\t",[NonPr,Printable,Materials,Env_Materials])
        
        print("Time\t\t",t)
        print("#Robots\t\t",len(robotlist))
        print("Materials\t",[NonPr,Printable,Materials,Env_Materials])
        print("#Collect:\t",c_flag)
        print("#Idle:\t\t",i_flag)

        ids=[]
        for j in robotlist:
            # print(t,len(robotlist),j.id,j.current_task,j.tasks_dur)
            ids.append(j.id)
        tcoordslist.append(t)
        rcoordslist.append(len(robotlist)) 

        # plt.scatter(t,len(robotlist),marker=".", c="black")
        # plt.scatter(t,listnumCollecting[t],marker=".", c="red")
        # plt.scatter(t,listnumPrinting[t],marker="x", c="green")
        # plt.scatter(t,listnumAssembling[t],marker="+", c="blue")
    
    plt.plot(tcoordslist,rcoordslist,color = "blue",label = "numcurrent")
    plt.bar(tcoordslist,listnumAssembling,width=0.5,label = "numbeingbuilt")
    curr_built = [x + y for (x, y) in zip(rcoordslist, listnumAssembling)] 
    plt.scatter(tcoordslist,curr_built,marker=".",color="black",label = "numcurrent+numbeingbuilt")
    plt.legend()
    #plt.show()

        

if __name__ == "__main__":
    main()











