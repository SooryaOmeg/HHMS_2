from datetime import datetime, timezone, timedelta

from flask import session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from . import db


def convert_to_iso_format(date_str, time_str):
    # Parse the date and time from the given format
    dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M")

    # Add the time zone offset for India Standard Time (IST) +5:30
    ist_offset = timedelta(hours=5, minutes=30)
    dt = dt.replace(tzinfo=timezone(ist_offset))

    # Convert to ISO 8601 format
    iso_format = dt.isoformat()
    return iso_format

def add_minutes_to_time(time_str, minutes_to_add=10):
    # Parse the time string into a datetime object
    time_obj = datetime.strptime(time_str, "%H:%M")

    # Add the specified minutes
    updated_time = time_obj + timedelta(minutes=minutes_to_add)

    # Return the updated time in HH:MM format
    return updated_time.strftime("%H:%M")

def add_5_30_hrs(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M")

    updated_time = time_obj + timedelta(hours=5, minutes=30)

    return updated_time.strftime("%H:%M")

def get_calendar_service():
    creds = Credentials(**session['credentials'])
    return build('calendar', 'v3', credentials=creds)

def schedule_event(summary, start_time, end_time):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'}
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print("Event created:", event)
    return event


class Appointment(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    day = db.Column(db.String(200))
    date = db.Column(db.String(200))
    time = db.Column(db.String(200))
    Docid = db.Column(db.String(200))
    Status = db.Column(db.String(200))

    @classmethod
    def checkAvailability(cls, day, time):
        if time != "<-- Select Time Slot -->":
            avail = cls.query.filter_by(day=day, time=time, Status="Unbooked").all()
        else:
            avail = cls.query.filter_by(day=day, Status="Unbooked").all()
        return avail

    @classmethod
    def scheduleAppointment(cls, day, time):
        avail = cls.checkAvailability(day, time)
        return None if len(avail) == 0 else avail

    @classmethod
    def scheduleAppointments(cls, b_id, user_id, action):
        avail = Appointment.query.filter_by(id=b_id).first()
        stime = add_5_30_hrs(avail.time)
        start_dateTime = convert_to_iso_format(avail.date, stime)
        final_time = add_minutes_to_time(stime)
        end_dateTime = convert_to_iso_format(avail.date, final_time)
        event = schedule_event("Appointment", start_dateTime, end_dateTime)
        Physician.updateAppointment(user_id=user_id, avail=avail)
        Patient.userApp(doctor_id=avail.Docid, avail=avail)
        avail.Status = "Booked"
        db.session.commit()


class Patient(db.Model):
    app_id = db.Column(db.String(200), primary_key=True)
    doctor_id = db.Column(db.String(200))
    day = db.Column(db.String(200))
    date = db.Column(db.String(200))
    time = db.Column(db.String(200))

    @classmethod
    def userApp(cls, doctor_id, avail):
        # Create a new User_app record based on avail
        new_user_appointment = cls(
            app_id=avail.id,
            doctor_id=doctor_id,
            day=avail.day,
            date=avail.date,
            time=avail.time
        )
        db.session.add(new_user_appointment)
        db.session.commit()
        return new_user_appointment


class Physician(db.Model):
    app_id = db.Column(db.String(200), primary_key=True)
    doctor_id = db.Column(db.String(200))
    patient_id = db.Column(db.String(200))
    date = db.Column(db.String(200))
    time = db.Column(db.String(200))
    day = db.Column(db.String(200))

    @classmethod
    def updateAppointment(cls, user_id, avail):
        # Create a new User_app record based on avail
        new_user_appointment = cls(
            app_id=avail.id,
            doctor_id=avail.Docid,
            patient_id=user_id,
            day=avail.day,
            date=avail.date,
            time=avail.time
        )
        db.session.add(new_user_appointment)
        db.session.commit()
        return new_user_appointment
