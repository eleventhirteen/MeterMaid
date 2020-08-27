#
import subprocess
import time
import json
import logging,sys,traceback
import utility_meters as um

### housekeeping.
try:import config
except ImportError:raise

from database import Database
database = Database(config.mysql)

try:db = database.get_db()
except:raise

print(config.meters)
config.meters['test']={}

utility = um.UtilityMeter(database)

#begin.

if config.rtltcp.get("RTL_TCP"):
    # start the rtl device
    if config.debug:print("Sarting RTL_TCP on Port 5566")
    rtl_tcp = subprocess.Popen("/usr/bin/rtl_tcp -p 5566", stdout=subprocess.PIPE, shell=True)
    if config.debug:print("sleeping 15 seconds")
    time.sleep(15)   

print("Sarting RTLAMR")
rtlamr = subprocess.Popen("{} {}".format(config.rtlamr['PATH'],config.rtlamr["FLAGS"]), stdout=subprocess.PIPE, shell=True)


while True:
    output = rtlamr.stdout.readline()
    if output == '' and rtlamr.poll() is not None: break
    
    if output:
        data = json.loads(output.decode().strip())
        try:
            """ where things are processed """
                   
            protocol_type = data.get('Type')
            message_type = data.get('Message').get('Type')
            meter_type = None
            
            if 'SCM' in protocol_type and message_type in config.scm_electric: meter_type = "Electric"
            elif 'SCM' in protocol_type and message_type in config.scm_water: meter_type = "Water"
            elif 'SCM' in protocol_type and message_type in config.scm_gas: meter_type = "Gas"
            elif 'R900' in protocol_type: 
                meter_type = "water" # all I have are r900 water to test against. 
                #print(protocol_type,message_type,meter_type)
                utility.water_meter(data)
                
                        
        
        
        except:
             logging.debug(traceback.print_exc(file=sys.stdout))
        
    
    rc = rtlamr.poll()
