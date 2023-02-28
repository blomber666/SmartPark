#!/bin/bash
wg-quick down raspberry1 &
wait
wg-quick up raspberry1 &
wait

python /home/pi/yolov5/detect.py --weights /home/pi/yolo5/runs/best.pt --source 0 &> /home/pi/yolo.log &
python /home/pi/ultrasonic.py &> /home/pi/ultrasonic.log


