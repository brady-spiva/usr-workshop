# Import required libraries
import secrets
import string
import re
import csv
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import dash
from dash import html, callback_context
from dash.dependencies import Input, Output, State
from flask import Flask
import dash_bootstrap_components as dbc
from kubernetes import client, config
from openshift.dynamic import DynamicClient


load_dotenv(find_dotenv())
# Check if kubeconfig file exists
here = Path(__file__).parent
kubeconfig_path = here.joinpath(*os.getenv('KUBECONFIG').split(os.sep))
# check if the kubeconfig file exists at the provided path
if not kubeconfig_path.exists():
    raise FileNotFoundError(f'Kubeconfig file not found at {kubeconfig_path}')

k8s_client = config.new_client_from_config(config_file=kubeconfig_path.as_posix())
dyn_client = DynamicClient(k8s_client)

# Initialize the Flask app and Dash app
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = html.Div(
    [
        dbc.Container(
            [
                html.H1('User Self Registration', className='mt-5 mb-4 text-center'),  # Center the heading
                # html.Div('Please enter a username - your password will be automagically generated. Your username should be at least 5 characters long and contain only letters, numbers, and underscores.', className='text-center text-muted mb-4'),
                html.Div('Please fill out the form below and your credentials will be automagically generated!', className='text-center text-muted mb-4'),
                html.Div('Your username should be at least 5 characters long and contain only letters, numbers, and underscores.', className='text-center text-muted mb-4'),
                html.Div('Your email address should be a valid address.', className='text-center text-muted mb-4'),
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
                                dbc.Label('First Name:'),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(id='first-name-input', type='text', value='', className='form-control'),
                                    ]
                                ),
                                dbc.Label('Last Name:'),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(id='last-name-input', type='text', value='', className='form-control'),
                                    ]
                                ),
                                dbc.Label('Email:'),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(id='email-input', type='text', value='', className='form-control'),
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
                dbc.ModalHeader('Account Information'),
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
    [State('username-input', 'value'),
     State('first-name-input', 'value'),
     State('last-name-input', 'value'),
     State('email-input', 'value')],
    prevent_initial_call=True
)
def process_user_creation(create_clicks, close_clicks, username_from_ui, first_name, last_name, email):
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

        # "in-cluster config"? research this! 
        # TODO: how do we handle duplicate usernames? does the CLI handle this natively?
        
        # create_user_in_cluster(ocp_admin_username, ocp_admin_password, ocp_cluster_url, username_from_ui, autogenerated_user_password)
        # Save user details to a local CSV file
        file_path = Path('users.csv')
        if not file_path.exists() or file_path.stat().st_size == 0:
            # File doesn't exist or is empty, so write the header
            with open('users.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['First Name', 'Last Name', 'Email', 'Username', 'Password'])
        # Now, append the data row
        with open('users.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([first_name, last_name, email, username_from_ui, autogenerated_user_password])

        ### end create user code
        return True, username_from_ui, autogenerated_user_password, ocp_cluster_url
    elif 'close-modal-button' in ctx.triggered_id:
        return False, '', '', ''

# Define input validation callback function for both username and password
@app.callback(
    Output('create-button', 'disabled'),
    [
        Input('username-input', 'value'),
        Input('email-input', 'value')
    ],
    prevent_initial_call=False
)
def validate_inputs(username, email):
    # Regular expression pattern for a basic email validation
    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    
    # Validate username
    if (username is None or len(username) < 5 or re.search(r'[^\w]', username) or ' ' in username):
        return True  # Disable the button if validation fails
    
    # Validate email
    if not re.match(email_pattern, email):
        return True  # Disable the button if validation fails
    
    return False  # Enable the button if validation passes

def create_user_in_cluster(ocp_admin_username, ocp_admin_password, ocp_cluster_url, username_from_ui, autogenerated_user_password):
    # TODO: configure an htpasswd identity provider in the cluster, per these instructions: https://docs.openshift.com/container-platform/4.8/authentication/identity_providers/configuring-htpasswd-identity-provider.html#identity-provider-creating-htpasswd-secret_configuring-htpasswd-identity-provider
    # every time a new user is created, reapply the htpasswd file to the cluster
    
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

# Run the app
if __name__ == '__main__':
    # host needs to be set to this for deployment
    app.run_server(debug=True, host='0.0.0.0', port=8080)
