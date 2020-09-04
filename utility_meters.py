#!/usr/bin/env python3.4
import time
import datetime
from datetime import timezone
from dateutil import parser
from dateutil.tz import UTC
import config

class UtilityMeter:
    def __init__(self,database):
            
            self._database = database            
            self.meterID = None
            
            self.currentTime = None
            
            self.oldTime = None
            self.newTime = None
            
            self.timeDiff = None
            
            self.oldConsumption = None
            self.newConsumption = None
            self.currentConsumption = None

            
            
    def electric_meter(self, data):
        # convert power diff from kwh to kws
        #self.watts = (self.powerDiff * 3600 /self.timeDiff)
        """ something.  . ..  electric meter data processor"""

        dtime = data.get('Time')
        self.newTime = parser.parse(dtime)

        self.meterID = data.get('Message').get('ID')
        self.currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        
        self.newConsumption = data.get('Message').get('Consumption')
        
        self.meter_type = "Electric"

        if not self.meterID in config.meters.keys():
            if config.debug:print("first time seeing this id: {}".format(self.meterID))
            config.meters[self.meterID] = {"Time": self.newTime, "ID":self.meterID, "Consumption": self.newConsumption}
            return False
        else:

            self.oldConsumption = config.meters[self.meterID].get('Consumption')
            self.oldTime = config.meters[self.meterID].get('Time')

            # level shift.
            config.meters[self.meterID]['Consumption'] = self.newConsumption
            config.meters[self.meterID]['Time'] = self.newTime


            self.timeDiff = self.newTime - self.oldTime

            ##### DEbUG TAKE OUT.
            #if self.meterID in config.myMeters:print(data)

            if(self.timeDiff.total_seconds() < 0):print("Error: Time Diff Negative. Customer: %s. %d - %d = %d" % (self.meterID, self.newTime, self.oldTime, self.timeDiff))

            self.wattDiff = self.newConsumption - self.oldConsumption

            #if(self.wattDiff != 0):
            #if(self.wattDiff):
            if data.get('Message').get('Consumption'):

                #print(data)
                self.kwhPerMin = (self.wattDiff / (self.timeDiff.total_seconds() / 60)) / 100 # <-


                # if numbers are way out of range throw error
                if self.meterID in config.myMeters:
                    print("[%s] Customer %s Using %f kwh per minute. (consumption: %d) - (time elapsed: %d s) ### %d" % (self.currentTime, self.meterID, self.kwhPerMin, self.wattDiff, self.timeDiff.total_seconds(),self.newConsumption))
                else:
                    print("[%s] Customer %s Using %f kwh per minute. (consumption: %d) - (time elapsed: %d s)" % (self.currentTime, self.meterID, self.kwhPerMin, self.wattDiff, self.timeDiff.total_seconds()))
                
                self.log_data(data,self.wattDiff,self.kwhPerMin,"kwh/min")

            else:
                # consumption data hasn't changed. time shift back and wait some more.
                config.meters[self.meterID]['Time'] = self.oldTime
                config.meters[self.meterID]['Consumption'] = self.oldConsumption #redundant?
                self.log_data(data,0,0,"kwh/min")
            return True

    def gas_meter(self, data):
        """ something.  . ..  gas meter data processor"""

        dtime = data.get('Time')

        self.newTime = parser.parse(dtime)
        self.meterID = data.get('Message').get('ID')
        self.currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        self.newConsumption = data.get('Message').get('Consumption')
        
        self.meter_type = "Gas"

        if not self.meterID in config.meters.keys():
            if config.debug:print("first time seeing this id: {}".format(self.meterID))
            config.meters[self.meterID] = {"Time": self.newTime, "ID":self.meterID, "Consumption": self.newConsumption}
            return False
        else:

            self.oldConsumption = config.meters[self.meterID].get('Consumption')
            self.oldTime = config.meters[self.meterID].get('Time')

            # level shift.
            config.meters[self.meterID]['Consumption'] = self.newConsumption
            config.meters[self.meterID]['Time'] = self.newTime


            self.timeDiff = self.newTime - self.oldTime

            ##### DEbUG TAKE OUT.
            #if self.meterID in config.myMeters:print(data)

            if(self.timeDiff.total_seconds() < 0):print("Error: Time Diff Negative. Customer: %s. %d - %d = %d" % (self.meterID, self.newTime, self.oldTime, self.timeDiff))

            self.mcfDiff = self.newConsumption - self.oldConsumption

            #if(self.wattDiff != 0):
            #if(self.mcfDiff):
            
            if data.get('Message').get('Consumption'):
                #print(data)
                self.mcfPerMin = (self.mcfDiff / (self.timeDiff.total_seconds() / 60)) / 1000 # <-

                # if numbers are way out of range throw error
                if self.meterID in config.myMeters:
                    print("[%s] Customer %s Using %f mcf per minute. (consumption: %d) - (time elapsed: %d s) ### %d" % (self.currentTime, self.meterID, self.mcfPerMin, self.mcfDiff, self.timeDiff.total_seconds(),self.newConsumption))
                else:
                    print("[%s] Customer %s Using %f mcf per minute. (consumption: %d) - (time elapsed: %d s)" % (self.currentTime, self.meterID, self.mcfPerMin, self.mcfDiff, self.timeDiff.total_seconds()))

                self.log_data(data,self.mcfDiff,self.mcfPerMin,"mcf/min")
                
            else:
                # consumption data hasn't changed. time shift back and wait some more.
                config.meters[self.meterID]['Time'] = self.oldTime
                config.meters[self.meterID]['Consumption'] = self.oldConsumption #redundant?
                
                self.log_data(data,0,0,"mcf/min")

            return True


    def water_meter(self, data):
        """ something.  . ..  water meter data processor"""
    
        dtime = data.get('Time')
        
        self.newTime = parser.parse(dtime)
        
        self.meterID = data.get('Message').get('ID') 
        self.currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        
        self.currentConsumption = data.get('Message').get('Consumption')
        
        self.meter_type = "Water"
        
        if "900" in data.get("Type"):
            #Neptune R900 meters. Cu3/GPM 1/10
            self.newConsumption = data.get('Message').get('Consumption') / 10.0
        else:
            #Assuming others are 1:1 
            self.newConsumption = data.get('Message').get('Consumption')    

        if not self.meterID in config.meters.keys():
            if config.debug:print("first time seeing this id: {}".format(self.meterID))
            config.meters[self.meterID] = {"Time": self.newTime, "ID":self.meterID, "Consumption": self.newConsumption}
            return False
        else:
            
            self.oldConsumption = config.meters[self.meterID].get('Consumption')
            self.oldTime = config.meters[self.meterID].get('Time')
            
            # level shift.
            config.meters[self.meterID]['Consumption'] = self.newConsumption
            config.meters[self.meterID]['Time'] = self.newTime
            

            self.timeDiff = self.newTime - self.oldTime
                        
            ##### DEbUG TAKE OUT.
            #if self.meterID in config.myMeters:print(data)
            
            if(self.timeDiff.total_seconds() < 0):print("Error: Time Diff Negative. Customer: %s. %d - %d = %d" % (self.meterID, self.newTime, self.oldTime, self.timeDiff))
            
            self.waterDiff = (self.newConsumption - self.oldConsumption) 
            
            if(self.waterDiff != 0):
            # water meter only updates a static export every 7-15 minutes and repeats ~30. ignore unless something changed.
                if "900" in data.get("Type"):
                #Neptune R900 meters. Cu3/GPM 1/10
                    self.waterPerMin = self.waterDiff / (self.timeDiff.total_seconds() / 60) 

                else:
                    #Assuming others are 1:1
                    self.waterPerMin = self.waterDiff / (self.timeDiff.total_seconds() / 60)

                
                ### disply whats new and write to database.
                if self.meterID in config.myMeters:
                    print("[%s] Customer %s Using %f gallons per min. (consumption: %d) - (time elapsed: %d s) ### %d" % (self.currentTime, self.meterID, self.waterPerMin, self.waterDiff, self.timeDiff.total_seconds(),self.currentConsumption))
                else:
                    print("[%s] Customer %s Using %f gallons per min. (consumption: %d) - (time elapsed: %d s)" % (self.currentTime, self.meterID, self.waterPerMin, self.waterDiff, self.timeDiff.total_seconds()))
                
                self.log_data(data,self.waterDiff,self.waterPerMin,"gallons/min")

                    
            else:
                # consumption data hasn't changed. time shift back and wait some more.
                config.meters[self.meterID]['Time'] = self.oldTime
                config.meters[self.meterID]['Consumption'] = self.oldConsumption #redundant?
                
                # log no change to db for graph. test.
                self.log_data(data,0,0,"gallons/min")
                
            return True

    def log_data(self, data, diff=None, usage=None, measurement=None):

        sql = """
                INSERT INTO Utilities
                VALUES(0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        protocol = data.get('Type')
        message_type = data.get('Message').get('Type')
        consumption =  data.get('Message').get('Consumption')
        
        #print(self.newTime,self.meterID,protocol,message_type,self.meter_type,usage,measurement,consumption,diff,None)
        
        self._database.insert_db(sql,(
                            self.newTime,
                            self.meterID,
                            protocol,
                            message_type,
                            self.meter_type,
                            usage,
                            measurement,
                            consumption,
                            diff,
                            None
                            ))
        

