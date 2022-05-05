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


timesteps = 120
fig, ax = plt.subplots(3,2)
# plt.title("SRRS - DHO Config.")
# plt.xlabel("Time")
# plt.ylabel("Number of robots")
# plt.grid(axis='y')

# set random number generator
random.seed()

# global variables
rid = 1
nid = 0
aid = 0
pid = 0
decimalPlaces = 3

# simulation parameters
Num_Steps = 100				#; % Number of iterations/time-steps that the simulation goes through.
NonPr = 300.0 				#; % The robot system=s starting quantity of nonprintable components.
Printable = 100.0 			#; % The robot system’s starting quantity of printable components.
Materials = 50.0 			#; % The robot system’s starting quantity of raw printing materials.
Env_Materials = 500.0 		#; % The environment’s quantity of collectable raw printing materials.
BaseCost_NonPr = 1 			#; % Base robot cost of nonprintable components.
PrintCost_NonPr = 1 		#; % Print capability cost of nonprintable components.
AssembleCost_NonPr = 1 		#; % Assemble capability cost of nonprintable components.
BaseCost_Pr = 2 			#; % Base robot cost of printable components.
PrintCost_Pr = 2 			#; % Print capability cost of printable components.
AssembleCost_Pr = 2 		#; % Assemble capability cost of printable components.
BaseCost_Time = 2 			#; % Base robot cost of build time (in time-steps).
PrintCost_Time = 2 			#; % Print capability cost of build time (in time-steps).
AssembleCost_Time = 2 		#; % Assemble capability cost of build time (in time-steps).
Print_Efficiency = 1.0 		#; % Factor that scales raw printing materials to printable components.
Print_Amount = 1.0 			#; % Amount of raw materials converted per print task.
Collect_Amount = 1.0 		#; % Raw printing materials per collecting robot per timestep.
QualityThreshold = 0.5 		#; % Robots with a quality below this are non-functional.
Quality_incr_Chance = 5.0 	#; % Chance that a new robot’s build quality will increase.
Quality_incr_Lower = 0.01 	#; % Lower bound for quality increase amount.
Quality_incr_Upper = 0.05 	#; % Upper bound for quality increase amount.
Quality_decr_Chance = 50.0 	#; % Chance that a new robot s build quality will decrease.
Quality_decr_Lower = 0.01 	#; % Lower bound for quality decrease amount.
Quality_decr_Upper = 0.25 	#; % Upper bound for quality decrease amount.
RiskAmount_Collect = 1.0 	#; % Risk chance for the collect task type.
RiskAmount_Assemble = 0.1 	#; % Risk chance for the assemble task type.
RiskAmount_Print = 0.1 		#; % Risk chance for the print task type.
RiskQuality_Modifier = 5.0 	#; % Multiplier for impact of quality defects on risk amount.
RiskFactory_Modifier = 0.1 	#; % Multiplier for impact of factory-made robots on risk amount

# [replicator,normal,assembler,printer]
cost_Pr = [6,2,4,4]			#; % Total cost printable
cost_NonPr = [3,1,2,2]		#; % Total cost nonprintable

timecost_base = 2			#; % time cost basic
timecost_print = 2			#; % time cost print capability
timecost_assemble = 2		#; % time cost assemble capability

timecost_normal = timecost_base
timecost_replicator = timecost_base+timecost_assemble+timecost_print
timecost_printer = timecost_base+timecost_print
timecost_assembler = timecost_base+timecost_assemble

# robot object
class Robot:
	def __init__(self,type,build_qual,id):
		self.type = type
		self.current_task = "idle"
		self.prev_task = "idle"
		self.id = self.type[0]+str(id)
		self.build_qual = round(build_qual,decimalPlaces)
		self.factory_made = True
		self.tasks_dur = 0
		self.taskindex = 0
		
		if(self.type == "Replicator"):
			self.tasks = ["Assemble","Print","Collect"]
			self.beingbuiltlist = []
		if(self.type == "Normal"):
			self.tasks = ["Collect"]
		if(self.type == "Assembler"):
			self.tasks = ["Assemble","Collect"]
		if(self.type == "Printer"):
			self.tasks = ["Print","Collect"]
		self.num_tasks = len(self.tasks)

	def __str__(self):
		return str(self.id)+" "+str(self.current_task)

	def set_curr_task(self,tasktype):
		self.current_task = tasktype
		if(self.current_task == "idle"):
			self.tasks_dur = 0
		if(self.current_task == "collecting"):
			self.tasks_dur = 1
		if(self.current_task == "assembling"):
			self.tasks_dur = 2
		if(self.current_task == "printing"):
			self.tasks_dur = 2

	# methods of robot object
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

# check if robot can collect from Env_Materials
def collectCheck(robot):
	global Materials, Env_Materials, Collect_Amount
	if (Env_Materials - Collect_Amount >= 0):
		# Materials = Materials + Collect_Amount
		# Env_Materials = Env_Materials - Collect_Amount
		return True
	else:
		return False

# task function - collecting
def collecting(robot):
	global Materials, Env_Materials, Collect_Amount
	robot.set_prev_task(robot.get_curr_task())
	robot.set_curr_task("collecting")
	robot.set_task_dur(1)
	Materials = Materials + Collect_Amount
	Env_Materials = Env_Materials - Collect_Amount

# build robot task - assembler and replicator
# assemble task

def assembleCheck(robot,tobuild):
	# global rid,nid,aid,pid,Printable,NonPr,Quality_incr_Chance,Quality_incr_Lower, Quality_incr_Upper
	
	if(tobuild == "Replicator"):
		i=0
		# rid = rid+1
		# robotid = rid
	if(tobuild == "Normal"):
		i=1
		# nid = nid+1
		# robotid = nid
	if(tobuild == "Assembler"):
		i=2
		# aid = aid+1
		# robotid = aid
	if(tobuild == "Printer"):
		i=3
		# pid = pid+1
		# robotid = pid

	if Printable - cost_Pr[i] >= 0 and NonPr - cost_NonPr[i] >= 0:
		return True
	else:
		return False


def assembling(robot,tobuild):
	global rid,nid,aid,pid,Printable,NonPr,Quality_incr_Chance,Quality_incr_Lower, Quality_incr_Upper
	
	if(tobuild == "Replicator"):
		i=0
		taskDur = timecost_replicator
	if(tobuild == "Normal"):
		i=1
		taskDur = timecost_normal
	if(tobuild == "Assembler"):
		i=2
		taskDur = timecost_assembler
	if(tobuild == "Printer"):
		i=3
		taskDur = timecost_printer
	
	robot.set_prev_task(robot.get_curr_task())
	robot.set_curr_task("assembling")
	robot.set_task_dur(taskDur)
	if(robot.type=="Assembler" or robot.type=="Replicator"):
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
		
		robot.beingbuiltlist.append(tobuild[0]+str(robotid))
		return True
	else:
		robot.set_prev_task(robot.get_curr_task())
		robot.set_curr_task("idle")
		robot.set_task_dur(0)
		return False

		

def assemble(builder,tobuild):
	global rid,nid,aid,pid,Printable,NonPr,Quality_incr_Chance,Quality_incr_Lower, Quality_incr_Upper
	
	if(builder.type=="Assembler" or builder.type=="Replicator"):
		if(tobuild == "Replicator"):
			i=0
			
		if(tobuild == "Normal"):
			i=1
			
		if(tobuild == "Assembler"):
			i=2
			
		if(tobuild == "Printer"):
			i=3

		AssemblerQuality = builder.get_buid_qual()
		# robot's build quality		
		rand = round(random.uniform(0,1),decimalPlaces)
		if rand > round((1.0 - Quality_incr_Chance/100),decimalPlaces):
			RobotQuality = AssemblerQuality + random.uniform(Quality_incr_Lower, Quality_incr_Upper)
		elif rand < Quality_decr_Chance :
			RobotQuality = AssemblerQuality - random.uniform(Quality_decr_Lower, Quality_decr_Upper)
		else :
			RobotQuality = AssemblerQuality
		# print(builder,builder.beingbuiltlist)
		newRobot = Robot(tobuild,RobotQuality,builder.beingbuiltlist.pop(0)[1:])
		return newRobot
	else:
		return None


def printCheck(robot):
	if(robot.type=="Replicator" or robot.type=="Printer"):
		global Print_Efficiency, Print_Amount, Materials, Printable
		if Materials - (Print_Efficiency*Print_Amount) > 0:
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
	Materials = Materials - (Print_Efficiency*Print_Amount)
	Printable = Printable + (Print_Efficiency*Print_Amount)

def main():
	
	build_qual_range = [0.85,0.95]
	init_build_qual = random.uniform(build_qual_range[0],build_qual_range[1])
	
	df = pd.DataFrame(columns = ["Time","NonPr","Printable","Materials","Env_Materials",
		"#Replicator","#Normal","#Assembler","#Printer",
		"#Assembling","#Printing","#Collecting","#Idle",
		"#In","#Out",
		"Average Build Quality in-service","Average Build Quality of System",
		"#WasteReplicator","#WasteNormal","#WasteAssembler","#WastePrinter"])
	robot = Robot("Replicator",init_build_qual,rid)
	
	totlist = [robot]
	robotlist = [robot]
	useless = []
	
	# number of bots working
	listnumCollecting = []
	listnumPrinting = []
	listnumAssembling = []

	# use lists
	tcoordslist = []
	rcoordslist = []
	wastecoordslist = []
	t_build_quality_list = []

	for t in range(0,timesteps):
		
		for i in range(len(robotlist)):
			# IDLE
			if(robotlist[i].current_task=="idle"):
				
				# Replicator
				if(robotlist[i].type == "Replicator"):
					if(assembleCheck(robotlist[i],"Replicator")):
						isAssembling = assembling(robotlist[i],"Replicator")
					elif(printCheck(robotlist[i])):
						isPrinting = printing(robotlist[i])	
					else:
						robotlist[i].set_prev_task(robotlist[i].get_curr_task())
						robotlist[i].set_task_dur(0)
						robotlist[i].set_curr_task("idle")
					
				# Normal
				elif(robotlist[i].type == "Normal"):
					canCollect = collectCheck(robotlist[i])
					# print(t,robotlist[i].id,canCollect)
					if canCollect:
						collecting(robotlist[i])

			# NOT IDLE
			else:
				# reduce task duration every time step
				if(robotlist[i].tasks_dur - 1 != 0):
					robotlist[i].set_task_dur(robotlist[i].tasks_dur - 1)
				
				# Replicator 
				elif(robotlist[i].tasks_dur - 1 == 0 and robotlist[i].type == "Replicator"):
					# check if it can keep assembling next time step
					if(assembleCheck(robotlist[i],"Replicator")):
						isAssembling = assembling(robotlist[i],"Replicator")
					elif(printCheck(robotlist[i])):
						isPrinting = printing(robotlist[i])	
					else:
						isAssembling = False
						robotlist[i].set_prev_task(robotlist[i].get_curr_task())
						robotlist[i].set_task_dur(0)
						robotlist[i].set_curr_task("idle")
					
					# it enters this loop only when it has to pop a new robot
					if(robotlist[i].get_prev_task()=="assembling"):
						newbot = assemble(robotlist[i],"Normal")
						if newbot and newbot.build_qual>=0.5:
							if(newbot.type == "Normal"):
								canCollect = collectCheck(newbot)
								if canCollect:
									collecting(newbot)
							totlist.append(newbot)
							robotlist.append(newbot)
						else:
							totlist.append(newbot)
							useless.append(newbot)
						robotlist[i].set_prev_task(robotlist[i].current_task)

				# Normal
				elif(robotlist[i].type == "Normal"):
					canCollect = collectCheck(robotlist[i])
					if(canCollect):
						collecting(robotlist[i])
					else:
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
			if i.current_task=="collecting":
				# print(i)
				c_flag+=1
			if i.current_task=="printing":
				p_flag+=1
			if i.current_task=="assembling":
			 	a_flag+=1
			if i.current_task=="idle":
				# print(i)
				i_flag+=1

			if(i.type=="Replicator"):
				n_replicator += 1;
			if(i.type== "Normal"):
				n_normal += 1;
			if(i.type== "Assembler"):
				n_assembler += 1;
			if(i.type== "Printer"):
				n_printer += 1;

			tot_build_qual_inservice = tot_build_qual_inservice + i.get_buid_qual()

		for i in useless:
			if(i.type=="Replicator"):
				useless_r_flag += 1;
			if(i.type== "Normal"):
				useless_c_flag += 1;
			if(i.type== "Assembler"):
				useless_a_flag += 1;
			if(i.type== "Printer"):
				useless_p_flag += 1;

		for i in totlist:
			tot_build_qual_inoutservice = tot_build_qual_inoutservice + i.get_buid_qual()
			plt.subplot(3,2,5)
			plt.scatter(t,i.get_buid_qual(),marker='x',color='black',s=0.1)
			build_quality_list.append(i.get_buid_qual())

		avg_build_qual_inservice = round(tot_build_qual_inservice/len(robotlist),decimalPlaces)
		avg_build_qual_inoutservice = round(tot_build_qual_inoutservice/len(totlist),decimalPlaces)
		
		listnumCollecting.append(c_flag)
		listnumPrinting.append(p_flag)
		listnumAssembling.append(a_flag)
	
		# print("="*50)
		neatPrint = False
		if neatPrint:
			print("="*50)
			print(t,":",len(robotlist),[NonPr,Printable,Materials,Env_Materials])			
			print("Time\t\t",t)
			print("#Replicator:\t",n_replicator)
			print("#Normal:\t",n_normal)
			print("#Assembling:\t",n_assembler)
			print("#Printinger:\t",n_printer)
			print("#Robots\t\t",len(robotlist))
			print("Materials\t",[NonPr,Printable,Materials,Env_Materials])
			print("#Assembling:\t",a_flag)
			print("#Printing:\t\t",p_flag)
			print("#Collecting:\t",c_flag)
			print("#Idle:\t\t",i_flag)
		
		ids=[]
		for j in totlist:
			isWaste = False
			if j.build_qual<QualityThreshold:
				isWaste = True
			# print(t,len(totlist),j.id,j.current_task,j.get_task_dur(),":\t",j.build_qual)
			# if(j.type=="Replicator"): print(j.beingbuiltlist)
			ids.append(j.id)
		
		df.loc[len(df)] = [t,NonPr,Printable,Materials,Env_Materials,
		n_replicator,n_normal,n_assembler,n_printer,
		a_flag,p_flag,c_flag,i_flag,
		len(robotlist),len(useless),
		avg_build_qual_inservice,avg_build_qual_inoutservice,
		useless_r_flag,useless_c_flag,useless_a_flag,useless_p_flag]
		
		# "#WasteReplicator","#WasteNormal","#WasteAssembler","#WastePrinter"])

		tcoordslist.append(t)
		rcoordslist.append(len(robotlist)) 
		wastecoordslist.append(len(useless))
		t_build_quality_list.append(build_quality_list)

	# print(df.to_string())
	
	
	# plotting	
	flag = True
	plotConfig = flag
	if plotConfig:
		plt.subplot(3,2,1)
		plt.plot(tcoordslist,rcoordslist,color = "blue",label = "#Robots")
		plt.plot(tcoordslist,wastecoordslist,color = "red",label = "#Wasted Robots")
		plt.bar(tcoordslist,listnumAssembling,width=0.5,label = "#Being built")
		curr_built = [x + y for (x, y) in zip(rcoordslist, listnumAssembling)] 
		plt.scatter(tcoordslist,curr_built,marker=".",color="black",label = "#Robots + #Being built")
		plt.legend()
		
		plt.subplot(3,2,2)
		plt.plot(tcoordslist,df["NonPr"],label = "NonPr")
		plt.plot(tcoordslist,df["Printable"],label = "Printable")
		plt.plot(tcoordslist,df["Materials"],label = "Materials")
		plt.plot(tcoordslist,df["Env_Materials"],label = "Env_Materials")
		plt.legend()
		plt.gca().set_xlim(left=0)
		plt.gca().set_ylim(bottom=0)
		
		plt.subplot(3,2,3)
		plt.plot(tcoordslist,df['Average Build Quality in-service'],label = "Avg. Build Quality in service")
		plt.plot(tcoordslist,df['Average Build Quality of System'],label = "Avg. Build Quality total")
		plt.legend()
		plt.gca().set_xlim(left=0)
		plt.gca().set_ylim(top=1,bottom=0)

		plt.subplot(3,2,4)
		plt.plot(tcoordslist,df["#Assembling"],label = "#Assembling")
		plt.plot(tcoordslist,df["#Printing"],label = "#Printing")
		plt.plot(tcoordslist,df["#Collecting"],label = "#Collecting")
		plt.plot(tcoordslist,df["#Idle"],label = "#Idle")
		plt.legend()
		plt.gca().set_xlim(left=0)
		plt.gca().set_ylim(bottom=0)
		# plt.show()

		plt.subplot(3,2,5)
		plt.fill_between(tcoordslist, 0, [0.5]*len(tcoordslist),alpha=0.2,color='red')
		plt.fill_between(tcoordslist, 0.5, [1]*len(tcoordslist),alpha=0.2,color='green')
		plt.gca().set_xlim(left=0)
		plt.gca().set_xlim(right=timesteps)
		plt.gca().set_ylim(bottom=0)
		plt.gca().set_ylim(top=1)

		plt.subplot(3,2,6)
		plt.plot(tcoordslist,df["#Assembler"],label = "#A(in)")
		plt.plot(tcoordslist,df["#Printer"],label = "#P(in)")
		plt.plot(tcoordslist,df["#Replicator"],label = "#R(in)")
		plt.plot(tcoordslist,df["#Normal"],label = "#N(in)")
		plt.plot(tcoordslist,df["#WasteAssembler"],label = "#A(out)",color="blue",linestyle="dashed")
		plt.plot(tcoordslist,df["#WastePrinter"],label = "#P(out)",color="orange",linestyle="dashed")
		plt.plot(tcoordslist,df["#WasteReplicator"],label = "#R(out)",color="green",linestyle="dashed")
		plt.plot(tcoordslist,df["#WasteNormal"],label = "#N(out)",color="red",linestyle="dashed")

		
		#plt.legend(bbox_to_anchor=(1.05, 1.0, 0.3, 0.2), loc='upper left')
		plt.legend()		
		plt.show()

	df.to_csv("srrs_cho.csv")


if __name__ == "__main__":
	main()
	









