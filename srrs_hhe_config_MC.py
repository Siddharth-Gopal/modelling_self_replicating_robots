### Libraries
# pandas             1.4.2
# matplotlib         3.5.1
# numpy              1.22.3

### Installation
# pip install <library name>==<version>
# 	or
# pip3 install <library name>==<version>

### To run:
# $ python3 <filename>.py

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from matplotlib.patches import Rectangle

timesteps = 90
fig, ax = plt.subplots(3, 2)
# plt.title("SRRS - DHO Config.")
# plt.xlabel("Time")
# plt.ylabel("Number of robots")
# plt.grid(axis='y')

# set random number generator
random.seed()

# global variables
rid = 0
nid = 0
aid = 1
pid = 1
decimalPlaces = 3

# simulation parameters
Num_Steps = 100  # ; % Number of iterations/time-steps that the simulation goes through.
NonPr = 300.0  # ; % The robot system=s starting quantity of nonprintable components.
Printable = 100.0  # ; % The robot system’s starting quantity of printable components.
Materials = 50.0  # ; % The robot system’s starting quantity of raw printing materials.
Env_Materials = 500.0  # ; % The environment’s quantity of collectable raw printing materials.
BaseCost_NonPr = 1  # ; % Base robot cost of nonprintable components.
PrintCost_NonPr = 1  # ; % Print capability cost of nonprintable components.
AssembleCost_NonPr = 1  # ; % Assemble capability cost of nonprintable components.
BaseCost_Pr = 2  # ; % Base robot cost of printable components.
PrintCost_Pr = 2  # ; % Print capability cost of printable components.
AssembleCost_Pr = 2  # ; % Assemble capability cost of printable components.
BaseCost_Time = 2  # ; % Base robot cost of build time (in time-steps).
PrintCost_Time = 2  # ; % Print capability cost of build time (in time-steps).
AssembleCost_Time = 2  # ; % Assemble capability cost of build time (in time-steps).
Print_Efficiency = 1.0  # ; % Factor that scales raw printing materials to printable components.
Print_Amount = 1.0  # ; % Amount of raw materials converted per print task.
Collect_Amount = 1.0  # ; % Raw printing materials per collecting robot per timestep.
QualityThreshold = 0.5  # ; % Robots with a quality below this are non-functional.
Quality_incr_Chance = 5.0  # ; % Chance that a new robot’s build quality will increase.
Quality_incr_Lower = 0.01  # ; % Lower bound for quality increase amount.
Quality_incr_Upper = 0.05  # ; % Upper bound for quality increase amount.
Quality_decr_Chance = 50.0  # ; % Chance that a new robot s build quality will decrease.
Quality_decr_Lower = 0.01  # ; % Lower bound for quality decrease amount.
Quality_decr_Upper = 0.25  # ; % Upper bound for quality decrease amount.
RiskAmount_Collect = 1.0  # ; % Risk chance for the collect task type.
RiskAmount_Assemble = 0.1  # ; % Risk chance for the assemble task type.
RiskAmount_Print = 0.1  # ; % Risk chance for the print task type.
RiskQuality_Modifier = 5.0  # ; % Multiplier for impact of quality defects on risk amount.
RiskFactory_Modifier = 0.1  # ; % Multiplier for impact of factory-made robots on risk amount

# [replicator,normal,assembler,printer]
cost_Pr = [6, 2, 4, 4]  # ; % Total cost printable
cost_NonPr = [3, 1, 2, 2]  # ; % Total cost nonprintable

timecost_base = 2  # ; % time cost basic
timecost_print = 2  # ; % time cost print capability
timecost_assemble = 2  # ; % time cost assemble capability

timecost_normal = timecost_base
timecost_replicator = timecost_base + timecost_assemble + timecost_print
timecost_printer = timecost_base + timecost_print
timecost_assembler = timecost_base + timecost_assemble


# robot object
class Robot:
    def __init__(self, type, build_qual, id):
        self.type = type
        self.current_task = "idle"
        self.prev_task = "idle"
        self.id = self.type[0] + str(id)
        self.build_qual = round(build_qual, decimalPlaces)
        self.factory_made = True
        self.tasks_dur = 0
        self.taskindex = 0
        self.previouslyBuilt = ""

        if (self.type == "Replicator"):
            self.tasks = ["Assemble", "Print", "Collect"]
            self.beingbuiltlist = []
        if (self.type == "Normal"):
            self.tasks = ["Collect"]
        if (self.type == "Assembler"):
            self.tasks = ["Assemble", "Collect"]
            self.beingbuiltlist = []
        if (self.type == "Printer"):
            self.tasks = ["Print", "Collect"]
        self.num_tasks = len(self.tasks)

    def __str__(self):
        return str(self.id) + " " + str(self.current_task)

    def set_curr_task(self, tasktype):
        self.current_task = tasktype
        if (self.current_task == "idle"):
            self.tasks_dur = 0
        if (self.current_task == "collecting"):
            self.tasks_dur = 1
        if (self.current_task == "assembling"):
            self.tasks_dur = 2
        if (self.current_task == "printing"):
            self.tasks_dur = 2

    # methods of robot object
    def set_prev_task(self, tasktype):
        self.prev_task = tasktype

    def set_task_dur(self, task_dur):
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

    def set_previously_built(self, val):
        self.previouslyBuilt = val

    def get_previously_built(self):
        return self.previouslyBuilt


# print current resources
def printResources():
    print(NonPr, Printable, Materials, Env_Materials)


# Checks if resources are available to collect from environment
def collectCheck():
    global Materials, Env_Materials, Collect_Amount
    if (Env_Materials - Collect_Amount >= 0):
        # Materials = Materials + Collect_Amount
        # Env_Materials = Env_Materials - Collect_Amount
        return True
    else:
        return False


# Reduces resources from the environment(Happens when the task in ongoing) and updates robot task(This happens when the task is finished)
def collecting(robot):
    global Materials, Env_Materials, Collect_Amount
    robot.set_prev_task(robot.get_curr_task())
    robot.set_curr_task("collecting")
    robot.set_task_dur(1)
    Materials = Materials + Collect_Amount
    Env_Materials = Env_Materials - Collect_Amount


# Checks if resources are available to assemble from printable and non-printable
def assembleCheck(tobuild):
    # global rid,nid,aid,pid,Printable,NonPr,Quality_incr_Chance,Quality_incr_Lower, Quality_incr_Upper

    if (tobuild == "Replicator"):
        i = 0
    # rid = rid+1
    # robotid = rid
    if (tobuild == "Normal"):
        i = 1
    # nid = nid+1
    # robotid = nid
    if (tobuild == "Assembler"):
        i = 2
    # aid = aid+1
    # robotid = aid
    if (tobuild == "Printer"):
        i = 3
    # pid = pid+1
    # robotid = pid

    if Printable - cost_Pr[i] >= 0 and NonPr - cost_NonPr[i] >= 0:
        return True
    else:
        return False


# Assigns the robot assembling task, reduce resources from printable and non-printable and add to assemble queue
def assembling(robot, tobuild):
    global rid, nid, aid, pid, Printable, NonPr, Quality_incr_Chance, Quality_incr_Lower, Quality_incr_Upper

    if (tobuild == "Replicator"):
        i = 0
        taskDur = timecost_replicator
    if (tobuild == "Normal"):
        i = 1
        taskDur = timecost_normal
    if (tobuild == "Assembler"):
        i = 2
        taskDur = timecost_assembler
    if (tobuild == "Printer"):
        i = 3
        taskDur = timecost_printer

    robot.set_prev_task(robot.get_curr_task())
    robot.set_curr_task("assembling")
    robot.set_task_dur(taskDur)

    if (robot.type == "Assembler" or robot.type == "Replicator"):
        if (tobuild == "Replicator"):
            i = 0
            rid = rid + 1
            robotid = rid
        if (tobuild == "Normal"):
            i = 1
            nid = nid + 1
            robotid = nid
        if (tobuild == "Assembler"):
            i = 2
            aid = aid + 1
            robotid = aid
        if (tobuild == "Printer"):
            i = 3
            pid = pid + 1
            robotid = pid

        # subtract resources
        Printable = Printable - cost_Pr[i]
        NonPr = NonPr - cost_NonPr[i]

        robot.beingbuiltlist.append(tobuild[0] + str(robotid))
        robot.set_previously_built(tobuild)
        # print(robot.get_previously_built())
        return True
    else:
        robot.set_prev_task(robot.get_curr_task())
        robot.set_curr_task("idle")
        robot.set_task_dur(0)
        return False


# Assigns a build quality and creates new robot object and returns it
def assemble(builder, tobuild):
    global rid, nid, aid, pid, Printable, NonPr, Quality_incr_Chance, Quality_incr_Lower, Quality_incr_Upper

    if (builder.type == "Assembler" or builder.type == "Replicator"):
        if (tobuild == "Replicator"):
            i = 0

        if (tobuild == "Normal"):
            i = 1

        if (tobuild == "Assembler"):
            i = 2

        if (tobuild == "Printer"):
            i = 3

        AssemblerQuality = builder.get_buid_qual()
        # robot's build quality
        rand = round(random.uniform(0, 1), decimalPlaces)

        if rand > round((1.0 - Quality_incr_Chance / 100), decimalPlaces):
            RobotQuality = AssemblerQuality + random.uniform(Quality_incr_Lower, Quality_incr_Upper)
        elif rand < Quality_decr_Chance:
            RobotQuality = AssemblerQuality - random.uniform(Quality_decr_Lower, Quality_decr_Upper)
        else:
            RobotQuality = AssemblerQuality
        # print(builder.beingbuiltlist)
        newRobot = Robot(tobuild, RobotQuality, builder.beingbuiltlist.pop(0)[1:])
        # print(builder,builder.get_previously_built())
        # print("new",tobuild,newRobot)
        return newRobot
    else:
        return None


def printCheck(robot):
    if (robot.type == "Replicator" or robot.type == "Printer"):
        global Print_Efficiency, Print_Amount, Materials, Printable
        if Materials - (Print_Efficiency * Print_Amount) > 0:
            return True
        else:
            return False
    else:
        return False


def printing(robot):
    global Print_Efficiency, Print_Amount, Materials, Printable
    robot.set_prev_task(robot.get_curr_task())
    robot.set_curr_task("printing")
    robot.set_task_dur(PrintCost_Time)
    Materials = Materials - (Print_Efficiency * Print_Amount)
    Printable = Printable + (Print_Efficiency * Print_Amount)


def main():
    mcdf = pd.DataFrame(columns=["Time", "NonPr", "Printable", "Materials", "Env_Materials",
                                 "#Replicator", "#Normal", "#Assembler", "#Printer",
                                 "#Assembling", "#Printing", "#Collecting", "#Idle",
                                 "#In", "#Out",
                                 "Average Build Quality in-service", "Average Build Quality of System",
                                 "#WasteReplicator", "#WasteNormal", "#WasteAssembler", "#WastePrinter"])
    for mc in range(Num_Steps):
        global NonPr, Printable, Materials, Env_Materials
        NonPr = 300.0  # ; % The robot system=s starting quantity of nonprintable components.
        Printable = 100.0  # ; % The robot system’s starting quantity of printable components.
        Materials = 50.0  # ; % The robot system’s starting quantity of raw printing materials.
        Env_Materials = 500.0  # ; % The environment’s quantity of collectable raw printing materials.

        # Setting build quality according
        build_qual_range = [0.85, 0.95]
        init_build_qual = random.uniform(build_qual_range[0], build_qual_range[1])

        df = pd.DataFrame(columns=["Time", "NonPr", "Printable", "Materials", "Env_Materials",
                                   "#Replicator", "#Normal", "#Assembler", "#Printer",
                                   "#Assembling", "#Printing", "#Collecting", "#Idle",
                                   "#In", "#Out",
                                   "Average Build Quality in-service", "Average Build Quality of System",
                                   "#WasteReplicator", "#WasteNormal", "#WasteAssembler", "#WastePrinter"])

        # Creating data frame to store data of each time step
        # df = pd.DataFrame(columns = ["Time","NonPr","Printable","Materials","Env_Materials","#Replicator","#Normal","#Assembler","#Printer","#Assemble","#Print","#Collect","#Idle","#In","#Out","Average Build Quality"])

        # Building first robot(replicator)
        robot1 = Robot("Printer", init_build_qual, pid)
        robot2 = Robot("Assembler", init_build_qual, aid)

        # Lists to track the number of robots being built
        totlist = [robot1, robot2]
        robotlist = [robot1, robot2]
        useless = []

        # To calculate number of bots of each type on each time step
        listnumCollecting = []
        listnumPrinting = []
        listnumAssembling = []

        # Lists used for visualization
        tcoordslist = []
        rcoordslist = []
        wastecoordslist = []
        t_build_quality_list = []

        # For loop for each time step
        for t in range(0, timesteps):

            # Parsing through complete robot list to check their availability
            for i in range(len(robotlist)):
                # Checking if robot is idle
                if (robotlist[i].current_task == "idle"):

                    # If idle and replicator
                    if (robotlist[i].type == "Replicator"):

                        # Checking if robot can assemble
                        if (assembleCheck("Replicator")):
                            # Starting the assembly process + reducing resources
                            assembling(robotlist[i], "Replicator")

                        # checking if robot can print
                        elif (printCheck(robotlist[i])):
                            # Starting the printing process + reducing resources
                            printing(robotlist[i])

                        # checking if robot can collect
                        elif (collectCheck()):
                            # Starting the collecting process + reducing resources
                            collecting(robotlist[i])

                        # If can't do any task then set robot to idle
                        else:
                            robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                            robotlist[i].set_task_dur(0)
                            robotlist[i].set_curr_task("idle")

                    # If idle and printer
                    elif (robotlist[i].type == "Printer"):

                        if (printCheck(robotlist[i])):
                            printing(robotlist[i])
                        elif (collectCheck()):
                            collecting(robotlist[i])
                        else:
                            robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                            robotlist[i].set_task_dur(0)
                            robotlist[i].set_curr_task("idle")

                    # If idle and assembler
                    elif (robotlist[i].type == "Assembler"):

                        if (robotlist[i].get_previously_built() == ""):
                            if (assembleCheck("Normal")):
                                isAssembling = assembling(robotlist[i], "Normal")
                            elif (assembleCheck("Assembler")):
                                isAssembling = assembling(robotlist[i], "Assembler")
                            elif (assembleCheck("Printer")):
                                isAssembling = assembling(robotlist[i], "Printer")
                            elif (collectCheck()):
                                collecting(robotlist[i])
                            else:
                                robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                                robotlist[i].set_task_dur(0)
                                robotlist[i].set_curr_task("idle")
                        else:
                            if (robotlist[i].get_previously_built() == "Assembler" and assembleCheck("Printer")):
                                isAssembling = assembling(robotlist[i], "Printer")
                            elif (robotlist[i].get_previously_built() == "Printer" and assembleCheck("Normal")):
                                isAssembling = assembling(robotlist[i], "Normal")
                            elif (robotlist[i].get_previously_built() == "Normal" and assembleCheck("Assembler")):
                                isAssembling = assembling(robotlist[i], "Assembler")
                            elif (collectCheck()):
                                collecting(robotlist[i])
                            else:
                                robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                                robotlist[i].set_task_dur(0)
                                robotlist[i].set_curr_task("idle")

                    # If idle and collector
                    elif (robotlist[i].type == "Normal"):
                        # checking if robot can collect
                        if (collectCheck()):
                            # Starting the collecting process + reducing resources
                            collecting(robotlist[i])
                        else:
                            robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                            robotlist[i].set_task_dur(0)
                            robotlist[i].set_curr_task("idle")

                # If robot is not idle
                else:

                    # Reduce task duration if task not ending in the next time step
                    if (robotlist[i].tasks_dur - 1 != 0):
                        robotlist[i].set_task_dur(robotlist[i].tasks_dur - 1)

                    # If task is ending in the next time step and Printer
                    elif (robotlist[i].tasks_dur - 1 == 0 and robotlist[i].type == "Printer"):

                        # checking if robot can print
                        if (printCheck(robotlist[i])):
                            # Starting the printing process + reducing resources
                            printing(robotlist[i])

                        # checking if robot can collect
                        elif (collectCheck()):
                            # Starting the collecting process + reducing resources
                            collecting(robotlist[i])

                        # If can't do any task then set robot to idle
                        else:
                            robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                            robotlist[i].set_task_dur(0)
                            robotlist[i].set_curr_task("idle")


                    # If task is ending in the next time step and current robot is Assembler
                    elif (robotlist[i].tasks_dur - 1 == 0 and robotlist[i].type == "Assembler"):

                        if (assembleCheck("Normal") and robotlist[i].get_previously_built() == "Printer"):
                            assembling(robotlist[i], "Normal")
                        elif (assembleCheck("Printer") and robotlist[i].get_previously_built() == "Assembler"):
                            assembling(robotlist[i], "Printer")
                        elif (assembleCheck("Assembler") and robotlist[i].get_previously_built() == "Normal"):
                            assembling(robotlist[i], "Assembler")
                            # checking if robot can collect
                        elif (collectCheck()):
                            # Starting the collecting process + reducing resources
                            collecting(robotlist[i])

                            # If can't do any task then set robot to idle
                        else:
                            robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                            robotlist[i].set_task_dur(0)
                            robotlist[i].set_curr_task("idle")

                        # If robot task is ending in the next step
                        # Create a new robot for the robot list that can start working the next cycle
                        if (robotlist[i].get_prev_task() == "assembling"):

                            # Build a new robot in a fixed pattern
                            if (robotlist[i].get_previously_built() == ""):
                                newbot = assemble(robotlist[i], "Normal")
                            elif (robotlist[i].get_previously_built() == "Normal"):
                                newbot = assemble(robotlist[i], "Printer")
                            elif (robotlist[i].get_previously_built() == "Printer"):
                                newbot = assemble(robotlist[i], "Assembler")
                            elif (robotlist[i].get_previously_built() == "Assembler"):
                                newbot = assemble(robotlist[i], "Normal")
                            else:
                                newbot = assemble(robotlist[i], "Normal")

                            # Build a new replicator
                            # newbot = assemble(robotlist[i], robotlist[i].get_previously_built())
                            # If newbot passes the quality check
                            if newbot and newbot.build_qual >= 0.5:

                                # If newbot is a collector))
                                if (newbot.type == "Normal"):
                                    # checking if robot can collect
                                    if (collectCheck()):
                                        # Starting the collecting process + reducing resources
                                        collecting(newbot)
                                    else:
                                        newbot.set_prev_task(newbot.get_curr_task())
                                        newbot.set_task_dur(0)
                                        newbot.set_curr_task("idle")

                                elif (newbot.type == "Printer"):
                                    if (printCheck(newbot)):
                                        printing(newbot)
                                    elif (collectCheck()):
                                        collecting(newbot)
                                    else:
                                        newbot.set_prev_task(newbot.get_curr_task())
                                        newbot.set_task_dur(0)
                                        newbot.set_curr_task("idle")
                                # If idle and assembler
                                elif (newbot.type == "Assembler"):
                                    if (newbot.get_previously_built() == ""):
                                        if (assembleCheck("Normal")):
                                            isAssembling = assembling(newbot, "Normal")
                                        elif (assembleCheck("Assembler")):
                                            isAssembling = assembling(newbot, "Assembler")
                                        elif (assembleCheck("Printer")):
                                            isAssembling = assembling(newbot, "Printer")
                                        elif (collectCheck()):
                                            collecting(newbot)
                                        else:
                                            newbot.set_prev_task(newbot.get_curr_task())
                                            newbot.set_task_dur(0)
                                            newbot.set_curr_task("idle")
                                    else:
                                        if (newbot[i].get_previously_built() == "Assembler" and assembleCheck("Printer")):
                                            isAssembling = assembling(newbot, "Printer")
                                        elif (newbot[i].get_previously_built() == "Printer" and assembleCheck("Normal")):
                                            isAssembling = assembling(newbot, "Normal")
                                        elif (newbot[i].get_previously_built() == "Normal" and assembleCheck("Printer")):
                                            isAssembling = assembling(newbot, "Printer")
                                        elif (collectCheck()):
                                            collecting(newbot)
                                        else:
                                            newbot.set_prev_task(newbot.get_curr_task())
                                            newbot.set_task_dur(0)
                                            newbot.set_curr_task("idle")

                                # Adding the newbot to the total robot list and robot list
                                totlist.append(newbot)
                                robotlist.append(newbot)

                            # If newbot does not pass the quality check
                            else:
                                # Adding the newbot to the total robot list and useless list
                                totlist.append(newbot)
                                useless.append(newbot)

                        # check if it can keep assembling next time step


                    # If task is ending in the next time step and Collector
                    elif (robotlist[i].type == "Normal"):

                        # checking if robot can collect
                        if (collectCheck()):
                            # Starting the collecting process + reducing resources
                            collecting(robotlist[i])
                        else:
                            robotlist[i].set_prev_task(robotlist[i].get_curr_task())
                            robotlist[i].set_task_dur(0)
                            # set current task to idle if can not collect
                            robotlist[i].set_curr_task("idle")

            n_replicator = 0
            n_normal = 0
            n_assembler = 0
            n_printer = 0

            c_flag = 0
            p_flag = 0
            a_flag = 0
            i_flag = 0

            useless_c_flag = 0
            useless_p_flag = 0
            useless_a_flag = 0
            useless_r_flag = 0

            tot_build_qual_inservice = 0
            tot_build_qual_inoutservice = 0

            build_quality_list = []

            # print(t)
            for i in robotlist:
                if i.current_task == "collecting":
                    # print(i)
                    c_flag += 1
                if i.current_task == "printing":
                    p_flag += 1
                if i.current_task == "assembling":
                    a_flag += 1
                if i.current_task == "idle":
                    # print(i)
                    i_flag += 1

                if (i.type == "Replicator"):
                    n_replicator += 1;
                if (i.type == "Normal"):
                    n_normal += 1;
                if (i.type == "Assembler"):
                    n_assembler += 1;
                if (i.type == "Printer"):
                    n_printer += 1;

                tot_build_qual_inservice = tot_build_qual_inservice + i.get_buid_qual()

            for i in useless:
                if (i.type == "Replicator"):
                    useless_r_flag += 1;
                if (i.type == "Normal"):
                    useless_c_flag += 1;
                if (i.type == "Assembler"):
                    useless_a_flag += 1;
                if (i.type == "Printer"):
                    useless_p_flag += 1;

            for i in totlist:
                tot_build_qual_inoutservice = tot_build_qual_inoutservice + i.get_buid_qual()

                build_quality_list.append(i.get_buid_qual())

            avg_build_qual_inservice = round(tot_build_qual_inservice / len(robotlist), decimalPlaces)
            avg_build_qual_inoutservice = round(tot_build_qual_inoutservice / len(totlist), decimalPlaces)

            listnumCollecting.append(c_flag)
            listnumPrinting.append(p_flag)
            listnumAssembling.append(a_flag)


            neatPrint = False
            if neatPrint:
                print("=" * 50)
                print(t, ":", len(robotlist), [NonPr, Printable, Materials, Env_Materials])
                print("Time\t\t", t)
                print("#Replicator:\t", n_replicator)
                print("#Normal:\t", n_normal)
                print("#Assembling:\t", n_assembler)
                print("#Printinger:\t", n_printer)
                print("#Robots\t\t", len(robotlist))
                print("Materials\t", [NonPr, Printable, Materials, Env_Materials])
                print("#Assembling:\t", a_flag)
                print("#Printing:\t\t", p_flag)
                print("#Collecting:\t", c_flag)
                print("#Idle:\t\t", i_flag)

            ids = []
            for j in totlist:
                isWaste = False
                if j.build_qual < QualityThreshold:
                    isWaste = True

                # if(j.type=="Replicator"): print(j.beingbuiltlist)
                ids.append(j.id)

            df.loc[len(df)] = [t, NonPr, Printable, Materials, Env_Materials,
                               n_replicator, n_normal, n_assembler, n_printer,
                               a_flag, p_flag, c_flag, i_flag,
                               len(robotlist), len(useless),
                               avg_build_qual_inservice, avg_build_qual_inoutservice,
                               useless_r_flag, useless_c_flag, useless_a_flag, useless_p_flag]

        last_row = df.tail(1)
        mcdf = mcdf.append(last_row, ignore_index=True)


    mcdf.to_csv("./Output/HHE/srrs_HHE_mc.csv")


if __name__ == "__main__":
    main()









