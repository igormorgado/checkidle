#!/usr/bin/env python3
import sys
import time
import subprocess
import os

# set idle time below (seconds)
idle_set = 1200

# Everything below this is idle (in packets)
net_idle_threshold = 100

# Everything below this is idle (in 1min load average)
sys_idle_threshold = 1


def get_packets(iface="eth0"):

    sysdir="/sys/class/net/{}/statistics/".format(iface)

    rxfile=os.path.join(sysdir,"rx_packets")
    txfile=os.path.join(sysdir,"tx_packets")

    try:
        rx = int(open(rxfile, "r").readline().strip())
        tx = int(open(txfile, "r").readline().strip())
    except IOError as e:
        print("Could not open statistics file")
        sys.exit(1)

    return  rx,tx



def l1m():
    return os.getloadavg()[0]


rx0,tx0 = get_packets()
la0 = l1m()

net_idle_time=0
sys_idle_time=0

while True:
    time.sleep(10)

    rx1,tx1 = get_packets()

    la1 = l1m()

    if all([rx1 - rx0 < net_idle_threshold, tx1 - tx0 < net_idle_threshold ]):
        net_idle_time += 10
    else:
        net_idle_time = 0

    if (la1 < sys_idle_threshold):
        sys_idle_time += 10
    else:
        sys_idle_time = 0



    if all([net_idle_time > idle_set, sys_idle_time > idle_set]):
        message="""
        Sending shutdown to 10 minutes right now. Cancel me with

        sudo shutdown -c

        If you want more 30 minutes.

        """
        net_idle_time = 0
        sys_idle_time = 0
        
        subprocess.Popen(["shutdown", "-h", "+10"])
        # gcloud alpha compute instances suspend instance-1


    # else:
        # print("net_idle_time: {}\tsys_idle_time: {}\trx0: {}\ttx0: {}\tla0: {}\trx1: {}\ttx1: {}\tla1: {}\trxD: {}\ttxD: {}\tlaD: {}".format(net_idle_time,sys_idle_time, rx0,tx0,la0 , rx1,tx1,la1, rx1-rx0,tx1-tx0,la1))
        # print("net_idle_time: {}\tsys_idle_time: {}".format(net_idle_time,sys_idle_time))
        # print("rx0: {}\ttx0: {}\tla0: {}".format(rx0,tx0,la0))
        # print("rx1: {}\ttx1: {}\tla1: {}".format(rx1,tx1,la1))
        # print("rxD: {}\ttxD: {}\tlaD: {}".format(rx1-rx0,tx1-tx0,la1))
        # print()

    rx0, tx0, la0 = rx1, tx1, la1
