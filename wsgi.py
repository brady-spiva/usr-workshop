# Import required libraries
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from flask import Flask
from flask_mail import Mail, Message

# Initialize the Flask app and Dash app
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Configure email settings
app.config['MAIL_SERVER'] = 'your-mail-server.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Define the layout of the app
app.layout = html.Div([
    html.H1('OpenShift User Creation App'),
    html.Div([
        html.Label('Username:'),
        dcc.Input(id='username-input', type='text', value=''),
        html.Label('Password:'),
        dcc.Input(id='password-input', type='password', value=''),
        html.Button('Create User', id='create-button', n_clicks=0),
        html.Div(id='output-message')
    ])
])

# Define callback to handle button click event
@app.callback(
    Output('output-message', 'children'),
    Input('create-button', 'n_clicks'),
    Input('username-input', 'value'),
    Input('password-input', 'value')
)
def create_user(n_clicks, username, password):
    if n_clicks > 0:
        # Logic to create user in OpenShift Cluster
        # Code for creating user in OpenShift Cluster goes here
        # For demonstration purposes, let's assume the user creation is successful
        user_creation_success = True

        if user_creation_success:
            # Send email to the user
            msg = Message('OpenShift Account Information', sender='your-email@example.com', recipients=[username])
            msg.body = f'Username: {username}\nPassword: {password}\nOpenShift Cluster URL: https://openshift-cluster-url.com'
            mail.send(msg)
            return 'User created successfully! Check your email for login information.'
        else:
            return 'User creation failed. Please try again.'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


# run gunicorn manually on localhost
# gunicorn wsgi:application -b 127.0.0.1:8080
