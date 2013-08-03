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
      "ruby", "supervisor"],
    "message":"Installing apt-get packages"},

  # List of pypi packages to install
  {"action":"pip", "params":["virtualenv", "virtualenvwrapper"],
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

  # virtualenvwrapper
  {"action":"sudo", "params":"mkdir %(VIRTUALENV_DIR)s", "message":"Configuring virtualenvwrapper"},
  {"action":"sudo", "params":"chown -R %(SERVER_USERNAME)s: %(VIRTUALENV_DIR)s"},
  {"action":"run", "params":"echo 'export WORKON_HOME=%(VIRTUALENV_DIR)s' >> /home/%(SERVER_USERNAME)s/.profile"},
  {"action":"run", "params":"echo 'source /usr/local/bin/virtualenvwrapper.sh' >> /home/%(SERVER_USERNAME)s/.profile"},
  {"action":"run", "params":"source /home/%(SERVER_USERNAME)s/.profile"},

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
  {"action":"run", "params":"git clone %(GITHUB_REPO)s %(PROJECT_NAME)s",
    "message":"Checking out project"},

  # hacks
  {"action":"sudo", "params":"ln -s /usr/bin/python /usr/local/bin/python"},
  {"action":"run", "params":"rm -f %(PROJECT_NAME)s/runtime.txt"},

  # Run Mason
  {"action":"run", "params":"mason buildpacks:install https://github.com/heroku/heroku-buildpack-python.git#v24",
    "message":"Installing python buildpacks"},
  {"action":"run", "params":"mason build %(PROJECT_NAME)s -t dir -o %(VIRTUALENV_DIR)s/%(PROJECT_NAME)s",
    "message":"Building application"},

  # Foreman
  {"action":"run", "params":"foreman export -u ubuntu -a %(PROJECT_NAME)s -f %(VIRTUALENV_DIR)s/%(PROJECT_NAME)s/Procfile supervisord /home/%(SERVER_USERNAME)s",
    "message":"Configuring app supervisor"},
  #/home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s.conf

  # Setup supervisor
  {"action":"sudo", "params":"ln -s /home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s.conf /etc/supervisor/conf.d/",
      "message":"Linking supervisor conf"},
  #{"action":"sudo", "params":"supervisorctl start"},
  {"action":"sudo", "params":"supervisorctl update"},
  #{"action":"sudo", "params":"update-rc.d supervisord defaults"},
]