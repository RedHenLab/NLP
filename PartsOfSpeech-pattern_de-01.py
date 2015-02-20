#!/usr/bin/python
#
# Written by FFS, 2014-07-18
#
# To do:
#
# Changelog:
#
#       2015-02-05 Read the file in utf8 -- why didn't I know this earlier?
#       2014-12-21 Forked from Sentiment-02.py, support German parts of speech and utf-8 output
#       2014-07-31 Each line is tokenized into sentences for MBSP, but not yet Pattern
#       2014-07-30 Catch MBSP utf8 error or file is truncated; no tokenization
#       2014-07-29 Added parts of speech tag, changed name to CLiPS-02.py
#       2014-07-27 Learned enough python to control the format, logic improved 
#       2014-07-18 First version SentiWordNet.py, poor sentiment output format
#
# --------------------------------------------------------------------------------------------------

# User input
import sys, os.path, datetime, re, codecs
scriptname = os.path.basename(sys.argv[0])
filename = sys.argv[1]

# Help screen
if filename == "-h" :
   print "".join([ "\n","\t","This is a production script for German parts of speech annotation -- issue:","\n" ])
   print "".join([ "\t","\t",scriptname," $FIL.txt > $FIL.seg" ])
   print "".join([ "\n","\t","or use the seg-PartsOfSpeech-pattern_de bash script for bulk processing.","\n" ])
   quit()

# Libraries
from pattern.de import parse

# Counter
n = 0

# A. Get the lines from the file in utf8
with codecs.open(filename,encoding='utf8') as fp:
   for line in fp:

# B. Split each line into fields
      field = line.split("|")

#    Pretty debug
#     print('\n'.join('{}: {}'.format(*k) for k in enumerate(field)))

# C. Header and footer
      if len(field[0]) != 18:
         print line.encode('utf8'),
         continue

# D. Program credit
      if n == 0:
         credit=["POS_03|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=Pattern.de 2.6, ",scriptname,"|Source_Person=Tom De Smedt, FFS|Codebook=Treebank II"]
         print  "".join(credit).encode('utf8')
         n=1

# E. Segment tags and other non-caption tags
      if field[2] == "SEG":
         print line.encode('utf8'),
         continue
      elif len(field[2]) != 3:
         print line.encode('utf8'),
         continue

# F. Get the text, clean leading chevrons, and print the line
      try:
         text = re.sub('^[>,\ ]{0,6}', '', field[3])
      except IndexError:
         print line.encode('utf8')
         continue
      print line.encode('utf8'),
      snt = ""

# G. Clean ups
      text = re.sub('Mind\.', 'Mindestens', text)

# H. Pattern 2.6 parts of speech -- split the text if needed
      try:
         pos = parse(text, lemmata=True, relations=True, encoding = 'utf-8')
         for pos in pos.splitlines():
             pos = re.sub('\ ', '|', pos)
             print u"".join([field[0],"|",field[1],"|POS_03|",pos]).encode('utf-8').strip()
      except (UnicodeDecodeError, UnicodeEncodeError, IndexError, AssertionError):
         # Tag failed lines NA to enable repair
         print "".join([field[0],"|",field[1],"|POS_03","|NA"])

# I. Close the file
fp.close()

# EOF
