#!/usr/bin/env python
Version = '20120405'

# Original author: Walied Othman <rainwolf@submanifold.be>
# IMAP and SMTP support: Ray Cathcart <gknujon@vantcm.com>
# This wouldn't be without python
# http://www.python.org

#ToDo
# - allow user to configure SMTP port and/or server
# - forward spam without downloading it
# - catch exceptions
# - ...

import imaplib, os, zipfile, sys, smtplib, re, socket, string, tempfile, getpass
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders


# RLC - I found this sendMail subroutine on dzone.com. Modified it to work with
#       google's authentication.
#to python files mail smtp by manatlan on Wed Sep 21 16:30:49 -0400 2005
# to        => [list] of addresses for "To:" field
# subject   => string for "Subject:" field
# text      => string for body of email
# files     => [list] of files to attach using MIME
# server    => string containing SMTP server address (e.g. smtp.gmail.com)
# smtp_user => string containing the user name (unauthenticated use "")
# smtp_pass => string containing the password (unauthenticated use "")
def sendMail(to, subject, text, files, server, smtp_user, smtp_pass):
    assert type(to)==list
    assert type(files)==list
    fro = "<"+smtp_user+">"

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    # Add text part to message
    result = msg.attach( MIMEText(text) )

    # Encode and add files to message
    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        result = msg.attach(part)
        
    # ISPs often block port 25, so use gmail's port 587 (which is technically
    # more correct anyway since we are using tls)
    socket.setdefaulttimeout(timeOut)
    smtp = smtplib.SMTP(server, 587)
    if smtp_user != "":
        # RLC - This authentication works with gmail - I have not tested it elsewhere.
        # first you have to say 'hi' to the server
        result = smtp.ehlo()
        # start the secure session. Google requires it, and you won't get in
        # trouble from your ISP for sending "SPAM".
        result = smtp.starttls()
        # say hello again
        result = smtp.ehlo()
        # login
        result = smtp.login(smtp_user, smtp_pass)
    # Send off the message
    # raise Exception
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.quit() # to be uncommented with python 2.6 / 3.0


def verifyLang(testSet, langSet):
    foundMatch = True
    for word in testSet:
      foundMatch = foundMatch and (word in langSet)
      if not foundMatch:
        break
    return foundMatch

def nextAvailable(path, msgn,extn):
    j=0
    while os.path.exists(os.path.join(tempfile.gettempdir(),path,msgn+str(j)+'.'+extn)):
      j=j+1
    return os.path.join(tempfile.gettempdir(),path,msgn+str(j)+'.'+extn)

#----- begin no-sync zone

print ''
print 'This is gKnujOn, version '+str(Version)
if ('-h' in sys.argv) or (len(sys.argv) == 1):
  print 'Usage: gknujon.py -l username -p password -r reportingaddress'
  print '       -p can be omitted to interactively enter a password'
  print 'Optional parameters:'
  print '- set the time out for the smtp connection to a custom value, default=10'
  print ' -timeOut 20'
  print '- set maxReportSize to the maximal number of spams you want each email (report) to contain, default=50'
  print ' -maxReportSize 17'
  print '- set if you want all your spam, read AND unread, reported'
  print ' -processAllSpam'
  print '- set if you want your reports automatically trashed'
  print ' -autoTrashReports'
  print '- set if you want your spam automatically trashed'
  print ' -autoTrashSpam'
  print '- set if you want the SEC delivery notifications automatically deleted'
  print ' -autoTrashSec'
  print '- set if you want your stockjunk reported somewhere else'
  print ' -s stockjunkreportingaddress'
  print '- set if you don''t want any interaction'
  print ' -automate'
  raw_input('Exiting, press Enter...')
  raise SystemExit
if '-l' in sys.argv:
  username = sys.argv[sys.argv.index('-l')+1]
else:
  print 'Error: No Username Found!'
  print '-> usage: gknujon.py -l username'
  raw_input('Exiting, press Enter...')
  raise SystemExit
if '-p' in sys.argv:
  try:
    password = sys.argv[sys.argv.index('-p')+1]
    if password.startswith("-"):
      password = getpass.getpass('Enter password for '+username+' : ')
  except IndexError:
    password = getpass.getpass('Enter password for '+username+' : ')
else:
  print 'No Password Found!'
  print '-> usage: gknujon.py -p password.'
  print '- Enter your password now or press Enter to exit.'
  password = getpass.getpass('Enter password for '+username+' : ')
  if password == "":
    raise SystemExit
if '-r' in sys.argv:
  to = sys.argv[sys.argv.index('-r')+1]
else:
  print 'Error: No Reporting Address Found!'
  print '-> usage: gknujon.py -r reportingaddress'
  raw_input('Exiting, press Enter...')
  raise SystemExit
if '-timeOut' in sys.argv:
  timeOut = int(sys.argv[sys.argv.index('-timeOut')+1])
else:
  timeOut = 10
if '-maxReportSize' in sys.argv:
  maxReportSize = int(sys.argv[sys.argv.index('-maxReportSize')+1])
else:
  maxReportSize = 50
if '-processAllSpam' in sys.argv:
  processAllSpam = ''
else:
  processAllSpam = 'AND is:unread '
if '-s' in sys.argv:
  stockTo = sys.argv[sys.argv.index('-s')+1]
  useStockTo = True
else:
  useStockTo = False    
if '-autoTrashReports' in sys.argv:
  autoTrashReports = True
else:
  autoTrashReports = False    
if '-autoTrashSpam' in sys.argv:
  autoTrashSpam = True
else:
  autoTrashSpam = False
if '-autoTrashSec' in sys.argv:
  autoTrashSec = True
else:
  autoTrashSec = False
if '-automate' in sys.argv:
  automate = True
else:
  automate = False

#----- end no-sync zone

# and... action! First login and set everything up
# Create IMAP connection and try to login
#socket.setdefaulttimeout(20.0)
ga = imaplib.IMAP4_SSL("imap.gmail.com")
try:
  ga.login(username, password)
except imaplib.IMAP4.error:
  print "Login failed. (Wrong username/password?)"
  raw_input("Exiting... Press Enter to Close")
  raise SystemExit
else:
  print "Login successful - "+username+' logged in'
if not os.path.exists(os.path.join(tempfile.gettempdir(),'downloaded_spam')):
  os.mkdir(os.path.join(tempfile.gettempdir(),'downloaded_spam'))

  
# Check to see what language we are in
mb_names = []
mb_list = ga.list()
spam_mb = 'Spam'
mb_name = 'Gmail'
for item in mb_list[1]:
  mb_item = item.split('"')[3]
  if (mb_item[:7] == "[Gmail]"):
    mb_names.append(mb_item[8:])
  if (mb_item[:13] == "[Google Mail]"):
    mb_name = 'Google Mail'
    mb_names.append(mb_item[14:])
mb_names = mb_names[1:]
if verifyLang(mb_names,['All Mail', 'Drafts', 'Important', 'Sent Mail', 'Spam', 'Starred', 'Trash']):
  # Must be English
  sent_mb = 'Sent Mail'
  trash_mb = 'Trash'
elif verifyLang(mb_names,['Brouillons', 'Corbeille', 'Important', 'Messages envoy&AOk-s', 'Spam', 'Suivis', 'Tous les messages']):
  # Must be French
  sent_mb = 'Messages envoy&AOk-s'
  trash_mb = 'Corbeille'
elif verifyLang(mb_names,['Alle Nachrichten', 'Entw&APw-rfe', 'Wichtig', 'Gesendet', 'Markiert', 'Papierkorb', 'Spam']):
  # Must be German
  sent_mb = 'Gesendet'
  trash_mb = 'PapierKorb'
elif verifyLang(mb_names,['Borradores', 'Destacados', 'Importante', 'Enviados', 'Papelera', 'Spam', 'Todos']):
  # Must be Spanish
  sent_mb = 'Enviados'
  trash_mb = 'Papelera'   
elif verifyLang(mb_names,['Kosz', 'Spam', 'Wersje robocze', 'Wa&AXw-ne', 'Wszystkie', 'Wys&AUI-ane', 'Oznaczone gwiazdk&AQU-']):
  # Must be Polish
  sent_mb = 'Wys&AUI-ane'
  trash_mb = 'Kosz'
elif verifyLang(mb_names,['Bozze', 'Cestino', 'Posta inviata', 'Importante', 'Spam', 'Speciali', 'Tutti i messaggi']):
  # Must be Italian
  sent_mb = 'Posta inviata'
  trash_mb = 'Cestino'
elif verifyLang(mb_names,['Kaikki viestit', 'Luonnokset', 'L&AOQ-hetetyt viestit', 'Roskakori', 'Roskaposti', 'T&AOQ-hdell&AOQ- merkityt', 'T&AOQ-rke&AOQA5A-']):
  # Must be Finnish
  spam_mb = 'Roskaposti'
  sent_mb = 'L&AOQ-hetetyt viestit'
  trash_mb = 'Roskakori'
elif verifyLang(mb_names,['Alla mail', 'Papperskorgen', 'Skickat mail', 'Skr&AOQ-ppost', 'Stj&AOQ-rnm&AOQ-rkt', 'Utkast', 'Viktigt']):
  # Must be Swedish
  spam_mb = 'Skr&AOQ-ppost'
  sent_mb = 'Skickat mail'
  trash_mb = 'Papperskorgen'
elif verifyLang(mb_names,['All Mail', 'Bin', 'Drafts', 'Important', 'Sent Mail', 'Spam', 'Starred']):
  # Must be UK English
  sent_mb = 'Sent Mail'
  trash_mb = 'Bin'
elif verifyLang(mb_names,['Alle berichten', 'Concepten', 'Met ster', 'Belangrijk', 'Prullenbak', 'Spam', 'Verzonden berichten']):
  # Must be Dutch
  sent_mb = 'Verzonden berichten'
  trash_mb = 'Prullenbak'
elif verifyLang(mb_names,['G&APY-nderilmi&AV8- Postalar', 'Spam', 'Taslaklar', 'T&APw-m Postalar', 'Y&ATE-ld&ATE-zl&ATE-', '&AMcA9g-p kutusu', '&ANY-nemli']):
  # Must be Turkish
  sent_mb = 'G&APY-nderilmi&AV8- Postalar'
  trash_mb = '&AMcA9g-p kutusu'
else:
  # Unknown Language
  print "Language is unknown and unsupported. Please send the authors this" + \
        " message and the following text. If possible, please include a" + \
        " translation."
  print mb_names
  raise SystemExit

# first the stockjunk
if useStockTo:
  if not os.path.exists(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk')):
    os.mkdir(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk'))
  # Select the gmail Spam box
  ga.select('['+mb_name+']/'+spam_mb)
  
  # There is probably a slicker way to search for more than one item, but this
  # works.
  response, mail_list = ga.search(None, "BODY", "application/pdf")
  folder = mail_list[0].split()
  response, mail_list = ga.search(None, "BODY", "image/jpg")
  folder.extend( mail_list[0].split() )
  response, mail_list = ga.search(None, "BODY", "image/jpeg")
  folder.extend( mail_list[0].split() )
  response, mail_list = ga.search(None, "BODY", "image/gif")
  folder.extend( mail_list[0].split() )
  response, mail_list = ga.search(None, "BODY", "image/png")
  folder.extend( mail_list[0].split() )
  
  # Eliminate duplicates
  folder = list(set(folder))
  
  # Eliminate any read messages if "processAllSpam" flag is not set
  if processAllSpam != '':
    # Get list of unread messages
    response, unread = ga.search(None, "UNSEEN")
    # Messages comes down as space delimited list of message ids, all packed
    # into the first element of a list, so we need to split up the line to make
    # a proper list. This is done every time we use the "search" function.
    unread = unread[0].split()
    # loop through "folder" list and only include messages which are unread
    new_folder = []
    for item in folder:
      if item in unread:
        new_folder.append(item)
    # replace the old list with the unread-only list
    folder = new_folder
  
  total=len(folder)
  print '- '+str(total)+' (presumed) stockspam messages found in '+string.replace(spam_mb,'&','+').decode('utf-7').encode('utf-8')+' folder'
  i = 0
# download the junk
  for msg in folder:
    i = i + 1
    print "\r"+" "*60, 
    print "\r"+' - downloading (presumed) stockspam message ('+str(i)+'/'+str(total)+')',
    sys.stdout.flush()
    f = open(nextAvailable('downloaded_stockjunk',msg,'txt'),'wb')
    # Get contents of message - 'RFC822' returns the entire message, including
    # the header. "fetch" returns a multi-dimensional list, and we are only
    # interested in the 2nd part of the 1st element, which is the contents of
    # the message
    response, message = ga.fetch(msg,'RFC822')
    # mark message as read (\\SEEN in IMAP's terminology)
    ga.store(msg,'+FLAGS', '\\SEEN')
    f.writelines(message[0][1])
    f.close()
# zip the junk
  if (total>0):
    print ''
  spamlist = os.listdir(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk'))
  toRemove=[]
  for spam in spamlist:
    if not spam.endswith(".txt"):
      toRemove.append(spam)
  for spam in toRemove:
    spamlist.remove(spam)
  total = len(spamlist)
  if (total>0):
    stockJunkZip = zipfile.ZipFile(nextAvailable('downloaded_stockjunk','stockJunkZip','zip'), 'w',zipfile.ZIP_DEFLATED)
    i=0
    for spam in spamlist:
      i=i+1
      print "\r"+" "*60, 
      print "\r"+' - Zipping stockspam message ('+str(i)+'/'+str(total)+')',
      sys.stdout.flush()
      stockJunkZip.write(os.path.join(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk'),spam), spam)
      os.remove(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk',spam))
      if ((i%maxReportSize)==0) and (i<>total):
        stockJunkZip.close()
        stockJunkZip = zipfile.ZipFile(nextAvailable('downloaded_stockjunk','stockJunkZip','zip'), 'w',zipfile.ZIP_DEFLATED)
    if (i>0):
      print ''
    stockJunkZip.close()
# report the junk
  ziplist = os.listdir(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk'))
  total=len(ziplist)
  if (total>0):
    i=0
    for name in ziplist:
      i=i+1
      names = []
      names.append(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk',name))
      try:
        # sendMail is defined above - it handles the message creation and sending.
        sendMail( [stockTo], 'stockspam report', '', names, 'smtp.gmail.com', username, password )
        print "\r"+" "*60, 
        print "\r"+' - Sent report ('+str(i)+'/'+str(total)+')',
        sys.stdout.flush()
        os.remove(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk',name))
      except:
        print ' Reporting failed.'
    if (i>0):
      print ''
  if os.path.exists(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk')):
    try:
      os.rmdir(os.path.join(tempfile.gettempdir(),'downloaded_stockjunk'))
    except OSError:
      True
      
# then onto the rest of the junk
# Select the Gmail Spam box
ga.select('['+mb_name+']/'+spam_mb)
if processAllSpam == '':
  # Get all spam, not just Unread.
  response, folder = ga.search(None, "ALL")
else:
  # UNSEEN is IMAP-terminology for "Unread"
  response, folder = ga.search(None, "UNSEEN")
folder = folder[0].split()
total=len(folder)
print '- '+str(total)+' messages found in '+string.replace(spam_mb,'&','+').decode('utf-7').encode('utf-8')+' folder'
i = 0
# download the junk
for msg in folder:
  i = i + 1
  print "\r"+" "*60, 
  print "\r"+' - downloading spam message ('+str(i)+'/'+str(total)+')',
  sys.stdout.flush()
  f = open(nextAvailable('downloaded_spam',msg,'txt'),'wb')
  # Get contents of message - 'RFC822' returns the entire message, including
  # the header. "fetch" returns a multi-dimensional list, and we are only
  # interested in the 2nd part of the 1st element, which is the contents of
  # the message
  response, message = ga.fetch(msg,'RFC822')
  # mark message as read (\\SEEN in IMAP's terminology)
  ga.store(msg,'+FLAGS', '\\SEEN')
  f.writelines(message[0][1])
  f.close()
if (total>0):
  print ''
spamlist = os.listdir(os.path.join(tempfile.gettempdir(),'downloaded_spam'))
toRemove=[]
for spam in spamlist:
  if not spam.endswith(".txt"):
    toRemove.append(spam)
for spam in toRemove:
  spamlist.remove(spam)
total = len(spamlist)
if (total>0):
  junkZip = zipfile.ZipFile(nextAvailable('downloaded_spam','junkZip','zip'), 'w',zipfile.ZIP_DEFLATED)
  i=0
  for spam in spamlist:
    i=i+1
    print "\r"+" "*60, 
    print "\r"+' - Zipping spam message ('+str(i)+'/'+str(total)+')',
    sys.stdout.flush()
    junkZip.write(os.path.join(tempfile.gettempdir(),'downloaded_spam',spam),spam)
    os.remove(os.path.join(tempfile.gettempdir(),'downloaded_spam',spam))
    if ((i%maxReportSize)==0) and (i<>total):
      junkZip.close()
      junkZip = zipfile.ZipFile(nextAvailable('downloaded_spam','junkZip','zip'), 'w',zipfile.ZIP_DEFLATED)
  if (i>0):
    print ''
  junkZip.close()
# report the junk
ziplist = os.listdir(os.path.join(tempfile.gettempdir(),'downloaded_spam'))
total=len(ziplist)
if (total>0):
  i=0
  for name in ziplist:
    i=i+1
    names = []
    names.append(os.path.join(tempfile.gettempdir(),'downloaded_spam',name))
    try:
      # sendMail is defined above - it handles the message creation and sending.
      sendMail( [to], 'spam report', '', names, 'smtp.gmail.com', username, password )
      print "\r"+" "*60, 
      print "\r"+' - Sent report ('+str(i)+'/'+str(total)+')',
      sys.stdout.flush()
      os.remove(os.path.join(tempfile.gettempdir(),'downloaded_spam',name))
    except:
      print ' Reporting failed.'
  if (i>0):
    print ''
if os.path.exists(os.path.join(tempfile.gettempdir(),'downloaded_spam')):
  try:
    os.rmdir(os.path.join(tempfile.gettempdir(),'downloaded_spam'))
  except OSError:
    True

# reports clean up from sent mail
# Select the Gmail Sent Mail box.
ga.select('['+mb_name+']/' + sent_mb)
# Search for any messages with the Subject: spam report and the
# To: <spam reporting address>
response, folder = ga.search(None, "SUBJECT", 'spam report', "TO", to)
folder = folder[0].split()
stockfolder = []
if useStockTo:
  # Search for any messages with the Subject: stockspam report and the
  # To: <stock spam reporting address>
  response, stockfolder = ga.search(None, "SUBJECT", 'stockspam report', "TO", stockTo)
  stockfolder = stockfolder[0].split()


print "- There are "+str(len(folder)+len(stockfolder))+" spam reports in your "+string.replace(sent_mb,'&','+').decode('utf-7').encode('utf-8')
if (len(folder)+len(stockfolder))>0:
  next = 'y'
  if not autoTrashReports:
    if automate:
      next = 'n'
    else:
      next = raw_input(" Trash the spam reports? (y/n) \n or Press Enter to quit: ")
    if next=='':
      raise SystemExit
  if (next=='y'):
    i = 0
    total = len(folder)+len(stockfolder)
    for msg in stockfolder:
      i = i + 1
      print "\r"+" "*60, 
      print "\r"+" Trashing spam report: ("+str(i)+"/"+str(total)+")",
      sys.stdout.flush()
      # To move a message using IMAP, we first copy it to the trash folder,
      # then set it's flag to /DELETE. Finally, expunge the messages to delete
      # them from the server.
      # NOTE: cutting out the copy would save time - do we really want this
      #       item moved into the Trash folder???
      ga.copy(msg,'['+mb_name+']/'+trash_mb)
      ga.store(msg,'+FLAGS', '\\Deleted')
    for msg in folder:
      i = i + 1
      print "\r"+" "*60, 
      print "\r"+" Trashing spam report: ("+str(i)+"/"+str(total)+")",
      sys.stdout.flush()
      ga.copy(msg,'['+mb_name+']/'+trash_mb)
      ga.store(msg,'+FLAGS', '\\Deleted')
    # Expunge all deleted messages. Until this command, the deleted messages
    # are just flagged for deletion... this will remove them for good.
    ga.expunge()
    print ""

# INBOX clean up (enforcement notifications)
# Select the main mailbox (Inbox)
ga.select()
response, folder = ga.search(None, "SUBJECT", 'Delivery Notification / Enforcement Complaint Response', "FROM", 'enforcement@sec.gov')
folder = folder[0].split()
print "- There are "+str(len(folder))+" SEC-delivery notifications in your inbox"
if len(folder)>0:
  next = 'y'
  if not autoTrashSec:
    if automate:
      next = 'n'
    else:
      next = raw_input(" Clean Inbox? (y/n) \n or Press Enter to quit: ")
    if next=='':
      raise SystemExit
  if (next=='y'):
    i = 0
    total = len(folder)
    for msg in folder:
      i = i + 1
      print "\r"+" "*60, 
      print "\r"+" trashing ("+str(i)+"/"+str(total)+") :   "+msg.subject[:30]+"...",
      sys.stdout.flush()
      # To move a message using IMAP, we first copy it to the trash folder,
      # then set it's flag to /DELETE. Finally, expunge the messages to delete
      # them from the server.
      # NOTE: cutting out the copy would save time - do we really want this
      #       item moved into the Trash folder???
      ga.copy(msg,'['+mb_name+']/'+trash_mb)
      ga.store(msg,'+FLAGS', '\\Deleted')      
    # Expunge all deleted messages. Until this command, the deleted messages
    # are just flagged for deletion... this will remove them for good.
    ga.expunge()
    print ""

		
# spam folder clean up
# Select the Gmail Spam box
ga.select('['+mb_name+']/'+spam_mb)
# Search for all read messages. Ignore unread, since they might have arrived
# after our script started running.
response, folder = ga.search(None, "SEEN")
folder = folder[0].split()
# gmail drops the message as soon as the flag is set to delete, so we need to
# sort the list in reverse so that the highest number gets dropped first. This
# is likely to be a bug in gmail, but this fix shouldn't break even if they fix
# the bug.
folder.reverse()
print "- There are "+str(len(folder))+" messages in your "+string.replace(spam_mb,'&','+').decode('utf-7').encode('utf-8')+" folder"
if len(folder)>0:
  next = 'y'
  if not autoTrashSpam:
    if automate:
      next = 'n'
    else:
      next = raw_input(" Empty spam folder? (y/n) \n or Press Enter to quit: ")
    if next=='':
      raise SystemExit
  if (next=='y'):
    i = 0
    total = len(folder)
    subject_re = re.compile("Subject: (.*)")
    for msg in folder:
      i = i + 1
      print "\r"+" "*60, 
      header = ga.fetch(msg,'RFC822.HEADER')
      header = header[1][0][1]
      subject = subject_re.search(header)
      if subject:
        subject = subject.group(1)
      else:
        subject = ''
      if (len(subject)>0):
        subject=subject[:len(subject)-1]
      print "\r"+" trashing ("+str(i)+"/"+str(total)+"):  "+subject[:50]+"...",
      sys.stdout.flush()
      # To move a message using IMAP, we first copy it to the trash folder,
      # then set it's flag to /DELETE. Finally, expunge the messages to delete
      # them from the server.
      # NOTE: cutting out the copy would save time - do we really want this
      #       item moved into the Trash folder???
      ga.copy(msg,'['+mb_name+']/'+trash_mb)
      ga.store(msg,'+FLAGS', '\\Deleted')      
    # We don't technically need to do this in gmail, since stuff in the spam
    # folder gets deleted as soon as it is marked. Doing the expunge anyway
    # won't hurt anything, and will avoid relying on the special behavior of the
    # Spam box if they ever "fix" it to work in the standard way.
    ga.expunge()
    print ""
# Close out and clean up the mailbox
ga.close()
# Logout of IMAP server
ga.logout()
if not automate:
  raw_input("Press Enter to quit... ")
