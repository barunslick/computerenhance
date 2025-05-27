"""
Generator function that generates a random pair of longitude and latitude
to generate haversine distance between two points on the Earth.
{
    pairs: [
        { "x0": 12.34, "y0": 56.78, "x1": 23.45, "y1": 67.89, "distance": 1234.56 },
        { "x0": 34.56, "y0": 78.90, "x1": 45.67, "y1": 89.01, "distance": 2345.67 },
        ...
    ]
}

Use clustered approach so that when we generate large numbers of pairs, the average distance is different
"""

import json
import random
import math
import argparse


def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the haversine distance between two points on the earth.
    All angles are in degrees.
    
    Returns distance in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def generate_random_point(cluster_center: tuple = None, cluster_radius: float = None) -> tuple:
    """
    Generate a random point (longitude, latitude).
    If cluster_center is provided, the point will be within cluster_radius of the center.
    Otherwise, it will be a random point on Earth.
    
    Returns (longitude, latitude) tuple.
    """
    if cluster_center and cluster_radius:
        radius_in_radians = cluster_radius / 6371.0
        
        distance = random.random() * radius_in_radians
        
        angle = random.random() * 2 * math.pi
        
        center_lon_rad, center_lat_rad = map(math.radians, cluster_center)
        
        new_lat_rad = center_lat_rad + distance * math.cos(angle)
        new_lon_rad = center_lon_rad + distance * math.sin(angle) / math.cos(center_lat_rad)
        
        # Convert back to degrees and ensure within bounds
        new_lon = (math.degrees(new_lon_rad) + 180) % 360 - 180
        new_lat = max(min(math.degrees(new_lat_rad), 90), -90)
        
        return (new_lon, new_lat)
    else:
        lon = random.uniform(-180, 180)
        lat = random.uniform(-90, 90)
        return (lon, lat)


def generate_pairs_to_file(count: int, output_file: str, seed: int = None, num_clusters: int = 5) -> None:
    """
    Generate 'count' pairs of points and calculate their haversine distances.
    Uses a clustered approach for more interesting distributions.
    
    Writes results directly to the specified output file in JSON format.
    Also calculates and includes the average distance.
    """
    if seed is not None:
        random.seed(seed)
    
    clusters = []
    for _ in range(num_clusters):
        center = (random.uniform(-180, 180), random.uniform(-90, 90))
        radius = random.uniform(100, 3000)  # Cluster radius in km
        clusters.append((center, radius))
    
    total_distance = 0.0
    
    with open(output_file, 'w') as f:
        f.write('{\n  "pairs": [\n')
        
        for i in range(count):
            if random.random() < 0.7:  # 70% clustered, 30% random
                cluster = random.choice(clusters)
                
                point1 = generate_random_point(cluster[0], cluster[1])
                
                if random.random() < 0.5:  # 50% same cluster
                    point2 = generate_random_point(cluster[0], cluster[1])
                else:  # 50% different cluster
                    different_cluster = random.choice([c for c in clusters if c != cluster])
                    point2 = generate_random_point(different_cluster[0], different_cluster[1])
            else:
                point1 = generate_random_point()
                point2 = generate_random_point()
            
            lon1, lat1 = point1
            lon2, lat2 = point2
            distance = haversine_distance(lon1, lat1, lon2, lat2)
            
            total_distance += distance
            
            pair = {
                "x0": lon1,
                "y0": lat1,
                "x1": lon2,
                "y1": lat2,
                "distance": distance
            }
            
            f.write('    ' + json.dumps(pair))
            
            # Add comma if this is not the last pair
            if i < count - 1:
                f.write(',\n')
            else:
                f.write('\n')
        
        avg_distance = total_distance / count if count > 0 else 0
        
        f.write('  ],\n')
        f.write(f'  "average_distance": {avg_distance}\n}}')

        return avg_distance


def main():
    parser = argparse.ArgumentParser(description='Generate random coordinate pairs with haversine distances')
    parser.add_argument('--count', type=int, default=100, help='Number of pairs to generate')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--output', type=str, default='haversine_data.json', help='Output JSON file')
    
    args = parser.parse_args()
    
    avg_distance = generate_pairs_to_file(args.count, args.output, args.seed)
    
    print(f"Generated {args.count} pairs and saved to {args.output}")
    print(f"Seed: {args.seed if args.seed is not None else 'Random'}")
    print(f"Number of pairs: {args.count}")
    print(f"Average distance: {avg_distance:.2f} km")


if __name__ == "__main__":
    main()
