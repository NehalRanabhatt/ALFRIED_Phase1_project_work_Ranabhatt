# -*- coding: utf-8 -*-
"""
Created on Mon May 23 18:21:14 2022

@author: Ranabhatt

inputFormat("output_19_06_2022_P1p2_with.txt", "output_19_06_2022_P1p2_without.txt","cu_plot_output")
inputFormat("output_08_07_2022_P1p2_with.txt","output_08_07_2022_P1p2_with.txt","trial")
inputFormat("output_08_07_2022_P2p1_with.txt","output_08_07_2022_P2p1_without.txt","cu_plot_08_07_2022")

inputFormat("output_19_09_2022_P2p1_with.txt","output_19_09_2022_P2p1_without.txt","cu_plot_19_09_2022")

"""

from datetime import datetime

def inputFormat(tripCancellationResults, tripDefaultResults, outputFilePrefix):
    dest = open(outputFilePrefix+"_entireWeekResults.csv", "w")
    dest1 = open(outputFilePrefix+"_onlyWorkingDayResults.csv", "w")
    dateCancellationDict = fileToDict(tripCancellationResults)
    dateDefaultDict = fileToDict(tripDefaultResults)
    dest.write("date"+","+"Av_CU_default_trip"+","+"Av_CU_cancelled_trip"+"\n")
    for dateKey in dateDefaultDict:
        dateKeyFormat=datetime.strptime(dateKey,'%Y-%m-%d').date()
        if dateKey in dateCancellationDict:
            dest.write(dateKey+","+str((dateDefaultDict[dateKey][1]/dateDefaultDict[dateKey][0])*100)+","+
                   str((dateCancellationDict[dateKey][1]/dateCancellationDict[dateKey][0])*100)+"\n")
            if dateKeyFormat.weekday() < 5:
                dest1.write(dateKey+","+str((dateDefaultDict[dateKey][1]/dateDefaultDict[dateKey][0])*100)+","+
                   str((dateCancellationDict[dateKey][1]/dateCancellationDict[dateKey][0])*100)+"\n")
        else:
            dest.write(dateKey+","+str((dateDefaultDict[dateKey][1]/dateDefaultDict[dateKey][0])*100)+","+
                   "0"+"\n")
            if dateKeyFormat.weekday() < 5:
                dest1.write(dateKey+","+str((dateDefaultDict[dateKey][1]/dateDefaultDict[dateKey][0])*100)+","+
                   str((dateCancellationDict[dateKey][1]/dateCancellationDict[dateKey][0])*100)+"\n")
    dest.close()
    dest1.close()


def fileToDict(file1):
    dateCancellationDict = {}
    header = 0
    with open(file1) as source:
        for line in source:
            line = line.rstrip().split()
            dateIn = line[0].split(",")[0]
            if header == 0:
                header += 1
            else:
                if dateIn not in dateCancellationDict:
                    dateCancellationDict[dateIn] = [ 0, 0 ]
                if len(line[0].split(",")) == 4:
                    dateCancellationDict[dateIn][1]  += float(line[2])
                dateCancellationDict[dateIn][0]  += 1
    #print(dateCancellationDict)
    return dateCancellationDict
