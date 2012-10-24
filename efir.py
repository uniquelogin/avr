#!/usr/bin/env python
# coding:utf-8
import sys
import os
sys.path.append(os.path.expanduser('~/bin'))

import urllib2
import avrlib
import random
import time
import re
import textwrap

query_re = re.compile(r'<item.+?>(.+?)</item>')

avr = avrlib.TAvrDisplay()

xtable_src = """
а 61
б b2
в b3
г b4
д 67
е 65
ё b5
ж b6
з b7 
и b8
й b9
к ba
л bb
м bc
н bd
о 6f
п be
р 70
с 63
т bf
у 79
ф e4
х 78
ц e5
ч c0
ш c1
щ e6
ъ c2 
ы c3
ь c4
э c5
ю c6
я c7
А 41
Б a0
В 42
Г a1
Д e0
Е 45
Ж a3
З a4
И a5
К 4b
Л a7
М 4d
Н 48
О 4f
П a8
Р 50
С 43
Т 54
У a9
Ф aa
Х 58
Ц e1
Ч ab
Ш ac
Щ e2
Ъ ad
Ы ae
Ь 62
Э af
Ю b0
Я b1
• 84
і 69
– 2d 
"""


xtable = {}
for line in xtable_src.split('\n'):
    line = line.strip()
    if not line:
        continue
    key, value = line.split()
    xtable[key.decode('utf-8')] = int(value, 16)

curr_lines = []

def print_query(query):
    global curr_lines
    query = (u'•' + query.decode('utf-8'))
    curr_lines = (curr_lines + textwrap.wrap(query, 20))[-4:]
    q = u'\n'.join(curr_lines)
    msg = ''
    for c in q:
        if c in xtable:
            msg += chr(xtable[c])
        elif ord(c) <= 0x7a:
            msg += chr(ord(c))
        else:
            msg += '\x93'
    if msg:
        avr.set_message(msg)

while True:
    req = urllib2.urlopen('http://export.yandex.ru/last/last20x-static.xml?ncrnd=123')
    body = req.read().split('\n')
    req.close()
    lines = []
    for line in body:
        line = line.strip()
        if not line:
            continue
        match = query_re.match(line)
        if match:
            qtext = match.group(1)
            lines.append(qtext)
    for query in random.sample(lines, 30):
        print_query(query)
        print query
        time.sleep(1)
