#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import os
from pocketsphinx import LiveSpeech, get_model_path
import pyttsx

model_path = get_model_path()
print(model_path)

engine = pyttsx.init()

speech = LiveSpeech(
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    hmm=os.path.join(model_path, 'en-us'),
    lm=os.path.join(model_path, 'en-us.lm.bin'),
    dic=os.path.join(os.path.expanduser("~/catkin_ws")+"/src/ASR_Doris/", 'doris.dict')
)

def treat_message(message):
    words = message.split()
    message = ""
    pub = False

    if "today" in words:
        if "day" in words:
            message = "What day is today?"
        else:
            message = "What day is today?"

    if "name" in words:
        if "your" in words:
            message = "What is your name?"
        elif "my" in words:
            message = "What is my name?"
        else:
            message = "What is my name?"

    if "kitchen" in words:
        if "go" in words:
            message = "Go to the kitchen"
        elif "where" in words:
            message = "Where is the kitchen"
        else:
            message =  "Where is the kitchen"
    
    if "people" in words:
        if "how many" in words:
            message =  "How many peoople are"
    
    if message != "":
        pub = True
        print("Command: "+message)
        engine.say(message)
        engine.runAndWait()

    return message, pub 
def my_robot_talker():
    hello_pub = rospy.Publisher('doris/acr', String,queue_size=10)
    rospy.init_node('Speech_Recognition', anonymous=False)
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        for raw_message in speech:
            print("Raw message: "+str(raw_message))
            message, pub = treat_message(str(raw_message))
            #rospy.loginfo(message)
            if pub == True:
                hello_pub.publish(message)
            rate.sleep()

if __name__=='__main__':
    #print(stt())
    try:
    	my_robot_talker()
    except rospy.ROSInterruptException:
    	print("Deu ruim!")


