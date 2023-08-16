from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import app, db
from app.models import User
from geopy.distance import geodesic
from datetime import datetime
import threading
import folium
import requests
import time


url = 'https://raw.githubusercontent.com/MatheusSantanaDev/TestWebRota/master/positions.json'

def create_map(data):
    m = folium.Map(location=[float(data[0]['latitude']), float(data[0]['longitude'])], zoom_start=10, tiles='OpenStreetMap')

    polygon_points = []
    for position in data:
        lat, lon = float(position['latitude']), float(position['longitude'])
        folium.Marker([lat, lon]).add_to(m)
        polygon_points.append((lat, lon))

    folium.PolyLine(locations=polygon_points, color='blue').add_to(m)

    m.save('app/templates/map.html')
    print('Map created.')

def calculate_total_distance(data):
    total_distance = 0
    for i in range(len(data) - 1):
        coord1 = (float(data[i]['latitude']), float(data[i]['longitude']))
        coord2 = (float(data[i + 1]['latitude']), float(data[i + 1]['longitude']))
        total_distance += geodesic(coord1, coord2).kilometers
    return total_distance

def update_positions():
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            create_map(data)
            print('Positions updated.')
        time.sleep(300)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pwd = request.form['password']

        user = User(name, email, pwd)
        db.session.add(user)
        db.session.commit()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']

        if not email or not pwd:
            flash('Both email and password are required.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.verify_password(pwd):
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', total_distance=calculate_total_distance(requests.get(url).json()['data']))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/view_map')
@login_required
def view_map():
    return render_template('map.html')

@app.route('/add_point', methods=['GET', 'POST'])
@login_required
def add_point():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            new_point = {
                "date_time": datetime.utcnow().isoformat(),
                "latitude": latitude,
                "longitude": longitude
            }
            data['data'].append(new_point)

            response = requests.put(url, json=data)
            if response.status_code == 200:
                print('New point added:', latitude, longitude)
                create_map(data)
        return redirect('/dashboard')

    return render_template('add_point.html')

if __name__ == '__main__':
    update_positions_thread = threading.Thread(target=update_positions)
    update_positions_thread.start()
    app.run(debug=True)