import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, mapping
import json

def read_gtfs_data(gtfs_folder):
    # Read necessary GTFS files into pandas DataFrames
    stops = pd.read_csv(os.path.join(gtfs_folder, 'stops.txt'))
    stop_times = pd.read_csv(os.path.join(gtfs_folder, 'stop_times.txt'))
    trips = pd.read_csv(os.path.join(gtfs_folder, 'trips.txt'))
    routes = pd.read_csv(os.path.join(gtfs_folder, 'routes.txt'))
    
    return stops, stop_times, trips, routes

def generate_geojson_per_route(gtfs_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    stops, stop_times, trips, routes = read_gtfs_data(gtfs_folder)
    
    # Merge data to get the full picture
    merged = (stop_times
              .merge(trips, on='trip_id')
              .merge(stops, on='stop_id'))
    
    # Group by route_id and sort by stop_sequence
    for route_id, group in merged.groupby('route_id'):
        group = group.sort_values('stop_sequence')
        
        # Create a LineString geometry for the route
        coords = group[['stop_lon', 'stop_lat']].values
        line = LineString(coords)
        
        # Find route information
        route_info = routes[routes['route_id'] == route_id].iloc[0]
        
        # Create a GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": mapping(line),
            "properties": {
                "route_id": route_id,
                "route_short_name": route_info.get('route_short_name', ''),
                "route_long_name": route_info.get('route_long_name', ''),
                "route_desc": route_info.get('route_desc', ''),
                "route_type": route_info.get('route_type', ''),
                "route_url": route_info.get('route_url', ''),
                "route_color": route_info.get('route_color', ''),
                "route_text_color": route_info.get('route_text_color', '')
            }
        }
        
        # Write the GeoJSON file
        geojson = {
            "type": "FeatureCollection",
            "features": [feature]
        }
        
        output_path = os.path.join(output_folder, f'route_{route_id}.geojson')
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=4)
        
        print(f'GeoJSON for route {route_id} saved to {output_path}')

if __name__ == '__main__':
    gtfs_folder = 'gtfs_datasets/export_lio'  # Replace with the path to your GTFS folder
    output_folder = 'geojson_files/'  # Replace with your desired output folder
    generate_geojson_per_route(gtfs_folder, output_folder)

