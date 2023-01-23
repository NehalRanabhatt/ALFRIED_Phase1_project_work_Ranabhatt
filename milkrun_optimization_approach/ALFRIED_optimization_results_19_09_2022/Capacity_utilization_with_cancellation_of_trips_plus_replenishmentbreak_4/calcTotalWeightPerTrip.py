# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 20:29:43 2022

@author: Ranabhatt
"""

def calculateWeightBasedCu(orderFile,tripInfoFile,outFile):
    dest = open(outFile, "w")
    orderFileWeightDict = {}
    header = 0
    with open(orderFile) as source:
        for line in source:
            if header == 0:
                header += 1
            else:
                line = line.rstrip()
                line = line.split("\t")
                if len(line) != 29:
                    print("ERROR the total field not equal to 29 ",str(len(line)))
                else:
                    if line[-1] not in orderFileWeightDict:
                        orderFileWeightDict[line[-1]] = float(-4)
                    else:
                        print("ERROR duplicate order id", line[0], line[-1])
    header = 0
    with open(tripInfoFile) as source:
        for line in source:
            if header == 0:
                header += 1
            else:
                print(line)
                line = line.split()
                print(len(line))
                orderIds = line[3]
                orderIdsList = orderIds.split(",")
                totalTripWeight = 0
                for orderId in orderIdsList:
                    totalTripWeight += orderFileWeightDict[orderId]
                    line.append(str(totalTripWeight))
                dest.write("\t".join(line))
                dest.write("\n")
    dest.close()
