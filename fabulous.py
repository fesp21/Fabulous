from fabric.api import *
from fabric.colors import green as _green, yellow as _yellow
from fabric.exceptions import NetworkError
from .fabulous_conf import fabconf
from .cookbook import recipe
import boto
import time


fabconf.update(env)
env.user = fabconf['SERVER_USERNAME']
env.key_filename = fabconf['SSH_PRIVATE_KEY_PATH']


def ulous(giturl=None, environ_file=None):
    """ec2_key = 'AKIAJCR7D5FNQO5RVY5Q'
    *** This is what you run the first time ***
    """
    if giturl:
        fabconf['GITHUB_REPO'] = giturl
    if environ_file:
        pass
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
    while retries:
        try:
            _run('ls')
        except NetworkError:
            if retries:
                retries -= 1
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
        _virtualenv_command(_render(params))


def _apt(params):
    """
    Runs apt-get install commands
    """
    for pkg in params:
        _sudo("apt-get install -qq %s" % pkg)


def _pip(params):
    """
    Runs pip install commands
    """
    for pkg in params:
        _sudo("pip install %s" % pkg)


def _gem(params):
    """
    Runs gem install commands
    """
    for pkg in params:
        _sudo("gem install %s" % pkg)


def _run(params):
    """
    Runs command with active user
    """
    command = _render(params)
    run(command)


def _sudo(params):
    """
    Run command as root
    """
    command = _render(params)
    sudo(command)


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


def _virtualenv_command(command):
    """
    Activates virtualenv and runs command
    """
    with cd(fabconf['APPS_DIR']):
        sudo(fabconf['ACTIVATE'] + ' && ' + command, user=fabconf['SERVER_USERNAME'])
