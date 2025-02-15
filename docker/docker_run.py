#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import getpass
import json


if __name__=="__main__":
	with open('docker.json', 'r') as f:
		cfgs = json.load(f)

	user_name = getpass.getuser()

	default_image_name = cfgs['image_name'] + ":latest"

	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--image", type=str,
		help="(required) name of the image that this container is derived from", default=default_image_name)

	parser.add_argument("-c", "--container", type=str, default=cfgs['container_name'], help="(optional) name of the container")\

	parser.add_argument("-d", "--dry_run", action='store_true', help="(optional) perform a dry_run, print the command that would have been executed but don't execute it.")

	parser.add_argument("-e", "--entrypoint", type=str, default="", help="(optional) thing to run in container")

	parser.add_argument("-p", "--passthrough", type=str, default="", help="(optional) extra string that will be tacked onto the docker run command, allows you to pass extra options. Make sure to put this in quotes and leave a space before the first character")

	args = parser.parse_args()
	print("running docker container derived from image %s" %args.image)
	source_dir = os.path.join(os.getcwd(),"../")
	source_dir_name = os.path.dirname(os.path.abspath(os.getcwd())).split('/')[-1]
	config_file = os.path.join(source_dir, 'config', 'docker_run_config.yaml')

	image_name = args.image
	home_directory = '/home/' + user_name
	dense_correspondence_source_dir = os.path.join(home_directory, 'code')

	cmd = ""
	cmd += "xhost +local:root \n"
	cmd += "docker run --gpus all --shm-size 32g --dns 8.8.8.8"
	
	container_name = args.container
	i = 0
	info = os.popen("docker ps").read()
	while (container_name + '_{}'.format(i)) in info:	i += 1
	container_name += '_{}'.format(i)

	# if args.container:
	cmd += " --name %(container_name)s " % {'container_name': container_name}
	# cmd += "-e NVIDIA_DRIVER_CAPABILITIES=compute,utility "
	
	try:
		disp = os.environ['DISPLAY']
		cmd += '-e DISPLAY={}'.format(disp)
	except KeyError:
		print('Display not found! Running in headless mode.')

	# cmd += " -e DISPLAY -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw "     # enable graphics 
	cmd += " -v %(source_dir)s:%(home_directory)s/%(source_dir_name)s "  \
		% {'source_dir': source_dir, 'home_directory': home_directory, 'source_dir_name': source_dir_name}              # mount source
	# cmd += " -v ~/.ssh:%(home_directory)s/.ssh " % {'home_directory': home_directory}   # mount ssh keys
	# cmd += " -v /media:/media " #mount media
	# cmd += " -v ~/.torch:%(home_directory)s/.torch " % {'home_directory': home_directory}  # mount torch folder 
														# where pytorch standard models (i.e. resnet34) are stored

	# cmd += '-v /home/rex/projects/comms'
	# cmd += " --user %s " % user_name                                                    # login as current user

	# uncomment below to mount your data volume
	# config_yaml = yaml.load(file(config_file))
	# host_name = socket.gethostname()
	# cmd += " -v %s:%s/data_volume " %(config_yaml[host_name][user_name]['path_to_data_directory'], dense_correspondence_source_dir)

	# expose UDP ports
	# cmd += " -p 8888:8888 "
	# cmd += " --ipc=host "

	# share host machine network
	cmd += " --network=host "

	# cmd += " " + args.passthrough + " "

	# cmd += " --privileged -v /dev/bus/usb:/dev/bus/usb " # allow usb access

	cmd += " --rm " # remove the image when you exit

	if args.entrypoint and args.entrypoint != "":
		cmd += "--entrypoint=\"%(entrypoint)s\" " % {"entrypoint": args.entrypoint}
	else:
		cmd += "-it "
	cmd += args.image
	cmd_endxhost = "xhost -local:root"

	print("command = \n \n", cmd)
	print("")

	# build the docker image
	if not args.dry_run:
		print("executing shell command")
		os.system('export DISPLAY=:0')
		code = os.system(cmd)
		print("Executed with code ", code)
		os.system(cmd_endxhost)
		# Squash return code to 0/1, as
		# Docker's very large return codes
		# were tricking Jenkins' failure
		# detection
		exit(code != 0)
	else:
		print("dry run, not executing command")
		exit(0)
