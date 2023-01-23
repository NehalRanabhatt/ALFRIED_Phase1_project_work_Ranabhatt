# -*- coding: utf-8 -*-
"""
Created on Mon Apr  11 16:52:39 2022

@author: Ranabhatt
"""

import pandas as pd
import sys
from os import listdir, walk, path
import yaml
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# logi = 9.471631
# lati = 47.659462

plant_2 = Polygon([(9.471631,47.659462),(9.475021,47.664665),(9.468155,47.666572),(9.463477,47.665387),(9.462404,47.662988),(9.464722,47.66004),(9.471631,47.659462)])
plant_1 = Polygon([(9.485128,47.657424),(9.48796,47.659636),(9.491866,47.661471),(9.495406,47.659809),(9.486909,47.656167),(9.485128,47.657424)])

class CalculateTrips:

    def __init__(self,yamlInput):
        self.yamlInput = yamlInput
        self.lastRecordDict = {"timeStamp":"NA","plant":"NA"}


    def readYaml(self):
        stream = open(self.yamlInput, 'r')
        dictionary = yaml.safe_load(stream)
        rootDir = dictionary["root"]
        dest = open(dictionary["ordersCalculationOutput"],"w")
        startDate = dictionary["startDate"].split("-")
        endDate = dictionary["endDate"].split("-")
        startDate = datetime(day=int(startDate[2]),month=int(startDate[1]),year=int(startDate[0]))
        endDate = datetime(day=int(endDate[2]),month=int(endDate[1]),year=int(endDate[0]))
        dest.write("P2_start"+"\t"+"P1_end"+"\t"+"P1_start"+"\t"+"P2_end"+"\n")
        for root, subdirs, files in walk(str(rootDir)):
            for dirs in subdirs:
                dirs = str(dirs).split("-")
                dateFolderName = datetime(day=int(dirs[2]),month=int(dirs[1]),year=int(dirs[0]))
                if startDate<=dateFolderName<=endDate:
                    print(startDate, endDate, dateFolderName)
                    dirs= "-".join(dirs)
                    rootDirs = path.join(str(rootDir),dirs)
                    onlyFiles = [f for f in listdir(rootDirs) if path.isfile(path.join(rootDirs, f))]
                    if len(onlyFiles)>1:
                        print("only one file is expected, two files found ", rootDirs)
                        sys.exit(1)
                    else:
                        rootDirsFile = path.join(rootDirs, onlyFiles[0])
                        tmpDf = self.compressedFileToDf(rootDirsFile)
                        #self.tmpFile = tempfile.TemporaryFile(mode="r+")
                        tmpDf.to_csv("sortedFile.txt", index=False, sep="|",doublequote=False)
                        dayTripList = self.calculateTrips("sortedFile.txt")
                        if len(dayTripList)==0:
                            print("WARNING: No trip exists to either plant p1 or plant p2", rootDirsFile)
                        else:
                            for dayTrip in dayTripList:
                                dayTrip=list(map(str,dayTrip))
                                dest.write("\t".join(dayTrip)+"\n")
        dest.close()

    def calculateTrips(self, inputFile):
        header = 0
        tripStart = "NA"
        sampleIndex = "NA"
        currentTripStartTime = "NA"
        dayTripList= []
        tmpList = []
        with open(inputFile) as source:
            for line in source:
                if header == 0:
                    header += 1
                else:
                    record = line.strip().split("|")
                    #timeStampT = (int(record[3])+int(record[4]))/1000000
                    #timeStampT = datetime.fromtimestamp(timeStampT)
                    timeStampT = record[3]
                    if record[7] == "lat":
                        lati = float(record[8])
                        sampleIndex = record[4]
                    if record[7] == "lon" and sampleIndex == record[4]:
                        longi = float(record[8])
                        positionTruck = Point(longi,lati)
                        if plant_2.contains(positionTruck):
                            if tripStart == "NA" :
                                tmpList = []
                                tripStart = "P2"
                                signalOut = self.checkBoundaryCondition(tripStart)
                                if signalOut=="1":
                                    tmpList = [" "," ",self.lastRecordDict["timeStamp"],timeStampT]
                                    dayTripList.append(tmpList[:])
                                    del tmpList[:]
                            elif tripStart == "P1":
                                tmpList.append(currentTripStartTime)
                                tmpList.append(timeStampT)
                                dayTripList.append(tmpList[:])
                                del tmpList[:]
                                tripStart = "P2"
                            currentTripStartTime = timeStampT
                            self.lastRecordDict["timeStamp"] = timeStampT
                            self.lastRecordDict["plant"] = tripStart
                        if plant_1.contains(positionTruck):
                            if tripStart == "P2" :
                                tmpList.append(currentTripStartTime)
                                tmpList.append(timeStampT)
                                tripStart = "P1"
                            elif tripStart == "NA":
                                currentTripStartTime = timeStampT
                                tripStart = "P1"
                                tmpList = [" "," "]
                                signalOut = self.checkBoundaryCondition(tripStart)
                                if signalOut=="1":
                                    tmpList = [self.lastRecordDict["timeStamp"],timeStampT," "," "]
                                    dayTripList.append(tmpList[:])
                                    del tmpList[:]
                            currentTripStartTime = timeStampT
                            self.lastRecordDict["timeStamp"] = timeStampT
                            self.lastRecordDict["plant"] = tripStart
            if len(tmpList)>0:
                tmpList.append(" ")
                tmpList.append(" ")
                dayTripList.append(tmpList[:])
                del tmpList[:]
            return dayTripList

    def checkBoundaryCondition(self,tripStart):
        if self.lastRecordDict["timeStamp"]!= "NA":
            if self.lastRecordDict["plant"]!= tripStart:
                return "1"
            else:
                return "0"
        else:
            return "0"

    def compressedFileToDf(self,inFile):
        df = pd.read_csv(inFile,sep="|",header=0)
        print(df)
        df["ts_msg_usec"] = df["ts_msg_usec"]/1000000
        df['ts_msg_usec'] = pd.to_datetime(df['ts_msg_usec'],unit='s').dt.tz_localize('UTC').dt.tz_convert('Europe/Paris').dt.strftime('%Y-%m-%d %H:%M:%S')
        df = df.sort_values(by='ts_msg_usec', ascending=True)
        return df

if __name__=="__main__":
    CALCULATE_TRIPS = CalculateTrips("tripCalculation.yaml")
    CALCULATE_TRIPS.readYaml()
