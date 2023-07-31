#! /usr/bin/env python3
# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import threading
import numpy as np


###en este, la ID es dada por well y no por next object ID

class CentroidTracker():
    def __init__(self, maxDisappeared=0, thresholdValue=1200):
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
##        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.speed = OrderedDict()
        self.well = OrderedDict()
        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.maxDisappeared = maxDisappeared
        self.thresholdValue = thresholdValue
       
        
        
    def register(self, centroid,area):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.objects[area] = centroid
        self.disappeared[area] = 0
        self.speed[area] = 0
        self.well[area] = area
        
##        self.nextObjectID += 1
        
    def deregister(self, objectID):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[objectID]
        del self.disappeared[objectID]
        del self.speed[objectID]
        del self.well[objectID]
    
    def createList(self, well, objects, speed):
        list_tracking = [well, objects, speed]
        self.final = {}
        for i in list_tracking:
            for k in i:
                if not k in self.final:
                    self.final[k]=[]
                self.final[k].append(i[k])
        return self.final
    
    
    def defineWell(self,centroid,points):

        Sx,Sy,x1,y1,horizontal = points

        normX = centroid[0]-Sx
        normY = centroid[1]-Sy

        self.area = int(normX/x1)+int(normY/y1)*horizontal
       
        return self.area
    
    
    def update(self, rects):
        # check to see if the list of input bounding box rectangles
        # is empty
        if len(rects) == 0:
            # loop over any existing tracked objects and mark them
            # as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            self.createList(self.well, self.objects, self.speed)
            return self.final

##################

##        acá calcular la velocidad como la distancia entre
##        el centroide actual y el anterior.

#################################


        # initialize an array of input centroids for the current frame
        inputCentroids = np.zeros((len(rects), 2), dtype="int")
##        inputIntensidad = np.zeros((len(rects), 1), dtype="int")
##        inputAR = np.zeros((len(rects), 1), dtype="float")
        # loop over the bounding box rectangles
        for (i, ((cX, cY),(Sx,Sy,x1,y1,horizontal))) in enumerate(rects):
            inputCentroids[i] = (cX, cY)

            points = Sx,Sy,x1,y1,horizontal

        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                area1 = self.defineWell(inputCentroids[i],points)
                self.register(inputCentroids[i],area1)

        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            
        ###########    define el area para un centroide,busca el centroide existente para ese area y calcula la distancia
            #######    asigna el nuevo centroide y resetea el valor de disappeared.

        ######  PARA LLEVAR REGISTRO DE CENTROIDES NUEVOS, DEBERIA CALCULAR ANTES LAS AREAS OCUPADAS E IR BORRANDO UNA A UNA
            ## SI QUEDAN AREAS SIN BORRAR O HAY MÁS AREAS, HAY QUE REGISTRAR O DEREGISTRAR.
            occupiedWells = list(self.objects.keys())
            occupiedWells2 = list(self.well.values())

            for i in range(len(inputCentroids)):
                area = self.defineWell(inputCentroids[i],points)
                if area in occupiedWells:
                    objectID = area
                    prevCentroid = self.objects[area]
                    speed = dist.euclidean(prevCentroid,inputCentroids[i])
                    if speed <=1.5:
                        speed = 0
                    self.objects[objectID] = inputCentroids[i]
                    self.well[objectID] = area
                    self.speed[objectID] = speed
                    self.disappeared[objectID] = 0
                    occupiedWells.remove(area)
                else:
                    self.register(inputCentroids[i],area)
                

            if len(occupiedWells) > 0:
                for i in range(len(occupiedWells)):
                    objectID = occupiedWells[i]
                    self.disappeared[objectID] += 1
                    self.speed[objectID] = -1
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)
                


        # return the set of trackable objects
        self.createList(self.well, self.objects, self.speed)
        return self.final
