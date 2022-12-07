#!/bin/env python3
import sys, math, json;
from datetime import datetime

def print_help():
    print("usage: py_coords.py latitude longitude angle [ error_distance ]")
    print("lat,long refer to the traffic light, angle (0-360) is relative to north")
    print("and refers to the direction (from the traffic light's perspective)")
    print("the simulated vehicle (heading towards the traffic light) is coming from")
    print("If the traffic light expects vehicles approaching from the west, angle")
    print("should be around 270")
    sys.exit(1)

def print_request():
    if len(sys.argv) < 4:
        print_help()

    target = {}
    alpha_1=0.0
    try:
        target["lat"] = float(sys.argv[1]) #50.1234
        target["lon"] = float(sys.argv[2]) #8.123
        alpha_1 = 2 * math.pi * float(sys.argv[3]) / 360.0 #95
    except:
        print_help()

    distance_to_target = 40.0 #meter, distance between the argv provided position and the generated (fake) current position
    distance_to_last_pos = 10.0 #meter, distance between generated positions, 3 in total

    degree_to_meter = 10000000.0 / 90.0 #10.000 km ~ 1/4 of earth's circumference = 90 degrees
    lon_factor = math.cos((target["lat"]*math.pi)/(90*2)) #1 degree (lat) has always fixed length, but this is not true for lon-degrees

    #  s---l---c-----------------------traffic-light (from argv)
    #  |   |   | ^
    #  |   |   | | optional position error for testing the valid range
    #  |   |   | v 
    #  e   e   e

    simulated_error_distance = 0
    try:
        simulated_error_distance = float(sys.argv[4])
    except:
        pass

    alpha_error = alpha_1 + (math.pi/2) #+90 degrees
    #alpha_2 = alpha_1 + math.pi

    current_pos = {}
    current_pos["lat"] = target["lat"] + ((math.cos(alpha_1) * distance_to_target) + math.cos(alpha_error) * simulated_error_distance) / degree_to_meter
    current_pos["lon"] = target["lon"] + ((math.sin(alpha_1) * distance_to_target) + math.sin(alpha_error) * simulated_error_distance) / (degree_to_meter*lon_factor)

    #error_distance missing atm
    last_pos = {}
    last_pos["lat"] = current_pos["lat"] + (math.cos(alpha_1) * distance_to_last_pos) / degree_to_meter
    last_pos["lon"] = current_pos["lon"] + (math.sin(alpha_1) * distance_to_last_pos) / (degree_to_meter*lon_factor)

    sec_last_pos = {}
    sec_last_pos["lat"] = current_pos["lat"] + (math.cos(alpha_1) * distance_to_last_pos*2) / degree_to_meter
    sec_last_pos["lon"] = current_pos["lon"] + (math.sin(alpha_1) * distance_to_last_pos*2) / (degree_to_meter*lon_factor)

    #keys refer to utc values in the template file as well as to the duration in ms to substract from time.now(), respectively
    gps_record_order = {0 : current_pos, 1000 : last_pos, 2000 : sec_last_pos}
    f = open('template.json') #fixme: use path relative to script location instead of cwd

    time_now = int(datetime.now().strftime("%s")) * 1000 #seconds since 1970(?) multiplied by 1000 to get milliseconds
    post_payload = json.load(f)
    post_payload["utcTime"] = time_now
    for record in post_payload["gpsRecords"]:
        pos = gps_record_order[record["utcTime"]] #current_pos, last_pos or sec_last_pos
        record["latitude"] = pos["lat"]
        record["longitude"] = pos["lon"]
        record["utcTime"] = time_now - record["utcTime"] #0, 1000, 2000
        record["speed"] = distance_to_last_pos #m/s
        record["heading"] = (((alpha_1 + math.pi) % (2*math.pi)) / (2*math.pi)) * 360.0 #reverse the argv heading, normalize to [0,360]
        record["distance"] = distance_to_last_pos #meter

    print(json.dumps(post_payload, indent=4))
    f.close()


if __name__ == "__main__":
    print_request()
