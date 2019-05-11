import cv2
import numpy as np

class VideoStream(object):
    def __init__(self,url,pos,resolution=(480,640)):
        self.cam=cv2.VideoCapture(url)
        self.pos=pos
        self.url=url
        self.resolution=resolution
        self.emptyframe=np.zeros((*self.resolution,3),dtype=np.uint8)

    def __repr__(self):
        print("VideoStream object at url: {}".format(self.url))
    
    def read(self,framebuffer):
        
        ret,frame=self.cam.read()
        
        if ret:
            this_frame=frame
        else:
            this_frame=self.emptyframe

        if self.pos==1:
            framebuffer[:self.resolution[0],:self.resolution[1]]=this_frame
        elif self.pos==2:
            framebuffer[:self.resolution[0],self.resolution[1]:]=this_frame
        elif self.pos==3:
            framebuffer[self.resolution[0]:,:self.resolution[1]]=this_frame
        elif self.pos==4:
            framebuffer[self.resolution[0]:,self.resolution[1]:]=this_frame

    def cleanup(self):
        self.cam.release()

class VideoStreamHandler(object):
    def __init__(self,urls,resolution=(480,640)):
        assert len(urls)==4,'At the moment this code is meant to handle 4 streams'
        self.url1=urls[0]
        self.url2=urls[1]
        self.url3=urls[2]
        self.url4=urls[3]
        self.resolution=resolution
        self.s1,self.s2,self.s3,self.s4=self.setup_streams()
        self.framebuffer=np.zeros((2*resolution[0],2*resolution[1],3),dtype=np.uint8)

    def setup_streams(self):
        stream1=VideoStream(self.url1,1,self.resolution)
        stream2=VideoStream(self.url2,2,self.resolution)
        stream3=VideoStream(self.url3,3,self.resolution)
        stream4=VideoStream(self.url4,4,self.resolution)

        return stream1,stream2,stream3,stream4

    def read_streams(self):
        self.s1.read(self.framebuffer)
        self.s2.read(self.framebuffer)
        self.s3.read(self.framebuffer)
        self.s4.read(self.framebuffer)
        return self.framebuffer

    def close(self):
    	self.s1.cleanup()
    	self.s2.cleanup()
    	self.s3.cleanup()
    	self.s4.cleanup()