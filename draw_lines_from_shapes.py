import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import json

path_to_gtfs_folder='gtfs_datasets'
path_for_generated_geojson='geojson_files'

# Load shapes.txt and routes.txt into pandas DataFrames
shapes_df = pd.read_csv(path_to_gtfs_folder+'/shapes.txt')
routes_df = pd.read_csv(path_to_gtfs_folder+'/routes.txt')

# Merge shapes with routes to get route names
merged_df = shapes_df.merge(routes_df, left_on='shape_id', right_on='route_id')

# Group merged data by shape_id
grouped_shapes = merged_df.groupby('shape_id')

# Iterate over each shape
for shape_id, group in grouped_shapes:
    # Extract latitude and longitude coordinates
    coordinates = [(row['shape_pt_lon'], row['shape_pt_lat']) for _, row in group.iterrows()]
    
    # Create LineString geometry
    shape_line = LineString(coordinates)
    
    # Get the route name
    route_name = group['route_short_name'].iloc[0]  # Assuming route_short_name is the desired name property
    
    # Convert LineString to GeoJSON format with properties
    shape_geojson = {
        "type": "Feature",
        "geometry": shape_line.__geo_interface__,
        "properties": {
            "name": route_name
        }
    }

    # Write shape GeoJSON to file
    with open(f"{path_for_generated_geojson}/shape_{shape_id}.geojson", "w") as outfile:
        json.dump(shape_geojson, outfile)

