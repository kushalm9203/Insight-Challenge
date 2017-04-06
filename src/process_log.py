from __future__ import print_function
import os
import sys
import operator
import re
from datetime import datetime, timedelta
from collections import deque
import calendar


def active_hosts(f, base):
    
    out_file = os.path.join(base, "log_output", "hosts.txt")
    dct = {}
      
    for line in f:
        dct[line.split(" ", 1)[0]] = dct.get(line.split(" ", 1)[0], 0) + 1
      
    
    with open(out_file, 'w') as f_out:
        for i in sorted(dct, key=dct.get, reverse=True)[:10]: 
            print("".join([i, ",", str(dct[i])]), file = f_out)
            

def most_resources(f, base):
    
    out_file = os.path.join(base, "log_output", "resources.txt")
    dct = {}

    
    for line in f:
        idx = line.split("\"")[1]
        if len(idx.split()) == 1:
            idx = idx[0]
        else:
            idx = idx.split()[1]

        if line.rsplit(" ", 1)[1] == "-\n":
            num_bytes = 0
        else:
            num_bytes = int(line.rsplit(" ", 1)[1])
        dct[idx] = dct.get(idx, 0) + num_bytes

    with open(out_file, 'w') as f:
        for i in sorted(dct, key=dct.get, reverse=True)[:10]: 
            print(i, file = f)


def busiest_hours(f_in, base):
    
    out_file = os.path.join(base, "log_output", "hours.txt")
    dct = {}    
    
    mainlst = []
    
    count = 0
    delta = timedelta(seconds=3600)
    with open(out_file, 'w') as f_out:
        for line in f_in:
            
            dtimestring = re.split('[\[\]]', line)[1]
            dtimelist = re.split('[/ :]', dtimestring)
            
            dtime = datetime(int(dtimelist[2]), 7, int(dtimelist[0]), int(dtimelist[3]), int(dtimelist[4]), int(dtimelist[5]))
            
            dct[dtime] = dtimestring
            mainlst.append(dtime)
    
        for i in range(10): 
            start = 0
            end = 0
            maxim = 0
            diff = 0
            current = 1
            max_start = 0
            max_end = 0
            while end < len(mainlst)-1:
                end += 1
                diff = mainlst[end] - mainlst[start]                
                current += 1
                while diff > delta:
                    start += 1
                    diff = mainlst[end] - mainlst[start]
                    current -= 1
                if maxim < current:
                    
                    maxim = current
                    max_start = start
                    max_end = end

            print("".join([dct[mainlst[max_start]], ",", str(maxim)]), file=f_out)

            del mainlst[max_start:max_end+1]
        



def blocked_ip(f_in, base, months):
    
    out_file = os.path.join(base, "log_output", "blocked.txt")
    dct = {}    
    blocked = []
    
    
    count = 0
    delta1 = timedelta(seconds=20)
    delta2 = timedelta(seconds=300)
    with open(out_file, 'w') as f_out:

        prev_host = None
        for line in f_in:
            current_ele = False
            current = re.split('[\[\]]', line, 2)
            host = current[0].split()[0]
            
            dtimelist = re.split('[/: ]', current[1])
            dtime = datetime(int(dtimelist[2]), int(months[dtimelist[1]]), int(dtimelist[0]), int(dtimelist[3]), int(dtimelist[4]), int(dtimelist[5]))
            code = int(current[2].rsplit(" ", 2)[1])
            
            for b in blocked:
                if (dtime - b[1] > delta2) and host != b[0]:
                    blocked.remove(b)
                elif host == b[0]:
                    if dtime - b[len(b)-1] <= delta2:
                        b.pop(1)
                        b.append(dtime)
                        print(line, file=f_out)
                        current_ele = True
                    else:
                        blocked.remove(b)
                        current_ele = False

                
            if code != 401 and not current_ele:
                dct[host] = []
            
            elif code == 401:
                if dct.get(host, []) and (dtime - dct[host][0] <= delta1):
                    dct[host].append(dtime)
                    if len(dct[host]) == 3 and not current_ele:
                        blocked.append([host, dtime])
                    elif current_ele:
                        del dct[host][0]                  
                else:
                    dct[host] = [dtime]

                

months = dict((v,k) for k,v in enumerate(calendar.month_abbr))
base = os.path.dirname(os.getcwd())
in_file = os.path.join(base, "log_input", "log.txt")
with open(in_file) as f:    
    active_hosts(f, base)
    most_resources(f, base)
    busiest_hours(f, base)
    blocked_ip(f, base, months)
