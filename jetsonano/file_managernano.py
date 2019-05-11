import os, time
import threading, queue
import urllib.request, urllib.parse, urllib.error
import send_email as sem
from config import h264_folder, mp4_folder, motion_threshold,log_dir,log_file,logwrite_th, connect_th
import human_detect as hd
import shutil
from copy import deepcopy
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
        self.last_files_not_sent=[]
        self.time_last_written=time.time()
        self.time_last_checked=time.time()
        self.last_status=False

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                h264_filename = self.h264_q.get(True, 0.05)
                fname=mp4_folder+h264_filename
                now=time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime())
                #os.system("rm {}".format(fname))
                os.system("mv {} {}".format(h264_folder+h264_filename,fname))
                try:
                    should_send,message=hd.determine_if_person_in(fname,is_nano=True)
                    #if not should_send:
                    if should_send:
                        jpeg_name=fname[:fname.rfind('.')+1]+'jpg'
                        if os.path.exists(jpeg_name):
                            send_list=[fname,jpeg_name]
                        else:
                            send_list=[fname]
                        sem.send_mail(files=send_list,text=message)
                        self.files_sent.append((fname,now))
                        os.remove(fname)
                except Exception as e:
                    print(str(e))
                    #if should_send:
                    self.files_not_sent.append((fname,now))
            except queue.Empty:
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
                if time.time()-self.time_last_written>logwrite_th:
                    self.time_last_written=time.time()
                    if len(self.files_not_sent)>0:
                        if self.files_not_sent != self.last_files_not_sent:
                            self.last_files_not_sent=deepcopy(self.files_not_sent)
                            with open(log_dir+log_file,'a')  as f:
                                f.write(time.strftime("%a, %d %b %Y %H:%M:%S\n",time.localtime()))
                                f.write(str(self.files_not_sent))
                                f.write('\n')
                                f.write('\n')

    def join(self, timeout=None):
        self.stoprequest.set()
        super(FileManagerThread, self).join(timeout)

    def _connected(self):
        #return True
        if (time.time()-self.time_last_checked)>connect_th:
            self.time_last_checked=time.time()
            try:
                urllib.request.urlopen('https://www.google.com')
                self.last_status=True
            except Exception as err:
                print(err)
                self.last_status=False
            return self.last_status
        else:
            return self.last_status

class FileCleanerThread(threading.Thread):
    def __init__(self):
        super(FileCleanerThread, self).__init__()
        self.stoprequest = threading.Event()
        self.files_sent=[]
        self.files_not_sent=self.get_file_names()
        self.time_last_checked=time.time()
        self.last_status=False
        
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
                if len(self.files_not_sent)>0:
                    with open(log_dir+log_file,'a')  as f:
                        f.write(time.strftime("%a, %d %b %Y %H:%M:%S\n",time.localtime()))
                        f.write(str(self.files_not_sent))
                        f.write('\n')
            except:
                continue

    def get_file_names(self):
        with open(log_dir+log_file,'r') as f:
            alltext=f.read().split('\n')
        for line in reversed(alltext):
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
        #return True
        if (time.time()-self.time_last_checked)>connect_th:
            self.time_last_checked=time.time()
            try:
                urllib.request.urlopen('https://www.google.com')
                self.last_status=True
            except Exception as err:
                print(err)
                self.last_status=False
            return self.last_status
        else:
            return self.last_status

class counter(object):
    def __init__(self,countfile):
        self.log=countfile
        self.count=self.get_current_count()
    
    def set_count(self,newcount):
        self.count=newcount
        with open(self.log,'w'):
            f.write(str(self.count))
    
    def update_count(self):
        self.count+=1
        with open(self.log,'w') as f:
            f.write(str(self.count))

    def get_current_count(self):
        try:
            with open(self.log,'r') as f:
                count=int(f.read())
        except Exception as e:
            print((str(e)))
            count=0
        return count