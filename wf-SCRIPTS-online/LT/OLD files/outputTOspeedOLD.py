#! /usr/bin/env python3

#this OLD version has been replaced by V2

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import time
import csv

def toSpeed(basePath, outputFile):
    data = outputFile +".csv"
    for filename in os.listdir(basePath):
        if filename == data:
            print(f"\n-----Analyzing data in {data} -----")
            time.sleep(2)
            newname = filename.split(".csv")[0]
            newname1 = basePath +"/"+ newname + "-speed.csv"
            newname2 = basePath +"/" + newname + "-speed.png"
            newname3 = basePath +"/"+ newname + "-avg.csv"
            newname4 = basePath +"/"+ newname + "-barchart.png"
            newname5 = basePath +"/"+ newname + "-boxplot.png"
            newname6 = basePath +"/"+ newname + "-walking.csv"
            file= basePath +"/"+ data
            df = pd.read_csv(basePath +"/"+ data, sep=",")
            
            maxSpeed = df.iloc[:,3].max()
            
            #find the wells with flies
            ID = []
            for row in range(1,len(df)):
                if df.iloc[row,1] in ID:
                    pass
                else:
                    ID.append(df.iloc[row,1])
            ID.sort()
            
            #make list of all timestamps
            timestampList =[]
            for row in range(1,len(df)):
                if df.iloc[row,4] in timestampList:
                    pass
                else:
                    timestampList.append(df.iloc[row,4])
            timestampList.sort()
            
            #creates a list with the length of timestampList full of -1
            emptySeries = []
            for i in range(len(timestampList)):
                emptySeries.append(-1)


            headers = ["timestamp"] + ["timeDif"] + ID

            finalDict = {headers[i]:emptySeries.copy() for i in range(len(headers))}

            j = 0
            finalDict["timestamp"][j]= timestampList[j]
            finalDict["timeDif"][j] = 0
            for row in range(len(df)):
                if df.iloc[row,4] == finalDict["timestamp"][j]:
                    finalDict[df.iloc[row,1]][j] = df.iloc[row,3]
                else:
                    j = j+1
                    if j < len(timestampList):
                        finalDict["timestamp"][j]= timestampList[j]
                        finalDict["timeDif"][j] = round(finalDict["timestamp"][j]-finalDict["timestamp"][j-1])+finalDict["timeDif"][j-1] 
                        if df.iloc[row,4] == finalDict["timestamp"][j]:
                            finalDict[df.iloc[row,1]][j] = df.iloc[row,3]
                    else:
                        break    

            print("saving file")

            for i in range(len(ID)):
                ID[i] = "fly" + str(ID[i])
            columnNames = ["timestamp"] + ["timeDif"] + ID
            destDF = pd.DataFrame.from_dict(finalDict)#, columns=COLUMN_NAMES)
            destDF.columns= columnNames
            destDF.to_csv(newname1)

            print("making graph")

            numberofgraphs = len(ID)
            alto = numberofgraphs*1
            
            plt.figure(figsize=(9,alto))
            
            for j in range(2,numberofgraphs+2):
                plt.subplot(numberofgraphs,1,j-1)
                plt.title(destDF.columns[j], loc="right", pad="-15")
                a = str(10/10) #reemplazar el primer 10 por selectFrame
                a = "speed [px/"+a+"sec]"
                plt.suptitle(a)
                plt.suptitle("speed [px/sec]")
                plt.plot(destDF["timeDif"], destDF.iloc[:,j], color="blue",linewidth=1,markersize=5)#,mfc=black
                plt.ylim(top= maxSpeed, bottom = -5)
                if j<numberofgraphs:
                    plt.tick_params(axis="x", labelbottom =False)
            
            plt.tight_layout() 
            plt.savefig(newname2)

####calculo de promedios y otros parametros
            finalDict2 ={}
            filteredDict = {}
           
            index_list = ["speed avg", "speed std", "walked pixels", "total", "count>0", "count0", "count-1","%walking","%still","error"]
            total = len(destDF)
            boxplot_list = []
            
            for i in range(len(ID)):
                j = i+2
                count1= len(destDF[destDF.iloc[:,j] == -1])
                count0 = len(destDF[destDF.iloc[:,j] == 0])
                walking = destDF[destDF.iloc[:,j] > 0]
                countWalking = len(walking)
                mean = walking.iloc[:,j].mean()
                std = walking.iloc[:,j].std()
                sumpix = walking.iloc[:,j].sum()
                if pd.isna(mean):
                    mean = 0
                if pd.isna(std):
                    std = 0
                percWalking = countWalking*100/(countWalking + count0)
                percError = count1*100/total
                percStill = count0*100/(countWalking + count0)
                finalDict2[ID[i]] = [mean, std, sumpix, total, countWalking, count0, count1, percWalking, percStill,percError]
                filteredData = walking.iloc[:,j].tolist() #hace una lista con los valores >0
                filteredDict[ID[i]] = filteredData
                boxplot_list.append(filteredData) #agrega valores >0 a una lista para hacer boxplot

            avgDF = pd.DataFrame(finalDict2, index = index_list)#, columns=COLUMN_NAMES)
            avgDF.to_csv(newname3)

            filteredDF = pd.DataFrame.from_dict(filteredDict, orient="index") #usa los indices como columnas y llena valores vacíos con NaN y luego
                                                                #transpone porque si no, dice que array tienen distintos largos
            filteredDF = filteredDF.transpose() 
            filteredDF.to_csv(newname6)
            
            maxavg = avgDF.loc["speed avg"].max()
            maxstd = avgDF.loc["speed std"].max()
            maxSum = maxavg + maxstd + 5

            
#####bar chart
            plt.figure(figsize=(6,8))
            plt.subplot(2,2,1)
            plt.barh(avgDF.columns,avgDF.iloc[0],xerr=avgDF.iloc[1]) ##iloc[0] es speed avg
            plt.xlim(right= maxSum)
            plt.title("avg speed +/- std",fontsize=10)
            a = str(selectFrame/10)
            a = "[px/"+a+" sec]"
            plt.xlabel(a)
            
            plt.subplot(2,2,2)
            plt.barh(avgDF.columns,avgDF.iloc[7]) ##iloc[7] es % time walking
            plt.title("percentage of time walking",fontsize=10)
            plt.xlabel("percent")
            plt.xlim(right = 100)
##            plt.tick_params(axis="y", labelleft =False, left=False)

            plt.subplot(2,2,3)
            plt.barh(avgDF.columns,avgDF.iloc[2]) ##iloc[7] es % sum pixels
            plt.title("total distance walked",fontsize=10)
            plt.xlabel("pixels")
##            plt.xlim(right = 100)
##            plt.tick_params(axis="y", labelleft =False, left=False)
            plt.subplot(2,2,4)
            plt.barh(avgDF.columns,avgDF.iloc[9]) ##iloc[7] es % sum pixels
            plt.title("% time not detected",fontsize=10)
##            plt.xlim(right= maxSum)
            plt.xlabel("percent")


            plt.tight_layout()
            
            plt.savefig(newname4)

            
#######boxplot
            plt.figure()
            plt.boxplot(boxplot_list,vert=False,flierprops=dict(markersize=2),labels=avgDF.columns)
            plt.xlabel(a)
            plt.title("speed")
            plt.savefig(newname5)
            
        

            print("graph saved")
            time.sleep(1)
#             plt.show()
            

if __name__ == "__main__":
    data =  "output.csv"
    toSpeed(data)
