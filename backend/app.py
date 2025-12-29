"""
Main Application Module.

Entry point for the e-learning Flask application.
Configures the application and registers blueprints.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config
from database import db
from routes import account_bp, pmsas_bp


def create_app():
    """
    Application factory function.
    Creates and configures the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config['SECRET_KEY'] = config.JWT_SECRET_KEY
    app.config['DEBUG'] = config.DEBUG if hasattr(config, 'DEBUG') else False
    
    # Enable CORS for frontend communication
    # Allow all localhost ports for development
    CORS(app, 
         resources={r"/api/*": {
             "origins": ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }},
         supports_credentials=True
    )
    
    # Initialize database connection (lazy - won't fail if offline)
    try:
        db.connect()
    except Exception as e:
        print(f"[WARNING] Database connection deferred: {e}")
    
    # Register blueprints
    app.register_blueprint(account_bp)
    app.register_blueprint(pmsas_bp)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'service': 'e-learning-api'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


