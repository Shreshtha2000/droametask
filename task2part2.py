import pyfirmata
import sys
import time
import csv
import math

#To store imu data from csv
csvcont = []

#To store distance data from csv
dist=[]

#Reading imu data
with open("imu.csv",mode = 'r') as file:
	fileread = csv.reader(file)
	# print(type(fileread))
	for line in fileread:
		csvcont.append(line)

#Reading distance data
with open("dist.csv",mode = 'r') as file:
	fileread = csv.reader(file)
	# print(type(fileread))
	for line in fileread:
		dist.append(line)

#iterator		
i=1
if __name__ == '__main__':
	board = pyfirmata.Arduino('/dev/ttyVSP2')
	print("Connected")

	#Setting the weihgtage of imu data to be more
	alpha = 0.98
	#time between sampling keeping it nearly equal to reading frequency from microcontroller
	dt = 0.01


	#Motor (1) Connection for Motor placed in front on left side positive terminal
	motorFrontL_post = board.digital[2]
	motorFrontL_post.mode=pyfirmata.OUTPUT

	#Motor (1) Connection for Motor placed in front on left side negative terminal
	motorFrontL_negt = board.digital[4]
	motorFrontL_negt.mode=pyfirmata.OUTPUT

	#Motor (2) Connection for Motor placed in rear on left side positive terminal
	motorRearL_post = board.digital[7]
	motorRearL_post.mode=pyfirmata.OUTPUT

	#Motor (2) Connection for Motor placed in rear on left side negative terminal
	motorRearL_negt = board.digital[8]
	motorRearL_negt.mode=pyfirmata.OUTPUT

	# enable pin connection of motor (1) with pwm pin 9 of arduino to control rpm
	enableMFL = board.digital[9]
	enableMFL.mode = pyfirmata.PWM

	# enable pin connection of motor (2) with pwm pin 10 of arduino to control rpm
	enableMRL = board.digital[10]
	enableMRL.mode = pyfirmata.PWM

	#Motor (3) Connection for Motor placed in front on right side positive terminal
	motorFrontR_post = board.digital[13]
	motorFrontR_post.mode=pyfirmata.OUTPUT

	#Motor (3) Connection for Motor placed in front on right side negative terminal
	motorFrontR_negt = board.digital[12]
	motorFrontR_negt.mode=pyfirmata.OUTPUT

	#Motor (4) Connection for Motor placed in rear on right side positive terminal
	motorRearR_post = board.digital[5]
	motorRearR_post.mode=pyfirmata.OUTPUT

	#Motor (4) Connection for Motor placed in rear on right side negative terminal
	motorRearR_negt = board.digital[3]
	motorRearR_negt.mode=pyfirmata.OUTPUT

	# enable pin connection of motor (3) with pwm pin 6 of arduino to control rpm
	enableMFR = board.digital[6]
	enableMFR.mode = pyfirmata.PWM

	# enable pin connection of motor (4) with pwm pin 11 of arduino to control rpm
	enableMRR = board.digital[11]
	enableMRR.mode = pyfirmata.PWM



	#Setting up motor connection polarity for diagonally same direction of rotation of blades
	#Motor1 Cloclwise
	motorFrontL_post.write(0)
	motorFrontL_negt.write(1)

	#Motor2 anticlockwise
	motorRearL_post.write(1)
	motorRearL_negt.write(0)

	#Motor3 anticlockwise
	motorFrontR_post.write(1)
	motorFrontR_negt.write(0)

	#Motor4 Clockwise
	motorRearR_post.write(0)
	motorRearR_negt.write(1)

	#Setting up thrust,pitch,yaw and roll pins for receiving values from joystick

	#Thrust connection
	js_thrust_pin = board.analog[2]

	#Pitch Connection
	js_pitch_pin = board.analog[5]

	#Yaw Connection
	js_yaw_pin = board.analog[1]

	#Roll Connection
	js_roll_pin = board.analog[4]
	js_thrust_pin.enable_reporting()
	js_pitch_pin.enable_reporting()
	js_roll_pin.enable_reporting()
	js_yaw_pin.enable_reporting()

	
	#initializing for further calculation
	pitch = 0
	roll=0
	yaw=0
	prev_yaw=0
	prev_roll=0
	prev_thrust=0.1
	prev_pitch=0

	
	it = pyfirmata.util.Iterator(board)
	it.start()
	time.sleep(0.5)
	while True:
		print("read val")
		#to store value received upon reading from pitch pin
		js_pitch_val = js_pitch_pin.read()*1000
		#to store value received upon reading from roll pin
		js_roll_val = js_roll_pin.read()*1000
		#to store value received upon reading from yaw pin
		js_yaw_val = js_yaw_pin.read()*1000

		#to store value received upon reading from thrust pin
		js_thrust_val = 1-js_thrust_pin.read()

		# print(js_thrust_val)
		# print(js_pitch_val)
		# print(js_roll_val)
		# print(js_yaw_val)

		#Converting value received to use in accordance with value of thrust
		if js_pitch_val is not None:
			pitch_val = round((500 -js_pitch_val)/500*js_thrust_val,2)
		if js_roll_val is not None:
			roll_val = round((500-js_roll_val)/500*js_thrust_val,2)
		if js_yaw_val is not None:
			yaw_val = round((500-js_yaw_val)/500*js_thrust_val,2)


		# print("individual val")
		# print(js_thrust_val)
		# print(pitch_val)
		# print(roll_val)
		# print(yaw_val)

		#reading distance from object 
		distance = float(dist[i][0])

		#reading imu data
		accX = float(csvcont[i][1])
		accY = float(csvcont[i][2])
		accZ = float(csvcont[i][3])
		gyroX = float(csvcont[i][4])
		gyroY = float(csvcont[i][5])
		gyroZ = float(csvcont[i][6])

		#calculaing pitch, yaw and roll
		pitch= alpha*(pitch+gyroX*dt)+(1-alpha)*(math.atan2(accY,accZ)*180/math.pi)
		roll= alpha*(roll+gyroY*dt)+(1-alpha)*(math.atan2(-accX,accZ)*180/math.pi)
		yaw= alpha*(yaw+gyroZ*dt)+(1-alpha)*(gyroZ*180/math.pi)

		# pitch_pwm = map(pitch,-1.57,1.57,0,prev_thrust)
		# roll_pwm = map(roll,-1.57,1.57,0,prev_thrust)
		# yaw_pwm = map(yaw,-3.14,3.14,0,prev_thrust)


		print("IMU pitch roll yaw")

		print(pitch)
		print(roll)
		print(yaw)
		#max angle for pitch roll = 90 and for yaw = 180 
		pitch_pwm = (pitch - (-1.57)) * (prev_thrust - 0) / (1.57 - (-1.57)) 
		roll_pwm = (roll - (-1.57)) * (prev_thrust - 0) / (1.57 - (-1.57)) 
		yaw_pwm = (yaw - (-3.14)) * (prev_thrust - 0) / (3.14 - (-3.14)) 

		# pitch_error = prev_pitch-pitch_pwm
		# roll_error = prev_roll-roll_pwm
		# yaw_error = prev_yaw-yaw_pwm
		
		#calculating no desired pitch, yaw and role
		desired_pitch = pitch_val-pitch_pwm
		desired_roll = roll_val-roll_pwm
		desired_yaw = yaw_val-yaw_pwm

		#checking if the object is in front of uav then set the desired pitch to 0
		if(distance<=5):
			desired_pitch=0

		print("Desired pitch yaw roll")
		print(desired_yaw)
		print(desired_roll)
		print(desired_pitch)
		
		#Calculating pwm values to be sent to enable pins of each motor based on which attitute will affect which motor
		enable_val_MFL = round(js_thrust_val+(-1*desired_pitch-desired_roll-desired_yaw)*0.9,2)
		enable_val_MRL = round(js_thrust_val+(desired_pitch-desired_roll+desired_yaw)*0.9,2)
		enable_val_MFR = round(js_thrust_val+(-1*desired_pitch+desired_roll+desired_yaw)*0.9,2)
		enable_val_MRR = round(js_thrust_val+(desired_pitch+desired_roll-desired_yaw)*0.9,2)


		# print(enable_val_MFL)
		# print(enable_val_MRL)
		# print(enable_val_MFR)
		# print(enable_val_MRR)

		#Just checking for limiting conditions
		if(enable_val_MFL<0):
			enable_val_MFL = 0.1
		elif enable_val_MFL>1:
			enable_val_MFL=1
		if(enable_val_MRL<0):
			enable_val_MRL = 0.1
		elif enable_val_MRL>1:
			enable_val_MRL = 1
		if(enable_val_MFR<0):
			enable_val_MFR = 0.1
		elif enable_val_MFR>1:
			enable_val_MFR = 1
		if(enable_val_MRR<0):
			enable_val_MRR = 0.1
		elif enable_val_MRR>1:
			enable_val_MRR=1

		#Setting the pwm value for each motor
		enableMFL.write(enable_val_MFL)
		enableMRL.write(enable_val_MRL)
		enableMFR.write(enable_val_MFR)
		enableMRR.write(enable_val_MRR)

		prev_thrust = js_thrust_val
		prev_yaw = desired_yaw
		prev_roll=desired_roll
		prev_pitch=desired_pitch

		# print(pval)
		i=i+1
		if(i>=len(csvcont)):
			i=1
		print("distance from object:")
		print(distance)
		if(distance<5):
			print("Object Ahead")
			time.sleep(0.5)
		time.sleep(0.01)



		
