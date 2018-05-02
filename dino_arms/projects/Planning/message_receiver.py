#!/usr/bin/env python

import rospy
import rospkg
from irl.msg import Real_Cube, Grid_Cube, Real_Structure, Grid_Structure, Cube_Structures
from std_msgs.msg import String

import getpass, imaplib
import time

'''
arms.irl2018@gmail.com
Password: PolluxCastor2018
'''

class MessageReceiver(object):
    """
    The class that receives message from email, parse and re-send the message to
    the build_cmd ros topic.
    """
    def __init__(self):
        rospy.init_node("message_receiver")

        self.cmd_pub = rospy.Publisher("/build_cmd", Cube_Structures, queue_size=1)
        self.is_receiving = False
        self.previous_subject = ""

    def receive_email(self):
        username= 'arms.irl2018@gmail.com'
        password= 'PolluxCastor2018'

        # login to mail service
        M = imaplib.IMAP4_SSL('imap.gmail.com', '993')
        # M.login(username, getpass.getpass())
        M.login(username, password)

        M.select()
        typ, data = M.search(None, 'ALL')

        # read from the most recent email
        num = data[0][-1]
        typ, data = M.fetch(num, '(RFC822)')
        subject = data[0][1].split('\r\n')[11]
        body = data[0][1].split('\r\n')[15]
        M.close()
        M.logout()

        if subject != self.previous_subject and self.is_receiving:
            cube_structure = Cube_Structures()
            coords = body.split(',')
            real_building = Real_Structure()
            coords = coords[0:len(coords)-1]

            for i in range(len(coords) / 6):
                real_building.building.append(Real_Cube(x=float(coords[i*3]), y=float(coords[i*3+1]), z=float(coords[i*3+2])))
            cube_structure.real_building = real_building

            grid_building = Grid_Structure()
            for i in range(len(coords)/6, len(coords)/3):
                grid_building.building.append(Grid_Cube(x=int(coords[i*3]), y=int(coords[i*3+1]), z=int(coords[i*3+2])))
            cube_structure.grid_building = grid_building

            # print(cube_structure)
            self.cmd_pub.publish(cube_structure)

        self.previous_subject = subject
        self.is_receiving = True

    def run(self):
        print("Message Receiver Running")

        while not rospy.is_shutdown():
            try:
                self.receive_email()
                time.sleep(5)
            except KeyboardInterrupt:
                break

if __name__=="__main__":
    mr = MessageReceiver()
    mr.run()
