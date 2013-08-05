from fabric.api import *
from fabric.colors import green as _green, yellow as _yellow
from fabric.exceptions import NetworkError
from fabulous_conf import fabconf
from cookbook import recipe
import boto
import time
import os


env.user = fabconf['SERVER_USERNAME']
env.key_filename = fabconf.get('SSH_PRIVATE_KEY_PATH', os.path.join(fabconf['SSH_PATH'], fabconf['EC2_KEY_NAME']))


def ulous(giturl=None, environ_file=None):
    """
    *** This is what you run the first time ***
    """
    if giturl:
        fabconf['GITHUB_REPO'] = giturl
    if environ_file:
        fabconf['ENVIRON_FILE'] = environ_file
    fabconf.setdefault('ENVIRON_PAYLOAD', '')
    if fabconf.get('ENVIRON_FILE'):
        fabconf['ENVIRON_PAYLOAD'] += '\n'+open(fabconf['ENVIRON_FILE'], 'r').read()
    fab()


def fab():
    """
    This does the real work for the ulous() task. Is here to provide backwards compatibility
    """
    start_time = time.time()
    print(_green("Started..."))
    env.host_string = _create_server()
    print(_green("Waiting 30 seconds for server to boot..."))
    time.sleep(30)
    print(_green("Polling server..."))
    retries = 6
    while retries > 0:
        retries -= 1
        try:
            _run('ls')
        except NetworkError:
            if retries:
                time.sleep(5)
            else:
                raise
        else:
            break
    _oven()
    end_time = time.time()
    print(_green("Runtime: %f minutes" % ((end_time - start_time) / 60)))
    print(_green(env.host_string))


def _oven():
    """
    Cooks the recipe. Fabulous!
    """
    for ingredient in recipe:
        try:
            print(_yellow(ingredient['message']))
        except KeyError:
            pass
        globals()["_" + ingredient['action']](ingredient['params'])


def _create_server():
    """
    Creates EC2 Instance
    """
    print(_yellow("Creating instance"))
    conn = boto.connect_ec2(fabconf['ec2_key'], fabconf['ec2_secret'])
    image = conn.get_all_images(fabconf['ec2_amis'])

    reservation = image[0].run(1, 1, fabconf['ec2_keypair'], fabconf['ec2_secgroups'],
        instance_type=fabconf['ec2_instancetype'])

    instance = reservation.instances[0]
    conn.create_tags([instance.id], {"Name":fabconf['INSTANCE_NAME_TAG']})

    while instance.state == u'pending':
        print(_yellow("Instance state: %s" % instance.state))
        time.sleep(10)
        instance.update()

    print(_green("Instance state: %s" % instance.state))
    print(_green("Public dns: %s" % instance.public_dns_name))

    return instance.public_dns_name


def _virtualenv(params):
    """
    Allows running commands on the server
    with an active virtualenv
    """
    with cd(fabconf['APPS_DIR']):
        _virtualenv_command(params)


def _apt(params, attempts=2):
    """
    Runs apt-get install commands
    """
    for pkg in params:
        _sudo("apt-get install -qq %s" % pkg, attempts)


def _pip(params, attempts=2):
    """
    Runs pip install commands
    """
    for pkg in params:
        _sudo("pip install %s" % pkg, attempts)


def _gem(params, attempts=2):
    """
    Runs gem install commands
    """
    for pkg in params:
        _sudo("gem install %s" % pkg, attempts)


def _run(params, attempts=1):
    """
    Runs command with active user
    """
    command = _render(params)
    while attempts > 0:
        attempts -= 1
        try:
            run(command)
        except:
            if attempts < 1:
                raise


def _sudo(params, attempts=1):
    """
    Run command as root
    """
    command = _render(params)
    while attempts > 0:
        attempts -= 1
        try:
            sudo(command)
        except:
            if attempts < 1:
                raise


def _put(params):
    """
    Moves a file from local computer to server
    """
    put(_render(params['file']), _render(params['destination']))


def _put_template(params):
    """
    Same as _put() but it loads a file and does variable replacement
    """
    f = open(_render(params['template']), 'r')
    template = f.read()

    run(_write_to(_render(template), _render(params['destination'])))


def _render(template, context=fabconf):
    """
    Does variable replacement
    """
    return template % context


def _write_to(string, path):
    """
    Writes a string to a file on the server
    """
    return "echo '" + string + "' > " + path


def _append_to(string, path):
    """
    Appends to a file on the server
    """
    return "echo '" + string + "' >> " + path


def _virtualenv_command(params, attempts=1):
    """
    Activates virtualenv and runs command
    """
    command = _render(params)
    with cd(fabconf['APPS_DIR']):
        while attempts > 0:
            attempts -= 1
            try:
                sudo(fabconf['ACTIVATE'] + ' && ' + command, user=fabconf['SERVER_USERNAME'])
            except:
                if attempts < 1:
                    raise


def _write_env(params):
    payload = fabconf['ENVIRON_PAYLOAD'] + '\n' + _render(params)
    path = _render('/home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s.env')
    run(_write_to(payload, path))
