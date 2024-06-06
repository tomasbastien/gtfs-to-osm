import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json

path_to_gtfs_folder='gtfs_datasets/'
path_for_generated_geojson='geojson_files/'

# Load GTFS files into pandas DataFrames
stops_df = pd.read_csv(path_to_gtfs_folder+'stops.txt')
routes_df = pd.read_csv(path_to_gtfs_folder+'routes.txt')
stop_times_df = pd.read_csv(path_to_gtfs_folder+'stop_times.txt')
trips_df = pd.read_csv(path_to_gtfs_folder+'trips.txt')

# Merge relevant data
merged_df = stop_times_df.merge(trips_df, on='trip_id').merge(routes_df, on='route_id').merge(stops_df, on='stop_id')

# Group merged data by route_id
grouped_routes = merged_df.groupby('route_id')

# Iterate over each route
for route_id, group in grouped_routes:
    # Create GeoDataFrame for the route's stops
    geometry = [Point(xy) for xy in zip(group['stop_lon'], group['stop_lat'])]
    route_stops_gdf = gpd.GeoDataFrame(group, geometry=geometry, crs="EPSG:4326")

    # Convert GeoDataFrame to GeoJSON format
    route_stops_geojson = route_stops_gdf[['stop_id', 'stop_name', 'geometry']].to_json()

    # Write stops GeoJSON to file
    with open(f"{path_for_generated_geojson}route_{route_id}_stops.geojson", "w") as outfile:
        outfile.write(route_stops_geojson)

