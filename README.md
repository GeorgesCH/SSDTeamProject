# SSD Team 4 Project Read Me


### Requirements and Running

This project has been written using Python 3.9, taking advantage of the Flask web framework. A full list of the 
packages used in this project can be found in the _requirements.txt_ file. These packages can be installed in your 
own virtual environment using the `$ pip install -r requirements.txt` command. All the packages and technologies used
in the development of this project are open-source as required by the project specifications.

The server can be started by using the `$ python3 run.py` command while in the project root directory. Once the server 
is running, the web app can be accessed by navigating to http://127.0.0.1:5000 in a web browser. If port 5000 is 
already in use, then the port from which the web app may be accessed can be found in the console where the server is 
running. There are three accounts in the default database which can be used to log into the app. No functionality is
available to unauthorised users.

These default logins are: 

| Email               | Password            | Role                |
| ------------------- | ------------------- | ------------------- |
| admin@email.com     | password            | Admin               |
| astro@email.com     | testing             | Astronaut           |
| doc@email.com       | test123             | Medic               |

Note that the request limiter is set to 200 request per day or 100 requests per hour, the session length for users in
the web app is 30 minutes, and the JSON web tokens used by the API have an expiry time of 10 minutes.


### System Functionality
The application is designed to allow the astronauts on board the International Space Station (ISS) to be able to 
securely send health data to medical staff on the ground. To demonstrate this functionality we have chosen blood 
pressure and weight as two health metrics which can be input. The system also allows the astronauts and medics to 
exchange private messages. All medical records and messages are encrypted using Fernet symmetric encryption.

The system makes use of three roles (Admin, Astronaut, and Medic) to limit the access that each user. For example, one 
astronaut cannot view another's medical data or private messages. Due to the expected use of the application we have 
also chosen to not allow users to sign up for their own account. Only an admin user can register new user accounts. 
Users can delete their own account using the API, and an admin may delete any user by using the web app or API.

In addition to viewing the messages and records in the web app, users may also download any
of the data they have access to as a csv file.


### REST API
 Alongside the web api, we have also developed a REST API. All data is sent and recieved as JSON.
 
The API contains the following resources:

| Resource                  | Methods                 |
| ------------------------- | ----------------------- |
| /api/login                | PUT                     | 
| /api/user                 | GET, PUT, PATCH, DELETE |
| /api/record/<record_type> | GET, PUT                | 
| /api/post                 | GET, PUT                | 

`PUT /api/login` allows users to log in by sending their email and password as arguments with the request. This request
will return a JSON web token which must be sent with all other requests to authenticate the user.

`GET /api/user` allows an authenticated user to view details about various users registered in the database, providing
they have the correct permissions.

`PUT /api/user`allows an admin user to register a new user account.

`PATCH /api/user` allows an admin user to update the account details of any user registered in the database.

`DELETE /api/user` allows an admin user to delete any user from the database, along with all their associated records.
This also allows a user to delete their own account and records.

`GET /api/record/<record_type>` allows a user to view their own records. Also allows an admin or medic to view
the records of any astronaut.

`PUT /api/record/<record_type>` allows an astronaut to add a new record to the database.

`GET /api/post` allows users to view all their private messages, either to and from all other users, or a specific
user.

`PUT /api/post` allows a user to send a private message to another user in the database.

Full examples of the API uses, including the required arguments, are available in the _/healthapp/restapi/tests_ folder.

### Testing
Tests that demonstrate the successful use of the REST APIs can be found in the _/healthapp/restapi/tests_ folder. This
folder also contains a rebuild_db.py which when run resets the database to a default state.

This project conforms to the PEP-8 style guide as much as possible. All the modules in this project score an 8 or above 
when analysed using Pylint, with the exception of the _/healthapp/forms.py_ module. This is due to the classes
inheriting from FlaskForms, and therefore not requiring their own method definitions.


### Monolithic vs. Distributed System
This assignment required the development of both a monolithic and distributed solution. In its current state, the app
runs as a monolithic system. The server connects to the _/healthapp/database.db_ sqlite database by default.

The app can be connected to a PostgreSQL database running elsewhere by editing the _/healthapp/\_\_init\_\_.py_ file.
By default, lines 15 - 19 look like so:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<<username>>:<<password>>@<<ip address>>/<<database_name>>'
db = SQLAlchemy(app)
# db.init_app(app)
# migrate = Migrate(app, db)
```

To connect to a PostgreSQL database instead, edit the file to look like so, replacing anything inside << _data_ >> with
the appropriate information:

```python
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<<username>>:<<password>>@<<ip address>>/<<database_name>>'
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
```

As we have nowhere to host our own PostgreSQL server, both our "distributed" API and our monolithic web app use the
same sqlite database in their current state. Due to the shared codebase, we have opted to submit a single project file
which contains both required solutions.

### Further Improvements and Limitations
One obvious limitation of the app in its current form is that it only supports the manual input of health records by 
the astronauts using the system. If the app was to continue in development, the next step would be to allow the system
to ingest data from third party sources, such as any health monitoring devices worn by the astronauts while onboard 
the ISS. 

Another is that the web forms used for the submission of data, currently simply take in strings of up to 12 characters.
In future iterations, a more robust method of taking in and validating the data could be implemented. However, due to 
the use of this interface being restricted to only the astronauts on the ISS, it isn't unreasonable to assume they can
enter the data in an appropriate fashion. Similarly, more robust validation of the arguments sent with requests to the
API could be implemented. Currently, these arguments are only validated by the parsers, and have no length limits.

A final issue which would need to be addressed before the application were to be used in production is the storage of
the encryption keys. Currently, each user's unique key is stored in the same table as the other user data in the 
database. This is an obvious security issue, as gaining access to the database also gains you access to the keys needed
to decrypt the private data stored in it. One solution would be to store these keys in a seperate database, along with
a hashed user id for referencing.