import folium
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from shapely.geometry import Point, Polygon

m = folium.Map(tiles="cartodb positron")

# Load the lists of the coordinates of the polygons that defines the border of each country, approximately
polygon_list = []
with open('country_data.geojson', 'r') as read_file:
    data = json.load(read_file)
    for i in range(241):
        geometry = data['features'][i]['geometry']
        coords = geometry['coordinates']
        if geometry['type'] == 'Polygon':
            point_list = []
            for x1 in coords:
                for x2 in x1:
                    point_list.append((x2[1], x2[0]))
            polygon_list.append(Polygon(point_list))
        elif geometry['type'] == 'MultiPolygon':
            for x3 in coords:
                point_list = []
                for x1 in x3:
                    for x2 in x1:
                        point_list.append((x2[1], x2[0]))
                polygon_list.append(Polygon(point_list))
        else:
            raise ValueError(f'type {geometry["type"]}not known')

def is_land(point:Point):
    '''
    This function checks if a given point is contained in any of the polygon in polygon_list, the same as whether it is a point on land or not
    '''
    for polygon in polygon_list:
        if point.within(polygon):
            return True
    return False

M = 100000 # The approximate number of points generated, the actual number will be less because of flooring when calculating the frequency according to the weights

# Generate random latitudes with different weights for each 10-degree interval using area ratio
# Each of those intervals will have a fixed number of random points generated inside it, contained in the frequency array
interval_weights = (np.sin(np.arange(-80, 100, 10)*np.pi/180) - np.sin(np.arange(-90, 90, 10)*np.pi/180))/2
frequency = np.floor(M*interval_weights).astype(int)
N = np.sum(frequency) # The real number of random points generated
print(f'N = {N}')
lat = np.random.uniform(low=-90, high=-80, size=(frequency[0],))
for i in range(1, 18):
    lat = np.concatenate((lat, np.random.uniform(low=10*i-90, high=10*i-80, size=frequency[i])))

# Generate random uniform longitudes
long = np.random.uniform(low=-180, high=180, size=(N,))

def plot_earth():
    '''
    This function plots a 3D sphere representation of Earth, marking all the random points generated above with the color that defines whether it is land or not
    '''
    land_lat = []
    land_long = []
    water_lat = []
    water_long = []
    for i in range(N):
        if is_land(Point(lat[i], long[i])):
            land_lat.append(lat[i])
            land_long.append(long[i])
        else:
            water_lat.append(lat[i])
            water_long.append(long[i])
        if i%10000==0:
            print(f"Currently processing point at index #{i}")
    land_lat = np.array(land_lat)*np.pi/180
    land_long = np.array(land_long)*np.pi/180
    water_lat = np.array(water_lat)*np.pi/180
    water_long = np.array(water_long)*np.pi/180
    # Convert latitudes and longitudes to Cartesian coordinates
    # Earth is mapped to a sphere centered at (0, 0, 0) and has a radius of 1, the Equator is on the xy-plane
    land_x, land_y = np.multiply(np.cos(land_lat),np.cos(land_long)), np.multiply(np.cos(land_lat), np.sin(land_long))
    water_x, water_y = np.multiply(np.cos(water_lat),np.cos(water_long)), np.multiply(np.cos(water_lat), np.sin(water_long))
    land_z, water_z = np.sin(land_lat), np.sin(water_lat)
    # Create a matplotlib figure
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(land_x, land_y, land_z, c="red")
    ax.scatter(water_x, water_y, water_z, c="blue")
    # Define sphere parameters for the black background of the Earth
    radius = 0.98
    theta = np.linspace(0, 2.*np.pi, 100)
    phi = np.linspace(0, np.pi, 100)
    x = radius * np.outer(np.cos(theta), np.sin(phi))
    y = radius * np.outer(np.sin(theta), np.sin(phi))
    z = radius * np.outer(np.ones(np.size(theta)), np.cos(phi))
    ax.plot_surface(x, y, z, color='black')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect([1,1,1])
    plt.show()

# plot_earth()

#Calculating the ratio and save the map in an html file
count_land = 0
for i in range(N):
    point = Point(lat[i], long[i])
    if is_land(point):
        count_land+=1
        folium.CircleMarker(location=[point.x, point.y], radius=1, color='#0000ff').add_to(m)
    else:
        folium.CircleMarker(location=[point.x, point.y], radius=1, color='#ff0000').add_to(m)
    if i%10000==0:
        print(f'Currently marking point at index #{i}')
print(count_land/N)
m.save('Land_and_Water_on_Earth.html')


