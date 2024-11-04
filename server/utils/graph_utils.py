# utils/graph_utils.py
import matplotlib.pyplot as plt
import os
import numpy as np

def generate_order_count_graph(vegorders, veganorders, nonvegorders, ngo_ids):
    # Number of NGOs
    n = len(ngo_ids)
    
    # Set the bar width
    bar_width = 0.2
    
    # Create an array for the x locations of the bars
    index = np.arange(n)
    
    # Create the graph
    plt.figure(figsize=(10, 5))
    plt.bar(index, vegorders, bar_width, label='Vegetarian', color='green')
    plt.bar(index + bar_width, veganorders, bar_width, label='Vegan', color='orange')
    plt.bar(index + 2 * bar_width, nonvegorders, bar_width, label='Non-Vegetarian', color='red')
    
    # Labeling
    plt.xlabel('NGO IDs')
    plt.ylabel('Order Counts')
    plt.title('Order Counts per NGO by Food Type')
    plt.xticks(index + bar_width, ngo_ids, rotation=45)
    plt.legend()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.join('static', 'graphs'), exist_ok=True)

    # Save the graph as a PNG file
    graph_path = os.path.join('static', 'graphs', 'order_counts.png')
    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()  # Close the plot to free memory
    return graph_path
