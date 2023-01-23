# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4  9 00:09:40 2022

@author: Ranabhatt
"""

from lib.database_to_orders_calculations import Databasetoorderscalculation

databaseToOrderCalculation = Databasetoorderscalculation("config.yaml")
databaseToOrderCalculation.mainFunction()
