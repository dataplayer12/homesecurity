import smtplib, time, os
os.environ['TZ']= 'Asia/Kolkata'
time.tzset()

with open('confidential.txt','r') as f:
	info=eval(f.read())

MY_EMAIL=info['myemail']
MY_PASSWD=info['mypass']
RECEPIENT=info['recepients']

SUBJECT="CCTV recording for last few seconds"

import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

def send_mail(send_from=MY_EMAIL, send_to=RECEPIENT, subject=SUBJECT, files=['video0.mp4'], text=''):
    text+="Motion detected in your room at {}. Please see attached video.\n".format(time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime()))

    server="smtp.gmail.com"
    port=587
    username=MY_EMAIL
    password=MY_PASSWD
    isTls=True

    msg = MIMEMultipart()
    msg['From'] = send_from[0]
    msg['To'] = 'recepients'
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if isTls:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        #print(username)
        smtp.login(username,password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()

if __name__=="__main__":
	send_mail()
