#!/usr/bin/env python3
from LT.Measure import medir
import LT.outputTOspeed_V2 as op
import cv2
import os
import LT.convert as convert
import sys

basePath = '/home/pi/Desktop/WALKING/'
if not os.path.exists(basePath):
    os.mkdir(basePath)
os.chown(basePath, 1000, 1000)

outputFile = medir(basePath)
op.toSpeed(basePath, outputFile)
convert.mp4(basePath, outputFile)

sys.exit()
