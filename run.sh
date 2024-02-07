#!/bin/bash
#
source /home/sso/udp-latency-corosync-monitor/venv/bin/activate
python3 /home/sso/udp-latency-corosync-monitor/monitor.py
deactivate
