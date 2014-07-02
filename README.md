## Development environment

### Clone the repository

Get the source code and create a virtual environment :
```bash
apt-get install libpq-dev python-dev virtualenvwrapper
git clone git@github.com:eost/gissmo.git
(or your fork repos if you tend to contribute)
cd gissmo
mkvirtualenv gissmo
pip install -r requirements.txt
```

### Database server

By default, Gissmo expects a PostGreSQL database named "gissmo" and an user "gissmo" with the password "gissmo" :
```bash
sudo apt-get install postgresql
sudo -u postgres createuser -E -P gissmo
(enter "gissmo" as password)
sudo -u postgres createdb -O gissmo gissmo
./manage syncdb
(create a superuser)
```

### Launch a test instance

Start the test server using this command :
```bash
./manage runserver
```

Open this following url : [http://127.0.0.1/gissmo]() using your superuser account. Finally submit your pull request ;)


