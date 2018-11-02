# Automatic Speech Recognition Doris

Arena Basic
Where is the <object> located - Where is the microwave located
-> Action::locate Object::microwave Location::- Object_action::- Object_adj::-
How many <object> are in the <location> - How many doors are in the bathroom
-> Action::quantify Object::doors Location::bathroom Object_action::- Object_adj::-
In which room is the <object> - In which room is the microwave
-> Action::locate Object::microwave Location::- Object_action::- Object_adj::-

Object Basic
Where can I find the <object>? - Where can I find the muesli?
-> Action::locate Object::muesli Location::- Object_action::- Object_adj::-
What objects are <objects_action> in the <location>? - What objects are stored in the drawer?
-> Action::identify Object::- Location::drawer Object_action::stored Object_adj::-
Between the <object> and <object>, which one is <object_adj>? - Between the chips and pringles, which one is bigger?
-> Action::identify Object::chips, pringles Location::- Object_action::- Object_adj::bigger
What is the category of the <object>? - What is the category of the pear?
-> Action::identify_category Object::pear, pringles Location::- Object_action::- Object_adj::-
Do the <object> and <object> belong to the same category? - Do the apple and tea spoon belong to the same category?
-> Action::identify_same_category Object::apple, tea spoon Location::- Object_action::- Object_adj::-
How many <objects> are <location>? - How many snacks are there?
-> Action::quantify Object::snacks Location::there Object_action::- Object_adj::-
Which is the <object_adj> <object>? - Which is the lightest drinks?
-> Action::identify Object::drinks Location::- Object_action::- Object_adj::lighest
What's the color of the <object>? - What's the color of the beer?
-> Action::identify Object::beer Location::- Object_action::- Object_adj::-

Crowd Basic
Tell me how many <object> are <object_action> <objecy_adj> - Tell me how many people are wearing white
-> Action::quantify Object::people Location::- Object_action::wearing Object_adj::white
Tell me the number of <object> in the <location> - Tell me the number of men in the crowd
-> Action::quantify Object::men Location::crowd Object_action::- Object_adj::-
How many <object> are in the <location>? - How many women are in the crowd?
-> Action::quantify Object::women Location::crowd Object_action::- Object_adj::-
Was the person <object_action> a <object> or <object>? - Was the person sitting a man or woman?
-> Action::identify Object::person Location::- Object_action::sitting Object_adj::-
Tell me if the person <object_action> <object> or <object>? - Tell me if the person waving was a man?
-> Action::identify Object::person Location::- Object_action::weaving Object_adj::-
In which room is the <object> - In which room is the counter
-> Action::locate Object::counter Location::- Object_action::- Object_adj::-

TO BE DONE
How many <object> in the <location> are <object_action>? - How many people in the crowd are waving?
-> Action::quantify Object::people Location::crowd Object_action::weaving Object_adj::-
How many people in the crowd are standing or lying down?
How many people in the crowd are raising their left arm?
How many people in the crowd are raising their right arm?

## Usage
Node:

***Speech_Recognition*** 

Topic - Type of message

***doris/asr*** - std_msgs/Command_basic.msg
string action
string[] object
string location
string[] object_action
string[] object_adj

This package continuosly reads from the app trought usb, decoding the inputs to a proper command. Then it publishes it on the /doris/asr topic
The type of message is a std_msgs String.




