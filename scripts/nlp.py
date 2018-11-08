import rospy
from std_msgs.msg import String
from ASR_Doris_msgs.msg import *
import os
import time
from subprocess import Popen, PIPE, STDOUT
import speech_recognition as sr

from gtts import gTTS

rooms = ["bathroom", "bedroom", "closet", "dining", "garage", \
        "hall", "kitchen", "laundry", "living", "office", \
        "staircase", "corridor", "counter", "crowd", "ground", \
        "there", "drawer", "shelf"
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
            "sideboard", "cutlery drawer", "dining", "table", "chair", "baby chair", \
            "bookshelf", "sofa", "coffee table", "center table", "bar", "fireplace", "tv couch", \
            "microwave", "cupboard", "counter", "sink", "stove", "fridge", "freezer", "washing machine", "dishwasher", \
            "cabinet", \
            "bidet", "shower", "bathtub", "toilet", "towel rail", "bathroom cabinet", "washbasin", \
            "object", "objects" \
            "females", "female", "male", "males", "woman", "man", "women", "men", "children", "people", "elders", \
            "sheets", "coke", "sofa", "bed", "television", "bottle", "can", "yogurt", "tea", "juice", "cookie", "schweppes", "soap", "cereal", \
            "chair", "chairs", "doors", "drawer", "soda"
            ]

object_action = ["lying", "standing", "dining", "wearing", "waiting", "sitting", "stored", "store", "pointing", "raising", "waving"]

object_adj = ["white", "blue", "red", \
                "biggest", "smallest", "bigger", "left", "right", "arm", "leg", "lighest"]

actions = ["locate", "identify", "quantify", "identify_category", "identify_same_category", "identify_color", "identify_if"]



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

def voice(text):
    tts = gTTS(text=text)
    tts.save("hello.mp3")
    os.system("play hello.mp3")


def treat_message(message):
    words = message.translate(None, '!@#$"').split()
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
    
    if 'located' in words:
        print("adsfasdfawef32")
    else:
        print(words[0])

    # Where is the <object> located - Where is the microwave located
    # -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-
    # Where can I find the <object>? - Where can I find the muesli?
    # -> Action::locate Object::muesli Location::- Object_action::- Object_adj::-
    if "located" in words or "locate" in words or "localize" in words or "find" in words or "finded" in words:
        command.action = "locate"
        command.object, object_found = find_object(words)
        if object_found == False:
            voice("I did not understand which object you want me to find")
        else:
            voice("You want to know where the "+command.object[0]+" is located")
        
    elif "many" in words:
        command.action = "quantify" 
        # Tell me how many <object> are <object_action> <objecy_adj> - Tell me how many people are wearing white
        # -> Action::quantify Object::people Location::- Object_action::wearing Object_adj::white    
        if "tell" in words or "Tell" in words:
            command.object, object_found = find_object(words)
            command.object_action, object_action_found = find_object_action(words)
            command.object_adj, object_adj_found = find_object_adj(words)

            #melhorar issoo
            
            if object_found == True and location_found == False and object_adj_found == True and object_action_found == False:
                voice("I did not understand the location and the action of the "+command.object[0]+" you want me to quantify with "+command.object_adj[0])
            elif object_found == True and location_found == False and object_adj_found == False and object_action_found == False:
                voice("I did not understand the location, the action and its feature of the "+command.object[0]+" you want me to quantify ")
            elif object_found == True and location_found == True and object_adj_found == False and object_action_found == False:
                voice("I did not understand the feature adn the action of the "+command.object[0]+" in the "+command.location+" you want me to quantify")
            elif object_found == False and location_found == True and object_adj_found == False and object_action_found == False:
                voice("I did not understand which object in the "+command.location+" you want me to quantify")
            elif object_found == False and location_found == True and object_adj_found == True and object_action_found == False:
                voice("I did not understand which object in the "+command.location+" with "+command.object_adj[0]+" you want me to quantify")
            elif object_found == False and location_found == False and object_adj_found == True and object_action_found == False:
                voice("I did not understand which object and the location with "+command.object_adj[0]+" that you want me to quantify")  
            elif object_found == True and location_found == True and object_adj_found == True and object_action_found == False:
                voice("I did not understand the object action of the object in the "+command.location+" with "+command.object_adj[0]+" you want me to quantify") 

            elif object_found == True and location_found == False and object_adj_found == True and object_action_found == True:
                voice("I did not understand the location of the "+command.object[0]+" "+command.object_adj[0]+" "+command.object_adj[0]+" you want me to quantify")
            elif object_found == True and location_found == False and object_adj_found == False and object_action_found == True:
                voice("I did not understand the location and the feature of the "+command.object_action[0]+" "+command.object[0]+" you want me to quantify ")
            elif object_found == True and location_found == True and object_adj_found == False and object_action_found == True:
                voice("I did not understand the feature of the "+command.object_action[0]+" "+command.object[0]+" in the "+command.location+" you want me to quantify")
            elif object_found == False and location_found == True and object_adj_found == False and object_action_found == True:
                voice("I did not understand which object "+command.object_action[0]+" in the "+command.location+" you want me to quantify")
            elif object_found == False and location_found == True and object_adj_found == True and object_action_found == True:
                voice("I did not understand which object in the "+command.location+" are "+command.object_action[0]+" "+command.object_adj[0]+" you want me to quantify")
            elif object_found == False and location_found == False and object_adj_found == True and object_action_found == True:
                voice("I did not understand which object and the location for "+command.object_action[0]+" "+command.object_adj[0]+" that you want me to quantify")  
            elif object_found == True and location_found == True and object_adj_found == True and object_action_found == True:
                voice(" You want me to quantify "+command.object[0]+" in the "+command.location+" "+command.object_action[0]+" "+command.object_adj[0])         

        # How many <object> in the <location> are <object_action>? - How many people in the crowd are waving?
        # -> Action::quantify Object::people Location::crowd Object_action::weaving Object_adj::-
        # How many people in the crowd are standing or lying down?
        # How many people in the crowd are raising their left arm?
        # How many people in the crowd are raising their right arm?
        command.object_action, object_action_found = find_object_action(words)
        if object_action_found == True:
            #command.object, object_found = find_object(words)
            command.object = ["people"]
            #command.location, location_found = find_room(words)
            command.location = "crowd"
            command.object_adj, object_adj_found = find_object_adj(words)
        
            if len(command.object_action) == 1 and object_adj_found == False:
                voice("You want me to quantify the people in the crowd "+command.object_action[0])
            elif len(command.object_action) == 1 and object_adj_found == True:
                voice("You want me to quantify the people in the crowd "+command.object_action[0]+" to the "+command.object_adj[0])
            elif len(command.object_action) == 2:
                voice("You want me to quantify the people in the crowd "+command.object_action[0]+" or "+command.action[1])
            else:
                voice("I did not understand what you want me to quantify about the people in the crowd")

        # How many <object> are in the <location> - How many doors are in the bathroom
        # -> Action::quantify Object::doors Location::bathroom Object_action::- Object_adj::-
        # How many <object> are in the <location>? - How many women are in the crowd?
        # -> Action::quantify Object::women Location::crowd Object_action::- Object_adj::-
        # How many <objects> are <location>? - How many snacks are there?
        # -> Action::quantify Object::snacks Location::there Object_action::- Object_adj::-
        else:                
            command.object, object_found = find_object(words)
            command.location, location_found = find_room(words)
            if object_found == True and location_found == True:
                voice("You want me to quantify the "+command.object[0]+" in the "+command.location)
            elif location_found == False and object_found == True:
                voice("I did not understand where you want me to quantify the "+command.object[0])
            elif location_found == True and object_found == False:
                voice("I did not understand what object you want me to quantify the "+command.location)
            else:
                voice("I did not understand what you want me to quantify")

    elif "which" in words and "between" not in words:
        # In which room is the <object> - In which room is the microwave
        # -> Action::locate Object::microwave Location::- Object_action::- Object_adj::-
        # In which room is the <object> - In which room is the counter
        # -> Action::locate Object::counter Location::- Object_action::- Object_adj::-
        if "room" in words:
            command.action = "locate"
            command.object, object_found = find_object(words)
            if object_found == False:
                voice("I did not understand which object you want me to find")
            else:
                voice("You want to know where the "+command.object[0]+" is located")

        # Which is the <object_adj> <object>? - Which is the lightest drinks?
        # -> Action::identify Object::drinks Location::- Object_action::- Object_adj::lighest
        else:
            command.action = "identify"
            command.object, object_found = find_object(words)
            command.object_adj, object_adj_found = find_object_adj(words)
            if object_found == False and object_adj_found == True:
                voice("I did not understand what object you want me to say that is the "+command.object_adj[0])
            elif object_found == True and object_adj_found == False:
                voice("I did not understand what what you want me to say about "+command.object[0])
            elif object_found == True and object_adj_found == True:
                voice("You want me to say the "+command.object_adj+" "+command.object[0])
            else:
                voice("I did not understand what you want me to identify")

    # Between the <object> and <object>, which one is <object_adj>? - Between the chips and pringles, which one is bigger?
    # -> Action::identify Object::chips, pringles Location::- Object_action::- Object_adj::bigger
    elif "between" in words:      
        command.action = "identify"
        command.object, object_found = find_object(words)
        command.object_adj, object_adj_found = find_object_adj(words)
        
        if object_found == True and object_adj_found == False and len(command.object) == 1:
            voice("I did not understand which object plus"+command.object[0]+" you want me to choose between")
        elif object_found == True and object_adj_found == False and len(command.object) == 2:
            voice("I did not understand what you what me to say about "+command.object[0]+" and "+command.object[1])
        elif object_found == True and object_adj_found == True and len(command.object) == 1:
            voice("I did not understand which object plus"+command.object[0]+" you want me to say what is "+command.object_adj[0])
        elif object_found == True and object_adj_found == True and len(command.object) == 2:
            voice("You want me to say if "+command.object[0]+" or "+command.object[1]+" is "+command.object_adj[0])
        else:
            voice("I did not understand which object you want me to choose between")

    # Tell me the number of <object> in the <location> - Tell me the number of men in the crowd
    # -> Action::quantify Object::men Location::crowd Object_action::- Object_adj::-
    elif "number" in words:
        command.action = "quantify" 
        command.object, object_found = find_object(words)
        command.location, location_found = find_room(words)
        if object_found == False and location_found == False:
            voice("I did not understand which object you want me to quantify")
        elif location_found == False and object_found == True:
            voice("I did not understand where you want me to quantify the "+command.object[0])
        elif location_found == True and object_found == False:
            voice("I did not understand what object you want me to quantify in the "+command.location)
        else:
            voice("You want me to quantify the "+command.object[0]+" in the "+command.location)

    # Was the person <object_action> a <object> or <object>? - Was the person sitting a man or woman?
    # -> Action::identify Object::person Location::- Object_action::sitting Object_adj::-
    # Tell me if the person <object_action> <object> or <object>? - Tell me if the person waving was a man?
    # -> Action::identify Object::person Location::- Object_action::weaving Object_adj::-
    elif ("was" in words or "what's" in words or "what" in words or "tell" in words) and "person" in words:
        command.action = "identify_if"
        command.object, object_found = find_object(words)
        command.object_action, object_action_found = find_object_action(words)
        if object_found == False and object_action_found == True:
            voice("I did not understand who you want me to identify "+command.object_action[0])
        elif object_found == True and (len(command.object) == 1) and object_action_found == True:
            voice("You want me to identify if "+command.object[0]+" was "+command.object_action[0])
        elif object_found == True and (len(command.object) == 2) and object_action_found == True:
            voice("You want me to identify if "+command.object[0]+" or "+command.object[1]+" was "+command.object_action[0])
        else:
            voice("I did not understand what you want me to identify")

    # What is the category of the <object>? - What is the category of the pear?
    # -> Action::identify_category Object::pear, pringles Location::- Object_action::- Object_adj::-
    # Do the <object> and <object> belong to the same category? - Do the apple and tea spoon belong to the same category?
    # -> Action::identify_same_category Object::apple, tea spoon Location::- Object_action::- Object_adj::-
    elif "category" in words:
        if "belong" not in words:
            command.action = "identify_category"
            command.object, object_found = find_object(words)
            if object_found == True:
                voice("You want to know the category of the "+command.object[0])
            else:
                voice("I do not know what object you want me to categorize")
        else:
            command.action = "identify_same_category"
            command.object, object_found = find_object(words)
            if object_found == True and len(command.object) == 1:
                voice("I did not understand the object you want me to compare with "+command.object[0])
            elif object_found == True and len(command.object) == 2:
                voice("You want me to compare the category "+command.object[0]+" with "+command.object[1])
            else:
                voice("I do not know what object you want me to compare its category")

    # What's the color of the <object>? - What's the color of the beer?
    # -> Action::identify Object::beer Location::- Object_action::- Object_adj::-
    elif "color" in words:
        command.action = "identify_color"
        command.object, object_found = find_object(words)
        if object_found == False:
            voice("I did not understand the object you want me to say the color")
        else:
            voice("You want to know th color of the "+command.object[0])


    # What objects are <objects_action> in the <location>? - What objects are stored in the drawer?
    # -> Action::identify Object::- Location::drawer Object_action::stored Object_adj::-
    elif "what" in words and ("object" in words or "objects" in words):
        command.action = "identify"
        command.object_action, object_action_found = find_object_action(words)
        command.location, location_found = find_room(words)
        if location_found == True and object_action_found == True: 
            voice("You want me to identify what objects are "+command.object_action[0]+" in the "+command.location)
        elif location_found == True and object_action_found == False: 
            voice("I did not understand what you want me to identify in the "+command.location)
        elif location_found == False and object_action_found == True: 
            voice("I did not understand what you want me to identify "+command.object_action[0])
        else:
            voice("I did not understand what you want me to identify")

    elif "what" in words and "today" in words:
	command.action = "identify"
	command.object = "day"
	voice("Today is the november eighth, two thousand and eighteen")

    elif "finished" in words or "finish" in words:
	command.action = "finish"

    elif len(words) > 1:
        voice("I did not understand what you said")

    print(command.action, command.object, command.location, command.object_action, command.object_adj) 

    return command
