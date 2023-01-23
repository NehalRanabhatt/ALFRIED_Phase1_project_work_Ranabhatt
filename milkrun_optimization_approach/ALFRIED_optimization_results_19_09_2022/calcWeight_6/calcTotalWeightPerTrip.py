"""
Created on Sun Sep 18 20:29:43 2022

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
                        orderFileWeightDict[line[-1]] = float(line[-4])
                    else:
                        print("ERROR duplicate order id", line[0], line[-1])
    header = 0
    with open(tripInfoFile) as source:
        for line in source:
            if header == 0:
                header += 1
            else:
                line = line.rstrip("\n")
                line = line.split("\t")
                print(line)
                orderIds = line[3]
                if line[3] == "":
                    line[3] = line[4] = line[5] = line[6] =line[7] = "0.0"
                    line.append("0.0")
                else:
                    orderIdsList = orderIds.split(",")
                    totalTripWeight = 0
                    for orderId in orderIdsList:
                        totalTripWeight += orderFileWeightDict[orderId]
                        #print(totalTripWeight)
                    line.append(str(totalTripWeight))
                dest.write("\t".join(line))
                dest.write("\n")
    dest.close()
