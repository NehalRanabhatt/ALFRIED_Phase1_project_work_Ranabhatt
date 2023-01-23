# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 13:56:49 2022

@author: Ranabhatt
"""
import datetime

class Jisdataformat:


    def __init__(self,jisOrderInput,orderCount):
        self.jisOrderInput = jisOrderInput
        self.orderCount = int(orderCount)
        self.outputList = []

    def readJisOrderInputFile(self):
        JisInfoDict = {}
        JisInfoDict["JIS400WEL001"] = {"containerId":"1T12.161.485","containerWeight(KG)":"267","weightSingleContFullCapacity":"384", "totalWeightOfOrder":"384"}
        JisInfoDict["JIS400STS001"] = {"containerId":"1T12.161.486","containerWeight(KG)":"172","weightSingleContFullCapacity":"345", "totalWeightOfOrder":"345"}
        with open(self.jisOrderInput) as source:
            header = 0
            for line in source:
                if header == 0:
                    header += 1
                else:
                    line = line.rstrip().split()
                    self.orderCount += 1
                    # read order time from the original Jis order file
                    orderDateTime = line[1].strip('""').replace(",","")

                    # read Bedarfszeitpunkt from the original Jis order file
                    latestDeliveryDateTime = line[2].strip('""').replace(",","")

                    #Jis order format
                    orderMonth, orderDay, orderYear, orderHour, orderMinute, orderSecond, orderDate, orderTime = self.extractOrderDateTime(orderDateTime)
                    latestDeliveryMonth, latestDeliveryDay, latestDeliveryYear, latestDeliveryHour, latestDeliveryMinute, latestDeliverySecond, latestDeliveryDate, latestDeliveryTime = self.extractOrderDateTime(latestDeliveryDateTime)
                    #print(orderDate, oderTime, latestDeliveryDate, latestDeliveryTime)

                    #empty order format
                    emptyOrderDate, emptyOrderTime = self.createEmptyOrders(orderYear, orderMonth, orderDay, orderHour, orderMinute, orderSecond)
                    latestDeliveryEmptyOrderDate, latestDeliveryEmptyOrderTime = self.createEmptyOrders(latestDeliveryYear, latestDeliveryMonth, latestDeliveryDay,  latestDeliveryHour, latestDeliveryMinute, latestDeliverySecond)
                    #print(emptyOrderDate, emptyOrderTime,latestDeliveryEmptyOrderDate, latestDeliveryEmptyemptyOrderTime )
                    """
                    #File format:
                     "booking type" + "\t"+
                    "Material" + "\t"+
                    "from SAP Plant" + "\t"+
                    "LOrt" + "\t"+
                    "material" + "\t"+
                    "to SAP Plant" + "\t"+
                    "order Time"+"\t"+
                    "pieces"+ "\t"+
                    "unit" + "\t"+
                    "order date"+ "\t"+
                    "remark" + "\t"+
                    "latestDelivery date" + "\t"+
                    "latestDelivery Time" + "\t"+
                    "material_weight(KG)"+"\t"+
                    "containerId"+ "\t"+
                    "containerWeight(KG)"+"\t"+
                    "material parts per container"+"\t"+
                    "steelBasket_id"+ "\t"+
                    "steelBasket_weight"+"\t"+
                    "material parts per steel basket"+"\t"+
                    "number of steel baskets per container"+"\t"+
                    "SAP_plant_assembling"+"\t"+
                    "weightSingleContFullCapacity"+"\t"+
                    "requiredContainer"+"\t"+
                    "requiredSteelBasket"+"\t"+
                    "totalWeightOfOrder"+"\t"+
                    "capacityUtilizationOfOrder"+"\t"+
                    "errorCode"+"\t"
                    "orderIds"+ "\n"
                    """
                    #adding filled order into tmp list
                    tmpFilledOrder = ["SCAN_P",line[0],"1504","-1",line[0],"1001",
                                    str(orderTime),"-1","-1",str(orderDate),"-1",str(latestDeliveryDate),
                                    str(latestDeliveryTime),"-1", JisInfoDict[line[0]]["containerId"],JisInfoDict[line[0]]["containerWeight(KG)"],
                                    "-1","-1","-1","-1","-1","-1",JisInfoDict[line[0]]["weightSingleContFullCapacity"],
                                    "1","-1",JisInfoDict[line[0]]["totalWeightOfOrder"] ,"100", "-1",str(self.orderCount)]
                    self.outputList.append(tmpFilledOrder[:])
                    #adding empty order into tmp list
                    tmpEmptyOrder = ["SCAN_P",line[0],"1001","-1",line[0],"1504", str(emptyOrderTime),"-1","-1",str(emptyOrderDate),"-1",
                                     str(latestDeliveryEmptyOrderDate),str(latestDeliveryEmptyOrderTime),"-1", JisInfoDict[line[0]]["containerId"]+"_E",
                                     JisInfoDict[line[0]]["containerWeight(KG)"], "-1","-1","-1","-1","-1","-1","-1", "1","-1",JisInfoDict[line[0]]["totalWeightOfOrder"] ,
                                     "-1", "-1",str(self.orderCount)+"_E"]
                    self.outputList.append(tmpEmptyOrder[:])
            return self.outputList

    def extractOrderDateTime(self,orderDateTime):
        orderMonth= (orderDateTime[4:6])
        if orderMonth[0]=="0":
            orderMonth = orderDateTime[5:6]
        orderDay= (orderDateTime[6:8])
        if orderDay[0]=="0":
            orderDay = orderDateTime[7:8]
        orderYear= (orderDateTime[0:4])

        orderHour= (orderDateTime[8:10])
        if orderHour[0]=="0":
            orderHour= (orderDateTime[9:10])
        orderMinute= (orderDateTime[10:12])
        orderSecond= (orderDateTime[12:14])

        orderDate = (orderMonth + "/"+ orderDay+"/"+ orderYear)
        orderTime = (orderHour + ":"+ orderMinute + ":" + orderSecond)

        return orderMonth, orderDay, orderYear, orderHour, orderMinute, orderSecond, orderDate, orderTime

    def createEmptyOrders(self, orderYear, orderMonth, orderDay, orderHour, orderMinute, orderSecond):

        #set jis empty order format
        #print(orderDay)
        setDate=datetime.datetime(year=int(orderYear),month=int(orderMonth),day=int(orderDay),hour=int(orderHour),minute=int(orderMinute),
          second=int(orderSecond))
        emptyOrderLeadTime=datetime.timedelta(hours=2,minutes=0,seconds=0)

        # add 2 hours to the actual Jis order time
        setEmptyOrderDateTime = setDate + emptyOrderLeadTime
        emptyOrderDateTime = str(setEmptyOrderDateTime).split()
        #print(emptyOrderDateTime)
        # empty order date
        emptyOrderDate = emptyOrderDateTime[0].replace("-","")
        #print(emptyOrderDate)
        emptyOrderYear = emptyOrderDate[0:4]
        emptyOrderMonth = emptyOrderDate[4:6]
        if emptyOrderMonth[0]=="0":
            emptyOrderMonth = emptyOrderDate[5:6]
        emptyOrderDay = emptyOrderDate[6:8]
        if emptyOrderDay[0] == "0":
            emptyOrderDay = emptyOrderDate[7:8]
        #empty order time
        emptyOrderTime = emptyOrderDateTime[1].replace(":","")
        emptyOrderHour = emptyOrderTime[0:2]
        if emptyOrderHour[0] == "0":
            emptyOrderHour = emptyOrderTime[1:2]
        emptyOrderMinute = emptyOrderTime[2:4]
        emptyOrderSecond = emptyOrderTime[4:6]

        emptyOrderDate= emptyOrderMonth +"/"+ emptyOrderDay+"/" + emptyOrderYear  #order Time + 2 hour
        emptyOrderTime = emptyOrderHour+ ":"+ emptyOrderMinute + ":" + emptyOrderSecond

        return emptyOrderDate, emptyOrderTime

    def writeJisFilledAndEmptyOrders(self):
        dest = open("JisEmptyFilledOrders.csv","w")
        for record in self.outputList:
            dest.write(",".join(record))
            dest.write("\n")
        dest.close()

if __name__=="__main__":
    jisDataFormat = Jisdataformat("20211217__JIS_order.txt",0) #create object fro the class
    jisDataFormat.readJisOrderInputFile()
    jisDataFormat.writeJisFilledAndEmptyOrders()
