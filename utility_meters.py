#!/usr/bin/env python3.4
import time
import datetime
from dateutil import parser
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
            
            
            
    def electric_meter(self, data):

        print(config.meters.get(data.get('Message').get('ID')))
        
        if not data.get('Message').get('ID') in config.meters.keys():
            config.meters[data.get('Message').get('ID')] = data
            return False
        else:
            print(config.meters)
            return True
            
        
    
        
        #time
        self.time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.watts = 0
        self.time2   = currTime
        self.consumption2  = currConsumption

        self.timeDiff = self.time2 - self.time1
        if(self.timeDiff < 0):
            print("Error: Time Diff Negative. Customer: %s. %d - %d = %d" % (self.mId, self.time2, self.time1, self.timeDiff))
        # min 5min granularity
        if(self.timeDiff >= 300):
            # figure out the power used in this time
            self.powerDiff = self.consumption2 - self.consumption1
            # if the power hasn't incremented then do nothing
            if(self.powerDiff != 0):
                # reset time1 and consumption1
                self.time1 = currTime
                self.consumption1 = currConsumption

                # convert power diff from kwh to kws
                self.watts = (self.powerDiff * 3600 /self.timeDiff)
                # if numbers are way out of range throw error
                if(self.watts > 10000 or self.watts < -10000):
                    print("Calculated use out of range! Got:")
                    print("[%s] Customer %s Using %f watts. %d Wh / %d s" % (self.time, self.mId, self.watts, self.powerDiff, self.timeDiff))
                    return -1
                print("[%s] Customer %s Using %f watts. %d Wh / %d s" % (self.time, self.mId, self.watts, self.powerDiff, self.timeDiff))

                # write to db
                self.dbCur.execute("insert into UtilityMeter(mId, mType, mTime, mTotalConsumption, mConsumed) values (%s, %d, %d, %d, %f)" % (self.mId, int(self.mType), int(currTime), int(currConsumption), self.watts))

        return self.watts

    # cubic feet / sec ??
    def gas_meter(self, data):
        #time
        self.time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.gasPerSec = 0
        self.time2  = currTime
        self.consumption2   = currConsumption

        self.timeDiff = self.time2 - self.time1
        if(self.timeDiff < 0):
            print("Error: Time Diff Negative. Customer: %s. %d - %d = %d" % (self.mId, self.time2, self.time1, self.timeDiff))
        # min 5min granularity
        if(self.timeDiff >= 300):
            # calculate gas / sec
            self.gasDiff = self.consumption2 - self.consumption1
            # if it hasn't changed do nothing
            if(self.gasDiff != 0):
                # reset time1 and consumption1
                self.time1 = currTime
                self.consumption1 = currConsumption

                self.gasPerSec = self.gasDiff / self.timeDiff
                # if numbers are way out of range throw error
                if(self.gasPerSec > 10000 or self.gasPerSec < -10000):
                    print("Calculated use out of range! Got:")
                    print("[%s] Customer %s Using %f cubic feet / sec. %d / %d s" % (self.time, self.mId, self.gasPerSec, self.gasDiff, self.timeDiff))
                    return -1
                print("[%s] Customer %s Using %f cubic feet / sec. %d / %d s" % (self.time, self.mId, self.gasPerSec, self.gasDiff, self.timeDiff))

                # write to db
                self.dbCur.execute("insert into UtilityMeter(mId, mType, mTime, mTotalConsumption, mConsumed) values (%s, %d, %d, %d, %f)" % (int(self.mId), int(self.mType), int(currTime), int(currConsumption), self.gasPerSec))

        return self.gasPerSec


    def water_meter(self, data):
        """ something.  . ..  water meter data processor"""
    
        dtime = data.get('Time')
        
        self.newTime = parser.parse(dtime)
        self.meterID = data.get('Message').get('ID') 
        
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
            
            ##### DEBUG TAKE OUT.
            #if self.meterID in config.myMeters:print(data)
            
            if(self.timeDiff.total_seconds() < 0):print("Error: Time Diff Negative. Customer: %s. %d - %d = %d" % (self.meterID, self.newTime, self.oldTime, self.timeDiff))
            
            self.waterDiff = self.newConsumption - self.oldConsumption

            if(self.waterDiff != 0):
                
                self.waterPerMin = self.waterDiff / (self.timeDiff.total_seconds() / 60)
                
                # if numbers are way out of range throw error
                if self.meterID in config.myMeters:
                    print("[%s] Customer %s Using %f gallons per min. (consumption: %d) - (time elapsed: %d s) ###" % (self.currentTime, self.meterID, self.waterPerMin, self.waterDiff, self.timeDiff.total_seconds()))
                else:
                    print("[%s] Customer %s Using %f gallons per min. (consumption: %d) - (time elapsed: %d s)" % (self.currentTime, self.meterID, self.waterPerMin, self.waterDiff, self.timeDiff.total_seconds()))
                    
            else:
                # consumption data hasn't changed. time shift back and wait some more.
                config.meters[self.meterID]['Time'] = self.oldTime
                config.meters[self.meterID]['Consumption'] = self.oldConsumption #redundant?
                
            return True
            