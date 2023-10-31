
# User Self Registration App

## Users for workshops, labs, etc. can register themselves and get credentials to use for the duration of the event. This is intended to be used on ephemeral OpenShift resources
![Screenshot](./imgs/Screenshot.png)


## Local development

Create virtual environment, activate, and install dependencies

```
python -m venv .venv
. ./.venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```

Run w/ python `_main_`

```
python wsgi.py
```

OR

Run w/ `gunicorn` (s2i python container does this)

```
gunicorn wsgi:application -c config.py
```

Access via http://localhost:8080/

## WSGI / gunicorn

This Python application relies on the support provided by the default S2I builder for deploying a WSGI application using the ``gunicorn`` WSGI server. The requirements which need to be satisfied for this to work are:

* The WSGI application code file needs to be named ``wsgi.py``.
* The WSGI application entry point within the code file needs to be named ``application``.
* The ``gunicorn`` package must be listed in the ``requirements.txt`` file for ``pip``.

In addition, the ``.s2i/environment`` file has been created to allow environment variables to be set to override the behavior of the default S2I builder for Python.

* The environment variable ``APP_CONFIG`` has been set to declare the name of the config file for ``gunicorn``.

See https://github.com/OpenShiftDemos/os-sample-python

## More information about this project

This repo contains a Dash application that can be deployed to OpenShift using Source to Image (S2I). Here are the main files:

1. The Dash Application (learn about Dash [HERE](https://dash.plotly.com/) )

    - `wsgi.py`;  main application, to be run by gunicorn

2. The S2I environment variables. Used to setup additional environment varibles (ex: setup packages using a Nexus repository)

    - `.s2i/environment`

3. This file contains the dependencies that the application needs to run

    - `requirements.txt`

    One way to create a requirements file for your application is by running the following:

    ```
    pip freeze > requirements.txt
    ```

#### How it works

The file `wsgi.py` contains the instructions for python to run Dash. 

When s2i builds the container, it will look into `.s2i` for additional instructions, including environment variables for installing packages with `pip`.

## Links
- [Python s2i examples](https://github.com/sclorg/s2i-python-container/tree/master/examples)
- [Dash (Plotly)](https://dash.plotly.com/)
