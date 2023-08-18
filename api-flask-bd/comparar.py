import folium
import json
import requests
import time

# URL do JSON raw do repositório
url = 'https://raw.githubusercontent.com/MatheusSantanaDev/TestWebRota/master/positions.json'

def create_map():
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['data']

        m = folium.Map(location=[float(data[0]['latitude']), float(data[0]['longitude'])], zoom_start=10, tiles='OpenStreetMap')

        polygon_points = []
        for position in data:
            lat, lon = float(position['latitude']), float(position['longitude'])
            folium.Marker([lat, lon]).add_to(m)
            polygon_points.append((lat, lon))

        folium.PolyLine(locations=polygon_points, color='blue').add_to(m)

        m.save('templates/map.html')
        print('Map created.')

# Cria o mapa quando a aplicação é iniciada
create_map()

# Função para atualizar o mapa
def update_map():
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['data']

        # Criação do mapa com OpenStreetMap como camada base
        m = folium.Map(location=[float(data[0]['latitude']), float(data[0]['longitude'])], zoom_start=10, tiles='OpenStreetMap')

        # Adição de marcadores e criação do polígono
        polygon_points = []
        for position in data:
            lat, lon = float(position['latitude']), float(position['longitude'])
            folium.Marker([lat, lon]).add_to(m)
            polygon_points.append((lat, lon))

        folium.PolyLine(locations=polygon_points, color='blue').add_to(m)

        # Salvando o mapa como um arquivo HTML
        m.save('map.html')
        print('Map updated.')

# Atualizar o mapa a cada 5 minutos (300 segundos)
interval = 300
while True:
    update_map()
    time.sleep(interval)
