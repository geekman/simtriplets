#!/usr/bin/env python

"""
FreeRADIUS module to handle authorization using simtriplets
Copyright (C) 2013 Darell Tan

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""


import radiusd
import random
from pprint import pformat


SIMTRIPLETS = '/etc/raddb/simtriplets'


simtriplets = {}
tuple_labels = ('EAP-Sim-Rand', 'EAP-Sim-SRES', 'EAP-Sim-KC')


def log(level, msg):
	radiusd.radlog(level, '[simtriplets.py] ' + msg)


def instantiate(p):
	log(radiusd.L_INFO, 'instantiated simtriplets.py')

	f = open(SIMTRIPLETS, 'rb')
	for line in f:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		imsi, rand, sres, kc = line.split(',')
		record = ('0x' + rand, '0x' + sres, '0x' + kc)
		if imsi in simtriplets:
			simtriplets[imsi].append(record)
		else:
			simtriplets[imsi] = [record]

	# dump database
	for imsi in simtriplets:
		log(radiusd.L_DBG, 'imsi %s: %d triplets' % (imsi, len(simtriplets[imsi])))

	log(radiusd.L_INFO, 'loaded %d IMSIs' % len(simtriplets.keys()))

	return 0


def authorize(data):
	username = None
	for k, v in data:
		if k == 'User-Name':
			username = v
			if username[0] == '"' and username[-1] == '"':
				username = username[1:-1]

			username = username.split('@')[0]

			# identity: 1=SIM, 0=AKA, 6=AKA_PRIME
			if username[0] == '1':
				username = username[1:]

	if username is None or username not in simtriplets:
		return radiusd.RLM_MODULE_NOTFOUND

	user_triplets = simtriplets[username]
	log(radiusd.L_DBG, 'found user %s with %d triplets' % (username, len(user_triplets)))

	triplets = random.sample(user_triplets, 3)
	log(radiusd.L_DBG, 'selected RAND values: ' + ', '.join(t[0] for t in triplets))
	reply = []
	for i in xrange(3):
		reply.extend( zip([k + str(i + 1) for k in tuple_labels], triplets[i]) )

	return (radiusd.RLM_MODULE_UPDATED, 
			tuple(reply),	# reply tuple
			tuple())		# config tuple


