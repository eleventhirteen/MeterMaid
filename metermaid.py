#
import subprocess
import time
import json
import logging,sys,traceback
import utility_meters as um

import asyncio
import sys
from asyncio.subprocess import PIPE, STDOUT


### housekeeping.
try:import config
except ImportError:raise

from database import Database
database = Database(config.mysql)

try:db = database.get_db()
except:raise

utility = um.UtilityMeter(database)

#begin.

if config.rtltcp.get("RTL_TCP"):
    # start the rtl device
    if config.debug:print("Sarting RTL_TCP on Port 5566")
    rtl_tcp = subprocess.Popen("/usr/bin/rtl_tcp -p 5566", stdout=subprocess.PIPE, shell=True)
    if config.debug:print("sleeping 15 seconds")
    time.sleep(15)   

# this feels gross but works. probably a more pythonic way to do this.
if config.myMetersOnly: 
    config.rtlamr["command"].append("--filterid={}".format(config.myMeters).replace('[','').replace(']','').replace(' ',''))
    

async def run_command(*args, timeout=None):

    print("Sarting RTLAMR ({})".format(" ".join(config.rtlamr['command'])))
    process = await asyncio.create_subprocess_exec(*args,stdout=PIPE, stderr=STDOUT)

    # Read line (sequence of bytes ending with b'\n') asynchronously
    while True:
        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout)
        except asyncio.TimeoutError:
            print("TIMEOUT!")
            process.kill() # Timeout or some criterion is not satisfied
            break
        else:
            if not line: # EOF
                print("Unexpected result. Not a valid data response!")
                break
            else:
                #do work.
                is_json = True
                try:data = json.loads(line.decode().strip())
                except:is_json = False
                if is_json:
                    try:
                        #where things are processed
                        protocol_type = data.get('Type')
                        message_type = data.get('Message').get('Type')
                        meter_type = None
                        if 'SCM' in protocol_type and message_type in config.scm_electric:
                            meter_type = "Electric"
                            utility.electric_meter(data)
                        elif 'SCM' in protocol_type and message_type in config.scm_water:
                            meter_type = "Water"
                            utility.water_meter(data)
                        elif 'SCM' in protocol_type and message_type in config.scm_gas:
                            meter_type = "Gas"
                            utility.gas_meter(data)
                        elif 'R900' in protocol_type:
                            meter_type = "Water" # neptune
                            utility.water_meter(data)
                    except: logging.debug(traceback.print_exc(file=sys.stdout))
    
    return await process.wait() # Wait for the child process to exit

if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop() # For subprocess' pipes on Windows
    asyncio.set_event_loop(loop)
else:
    loop = asyncio.get_event_loop()

while True:

    returncode = loop.run_until_complete(run_command(*config.rtlamr["command"],timeout=10))
    
    if returncode:	
        print("return code", returncode)
        print("something broke. let's wait it out for a bit and try again.")
        time.sleep(30)
        continue
        

loop.close()

