# webapp

> Webapp is a cloud native web application that is being developed and maintained by gao.xiaob@northeastern.edu. It is for the couse learning of *CSYE6225 Network Structures and Cloud Computing*, and functionality will be complete as future assignments come. *Django* and *Django REST* are main frameworks to support its development.

## Run in Local Development

**> *Install Python3.6+, virtualenv, and MySQL5.6+***

**> *Create & enter a virtual environment***

    cd <root/webapp/directory>                
    virtualenv env
    source env/bin/activate    # on Windows: env/Scripts/activate          

**> *Install dependencies***
  
    pip install -r requirements.txt

**> *Set environment variables(on linux/unix, on Windows use <code>set</code> command instead)***

    # Enable MySQL as default database
    export DEV_ENV=1 

    # Credentials to connect to MySQL server             
    export MYSQL_DB_NAME=x    # database name
    export MYSQL_UNAME=x      # username
    export MYSQL_PWD=x        # password
    export MYSQL_HOST=x       # host name/IP address, imply 'localhost' when no x provided (i.e export MYSQL_HOST=)
    export MYSQL_PORT=x       # host port, imply '3306' when no x

**> *Run the app***

    cd ./src

    # Propagate changes you make to models (adding a field, deleting a model, etc.) into database schema
    python manage.py makemigrations
    python manage.py migrate

    python manage.py runserver

    # Run tests for assignment#2
    python manage.py test users

## API Calls from Assignment#2

#### Create a new user &#x25BE;

    POST: /v1/user/

###### REQUEST PARAMETERS
*Content-Type: application/json*

    first_name
    last_name
    username      # username is a valid email address
    password      # a valid password contains at least 9 characters with at least 1 uppercase letter, 1 number, and 1 special character in [@#?!+%]

###### SAMPLE RESPONSES

    Status: 201 Created
    {
        "id": "a9e20616-b674-4e96-baf2-ec3d8814afcc",
        "first_name": "Xiaobin",
        "last_name": "Gao",
        "username": "gao.xiaob@northeastern.edu",
        "account_created": "2020-09-29T20:39:39.704706Z",
        "account_updated": "2020-09-29T20:39:39.704714Z"
    }

    Status: 400 Bad Request
    {
        "email_address": [
            "User with that email already exists"
        ]
    }

    Status: 400 Bad Request
    {
        "first_name": [
            "This field is required."
        ]
    }


#### Generate an authentication token &#x25BE;

    POST: /api/token/

###### REQUEST PARAMETERS
*Content-Type: application/json*

    username      
    password

###### SAMPLE RESPONSE
    Status: 200 OK
    {
        "token": "eebdefc1caf23ca06332a7d8a41770dc53abe5a9"
    }


#### Get user information &#x25BE;

    GET: /v1/user/self/

###### REQUEST PARAMETERS
*Content-Type: application/json*
*Authorization: Token <code>< generated token ></code>*

###### SAMPLE RESPONSE

    Status: 200 OK
    {
        "id": "a9e20616-b674-4e96-baf2-ec3d8814afcc",
        "first_name": "Xiaobin",
        "last_name": "Gao",
        "username": "gao.xiaob@northeastern.edu",
        "account_created": "2020-09-29T20:39:39.704706Z",
        "account_updated": "2020-09-29T20:39:39.704714Z"
    }


#### Update user information &#x25BE;

    PUT: /v1/user/self/

###### REQUEST PARAMETERS
*Content-Type: application/json*
    
    first_name
    last_name
    username         # same username as that of the current authenticated user
    password

###### SAMPLE RESPONSES
    Status: 204 No Content

    Status: 400 BAD Request
    {
        "username": "Incorrect username.",
        "account_created": "Unchangeable field.",
        "account_updated": "Unchangeable field.",
        "id": "Unchangeable field."
    }

    Status: 400 BAD Request
    {
        "first_name": [
            "This field is required."
        ]
    }
# demo
