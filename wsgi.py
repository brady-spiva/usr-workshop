# Import required libraries
import secrets
import string
import re
import os
from dotenv import load_dotenv
from subprocess import run, PIPE
import dash
from dash import html, callback_context
from dash.dependencies import Input, Output, State
from flask import Flask
import dash_bootstrap_components as dbc

# Initialize the Flask app and Dash app
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = html.Div(
    [
        dbc.Container(
            [
                html.H1('OpenShift User Creation App', className='mt-5 mb-4 text-center'),  # Center the heading
                html.Div('Please enter a username - your password will be automagically generated. Your username should be at least 5 characters long and contain only letters, numbers, and underscores.', className='text-center text-muted mb-4'),
                dbc.Row(
                    dbc.Col(
                        dbc.CardGroup(
                            [
                                dbc.Label('Username:'),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(id='username-input', type='text', value='', className='form-control'),
                                    ]
                                ),
                            ]
                        ),
                        width=12,
                        className='mb-3'
                    ),
                ),
                dbc.Row(
                    dbc.Col(dbc.Button('Create User', id='create-button', n_clicks=0, color='primary', className='btn-lg btn-block'), width=12),
                    className='mb-4'
                ),
                dbc.Row(dbc.Col(html.Div(id='output-message', className='lead text-center')))
            ],
            className='border p-4',  # Add border and padding around the form
            style={'width': '400px', 'margin': '0 auto'},  # Set form width and center it horizontally
        ),
        html.Div(id='hidden-div', style={'display': 'none'}),  # Hidden div for storing state
        # Modal to display OpenShift credentials and cluster URL
        dbc.Modal(
            [
                dbc.ModalHeader('OpenShift Account Information'),
                dbc.ModalBody(
                    dbc.Table(
                        [
                            html.Tr([html.Th('Username:'), html.Td(id='modal-username')]),
                            html.Tr([html.Th('Password:'), html.Td(id='modal-password')]),
                            html.Tr([html.Th('Cluster URL:'), html.Td(id='modal-cluster-url')]),
                        ],
                        bordered=True,
                        striped=True,
                        hover=True,
                        responsive=True,
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button('Close - I have copied this information to another location', id='close-modal-button', n_clicks=0)
                ),
            ],
            id='output-modal',
            size='lg',
            centered=True,
        )
    ],
    className='d-flex justify-content-center align-items-center',
    style={'height': '100vh'}
)


# Combined callback to handle user creation and modal closing, and generate a random password
@app.callback(
    [Output('output-modal', 'is_open'),
     Output('modal-username', 'children'),
     Output('modal-password', 'children'),
     Output('modal-cluster-url', 'children')],
    [Input('create-button', 'n_clicks'),
     Input('close-modal-button', 'n_clicks')],
    [State('username-input', 'value')],
    prevent_initial_call=True
)
def process_user_creation(create_clicks, close_clicks, username_from_ui):
    ctx = callback_context

    if not ctx.triggered_id:
        raise dash.exceptions.PreventUpdate

    if 'create-button' in ctx.triggered_id:
        # Generate a random complex password excluding specific special characters
        excluded_special_characters = ':;\\/_-|'  # Special characters to be excluded
        password_characters = ''.join(
            char for char in string.ascii_letters + string.digits + string.punctuation if char not in excluded_special_characters
        )
        autogenerated_user_password = ''.join(secrets.choice(password_characters) for _ in range(12))

        ### Code for creating a user in OpenShift cluster
        # load dotenv file
        load_dotenv('.env')
        # get the username, password, and cluster_url from environment variables
        # Get environment variables

        # TODO: use the kube config file!!
        # "in-cluster config"? research this! 
            # generating a service account, with a role binding to allow it to create users
                # we could do this all in a single YAML file: the deployment config, the role binding, the service account, pull the app code, use s2i
            # when a pod is instantiated in a cluster, it already has a service account token that it can use to authenticate to the API server.
                # It is located inside the pod at: /var/run/secrets/kubernetes.io/serviceaccount/token
        # TODO: how do we handle duplicate usernames? does the CLI handle this natively?
        # TODO: we want to also capture the first name, last name, and email address of the user. Make these required - can we just dump this to a CSV? possibly use a configmap?
        # TODO: consider using the kubernetes python client library instead of the CLI. This might also allow for deploying this to vanilla kubernetes, not just OpenShift.
        # TODO: update the Cluster URL to be the URL for devspaces
        # TODO: add the deployment config to the repo, and use oc apply -f to deploy it
        # TODO: add an ansible playbook to deploy the app to a cluster

        ocp_admin_username = os.getenv("ZIPSHIP_USERNAME")
        ocp_admin_password = os.getenv("ZIPSHIP_PASSWORD")
        ocp_cluster_url = os.getenv("ZIPSHIP_CLUSTER_URL")

        create_user_in_cluster(ocp_admin_username, ocp_admin_password, ocp_cluster_url, username_from_ui, autogenerated_user_password)

        ### end create user code
        return True, username_from_ui, autogenerated_user_password, ocp_cluster_url
    elif 'close-modal-button' in ctx.triggered_id:
        return False, '', '', ''

# Define input validation callback function for both username and password
@app.callback(
    Output('create-button', 'disabled'),
    [Input('username-input', 'value')],
    #  Input('password-input', 'value')],
    prevent_initial_call=False
)
def validate_inputs(username):
    if (username is None or len(username) < 5 or re.search(r'[^\w]', username) or ' ' in username):
        return True  # Disable the button if validation fails
    return False  # Enable the button if validation passes

def create_user_in_cluster(ocp_admin_username, ocp_admin_password, ocp_cluster_url, username_from_ui, autogenerated_user_password):
    # Path to the htpasswd file
    htpasswd_file = 'users.htpasswd'

    # Check if htpasswd file exists, create it if not
    if not os.path.exists(htpasswd_file):
        with open(htpasswd_file, 'w') as file:
            file.write(f'{username_from_ui}:{autogenerated_user_password}\n')
    else:
        # Append user to existing htpasswd file
        with open(htpasswd_file, 'a') as file:
            file.write(f'{username_from_ui}:{autogenerated_user_password}\n')

    # Command to login to OpenShift cluster
    login_cmd = f'oc login {ocp_cluster_url} -u {ocp_admin_username} -p {ocp_admin_password} --insecure-skip-tls-verify=true'
    # Run the command
    result = run(login_cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # Command to create/update htpasswd secret in OpenShift cluster
    cmd = f'oc create secret generic htpass-secret --from-file=htpasswd={htpasswd_file} -n openshift-config'

    # Run the command
    result = run(cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # Check if the command was successful
    if result.returncode == 0:
        # Update OAuth configuration to use htpasswd identity provider
        oauth_cmd = f'oc apply -f - <<EOF\napiVersion: config.openshift.io/v1\nkind: OAuth\nmetadata:\n  name: cluster\nspec:\n  identityProviders:\n  - name: htpassidp\n    mappingMethod: claim\n    type: HTPasswd\n    htpasswd:\n      fileData:\n        name: htpass-secret\nEOF'
        oauth_result = run(oauth_cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        if oauth_result.returncode == 0:
            print(f'User {username_from_ui} created/updated successfully in the cluster.')
        else:
            print(f'Error updating OAuth configuration: {oauth_result.stderr.strip()}')
    else:
        print(f'Error creating htpasswd secret: {result.stderr.strip()}')




# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
