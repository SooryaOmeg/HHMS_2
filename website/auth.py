from flask import render_template
from .models import Appointment
import os
import requests
from flask import Blueprint, redirect, url_for, session, request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth.transport.requests


auth = Blueprint('auth', __name__)

flow = Flow.from_client_secrets_file('./credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar'],
    redirect_uri='http://localhost:5000/auth/callback'
)
CLIENT_SECRET_FILE = './credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_credentials():
    creds = None
    token_path = 'token.json'  # Where the access and refresh tokens will be stored
    # Load existing credentials if they are available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no valid credentials, use the OAuth flow to fetch them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh the token if it's expired
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_data_from_api():
    creds = get_google_credentials()
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://api.example.com/data', headers=headers)
    response.raise_for_status()
    return response.json()


@auth.route('/login')
def login():
    auth_url, state = flow.authorization_url(access_type='offline',
            include_granted_scopes='true',prompt='consent')
    print(auth_url)
    session['state'] = state
    return redirect(auth_url)

@auth.route('/auth/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    print(credentials)
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    return redirect(url_for('views.homepage'))

@auth.route('/raman.html', methods=['GET','POST'])
def book_appointment():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'check_availability':
            day = request.form.get('day')
            time = request.form.get('time')
            print(type(day), type(time))
            avail = Appointment.scheduleAppointment(day, time)
            return render_template('raman.html', result=avail)
        elif action == 'submit_booking':
            book_id = request.form.get('selected_booking').upper()
            user_id = "Dummy_ID1"
            print(book_id, user_id)
            booking = Appointment.scheduleAppointments(book_id, user_id, action)
            return redirect(url_for('views.homepage'))

    result = '0'
    return render_template('raman.html',result = result)
