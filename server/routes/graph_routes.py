from flask import Blueprint, send_from_directory
from controllers.recommendation_ml import get_order_counts_graph

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/graphs/order_counts', methods=['GET'])
def order_counts_graph():
    graph_path = get_order_counts_graph()
    return send_from_directory('static/graphs', 'order_counts.png')
