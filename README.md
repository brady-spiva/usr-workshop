
# User Self Registration App

### Users for workshops, labs, etc. can register themselves and get credentials to use for the duration of the event. This is intended to be used on ephemeral OpenShift resources
![Screenshot](./imgs/Screenshot.png)

The application is deployed to the `TODO` namespace. Users are managed using htpasswd. The htpasswd file is stored locally in the container and is **not persisted**. User information is also stored locally in the container to `users.csv`. This file is also **not persisted**.

After using this application, users can be deleted by deleting the namespace. This will delete the htpasswd file and the users.csv file.

Use the following command to retrieve the `users.csv` file from the container:

```
oc rsync <pod>:/path/to/users.csv .
```


## How to deploy User Self Registration App to an OpenShift cluster

1. Copy a valid kubeconfig to `/kubernetes/.kube/config`
2. 

## Local development

Create a Python virtual environment, activate it, and install Python dependencies

```
python -m venv .venv
. ./.venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```

Run w/ python `__main__`

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

## Misc
generating a service account, with a role binding to allow it to create users
- we could do this all in a single YAML file: the deployment config, the role binding, the service account, pull the app code, use s2i
when a pod is instantiated in a cluster, it already has a service account token that it can use to authenticate to the API server.
- It is located inside the pod at: /var/run/secrets/kubernetes.io/serviceaccount/token