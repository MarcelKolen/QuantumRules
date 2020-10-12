# QuantumRules
An online quiz and escape room development framework

The QuantumRules framework was developed with expandability in mind. Future development with this framework should allow new development teams to quickly implement new features.

To accomplish this, the framework has been designed with modularity in mind. It contains a lot of pre-fabd features that help programmers to quickly and independently develop new components without further knowledge about the framework. In this README.md a quick overview will be given on what is needed to develop the software and how you develop within the given framework.

# Getting started
To get started, a few steps need to be taken beforehand. Because this framework is based on a few packages and 3rd party systems, you'll need to set those up before development can start.
1. Create a new virtualenvironment with venv.
2. Install all the dependencies from **requirements.txt**. The dependencies have been created with python pip and you should be able to fetch all the requirements by feeding pip the **requirements.txt** file.
3. Install the in memory datastructure system *REDIS*. The REDIS API is used for group layered socket communications.
  - Windows users should install *Memurai*. *Memurai* is fully compatible with the REDIS API
4. In **QR2/settings.py** make sure that `DEBUG` is set to `True`. Make sure that the database is set to the default development database under `DATABASES` ***NEVER develop on a live database!***. Make sure that under `CHANNEL_LAYERS` you set the `hosts` to your local redis server (often localhost or *127.0.0.1*)
5. From **QR2** run ```python manage.py makemigrations```. This will generate a database initiation.
6. From **QR2** run ```python manage.py migrate```. This will construct all necessary database structures
7. You have to create a superuser to be able to do testing on the admin side. To do this run ```python manage.py createsuperuser```. For correctly setting up multiple users, please refer to the section about **users**
8. From **QR2** run ```python manage.py runserver```
9. Enjoy developing!
