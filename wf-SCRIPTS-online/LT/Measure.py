#! /usr/bin/python3
from LT.analysisclass import AnalysisClass
import picamera
import time
from LT.controlLED import ControlLED 
import numpy as np

def medir(basePath):
#     basePath = '/home/pi/Desktop/WALKING/'
    print("\n-----DELETE or move to another folder all the files in Desktop\WALKING")
    file = input("\nEnter a name for the output file or press Enter for default name (YearMonthDay_HH-MM): ")
    fecha = time.strftime("%Y%m%d_%H-%M",time.gmtime())
    if len(file) == 0:
        nameOfFile = fecha
        print(f"default name is: {fecha}" )
    else:
        nameOfFile = file 
        
    with picamera.PiCamera() as camera:
        camera.resolution = (1280,960)
        camera.framerate = 10
        camera.vflip = True
        camera.hflip = True
        camera.led = False
        camera.exposure_mode = "auto"
        camera.brightness = 55
        camera.awb_mode = "off"
        camera.awb_gains = (1.5,1.2) #red,blue
        
        output = AnalysisClass(camera, nameOfFile,basePath)
        video = 1
        camera.start_recording(output, splitter_port=2, format='bgr')
        
        time1=time.time()
        for filename in camera.record_sequence(( 
            (basePath + nameOfFile +"--%05d.h264") % i for i in range(1,25)), bitrate = 1000000 ):
            camera.wait_recording(300)
            print("video" + str(video))
            video += 1
        camera.stop_recording(splitter_port=2)
      
        x=ControlLED()
        x.GPIO_clean()

    #   camera.start_recording(output, splitter_port=2, format='bgr')
        
    camera.close()
    #         camera.stop_recording()
    # fin = np.full((38,50,3),200,dtype=np.uint8)
    # output.analyse(fin)      


    t = time.time()-time1
    if t < 60:
        print("tiempo total: " + str(t) + " seg.")
    elif t >= 60 and t < 3600:
        print("tiempo total: " + str(t/60) + " min")
    elif t >= 3600:
        print("tiempo total: " + str(t//3600) + " hr " + str((t%3600//60)) + " min")      
            
#     outputFile = nameOfFile + ".csv"
#     return outputFile
    return nameOfFile

if __name__ == "__main__":
    medir()
