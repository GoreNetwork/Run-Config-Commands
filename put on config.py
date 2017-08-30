import os
import re
import socket
import sys
import netmiko
from getpass import getpass
from pprint import pprint
# Un-comment to enable logging
#import logging
#logging.basicConfig(filename='test.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")

def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))
	
def get_ips (file_name):
	ips = []
	for line in open(file_name, 'r').readlines():
		line = get_ip(line)
		for ip in line: 
			ips.append(ip)
	return ips
	

def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()	

def to_doc_a(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.write("\n")
	f.close()	

def grab_username_and_password():
	username = input("Username: ")
	password = getpass()
	return [username,password]


def send_ssh_command(net_connect,command):
	output = net_connect.send_command_expect(command)
	return output
	
def make_connection (ip,username,password):
	try:
		return netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)
	except:
		try:
			return netmiko.ConnectHandler(device_type='cisco_ios_telnet', ip=ip, username=username, password=password)
		except:
			issue = ip+ ", can't be ssh/telneted to"
			to_doc_a("Issues.csv", varable)
			return None

def send_and_save_config(net_connect,config):
	net_connect.config_mode()
	test = net_connect.send_config_set(config)
	print (test)
	net_connect.exit_config_mode()
	net_connect.send_command_expect('write mem')
	
def read_doc (file_name):
	doc = []
	for line in open(file_name, 'r').readlines():
		doc.append(line)
	return doc	
			
IPs_file_name = "IPs.txt"
config_file_name = "Config.txt"
log_file_name = "log.csv"

configs = read_doc (config_file_name)

ips = get_ips (IPs_file_name)

account = grab_username_and_password()
username = account[0]
password = account[1]
for ip in ips:
	try:
		net_connect = make_connection (ip,username,password)
		send_and_save_config(net_connect,configs)
		start_config = send_ssh_command(net_connect,"show start")
		start_config = start_config.split("\n")
		for config in configs:
			if config not in start_config:
				varable = ip+","+config + ", not in start_up"
				to_doc_a(log_file_name, varable)
		done = ip+",done"
		to_doc_a(log_file_name, done)
	except:
		varable = ip+", Failed"
		to_doc_a(log_file_name, varable)
			
