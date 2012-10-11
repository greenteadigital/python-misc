#!/usr/bin/env python

# ipban2.py - scan linux server logs & ban ip addresses making malicious or
#			  abusive requests

# Periodically run this script to scan webserver (nginx) logs for abusive
# requests or vulnerability probes. Bans ip addresses based on predetermined
# signatures (see flags[] below), or manually by entering an offending ip
# address as an argument on launch.

# Built & used with the nginx webserver on Fedora 14 Linux. Requires: root,
# iptables, nginx-style log format. Can be easily adapted to other Linux
# distros or log formats.

import os, sys

usage = """Usage:

-f      list all current flags; i.e. ban-worthy strings

-ip     ban the ipaddress specified by the first argument, appending
        a comment string (required) given as the second argument.
		Example: "ipban2.py -ip 255.255.255.255 Morfeus"
		
-L      ban all ip addresses whos requests contain a string from the flags list
"""

valid_args = ['-f','-ip','-L']

#debug
# print '\nargc:', len(sys.argv)
# for n in range(len(sys.argv)):
	# print 'arg%s: %s'%(n, sys.argv[n])
# print #whitespace

# UA or any other string found in offending log entries; use wisely.
# If a log entry contains any of these flags, ALL traffic from the source ip address will be dropped!
flags = [
'Baiduspider',
'baidu.com',
'w00tw00t',
'Y-ivrrecording.php',
'phpmyadmin',
'phpldapadmin',
'ZmEu',
'whitehat.ro',
'any-request-allowed.com',
'allrequestsallowed.com',
'Morfeus',
'soapCaller.bs',
'muieblackcat'
]

def banList():
	global flags
	print '\nSaving iptable rules in RAM to disk...'
	os.system('service iptables save')
	curr_rules = open('/etc/sysconfig/iptables','r').read()
	target_log = '/var/log/nginx/access.log' 
	print 'scanning log file: '+target_log
	logfile = open(target_log,'r').readlines()
	bad_reqs = {}    #dict will contain mappings of ip addr. to flag string; see flags[]

	for flagstr in range(len(flags)):
		print 'searching flag \'%s\''%flags[flagstr]
		for logline in range(len(logfile)):
			if logfile[logline].find(flags[flagstr])>-1:
				addr = logfile[logline].split(' ')[0]   #the offending ip address
				if bad_reqs.keys().count(addr) == 0:
					if curr_rules.find(addr) == -1:
						bad_reqs[addr] = flags[flagstr]  #insert the ip with its flag in the bad_reqs dict
						print '  found new bad IP: '+addr
					if curr_rules.find(addr) > -1:
						print '  line %s: <%s> exists in filter table, skipping...'%(logline+1,addr)
	#print bad_reqs    #dbg
	keys = bad_reqs.iterkeys()
	for n in range(len(bad_reqs)):
		ip = keys.next()
		#insert ip address followed by its respective flag string into iptables system command
		#pulled as a key:value pair from bad_reqs{}
		os.system('iptables -I INPUT -s %s -m comment --comment "%s" -j DROP'%(ip,bad_reqs[ip]))
		print '  added '+ip+' to filter table with comment \"'+bad_reqs[ip]+'\"'
	if len(bad_reqs) > 0:
		os.system('service iptables save')
		os.system('service iptables restart')
	print 'ipban2.py complete...\n'

if len(sys.argv) == 1:
	print usage
if len(sys.argv) == 2:
	if sys.argv[1] == '-f':
		print "\nCurrent ban-worthy flags:"
		print "---------------------------"
		for n in range(len(flags)):
			print flags[n]
		print	#whitespace
	elif sys.argv[1] == '-L':
		banList()
	else:
		print 'command line argument \'%s\' is not a valid argument\n'%sys.argv[1]
		print usage
if len(sys.argv) == 3:
	print '\nError: missing or invalid argument. Try \'-ip\'?'
	print usage
if len(sys.argv) == 4 and sys.argv[1] == '-ip':
	parts = sys.argv[2].split('.')
	#verify input as ipv4 address; no support for ipv6
	if (0 <= int(parts[0]) <= 255 and
	0 <= int(parts[1]) <= 255 and
	0 <= int(parts[2]) <= 255 and
	0 <= int(parts[3]) <= 255):
		resp = raw_input("Banning IP address: %s \nWith comment: \"%s\" \n(Y)es or (N)o? "%(sys.argv[2], sys.argv[3]))
		if resp == 'y' or resp == 'Y':
			os.system('iptables -I INPUT -s %s -m comment --comment "%s" -j DROP'%(sys.argv[2], sys.argv[3]))
			os.system('service iptables save')
			print '  added '+sys.argv[2]+' to filter table with comment \"'+sys.argv[3]+'\"'
		else:
			print '\nNo action taken.'
			print usage
	else:
		print '\nInvalid ip address:', sys.argv[2]
		print usage
if len(sys.argv) > 4:
	print '\nToo many arguments.'
	print usage
