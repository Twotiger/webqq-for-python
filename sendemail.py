# -*- coding: utf-8 -*
import smtplib
from email.mime.text import MIMEText
from config import MAIL_HOST, MAIL_USER, MAIL_PASS, MAIL_POSTFIX, TO_LIST



def sendemail(sub, content , to_list=TO_LIST):

    me="状态提醒"+"<"+MAIL_USER+"@"+MAIL_POSTFIX+">"
    msg = MIMEText(content,_subtype='html',_charset='utf8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(MAIL_HOST)
        s.login(MAIL_USER, MAIL_PASS)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

if __name__ == "__main__":
    sendemail('hello text', '<h1>i love you</h1>')
