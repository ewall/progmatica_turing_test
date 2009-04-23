#!/usr/bin/env python
#
# Turing Test client for Progmatica entry
# by ewall <e@ewall.org> April 2009
#
# Requires:
# - TuringTester.py webserver is running on a local port
#
# Very Important Legal Disclaimer:
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, LOSS OF USE, DATA, OR
# SANITY; HEADACHE, NAUSEA, DRY MOUTH, URINARY RETENTION, BLURRED VISION,
# CONSTIPATION, SEDATION, SLEEP DISRUPTION, WEIGHT GAIN, AND/OR FECAL URGENCY).
#
# What to do:
# Run it (optionally specifying a port number on the command line),
# then read it and weep.
#
__author__ = "Eric W. Wallace <e@ewall.org>"
__version__ = "$Revision: 0.9 $"
__date__ = "$Date: 2009/04/23 $"
__copyright__ = "Copyright (c) 2009 Eric W. Wallace"
__license__ = "Creative Commons Attribution-ShareAlike (http://creativecommons.org/licenses/by-sa/3.0/)"

import sys, urllib, urllib2
from sgmllib import SGMLParser

class PageParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.in_h3 = 0
        self.results = {}

    def start_form(self, attrs):
        action = [v for k, v in attrs if k=='action']
        if action:
            self.results['form_action'] = action[0]

    def start_h3(self, attrs):
        self.in_h3 += 1

    def end_h3(self):
        self.in_h3 -= 1

    def handle_data(self, text):
        if self.in_h3 > 0: self.results['h3'] = text
        
if __name__ == "__main__":

    # The port number can be specified on the command line, default is 8080
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = 8080

    print "Connecting to the TuringTester.py server at http://localhost:%d/" % port

    try:
        req = urllib2.Request('http://localhost:%d/' % port)
        response = urllib2.urlopen(req)
    except IOError, e:
        if hasattr(e, 'reason'):
            print "ERROR: Failed to reach a server."
            print "Error reason: ", e.reason
        elif hasattr(e, 'code'):
            print "ERROR: The server couldn't fulfill the request."
            print "Error code: ", e.code
    else:
        print "Connection successful.\nPreparing form submission..."

        #parse out URL from form action element on page
        parser = PageParser()
        parser.feed(response.read())
        response.close()
        parser.close()
        form_action = parser.results['form_action']

        #prep and submit form
        form_url = 'http://localhost:%d%s' % (port, form_action)
        urllib.quote_plus = urllib.quote #hack: urlencode uses quote_plus(), but we want %20 for space, not plus signs
        data = urllib.urlencode({ 'name' : 'R. Daneel Olivaw',
                                  'computer' : 'yes',
                                  'sex' : 'binary',
                                  'word' : 'gobbletygook' })
        form_url += '?' + data #hack: must be submitted as a GET request, not POST
        req = urllib2.Request(form_url)
        try:
            response = urllib2.urlopen(req)
        except IOError, e:
            if hasattr(e, 'reason'):
                print "ERROR: Failed to reach a server."
                print "Error reason: ", e.reason
            elif hasattr(e, 'code'):
                print "ERROR: The server couldn't fulfill the request."
                print "Error code: ", e.code
        else:
            print "Submission successful."

            #parse out results & report
            parser.reset()
            parser.feed(response.read())
            response.close()
            parser.close()
            print "*** " + parser.results['h3'] + " ***"
