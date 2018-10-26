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

# adb forward tcp:53516 tcp:53515

PORT = 53516
bufferSize = 1024
SAVE_TO_FILE = False

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', PORT)
print 'Connecting to %s port %s' % server_address
sock.connect(server_address)

rooms = ["bathroom", "bedroom", "closet", "dining room", "garage", \
        "hall", "kitchen", "laundry", "living room", "office", \
        "staircase", "corridor", "counter", "crowd"
        ]

objects = ["shampoo", "soap", "cloth", "sponge", "toothpaste",  
            "chips", "M and Ms", "pringles", "cookies", \
            "apple", "melon", "banana", "pear", "peach", \
            "pasta", "noodles", "tuna fish", "pickles", \
            "choco flakes", "Robo Os", "muesli", \
            "tea", "beer", "coke", "water", "milk", \
            "tea spoon", "spoon", "fork", "knife", "napkin", \
            "big dish", "small dish", "bowl", "glass", "mug", \
            "tray", "box", "bag", \
            "bed", "night table", "wardrobe", "dresser", "armchair", "drawer", "desk", \
            "sideboard", "cutlery drawer", "dining table", "chair", "baby chair", \
            "bookshelf", "sofa", "coffee table", "center table", "bar", "fireplace", "tv couch", \
            "microwave", "cupboard", "counter", "cabinet", "sink", "stove", "fridge", "freezer", "washing machine", "dishwasher", \
            "cabinet", \
            "bidet", "shower", "bathtub", "toilet", "towel rail", "bathroom cabinet", "washbasin", \
            "females", "female", "male", "males"
            ]

action = ["find", "finded", "tell", "how many"]

object_action = []

####arena basic######
# Where is the <object> located - Where is the microwave located
# -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-
# How many <object> are in the <room> - How many doors are in the bathroom
# -> Action::quantify Object::doors Location::bathroom Object_action::- Object_adj::-
# In which room is the <object> - In which room is the microwave
# -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-

#######crowd basic########
# Tell me how many <object> are <object_action> <objecy_adj> - Tell me how many people are wearing white
# -> Action::quantify Object::people Location::- Object_action::wearing Object_adj::white
# Tell me the number of <object> in the <location> - Tell me the number of men in the crowd
# -> Action::quantify Object::men Location::crowd Object_action::- Object_adj::-
# How many <object> are in the <location>? - How many women are in the crowd?
# -> Action::quantify Object::women Location::crowd Object_action::- Object_adj::-
# Was the <object> <object_action> a man or woman? - Was the person sitting a man or woman?
# -> Action::identify Object::person Location::- Object_action::sitting Object_adj::-
# How many <object> in the <location> are <object_action>? - How many people in the crowd are waving?
# -> Action::quantify Object::people Location::crowd Object_action::weaving Object_adj::-
# Tell me if the <object> <object_action> was a man? - Tell me if the person waving was a man?
# -> Action::identify Object::person Location::- Object_action::weaving Object_adj::-
# Was the <object> <object_action> a boy or girl? - Was the person lying down a boy or girl?
# -> Action::identify Object::person Location::- Object_action::lyingdown Object_adj::-
# In which room is the <object> - In which room is the counter
# -> Action::locate Object::counter Location::- Object_action::- Object_adj::-

########object basic########
# Where can I find the <object>? - Where can I find the muesli?
# -> Action::locate Object::muesli Location::- Object_action::- Object_adj::-
# What <object> are <objects_action> in the <location>? - What objects are stored in the drawer?
# -> Action::identify Object::objects Location::drawer Object_action::stored Object_adj::-
# Between the <object> and <object>, which one is <object_adj>? - Between the chips and pringles, which one is bigger?
# -> Action::identify Object::chips, pringles Location::- Object_action::- Object_adj::bigger
# What is the category of the <object>? - What is the category of the pear?
# -> Action::identify_category Object::pear, pringles Location::- Object_action::- Object_adj::-
# Do the <object> and <object> belong to the same category? - Do the apple and tea spoon belong to the same category?
# -> Action::identify_same_category Object::apple, tea spoon Location::- Object_action::- Object_adj::-
# How many <objects> are <location>? - How many snacks are there?
# -> Action::quantify Object::snacks Location::there Object_action::- Object_adj::-
# Which is the <object_adj> <object>? - Which is the lightest drinks?
# -> Action::identify Object::drinks Location::- Object_action::- Object_adj::lighest
# What's the <object_adj> of the <object>? - What's the color of the beer?
# -> Action::identify Object::beer Location::- Object_action::- Object_adj::color

def treat_message(message):
    words = message.split()
    command = Command_basic()

    tagged = nltk.pos_tag(words)
    print("\nMsg_tagged: ",tagged)




   
    if (len(tagged)) >= 2:
        #How many
        if tagged[0][1] == "WRB" and tagged[1][1] == "JJ":
            command.action = "quantify"
            if tagged[2][1] == "NN" or tagged[2][1] == "NNS":
                command.object = [tagged[2][0]]

            for tag in tagged:
                if tag[0] in rooms:
                    command.location = tag[0]

        # In Which
        if tagged[0][1] == "IN" and tagged[1][1] == "WDT":
            command.action = "locate"
            if tagged[2][1] == "NN" or tagged[2][1] == "NNS":
                command.object = [tagged[2][0]]

            for tag in tagged:
                if tag[0] in objects:
                    command.location = tag[0]
        # Where is
        if tagged[0][1] == "WRB" and tagged[1][1] == "VBZ":
            command.action = "locate"
            for tag in tagged:
                if tag[0] in objects:
                    command.object = [tag[0]]
        
    print(command.action, command.object, command.location, command.object_action, command.object_adj) 

    return command

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

