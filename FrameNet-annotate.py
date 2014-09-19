#!/usr/bin/python
#
# This script annotates lemmas using python-framenet for NLTK 3.0 and the FrameNet 1.5 corpus.
# It is superceded by seg-FrameNet, which uses Semafor 3.0.
# 
#       http://www.nltk.org/howto/framenet.html
# 
# Each line is tokenized into sentences and then lemmatized by a local stanford-postagger socket server.
#
# The list of POSs used in the LUs is:
# v=verb n=noun a=adj adv=adv prep=prep num=numbers intj=interjection art=article c=conjunction scon=subordinating conjunction
#
# Written by FFS, 2014-08-03
#
# To do:
#
#       2014-08-26 Use stanford CoreNLP also for lemmatization
#
# Changelog:
#
#       2014-08-27 Add multiple frames per lemma and remove frame relations; add frame number argument
#       2014-08-26 Use stanford CoreNLP ssplit to catch run-ons
#       2014-08-14 Use stanford lemmatizer via POStagger (twice as fast as MBSP)
#       2014-08-06 Fixed FrameNet query logic (thanks to Nathan Schneider)
#       2014-08-03 Forked from PartsOfSpeech-01.py
#
# ------------------------------------------------

# User input
import sys, os.path
scriptname = os.path.basename(sys.argv[0])
filename = sys.argv[1]

# Help screen
if filename == "-h" :  
   print "".join([ "\n","\t","Test script for semantic frame analysis using FrameNet 1.5.","\n" ])
   print "".join([ "\t","Syntax:" ])
   print "".join([ "\t","\t",scriptname," <input filename> <number of frames to include> (default 3)" ])
   print "".join([ "\n","\t","Examples:" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg 5 > $FIL.frames" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg | tee -a $FIL.frames" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg | sponge $FIL.seg" ])
   print "".join([ "\n","\t","Use the seg-FrameNet bash script for bulk processing.","\n" ])
   quit()

# Number of frames to include
if len(sys.argv) > 2 :
    numframes = int(sys.argv[2])
else : numframes = 3

# Utility libraries
import datetime, string, re
from lxml.etree import fromstring

# Lemmatizer fram stanford.postagger via pypos, a tweak on pyner
import pos
Mix = pos.SocketPOS(host='localhost', port=9022, output_format='slashTags')
UPP = pos.SocketPOS(host='localhost', port=9023, output_format='slashTags')

# stanford-corenlp-python for sentence splitting to catch run-on sentences
# This slows down processing quite a bit -- if multiple instances, get the load balancer version
import jsonrpclib
from simplejson import loads
server = jsonrpclib.Server("http://localhost:8080")

# FrameNet
import nltk
from pprint import pprint
from nltk.corpus import framenet as fn

# This version does not work for 2.7, but might for 3.4
#from nltk.corpus.reader import framenet as fn
#print(fn)

# Debug
#len(fn.frames())
#print len(fn.frames())
#quit()

# Counter
n = 0

# A. Open the file
with open(filename) as fp:

   # Search within file -- filter out Named Entities?
   #pat = re.compile("^([A-Z][0-9]+)*$")
   #print sum(1 for line in fp if pat.search(line))
   #print ''.join((line for line in fp if pat.search(line)))

   # Examine a line at a time
   for line in fp:

# B. Strip newline and split into fields
      field = line.split("|")

#    Pretty debug
#     print('\n'.join('{}: {}'.format(*k) for k in enumerate(field)))

# C. Header and footer
      if len(field[0]) != 18:
          print line,
          continue

# D. Program credit
      if n == 0:
          credit=["FRM_01|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=FrameNet 1.5, ",scriptname,"|Source_Person=Charles Fillmore, FFS|Codebook=Lemma|Frame names"]
          print  "".join(credit)
          credit=["FRM_02|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=FrameNet 1.5, ",scriptname,"|Source_Person=Charles Fillmore, FFS|Codebook=Frame name|Core elements"]
          print  "".join(credit)
          n=1

# E. Segment tags and other non-caption tags
      if field[2] == "SEG":
          print line,
          continue
      elif len(field[2]) != 3:
          print line,
          continue

# F. Get the text, clean leading chevrons -- if BOM, strip non-ascii, otherwise remove individually
      try:
          text = re.sub('^[>,\ ]{0,6}','', field[3])
          if re.search("(\xef\xbf\xbd)", text): text = ''.join([x for x in text if ord(x) < 128])
          if text.strip() == '' : continue
          text = re.sub('[()]', '', text)
          text = str(text).replace('?','.').replace('!','.').replace('[','').replace(']','').replace('+',' plus ').replace('*','').replace('...',' ')
        #  text = str(text).replace('won\'t','will not').replace('shan\'t','shall not').replace('n\'t',' not')
        #  text = re.sub('won\'t', 'will not', text)
        #  text = re.sub('shan\'t', 'shall not', text)
        #  text = re.sub('n\'t', ' not', text)
          text = str(text).replace('\x00 ','').replace('\xef\xbf\xbd','')
          text = str(text).replace('\xf7','').replace('\xc3\xba','').replace('\xb6','').replace('\xa9','').replace('\xe2\x99\xaa','')
          text = str(text).replace('\xc3\xaf','').replace('\x5c','').replace('\xf1','').replace('\xe1','').replace('\xe7','').replace('\xfa','')
          text = str(text).replace('\xf3','').replace('\xed','').replace('\xe9','').replace('\xe0','').replace('\xae','').replace('\xc2','')
          text = str(text).replace('\xc3','').replace('\xa2','').replace('\xbf','')
#         print text
      except IndexError:
          print line
          continue

# G. Remove clearly wrong unicode characters -- BOM, NULL (only utf8 hex works)
      line = str(line).replace('\x00 ','').replace('\xef\xbf\xbd','')
      print line,

# H. Use stanford-corenlp-python to split run-on sentences
      reply = loads(server.parse(text.decode('utf-8', errors='ignore')))
      for dicts in reply.items()[0][1]:
        sentence = dicts.items()[1][1]

# H. Select the parser
        if sentence.isupper() or sentence.islower(): st = UPP
        else: st = Mix

# I. Lemmas with stanford-postagger via pyner (faster than MBSP)
     # May erratically truncate extremely long sentence strings!
        try:
          sentences = str(st.tag_text(sentence)).replace("</sentence>\n","</sentence>|")
#         print sentences
          for sentence in sentences.split("|"):
              if sentence.strip() == '' : continue
#             print sentence
              for tree in fromstring(sentence):
                  lemma = tree.items()[2][1].lower()
#                 print lemma

                  # Lemmas to skip (use re.match)
                  if lemma == "that" or lemma == "this" : continue
                  try:
                        # Query FrameNet -- frame names
                        frames = fn.frames_by_lemma(lemma) ; framenames = ""
                        for frame in frames:
#                           print frame.name,
#                           print len(frames)
#                           continue
                            # Cutoff point
                            if len(frames) > numframes : continue
                            framenames = "".join([framenames,"|",frame.name])
                        if framenames != "": print "".join([field[0],"|",field[1],"|FRM_01|",lemma,framenames])

                        # Core Frame Elements
                        for frame in frames:
                            if len(frames) > numframes : continue
                            ID = frame.ID ; framecores = ""
                            cores = [(fename,fe.ID) for fename,fe in fn.frame(ID).FE.items() if fe.coreType=='Core']
                            for core in cores: framecores = "".join([framecores,"|",core[0]])
                            if framecores != "": print "".join([field[0],"|",field[1],"|FRM_02|",frame.name,framecores])
                  except (AttributeError, nltk.corpus.reader.framenet.FramenetError):
                        continue
        except (UnicodeDecodeError, UnicodeEncodeError, IndexError, AssertionError):
          # Tag failed UTF-8 lines NA to enable repair
          print "".join([field[0],"|",field[1],"|FRM_01","|NA"])
          continue

# Clean up
fp.close()

# EOF
