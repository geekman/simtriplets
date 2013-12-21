#!/usr/bin/env python

from distutils.core import setup

setup(name='simtriplets',
	version='1.0',
	description='FreeRADIUS module to import simtriplets',
	author='Darell Tan',
	author_email='darell.tan@gmail.com',
	url='https://bitbucket.org/geekman/simtriplets',

	py_modules=['simtriplets'],

	include_package_data=True,
	package_data={'': ['LICENSE', 'README', 'simtriplets_module']}
	)

