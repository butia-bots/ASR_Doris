#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import os
from pocketsphinx import LiveSpeech, get_model_path

model_path = get_model_path()
print(model_path)

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

def my_robot_talker():
    hello_pub = rospy.Publisher('doris/acr', String,queue_size=10)
    rospy.init_node('Speech_Recognition', anonymous=False)
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        for message in speech:
            print(message)
            rospy.loginfo(message)
            hello_pub.publish(message)
            rate.sleep()

if __name__=='__main__':
    #print(stt())
    try:
    	my_robot_talker()
    except rospy.ROSInterruptException:
    	print("Deu ruim!")


