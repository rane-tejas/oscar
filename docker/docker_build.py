#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import getpass
import json


if __name__=="__main__":
	with open('docker.json', 'r') as f:
		cfgs = json.load(f)

	print("Building docker container . . . ")
	user_name = getpass.getuser()

	default_image_name = cfgs['image_name']
	isaacgym_path = cfgs['isaacgym_path']

	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--image", type=str,
		help="name for the newly created docker image", default=default_image_name)

	parser.add_argument("-d", "--dry_run", action='store_true', help="(optional) perform a dry_run, print the command that would have been executed but don't execute it.")

	parser.add_argument("-p", "--password", type=str,
						help="(optional) password for the user", default="password")

	parser.add_argument('-uid','--user_id', type=int, help="(optional) user id for this user", default=os.getuid())
	parser.add_argument('-gid','--group_id', type=int, help="(optional) user gid for this user", default=os.getgid())

	args = parser.parse_args()
	print("Docker image name:", args.image)
	
	cmd_get_isaacgym = f'cp -r {isaacgym_path} isaacgym'
	if not args.dry_run:
		os.system(cmd_get_isaacgym)

	print("command = \n \n", cmd_get_isaacgym)
	print("")

	build_args = {
		'user_name': user_name, 
		'password': args.password, 
		'user_id': args.user_id, 
		'group_id': args.group_id, 
		}
	
	cmd = "docker build --build-arg USER_NAME=%(user_name)s \
			--build-arg USER_PASSWORD=%(password)s \
			--build-arg USER_ID=%(user_id)s \
			--build-arg USER_GID=%(group_id)s" \
			%build_args
	cmd += " -t %s -f %s ." % (args.image, cfgs['dockerfile'])
	
	print("command = \n \n", cmd)
	print("")

	# build the docker image
	if not args.dry_run:
		print("executing shell command")
		os.system(cmd)

	cmd_rm_isaacgym = f'rm -rf isaacgym'
	print("command = \n \n", cmd_get_isaacgym)
	print("")

	if not args.dry_run:
		os.system(cmd_rm_isaacgym)
	else:
		print("dry run, not executing command")
