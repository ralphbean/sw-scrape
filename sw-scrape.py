#!/usr/bin/env python
""" Scrape SW.org and send it to Brian """

import smtplib
from email.mime.text import MIMEText
import urllib2
import BeautifulSoup
import datetime
import feedparser
import html2rst
import sys


def send_mail(msg=None, subject=None, recip=None, sender=None):
    """ Workhorse function.  Sends mail. """
    if not (msg and subject and recip and sender):
        raise ValueError, "send_mail given an empty parameter."

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recip

    s = smtplib.SMTP()
    s.connect()
    s.sendmail(sender, [recip], msg.as_string())
    s.quit()


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        raise ValueError, "usage: sw-scrape.py <sender> <recipient>"

    sender, recipient = sys.argv[1:]

    d = feedparser.parse('http://socialistworker.org/recent/feed')
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)

    for entry in d.entries:
        published = datetime.datetime.strptime(
            entry.updated[:-6], "%a, %d %b %Y %H:%M:%S")
        if published < today and published > yesterday:
            link = entry.link.replace('socialistworker.org',
                                      'socialistworker.org/print')
            page = urllib2.urlopen(link)
            html = unicode(BeautifulSoup.BeautifulSoup(page).html)
            html = html.encode('ascii', 'replace')

            # reST stands for reStructuredText.  Its an awesome markup.
            reST = html2rst.optwrap(html2rst.html2text_file(html, None))
            subject = "[sw]" + entry.title
            msg = MIMEText(reST)
            send_mail(msg=msg, subject=subject, recip=recipient, sender=sender)

    
