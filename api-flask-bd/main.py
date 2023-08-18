from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import app, db
from app.models import User
from geopy.distance import geodesic
from datetime import datetime
import threading
import folium
import json
import requests
import time


url = 'https://raw.githubusercontent.com/MatheusSantanaDev/TestWebRota/master/positions.json'

def calculate_total_distance(data):
    total_distance = 0
    
    for i in range(len(data) - 1):
        coord1 = (float(data[i]['latitude']), float(data[i]['longitude']))
        coord2 = (float(data[i + 1]['latitude']), float(data[i + 1]['longitude']))
        total_distance += geodesic(coord1, coord2).kilometers
    return total_distance

def create_map():
    response = requests.get(url)
    data = response.json()['data']

    m = folium.Map(location=[float(data[0]['latitude']), float(data[0]['longitude'])], zoom_start=10, tiles='OpenStreetMap')

    polygon_points = []
    for i, position in enumerate(data):
        lat, lon = float(position['latitude']), float(position['longitude'])
        
        total_distance = calculate_total_distance(data[:i + 1])
        
        popup_content = f'''
        <strong>Point {i + 1}</strong><br>
        Latitude: {lat}<br>
        Longitude: {lon}<br>
        Total Distance: {total_distance:.2f} km
        '''
        
        folium.Marker([lat, lon], popup=popup_content).add_to(m)
        polygon_points.append((lat, lon))

    folium.PolyLine(locations=polygon_points, color='blue').add_to(m)

    m.save('app/templates/map.html')
    print('Map created.')

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
    return render_template('dashboard.html')

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

        new_point = {
            "date_time": datetime.utcnow().isoformat(),
            "latitude": latitude,
            "longitude": longitude
        }
        
        try:
            with open('positions.json', 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {"data": []}

        data["data"].append(new_point)
        with open('positions.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print('New point added:', latitude, longitude)
        return redirect('/dashboard')
    return render_template('add_point.html')

def update_positions():
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            create_map()
            print('Positions updated.')
        time.sleep(300)

if __name__ == '__main__':
    update_positions_thread = threading.Thread(target=update_positions)
    update_positions_thread.start()
    app.run(debug=True)