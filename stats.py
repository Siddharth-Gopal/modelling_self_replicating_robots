import pandas as pd
import matplotlib.pyplot as plt

filename = "srrs_HHE_mc2"
config = "HHE"
df = pd.read_csv("./Output/"+config+"/"+filename+".csv")
last_row = df.mean()

# df.plot.hist(column = ['Average Build Quality in-service'],bins = 100)
plt.hist(df['Average Build Quality in-service'],bins=20)
plt.xlabel('Average Build Quality in-service')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_avgbuildqual_inserv")
fig.clear()


plt.hist(df['Environment Exhaust Time'],bins=20)
plt.xlabel('Environment Exhaust Time')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_env_exhaust")
fig.clear()

plt.hist(df['Printable Exhaust Time'],bins=20)
plt.xlabel('Printable Exhaust Time')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_printable_exhaust")
fig.clear()

plt.hist(df['NonPr Exhaust Time'],bins=20)
plt.xlabel('NonPr Exhaust Time')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_nonprintable_exhaust")
fig.clear()

plt.hist(df['Print Capacity'],bins=20)
plt.xlabel('Print Capacity')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_print_capacity")
fig.clear()

plt.hist(df['Assembling Capacity'],bins=20)
plt.xlabel('Assembling Capacity')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_assembling_capacity")
fig.clear()

plt.hist(df['Collection Capacity'],bins=20)
plt.xlabel('Collection Capacity')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_collection_capacity")
fig.clear()

plt.hist(df['Average Build Quality of System'],bins=20)
plt.xlabel('Average Build Quality of System')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_avgbuildqual_sys")
fig.clear()

plt.hist(df['#Out'],bins=20)
plt.xlabel('Wasted Robots')
plt.ylabel('Frequency')
fig = plt.gcf()
fig.savefig("./Output/"+config+"/hist_resource_wasted")
fig.clear()

df = df.append(last_row, ignore_index=True)


col = ['Environment Exhaust Time', 'Printable Exhaust Time','NonPr Exhaust Time','Print Capacity',
       'Assembling Capacity', 'Collection Capacity','Average Build Quality in-service', 'Average Build Quality of System','#Out']

mean = df.tail(1)
mean = mean[col]
print(mean.to_string())

last_row = df.std()
df = df.append(last_row, ignore_index=True)


std = df.tail(1)
std = std[col]
print(std.to_string())

df1 = mean.append(std)
df1.to_csv("./Output/"+config+"/"+filename+"_stats.csv")


