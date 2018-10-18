import os, time
import threading, Queue
import urllib
import send_email as sem
from config import h264_folder, mp4_folder, motion_threshold,log_dir,log_file

os.environ['TZ']= 'Asia/Kolkata'
time.tzset()

class FileManagerThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, h264_q):
        super(FileManagerThread, self).__init__()
        self.h264_q = h264_q
        self.stoprequest = threading.Event()
        self.files_sent=[]
        self.files_not_sent=[]

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                h264_filename = self.dir_q.get(True, 0.05)
                mp4_name=h264_filename[:h264_filename.rfind('.')]+'.mp4'
                now=time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime())
                os.system("rm {}".format(mp4_folder+mp4_name))
                os.system("MP4Box -add {} {}".format(h264_folder+h264_filename,mp4_folder+mp4_name))
                #os.system("python -u send_email.py {}".format(mp4_name))
				os.remove(h264_folder+h264_filename)
                try:
                    sem.send_mail(files=[mp4_folder+mp4_name])
                    self.files_sent.append((mp4_name,now))
                    os.remove(mp4_folder+mp4_name)
                except:
                    self.files_not_sent.append((mp4_name,now))
#                else:
#                	self.files_not_sent.append(mp4_name)
            except Queue.Empty:
            	#if nothing to do, we try to push files not sent earlier
            	if self._connected() and len(self.files_not_sent)>0:
            		for f,now in self.files_not_sent:
	            		try:
	            			text="Motion detected in your room at {}. Please see attached video.\n".format(now)
    	        			sem.send_mail(files=[mp4_folder+f],text=text)
    	        			self.files_not_sent.remove((f,now))
                    		os.remove(mp4_folder+f)    	        			
    	        		except:
    	        			continue
    	        if len(self.files_not_sent)>0:
	    	        with open(log_dir+log_file,'a')  as f:
	    	        	f.write(time.strftime("%a, %d %b %Y %H:%M:%S\n",time.localtime()))
	    	        	f.write(str(self.files_not_sent))
	    	        	f.write('\n')
	    	        	f.write('\n')

    def join(self, timeout=None):
        self.stoprequest.set()
        super(FileManagerThread, self).join(timeout)

    def _connected(self):
        try:
            urllib.urlopen('http://www.google.com')
            return True
        except Exception, err:
            print(err)
            return False

class FileCleanerThread(threading.Thread):
    def __init__(self):
        super(FileCleanerThread, self).__init__()
        self.stoprequest = threading.Event()
        self.files_sent=[]
        self.files_not_sent=self.get_file_names()

    def run(self):
        while len(self.files_not_sent)>0:
            try:
            	if self._connected():
            		for f,now in self.files_not_sent:
	            		try:
	            			text="Motion detected in your room at {}. Please see attached video.\n".format(now)
    	        			sem.send_mail(files=[mp4_folder+f],text=text)
    	        			self.files_not_sent.remove((f,now))
    	        		except:
    	        			continue
    	        if len(self.files_not_sent)>0
    	        with open(log_dir+log_file,'a')  as f:
    	        	f.write(time.strftime("%a, %d %b %Y %H:%M:%S\n",time.localtime()))
    	        	f.write(str(self.files_not_sent))
    	        	f.write('\n')

   	def get_file_names(self):
   		with open(log_dir+log_file,'r') as f:
   			alltext=f.read().split('\n')
   		for line in alltext.reverse()
   			if len(line)>2 and '[' in line: #making sure there is some content
   				files=eval(line)
   				break
   		else:
   			files=[]
   		return files

    def join(self, timeout=None):
        self.stoprequest.set()
        super(FileCleanerThread, self).join(timeout)

    def _connected(self):
        try:
            urllib.urlopen('http://www.google.com')
            return True
        except Exception, err:
            print(err)
            return False

class counter(object):
	def __init__(self,countfile):
		self.log=countfile
		self.count=self.get_start_point()
	
	def set_count(self,newcount):
		self.count=newcount
		with open(self.log,'w'):
			f.write(str(self.count))
	
	def update_count(self):
		self.count+=1
		with open(self.log,'w'):
			f.write(str(self.count))

	def get_start_point(self):
		with open(self.log,'r') as f:
			count=int(f.read)
		return count