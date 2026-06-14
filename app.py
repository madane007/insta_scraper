"""
Flask Application Setup
Main entry point for the Instagram Scraper API.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import DevelopmentConfig, ProductionConfig
from models import Database
import os
import logging

logger = logging.getLogger(__name__)


def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)

    # Load config
    if config is None:
        env = os.getenv('FLASK_ENV', 'development')
        config = ProductionConfig() if env == 'production' else DevelopmentConfig()

    app.config['SECRET_KEY'] = config.API_SECRET_KEY
    app.config['DEBUG'] = config.DEBUG

    # Enable CORS
    CORS(app, origins=config.API_CORS_ORIGINS)

    # Initialize database
    db = Database(db_url=config.SQLALCHEMY_DATABASE_URI)
    db.create_tables()
    app.db = db

    # Register blueprints
    from auth import auth_bp
    from routes import jobs_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')

    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'version': '0.1.0'})

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    logger.info("Flask app created successfully")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
