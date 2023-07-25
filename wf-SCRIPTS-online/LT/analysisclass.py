#! /usr/bin/env python3

from LT.centroidtracker import CentroidTracker
import picamera.array
import cv2
import time
import imutils
import numpy as np
import pandas as pd
import os
from pathlib import Path
import csv
import sys

# ct = CentroidTracker()


class AnalysisClass(picamera.array.PiRGBAnalysis):
    def __init__(self,camera, nameOfFile,basePath):
        super(AnalysisClass, self).__init__(camera)
        self.frames = 0
        self.start = 0
        self.ct = CentroidTracker()
#         filename = (str(os.path.abspath()) + "/settings.csv")
        filename = (str(Path().absolute()) + "/settings.csv")
        
        condition = os.path.exists(filename)
        if condition == False:
            print("\nRun setupWF first")
            input("\npress any key to quit")
            sys.exit()
            
        f = open(filename,"r")
        reader = csv.reader(f)
        self.default= next(reader)
        for i in range(len(self.default)):
            self.default[i] = int(self.default[i])
        f.close()
#         self.default = valores
#         self.default = [0, 0, 800, 523, 20, 200, 160, 87, 51, 25.0,5,6]
        self.outfile = basePath + nameOfFile + ".csv"
        self.settings = basePath + nameOfFile + ".jpg"
#         print(f"init: {self.default}  {self.outfile}")
            
    def nothing(self,j):
        pass
    

    def analyse(self, array):
        self.frames += 1
#         print(self.frames)
        cv2.namedWindow("Frame")
        cv2.createTrackbar("Show values", "Frame", 1, 1, self.nothing)

        if self.frames == 10:
            self.start += 1
            array = imutils.resize(array, width=800)
            w,h,c = array.shape
            mask1 = np.zeros([w,h,1],dtype=np.uint8)
            Sx = self.default[0]
#             print(type(Sx))
            Sy = self.default[1]
            Ix = self.default[2]
            Iy = self.default[3]
            sizeL = self.default[4]
            sizeU = self.default[5]
            
            x1 = self.default[6]
            y1 = self.default[7]
            
            horizontal = self.default[10]
            vertical = self.default[11]
            for i in range(horizontal):
                vert = Sx + x1*i
                cv2.line(array, (vert,0), (vert,600),(100,100,100), 1)
            for i in range (vertical):
                hor = Sy + y1*i
                cv2.line(array, (0,hor), (800,hor), (100,100,100),1)
                
            tPupa = self.default[8]
            tPupa2 = self.default[9]
            
            mask1[Sy:Iy,Sx:Ix]=255
#             cv2.imshow("firulai", mask1)
            stamp = time.time()
            rects = []
#             time1 = time.time() 

            self.frames = 0
            B,G,R =cv2.split(array)
            channel = B           
            mask = cv2.adaptiveThreshold(channel, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, tPupa, tPupa2)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.bitwise_and(mask,mask,mask=mask1)
        
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
            if len(cnts) > 0:
                indice = 0
                for i in cnts:
                    sup = cv2.contourArea(i)
               
                    if (sup > sizeL and sup < sizeU): # and largo < 150 and ancho > 4) :
                        M = cv2.moments(i)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                                                                    
                        points = (Sx,Sy,x1,y1,horizontal)
                        center=(center,points)
                        
                        rects.append(center)
                    indice = indice + 1
                   
            objects = self.ct.update(rects)
            # loop over the tracked objects
            for (objectID, variables) in objects.items():
                showBar = cv2.getTrackbarPos("Show values", "Frame")
                try:
                    for (well, centroid, speed) in [variables]:
                        text = "{}".format(well)
                        cv2.putText(array, text, (centroid[0] + 10, centroid[1] + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 25, 0), 1)
                        
                        cv2.circle(array, (centroid[0], centroid[1]), 4, (0,255, 255), -1)
                        speed = int(speed*10)
                        speed = float(speed/10)
                        if showBar == 1:
                            text2 = "speed: {}".format(speed)
                            cv2.putText(array, text2, (centroid[0] + 10, centroid[1] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 25, 0), 1)
                            
                           
                except ValueError:
                    print("value error")
            for objectID in list(objects.keys()):
                objects[objectID].append(stamp)
#             
            df = pd.DataFrame.from_dict(objects)
            df = df.T
            
#             if not os.path.isfile("output.csv"):
#                 df.to_csv("output.csv")
#             else:
#                 df.to_csv("output.csv",mode="a", header=False)
            if not os.path.isfile(self.outfile):
                df.to_csv(self.outfile)
            else:
                df.to_csv(self.outfile,mode="a", header=False)                    
                # draw both the ID of the object and the centroid of the
                # object on the output frame
               
            
#             result = cv2.bitwise_and(array,array,mask=mask)
    #             array = cv2.bitwise_and(array,array,mask=mask)
#             final = cv2.hconcat([array,result])
#             showMask = cv2.getTrackbarPos("Show mask", "Trackbars")
#             if showMask == 1: 
#                 result = cv2.bitwise_and(array,array,mask=mask)
#                 cv2.imshow("Mask", result)
#             else:
#                 cv2.destroyWindow("Mask")
    
            array = cv2.bitwise_and(array,array,mask=mask1)
            cv2.imshow("Frame",array)
            if self.start == 5:
                cv2.imwrite(self.settings, array)
#             cv2.imshow("G",G)
#             cv2.imshow("Gcorr",Gcorr)
#             cv2.imshow("B",B)
        
    #             mask = cv2.bitwise_and(mask,mask,mask=mask)
    #             cv2.imshow("F",final)

        cv2.waitKey(1) & 0xFF
           
#             cv2.destroyAllWindows()
