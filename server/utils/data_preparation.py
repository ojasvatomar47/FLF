import numpy as np
from models.user import User

def create_user_item_matrix():
    # Fetch all NGOs
    ngos = User.objects(user_type="Charity/NGO")
    
    # Initialize lists to store NGO IDs and order counts
    ngo_ids = []
    order_counts = []

    # Loop over each NGO and get their food type order counts, defaulting to 0 if not present
    for ngo in ngos:
        ngo_ids.append(str(ngo.id))
        order_counts.append([
            getattr(ngo, 'vegorders', 0),
            getattr(ngo, 'veganorders', 0),
            getattr(ngo, 'nonvegorders', 0)
        ])
    
    # Convert lists to a numpy array (user-item matrix)
    user_item_matrix = np.array(order_counts)
    return user_item_matrix, ngo_ids
