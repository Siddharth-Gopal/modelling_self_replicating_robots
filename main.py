# SRRS

import random
random.seed(1)

class Robot:
    def __init__(self,type,build_qual):
        self.type = type
        self.build_qual = build_qual
        if(self.type == "Replicator"):
            self.tasks = ["Collect","Print","Assemble"]
        if(self.type == "Normal"):
            self.tasks = ["Collect"]
        if(self.type == "Assembler"):
            self.tasks = ["Collect","Assemble"]
        if(self.type == "Printer"):
            self.tasks = ["Collect","Print"]
        self.num_tasks = len(self.tasks)

    def __str__(self):
        return str(self.type)+" "+str(self.build_qual)+" "+str(self.num_tasks)+" "+str(self.tasks)


robot = Robot("Replicator",random.uniform(0, 1))
print(robot)

# sim param

Num_Steps = 100             #; % Number of iterations/time-steps that the simulation goes through.
Initial_NonPr = 300.0       #; % The robot system=s starting quantity of nonprintable components.
Initial_Printable = 100.0   #; % The robot system’s starting quantity of printable components.
Initial_Materials = 50.0    #; % The robot system’s starting quantity of raw printing materials.
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