# -*- coding: utf-8 -*-
from flask import render_template
from email.MIMEText import MIMEText
import smtplib
import server.models


def email_sender(recv_email, otp):
    data = server.models.Mail.query.all()[0]
    contents = render_template('email.html', otp=otp)
    msg = MIMEText(contents, 'html', _charset='UTF-8')
    msg['SUBJECT'] = u'[server] 계정 등록 OTP 메일입니다.'
    msg['FROM'] = data.mail_id
    msg['To'] = recv_email
    s = smtplib.SMTP_SSL(data.mail_host)
    s.login(data.mail_id, data.mail_pw)
    s.sendmail(data.mail_id, recv_email, msg.as_string())
    s.quit()
    return True