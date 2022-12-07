#!/bin/env python3
import sys, json;
data = json.load(sys.stdin)
for sg in data["predictionSignalgroups"]:
    if sg["level"] == 0:
        print(sg["prediction"].replace(";","\n"))
