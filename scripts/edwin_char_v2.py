#!/usr/bin/env python
import rospkg
import rospy
import math
import time

import csv
from std_msgs.msg import String
from edwin.msg import Bones
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import random

class Gestures:
    def __init__(self,skeleton):
        self.skeleton = skeleton
        rospy.init_node('gestures', anonymous=True)
        rospy.Subscriber('/skeleton', Bones, self.data_callback)
        self.number =0
        self.bow = 0
        self.disco = 0
        self.check = 0
        self.pub = rospy.Publisher('skeleton_points', String, queue_size=10)
        self.trainingSet = []
        self.testSet = []
        self.labels_test =[]
        self.labels_train = []
        self.data_from_sub = []
        self.gestures = {"bow":0,"bow1":0, "bow2":0, "dab":0,"disco":0,"disco1":0,"disco2":0,"heart":0,"high_five":0,"hug":0,
          "rub_tummy":0,"star":0,"touch_head":0,"wave":0}
        with open('skeleton.csv', 'r') as csvfile:
            lines = csv.reader(csvfile)
            labels =[]
            dataset =[]
            for rows in lines:
                labels.append(rows[0])
                dataset.append(rows[1:])
            dataset= dataset[1:]
            #labels= labels[1:]
            #print(dataset)
            for i in dataset:
                for l in range(len(i)):
                    if l % 3 == 0:
                        i[l]= float(i[l])+float(i[3])
                    if l % 3 == 1:
                        i[l]= float(i[l])+float(i[4])
                    if l % 3 == 2:
                        i[l]= float(i[l])+float(i[5])
            #print(labels)
            #print(dataset)
            for x in range(len(dataset)-1):
                if random.random() < .8 :
                    self.trainingSet.append(dataset[x])
                    self.labels_train.append(labels[x])
                else:
                    self.testSet.append(dataset[x])
                    self.labels_test.append(labels[x])
        self.neighbors= KNeighborsClassifier()
        time.sleep(2)
        #recieving data in forms of a list of tuples

    def data_callback(self,data):
        self.data_from_sub = []
        self.data_from_sub.extend([data.h.x,data.h.y,data.h.z])
        self.data_from_sub.extend([data.n.x,data.n.y,data.n.z])
        self.data_from_sub.extend([data.t.x,data.t.y,data.t.z])
        self.data_from_sub.extend([data.rs.x,data.rs.y,data.rs.z])
        self.data_from_sub.extend([data.re.x,data.re.y,data.re.z])
        self.data_from_sub.extend([data.rh.x,data.rh.y,data.rh.z])
        self.data_from_sub.extend([data.ls.x,data.ls.y,data.ls.z])
        self.data_from_sub.extend([data.le.x,data.le.y,data.le.z])
        self.data_from_sub.extend([data.lh.x,data.lh.y,data.lh.z])
        for l in range(len(self.data_from_sub)):
            if l % 3 == 0:
                self.data_from_sub[l]= float(self.data_from_sub[l])+float(self.data_from_sub[3])
            if l % 3 == 1:
                self.data_from_sub[l]= float(self.data_from_sub[l])+float(self.data_from_sub[4])
            if l % 3 == 2:
                self.data_from_sub[l]= float(self.data_from_sub[l])+float(self.data_from_sub[5])

    def training(self):
        self.neighbors = KNeighborsClassifier(n_neighbors=7)
        self.neighbors.fit( self.trainingSet, self.labels_train)

    def machine_learning(self):
        #print(self.data_from_sub)
        result = self.neighbors.predict([self.data_from_sub])[0]
        if self.disco == 1:
            if result == 'disco2':
                self.checking('disco')
            elif result == 'disco1':
                self.checking('wave')
            else:
                self.disco = 0
        elif result == 'disco1':
            self.disco =+1
        elif self.bow ==1:
            if result == 'bow2':
                self.checking('bow')
            else:
                self.bow = 0
        elif result == 'bow1':
            self.bow =+1
        else:
            self.checking(result)
        #print(self.neighbors.predict([self.data_from_sub]))

    def checking(self,gesture):
        #print(gesture)
        if self.check == 20:
            self.gestures[gesture] = self.gestures.get(gesture,0) +1
            self.check = 0
            self.publishing()
        else:
            self.check = self.check + 1
            self.gestures[gesture] = self.gestures.get(gesture,0) +1

    def publishing(self):
        print(self.gestures)
        for key,val in self.gestures.items():
            if val == max(self.gestures.values()):
                key1 = key
        print(key1)
        #[key for key,val in self.gestures.items() if val == max(self.gestures.values())]
        if key1 == 'disco2':
            print('we got disco2')
            self.pub.publish('disco')
        elif key1 == 'disco1':
            self.pub.publish('wave')
        elif key1 == 'bow1':
            print('why')
            self.pub.publish('bow')
        elif key1 == 'bow2':
            self.pub.publish('bow')
        else:
            print('this!')
            self.pub.publish(key1)
        self.gestures = dict()
        print(self.gestures)

    def run(self):
        r = rospy.Rate(10)
        self.training()
        while not rospy.is_shutdown():
            # self.close_points()
            self.machine_learning()
            r.sleep()

if __name__ == "__main__":
    #import doctest
    gest = Gestures([(1,2,3),(5,3,6)])
    gest.run()
    #doctest.testmod()
    #doctest.run_docstring_examples(Gestures.close_points, globals(),verbose = True)
