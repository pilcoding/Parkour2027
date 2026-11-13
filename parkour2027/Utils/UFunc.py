import numpy as np

def rad_to_degree(angle):
    return angle*360/(2*np.pi)

def degree_to_rad(angle):
    return angle*2*np.pi/360