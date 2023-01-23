# -*- coding: utf-8 -*-
"""
Created on Mon May 23 18:21:14 2022

@author: Ranabhatt

inputFormat("output_19_06_2022_cancelled_trips_info.txt","trip_info_output_18_06_2022.txt","outpt_format_19_06_22")

inputFormat("output_19_06_2022_cancelled_trips_info.txt","trip_input_sep_dec_2021_plus_Jan22_apr22.txt","outpt_format_08_07_22")

inputFormat("output_19_09_2022_cancelled_trips_info.txt","trip_info_output_19_09_2022.txt","outpt_format_19_09_22")
"""

from datetime import datetime

def inputFormat(tripCancellationResults, tripDefaultResults, outputFilePrefix):
    dest = open(outputFilePrefix+"_entireWeekResults.csv", "w")
    dest1 = open(outputFilePrefix+"_onlyWorkingDayResults.csv", "w")
    dateCancellationDict = fileToDict(tripCancellationResults)
    dateDefaultDict = fileToDict(tripDefaultResults)
    #print(dateCancellationDict)
    #print("BREAK BREAK BREAK")
    #print(dateDefaultDict)
    dest.write("date"+","+"Av_CU_default_trip"+","+"Av_CU_cancelled_trip"+"\n")
    for dateKey in dateDefaultDict:
        #print(dateKey)
        dateKeyFormat=datetime.strptime(dateKey,'%Y-%m-%d').date()
        #print(dateKeyFormat)
        if dateKey in dateCancellationDict:
            #print("inside")
            dest.write(dateKey+","+str(dateDefaultDict[dateKey])+","+str(dateCancellationDict[dateKey])+"\n")
            if dateKeyFormat.weekday() < 5:
                dest1.write(dateKey+","+str(dateDefaultDict[dateKey])+","+str(dateCancellationDict[dateKey])+"\n")
        else:
            dest.write(dateKey+","+str(dateDefaultDict[dateKey])+","+"0"+"\n")
            if dateKeyFormat.weekday() < 5:
                dest1.write(dateKey+","+str(dateDefaultDict[dateKey])+","+"0"+"\n")

    dest.close()
    dest1.close()


def fileToDict(file1):
    dateCancellationDict = {}
    #header = 0
    with open(file1) as source:
        for line in source:
            line = line.rstrip().split()
            dateIn = line[0]
            #if header == 0:
            #    header += 1
            #else:
            if dateIn not in dateCancellationDict:
                dateCancellationDict[dateIn] = 0
            dateCancellationDict[dateIn]  += 1
    #print(dateCancellationDict)
    return dateCancellationDict
