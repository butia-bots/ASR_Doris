#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import rospy

from gtts import gTTS
from kd_plugins.srv import SynthesizeVoice

def handle_speech_synthesis(req):
    tts = gTTS(text=req.text.decode('utf-8'), lang=req.lang)
    tts.save("hello.mp3")
    os.system("play hello.mp3")
    return 1

if __name__ == "__main__":
    rospy.init_node('speech_synthesis_server')
    s = rospy.Service('speech_synthesis', SynthesizeVoice, handle_speech_synthesis)
    print "Ready to synthesize DoRIS's voice."
    rospy.spin()