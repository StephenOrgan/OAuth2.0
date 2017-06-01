# Udacity - Item Catalogue Project


## Overview

This project contains a web application that allows user to create items within a variety of categories and integrates social sign-in with Google, Facebook, and LinkedIn for authorization.

## Pre-requisites

In order to run this application, please ensure you have Python, Vagrant, and VirtualBox installed.  This project uses a pre-configured Vagrant virtual machine which has a Flask server installed.

Three .json files are required to be created that provide the ClientID, Client Secret, and ReturnURL to your application in the respective social networks.


This project requires applications to be created on Google, Facebook, LinkedIn and storing the details in a .json file.

Since LinkedIn doesn't allow signing in from Localhost, you need to setup a virtual host and map the new URL with the IP address of the virtual machine in your host file.

Here are examples of the json within the files for this project that are stored in the root directory.  Replace ClientID and secret from your application:

### Google (client_secrets.json)

```
{"web":{
	"client_id":"XXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXX.apps.googleusercontent.com",
	"project_id":"test-project-162418",
	"auth_uri":"https://accounts.google.com/o/oauth2/auth",
	"token_uri":"https://accounts.google.com/o/oauth2/token",
	"auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"XXXXXXXXXXXXXXXXXX",
	"redirect_uris":["http://127.0.0.1:5500/login",
		"http://127.0.0.1:5500/gconnect",
		"http://localhost:5500/login",
		"http://localhost:5500/gconnect",
		"http://item-catalogue.dev:5500/gconnect"],
		"javascript_origins":["http://127.0.0.1:5500",
		"http://localhost:5500",
		"http://item-catalogue.dev:5500"]
	}
}
```

### Facebook (fb_client_secrets.json)

```
{
	"web": {
		"app_id": "XXXXXXXXXXXXX",
		"app_secret": "XXXXXXXXXXXXXXXXXXXXXX"
	}
}

```

### LinkedIn (ln_client_secrets.json)

Note that LinkedIn cannot have a return URL that is localhost and you must have a virtual host setup.  In this instance the virtual host is the URL: http://item-catalogue.dev:5500/callback/linkedin

```
{		
 	"web": {		
 		"app_id": "XXXXXXXX",		
 		"app_secret": "XXXXXXXXXXXXXXXX",
 		"return_uri": "http://item-catalogue.dev:5500/callback/linkedin"		
 	}		
 }
```


## Setting up the Database
In the root directory type the following commands to install the database and it's properties:

```
$ vagrant up
$ vagrant ssh
$ cd /vagrant
$ python itemcatalog_db_setup.py
```

## Importing Categories to the database
There is a file that can populate some categories into the database.  To preload some categories into the database:

```
$ vagrant up
$ vagrant ssh
$ cd /vagrant
$ python itemcatalog_import_categories.py
```



## Run the Application

```
$ cd vagrant
$ vagrant up
$ vagrant ssh
```

Within the virtual machine change in to the shared directory by running

```
$ cd /vagrant/catalog
$ python itemcatalog.py
```

Then in your browser navigate to localhost:5500 (and/or virtualhost:5500)