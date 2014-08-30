#!/usr/bin/python -W ignore
#
# This script reads a .seg file and parses each caption line for sentiment (polarity and subjectivity).
#
# First, it scores each sentence using the native sentiment detector in Pattern2.6
# https://github.com/clips/pattern and http://www.clips.ua.ac.be/pages/pattern-en#sentiment
#
#       20140710235636.492|20140710235648.904|SMT_01|0.1|0.45|different|0.0|0.6|very|0.2|0.3
#       Start time|End time|Primary tag|Sentence polarity|Sentence subjectivity(|Word|Word polarity|Word subjectivity)*
#
# Second, it scores the words present in the SentiWordNet dictionary.
# http://sentiwordnet.isti.cnr.it/ and http://sentiwordnet.isti.cnr.it/docs/SWNFeedback.pdf
# cartago:/usr/share/pyshared/pattern/text/en/wordnet/SentiWordNet_3.0.0_20130122.txt
#
#       20140720230042.157|20140720230050.866|SMT_02|HOLLYWOOD|0.0|0.0|MOURNING|-0.625|0.625|MAVERICK|0.375|0.375|OVER|0.375
#       Start time|End time|Primary tag(|Word|Word polarity|Word subjectivity)*
#
# Third, it scores the sentence using TextBlob 0.9-dev PatternAnalyzer sentiment detection, which may have a better lexicon
# http://textblob.readthedocs.org/en/dev/advanced_usage.html#advanced -- we seem to get the same scores as SMT_01
#
#       20140720230042.157|20140720230050.866|SMT_03|0.5|0.5
#       Start time|End time|Primary tag|Sentence polarity|Sentence subjectivity
#
# Fourth, it scores the sentence using TextBlob 0.9-dev NaiveBayesAnalyzer, an NLTK classifier trained on a movie reviews corpus
# http://textblob.readthedocs.org/en/dev/advanced_usage.html#advanced -- these scores are very different
#
#       20140720230042.157|20140720230050.866|SMT_04|0.927279087353
#       Start time|End time|Primary tag|Sentence positivity
#
# Direct the output to overwrite the input .seg file (using sponge) or to a new .smt file
# for FIL in `ls -1 /db/tv/2014/2014-07/2014-07-11/*seg` ; do python SentiWordNet.py $FIL > ${FIL%.*}.smt ; done
#
# Not all of these need to be activated at once -- in July-August 2014 we ran the first and second.
#
# Can be called by cc-integrate-rongda-segmentation and seg-Sentiment
#
# Written by FFS, 2014-07-18
#
# Changelog:
#
#       2014-08-13 Set #!/usr/bin/python -W ignore to turn off Unicode warnings
#       2014-08-02 Added sentiment detection SMT_03 and 04 from TextBlob
#       2014-08-02 Forked from CLiPS-03.py for a pure sentiment script
#       2014-07-27 Learned enough python to control the format, logic improved 
#       2014-05-18 First version SentiWordNet.py, poor sentiment output format
#
# --------------------------------------------------------------------------------------------------

# User input
import sys, os.path
scriptname = os.path.basename(sys.argv[0])
filename = sys.argv[1]

# Help screen
if filename == "-h" :
   print "".join([ "\n","\t","This is a production script for sentiment detection -- issue:","\n" ])
   print "".join([ "\t","\t","python ",scriptname," $FIL.seg > $FIL.smt" ])
   print "".join([ "\n","\t","or use the seg-Sentiment bash script for bulk processing.","\n" ])
   quit()

# Libraries
import nltk, datetime, re

# For Pattern2.6 native sentiment detection
# http://www.clips.ua.ac.be/pages/pattern-en#sentiment
from pattern.en import sentiment

# For the SentiWordNet dictionary
# http://www.clips.ua.ac.be/pages/pattern-en#wordnet
from pattern.en import wordnet
from pattern.en import ADJECTIVE

# For TextBlob PatternAnalyzer sentiment detection
# http://textblob.readthedocs.org/en/dev/advanced_usage.html#advanced
from textblob import TextBlob

# For TextBlob NLTK sentiment detection
# http://textblob.readthedocs.org/en/dev/advanced_usage.html#advanced
from textblob.sentiments import NaiveBayesAnalyzer

# Counter
n = 0

# A. Get the lines from the file
with open(filename) as fp:
   for line in fp:

# B. Split each line into fields
      field = line.split("|")

#    Pretty debug
     # print('\n'.join('{}: {}'.format(*k) for k in enumerate(field)))

# C. Header and footer
      if len(field[0]) != 18:
         print line,
         continue

# D. Program credit
      if n == 0:
         credit=["SMT_01|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=Pattern 2.6, ",scriptname,"|Source_Person=Tom De Smedt, FFS|Codebook=polarity, subjectivity"]
         print  "".join(credit)
         credit=["SMT_02|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=SentiWordNet 3.0, ",scriptname,"|Source_Person=Andrea Esuli, FFS|Codebook=polarity, subjectivity"]
         print  "".join(credit)
#         credit=["SMT_03|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=TextBlob 0.9-dev, ",scriptname,"|Source_Person=Steven Loria, FFS|Codebook=polarity, subjectivity"]
#         print  "".join(credit)
#         credit=["SMT_04|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=TextBlob 0.9-dev, NLTK, ",scriptname,"|Source_Person=Steven Loria, FFS|Codebook=positivity"]
#         print  "".join(credit)
         n=1

# E. Write segment tags and other non-caption lines
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
         ext = str(text).replace('\xf3','').replace('\xed','').replace('\xe9','').replace('\xe0','').replace('\xae','').replace('\xc2','')
         text = str(text).replace('\xc3','').replace('\xa2','').replace('\xbf','')
#        print text
      except IndexError:
         print line
         continue

# G. Remove clearly wrong unicode characters -- BOM, NULL (only utf8 hex works)
      line = str(line).replace('\x00 ','').replace('\xef\xbf\xbd','')
      print line,
      snt = ""
      smt = ""
      terms = ""
      smt3 = ""
      smt4 = ""

# G. You could split the text into sentences, but it breaks the adjacency of text and tags
     # http://www.clips.ua.ac.be/pages/pattern-en
     # tokenize(string, punctuation=".,;:!?()[]{}`''\"@#$^&*+-|=~_", replace={})
     # from pattern.en import tokenize
     # for sentence in tokenize(text):

# H. Pattern2.6 built-in sentiment detection by sentence and words
      snt = sentiment(text)
      for tup in sentiment(text).assessments:
         words = " ".join(tup[0])
         terms = "".join([terms,"|",words,"|",str(tup[1]),"|",str(tup[2])])
      if snt != "": print "".join([field[0],"|",field[1],"|SMT_01|",str(snt[0]),"|",str(snt[1]),terms])

# I. Word loop for the SentiWordNet dictionary
      try:
         for word in nltk.word_tokenize(text):
             weight = wordnet.synsets(word, ADJECTIVE)[0].weight
             smt = "".join([smt,"|",word,"|",str(weight[0]),"|",str(weight[1])])
      except (UnicodeDecodeError, UnicodeEncodeError, IndexError, AssertionError): continue
      if smt != "": print "".join([field[0],"|",field[1],"|SMT_02",smt])

      continue

# J. TextBlob default PatternAnalyzer sentiment detection
      try:
         smt3 = TextBlob(text)
         # Sentiment(polarity=0.13636363636363635, subjectivity=0.5)
      except UnicodeDecodeError: continue
      if smt3 != "": print "".join([field[0],"|",field[1],"|SMT_03|",str(smt3.sentiment[0]),"|",str(smt3.sentiment[1])])

# K. TextBlob NLTK sentiment detection
      try:
         smt4 = TextBlob(text, analyzer=NaiveBayesAnalyzer())
         # Sentiment(classification='pos', p_pos=0.9272790873528883, p_neg=0.07272091264711199)
      except UnicodeDecodeError: continue
      if smt4 != "": print "".join([field[0],"|",field[1],"|SMT_04|",str(smt4.sentiment[1])])

# L. Close the file
fp.close()

# EOF
