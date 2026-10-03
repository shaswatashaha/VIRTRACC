#!/usr/bin/env python

import numpy as np
import cv2
import timeit


# local modules
from video import create_capture
from common import clock, draw_str

help_message = '''
USAGE: facedetect.py [--cascade <cascade_fn>] [--ne sted-cascade <cascade_fn>] [<video_source>]
'''

def detect(img, cascade):
    # rects is a list (python array) that saves coordiantes of faces
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
# main function
if __name__ == '__main__':
    import sys, getopt
    print help_message

    args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
    try:
        video_src = video_src[0]
    except:
        video_src = 0
    args = dict(args)
    cascade_fn = args.get('--cascade', "../../data/haarcascades/haarcascade_frontalface_alt.xml")
    nested_fn  = args.get('--nested-cascade', "../../data/haarcascades/haarcascade_eye.xml")

    cascade = cv2.CascadeClassifier(cascade_fn)
    nested = cv2.CascadeClassifier(nested_fn)

    cam = create_capture(video_src, fallback='synth:bg=../data/lena.jpg:noise=0.05')

    
    while True:
        ret, img = cam.read()
        cv2.line(img,(320,0),(320,480),(0,255,0),3)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        t = clock()
        rects = detect(gray, cascade)
        #########################################
        # this is where you work with rects
        # BGR color code. is it true?
        height, width, channels = img.shape
        # height = 480 width = 640
        width = width / 2
        left_counter = 0
        right_counter = 0
        left_threshold = 2
        right_threshold = 2
        if not nested.empty():
            for x1, y1, x2, y2 in rects:   
                if x1 < width:
                    left_counter = left_counter + 1
                        
                if x1 > width:
                    right_counter = right_counter + 1
                
                total = left_counter + right_counter
                draw_str(img, (10, 20), 'Total traffic %d'%total)
                draw_str(img, (10, 50), 'Left total traffic %d'%left_counter)
                draw_str(img, (400, 50), 'Right total traffic %d'%right_counter)
                
                
                if (left_counter < left_threshold) and (right_counter < right_threshold):
                    print ''
                elif (left_counter > left_threshold) and (right_counter < right_threshold):
                    print "right road is free"
                    img1 = cv2.imread('map3.jpg')
                    cv2.imshow('map',img1)
                elif (left_counter < left_threshold) and (right_counter > right_threshold):
                    print "left road is free"
                    img2 = cv2.imread('map2.jpg')
                    cv2.imshow('map',img2)
                elif (left_counter > left_threshold) and (right_counter > right_threshold):
                    print "both road is blocked"
                    img3 = cv2.imread('red.jpg')
                    cv2.imshow('map',img3)
                
        ######################################
        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))
        if not nested.empty():
            for x1, y1, x2, y2 in rects:
                roi = gray[y1:y2, x1:x2]
                vis_roi = vis[y1:y2, x1:x2]
                subrects = detect(roi.copy(), nested)
                draw_rects(vis_roi, subrects, (255, 0, 0))
        dt = clock() - t

        #draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
        # this is where you show the image with rectangles
        cv2.imshow('facedetect', vis)

        if 0xFF & cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()
