#!/usr/bin/python -W ignore
#
# This script provides named entity recogntion with the NER-tagger from Stanford NLP.
# 
# Each line is tokenized into sentences -- a few lines are not correctly split into sentences by cc-segment-stories.
#
# http://www-nlp.stanford.edu/software/CRF-NER.shtml
# http://www.nltk.org/api/nltk.tag.html#module-nltk.tag.stanford
#
#       20130101012604.000|20130101012626.000|NER_03|Bill/PERSON|Clinton/PERSON|U.S./LOCATION
#       Start time|End time|Primary tag(|Word/ner tag)*
#
# Written by FFS, 2014-08-09
#
# Changelog:
#
#       2014-08-13 Set #!/usr/bin/python -W ignore to turn off Unicode warnings
#       2014-08-10 Server mode via pyner -- note dict output
#       2014-08-09 Forked from PartsOfSpeech-StanfordNLP-01.py
#
# -----------------------------------------------------------------------------------------------------------------

# User input
import sys, os.path
scriptname = os.path.basename(sys.argv[0])
filename = sys.argv[1]

# Help screen
if filename == "-h" :  
   print "".join([ "\n","\t","This is a production script for named entity recognition -- issue:","\n" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg > $FIL.pos or" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg | sponge $FIL.seg" ])
   print "".join([ "\n","\t","or use the seg-NER bash script for bulk processing." ])
   print "".join([ "\n","\t","Limit to six instances to avoid socket errors.","\n" ])
   quit()

# Libraries
import datetime, re

# Server mode (TCP/IP sockets, mixed and caseless, supported by pyner)
import ner
Mix = ner.SocketNER(host='localhost', port=2020, output_format='slashTags')
UPP = ner.SocketNER(host='localhost', port=2021, output_format='slashTags')

# Pattern for tokenizing
# http://www.clips.ua.ac.be/pages/pattern-en
from pattern.en import tokenize

# Counter
n = 0

# A. Get the lines from the file
with open(filename) as fp:
   for line in fp:

# B. Split each line into fields
      field = line.split("|")

#    Pretty debug
#     print('\n'.join('{}: {}'.format(*k) for k in enumerate(field)))

# C. Header and footer
      if len(field[0]) != 18:
         print line,
         continue

# D. Program credit
      if n == 0:
         credit=["NER_03|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=stanford-ner 3.4, ",scriptname,"|Source_Person=Jenny Rose Finkel, FFS|Codebook=Category/Entity"]
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

# H. Ensure the text is split into sentences
     # tokenize(string, punctuation=".,;:!?()[]{}`''\"@#$^&*+-|=~_", replace={})
      for sentence in tokenize(text):
         all = ""

# I. Select the parser
         if sentence.isupper() or sentence.islower(): st = UPP
         else: st = Mix

# J. Parts of speech with stanford-ner via pyner
         reply = st.get_entities(sentence)
         # {u'PERSON': [u'Bill Clinton'], u'LOCATION': [u'U.S.'], u'O': [u'was President of the']}
         try:
             for tup in reply.items():
                names = ""
                if tup[0] == "O" or not tup[0] : continue
                for name in tup[1]:
                   names = "".join([names,"/",name])
                all = "".join([all,"|",tup[0],names])
             if all != "": print "".join([field[0],"|",field[1],"|NER_03",all])
             # I/PRP|'M/MD|JOHN/NNP|DOE/NNP
         except (UnicodeDecodeError, UnicodeEncodeError, IndexError, AssertionError):
             print "".join([field[0],"|",field[1],"|NER_03","|NA"])
             continue

# K. Close the file
fp.close()

# EOF
