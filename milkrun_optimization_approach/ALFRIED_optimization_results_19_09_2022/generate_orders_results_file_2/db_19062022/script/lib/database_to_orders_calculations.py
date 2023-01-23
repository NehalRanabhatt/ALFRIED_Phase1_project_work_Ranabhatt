# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 10:59:50 2022

@author: Ranabhatt
changed on 10-09-2022 346,348
"""

import pymongo
import datetime
import yaml
from lib.Jis_filled_empty_orders import Jisdataformat

class Databasetoorderscalculation:

    def __init__(self,configYaml):

        stream = open(configYaml, 'r')
        self.dictionary = yaml.safe_load(stream)
        self.client=pymongo.MongoClient(self.dictionary["mongoClient"])  ##connect to the mongodb client
        self.dblist = self.client.list_database_names()  ## database names
        self.mydb=self.client[self.dictionary["database"]] #dbInput = "db_18022022"
        self.mycol=self.mydb[self.dictionary["database"]]
        self.cursor =self.mycol.find({})
        self.orders_record_dict={}#orders_record
        self.assembling_dict={} # to populate container assembling files records
        self.weight_dict={} # to populate material weight records
        self.errorCode_dict={} # add error codes number
        self.addTime_dict={"351":[24,0,0],"993":[5,0,0],"301":[5,0,0],"SCAN_P":[4,30,0]} # used to calculate lastest delivery time of orders
        self.error3_material_list=[] #
        self.missing_list=["-1",-1,float(-1)]
        self.orderCount = 0


    # populate assembling dict from conatiner assembling file
    def populateAssemblingDict(self):
        if self.doc["Material"] not in self.assembling_dict:
            self.assembling_dict[self.doc["Material"]] =[[],[],[],[],[],[]]

        self.assembling_dict[self.doc["Material"]][0].append(self.doc["container "])
        self.assembling_dict[self.doc["Material"]][1].append(int(self.doc["material parts per container"]))
        self.assembling_dict[self.doc["Material"]][2].append(self.doc["steel basket"])
        self.assembling_dict[self.doc["Material"]][3].append(int(self.doc["material parts per steel basket"]))
        self.assembling_dict[self.doc["Material"]][4].append(int(self.doc["quantity steel baskets per container"]))
        self.assembling_dict[self.doc["Material"]][5].append(self.doc["SAP plant"]) # adding all SAP plant assciated with matreial [1001', '1501', '1506']

    # populate weight dict from materal weight file and check error code 7
    def populateMaterialWeightDict(self):
        weight_unit = list(self.doc.values())[-1]
        weight_factor = 1
        if weight_unit!="KG":
            weight_factor = 1000
        # convert weight from G to KG
        weight_values = float(list(self.doc.values())[-2])/weight_factor

        if self.doc["Material"] not in self.weight_dict:
            self.weight_dict[self.doc["Material"]] = weight_values
        elif weight_values != self.weight_dict[self.doc["Material"]]:
            #print("Error3:Diffrent material weight for same container,steel_basket or container id",doc["Material"],list(doc.keys())[-2])
            self.error3_material_list.append(self.doc["Material"])#Diffrent material weight for same container,steel_basket or container id
        else:pass

    #calclate latest delivery time (993-segmetnKanban,301-manual booking,351-umlage)
    def calculateLastestDeliveryTimeOfOrders(self):
        #calculate latestdelivery time
        #print(self.doc["order Time"])
        #print(self.doc["order date"])
        orderTime=self.doc["order Time"].split(":")
        orderDate=self.doc["order date"].split("/")
        setDate=datetime.datetime(year=int(orderDate[2]),month=int(orderDate[0]),day=int(orderDate[1]),hour=int(orderTime[0]),minute=int(orderTime[1]),
                                  second=int(orderTime[2]))
        ## totalLeadTime = LeadTime + maximum transportation time
        totalLeadTime=datetime.timedelta(hours=self.addTime_dict[self.doc["booking type"]][0],minutes=self.addTime_dict[self.doc["booking type"]][1],seconds=self.addTime_dict[self.doc["booking type"]][2])
        latestDeliveryDateTime=setDate + totalLeadTime
        latestDeliveryDateTime = str(latestDeliveryDateTime).split()
        #print(latestDeliveryDateTime)
        latestDeliveryDateStr = latestDeliveryDateTime[0].replace("-","")
        latestDeliveryYear = latestDeliveryDateStr[0:4]
        latestDeliveryMonth = latestDeliveryDateStr[4:6]

        if latestDeliveryMonth[0]=="0":
            latestDeliveryMonth = latestDeliveryDateStr[5:6]
        latestDeliveryDay = latestDeliveryDateStr[6:8]

        latestDeliveryTimeStr = latestDeliveryDateTime[1].replace(":","")

        latestDeliveryHour = latestDeliveryTimeStr[0:2]
        if latestDeliveryHour[0] == "0":
            latestDeliveryHour = latestDeliveryTimeStr[1:2]
        latestDeliveryMinute = latestDeliveryTimeStr[2:4]
        latestDeliverySecond =latestDeliveryTimeStr[4:6]

        latestDeliveryDate= latestDeliveryMonth +"/"+ latestDeliveryDay+"/" + latestDeliveryYear
        self.latestDeliveryDate = latestDeliveryDate
        latestDeliveryTime = latestDeliveryHour+ ":"+ latestDeliveryMinute + ":" + latestDeliverySecond
        self.latestDeliveryTime = latestDeliveryTime
        #print(latestDeliveryDate)
        #print(latestDeliveryTime)

    def setEmptyOrderDateTime(self,inputOrderString):
        orderDateTime = str(inputOrderString).split()
        orderDateStr = orderDateTime[0].replace("-","")
        orderYear = orderDateStr[0:4]
        orderMonth = orderDateStr[4:6]
        if orderMonth[0]=="0":
            orderMonth = orderDateStr[5:6]
        orderDay = orderDateStr[6:8]

        orderTimeStr = orderDateTime[1].replace(":","")

        orderHour = orderTimeStr[0:2]
        if orderHour[0] == "0":
            orderHour = orderTimeStr[1:2]
        orderMinute = orderTimeStr[2:4]
        orderSecond =orderTimeStr[4:6]

        orderDate= orderMonth +"/"+ orderDay+"/" + orderYear # latesr delivery + 2 hr
        orderTime = orderHour+ ":"+ orderMinute + ":" + orderSecond

        return orderDate, orderTime


    def createEmptyOrders(self,filledOrderList):

        emptyOrder_list = []

        orderTime = filledOrderList[6].split(":")
        orderDate = filledOrderList[9].split("/")
        setDate = datetime.datetime(year=int(orderDate[2]),month=int(orderDate[0]),day=int(orderDate[1]),hour=int(orderTime[0]),minute=int(orderTime[1]),
          second = int(orderTime[2]))
        emptyOrderLeadTime = datetime.timedelta(hours=2,minutes=0,seconds=0)
        emptyOrderDateTime = setDate + emptyOrderLeadTime

        orderType = filledOrderList[0] # booking type
        emptyDeliveryLeadTime = datetime.timedelta(hours=self.addTime_dict[orderType][0],minutes=self.addTime_dict[orderType][1],seconds=self.addTime_dict[orderType][2])
        emptyOrderLatestDeliveryDateTime = emptyOrderDateTime + emptyDeliveryLeadTime

        emptyOrderDate, emptyOrderTime = self.setEmptyOrderDateTime(emptyOrderDateTime)
        emptyOrderLatestDeliveryDate, emptyOrderLatestDeliveryTime = self.setEmptyOrderDateTime(emptyOrderLatestDeliveryDateTime)

        emptyOrder_list.append(filledOrderList[0]) # booking type
        emptyOrder_list.append(str("-1")) #Material
        emptyOrder_list.append(filledOrderList[5]) # from SAP plant
        emptyOrder_list.append(str("-1")) #LOrt
        emptyOrder_list.append(str("-1")) # material
        emptyOrder_list.append(filledOrderList[2])#to SAP Plant
        emptyOrder_list.append(emptyOrderTime)# order Time
        emptyOrder_list.append(str("-1"))#pieces
        emptyOrder_list.append(str("-1"))#unit
        emptyOrder_list.append(emptyOrderDate)#order date
        emptyOrder_list.append(str("-1"))#remark
        emptyOrder_list.append(emptyOrderLatestDeliveryDate)#latestDelivery date"
        emptyOrder_list.append(emptyOrderLatestDeliveryTime)#"latestDelivery Time"
        emptyOrder_list.append(str("-1"))#"material_weight(KG)"
        emptyOrder_list.append(filledOrderList[14]+"_E")#"container_id"
        emptyOrder_list.append(str(filledOrderList[15]))#"container_weight(KG)
        emptyOrder_list.append(str("-1"))#"material parts per container
        emptyOrder_list.append(filledOrderList[17])#"steelBasket_id"
        emptyOrder_list.append(str(filledOrderList[18]))#"steelBasket_weight"
        emptyOrder_list.append(str("-1"))#"material parts per steel basket
        emptyOrder_list.append(filledOrderList[20])#"number of steel baskets per container"
        emptyOrder_list.append(str("-1"))#"SAP_plant_assembling"
        emptyOrder_list.append(str("-1"))#"weightSingleContFullCapacity"
        emptyOrder_list.append(str(int(float(filledOrderList[23]))))#"requiredContainer"
        emptyOrder_list.append(filledOrderList[24])#"requiredSteelBasket"
        emptyOrder_list.append(str(float(filledOrderList[18])*float(filledOrderList[24])+float(filledOrderList[15])*float(filledOrderList[23])))#"totalWeightOfOrder"
        emptyOrder_list.append(str("-1"))#"capacityUtilizationOfOrder"
        emptyOrder_list.append(str("-1"))#"errorCode"+"
        emptyOrder_list.append(filledOrderList[-1]+"_E")#orderIDs_E

        if filledOrderList[-1] == "3554":
            print(filledOrderList)

        return emptyOrder_list

    # read orders files,data cleansing with error code,orders capacity utilization calculations
    def filledOrdersCalculationAndErrorCodes(self):
        ##Error codes definitions##

        #error1:"to SAP Plant" ("SAP plant" matches to "to SAP" plant instead of "from SAP plant")
        #error2:"SAP plant not matched (neither from or to) incase of duplicate Materials ids"
        #error3:Diffrent material weight for same container,steel_basket or container id
        #error4:missing container id
        #error5:Material weight is zero
        #error6:Material available in order file and not in container_assembling

        #print("order file",self.doc)
        orders_record_list= list(self.doc.values())[1:]  # list is used to generate output file
        orders_record_list = orders_record_list
        SAP_plant_index = 0
        errorcode_list = [] # contains error code numbers
        latestDeliveryTime="NA"
        materialWeight_orders="NA"
        container_orders = "NA"
        containerWeight_orders = "NA"
        matPartsPerCont_orders = "NA"
        steelBskt_orders = "NA"
        basketWeight_orders = "NA"
        matPartsPerSteelBskt_orders = "NA"
        noOfSteelBsktPerCont_orders = "NA"
        weightSingleContFullCapacity = "NA"
        requiredContainer = "NA"
        requiredSteelBasket = "NA"
        totalWeightOfOrder = "NA"
        capacityUtilizationOfOrder = "NA"
        SAP_plant_assembling_orders = "NA"
        #lastEntryE

        if self.doc["Material"] in self.assembling_dict:
            Material= self.doc["Material"]
            #print(self.assembling_dict[Material])
            if len(self.assembling_dict[Material][0]) > 1:   ## check if material has more than one entry
                #assembling_dict[Material][5] = "SAP plant"
                if self.doc["from SAP Plant"] in self.assembling_dict[Material][5]:
                    SAP_plant_index = self.assembling_dict[Material][5].index(self.doc["from SAP Plant"])
                elif self.doc["to SAP Plant"] in self.assembling_dict[Material][5]:
                    SAP_plant_index = self.assembling_dict[Material][5].index(self.doc["to SAP Plant"])
                    errorcode_list.append("1") #"to SAP Plant"
                else:
                    errorcode_list.append("2") #"SAP plant not matched (neither from or to)"
            # fetch the entries according to plant index, example: [['1T02.154.642', '1T02.154.642'], [360, 48], ['1T31.156.618', '1T31.156.618'], [30, 4], [12, 12], ['1001', '1504']]
            container_orders = self.assembling_dict[Material][0][SAP_plant_index]
            matPartsPerCont_orders = self.assembling_dict[Material][1][SAP_plant_index]
            steelBskt_orders = self.assembling_dict[Material][2][SAP_plant_index]
            matPartsPerSteelBskt_orders = self.assembling_dict[Material][3][SAP_plant_index]
            noOfSteelBsktPerCont_orders = self.assembling_dict[Material][4][SAP_plant_index]
            SAP_plant_assembling_orders = self.assembling_dict[Material][5][SAP_plant_index]
            #print(SAP_plant_assembling_orders)
            #print(self.doc["Material"] )
            #print(noOfSteelBsktPerCont_orders)

            if (Material in self.error3_material_list) or (container_orders in self.error3_material_list) or (steelBskt_orders in self.error3_material_list): # check for material id, cotntainer id, steelbasekt id
                errorcode_list.append("3") # same Material,container id or steelbasket id having diffrent weights based on error1_list
            elif container_orders in self.missing_list:
                errorcode_list.append("4")# missing container id
            elif Material not in self.weight_dict:
                errorcode_list.append("6")
            else:
                containerWeight_orders = self.weight_dict[container_orders]
                basketWeight_orders = self.weight_dict[steelBskt_orders]
                materialWeight_orders = self.weight_dict[Material] #current value in orders
                piecesOrdered_orders = float(self.doc["pieces"].replace(",",""))# current value from order files
                if materialWeight_orders== 0:
                    errorcode_list.append("5")#Material weight zero
                else:
                    #calculation
                    weightSingleContFullCapacity =(matPartsPerCont_orders*materialWeight_orders)+(containerWeight_orders)+(noOfSteelBsktPerCont_orders*basketWeight_orders)
                    ###count the number of required containers
                    if matPartsPerCont_orders >=piecesOrdered_orders:
                        requiredContainer=1
                    elif piecesOrdered_orders%matPartsPerCont_orders==0:
                        requiredContainer=piecesOrdered_orders//matPartsPerCont_orders
                    else:
                        requiredContainer=(piecesOrdered_orders//matPartsPerCont_orders)+1
                    ##count the number of required steelbasket
                    if steelBskt_orders!="-1":
                        if matPartsPerSteelBskt_orders>=piecesOrdered_orders :
                            requiredSteelBasket=1
                        elif piecesOrdered_orders%matPartsPerSteelBskt_orders==0:
                            requiredSteelBasket=piecesOrdered_orders//matPartsPerSteelBskt_orders
                        else:
                            requiredSteelBasket=(piecesOrdered_orders//matPartsPerSteelBskt_orders)+1
                    else:
                        requiredSteelBasket=0
                    totalWeightOfOrder = (piecesOrdered_orders*materialWeight_orders)+(requiredContainer*containerWeight_orders)+(requiredSteelBasket*basketWeight_orders)
                    capacityUtilizationOfOrder =(totalWeightOfOrder/(weightSingleContFullCapacity*requiredContainer)*100)

                    self.calculateLastestDeliveryTimeOfOrders()
        else:
            errorcode_list.append("6") # Material available in orders and not in container_assembling
            #print("error 6")
            #print(self.doc["Material"] )
            #print(noOfSteelBsktPerCont_orders)
        # orders_record_list contains required infromation from orders file (from plant, material id,...) + calculated values
        #print("this",orders_record_list)
        orders_record_list.append(str(self.latestDeliveryDate))
        orders_record_list.append(str(self.latestDeliveryTime))
        orders_record_list.append(str(materialWeight_orders))
        orders_record_list.append(str(container_orders))
        orders_record_list.append(str(containerWeight_orders))
        orders_record_list.append(str(matPartsPerCont_orders))
        orders_record_list.append(str(steelBskt_orders))
        orders_record_list.append(str(basketWeight_orders))
        orders_record_list.append(str(matPartsPerSteelBskt_orders))
        orders_record_list.append(str(noOfSteelBsktPerCont_orders))
        orders_record_list.append(str(SAP_plant_assembling_orders))
        orders_record_list.append(str(weightSingleContFullCapacity))
        orders_record_list.append(str(requiredContainer))
        orders_record_list.append(str(requiredSteelBasket))
        orders_record_list.append(str(totalWeightOfOrder))
        orders_record_list.append(str(capacityUtilizationOfOrder))
        orders_record_list.append(str(",".join(errorcode_list)))
        self.orderCount+=1
        orders_record_list.append(str(self.orderCount))
        #print (orders_record_list)
        return orders_record_list

    def mainFunction(self):
        dest = open(self.dictionary["ordersCalculationOutput"],"w")
        dest.write("booking type" + "\t"+
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
            "container_id"+ "\t"+
            "container_weight(KG)"+"\t"+
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
            "orderIds"+ "\n")
        for doc in self.cursor:
            self.doc= doc
            # fetch container assembling file
            if "Material" in self.doc and "SAP plant" in self.doc:# first time used the doc
                #print(self.doc) #print container assembling file
                self.populateAssemblingDict()

            #fetch material weight file
            if "Material" in self.doc and ("weight" in self.doc or "Bruttogewicht" in self.doc):
                self.populateMaterialWeightDict()

            #fetch orders files
            if "Material" in doc and "from SAP Plant" in doc:
                 orders_record_list = self.filledOrdersCalculationAndErrorCodes()
                 if orders_record_list[-2]!="6":
                     emptyOrders_record_list = self.createEmptyOrders(orders_record_list)
                     dest.write("\t".join(orders_record_list)+"\n")
                 #if len(emptyOrders_record_list)>0:
                     dest.write("\t".join(emptyOrders_record_list)+"\n")
                     #del emptyOrders_record_list[:]
        ##create object for the Jisdataformat class
        jisDataFormat=Jisdataformat(self.dictionary["jisOrdersInputFile"],self.orderCount)
        ##following method read the Jis order input file and return the list containing the ouput
        jisOrderOutputList=jisDataFormat.readJisOrderInputFile()
        for record in jisOrderOutputList:
            dest.write("\t".join(record))
            dest.write("\n")
        dest.close()

if __name__=="__main__":
    databaseToOrderCalculation = Databasetoorderscalculation("config.yaml")
    databaseToOrderCalculation.mainFunction()
