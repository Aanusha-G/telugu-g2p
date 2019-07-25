#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
run_g2p.py
~~~~~~~~~~

This script converts Telugu graphemes to romanised phonemes (xipa) and then to their pronunciation (IPA
and XSAMPA).

Functions
    (1) g2p: convert Telugu graphemes to xipa phonemes
    (2) syllabify : Syllabifies generated xipa
    (3) xipa2other: Converts xipa phonemes to IPA/XSAMPA transcription
    (4) run_tests: Runs tests from test_telugu file

Aanusha Ghosh (aanusha.ghosh@gmail.com)

Created: 2019-07-25
Last updated: 2019-07-25 Aanusha Ghosh


'''
import os
import regex
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--interactive', action="store_true", help="read tokens from standard input")
parser.add_argument("-f", "--file", dest = 'filepath', help="path to file containing tokens in Bengali")
parser.add_argument("-t", "--run-tests", dest = 'tests', action = "store_true", help="Specify whether tests should be run. This is set to true by default if input file is not specified.")
parser.add_argument("--ipa", action="store_true", help="return IPA transcriptions" )
parser.add_argument("--xsampa", action="store_true", help="return XSAMPA transcriptions. If neither --ipa nor --xsampa flags are specified, xipa transcriptions are returned by default")
args = parser.parse_args()


def g2p(word):
	character_mappings = os.path.join(os.getcwd(), 'character_mappings')
	with open(character_mappings) as f:
		data = f.readlines()
	del_list = ['aal', 'il', 'el', 'ae', 'ao', 'oil', 'owl', 'oul', 'ul', 'XX']
	mappings = {}
	for line in data:
		character = line.split(' -> ')[0]
		xipa = line.split(' -> ')[1].strip()
		mappings[character] = xipa

	map_xipa = []
	for i in word:
		map_xipa.append(mappings[i.encode('utf-8')].strip('|').split('|'))
	phoneme_seq = [item for sublist in map_xipa for item in sublist]
	phoneme_string = '|'.join(phoneme_seq)+'|'

	replacements = [
		# Insert schwa-deletion or phonotactic rules here
		(r'AX\|00\|', r''),
		(r'AX\|L\|', r''),
		(r'AX\|', r'a|')
	]
	# print "phoneme_string before schwa_deletion", phoneme_string

	for old, new in replacements: 
		phoneme_string = regex.sub(old, new, phoneme_string)
	# print "phoneme_string after schwa_deletion" , phoneme_string
	return syllabify(phoneme_string)


def syllabify(word):
	vowels = [ 'a', 'aa', 'i', 'ii', 'u', 'uu', 'e', 'ee', 'o', 'oo', 'ai', 'au']
	ph = word.strip('|').split('|')
	syl = []
	v_flag = 0
	c_flag = 0
	l = len(ph) - 1
	for index, i in enumerate(reversed(ph)):
		syl.append(i+'|')
		if i in vowels:
			v_flag = 1
		else:
			if v_flag == 1:
				c_flag = 1
		if v_flag == 1 and c_flag == 1 and index != l:
			v_flag = c_flag = 0
			syl.append('-')
	
	syl_word = ''.join(list(reversed(syl)))
	# If first syllable has no vowel, remove first syllable marker
	first_syll = syl_word.split('-')[0]
	#print first_syll
	if regex.search(r'(a|aa|i|ii|u|uu|e|ee|o|oo|ai|au)', first_syll) == None:
		syl_word = regex.sub(r'-', r'', syl_word, 1)

	return syl_word

def map2others(word, mappings):
	path_to_mappings = os.path.join(os.getcwd(), mappings)
	with open(path_to_mappings, 'r') as f:
		map_lines = f.readlines()
	mappings_dict = {}
	for line in map_lines:
		xipa = line.split(' -> ')[0]
		mapto = line.split(' -> ')[1].strip()
		mappings_dict[xipa] = mapto
	word = word.strip('|').split('|')
	mapped_word = []
	for index,i in enumerate(word):
		if i in mappings_dict:
			mapped_word.append(mappings_dict[i])
		elif i.lstrip('-') in mappings_dict:
			mapped_word.append('.')
			mapped_word.append(mappings_dict[i.lstrip('-')])
		else:
			mapped_word.append(' ')	
	return ''.join(mapped_word)

def run_tests():
	test_telugu = os.path.join(os.getcwd(), "test_telugu")
	with open(test_telugu) as f:
		testdata = f.readlines()
	test_pairs = {}
	for line in testdata:
		word = line.split(' ')[0]
		pron = line.split(' ')[1].strip()
		test_pairs[word] = pron
	tot_tests = len(test_pairs)
	c = 0
	for i in test_pairs.keys():
		g2p_output = g2p(unicode(i,'utf-8'))
		print "Expected: ", test_pairs[i], "\nG2P: ", g2p_output
		if test_pairs[i] == g2p_output:
			#print "pass!"
			c+=1
		else:
			print "Expected: ", test_pairs[i], "\nG2P: ", g2p_output
			print "Test failed"
			print '________________'
	print c, " out of ", tot_tests, " passed "
	
def run_file(filepath):
	with open(filepath, 'r') as f:
		tokens_list = f.readlines()
	prons_dict = {}
	for token in tokens_list:
		token = token.strip()
		g2p_output = g2p(unicode(token,'utf-8'))
		prons_dict[token] = g2p_output
	for i in prons_dict: 
		print i, 't', prons_dict[i], '\n'

def run_interactive(ipa, xsampa):
	import sys
	while True:
		try:
			token = raw_input('Token: ')
			if token == "stop":
				break
			g2p_output = g2p(unicode(token.strip(),'utf-8'))
			print "phoneme: ", g2p_output
			if ipa:
				mapped_output = map2others(g2p_output, 'ipa_mappings')
				print "IPA: ", mapped_output
			if xsampa:
				mapped_output = map2others(g2p_output, 'xsampa_mappings')
				print "XSAMPA: ", mapped_output
		except KeyboardInterrupt:
			sys.exit()			

if args.tests or (not args.filepath and not args.interactive):
	run_tests()
if args.filepath:
	run_file(filepath, args.ipa, args.xsampa)
elif args.interactive: 
	run_interactive(args.ipa, args.xsampa)
