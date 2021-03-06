#! -*- coding:utf-8 -*-
from __future__ import division
import sys
import os
import re
StopWordtmp = [' ', u'\u3000',u'\u3001', u'\u300a', u'\u300b', u'\uff1b', u'\uff02', u'\u30fb', u'\u25ce',  u'\x30fb', u'\u3002', u'\uff0c', u'\uff01', u'\uff1f', u'\uff1a', u'\u201c', u'\u201d', u'\u2018', u'\u2019', u'\uff08', u'\uff09', u'\u3010', u'\u3011', u'\uff5b', u'\uff5d', u'-', u'\uff0d', u'\uff5e', u'\uff3b', u'\uff3d', u'\u3014', u'\u3015', u'\uff0e', u'\uff20', u'\uffe5', u'\u2022', u'.']

WordDic = {}
StopWord = []
StatisticDic = {}
span = 16

def InitStopword():
	for key in StopWordtmp:
		StopWord.append(key)

def InitDic(Dicfile):
	f = file(Dicfile)
	for line in f:
		line = line.strip().decode('utf-8')
		WordDic[line] = 1;
	f.close()
	print len(WordDic)
	print "Dictionary has built down!"

def InitStatisticDic(StatisticDicfile):
	StatisticDic['<BEG>'] = {}
	f = file(StatisticDicfile)
	for line in f:
		chunk = line.strip().decode('utf-8').split('  ')
		if chunk[0] != '':
			if not StatisticDic['<BEG>'].has_key(chunk[0]):
				StatisticDic['<BEG>'][chunk[0]] = 1
			else:
				StatisticDic['<BEG>'][chunk[0]] += 1

		for i in range(len(chunk) - 1):
			if not StatisticDic.has_key(chunk[i]) and chunk[i] != '':
				StatisticDic[chunk[i]] = {}
			if chunk[i] != '':
				if not StatisticDic[chunk[i]].has_key(chunk[i+1]):
					StatisticDic[chunk[i]][chunk[i+1]] = 1
				else:
					StatisticDic[chunk[i]][chunk[i+1]] += 1
		if not StatisticDic.has_key(chunk[-1]) and chunk[-1] != '':
			StatisticDic[chunk[-1]] = {}
		if chunk[-1] != '':
			if not StatisticDic[chunk[-1]].has_key('<END>'):
				StatisticDic[chunk[-1]]['<END>'] = 1
			else:
				StatisticDic[chunk[-1]]['<END>'] += 1
		
def WordSeg(Inputfile, Outputfile):
	f = file(Inputfile)
	w = file(Outputfile, 'w')
	dic_size = 0
	for key in StatisticDic:
		for keys in StatisticDic[key]:
			dic_size += StatisticDic[key][keys]
	for line in f:
		line = line.strip().decode('utf-8')
		senList = []
		newsenList = []
		tmpword = ''
		for i in range(len(line)):
			if line[i] in StopWord:
				senList.append(tmpword)
				senList.append(line[i])
				tmpword = ''
			else:
				tmpword += line[i]
				if i == len(line) - 1:
					senList.append(tmpword)
		#N-gram
		for key in senList:
			if key in StopWord:
				newsenList.append(key)
			else:
				Pretmplist = PreSenSeg(key, span)
				Posttmplist = PostSenSeg(key, span)
				tmp_pre = P(Pretmplist, dic_size)
				tmp_post = P(Posttmplist, dic_size)
				tmplist = []
				if tmp_pre > tmp_post:
					tmplist = Pretmplist 
				else:
					tmplist = Posttmplist
#print 'tmplist', tmplist
				for keyseg in tmplist:
					newsenList.append(keyseg)
		writeline = ''
		for key in newsenList:
			writeline = writeline + key + '  '
		writeline = writeline.strip('  ')
		w.write(writeline.encode('utf-8') + '\n')
#break

	f.close()
	w.close()

def P(tmplist, dic_size):
	rev = 1
	if len(tmplist) < 1:
		return 0
	'''
	print 'tmplist', tmplist
	print "tmplist[0]", tmplist[0]
	print '-----------'
	'''
	rev *= Pword(tmplist[0], '<BEG>', dic_size)
	rev *= Pword('<END>', tmplist[-1], dic_size)
	for i in range(len(tmplist)-1):
		rev *= Pword(tmplist[i+1], tmplist[i], dic_size)
	return rev

def Pword(word1, word2, dic_size):
#print 'word1:', word1
#print 'word2:', word2
	div_up = 0
	div_down = 0
	if StatisticDic.has_key(word2):
		for key in StatisticDic[word2]:
#print 'key:', key
			div_down += StatisticDic[word2][key]
			if key == word1:
				div_up = StatisticDic[word2][key]
	return (div_up+1) / (div_down + dic_size)

def PreSenSeg(sen, span):
	post = span
	if len(sen) < span:
		post = len(sen)
	cur = 0
	revlist = []
	while 1:
		if cur >= len(sen):
			break
		s = re.search(u"^[0|1|2|3|4|5|6|7|8|9|\uff11|\uff12|\uff13|\uff14|\uff15|\uff16|\uff17|\uff18|\uff19|\uff10|\u4e00|\u4e8c|\u4e09|\u56db|\u4e94|\u516d|\u4e03|\u516b|\u4e5d|\u96f6|\u5341|\u767e|\u5343|\u4e07|\u4ebf|\u5146|\uff2f]+", sen[cur:])
		if s:
			if s.group() != '':
				revlist.append(s.group())
			cur = cur + len(s.group()) 
			post = cur + span
			if post > len(sen):
				post = len(sen)
		s = re.search(u"^[a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|\uff41|\uff42|\uff43|\uff44|\uff45|\uff46|\uff47|\uff48|\uff49|\uff47|\uff4b|\uff4c|\uff4d|\uff4e|\uff4f|\uff50|\uff51|\uff52|\uff53|\uff54|\uff55|\uff56|\uff57|\uff58|\uff59|\uff5a|\uff21|\uff22|\uff23|\uff24|\uff25|\uff26|\uff27|\uff28|\uff29|\uff2a|\uff2b|\uff2c|\uff2d|\uff2e|\uff2f|\uff30|\uff31|\uff32|\uff33|\uff35|\uff36|\uff37|\uff38|\uff39|\uff3a]+", sen[cur:])
		if s:
			if s.group() != '':
				revlist.append(s.group())
			cur = cur + len(s.group()) 
			post = cur + span
			if post > len(sen):
				post = len(sen)
		if (WordDic.has_key(sen[cur:post])) or (cur + 1 == post):
			if sen[cur:post] != '':
				revlist.append(sen[cur:post])
			cur = post
			post = post + span
			if post > len(sen):
				post = len(sen)
		else:
			post -= 1	
	return revlist 

def PostSenSeg(sen, span):
	cur = len(sen)
	pre = cur -  span 
	if pre < 0:
		pre = 0
	revlist = []
	while 1:
		if cur <= 0:
			break
		s = re.search(u"[0|1|2|3|4|5|6|7|8|9|\uff11|\uff12|\uff13|\uff14|\uff15|\uff16|\uff17|\uff18|\uff19|\uff10|\u4e00|\u4e8c|\u4e09|\u56db|\u4e94|\u516d|\u4e03|\u516b|\u4e5d|\u96f6|\u5341|\u767e|\u5343|\u4e07|\u4ebf|\u5146|\uff2f]+$", sen[pre:cur])
		if s:
			if s.group() != '':
				revlist.append(s.group())
			cur = cur - len(s.group()) 
			pre = cur - span
			if pre < 0:
				pre = 0
		s = re.search(u"^[a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|\uff41|\uff42|\uff43|\uff44|\uff45|\uff46|\uff47|\uff48|\uff49|\uff47|\uff4b|\uff4c|\uff4d|\uff4e|\uff4f|\uff50|\uff51|\uff52|\uff53|\uff54|\uff55|\uff56|\uff57|\uff58|\uff59|\uff5a|\uff21|\uff22|\uff23|\uff24|\uff25|\uff26|\uff27|\uff28|\uff29|\uff2a|\uff2b|\uff2c|\uff2d|\uff2e|\uff2f|\uff30|\uff31|\uff32|\uff33|\uff35|\uff36|\uff37|\uff38|\uff39|\uff3a]+", sen[pre:cur])
		if s:
			if s.group() != '':
				revlist.append(s.group())
			cur = cur - len(s.group()) 
			pre = cur - span
			if pre < 0:
				pre = 0

		if (WordDic.has_key(sen[pre:cur])) or (cur - 1 == pre):
			if sen[pre:cur] != '':
				revlist.append(sen[pre:cur])
			cur = pre
			pre = pre - span
			if pre < 0:
				pre = 0
		else:
			pre += 1	
	return revlist[::-1] 

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print("Usage: python wordseg.py Dicfile Inputfile Outfile")
	Dicfile = sys.argv[1]
	StatisticDicfile = sys.argv[2]
	Inputfile = sys.argv[3]
	Outputfile = sys.argv[4]
	InitDic(Dicfile)
	InitStatisticDic(StatisticDicfile)

#print "Dic:", StatisticDic
	InitStopword()
	WordSeg(Inputfile, Outputfile)
