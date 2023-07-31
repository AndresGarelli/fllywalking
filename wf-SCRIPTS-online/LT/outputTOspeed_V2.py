#! /usr/bin/env python3

#this is a version of outputTOspeed-V2 modified to apply the V2 analysis to old files
#it will delete old .csv files except for the original output file and
#repeat the analysis. 

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import time
import csv
import statistics

##en este se hace una sola tabla para active e inactive y luego se filtra

def toSpeed(basePath, outputFile):
    #data = outputFile +".csv"
    pxTomm = 10/74
    #pxTomm = 1
    for filename in os.listdir(basePath):
        if filename.endswith(".png"):
            os.remove(basePath+"/"+filename)
            print(f"Deleted {filename}")
    for filename in os.listdir(basePath):
        file_sizes = {}
        for dirpath, dirnames, filenames in os.walk(basePath):
            for filename in filenames:
                if filename.endswith(".csv") or filename.endswith(".png"):
                    file_path = os.path.join(dirpath, filename)
                    size = os.path.getsize(file_path)
                    file_sizes[filename] = size
    #print(file_sizes)
    maxSize = max(file_sizes.values())
    #print(maxSize)
    for file in file_sizes:
        if (file.endswith(".csv") and file_sizes[file] < maxSize) or file.endswith(".png"):
            print(f"Delete {file}")
            file = basePath+"/"+file
            os.remove(file)
        else:
            print(f"Keep {file}")
                
    for filename in os.listdir(basePath):
        data = filename
        if filename.endswith(".csv"):
            print(f"\n----- Analyzing data in {data} -----")
            #time.sleep(2)
            
            newname = filename.split(".csv")[0]
            newname1 = basePath +"/"+ newname + "-speed.csv"
            newname2 = basePath +"/" + newname + "-speed.png"
            newname3 = basePath +"/"+ newname + "-summary.csv"
            newname4 = basePath +"/"+ newname + "-summary.png"
            newname5 = basePath +"/"+ newname + "-boxplot.png"
            #newname6 = basePath +"/"+ newname + "-walking.csv"
            newname7 = basePath +"/"+ newname + "-boutsRaw.csv"
            newname8 = basePath +"/"+ newname + "-active_bouts.png"
            newname9 = basePath +"/"+ newname + "-inactive_bouts.png"
            newname10 = basePath +"/"+ newname + "-sleep_bouts.png"
            newname11 = basePath +"/"+ newname + "-boutsSummary.csv"
            file= basePath +"/"+ data
            df = pd.read_csv(basePath +"/"+ data, sep=",")
            
            maxSpeed = df.iloc[:,3].max()*pxTomm
            
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
            for row in range(len(df)):
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
            finalDict["timeDif"][j] = 1
            for row in range(len(df)):
                if df.iloc[row,4] == finalDict["timestamp"][j]:
                    finalDict[df.iloc[row,1]][j] = df.iloc[row,3]*pxTomm
                else:
                    j = j+1
                    if j < len(timestampList):
                        finalDict["timestamp"][j]= timestampList[j]
                        finalDict["timeDif"][j] = round(finalDict["timestamp"][j]-finalDict["timestamp"][j-1])+finalDict["timeDif"][j-1] 
                        if df.iloc[row,4] == finalDict["timestamp"][j]:
                            finalDict[df.iloc[row,1]][j] = df.iloc[row,3]*pxTomm
                    
                    else:
                        break    

            print("saving file")

            for i in range(len(ID)):
                ID[i] = "fly" + str(ID[i])
            columnNames = ["timestamp"] + ["timeDif"] + ID
            speedDF = pd.DataFrame.from_dict(finalDict)#, columns=COLUMN_NAMES)
            speedDF.columns= columnNames
            speedDF.to_csv(newname1)

            print("making graphs")

            numberofgraphs = len(ID)
            alto = numberofgraphs*1

            
            plt.figure(figsize=(9,alto))
            
            for j in range(2,numberofgraphs+2):
                plt.subplot(numberofgraphs,1,j-1)
                plt.title(speedDF.columns[j], loc="right", pad="-15")
                a = str(10/10) #reemplazar el primer 10 por selectFrame
                if pxTomm == 1:
                    a = "speed [px/"+a+"sec]"
                    plt.ylim(top= maxSpeed, bottom = -5)
                else:
                    a = "speed [mm/"+a+"sec]"
                    plt.ylim(top= maxSpeed, bottom = -1)
                plt.suptitle(a)
                #plt.suptitle("speed [px/sec]")
                plt.plot(speedDF["timeDif"], speedDF.iloc[:,j], color="blue",linewidth=1,markersize=5)#,mfc=black
                
                if j<numberofgraphs:
                    plt.tick_params(axis="x", labelbottom =False)
            
            plt.tight_layout() 
            plt.savefig(newname2)

####calculo de promedios y otros parametros
            finalDict2 ={}
            filteredDict = {}
           
            index_list = ["speed avg", "speed std", "pixels travelled", "total", "count>0", "count0", "count-1","%active","%inactive","error"]
            total = len(speedDF)
            boxplot_list = []
            
            for i in range(len(ID)):
                j = i+2
                count1= len(speedDF[speedDF.iloc[:,j] == -1])
                count0 = len(speedDF[speedDF.iloc[:,j] == 0])
                active = speedDF[speedDF.iloc[:,j] > 0]
                countActive = len(active)
                mean = active.iloc[:,j].mean()
                std = active.iloc[:,j].std()
                sumpix = active.iloc[:,j].sum()
                if pd.isna(mean):
                    mean = 0
                if pd.isna(std):
                    std = 0
                percActive = countActive*100/(countActive + count0)
                percError = count1*100/total
                percInactive = count0*100/(countActive + count0)

                finalDict2[ID[i]] = [mean, std, sumpix, total, countActive, count0, count1, percActive, percInactive, percError]

                filteredData = active.iloc[:,j].tolist() #hace una lista con los valores >0
                filteredDict[ID[i]] = filteredData

               # boxplot_list.append(filteredData) #agrega valores >0 a una lista para hacer boxplot

            avgDF = pd.DataFrame(finalDict2, index = index_list)#, columns=COLUMN_NAMES)
            avgDF.to_csv(newname3)

            filteredDF = pd.DataFrame.from_dict(filteredDict, orient="index") #usa los indices como columnas y llena valores vacíos con NaN y luego
                                                                #transpone porque si no, dice que array tienen distintos largos
            filteredDF = filteredDF.transpose() 
            #filteredDF.to_csv(newname6)
            
            maxavg = avgDF.loc["speed avg"].max()
            maxstd = avgDF.loc["speed std"].max()
            maxSum = maxavg + maxstd + 5

            
#####bar chart
            plt.figure(figsize=(6,8))
            plt.subplot(2,2,1)
            plt.barh(avgDF.columns,avgDF.iloc[0],xerr=avgDF.iloc[1]) ##iloc[0] es speed avg
            plt.xlim(right= maxSum)
            plt.title("avg speed +/- std",fontsize=10)
###################################### Descomentar
#            a = str(selectFrame/10)

            a=str(1)
            if pxTomm == 1:
                a = "[px/"+a+" sec]"
            else:
                a = "[mm/"+a+" sec]"
            plt.xlabel(a)
            
            plt.subplot(2,2,2)
            plt.barh(avgDF.columns,avgDF.iloc[7]) ##iloc[7] es % time walking
            plt.title("percentage of time active",fontsize=10)
            plt.xlabel("percent")
            plt.xlim(right = 100)
##            plt.tick_params(axis="y", labelleft =False, left=False)

            plt.subplot(2,2,3)
            plt.barh(avgDF.columns,avgDF.iloc[2]) ##iloc[7] es % sum pixels
            plt.title("total distance travelled",fontsize=10)
            plt.xscale("log")
            if pxTomm == 1:
                plt.xlabel("pixels")
            else:
                plt.xlabel("mm")
            plt.xlim(left = 1)
##            plt.tick_params(axis="y", labelleft =False, left=False)
            plt.subplot(2,2,4)
            color = []
            for i in avgDF.iloc[9]:
                if i > 10:
                    color.append("red")
                else:
                    color.append("blue")
            plt.barh(avgDF.columns,avgDF.iloc[9],color=color) ##iloc[7] es % sum pixels
            plt.title("% time not detected",fontsize=10)
            maxval = avgDF.iloc[9].max()
            maxval = int(maxval/10)*10 + 10
            plt.xlim(right= maxval)
##            plt.xlim(right= maxSum)

            ########maxXvalue = int(maxXvalue/10)*10 + 10
            plt.xlabel("percent")


            plt.tight_layout()
            
            plt.savefig(newname4)

            
#######boxplot
##            plt.figure()
##            plt.boxplot(boxplot_list,vert=False,flierprops=dict(markersize=2),labels=avgDF.columns)
##            plt.xlabel(a)
##            plt.title("speed")
##            plt.savefig(newname5)
##            
##            print("graphs saved")
##            time.sleep(1)
#             plt.show()

##################walking bouts

            quiescent_threshold = 50*pxTomm   #  50*10/74 is 6.766 mm, that is 3.03Xfly if fly is 2.23
            sleep_threshold = 600
            
            listaGeneral =[]
            #hago una lista con los nombres de las columnas salteando las primeras dos
            flies = list(speedDF.columns)[2:]
            print("analyzing bouts")
            for fly in flies:
                begin = False
                time_active = 0
                time_inactive = 0
                distance = 0
                speed_list = []
                first = True
                
                indmax = max(list(speedDF[fly].index))
                for ind in speedDF.index:  #crea un interable conformado por los indices de el dataframe
                    if speedDF[fly][ind] > 0:
                        if begin == False:
                            begin = True
                            #begins active bout
                            time_active += (speedDF.iloc[ind,0]-speedDF.iloc[ind-1,0]) #le suma timeDif
                            distance += speedDF[fly][ind]
                            speed_list.append(speedDF[fly][ind])
                            
                            #ends inactive bout, saves inactive bout info and reset
                            if time_inactive >= sleep_threshold:
                                category = "sleep"
                            else:
                                category = "pause"
                            event = [fly,"inactive", time_inactive,category,0,0,0]
                            listaGeneral.append(event)
                            time_inactive = 0
                            
                        else:
                            time_active += (speedDF.iloc[ind,0]-speedDF.iloc[ind-1,0]) 
                            distance += speedDF[fly][ind]
                            speed_list.append(speedDF[fly][ind])
                            
                    elif speedDF[fly][ind]  == 0:
                        if begin == True:
                            #ends active bout, saves and resets parameters
                            begin = False
                            boutAvgSpeed = distance/time_active
                            boutMedianSpeed = statistics.median(speed_list)
                            
##                            if boutAvgSpeed <= quiescent_threshold:
##                                category = "micromovement"
##                            else:
##                                category = "walking"

                            if distance <= quiescent_threshold:
                                category = "micromovement"
                            else:
                                category = "walking"
                            event = [fly,"active", time_active, category, distance, boutAvgSpeed, boutMedianSpeed]
                            listaGeneral.append(event)
                            time_active = 0
                            distance = 0
                            speed_list = []
                            #begins inactive bout
                            time_inactive = (speedDF.iloc[ind,0]-speedDF.iloc[ind-1,0])
                        else:
                            #first frame
                            if first == True:
                                first = False
                                time_inactive = speedDF.iloc[ind,1] #time dif. If not, it is epoch
                            else:
                                time_inactive += (speedDF.iloc[ind,0]-speedDF.iloc[ind-1,0])    
                            #inicia inactive bout
                            
                            
                            
                    if ind == indmax:
                        if begin == True:  #saves last activ bout
                            begin = False
                            boutAvgSpeed = distance/time_active
                            boutMedianSpeed = statistics.median(speed_list)
##                            if boutAvgSpeed <= quiescent_threshold:
##                                category = "micromovement"
##                            else:
##                                category = "walking"

                            if distance <= quiescent_threshold:
                                category = "micromovement"
                            else:
                                category = "walking"
                            event = [fly,"active", time_active, category, distance, boutAvgSpeed, boutMedianSpeed]
                            listaGeneral.append(event)
                            time_active = 0
                            distance = 0
                        else:
                            #saves last inactive bout
                            if time_inactive >= sleep_threshold:
                                category = "sleep"
                            else:
                                category = "pause"
                            event = [fly,"inactive", time_inactive,category,0,0,0]
                            listaGeneral.append(event)
                            time_inactive = 0

            dfBouts = pd.DataFrame(listaGeneral, columns = ["fly", "type", "bout duration","category","bout distance", "bout Avg speed","bout Median speed"])                
            dfBouts.to_csv(newname7)

           # dfInactiveBouts = pd.DataFrame(listaGeneralInactive, columns = ["fly", "inactive bout#", "inactive bout duration"])
            #dfInactiveBouts.to_csv(newname9)
            
            ##busco el numero de bouts para cada animal. cuento cuantas veces aparece cada animal
            numberAB = []  #number of active bouts
            numberIB =[]   #number of inactive bouts
            number_pauseB =[]   #number of pause bouts
            number_sleepB =[]   #number of sleep bouts
            number_microB =[]   #number of micromovement bouts
            number_walkB =[]   #number of walk bouts

            activeTotalTime =[]  #total time of each behavior
            inactiveTotalTime =[]
            pauseTotalTime =[]
            sleepTotalTime =[]
            microTotalTime =[]
            walkTotalTime =[]

            activePercent =[]  #total time of each behavior
            inactivePercent =[]
            pausePercent =[]
            sleepPercent =[]
            microPercent =[]
            walkPercent =[]
            
            totalTime = []

            boxDuration =[]
            boxDistance =[]
            boxAvg =[]
            boxMedian =[]
            boxMicromovement =[]
            boxWalking = []
            boxSleepTime =[]
            boxDurationIB =[]
            boxPauseTime =[]

            qualitycheck = []
            check =[]
      
            for fly in flies:
                duration_temp =[]
                avg_temp =[]
                median_temp =[]
                distance_temp =[]

                durationIB_temp =[]

                sleepTime_temp =[]
                pause_temp =[]

                micromovement_temp = []
                walking_temp = []

                totalTime_temp = dfBouts[(dfBouts["fly"]==fly)].sum()[2]
                totalTime.append(totalTime_temp)
                
                flydf = dfBouts[(dfBouts["fly"]==fly) & (dfBouts["type"]=="active")]
                numberAB.append(len(flydf))
                activeTotalTime.append(flydf.sum()[2]) #clumna 2 es bout duration
                activePercent.append(round(flydf.sum()[2]*100/totalTime_temp,2))
                    
                for ind in flydf.index:
                    duration_temp.append(flydf["bout duration"][ind])                       
                    avg_temp.append(flydf["bout Avg speed"][ind])
                    median_temp.append(flydf["bout Median speed"][ind])
                    distance_temp.append(flydf["bout distance"][ind])
                    if flydf["category"][ind] == "micromovement":
                        micromovement_temp.append(flydf["bout distance"][ind])
                    elif flydf["category"][ind] == "walking":
                        walking_temp.append(flydf["bout distance"][ind])

                #quality check= verifies that total px in avgDF equals sum of distance of active bouts
                if (round(avgDF[fly][2],3) == round(flydf.sum()[4],3)): #busca suma total de px en speedDF y compara con flydf que también deriva de speedDF
                    pass
                else:
                    qualitycheck.append(fly)
                    
                boxDuration.append(duration_temp)
                boxAvg.append(avg_temp)
                boxMedian.append(median_temp)
                boxDistance.append(distance_temp)
                boxMicromovement.append(micromovement_temp)
                boxWalking.append(walking_temp)

                flydf = dfBouts[(dfBouts["fly"]==fly) & (dfBouts["category"]=="micromovement")]
                number_microB.append(len(flydf))
                microTotalTime.append(flydf.sum()[2]) #clumna 2 es bout duration
                microPercent.append(round(flydf.sum()[2]*100/totalTime_temp,2))

                flydf = dfBouts[(dfBouts["fly"]==fly) & (dfBouts["category"]=="walking")]
                number_walkB.append(len(flydf))
                walkTotalTime.append(flydf.sum()[2]) #clumna 2 es bout duration
                walkPercent.append(round(flydf.sum()[2]*100/totalTime_temp,2))                
                
                flydf = dfBouts[(dfBouts["fly"]==fly) & (dfBouts["type"]=="inactive")]
                numberIB.append(len(flydf))
                inactiveTotalTime.append(flydf.sum()[2]) #clumna 2 es bout duration
                inactivePercent.append(round(flydf.sum()[2]*100/totalTime_temp,2))

                for ind in flydf.index:
                    durationIB_temp.append(flydf["bout duration"][ind])
                boxDurationIB.append(durationIB_temp)

                flydf = dfBouts[(dfBouts["fly"]==fly) & (dfBouts["category"]=="pause")]
                number_pauseB.append(len(flydf))
                pauseTotalTime.append(flydf.sum()[2]) #clumna 2 es bout duration
                pausePercent.append(round(flydf.sum()[2]*100/totalTime_temp,2))
                for ind in flydf.index:
                    pause_temp.append(flydf["bout duration"][ind])
                boxPauseTime.append(pause_temp)

                flydf = dfBouts[(dfBouts["fly"]==fly) & (dfBouts["category"]=="sleep")]
                number_sleepB.append(len(flydf))
                sleepTotalTime.append(flydf.sum()[2]) #clumna 2 es bout duration
                sleepPercent.append(round(flydf.sum()[2]*100/totalTime_temp,2))
                
                for ind in flydf.index:
                    sleepTime_temp.append(flydf["bout duration"][ind])
                boxSleepTime.append(sleepTime_temp)


            for i in range(len(flies)):
                
                if (activeTotalTime[i] == microTotalTime[i] + walkTotalTime[i]) & (inactiveTotalTime[i] == sleepTotalTime[i] + pauseTotalTime[i]):
                    check.append("OK")
                else:
                    check.append("ERROR")

            boutSummary =[totalTime,check,[],
                       numberIB,inactiveTotalTime,inactivePercent,[],
                       number_pauseB,pauseTotalTime,pausePercent,[],
                       number_sleepB,sleepTotalTime,sleepPercent,[],
                       numberAB,activeTotalTime,activePercent,[],
                       number_microB,microTotalTime,microPercent,[],
                       number_walkB,walkTotalTime,walkPercent]
            boutSummaryDF = pd.DataFrame(boutSummary, columns = flies, index = ["Total time","check","","inactive bouts #", "Total inactive time [s]", "% inactive time","",
                                                                                    "pause bouts #","Total pause time [s]", "% pause time","",
                                                                                    "sleep bouts #","Total sleep time [s]", "% sleep time","",
                                                                                    "active bouts #"," Total active time [s]", "% inactive time","",
                                                                                    "micro bouts #","Total micro time [s]", "% micro time","",
                                                                                    "walk bouts #","Total walk time [s]", "% walk time",
                                                                       ])
            boutSummaryDF.to_csv(newname11)
            expTime= max(totalTime)
            
            if len(qualitycheck)== 0:
                print("quality check OK")
            else:
                for i in qualitycheck:
                    print(i + " quality check ERROR")

            print("making graphs")
####################                           grafico ACTIVE  bouts
            
##            plt.figure(figsize=(9,alto*2))
##            for j in range(2,numberofgraphs+2):
##                plt.subplot(numberofgraphs,1,j-1)
##                plt.title(speedDF.columns[j], loc="right", pad="-15")
##                a = str(10/10) #reemplazar el primer 10 por selectFrame
##                if pxTomm == 1:
##                    plt.xlabel("px")
##                else:   
##                    plt.xlabel("mm")
##                plt.suptitle(a)
##         
##                plt.hist(boxDistance[j-2], bins="sqrt")
##                plt.xlim(left=0)      
##            plt.title("active bout distance histogram",fontsize=10)
##            plt.tight_layout() 
##            plt.savefig("histogram.png")
            
            plt.figure(figsize=(10,14)) #ancho,alto
            plt.subplot(3,3,1)
            plt.barh(flies, numberAB,color='gray')
            Nmin,Nmax = plt.xlim()
            
            plt.title("active - N_bouts",fontsize=10)

            plt.subplot(3,3,2)
            plt.barh(flies, activeTotalTime,color='gray')
            plt.title("active - total time",fontsize=10)
            plt.xlim(left= 0,right=expTime)
            plt.xlabel("sec")

            plt.subplot(3,3,3)
            plt.boxplot(boxDistance,vert=False,flierprops=dict(markersize=2),labels=flies)
            if pxTomm == 1:
                plt.xlabel("px")
            else:
                plt.xlabel("mm")
            plt.xscale("log")
            xmin,xmax = plt.xlim()
            bottom, top = plt.ylim()
            plt.vlines(quiescent_threshold, ymin= bottom, ymax= top,color='r', linestyles='--', alpha=0.5) 
            plt.title("active bout distance",fontsize=10)
            
            plt.subplot(3,3,4)
            plt.barh(flies, number_microB,color='coral')
            plt.xlim(0,Nmax)
            plt.title("micromovement - N_bouts",fontsize=10)

            plt.subplot(3,3,5)
            plt.barh(flies, microTotalTime,color='coral')
            plt.title("micromovement - total time",fontsize=10)
            plt.xlim(left= 0,right=expTime)
            plt.xlabel("sec")

            plt.subplot(3,3,6)
            plt.boxplot(boxMicromovement,vert=False,flierprops=dict(markersize=2),labels=flies)
            if pxTomm == 1:
                plt.xlabel("px")
            else:
                plt.xlabel("mm")
            plt.xscale("log")
            plt.xlim(xmin,xmax)
            #bottom, top = plt.ylim()
            plt.vlines(quiescent_threshold, ymin= bottom, ymax= top,color='r', linestyles='--', alpha=0.5) 
            plt.title("micromovement bout distance",fontsize=10)

            plt.subplot(3,3,7)
            plt.barh(flies, number_walkB,color='yellowgreen')
            plt.xlim(0,Nmax)
            plt.title("walk - N_bouts",fontsize=10)

            plt.subplot(3,3,8)
            plt.barh(flies, walkTotalTime,color='yellowgreen')
            plt.title("walk - total time",fontsize=10)
            plt.xlim(left= 0,right=expTime)

            plt.subplot(3,3,9)
            plt.boxplot(boxWalking,vert=False,flierprops=dict(markersize=2),labels=flies)
            if pxTomm == 1:
                plt.xlabel("px")
            else:
                plt.xlabel("mm")
            plt.xscale("log")
            #bottom, top = plt.ylim()
            plt.xlim(xmin,xmax)
            plt.vlines(quiescent_threshold, ymin= bottom, ymax= top,color='r', linestyles='--', alpha=0.5) 
            plt.title("walk bout distance",fontsize=10)
            

##            plt.subplot(4,2,3)
##            plt.boxplot(boxDuration,vert=False,flierprops=dict(markersize=2),labels=flies)
##            plt.xlabel("sec")
##            plt.xscale("log")
##            plt.title("active bout duration",fontsize=10)

##            maxXavg = max([item for list in boxAvg for item in list])
##            maxXmedian = max([item for list in boxMedian for item in list])
##            maxXval= [maxXavg,maxXmedian]
##            maxXvalue = max(maxXval)
##            
##            maxXvalue = int(maxXvalue/10)*10 + 10
            
##            plt.subplot(4,2,5)
##            plt.boxplot(boxAvg,vert=False,flierprops=dict(markersize=2),labels=flies)
##            if pxTomm == 1:
##                plt.xlabel("px/sec")
##            else:
##                plt.xlabel("mm/sec")
##            plt.xlim(right = maxXvalue)
##            plt.title("active bout Avg speed",fontsize=10)

##            plt.subplot(4,2,6)
##            plt.boxplot(boxMedian,vert=False,flierprops=dict(markersize=2),labels=flies)
##            if pxTomm == 1:
##                plt.xlabel("px/sec")
##            else:
##                plt.xlabel("mm/sec")
##            plt.title("active bout Median speed",fontsize=10)
##            plt.xlim(right = maxXvalue)
            
##            plt.subplot(4,2,7)
##            plt.barh(flies, numberIB)
##            plt.title("# inactive bouts",fontsize=10)
##
 
##
##            maxAxis = max([item for list in boxDurationIB for item in list])
##            maxAxis = int(maxAxis/10)*10 + 10
##            #plt.xlim(right = maxXvalue)
##            plt.xlim(right = maxAxis)
            
                           
            plt.tight_layout()
            plt.savefig(newname8)

#############################                           grafico INACTIVE bouts

            plt.figure(figsize=(10,14)) #ancho,alto
            plt.subplot(3,3,1)
            plt.barh(flies, numberIB,color='gray')
            xmin,xmax = plt.xlim()
            plt.title("inactive - N_bouts",fontsize=10)

            plt.subplot(3,3,2)
            plt.barh(flies, inactiveTotalTime,color='gray')
            plt.title("inactive - total time",fontsize=10)
            plt.xlim(left= 0,right=expTime)
            plt.xlabel("sec")

            plt.subplot(3,3,3)
            plt.boxplot(boxDurationIB,vert=False,flierprops=dict(markersize=2),labels=flies)
            plt.xlabel("sec")
            plt.xscale("log")
            plt.title("inactive bout duration",fontsize=10)
            xmin,xmax = plt.xlim()
            bottom, top = plt.ylim()
            plt.vlines(sleep_threshold, ymin= bottom, ymax= top,color='r', linestyles='--', alpha=0.5)
            
            plt.subplot(3,3,4)
            plt.barh(flies, number_pauseB,color='coral')
            plt.xlim(0,Nmax)
            plt.title("pause - N_bouts",fontsize=10)

            plt.subplot(3,3,5)
            plt.barh(flies, pauseTotalTime,color='coral')
            plt.title("pause - total time",fontsize=10)
            plt.xlim(left= 0,right=expTime)
            plt.xlabel("sec")

            plt.subplot(3,3,6)
            plt.boxplot(boxPauseTime,vert=False,flierprops=dict(markersize=2),labels=flies)
            plt.xlabel("sec")
            plt.xscale("log")
            plt.title("pause bout duration",fontsize=10)
            plt.xlim(xmin,xmax)
            plt.vlines(sleep_threshold, ymin= bottom, ymax= top,color='r', linestyles='--', alpha=0.5) 
            

            plt.subplot(3,3,7)
            plt.barh(flies, number_sleepB,color='yellowgreen')
            if (Nmax - max(number_sleepB) < 200):
                plt.xlim(0,Nmax)
            plt.title("sleep - N_bouts",fontsize=10)

            plt.subplot(3,3,8)
            plt.barh(flies, sleepTotalTime,color='yellowgreen')
            plt.title("sleep - total time",fontsize=10)
            plt.xlim(left= 0,right=expTime)

            plt.subplot(3,3,9)
            plt.boxplot(boxSleepTime, vert=False,flierprops=dict(markersize=2),labels=flies)
            plt.xlabel("sec")
            plt.xscale("log")
            plt.title("sleep bout duration",fontsize=10)
            plt.xlim(xmin,xmax)
            plt.vlines(sleep_threshold, ymin= bottom, ymax= top,color='r', linestyles='--', alpha=0.5)           
                           
            plt.tight_layout()
            plt.savefig(newname9)



##            print("analyzing sleep")
##            plt.figure(figsize=(6,4)) #ancho,alto
##            
##            plt.subplot(1,3,1)
##            plt.barh(flies, sleepTotalTime)
##            plt.xlabel("sec")
##            plt.title("total sleep time",fontsize=10)
##
##            plt.subplot(1,3,2)
##            plt.barh(flies, sleepPercent)
##            plt.xlabel("percent")
##            plt.title("% time sleeping",fontsize=10)
##                                        
##            plt.subplot(1,3,3)
##            plt.boxplot(boxSleepTime,vert=False,flierprops=dict(markersize=2),labels=flies)
##            plt.xlabel("sec")
##            plt.title("sleep bout duration",fontsize=10)
##            plt.xlim(left = 500)
##            
##            plt.tight_layout()
##            
##            plt.savefig(newname10)
            #plt.show()
            print("----- Analysis completed -----")
            



if __name__ == "__main__":
    data =  "foo"
    path = os.path.dirname(os.path.abspath(__file__))
    toSpeed(path, data)
