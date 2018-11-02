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

rooms = ["bathroom", "bedroom", "closet", "dining", "garage", \
        "hall", "kitchen", "laundry", "living", "office", \
        "staircase", "corridor", "counter", "crowd", "ground", \
        "there"
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
            "microwave", "cupboard", "counter", "sink", "stove", "fridge", "freezer", "washing machine", "dishwasher", \
            "cabinet", \
            "bidet", "shower", "bathtub", "toilet", "towel rail", "bathroom cabinet", "washbasin", \
            "object", "objects" \
            "females", "female", "male", "males", "woman", "man", "women", "men", "children", "people", "elders", \
            "sheets"
            ]

object_action = ["lying", "standing", "dining", "wearing", "waiting", "sitting", "stored", "store"]

object_adj = ["white", "blue", "red", \
                "biggest", "smallest", "bigger"]

object_action = [locate, quantify, identify, identify_category, identify_same_category, identify_color]


####arena basic######
## Where is the <object> located - Where is the microwave located
# -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-
## How many <object> are in the <location> - How many doors are in the bathroom
# -> Action::quantify Object::doors Location::bathroom Object_action::- Object_adj::-
## In which room is the <object> - In which room is the microwave
# -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-

########object basic########
## Where can I find the <object>? - Where can I find the muesli?
# -> Action::locate Object::muesli Location::- Object_action::- Object_adj::-
## What objects are <objects_action> in the <location>? - What objects are stored in the drawer?
# -> Action::identify Object::- Location::drawer Object_action::stored Object_adj::-
## Between the <object> and <object>, which one is <object_adj>? - Between the chips and pringles, which one is bigger?
# -> Action::identify Object::chips, pringles Location::- Object_action::- Object_adj::bigger
## What is the category of the <object>? - What is the category of the pear?
# -> Action::identify_category Object::pear, pringles Location::- Object_action::- Object_adj::-
## Do the <object> and <object> belong to the same category? - Do the apple and tea spoon belong to the same category?
# -> Action::identify_same_category Object::apple, tea spoon Location::- Object_action::- Object_adj::-
## How many <objects> are <location>? - How many snacks are there?
# -> Action::quantify Object::snacks Location::there Object_action::- Object_adj::-
## Which is the <object_adj> <object>? - Which is the lightest drinks?
# -> Action::identify Object::drinks Location::- Object_action::- Object_adj::lighest
## What's the color of the <object>? - What's the color of the beer?
# -> Action::identify_color Object::beer Location::- Object_action::- Object_adj::-

#######crowd basic########
## Tell me how many <object> are <object_action> <objecy_adj> - Tell me how many people are wearing white
# -> Action::quantify Object::people Location::- Object_action::wearing Object_adj::white
## Tell me the number of <object> in the <location> - Tell me the number of men in the crowd
# -> Action::quantify Object::men Location::crowd Object_action::- Object_adj::-
## How many <object> are in the <location>? - How many women are in the crowd?
# -> Action::quantify Object::women Location::crowd Object_action::- Object_adj::-
## Was the person <object_action> a <object> or <object>? - Was the person sitting a man or woman?
# -> Action::identify Object::person Location::- Object_action::sitting Object_adj::-
## Tell me if the person <object_action> <object> or <object>? - Tell me if the person waving was a man?
# -> Action::identify Object::person Location::- Object_action::weaving Object_adj::-
## In which room is the <object> - In which room is the counter
# -> Action::locate Object::counter Location::- Object_action::- Object_adj::-

## How many <object> in the <location> are <object_action>? - How many people in the crowd are waving?
# -> Action::quantify Object::people Location::crowd Object_action::weaving Object_adj::-
# How many people in the crowd are standing or lying down?
# How many people in the crowd are raising their left arm?
# How many people in the crowd are raising their right arm?




# Doors == dollars


def find_object(words):
    temp = []
    flag = False
    for object in objects:
        if object in words:            
            temp.append(object)
            flag = True
            
    return temp, flag

def find_room(words):
    for object in rooms:
        if object in words:            
            return object, True
    
    return "", False

def find_object_action(words):
    temp = []
    flag = False
    for object in object_action:
        if object in words:            
            temp.append(object)
            flag = True
            
    return temp, flag

def find_object_adj(words):
    temp = []
    flag = False
    for object in object_adj:
        if object in words:            
            temp.append(object)
            flag = True
            
    return temp, flag


def treat_message(message):
    words = message.split()
    for i in range(0, len(words)):
        words[i] = words[i].lower()

    command = Command_basic()

    #tagged = nltk.pos_tag(words)
    #print("\nMsg_tagged: ",tagged)

    object_found = False
    location_found = False
    object_action_found = False
    object_adj_found = False

    print(words)

    # Where is the <object> located - Where is the microwave located
    # -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-
    # Where can I find the <object>? - Where can I find the muesli?
    # -> Action::locate Object::muesli Location::- Object_action::- Object_adj::-
    if "located" in words or "locate" in words or "localize" in words or "find" in words or "finded" in words:
        command.action = "locate"
        command.object, object_found = find_object(words)
        if object_found == False:
            print("I did not understand which object you want me to find")
        else:
            print("You want to know where the "+command.object[0]+" is")
        
    elif "how" in words:
        if "many" in words:
            command.action = "quantify" 
            # Tell me how many <object> are <object_action> <objecy_adj> - Tell me how many people are wearing white
            # -> Action::quantify Object::people Location::- Object_action::wearing Object_adj::white    
            if "tell" in words or "Tell" in words:
                command.object, object_found = find_object(words)
                command.object_action, object_action_found = find_object_action(words)
                command.object_adj, object_adj_found = find_object_adj(words)

                #melhorar issoo
                if object_found == False:
                    print("I did not understand which object you want me to quantify")
                if location_found == False:
                    print("I did not understand where you want me to quantify")
            
            # How many <object> in the <location> are <object_action>? - How many people in the crowd are waving?
            # -> Action::quantify Object::people Location::crowd Object_action::weaving Object_adj::-
            command.object_adj, object_adj_found = find_object_adj(words)
            if object_adj_found == True:
                command.object, object_found = find_object(words)
                command.location, location_found = find_room(words)
                if object_found == False and location_found == True:
                    print("I did not understand what "+command.object_adj[0]+" in the "+command.location+" you want me to quantify")
                elif object_found == True and location_found == False:
                    print("I did not understand the location of "+command.object[0]+command.object_adj[0]+" you want me to quantify")
                elif object_found == True and location_found == True:
                    print("You want to quantify the "+command.object[0]+command.object_adj[0]+" in the "+command.location)
                else:
                    print("I did not understand where you want me to quantify "+command.object_adj[0])

            # How many <object> are in the <location> - How many doors are in the bathroom
            # -> Action::quantify Object::doors Location::bathroom Object_action::- Object_adj::-
            # How many <object> are in the <location>? - How many women are in the crowd?
            # -> Action::quantify Object::women Location::crowd Object_action::- Object_adj::-
            # How many <objects> are <location>? - How many snacks are there?
            # -> Action::quantify Object::snacks Location::there Object_action::- Object_adj::-
            else:                
                command.object, object_found = find_object(words)
                command.location, location_found = find_room(words)
                if object_found == False and location_found == False:
                    print("I did not understand which object you want me to quantify")
                elif location_found == False and object_found == True:
                    print("I did not understand where you want me to quantify the "+command.object[0])
                elif location_found == True and object_found == False:
                    print("I did not understand what object you want me to quantify the "+command.location)
                else:
                    print("I did not understand what you want me to quantify")
    
    elif "which" in words and "between" not in words:
        # In which room is the <object> - In which room is the microwave
        # -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-
        # In which room is the <object> - In which room is the counter
        # -> Action::locate Object::counter Location::- Object_action::- Object_adj::-
        if "room" in words:
            command.action = "locate"
            command.object, object_found = find_object(words)
            if object_found == False:
                print("I did not understand which object you want me to find")
            else:
                print("You want to know where the "+command.object[0]+" is")

        # Which is the <object_adj> <object>? - Which is the lightest drinks?
        # -> Action::identify Object::drinks Location::- Object_action::- Object_adj::lighest
        else:
            command.action = "identify"
            command.object, object_found = find_object(words)
            command.object_adj, object_adj_found = find_object_adj(words)
            if object_found == False and object_adj_found == True:
                print("I did not understand what object you want me to say that is the "+command.object_adj[0])
            elif object_found == True and object_adj_found == False:
                print("I did not understand what what you want me to say about "+command.object[0])
            elif object_found == True and object_adj_found == True:
                print("You want me to say the "+command.object_adj+command.object[0])
            else:
                print("I did not understand what you want me to identify")

    # Between the <object> and <object>, which one is <object_adj>? - Between the chips and pringles, which one is bigger?
    # -> Action::identify Object::chips, pringles Location::- Object_action::- Object_adj::bigger
    elif "between" in words:      
        command.action = "locate"
        command.object, object_found = find_object(words)
        command.object_adj, object_adj_found = find_object_adj(words)
        
        if object_found == True and object_adj_found == False and len(command.object) == 1:
            print("I did not understand which object plus"+command.object[0]+" you want me to choose between")
        elif object_found == True and object_adj_found == False and len(command.object) == 2:
            print("I did not understand what you what me to say about "+command.object[0]+" and "+command.object[1])
        elif object_found == True and object_adj_found == True and len(command.object) == 1:
            print("I did not understand which object plus"+command.object[0]+" you want me to say what is "+command.object_adj[0])
        elif object_found == True and object_adj_found == True and len(command.object) == 2:
            print("You want me to say if "+command.object[0]+" or "+command.object[1]+" is "+command.object_adj[0])
        else:
            print("I did not understand which object you want me to choose between")

    # Tell me the number of <object> in the <location> - Tell me the number of men in the crowd
    # -> Action::quantify Object::men Location::crowd Object_action::- Object_adj::-
    elif "number" in words:
        command.action = "quantify" 
        command.object, object_found = find_object(words)
        command.location, location_found = find_room(words)
        if object_found == False and location_found == False:
            print("I did not understand which object you want me to quantify")
        elif location_found == False and object_found == True:
            print("I did not understand where you want me to quantify the "+command.object[0])
        elif location_found == True and object_found == False:
            print("I did not understand what object you want me to quantify the "+command.location)
        else:
            print("I did not understand what you want me to quantify")

    # Was the person <object_action> a <object> or <object>? - Was the person sitting a man or woman?
    # -> Action::identify Object::person Location::- Object_action::sitting Object_adj::-
    # Tell me if the person <object_action> <object> or <object>? - Tell me if the person waving was a man?
    # -> Action::identify Object::person Location::- Object_action::weaving Object_adj::-
    elif ("was" in words or "what's" in words or "what" in words or "tell" in words) and "person" in words:
        command.action = "identify"
        command.object, object_found = find_object(words)
        command.object_action, object_action_found = find_object_action(words)
        if object_found == False and object_action_found == True:
            print("I did not understand who you want me to identify "+command.object_action[0])
        elif object_found == True and (len(command.object) == 1) and object_action_found == True:
            print("You want me to identify if "+command.object[0]+" was "+command.object_action[0])
        elif object_found == True and (len(command.object) == 2) and object_action_found == True:
            print("You want me to identify if "+command.object[0]+" or "+command.object[1]+" was "+command.object_action[0])
        else:
            print("I did not understand what you want me to identify")

    # What is the category of the <object>? - What is the category of the pear?
    # -> Action::identify_category Object::pear, pringles Location::- Object_action::- Object_adj::-
    # Do the <object> and <object> belong to the same category? - Do the apple and tea spoon belong to the same category?
    # -> Action::identify_same_category Object::apple, tea spoon Location::- Object_action::- Object_adj::-
    elif "category" in words:
        if "belong" not in words:
            command.action = "identify_category"
            command.object, object_found = find_object(words)
            if object_found == True:
                print("You want to know the category of the "+command.object[0])
            else:
                print("I do not know what object you want me to categorize")
        else:
            command.action = "identify_same_category"
            command.object, object_found = find_object(words)
            if object_found == True and len(command.object) == 1:
                print("I did not understood each object you want me to compare with "+command.object[0])
            elif object_found == True and len(command.object) == 2:
                print("You want me to compare"+command.object[0]+" with "+command.object[1])
            else:
                print("I do not know what object you want me to compare its category")

    # What's the color of the <object>? - What's the color of the beer?
    # -> Action::identify Object::beer Location::- Object_action::- Object_adj::-
    elif "color" in words:
        command.action = "identify_color"
        command.object, object_found = find_object(words)
        if object_found == False:
            print("I did not understood each object you want me to say the color")
        else:
            print("You want to know th color of the "+command.object[0])


    # What objects are <objects_action> in the <location>? - What objects are stored in the drawer?
    # -> Action::identify Object::- Location::drawer Object_action::stored Object_adj::-
    elif "what" in words and ("object" in words or "objects" in words):
        command.action = "identify"
        command.object_action, object_action_found = find_object_action(words)
        command.location, location_found = find_room(words)
        if location_found == False and object_action_found == False: 
            print("You want me to identify what objects"+command.object_action[0]+"are in the "+command.location)
        elif location_found == True and object_action_found == False: 
            print("I did not understand what you want me to identify in the"+command.location)
        elif location_found == False and object_action_found == True: 
            print("I did not understand what you want me to identify "+command.object_action[0])
        else:
            print("I did not understand what you want me to identify")

    


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

