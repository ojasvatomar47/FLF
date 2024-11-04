# utils/matrix_factorization.py
from sklearn.decomposition import TruncatedSVD

def train_collaborative_filtering_model(user_item_matrix, n_components=2):
    # Initialize the SVD model
    svd = TruncatedSVD(n_components=n_components)
    
    # Fit the SVD model to the user-item matrix
    svd.fit(user_item_matrix)
    
    # Get the transformed matrix (approximate reconstruction of the user-item matrix)
    transformed_matrix = svd.inverse_transform(svd.transform(user_item_matrix))
    
    return transformed_matrix
