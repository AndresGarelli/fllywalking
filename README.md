# flywalking
scripts to monitor fly walking behavior in Raspberry Pi

Brief description of the script to acquire images

Flies are individually placed in rectangular wells sized 20x10 mm at the top, 16x6 mm at the bottom and 4mm deep arranged in a 5x6 array. The well at the top-left corner is considered well0 and on the bottom-right corner well29. The fly is given the same ID number as the well.
Videos are acquired using a camera attached to a Raspberry Pi single board computer with a 1280x960 pixel resolution at 10 frames per second during two hours and saved in 5 minute long fragments in .h264 format.
One every ten frames (i.e. 1 frame per second) is analyzed for fly detection. The frame is resized to 800x600 px, split in R, G and B channels and the Blue channel further processed to extract the contour of the fly from the background. At 800x600, and if the arena is placed at the usual distance, 74px equal 10mm (73.7 +/-2.6, depending on the position of the well within the arena and measurement error. Done on one frame, 16 measurements). Size of a fly is 16.5+/-0.9 px (n=15) or 2.23 +/-0.12 mm. These are approximate values that can vary between experiments if the arena is not placed exactly at the same distance of the camera. I believe the error will not be large. Just a gut feeling.
The (x,y) coordinates of the  centroid of the countour of each fly is saved as the current position value. The position is mapped to a particular well in the arena and used to calculate the speed as the Euclidean difference with the position of the fly detected in the same well in the preceding frame. This assumes that the fly has moved in a straight line. The first time a fly is detected, it is assigned a speed value of 0. In the case a fly is not detected for a certain amount of time, independently of its duration, the next time it is detected is given the same ID and an initial speed of 0.
The calculation of the centroid is influenced by the shape of the detected object and can vary if, for example, the fly extends one wing even though the fly has not changed its position. To eliminate this source of variability, differences in position smaller than 1.5 px were considered as 0.
The well, (x,y) coordinates, speed and a unix timestamp of each fly at each frame is saved in an output file.
Recording stops after 2 hours and the output file is processed to calculate the speed of each fly, the average speed, total walked distance, the percentage of time walking, the percentage of frames in which a fly was not detected and the activity bouts.
Finally, the 24 .h264 files are concatenated in one single file in mp4 format.

The resulting information is organized in four files (in version V2):
-	output.csv
Columns contain the flyID (it may change during the analysis, this information is not used), well, position as (x,y) coordinates, speed, timestamp. Seed value is -1 if a fly is not detected
-	output-speed.csv
Columns contain the timestamp, timeDifference, and the seed of each individual fly. TimeDifference is calculated as the substract of the timestamps and is expected to equal 1 if the video was recorded at 10fps and one every ten frames was analyzed. As before, a speed value of -1 means that the fly was not detected.

-	output-summary.csv
It contains statistical parameters and other variables calculated from the output-speed.csv file. These are speed avg, speed-std, walked pixels, total, count>0, count0, count-1, %walking, %still, error and are calculated as follows:
•	speed avg: the mean of speed values >0 (excludes frames in which flies were not detected nor changed position)
•	speed-std: the standard deviation of the speed values >0
•	pixels travelled: is the sum of speed values >0, because the speed is the distance in px covered in one second. 
•	total: number of frames analyzed.
•	count>0: number of frames with speed >0
•	count0: number of frames with speed = 0
•	count-1: number of frames with speed = -1 (no detection)
•	%active: count>0/total
•	%inactive: count0/total
•	error: count-1/total

-	output-boutsRaw.csv 
-	output-boutsSummary.csv (see below)


Active and inactive bouts
Behavior of flies is classified as active whenever speed is >0 and inactive if <0. Active bouts are considered micromovements when the distance covered is under or equal to 50 px (<=50) and walking if it is above that threshold. 50px is 6.76 mm, or 3.03 Xflies.
Periods of inactivity are considered a pause if they last less than 600 seconds (<600) and sleep if equal or larger than that threshold.
The information of this analysis is collected in the file output-boutsRaw.csv. Each row corresponds to one bout and the flyID, type of bout (active/inactive), bout duration, category (micromovement, walking, pause and sleep), bout distance, bout avg speed and bout median speed are displayed in columns.
From this data is calculated the number of each type of bout, the sum of the time of all bouts of each category and the proportion of time spent in each behavior during the experiment. That information is summarized in the file output-boutsSummary.csv. 
