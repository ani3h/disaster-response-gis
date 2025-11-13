"""
Main Flask Application Entry Point
===================================
This file initializes the Flask app, registers API blueprints,
configures CORS, and sets up error handlers.
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import config

# Import API blueprints
from backend.api.disaster_api import disaster_bp
from backend.api.routes_api import routes_bp
from backend.api.shelters_api import shelters_bp
from backend.api.layers_api import layers_bp

# Import database connection for initialization
from backend.db.db_connection import init_db, test_connection


def create_app():
    """
    Application factory function
    Creates and configures the Flask application

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__,
                template_folder='frontend/templates',
                static_folder='frontend/static')

    # Load configuration
    app.config.from_object(config)

    # Enable CORS for all routes (adjust origins for production)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize database connection
    with app.app_context():
        init_db()
        test_connection()

    # Register API blueprints
    app.register_blueprint(disaster_bp, url_prefix='/api/disaster')
    app.register_blueprint(routes_bp, url_prefix='/api/routes')
    app.register_blueprint(shelters_bp, url_prefix='/api/shelters')
    app.register_blueprint(layers_bp, url_prefix='/api/layers')

    # Main route - serve the frontend
    @app.route('/')
    def index():
        """Serve the main dashboard page"""
        return render_template('index.html')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """API health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Disaster Response GIS API',
            'version': '1.0.0'
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid request parameters'
        }), 400

    return app


if __name__ == '__main__':
    # Create the application
    app = create_app()

    # Run the development server
    # NOTE: In production, use a WSGI server like Gunicorn
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
