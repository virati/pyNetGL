#Created by Vineet Tiruvadi, 2010 - 2015
#This is a script that has, embedded, the modules that need to be extracted out into a library

#!/usr/bin/env python

import networkx as nx
import matplotlib.pyplot as plt
import numpy as nm
import time
import sys
import random
import math
import pdb
#import astroglia_net

display_mode='opengls'

#opengl parameters
view_angle_y = 0
view_angle_x = 0
zoom = -4.0
trans_x = 0.0
trans_y = -0.4

fig = plt.figure()
time_step = 0.01
n_nodes = 20
a_nodes = 25
N = []
A = []
state = nm.zeros( (n_nodes,n_nodes) )
t_loc = 0

#def add_z_pos(G):
#	for i in G.nodes():
#		G[i].pos[i].append(random.uniform(0,1))
#	return G
	
def gen_ntwrk(num,gamma,typ='neurons'):
	p = dict((i,(random.gauss(0,2),random.gauss(0,2),random.gauss(0,2))) for i in range(num))
	G = nx.random_geometric_graph(num,gamma)
	G.n_weights = []
	G.typ = typ
	G.pos = p
	#G = add_z_pos(G)
	#pos = G.pos
	
	if typ=='neurons':	
		for i in G.nodes():
			G.n_weights.append(300/(i+1))	
	elif typ=='astrocytes':
		for i in G.nodes():
			G.n_weights.append(100)	
	return G

def update_plot_graph(G, add='no'):
	if add == 'no':
		plt.clf()
	plt.axis('off')
	global timestep
	pos = G.pos#nx.get_node_attributes(G,'pos')
	
	w = [v for (u,v) in pos.iteritems()]
	pos2 = [(u,v) for (u,v,k) in w]
	
	n_weights = G.n_weights
	e_weights = [k['weight'] for (u,v,k) in G.edges(data=True)]
		
	if G.typ == 'astrocytes':
		G_color = 'b'
	else:
		G_color = 'r'

	nx.draw_networkx_nodes(G,pos2,node_size=n_weights, node_color=G_color)
	if G.typ == 'astrocytes':
		nx.draw_networkx_edges(G,pos2,alpha=0.5,edge_color='g')
	else:
		nx.draw_networkx_edges(G,pos2,width=e_weights)

def setup_plott():
	fig.canvas.mpl_connect('key_press_event', onpress)
	plt.show()

#gamma = 1 says that every neuron has at least 1 astrocyte associated with it
def merg_NA_net(Nu,As,gamma=1):
	
	As_size = len(As.nodes())
	for i in Nu.edges(data=True):
		for j in range(i[2]['weight']):
			test=1
	
	return Nu

#Adds edge weights that correspond to number of synapses for that edge
def add_syn_degen(Nu, max_conn=10):
	for i in Nu.edges():
		Nu.add_edge(i[0],i[1],weight=int(math.floor(random.uniform(1,max_conn))));
	return Nu
	
def main():
	global N
	global A
	
	timestep = 0
	N = gen_ntwrk(n_nodes, 0.25, 'neurons')
	A = gen_ntwrk(a_nodes, 0.2, 'astrocytes')
	
	#merg_NA_net(N,A);
	
	#print nx.adj_matrix(N)
	#print N.edges(data='True')
	#print
	
	N = add_syn_degen(N)
	A = add_syn_degen(A,1)
	#print N.edges(data='True')
	
	NuAs = merg_NA_net(N,A)
	
	update_plot_graph(N)
	update_plot_graph(A,'yes')
	if display_mode == 'opengl':
		glGraph()
	else:
		setup_plott()
		glGraph()


#### DISPLAY 'BACKEND' STUFF - - - - 
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import time

ESCAPE = '\033'

window = 0
rtri = 0.0
rquad = 0.0

def onpress(event):
	global timestep
	global angle
	global trans_x
	global G
	
	if event.key=='a':
		update_plot_graph(N)
		update_plot_graph(A,'yes')
		
		print timestep
		fig.canvas.draw()
		timestep += 1
	elif event.key=='q':
		update_plot_graph(N)
	elif event.key=='w':
		update_plot_graph(A)
	elif event.key=='d':
		plt.clf()
	elif event.key=='x':
		print nx.adj_matrix(N)
	elif event.key=='c':
		print nx.adj_matrix(A)

def GL_networkDraw(N):
	if N.typ=='astrocytes':
		node_color = [0.0, 0.0, 1.0]
		edge_color = [0.0, 1.0, 0.0, 0.5]
		node_radius = 0.04
		node_pulse = 0.1
	elif N.typ=='neurons':
		node_color = [1.0, 0.0, 0.0]
		edge_color = [1.0, 1.0, 1.0, 0.4]
		node_radius = 0.02
		node_pulse = 0

	node_pos = N.pos #nx.get_node_attributes(N,'pos')
	for i in N.nodes():
		glLoadIdentity()
		glTranslatef(trans_x,trans_y,zoom);	
		glRotatef(view_angle_y,0,1,0)
		glRotatef(view_angle_x,1,0,0)
		glTranslatef(node_pos[i][0], node_pos[i][1], node_pos[i][2])
				
		glColor3f(node_color[0],node_color[1],node_color[2])
		
		glutSolidSphere(node_radius + node_pulse*(math.sin(t_loc)),20,20)

	for i in N.edges():
		glLoadIdentity()
		glTranslatef(trans_x,trans_y,zoom);
		glRotatef(view_angle_y,0,1,0)
		glRotatef(view_angle_x,1,0,0)
		glBegin(GL_LINES)
		
		glColor4f(edge_color[0],edge_color[1],edge_color[2], edge_color[3])
		
		glVertex3f(float(node_pos[i[0]][0]),float(node_pos[i[0]][1]),float(node_pos[i[0]][2]))
		glVertex3f(float(node_pos[i[1]][0]),float(node_pos[i[1]][1]),float(node_pos[i[1]][2]))
		
		glEnd()
		
def DrawGLScene():
	global view_angle_y
	global view_angle_x
	global zoom
	global t_loc
	global time_step
	
	time.sleep(0.001)
	
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	# Clear The Screen And The Depth Buffer
	#glLoadIdentity();					# Reset The View
	glTranslatef(0.0,0.0,-9.0);				# Move Left And Into The Screen

	GL_networkDraw(N)
	GL_networkDraw(A)	
	
	glutSwapBuffers()
	time.sleep(0.01)
	t_loc += time_step
	#view_angle+=0.1

def InitGL(Width, Height):				# We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
    glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
    glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
	
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()					# Reset The Projection Matrix
										# Calculate The Aspect Ratio Of The Window
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    
    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
	    Height = 1

    glViewport(0, 0, Width, Height)		# Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# The main drawing function. 

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
	global view_angle_y
	global view_angle_x
	global zoom
	global trans_x
	global trans_y
	
	#print args[0]
	if args[0] == ESCAPE:
		sys.exit()
	elif args[0] == 'q':
		view_angle_y -= 5.0
	elif args[0] =='w':
		view_angle_y += 5.0
	elif args[0] == 'a':
		view_angle_x -= 5.0
	elif args[0] == 's':
		view_angle_x += 5.0
	elif args[0] == 'z':
		zoom += 1.0
	elif args[0] == 'x':
		zoom -= 1.0
	elif args[0] == 'r':
		setup_plott(N)
	elif args[0] == '[':
		trans_x += 0.2
	elif args[0] == ']':
		trans_x -= 0.2
	elif args[0] == 'o':
		trans_y += 0.2
	elif args[0] == 'p':
		trans_y -= 0.2
	elif args[0] == '1':
		setup_plott()
		

def glGraph():
	global window
	glutInit(sys.argv)

	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	
	glutInitWindowSize(640, 480)
	
	# the window starts at the upper left corner of the screen 
	glutInitWindowPosition(0, 0)
	
	# Okay, like the C version we retain the window id to use when closing, but for those of you new
	# to Python (like myself), remember this assignment would make the variable local and not global
	# if it weren't for the global declaration at the start of main.
	window = glutCreateWindow("Interactive and Spatially Aware Network View")

   	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
	# set the function pointer and invoke a function to actually register the callback, otherwise it
	# would be very much like the C version of the code.	
	glutDisplayFunc(DrawGLScene)
	
	# Uncomment this line to get full screen.
	# glutFullScreen()

	# When we are doing nothing, redraw the scene.
	glutIdleFunc(DrawGLScene)
	
	# Register the function called when our window is resized.
	glutReshapeFunc(ReSizeGLScene)
	
	# Register the function called when the keyboard is pressed.  
	glutKeyboardFunc(keyPressed)

	# Initialize our window. 
	InitGL(640, 480)

	# Start Event Processing Engine
	glutMainLoop()

if __name__ == '__main__': 
	main()
