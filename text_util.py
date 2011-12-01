#!/usr/bin/env python
# encoding: utf-8
"""
text_util.py

Created by Delai on 2011-11-10.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import re

INDEX_URL = ''


def at_link(at_name):
    if at_name.group(0)[-1] == ' ':
        name = at_name.group(0)[:-1]
    else:
        name = at_name.group(0)
    return "<a href=\"%s/%s\">%s</a>&nbsp" % (INDEX_URL, name[1:], name)
    

def html_process(text):
    str = re.sub('(@[^ \.]+ )|(@[^ \.]+$)', at_link , text)   # match not space
    return str

if __name__ == '__main__':
    #print html_process('@施德来 不是人，shidelai@gmail.com @bobo 哈哈 @jialiang @shidelai')
    test_str = '@施德来 不是人，shidelai@gmail.com @bobo 哈哈 @jialiang @shidelai'
    assert_str = '<a href="/施德来">@施德来</a>&nbsp不是人，shidelai@gmail.com <a href="/bobo">@bobo</a>&nbsp哈哈 <a href="/jialiang">@jialiang</a>&nbsp<a href="/shidelai">@shidelai</a>&nbsp'
    assert html_process(test_str) == assert_str, 'run html_process(%s) \n -> %s \n not %s' % (test_str, html_process(test_str), assert_str)
    print 'test success'
