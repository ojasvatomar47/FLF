# utils/matrix_factorization.py
import numpy as np

def svd_scratch(matrix, n_components=2, n_iter=100):
    """
    Perform SVD from scratch to approximate the user-item matrix.
    
    Parameters:
        matrix (numpy array): The user-item matrix.
        n_components (int): Number of singular values/vectors to keep.
        n_iter (int): Number of iterations for power method.
        
    Returns:
        numpy array: Approximate reconstruction of the user-item matrix.
    """
    m, n = matrix.shape
    U = np.zeros((m, n_components))
    S = np.zeros((n_components,))
    V = np.zeros((n_components, n))
    
    # Iteratively approximate singular values/vectors
    for i in range(n_components):
        # Random initialization for power iteration
        vec = np.random.rand(n)
        
        for _ in range(n_iter):
            # Apply matrix operations for power method
            vec = matrix.T @ (matrix @ vec)
            vec /= np.linalg.norm(vec)
        
        # Singular value and corresponding singular vectors
        sigma = np.linalg.norm(matrix @ vec)
        U[:, i] = (matrix @ vec) / sigma
        S[i] = sigma
        V[i, :] = vec
    
    # Reconstruct the matrix using the top n_components
    reconstructed_matrix = U @ np.diag(S) @ V
    
    return reconstructed_matrix

def train_collaborative_filtering_model(user_item_matrix, n_components=2):
    """
    Train a collaborative filtering model from scratch using SVD.
    
    Parameters:
        user_item_matrix (numpy array): The user-item matrix.
        n_components (int): Number of components (latent factors) to retain.
        
    Returns:
        numpy array: Approximate reconstruction of the user-item matrix.
    """
    # Perform SVD from scratch
    transformed_matrix = svd_scratch(user_item_matrix, n_components=n_components)
    return transformed_matrix
