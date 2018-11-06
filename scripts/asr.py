#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from ASR_Doris_msgs.msg import *
import os
import time
from subprocess import Popen, PIPE, STDOUT
import socket
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

from nlp import *

# adb forward tcp:53516 tcp:53515

PORT = 53516
bufferSize = 1024
SAVE_TO_FILE = False

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', PORT)
print 'Connecting to %s port %s' % server_address
sock.connect(server_address)

def my_robot_talker():
    hello_pub = rospy.Publisher('doris/asr', Command_basic, queue_size=10)
    rospy.init_node('Speech_Recognition', anonymous=False)
    rate = rospy.Rate(1)
    try:
        # Send data
        message = 'mirror\n'
        print 'Sending mirror cmd'
        sock.sendall(message)
        while not rospy.is_shutdown():
            raw_message = sock.recv(bufferSize)
            print("Raw message: " + raw_message)
            message = treat_message(str(raw_message))                        
            hello_pub.publish(message)
            rate.sleep()
    finally:
        sock.close()

if __name__=='__main__':
    #print(stt())
    try:
    	my_robot_talker()
    except rospy.ROSInterruptException:
    	print("Deu ruim!")

