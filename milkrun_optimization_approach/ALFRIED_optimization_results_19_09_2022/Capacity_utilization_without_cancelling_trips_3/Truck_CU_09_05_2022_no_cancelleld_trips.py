# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:59:37 2022

@author: Ranabhatt
"""

# -*- coding: utf-8 -*-
"""
new considerations:
## fill up the containers with orders (don't split the order containers in to the next trip',consider that order into next trip)
## fillup the empty containers only in empty rows (do not mix the filledup and empty containers --> it will increase forkliftman's effort)
## Priority: fillup the container based on latestdelivery time and First priority filled up container and second priority empty containers

next steps:
## give the same results for the 3 months
"""

#self.addTime_dict={"351":[24,0,0],"993":[5,0,0],"301":[5,0,0],"SCAN_P":[4,30,0]}

"""
##assumption
--> priortiy based on latest delivery time
--> new order will start with the new raw
--> empty order will have lower priority than the filled order
--> specific
slot --> 2 orders --> large containers
order 1 --> sixth priority --> 4 Large ---> next trip
order 2 --> seventh priority -->2 Large
[[L,L],[L,L],[L,L],[L,L],[L,L],[2L,2L]]


TruckCU("orders_results_18_0_2022_plus_JIS_orders.txt","truckInfo.txt","02_11_2021_trips_output.txt","output")

TruckCU("orders_results_14_03_2022.txt","truckInfo.txt","02_11_2021_trips_output.txt","output_14_03_2022")

TruckCU("orders_results_09_05_2022.txt","truckInfo.txt","trip_input_sep_dec_2021.txt","output_09_05_2022")

to merge the file row-wise
cat Order_from_P1p2.txt Order_from_P2p1.txt > All_Orders_Available_In_Trip_info.txt

dest1=open(outputPrefix+"_P1p2.csv","w")

dest2=open(outputPrefix+"_P2p1.csv","w")

    dest1.write("tripStart"+","+"tripEnd"+","+"total_orders"+","+"order_ids"+","+"emptyOrderIds"+","+"total_containers"+","+\
                "truck_cu"+","+"total_empty_containers"+","+"small_empty_cont_ids"+\
                    ","+"small_cont_ids"+","+"large_empty_cont_ids"+","+"large_cont_ids"+"\n")
    dest2.write("tripStart"+","+"tripEnd"+","+"total_orders"+","+"order_ids"+","+"emptyOrderIds"+","+"total_containers"+","+\
                "truck_cu"+","+"total_empty_containers"+","+"small_empty_cont_ids"+\
                    ","+"small_cont_ids"+","+"large_empty_cont_ids"+","+"large_cont_ids"+"\n")

dest = open("cancelled_trips_info.txt","w")

dest5 = open("orders_replenishmentBreak_P1P2.txt","w")

dest6 = open("orders_replenishmentBreak_P2P1.txt","w")

TruckCU("orders_results_19_06_2022.txt","truckInfo.txt","trip_info_output_02_Nov.txt","output_19_06_2022")

TruckCU("orders_results_19_06_2022.txt","truckInfo.txt","trip_info_output_18_06_2022.txt","output_19_06_2022")

TruckCU("orders_results_19_06_2022.txt","truckInfo.txt","trip_input_sep_Apr_07_05_2022.txt","output_05_07_2022")

TruckCU("orders_results_19_06_2022.txt","truckInfo.txt","trip_input_sep_dec_2021_plus_Jan22_apr22.txt","output_08_07_2022")

TruckCU("orders_results_19_09_2022.txt","truckInfo.txt","trip_info_output_19_09_2022.txt","output_19_09_2022")


"""
from datetime import datetime, timedelta

def TruckCU(ordersInputFile,conatinerInfoInputFile,DaytripsInputFile,outputPrefix):

    ##process time is 04:30 hr
    ##process time is 01:50 hr
    #flexiblityTime_dict={"351":[22,30,0],"993":[3,30,0],"301":[3,30,0],"SCAN_P":[3,0,0]}
    flexiblityTime_dict={"351":[19,30,0],"993":[0,30,0],"301":[0,30,0],"SCAN_P":[0,0,0]}
    emptyflexiblityTime_dict={"351":[23,30,0],"993":[22,30,0],"301":[21,30,0],"SCAN_P":[21,0,0]}
    containerInfoDict = {} ##read and store the content of "containerInfoInputFile
    filledOrderP2p1 = {}
    filledOrderP1p2 = {}
    tripDictP2p1 = {}
    tripDictP1p2 = {}
    tripDeliveryTimeP1p2 = {}
    tripDeliveryTimeP2p1 = {}
    roundTripDict = {}
    orderTimeDict = {}

    with open(conatinerInfoInputFile) as source:
        for line in source:
            line = line.rstrip().split()
            dictValue = line[1]
            if "," in dictValue:
                dictValue = dictValue.split(",")
            containerInfoDict[line[0]] = dictValue
            #print(containerInfoDict)
    with open(DaytripsInputFile) as source:
        for line in source:
            #print(line)
            line = line.rstrip().split()
            p2StartTimeList=line[1].split(".")[0].split(":")
            #print(p2StartTimeList)
            p2EndTimeList=line[3].split(".")[0].split(":")
            p1StartTimeList=line[5].split(".")[0].split(":")
            p1EndTimeList=line[7].split(".")[0].split(":")
            P2p1TripDateList=line[0].split("/")
            P1p2TripDateList=line[4].split("/")
            p2p1List=[line[1],line[3]]
            p1p2List=[line[5],line[7]]
            #print(p2p1List) #['4:48:59', '4:54:20']
            #print(p1p2List)
            #combined data and time

            p2DateStartTime=datetime(year=int(P2p1TripDateList[0]),month=int(P2p1TripDateList[1]),day=int(P2p1TripDateList[2]),hour=int(p2StartTimeList[0]),minute=int(p2StartTimeList[1]),
                                               second=int(p2StartTimeList[2]))
            #print(p2DateStartTime)
            p2DateEndTime=datetime(year=int(P2p1TripDateList[0]),month=int(P2p1TripDateList[1]),day=int(P2p1TripDateList[2]),hour=int(p2EndTimeList[0]),minute=int(p2EndTimeList[1]),
                                               second=int(p2EndTimeList[2]))
            p1DateStartTime=datetime(year=int(P1p2TripDateList[0]),month=int(P1p2TripDateList[1]),day=int(P1p2TripDateList[2]),hour=int(p1StartTimeList[0]),minute=int(p1StartTimeList[1]),
                                               second=int(p1StartTimeList[2]))
            p1DateEndTime=datetime(year=int(P1p2TripDateList[0]),month=int(P1p2TripDateList[1]),day=int(P1p2TripDateList[2]),hour=int(p1EndTimeList[0]),minute=int(p1EndTimeList[1]),
                                               second=int(p1EndTimeList[2]))
            p2p1List=[p2DateStartTime,p2DateEndTime]
            p1p2List=[p1DateStartTime,p1DateEndTime]

            roundTripDict[str(p2DateStartTime)+" "+str(p2DateEndTime)] = str(p1DateStartTime)+" "+str(p1DateEndTime)

            #print(p1p2List)
            #print(p2p1List)


            ##these dates will be set as key to compare with the order date
            dateP2p1=datetime.strptime(line[0],'%Y/%m/%d').date() # p2 start
            #print("dateP2p1",dateP2p1)
            dateP1p2=datetime.strptime(line[4],'%Y/%m/%d').date() # p1 start
            ###print(str(dateP2p1) + "\t"+ str(dateP1p2))

            #add date and time
            #tripDictContainer--> future output storage
            if dateP2p1 not in filledOrderP2p1:
                filledOrderP2p1[dateP2p1]=[]
                filledOrderP2p1[dateP2p1].append({})#  {datetime.date(2021, 11, 2): [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}], datetime.date(2021, 11, 3): [{}]}
                #print("filledOrderP2p1" , filledOrderP2p1)
                tripDictP2p1[dateP2p1]=[]
                tripDictP2p1[dateP2p1].append(p2p1List)
                #print("tripDictP2p1", tripDictP2p1)
            else:
                tripDictP2p1[dateP2p1].append(p2p1List)
                filledOrderP2p1[dateP2p1].append({})##0 container and 0 weight, []- order Ids, []--> small container ids, [] --> big container ids
                #print("else",line,filledOrderP2p1)
            if dateP1p2 not in filledOrderP1p2:
                filledOrderP1p2[dateP1p2]=[]
                filledOrderP1p2[dateP1p2].append({})##0 container and 0 weight, []- order Ids, []--> small container ids, [] --> big container ids
                tripDictP1p2[dateP1p2]=[]
                tripDictP1p2[dateP1p2].append(p1p2List)
                #print("if",line,filledOrderP2p1)
            else:
                tripDictP1p2[dateP1p2].append(p1p2List)
                filledOrderP1p2[dateP1p2].append({})##0 container and 0 weight, []- order Ids, []--> small container ids, [] --> big container ids
    #print("tripDictP1p2",tripDictP1p2) # tripDictP1p2 {datetime.date(2021, 11, 2): [[datetime.datetime(2021, 11, 2, 5, 45, 57), datetime.datetime(2021, 11, 2, 5, 53, 17)], [datetime.datetime(2021, 11, 2, 7, 15, 42), datetime.datetime(2021, 11, 2, 7, 22, 52)],...]
    #print("\n", filledOrderP1p2)  #{datetime.date(2021, 11, 2): [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}], datetime.date(2021, 11, 3): [{}]}

    header = 0
    with open(ordersInputFile) as source:
        for line in source:
            if header == 0:
                header+=1
            else:
                addContainer=0
                line = line.rstrip().split("\t")
                #print(line[-1])
                orderDate=datetime.strptime(line[9],'%m/%d/%Y').date()
                orderDateList=line[9].split("/")
                orderTimeList=line[6].split(":")
                setOrderDateTime=datetime(year=int(orderDateList[2]),month=int(orderDateList[0]),day=int(orderDateList[1]),hour=int(orderTimeList[0]),minute=int(orderTimeList[1]),
                                              second=int(orderTimeList[2]))
                orderTimeDict[line[-1]] = setOrderDateTime
                deliveryDateList=line[11].split("/")
                deliveryTimeList=line[12].split(":")
                deliveryDateTime=datetime(year=int(deliveryDateList[2]),month=int(deliveryDateList[0]),day=int(deliveryDateList[1]),hour=int(deliveryTimeList[0]),minute=int(deliveryTimeList[1]),
                                               second=int(deliveryTimeList[2]))
                #print(orderDate)
                ##get the trip entries, p1 to p2 from the ordered # order date --2Nov2021
                if orderDate in tripDictP1p2:
                    ###line[2] --> from SAP plant
                    ###line[5] --> to SAP plant
                    if "_E" in line[-1]:
                        hours_add = emptyflexiblityTime_dict[line[0]][0]
                        #hours_add = 23
                        mins_add = emptyflexiblityTime_dict[line[0]][1]
                    else:
                        hours_add = flexiblityTime_dict[line[0]][0]
                        #print(hours_add)
                        mins_add = flexiblityTime_dict[line[0]][1]
                    if line[2] in containerInfoDict["plant1"] and line[5] in containerInfoDict["plant2"] :
                        if deliveryDateTime not in tripDeliveryTimeP1p2:
                            tripDeliveryTimeP1p2[deliveryDateTime]=0
                            latestLoadTime=setOrderDateTime+timedelta(hours=hours_add)+timedelta(minutes=mins_add)+timedelta(seconds=tripDeliveryTimeP1p2[deliveryDateTime])
                        else:
                            tripDeliveryTimeP1p2[deliveryDateTime]+=1
                            latestLoadTime=setOrderDateTime+timedelta(hours=hours_add)+timedelta(minutes=mins_add)+timedelta(seconds=tripDeliveryTimeP1p2[deliveryDateTime])
                            deliveryDateTime+=timedelta(seconds=tripDeliveryTimeP1p2[deliveryDateTime])
                            tripDeliveryTimeP1p2[deliveryDateTime]=0
                        ##compare setOrderDateTime with trip time in tripDictp1p2
                        addContainer=0
                        #latestLoadTime=setOrderDateTime+timedelta(hours=hours_add)+timedelta(minutes=mins_add)+timedelta(seconds=tripDeliveryTimeP1p2[deliveryDateTime])
                        setOrderDateTime = setOrderDateTime + timedelta(minutes = 20)
                        tripsDateP1p2=tripDictP1p2[orderDate]
                        for tripIndex in range(len(tripsDateP1p2)):
                            #the first trip immediately after the oredr time
                            if tripsDateP1p2[tripIndex][0]>=setOrderDateTime:
                                filledOrderP1p2[orderDate][tripIndex][latestLoadTime]=[line[-1],int(float(line[23])),line[14], str(deliveryDateTime)]
                                #print(filledOrderP1p2)
                                addContainer=1
                                break
                        ###check boundary condition
                        if addContainer==0:
                            orderDateNext=orderDate+timedelta(minutes=1440)
                            if orderDateNext in tripDictP1p2:
                                tripsDateNextP1p2=tripDictP1p2[orderDateNext]
                                for tripIndex in range(len(tripsDateNextP1p2)):
                                    if tripsDateNextP1p2[tripIndex][0] >=setOrderDateTime:
                                        filledOrderP1p2[orderDateNext][tripIndex][latestLoadTime]=[line[-1],int(float(line[23])),line[14], str(deliveryDateTime)]
                                        addContainer=1
                                        break
                    elif line[2] in containerInfoDict["plant2"] and line[5] in containerInfoDict["plant1"] and orderDate in tripDictP2p1:
                        ##get the trip entries, p1 to p2 from the ordered
                        tripsDateP2p1=tripDictP2p1[orderDate] # order date --2Nov2021
                        #print(tripsDateP1p2)
                        ##compare setOrderDateTime with trip time in tripDictp1p2
                        addContainer=0
                        if deliveryDateTime not in tripDeliveryTimeP2p1:
                            tripDeliveryTimeP2p1[deliveryDateTime]=0
                            latestLoadTime=setOrderDateTime+timedelta(hours=hours_add)+timedelta(minutes=mins_add)+timedelta(seconds=tripDeliveryTimeP2p1[deliveryDateTime])
                        else:
                            tripDeliveryTimeP2p1[deliveryDateTime]+=1
                            latestLoadTime=setOrderDateTime+timedelta(hours= hours_add)+timedelta(minutes=mins_add)+timedelta(seconds=tripDeliveryTimeP2p1[deliveryDateTime])
                            deliveryDateTime+=timedelta(seconds=tripDeliveryTimeP2p1[deliveryDateTime])
                            tripDeliveryTimeP2p1[deliveryDateTime]=0
                        ##tripsDateP1p2=[[datetime.datetime(2021, 11, 2, 17, 18, 44), datetime.datetime(2021, 11, 2, 17, 29, 21)],list,list,list,list,list,list....]
                        ##11/2/2021 19:01	11/2/2021 19:08

                        for tripIndex in range(len(tripsDateP2p1)):

                            if tripsDateP2p1[tripIndex][0] >= setOrderDateTime:
                                #print(line)
                                filledOrderP2p1[orderDate][tripIndex][latestLoadTime]=[line[-1],int(float(line[23])),line[14], str(deliveryDateTime)]
                                addContainer=1
                                #print(filledOrderP2p1)
                                break
                        ###check boundary condition for changing in the date
                        if addContainer==0:
                            orderDateNext=orderDate+timedelta(minutes=1440)
                            if orderDateNext in tripDictP2p1:
                                tripsDateNextP2p1=tripDictP2p1[orderDateNext]
                                for tripIndex in range(len(tripsDateNextP2p1)):
                                    if tripsDateNextP2p1[tripIndex][0] >= setOrderDateTime:
                                        filledOrderP2p1[orderDate][tripIndex][latestLoadTime]=[line[-1],int(float(line[23])),line[14], str(deliveryDateTime)]
                                        addContainer=1
                                        break

    tripContinuedP2p1Dict = adjustOrders(filledOrderP2p1, tripDictP2p1)
    tripContinuedP1p2Dict = adjustOrders(filledOrderP1p2, tripDictP1p2)

    dest1=open(outputPrefix+"_P2p1.txt","w")
    dest2=open(outputPrefix+"_P1p2.txt","w")
    dest1.write("tripStartDate"+" "+"tripStartTime"+" "+"tripEndDate"+" "+"tripEndTime"+" "+"total_containers"+" "+"trip_cus"+" "+"filledOrderIds"+" "+"emptyOrderIds"+" "+"filledcontainers"+" "+\
                "emptyContainers"+"\n")
    dest2.write("tripStartDate"+" "+"tripStartTime"+" "+"tripEndDate"+" "+"tripEndTime"+" "+"total_containers"+" "+"trip_cus"+" "+"filledOrderIds"+" "+"emptyOrderIds"+" "+"filledcontainers"+" "+\
                "emptyContainers"+"\n")
    dest3 = open(outputPrefix+"_round_empty_trips.txt","w")
    #for tripP2p1 in roundTripDict:
    #    if tripP2p1 in tripCancelledP2p1List:
    #        if roundTripDict[tripP2p1] not in tripCancelledP1p2List:
    #            print("ERROR cancelled trips do not match at P2p1", tripP2p1)
    #        else:
    #            dest3.write(tripP2p1+"\t"+roundTripDict[tripP2p1])
    #            dest3.write("\n")
    #orderP1p2Dict = {}
    dest4 = open(outputPrefix+"_orders_replenishmentBreak_P2p1.txt","w")
    dest5 = open(outputPrefix+"_orders_replenishmentBreak_P1p2.txt","w")
    #print(tripContinuedP1p2Dict)
    #print("\n"+"\n"+"\n")
    #print(tripContinuedP2p1Dict)
    #print("\n"+"\n"+"\n")
    #print(roundTripDict)
    orderListCaptured = []
    for tripP2p1 in roundTripDict:
        if tripP2p1 in tripContinuedP2p1Dict:
            tripP1p2 = roundTripDict[tripP2p1]
            listOutP2p1, replenishmentBreakP2p1 = extractInfoDict(tripP2p1,tripContinuedP2p1Dict)
            orderListCaptured += listOutP2p1[3]
            orderListCaptured += listOutP2p1[4]
            for listIn in listOutP2p1:
                    dest1.write(",".join(listIn))
                    dest1.write("\t")
            dest1.write("\n")
            if len(replenishmentBreakP2p1) > 0:
                    for listIn in replenishmentBreakP2p1:
                        dest4.write(" ".join(listIn))
                        dest4.write("\n")
            if tripP1p2 in tripContinuedP1p2Dict:
                listOutP1p2, replenishmentBreakP1p2 = extractInfoDict(tripP1p2,tripContinuedP1p2Dict)
                orderListCaptured += listOutP1p2[3]
                orderListCaptured += listOutP1p2[4]
                for listIn in listOutP1p2:
                    dest2.write(",".join(listIn))
                    dest2.write("\t")
                dest2.write("\n")
                if len(replenishmentBreakP1p2) > 0:
                    for listIn in replenishmentBreakP1p2:
                        dest5.write(" ".join(listIn))
                        dest5.write("\n")
            else:
                dest2.write(tripP1p2+" "+"0"+" "+"0"+" "+"0"+" "+"0"+" "+"0"+"\n")
        elif roundTripDict[tripP2p1] in tripContinuedP1p2Dict:
            tripP1p2 = roundTripDict[tripP2p1]
            listOutP1p2, replenishmentBreakP1p2 = extractInfoDict(tripP1p2,tripContinuedP1p2Dict)
            orderListCaptured += listOutP1p2[3]
            orderListCaptured += listOutP1p2[4]
            for listIn in listOutP1p2:
                    dest2.write(" ".join(listIn))
                    dest2.write(" ")
            dest2.write("\n")
            if len(replenishmentBreakP1p2) > 0:
                for listIn in replenishmentBreakP1p2:
                    dest5.write(" ".join(listIn))
                    dest5.write("\n")
            dest1.write(tripP2p1+" "+"0"+" "+"0"+" "+"0"+" "+"0"+" "+"0"+"\n")
        else:
            dest3.write(tripP2p1+"\t"+roundTripDict[tripP2p1])
            dest3.write("\n")
    print(len(list(set(orderListCaptured))))


def extractInfoDict(tripTime, dictIn):
    listOut = []
    replenishmentBreak = []
    dateKeyTrip = tripTime.split()
    deliveryDate = dateKeyTrip[2]
    deliveryTime = dateKeyTrip[3]
    listOut.append(dateKeyTrip)
    dtObj = stringToDateTime(deliveryDate, deliveryTime)
    rowFilledDataList = dictIn[tripTime][0]
    latestDeliveryList = dictIn[tripTime][-1]
    orderList = dictIn[tripTime][1]
    containerList = dictIn[tripTime][2]
    totalNumberRows = len(rowFilledDataList)
    totalContainers = 0
    totalCus = 0
    filledOrderIds = []
    emptyOrderIds = []
    filledContainerIds = []
    emptyContainerIds = []
    for r in range(totalNumberRows):
        rowFilled = rowFilledDataList[r].count(1)
        rowCu = (rowFilled/len(rowFilledDataList[r]))*100
        totalContainers += rowFilled
        totalCus += rowCu
        for i in range(len(rowFilledDataList[r])):
            if rowFilledDataList[r][i] != 0:
                latestDeliveryDate = latestDeliveryList[r][i].split()[0]
                latestDeliveryTime = latestDeliveryList[r][i].split()[1]
                latestDtObj = stringToDateTime(latestDeliveryDate, latestDeliveryTime)
                if "_E" in orderList[r][i]:
                    emptyOrderIds.append(orderList[r][i])
                    emptyContainerIds.append(containerList[r][i])
                else:
                    filledOrderIds.append(orderList[r][i])
                    filledContainerIds.append(containerList[r][i])
                if latestDtObj < dtObj:
                    if "_E" not in orderList[r][i]:
                        tmpList = [str(latestDtObj), str (dtObj), str(orderList[r][i])]
                        replenishmentBreak.append(tmpList[:])
    listOut.append([str(totalContainers)])
    listOut.append([str(float(totalCus/600))])
    listOut.append(filledOrderIds)
    listOut.append(emptyOrderIds)
    listOut.append(filledContainerIds)
    listOut.append(emptyContainerIds)
    return listOut, replenishmentBreak

def adjustOrders(dictIn, tripDict):
    previousOrder = {}
    tripContinued = {}
    for dates in dictIn:
        dictList = dictIn[dates]
        tripTimes = tripDict[dates]
        for i in range(len(dictList)):
            trip=dictList[i]
            tripTime=tripTimes[i]
            trip.update(previousOrder)
            previousOrder = {}
            tripSorted=sorted(trip.items(), key=lambda t: t[0])
            if len(tripSorted)>0:
                truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time = countFilledRows(tripSorted)
                print(truck_carrier_orders)
                if len(truck_carrier_rows) >= 6:
                    previous_truck_carrier_rows, previous_truck_carrier_orders, previous_truck_carrier_contId, previous_truck_carrier_latestLoad_time, previous_truck_carrier_latestDelivery_time, previousOrder = adjustCurrentContainers(truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time)
                else:
                    previous_truck_carrier_rows, previous_truck_carrier_orders, previous_truck_carrier_contId, previous_truck_carrier_latestLoad_time, previous_truck_carrier_latestDelivery_time = truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time
                tripContinued[str(tripTime[0])+" "+str(tripTime[1])] = [previous_truck_carrier_rows, previous_truck_carrier_orders, previous_truck_carrier_contId, previous_truck_carrier_latestLoad_time, previous_truck_carrier_latestDelivery_time ]
    return tripContinued



def countFilledRows(tripSorted):
    bigContainerIds = ["1T02.154.630","1T03.154.632","1T02.154.642","1T12.161.485","1T02.154.630_E","1T03.154.632_E","1T02.154.642_E","1T12.161.485_E"]
    truck_carrier_rows = []
    truck_carrier_orders = []
    truck_carrier_contId = []
    truck_carrier_latestLoad_time = []
    truck_carrier_latestDelivery_time = []
    for orderItem in tripSorted:
        if orderItem[0] != datetime(2212, 12, 12, 12, 12, 12):
            if orderItem[1][2] in bigContainerIds:
                container_type_divide = 2
            else: container_type_divide = 3
            fillRow, fillOrders, fillContId, fillLoadTime, filledDeliveryTime = filledRowInCarrier(orderItem[0], orderItem[1],container_type_divide)
            truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time = adjustCarrierRows(fillRow, fillOrders, fillContId, fillLoadTime, filledDeliveryTime, truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time, container_type_divide)
    return truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time

def filledRowInCarrier(latestLoadTime, listIn, container_type_divide):
    if container_type_divide == 2:
        cont_pattern = [1,1]
        cont_order = [listIn[0],listIn[0]]
        cont_id = [listIn[2],listIn[2]]
        cont_loadTime = [latestLoadTime, latestLoadTime]
        cont_deliveryTime = [listIn[3],listIn[3]]
    else:
        cont_pattern = [1,1,1]
        cont_order = [listIn[0], listIn[0], listIn[0]]
        cont_id = [listIn[2],listIn[2],listIn[2]]
        cont_loadTime = [latestLoadTime, latestLoadTime, latestLoadTime]
        cont_deliveryTime = [listIn[3],listIn[3], listIn[3]]
    numRow = listIn[1] // container_type_divide
    halfRow = listIn[1] % container_type_divide
    fillRow = []
    fillOrders = []
    fillContId = []
    fillLoadTime = []
    fillDeliveryTime = []
    for i in range(numRow):##this code takes care of aliasing issues
        fillRow.append(cont_pattern[:])
        fillOrders.append(cont_order[:])
        fillContId.append(cont_id[:])
        fillLoadTime.append(cont_loadTime[:])
        fillDeliveryTime.append(cont_deliveryTime[:])
    if halfRow == 1:
        if container_type_divide == 2:
            fillRow.append([1, 0])
            fillOrders.append([listIn[0],0])
            fillContId.append([listIn[2],0])
            fillLoadTime.append([latestLoadTime, datetime(2212, 12, 12, 12, 12, 12)])
            fillDeliveryTime.append([listIn[3], datetime(2212, 12, 12, 12, 12, 12)])
        else:
            fillRow.append([1, 0, 0])
            fillOrders.append([listIn[0], 0, 0])
            fillContId.append([listIn[2],0, 0])
            fillLoadTime.append([latestLoadTime, datetime(2212, 12, 12, 12, 12, 12), datetime(2212, 12, 12, 12, 12, 12)])
            fillDeliveryTime.append([listIn[3], datetime(2212, 12, 12, 12, 12, 12), datetime(2212, 12, 12, 12, 12, 12)])
    elif halfRow == 2:
        fillRow.append([1, 1, 0])
        fillOrders.append([listIn[0], listIn[0], 0])
        fillContId.append([listIn[2], listIn[2], 0])
        fillLoadTime.append([latestLoadTime, latestLoadTime, datetime(2212, 12, 12, 12, 12, 12)])
        fillDeliveryTime.append([listIn[3],listIn[3], datetime(2212, 12, 12, 12, 12, 12)])
    return fillRow, fillOrders, fillContId, fillLoadTime, fillDeliveryTime

def adjustCarrierRows(fillRow, fillOrders, fillContId, fillLoadTime, fillDeliveryTime, truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time, container_type_divide):
    emptySpaceGlobalIndex = []
    emptySpaceLocalIndex = []
    emptySpaceEmptyContainerPresent = []
    emptySpaceRowLength = []
    for i in range(len(truck_carrier_rows)):
        for j in range(len(truck_carrier_rows[i])):
            if truck_carrier_rows[i][j] == 0:
                emptySpaceGlobalIndex.append(i)
                emptySpaceLocalIndex.append(j)
                emptySpaceRowLength.append(len(truck_carrier_rows[i]))
                containEmptyOrder = isContainEmptyOrder(truck_carrier_orders[i])
                emptySpaceEmptyContainerPresent.append(containEmptyOrder)
    for i in range(len(emptySpaceGlobalIndex)):
        for j in range(len(fillRow)):
            if len(fillRow[j]) == emptySpaceRowLength[i]:
                presentEmptyOrder = isContainEmptyOrder(fillOrders[j])
                if emptySpaceEmptyContainerPresent[i] == presentEmptyOrder:
                    if 1 in fillRow[j]:
                        containerIndex = len(fillRow[j])-1-fillRow[j][::-1].index(1)
                        orderId = fillOrders[j][containerIndex]
                        containerId = fillContId[j][containerIndex]
                        loadTime = fillLoadTime[j][containerIndex]
                        deliveryTime = fillDeliveryTime[j][containerIndex]
                        truck_carrier_rows[emptySpaceGlobalIndex[i]][emptySpaceLocalIndex[i]] = 1
                        truck_carrier_orders[emptySpaceGlobalIndex[i]][emptySpaceLocalIndex[i]] = orderId
                        truck_carrier_contId[emptySpaceGlobalIndex[i]][emptySpaceLocalIndex[i]] = containerId
                        truck_carrier_latestLoad_time[emptySpaceGlobalIndex[i]][emptySpaceLocalIndex[i]] = loadTime
                        truck_carrier_latestDelivery_time[emptySpaceGlobalIndex[i]][emptySpaceLocalIndex[i]] = deliveryTime
                        fillRow[j][containerIndex] = fillOrders[j][containerIndex] = fillContId[j][containerIndex] = 0
                        fillLoadTime[j][containerIndex] = fillDeliveryTime[j][containerIndex] = datetime(2212, 12, 12, 12, 12, 12)
                        break
    for i in range(len(fillRow)):
        if fillRow[i].count(0) != len(fillRow[i]):
            truck_carrier_rows.append(fillRow[i])
            truck_carrier_orders.append(fillOrders[i])
            truck_carrier_contId.append(fillContId[i])
            truck_carrier_latestLoad_time.append(fillLoadTime[i])
            truck_carrier_latestDelivery_time.append(fillDeliveryTime[i])
    return truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time



def isContainEmptyOrder(listIn):
    containEmptyOrder = False
    for content in listIn:
        if content!=0:
            if "_E" in content:
                containEmptyOrder = True
    return containEmptyOrder


def adjustCurrentContainers(truck_carrier_rows, truck_carrier_orders, truck_carrier_contId, truck_carrier_latestLoad_time, truck_carrier_latestDelivery_time):
    remainingOrderDict = {}
    present_carrier_rows = []
    present_carrier_orders = []
    present_carrier_contId = []
    present_carrier_latestLoadTime = []
    present_carrier_latestDelivery_time =[]
    for i in range(len(truck_carrier_rows)):
        if i<=5:
            present_carrier_rows.append(truck_carrier_rows[i])
            present_carrier_orders.append(truck_carrier_orders[i])
            present_carrier_contId.append(truck_carrier_contId[i])
            present_carrier_latestLoadTime.append(truck_carrier_latestLoad_time[i])
            present_carrier_latestDelivery_time.append(truck_carrier_latestDelivery_time[i])
        else:
            loadTimeElements = truck_carrier_latestLoad_time[i]
            for timeElementIndex in range(len(loadTimeElements)):
                if loadTimeElements[timeElementIndex] not in remainingOrderDict:
                    remainingOrderDict[loadTimeElements[timeElementIndex]] = [truck_carrier_orders[i][timeElementIndex], 1, truck_carrier_contId[i][timeElementIndex], truck_carrier_latestDelivery_time[i][timeElementIndex]]
                else:remainingOrderDict[loadTimeElements[timeElementIndex]][1]+=1
    return present_carrier_rows, present_carrier_orders, present_carrier_contId, present_carrier_latestLoadTime, present_carrier_latestDelivery_time, remainingOrderDict


def isEmptyFilledMix(list1,list2):
    emptyFilledMix = False
    list1Empty = False
    list2Empty = False
    for container in list1Empty:
        if "_E" in container:
            list1Empty = True
    for container in list2Empty:
        if "_" in container:
            list2Empty = True
    if list1Empty != list2Empty:
        emptyFilledMix = True
    return emptyFilledMix

def makeDict(previous_truck_carrier_rows, previous_truck_carrier_orders, previous_truck_carrier_contId, previous_truck_carrier_latestLoad_time, previous_truck_carrier_latestDelivery_time):
    reshuffleOrderDict = {}
    for i in range(len(previous_truck_carrier_latestLoad_time)):
        for j in range(len(previous_truck_carrier_latestLoad_time[i])):
            if previous_truck_carrier_latestLoad_time[i][j] not in reshuffleOrderDict:
                        reshuffleOrderDict[previous_truck_carrier_latestLoad_time[i][j]] = [previous_truck_carrier_orders[i][j], 1, previous_truck_carrier_contId[i][j], previous_truck_carrier_latestDelivery_time[i][j]]
            else:reshuffleOrderDict[previous_truck_carrier_latestLoad_time[i][j]][1]+=1
    return reshuffleOrderDict

def stringToDateTime(str1,str2):
    dateList = str1.split("-")
    timeList = str2.split(":")
    #print(dateList, timeList)
    dtObj = datetime(year=int(dateList[0]),month=int(dateList[1]),day=int(dateList[2]),hour=int(timeList[0]),minute=int(timeList[1]),
                                               second=int(timeList[2]))
    return dtObj
