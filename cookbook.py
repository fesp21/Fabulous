# cookbook.py
# This file describes the packages to install and how to set them up.
#
# Ingredients: nginx, memecached, gunicorn, supervisord, virtualenv, git

recipe = [
  # First command as regular user
  {"action":"run", "params":"whoami"},

  # sudo apt-get update
  {"action":"sudo", "params":"apt-get update -qq",
    "message":"Updating apt-get"},

  # List of APT packages to install
  {"action":"apt",
    "params":["mysql-client", "libmysqlclient-dev", "nginx", "memcached", "git",
      "python-setuptools", "python-dev", "build-essential", "python-pip", "python-mysqldb",
      "ruby", "supervisor", "libpq-dev", "libevent-dev", "libmemcached-dev"],
    "message":"Installing apt-get packages"},

  # List of pypi packages to install
  {"action":"pip", "params":["virtualenv"],
    "message":"Installing pip packages"},

  # List of ruby packages to install
  {"action":"gem", "params":["foreman", "mason"],
    "message":"Installing ruby packages"},

  # nginx
  {"action":"put", "params":{"file":"%(FABULOUS_PATH)s/templates/nginx.conf",
    "destination":"/home/%(SERVER_USERNAME)s/nginx.conf"},
    "message":"Configuring nginx"},
  {"action":"sudo", "params":"mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.old"},
  {"action":"sudo", "params":"mv /home/%(SERVER_USERNAME)s/nginx.conf /etc/nginx/nginx.conf"},
  {"action":"sudo", "params":"chown root:root /etc/nginx/nginx.conf"},
  {"action":"put_template", "params":{"template":"%(FABULOUS_PATH)s/templates/nginx-app-proxy",
                                      "destination":"/home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s"}},
  {"action":"sudo", "params":"rm -rf /etc/nginx/sites-enabled/default"},
  {"action":"sudo", "params":"mv /home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s /etc/nginx/sites-available/%(PROJECT_NAME)s"},
  {"action":"sudo", "params":"ln -s /etc/nginx/sites-available/%(PROJECT_NAME)s /etc/nginx/sites-enabled/%(PROJECT_NAME)s"},
  {"action":"sudo", "params":"chown root:root /etc/nginx/sites-available/%(PROJECT_NAME)s"},
  {"action":"sudo", "params":"/etc/init.d/nginx restart", "message":"Restarting nginx"},

  # webapps alias
  {"action":"run", "params":"""echo "alias webapps='cd %(APPS_DIR)s'" >> /home/%(SERVER_USERNAME)s/.profile""",
    "message":"Creating webapps alias"},

  # webapps dir
  {"action":"sudo", "params":"mkdir %(APPS_DIR)s", "message":"Creating webapps directory"},
  {"action":"sudo", "params":"chown -R %(SERVER_USERNAME)s: %(APPS_DIR)s"},

  # git setup
  {"action":"run", "params":"git config --global user.name '%(GIT_USERNAME)s'",
    "message":"Configuring git"},
  {"action":"run", "params":"git config --global user.email '%(ADMIN_EMAIL)s'"},
  {"action":"put", "params":{"file":"%(GITHUB_DEPLOY_KEY_PATH)s",
                            "destination":"/home/%(SERVER_USERNAME)s/.ssh/%(GITHUB_DEPLOY_KEY_NAME)s"}},
  {"action":"run", "params":"chmod 600 /home/%(SERVER_USERNAME)s/.ssh/%(GITHUB_DEPLOY_KEY_NAME)s"},
  {"action":"run", "params":"""echo 'IdentityFile /home/%(SERVER_USERNAME)s/.ssh/%(GITHUB_DEPLOY_KEY_NAME)s' >> /home/%(SERVER_USERNAME)s/.ssh/config"""},
  {"action":"run", "params":"ssh-keyscan github.com >> /home/%(SERVER_USERNAME)s/.ssh/known_hosts"},

  # Download project code
  {"action":"run", "params":"git clone %(GITHUB_REPO)s %(PROJECT_PATH)s",
    "message":"Checking out project"},

  # hacks
  {"action":"sudo", "params":"ln -s /usr/bin/python /usr/local/bin/python"},
  {"action":"sudo", "params":"mkdir -p /var/log/%(PROJECT_NAME)s"},
  {"action":"sudo", "params":"chown %(SERVER_USERNAME)s /var/log/%(PROJECT_NAME)s"},

  # Run Mason
  #TODO make buildpack configurable
  #{"action":"run", "params":"mason buildpacks:install https://github.com/zbyte64/heroku-buildpack-python.git",
  #  "message":"Installing python buildpacks"},
  #{"action":"run", "params":"mason build /home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s -t dir -o %(VIRTUALENV_DIR)s/%(PROJECT_NAME)s",
  #  "message":"Building application"},
  {"action":"run", "params":"virtualenv %(PROJECT_PATH)s",
      "message":"Creating virtualenv"},
  {"action":"virtualenv_command", "params":"pip install -r %(PROJECT_PATH)s/requirements.txt",
      "message":"Installing requirements", "attempts":2},

  # Foreman
  {"action": "write_env", "params":'PATH="%(PROJECT_PATH)s/bin:%(PATH)s"\nVIRTUAL_ENV="%(PROJECT_PATH)s"'},
  {"action":"run", "params":"foreman export -u ubuntu -a %(PROJECT_NAME)s -f %(PROJECT_PATH)s/Procfile -e /home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s.env -p 8000 supervisord /home/%(SERVER_USERNAME)s",
    "message":"Configuring app supervisor"},
  #/home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s.conf

  # Setup supervisor
  {"action":"sudo", "params":"ln -s /home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s.conf /etc/supervisor/conf.d/",
      "message":"Linking supervisor conf"},
  #{"action":"sudo", "params":"supervisorctl start"},
  {"action":"sudo", "params":"supervisorctl update"},
  #{"action":"sudo", "params":"update-rc.d supervisord defaults"},
]