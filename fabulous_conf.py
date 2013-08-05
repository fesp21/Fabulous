import os.path
from os.path import expanduser
from fabric.api import env

fabconf = {}

#  Do not edit
fabconf['FABULOUS_PATH'] = os.path.dirname(__file__)

# Username for connecting to EC2 instaces
fabconf['SERVER_USERNAME'] = "ubuntu"

# Full local path for .ssh
fabconf['SSH_PATH'] = os.path.join(expanduser("~"), ".ssh")

# Name of the private key file you use to connect to EC2 instances
fabconf['EC2_KEY_NAME'] = "key.pem"

# Project name: polls
fabconf['PROJECT_NAME'] = "polls"

# App domains
fabconf['DOMAINS'] = "example.com www.example.com"

# Email for the server admin
fabconf['ADMIN_EMAIL'] = "webmaster@localhost"

# Git username for the server
fabconf['GIT_USERNAME'] = "Server"

# Name of the private key file used for github deployments
fabconf['GITHUB_DEPLOY_KEY_NAME'] = "github"


# Path to the repo of the application you want to install
fabconf['GITHUB_REPO'] = "https://github.com/gcollazo/Blank-django-Project.git"

# Name tag for your server instance on EC2
fabconf['INSTANCE_NAME_TAG'] = "AppServer"

# EC2 key. http://bit.ly/j5ImEZ
fabconf['ec2_key'] = ''

# EC2 secret. http://bit.ly/j5ImEZ
fabconf['ec2_secret'] = ''

# AMI name. http://bit.ly/liLKxj
fabconf['ec2_amis'] = ['ami-1335f37a']

# Name of the keypair you use in EC2. http://bit.ly/ldw0HZ
fabconf['ec2_keypair'] = ''

# Name of the security group. http://bit.ly/kl0Jyn
fabconf['ec2_secgroups'] = []

# API Name of instance type. http://bit.ly/mkWvpn
fabconf['ec2_instancetype'] = 't1.micro'


fabconf['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'


for key, value in env.items():
    if isinstance(fabconf.get(key), list):
        value = [val.strip() for val in value.split(',')]
    fabconf[key] = value


# Where to install apps
fabconf.setdefault('APPS_DIR', "/home/%s/webapps" % fabconf['SERVER_USERNAME'])

# Path for virtualenvs
fabconf.setdefault('VIRTUALENV_DIR', fabconf['APPS_DIR'])

# Where you want your project installed: /APPS_DIR/PROJECT_NAME
fabconf.setdefault('PROJECT_PATH', "%s/%s" % (fabconf['APPS_DIR'], fabconf['PROJECT_NAME']))

# Virtualenv activate command
fabconf.setdefault('ACTIVATE', "source %s/bin/activate" % (fabconf['PROJECT_PATH']))

# Don't edit. Local path for deployment key you use for github
fabconf.setdefault('GITHUB_DEPLOY_KEY_PATH', "%s/%s" % (fabconf['SSH_PATH'], fabconf['GITHUB_DEPLOY_KEY_NAME']))
