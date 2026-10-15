def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on the Earth specified by latitude and longitude.
    
    Parameters:
    lat1 (float): Latitude of the first point in decimal degrees.
    lon1 (float): Longitude of the first point in decimal degrees.
    lat2 (float): Latitude of the second point in decimal degrees.
    lon2 (float): Longitude of the second point in decimal degrees.
    
    Returns:
    float: Distance between the two points in kilometers.
    """
    from math import radians, sin, cos, sqrt, atan2
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    a = min(1.0, max(0.0, a))
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Radius of Earth in kilometers (mean radius)
    R = 6371.0
    distance = R * c
    
    return distance

def filter_zones_by_radius(zones, center_lat, center_lon, radius_km):
    """
    Filter zones based on their distance from a central point defined by latitude and longitude.
    
    Parameters:
    zones (list of dict): List of zones, each represented as a dictionary with 'latitude' and 'longitude' keys.
    center_lat (float): Latitude of the central point in decimal degrees.
    center_lon (float): Longitude of the central point in decimal degrees.
    radius_km (float): Radius in kilometers to filter zones.
    
    Returns:
    list of dict: List of zones that are within the specified radius from the central point.
    """
    filtered_zones = []
    
    for zone in zones:
        zone_lat = zone.get('latitude')
        zone_lon = zone.get('longitude')
        
        if zone_lat is not None and zone_lon is not None:
            distance = calculate_haversine_distance(center_lat, center_lon, zone_lat, zone_lon)
            if distance <= radius_km:
                filtered_zones.append(zone)
    
    return filtered_zones