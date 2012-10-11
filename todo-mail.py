#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo-mail.py - Send a quick to-do email to your desktop while you're away from your desk

# Runs as a server-side web app and sends an email reminder containing the user 
# supplied subject and message contained in the requested URL. I built this app 
# for times when I was away from my desk and needed a to-do reminder to hit my 
# inbox. Much more streamlined than using a full email client like Gmail. This is the 
# server-side script. The connecting client could be another python script, or a 
# javascript enabled html file, among others.

# Use a variation of the following url to test this mailer script:
# https://www.greenteadigital.com/todo.py?app=taskmail&subject=SUB&message=MSG&key=77ff0f94b78ff26fb4070951651643c8a90da8399acb2d6b641e020d8b1359223b6da313f9897ea2861674e4ee35c8b2aa36143f9f3ffd3c3adcd119ea8832a6

# When testing or calling this script from a browser like firefox, url
# encoding/normalization (i.e. %20 for space, etc.) will be handled by the
# browser. If using a python app to make a request to the server, use something
# like the following:
# normed_url = urllib.quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]")
# urllib.open(normed_url)

from gevent.wsgi import WSGIServer
import subprocess, urllib

def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
    query_params = environ['QUERY_STRING'].split('&')
    #print 'query_params =', query_params
    queries_dict = {}
    if len(query_params[0]) > 0:
        for n in range(len(query_params)):
            subquery = query_params[n].split('=')
            queries_dict[subquery[0]] = subquery[1]
    #print 'queries_dict =', queries_dict
    keyA = '77ff0f94b78ff26fb4070951651643c8a90da8399acb2d6b641e020d8b135922'
    keyB = '3b6da313f9897ea2861674e4ee35c8b2aa36143f9f3ffd3c3adcd119ea8832a6'
    if ('subject' in queries_dict and
    'message' in queries_dict and
    'app' in queries_dict and
    'key' in queries_dict and
    queries_dict['app'] == 'taskmail' and
    queries_dict['key'] ==  keyA + keyB and
    environ['HTTP_X_FORWARDED_PROTOCOL'] == 'https' and
    environ['PATH_INFO'] == '/todo.py'):
        sub = urllib.unquote(queries_dict['subject']) # remove %20 for spaces, etc.
        msg = urllib.unquote(queries_dict['message'])
        command = ['/bin/mail', '-s', '%s'%sub, '-r','ben@greenteadigital.com','bhall@stjohnscathedral.org']
        mailer = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        returned = mailer.communicate(msg + '\n.\n')
        #print 'returned =', returned
        return 'SUCCESS!'
    else:
        resp = ''
        keys = environ.iterkeys()
        for n in range(len(environ)):
            i = keys.next()
            resp = resp + str(i) + ': ' + str(environ[i]) + '\n'
        return [resp]

address = "127.0.0.1",8080
server = WSGIServer(address, application)
server.backlog = 256
server.serve_forever()
