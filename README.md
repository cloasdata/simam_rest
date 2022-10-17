# SIMAM_REST - sitemangement messenger
A test project to investigate following stack:
* REST Api backend with starlite
* Database integration via sqlalchemy
* Simple client based on commandline interface
* Text userinterface based on asciimatics
* In progress Flutter Client for Android etc.


## installation:
### install from git
    pip install git+https://github.com/cloasdata/simam_rest

or clone

### install database
    py cmd.py database --install 'path to database'

## usage

start server (needs ASGI server needs to be installed in front)

      uvicorn server:app --reload       

start client
    
    py cmd.py -c http://127.0.0.1:8000 user_1 user_1 -t 1

starts the client, with a user_1 at project id 1


