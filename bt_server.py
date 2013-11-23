# Matthew Coppola
#
# Bluetooth server and touch accuracy game
# For browser box protype
from bluetooth import *
from random import randint
import sys, pygame, json, math

class MyPointDecoder(json.JSONDecoder):

	def __init__(self):
		json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

	def dict_to_object(self, d):
		if 'x' in d:
			self.x = int(math.floor(float(d.pop('x'))))
			self.y = int(math.floor(float(d.pop('y'))))
		return self

class MyWindowDecoder(json.JSONDecoder):

	def __init__(self):
		json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

	def dict_to_object(self, d):
		if 'width' in d:
			self.width = int(math.floor(float(d.pop('width'))))
			self.height = int(math.floor(float(d.pop('height'))))
		return self

class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y


# init bluetooth serverfloat(
server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",22))
server_sock.listen(1)
port = server_sock.getsockname()[1]
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
                   protocols = [ OBEX_UUID ] 
                    )
                
# Wait for client connectionfloat(
print "Waiting for connection on RFCOMM channel %d" % port
client_sock, client_info = server_sock.accept()
print "Accepted connection from ", client_info

# First message should contain window dimmentons
# try to get it to init game window at same aspect ration
windowData = client_sock.recv(1024)
print windowData
pygame.init()
try:
	clientWindow = MyWindowDecoder().decode(windowData)
	window = pygame.display.set_mode((clientWindow.width, clientWindow.height))
except Exception, e:
	print 'did not get window size from client'
	print e
	window = pygame.display.set_mode((640, 480))


# game variables
points = [] # we will store the test point, the response, and the new test point
pointCount = 0
acc_sum = 0
acc_master = 0
font = pygame.font.Font(None,30)
acc = font.render("accuracy = " + str(acc_master), 1, (255,255,0))
window.blit(acc, (100, 200))
# game loop
try:
	while True:
		# clear window
		window.fill((0,0,0))
		# make target, wait for response
		target = Point(randint(0,clientWindow.width), randint(0,clientWindow.height))
		points.append(target)
		count = 0
		for p in points:
			if (count % 2 == 0):
				pygame.draw.circle(window, (255, 0, 0), (p.x, p.y), 5)
			else:
				pygame.draw.circle(window, (255, 255, 255), (p.x, p.y), 5)
			count += 1
		pygame.display.flip()
		data = client_sock.recv(1024)
		pointCount += 1
		if len(data) == 0: break
		print "received [%s]" % data

		# got response print response, old target, and new target
		try:
			point = MyPointDecoder().decode(data)
			points.append(point)
			count = 0
			for p in points:
				if (count % 2 == 0):
					pygame.draw.circle(window, (255, 0, 0), (p.x, p.y), 5)
				else:
					pygame.draw.circle(window, (255, 255, 255), (p.x, p.y), 5)
				count += 1
			pygame.display.flip()
			points = []
			points.append(target)
			points.append(point)

			# calculate accuracy
			accuracy = ((100 - (math.fabs(target.x - point.x)/clientWindow.width)*100) - (math.fabs(target.y - point.y)/clientWindow.height)*100)
			acc_sum = acc_sum + accuracy 
			acc_master = acc_sum / pointCount
			acc = font.render("accuracy = " + str(acc_master), 1, (255,0,255))
			window.blit(acc, (0, 5))
			print acc_master
		except Exception, e:
			print str(e)

except IOError:
    pass

print "disconnected"

client_sock.close()
server_sock.close()
print "all done"