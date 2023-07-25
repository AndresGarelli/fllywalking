#!/usr/bin/env python3
# from LT.analysisclass import AnalysisClass
from LT.centroidtracker import CentroidTracker
import picamera
import picamera.array
import time
# import argparse
from LT.controlLED import ControlLED 
import cv2
import os
import numpy as np
import csv


def nothing(x):
    pass

def setup():
    print("Set values with sliders and press Enter")
    name = "Press Enter when values are set"
    cv2.namedWindow(name)

    cv2.createTrackbar("#wells-Hor", name, 5,10,nothing)
    cv2.createTrackbar("#wells-Vert", name, 6,10,nothing)

    cv2.createTrackbar("size L", name, 20, 500, nothing)
    cv2.createTrackbar("size U", name, 200, 2000, nothing)
    cv2.createTrackbar("threshold", name, 50, 255, nothing)
    cv2.createTrackbar("C", name, 25, 40, nothing)
    cv2.createTrackbar("Show values", name, 1, 1, nothing)
    cv2.createTrackbar("Show mask", name, 0, 1, nothing)

    cv2.createTrackbar("Top", name, 0,600, nothing)
    cv2.createTrackbar("Bottom", name, 523,600, nothing)
    cv2.createTrackbar("Left", name, 0,800, nothing)
    cv2.createTrackbar("Right", name, 800,800, nothing)


    camera = picamera.PiCamera()
    camera.resolution = (800,608)
    camera.vflip = True
    camera.hflip = True
    camera.framerate = 10
    rawCapture = picamera.array.PiRGBArray(camera, size=(800,608))
    camera.exposure_mode = "auto"
#     camera.awb_mode = "auto"
    camera.brightness = 55
#     time.sleep(1)
    camera.awb_mode = "off"
    camera.awb_gains = (1.5, 1.2)

    ct = CentroidTracker()

    frames = 0
    for cuadro in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frames += 1
        if frames == 10:
            frames = 0
            frame = cuadro.array
            B,G,R =cv2.split(frame)
            channel = B
            w,h,c = frame.shape
            mask1 = np.zeros([w,h,1],dtype=np.uint8)
            Sx = cv2.getTrackbarPos("Left", name)
            Sy = cv2.getTrackbarPos("Top", name)
            Ix = cv2.getTrackbarPos("Right", name)
            Iy = cv2.getTrackbarPos("Bottom", name)
            
            mask1[Sy:Iy,Sx:Ix]=255

            sizeL = cv2.getTrackbarPos("size L", name)
            sizeU = cv2.getTrackbarPos("size U", name)

            vertical = cv2.getTrackbarPos("#wells-Vert",name)
            if vertical == 0:
                vertical =1
            horizontal = cv2.getTrackbarPos("#wells-Hor",name)
            if horizontal ==0:
                horizontal = 1
                
            x1 = int((Ix-Sx)/horizontal)
            y1 = int((Iy-Sy)/vertical)

            for i in range(horizontal):
                vert = Sx + x1*i
                cv2.line(frame, (vert,0), (vert,608),(100,100,100), 1)
            for i in range (vertical):
                hor = Sy + y1*i
                cv2.line(frame, (0,hor), (800,hor), (100,100,100),1)

            tPupa = cv2.getTrackbarPos("threshold",name)
            if tPupa%2 ==0:
                tPupa = tPupa +1
            tPupa2 = cv2.getTrackbarPos("C",name)

            mask = cv2.adaptiveThreshold(channel, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, tPupa, tPupa2)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.bitwise_and(mask,mask,mask=mask1)

            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
            rects = []
            if len(cnts) > 0:
                indice = 0
                for i in cnts:
                    sup = cv2.contourArea(i)
                  
                    if (sup > sizeL and sup < sizeU): #and largo < 150 and ancho > 4) :
                        M = cv2.moments(i)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                        black = np.zeros([w,h,1],dtype=np.uint8)
                        black = cv2.drawContours(black,cnts,int(indice),(255),-1)
                        points = (Sx,Sy,x1,y1,horizontal)
                        center=(center,points)
                        rects.append(center)

                    indice = indice + 1


            objects = ct.update(rects)
        #         print(objects)
            # loop over the tracked objects
            
            for (objectID, variables) in objects.items():
            # draw both the ID of the object and the centroid of the
            # object on the output frame}

                showBar = cv2.getTrackbarPos("Show values", name)
                
                try:
                    for (well, centroid, speed) in [variables]:
                        text = "{}".format(well)
                        cv2.putText(frame, text, (centroid[0] + 10, centroid[1] + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 25, 0), 1)
                        
                        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 255), -1)
                        speed = int(speed*10)
                        speed = float(speed/10)
                        if showBar == 1:
                            text2 = "speed: {}".format(speed)
                            cv2.putText(frame, text2, (centroid[0] + 10, centroid[1] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 25, 0), 1)
                            
                           
                except ValueError:
                    print("value error")

                               
            frame = cv2.bitwise_and(frame,frame,mask=mask1)
            cv2.imshow("Frame", frame)

            showMask = cv2.getTrackbarPos("Show mask", name)
            if showMask == 1:
                result = cv2.bitwise_and(frame,frame,mask=mask)
                cv2.imshow("Mask",result)
            else:
                bb = cv2.getWindowProperty("Mask", cv2.WND_PROP_VISIBLE)
                if bb==1:
                    cv2.destroyWindow("Mask")
                

            key = cv2.waitKey(1) & 0xFF
                # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break
            elif key == 13:
                break
            ##        cv2.destroyAllWindows()
                
        
        rawCapture.truncate(0)
#     camera.release()
    camera.close()

    
    a = (Sx,Sy,Ix,Iy,sizeL,sizeU,x1,y1,tPupa,tPupa2, horizontal,vertical)
#     print("valores: " + str(a)[1:-1] )
    cv2.destroyAllWindows()
#     with open("settings.txt", "w+") as f:
#         for items in a:
#             f.write("%s " %items)
#     f.close()

    with open("settings.csv", "w+") as g:
        write = csv.writer(g)
        write.writerow(a)
    g.close()
    
    
if __name__ == "__main__":
    setup()


      
