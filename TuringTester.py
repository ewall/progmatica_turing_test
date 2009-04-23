#!/usr/bin/env python
#
# Turing Test webserver for Progmatica entry
# by ewall <e@ewall.org> April 2009
#
# Requires:
# - PyCATCHA module (svn from http://svn.navi.cx/misc/trunk/pycaptcha/)
# - PIL module (install from http://www.pythonware.com/products/pil/)
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
# then point your web browser at the given URL.
#
__author__ = "Eric W. Wallace <e@ewall.org>"
__version__ = "$Revision: 0.9 $"
__date__ = "$Date: 2009/04/23 $"
__copyright__ = "Copyright (c) 2009 Eric W. Wallace"
__license__ = "Creative Commons Attribution-ShareAlike (http://creativecommons.org/licenses/by-sa/3.0/)"

from Captcha.Visual import Tests
from Captcha import Factory
import BaseHTTPServer, urlparse, sys, cStringIO, webbrowser
from urllib import unquote_plus

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        scheme, host, path, parameters, query, fragment = urlparse.urlparse(self.path)

        # Split the path into segments
        pathSegments = path.split('/')[1:]

        # Split the query into key-value pairs
        self.args = {}
        for pair in query.split("&"):
            if pair.find("=") >= 0:
                key, value = pair.split("=", 1)
                value=unquote_plus(value)
                self.args.setdefault(key, []).append(value)
            else:
                self.args[pair] = []

        if pathSegments[0] == "":
            #first CAPTCHA test is "PseudoGimpy"
            self.handleRootPage(self.args.get('test', Tests.__all__)[0])

        elif pathSegments[0] == "style.css":
            self.handleCSS()

        elif pathSegments[0] == "images":
            self.handleImagePage(pathSegments[1])

        elif pathSegments[0] == "solutions":
            self.handleSolutionPage(pathSegments[1], self.args['word'][0])

        else:
            self.handle404()

    def handle404(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("<html><body><h1>No such resource</h1></body></html>")

    def handleRootPage(self, testName):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        test = self.captchaFactory.new(getattr(Tests, testName))
 
        self.wfile.write("""<html>
<head>
<title>Tricky Turing Test</title>
<link href="/style.css" rel="stylesheet" type="text/css" />
</head>
<body>
<h1>Tricky Turing Test</h1>

<p>Please fill in the information request below as we attempt to determine
if you are a computer or a human being.</p>

<div id="box">

<img src="http://www.adeptis.ru/vinci/alan_turing2.jpg" width=220 height=275>

<form action="/solutions/%s" method="get">

<ul>

<li>
Name?:
<input type="text" name="name" />
</li>

<li>
Are you not a computer?: 
<input type="radio" name="computer" value="yes" /> Yes |
<input type="radio" name="computer" value="no" /> No
</li>

<li>
Sex?:
<input type="radio" name="sex" value="male" /> Male |
<input type="radio" name="sex" value="female" /> Female |
<input type="radio" name="sex" value="binary" /> Binary |
<input type="radio" name="sex" value="no" /> No |
<input type="radio" name="sex" value="yes" /> Yes<br />
</li>

<li>
Look at the following
<a href="http://en.wikipedia.org/wiki/Captcha" target="_blank">CAPTCHA</a> image:<br />
&nbsp;&nbsp;&nbsp;&nbsp;<img src="/images/%s" /><br />
Enter CAPTCHA here: <input type="text" name="word" /><br />
</li>

</ul>

<input type="submit" value="Submit My Answers For Verification"/>

</form>

</div>

</body>
</html>
""" % (test.id, test.id))

    def handleCSS(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/css")
        self.end_headers()
        self.wfile.write("""body {
	border: 0;
	margin: 0;
	padding: 0;
}

h1 {
	margin: 10px 0 0 0;
	padding: 0;
	display: block;
	width: 100%;
	background-color: #508fc4;
	border-top: 5px solid #1958b7;
	border-bottom: 5px solid #1958b7;
	text-align: center
}

h1 + p {
	padding: 0 0 0 1em;
	font-style: italic;
}

div#box {
	display: table;
	margin: 0 auto;
	background-color: #508fc4;
	border: 5px solid #1958b7;
    margin-left: auto;
    margin-right: auto;
	padding: 1em;
	width: 90%;
	min-width: 700px;
	max-width: 1100px;
}

div#box>img {
	display: block;
	float: right;
	width: 224px;
	margin: 0 4px 0 0;
	padding: 4px;
	border: 3px solid #2175bc;
	border-bottom-color: #1958b7;
	border-right-color: #1958b7;
	background-color: white;
}

div#box ul {
	display: block;
	float: left;
	width: 65%;
	list-style: none;
	margin: 0 auto;
	padding: 0;
	border: none;
}

div#box ul li {
	display: block;
	text-indent: none;
	padding: 1em;
	background-color: #2175bc;
	color: white;
	text-decoration: none;
}

div#box input[type=submit], div#box p, div#box h3  {
	float: left;
	clear: both;
    margin: 1em 0 0 0;
    padding: 4px;
    font-weight: bold;
}
""")

    def handleImagePage(self, id):
        test = self.captchaFactory.get(id)
        if not test:
            return self.handle404()

        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.end_headers()
        #test.render().save(self.wfile, "JPEG") #this fails on Win32
        altoutput = cStringIO.StringIO()
        test.render().save(altoutput, "JPEG")
        self.wfile.write(altoutput.getvalue())
        altoutput.close()

    def handleSolutionPage(self, id, word):
        test = self.captchaFactory.get(id)
        if not test:
            return self.handle404()

        strName = self.args['name'][0]
        if strName=="": strName = "John Doe"

        computer = self.args.get('computer',['no'])[0]
        strComputer = "You said, " + computer + ", you are "
        if computer=="no": strComputer += "not "
        strComputer += "not a computer (which I think means you really are "
        if computer=="yes": strComputer += "not "
        strComputer += "one)."

        sex = self.args.get('sex',['no'])[0]
        strSex = (
            ( (sex=="yes") and "You said 'yes' to sex... that sounds very human (and probably male, too)." ) or
            ( (sex=="no") and "You said 'no' to sex? What kind of robot are you?" ) or
            ( (sex=="binary") and "You said your sex is 'binary'... um, I don't want to know anymore!" ) or
            "You said you are " + sex )

        strAnswer = self.args['word'][0]
        if strAnswer=="CAPTCHA":
            strCaptcha = "correct"
            strResult = "You ARE a computer. (Cheater!)"
        else:
            strCaptcha = "wrong"
            strResult = "You are NOT a computer. (Phew!)"

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write( """<html>
<head>
<title>Tricky Turing Test &mdash; Results</title>
<link href="/style.css" rel="stylesheet" type="text/css" />
</head>
<body>
<h1>Tricky Turing Test &mdash; Results</h1>

<p>Hi, %s (if that's your real name). Below are the results for your submissions to our Turing Test.</p>

<div id="box">

<img src="http://www.adeptis.ru/vinci/alan_turing4.jpg" width=220 height=275>

<ul>

<li>Your name is %s. (And just what ethnicity would you say that is?)</li>

<li>%s</li>

<li>%s</li>

<li>Your answer for the CAPTCHA image ("%s") was %s.<br />
&nbsp;&nbsp;&nbsp;&nbsp;<img src="/images/%s"/></li>

</ul>

<h3>Conclusion: %s</h3>

<p><a href="/">Try again?</a></p>

</div>

</body>
</html>
""" % (strName, strName, strComputer, strSex, strAnswer, strCaptcha, test.id, strResult) )

### main ###

def main(port):
    print "\nStarting Turing Tester server at http://localhost:%d/" % port
    print "(CTRL-C and page refresh to close the server cleanly)\n"

    #theoretically this could be a race condition, but the browser is almost certain to be slower than this service
    print "Opening your web browser...\n"
    try:
        webbrowser.open_new("http://localhost:%d/" % port)
    except:
        pass

    handler = RequestHandler
    handler.captchaFactory = Factory()
    BaseHTTPServer.HTTPServer(('', port), RequestHandler).serve_forever()

if __name__ == "__main__":

    # The port number can be specified on the command line, default is 8080
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = 8080
    main(port)
