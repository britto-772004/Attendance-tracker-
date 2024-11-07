from flask import Flask, render_template, request ,redirect ,url_for, send_file,session, make_response
import sqlite3
from datetime import datetime
import subprocess 
from io import StringIO
import os
import csv

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/faculty_page')
def faculty_page():
    return render_template('faculty_page.html')

@app.route('/attendance_viewer')
def attendance_viewer():
    return render_template('index.html', selected_date='', no_data=False)

@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    starting_selected_time = request.form.get('starting_selected_time')
    ending_selected_time = request.form.get('ending_selected_time')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    starting_selected_time_obj = datetime.strptime(starting_selected_time, '%H:%M')
    ending_selected_time_obj = datetime.strptime(ending_selected_time, '%H:%M')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')
    starting_formatted_time = starting_selected_time_obj.strftime('%H:%M')
    ending_formatted_time = ending_selected_time_obj.strftime('%H:%M')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()
    datas = [atten for atten in attendance_data if (ending_formatted_time > atten[1] > starting_formatted_time)]
       

    seen_first_elements = {}

    unique_data = []

    for item in datas:
        first_element = item[0]
        if first_element not in seen_first_elements:
            unique_data.append(item)
            seen_first_elements[first_element] = True

    print(unique_data)
    data=[]
    data = unique_data
    conn.close()

    #if not unique_data:
     #   return render_template('index.html', selected_date=selected_date,selected_time=starting_selected_time , no_data=True)
    session['data'] = data
    return render_template('index.html', selected_date=selected_date,selected_time=starting_selected_time, data=data)


@app.route('/attendance_taker')
def attendance_taker():
    subprocess.run(['python3','attendance_taker.py'])
    return redirect(url_for('home'))

@app.route("/register_the_face")
def register_the_face():
    subprocess.run(['python3','get_faces_from_camera_tkinter.py'])
    subprocess.run(['python3','features_extraction_to_csv.py'])
    return redirect(url_for('home'))

def convert_to_csv(data):
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerows(data)
    return csv_data.getvalue()

@app.route("/download")
def download():
    data = session.get('data')
    csv_data = convert_to_csv(data)
    response = make_response(csv_data)

    # Set the appropriate headers
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    response.headers['Content-Type'] = 'text/csv'
    #return send_file(StringIO(csv_data),mimetype='text/csv',attachment_filename='data.csv',as_attachment=True)
    return response


if __name__ == '__main__':
    app.run(debug=True)
