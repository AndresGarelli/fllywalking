#! /usr/bin/env python3
import subprocess
import time
from pathlib import Path
import os

def mp4(basePath, nameOfFile):
    ffmpeg = "/usr/bin/ffmpeg"
    ##ffmpeg = "C:/ffmpeg/bin/ffmpeg.exe"

    text = "drawtext=text='" + nameOfFile + "':fontcolor=white:boxcolor=black:fontsize=30:x=(w-text_w)/2:y=(h-30)" 
#     text = "drawtext=text='feo':fontcolor=white:fontsize=20:x=(w-text_w)/2:y=(h/2)" 
    
    
#     mypath = str(Path().absolute()) + "/"
    mypath = basePath + "/"
    a= os.listdir(mypath)
    with open(mypath + "mylistH264.txt", "w+") as f:
        for i in a:
            if i.endswith(".h264"):
##                f.write("file '%s'\n" %i)
                f.write(f"file '{i}'\n")
    f.close()
    path = mypath + "mylistH264.txt"
    outputh264 = mypath + "output.h264"
    nameOfFilemp4 = mypath + nameOfFile + ".mp4"
#     print(path)
  
#     command1 = ["for i in `ls ",mypath,"*.h264 | sort -V`; do echo ""file $i""; done >> mylistH264.txt"]
    command1= [ffmpeg, "-f", "concat", "-i", path , "-c", "copy", outputh264]
    command2= [ffmpeg, "-framerate", "10", "-i", outputh264, "-c:v", "libx264", "-preset", "fast", "-crf",
               "25", "-vf", text, "-c:a", "copy", nameOfFilemp4,"-y"]
    print("\n-----Converting to .mp4-----")
    print("\n   ->Running step 1 of 2")
    time.sleep(2)
    codigo = subprocess.run(command1, shell = False).returncode
    if codigo == 0:
        print("\n Step 1 completed")
        print("\n   ->Running step 2 of 2")
        time.sleep(2)
        codigo = subprocess.run(command2, shell = False).returncode
        if codigo == 0:
            print ("\nStep 2 of 2 completed")
            time.sleep(3)
        else:
            print ("\nThere was an error in step2")
            input("press any key to quit")
    
    else:
        print("\nThere was an error in step 1")
    os.remove(path)
    os.remove(mypath + "output.h264")

if __name__ == "__main__":
    basePath = '/home/pi/Desktop/WALKING/'
    nameOfFile = time.strftime("%Y%m%d",time.gmtime())
    mp4(basePath, nameOfFile)
