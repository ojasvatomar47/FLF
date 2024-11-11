# import osmnx as ox
# import networkx as nx
# from flask import jsonify, request
# from models.user import User  # Import the User model


# def calculate_route():
#     data = request.get_json()
    
#     # Coordinates of the two users (replace these with actual user coordinates)
#     origin = (data.get('origin_latitude'), data.get('origin_longitude'))
#     destination = (data.get('destination_latitude'), data.get('destination_longitude'))

#     if not origin or not destination:
#         return jsonify({"error": "Invalid coordinates provided"}), 400
    
#     # Load the graph for a larger area around the origin
#     G = ox.graph_from_point(origin, dist=5000, network_type='drive')  # Increase distance for a broader network

#     # Find the nearest nodes on the graph for the origin and destination
#     origin_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
#     destination_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

#     # Calculate the shortest path between the two nodes
#     try:
#         route = nx.shortest_path(G, origin_node, destination_node, weight='length')
#         # Get the coordinates of the route (latitude, longitude)
#         route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

#         return jsonify({'route': route_coords})
#     except nx.NetworkXNoPath:
#         return jsonify({"error": "No path found between the locations"}), 404
import osmnx as ox
import networkx as nx
from flask import jsonify, request
from models.user import User  # Import the User model
from geopy.distance import geodesic  # Import for distance calculations

def calculate_route():
    data = request.get_json()
    print(data)
    # Coordinates of the two users (replace these with actual user coordinates)
    origin = (data.get('origin_latitude'), data.get('origin_longitude'))
    destination = (data.get('destination_latitude'), data.get('destination_longitude'))

    if not origin or not destination:
        return jsonify({"error": "Invalid coordinates provided"}), 400
    
    # Load the graph for a larger area around the origin
    G = ox.graph_from_point(origin, dist=5000, network_type='drive')  # Increase distance for a broader network

    # Find the nearest nodes on the graph for the origin and destination
    origin_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
    destination_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

    # Calculate the shortest path between the two nodes
    try:
        route = nx.shortest_path(G, origin_node, destination_node, weight='length')
        # Get the coordinates of the route (latitude, longitude)
        route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

        # Helper function to find the optimal meeting point
        def find_optimal_meeting_point(route_coords):
            # Calculate cumulative distances along the route
            cumulative_distances = [0]
            for i in range(1, len(route_coords)):
                dist = geodesic(route_coords[i-1], route_coords[i]).meters
                cumulative_distances.append(cumulative_distances[-1] + dist)
            
            # Total route distance and halfway point
            total_distance = cumulative_distances[-1]
            half_distance = total_distance / 2
            
            # Find the waypoint closest to half the total distance
            for i, dist in enumerate(cumulative_distances):
                if dist >= half_distance:
                    return route_coords[i]  # Return the meeting point coordinates

        # Find the optimal meeting point along the route
        optimal_meeting_point = find_optimal_meeting_point(route_coords)

        return jsonify({
            'route': route_coords,
            'optimal_meeting_point': optimal_meeting_point
        })
    except nx.NetworkXNoPath:
        return jsonify({"error": "No path found between the locations"}), 404
