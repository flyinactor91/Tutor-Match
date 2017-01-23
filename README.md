# Tutor-Match
Web API for matching tutors and students in the Orlando dev community

## Install

This downloads the repo, installs the Python3 libraries, and builds the default SQLite database

```
git clone https://github.com/flyinactor91/Tutor-Match.git
cd Tutor-Match
pip3 install -r requirements.txt
cd utils && python3 dbgen.py
```

## Running

This repo comes with a script to start a debug server on localhost:5555

```
python3 runserver.py
```

## API

### Endpoints

Users

* /users
* /users/count
* /users/[user-type]
* /users/[user-type]/count
* /users/with/[skill]/count
* /users/[user-type]/with/[skill]/count

Skills

* /skills
* /skills/count

### Vars

User Types

* tutor
* student