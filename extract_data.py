# USE PYTHON 2.7!
# place rosbags you want to extract data from in the same directory as this script

# Adapted from: https://idorobotics.com/2021/03/08/extracting-ros-bag-files-to-python/

import rosbag, sys, csv
import time
import string
import os #for file management make directory
import shutil #for file management, copy file
import rosbag
import cv2
from cv_bridge import CvBridge
import numpy as np

# For now, manually specify which topic contains the image messages.
IMAGE_TOPIC = '/versavis/cam0/image_raw'

#verify correct input arguments: 1 or 2
if (len(sys.argv) > 2):
	print("invalid number of arguments:   " + str(len(sys.argv)))
	print("should be 2: 'extract_data.py' and 'bagName'")
	print("or just 1  : 'extract_data.py'")
	sys.exit(1)
elif (len(sys.argv) == 2):
	listOfBagFiles = [sys.argv[1]]
	numberOfFiles = "1"
	print("reading only 1 bagfile: " + str(listOfBagFiles[0]))
elif (len(sys.argv) == 1):
	listOfBagFiles = [f for f in os.listdir(".") if f[-4:] == ".bag"]	#get list of only bag files in current dir.
	numberOfFiles = str(len(listOfBagFiles))
	print("reading all " + numberOfFiles + " bagfiles in current directory: \n")
	for f in listOfBagFiles:
		print(f)
	print("\n press ctrl+c in the next 3 seconds to cancel \n")
	time.sleep(3)
else:
	print("bad argument(s): " + str(sys.argv))	#shouldnt really come up
	sys.exit(1)

count = 0
for bagFile in listOfBagFiles:
	count += 1
	print("reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile)
	#access bag
	bag = rosbag.Bag(bagFile)
	bagContents = bag.read_messages()
	bagName = bag.filename


	#create a new directory
	folder = bagName.rstrip('.bag')
	try:	#else already exists
		os.makedirs(folder)
	except:
		pass
	shutil.copyfile(bagName, folder + '/' + bagName)


	#get list of topics from the bag
	listOfTopics = []
	for topic, msg, t in bagContents:
		if topic not in listOfTopics:
			listOfTopics.append(topic)


	for topicName in listOfTopics:
		print("Extracting topic: " + topicName)

		# TODO: Automatically detect topic type and extract image topics differently. 
		if topicName == IMAGE_TOPIC:
			try:	#else already exists
				os.makedirs(folder + "/images")
			except:
				pass
			image_topic = bag.read_messages(topicName)
			i = 0
			for k, b in enumerate(image_topic):
				bridge = CvBridge()
				cv_image = bridge.imgmsg_to_cv2(b.message, b.message.encoding)
				cv_image.astype(np.uint8)
				cv2.imwrite(folder + '/images/' + "image_" + str(i) + "_" + str(b.timestamp) + '.png', cv_image)
			# 	print('saved: ' + "image_" +  str(i) + "_" + str(b.timestamp) + '.png')


		else:
			#Create a new CSV file for each topic
			filename = folder + '/' + topicName.replace('/', '_') + '.csv'
			with open(filename, 'w+') as csvfile:
				filewriter = csv.writer(csvfile, delimiter = ',')
				firstIteration = True	#allows header row
				for subtopic, msg, t in bag.read_messages(topicName):	# for each instant in time that has data for topicName
					#parse data from this instant, which is of the form of multiple lines of "Name: value\n"
					#	- put it in the form of a list of 2-element lists
					msgString = str(msg)
					msgList = msgString.split('\n')
					instantaneousListOfData = []
					for nameValuePair in msgList:
						splitPair = nameValuePair.split(':')
						for i in range(len(splitPair)):	#should be 0 to 1
							splitPair[i] = splitPair[i].strip()
						instantaneousListOfData.append(splitPair)
					#write the first row from the first element of each pair
					if firstIteration:	# header
						headers = ["rosbagTimestamp"]	#first column header
						for pair in instantaneousListOfData:
							headers.append(pair[0])
						filewriter.writerow(headers)
						firstIteration = False
					# write the value from each pair to the file
					values = [str(t)]	#first column will have rosbag timestamp
					for pair in instantaneousListOfData:
						if len(pair) > 1:
							values.append(pair[1])
					filewriter.writerow(values)
	bag.close()
print("Done reading all " + numberOfFiles + " bag files.")