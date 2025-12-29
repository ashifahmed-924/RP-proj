"""
Database connection module.
Handles MongoDB connection and provides database instance.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from config import get_config


class Database:
    """Singleton database connection handler."""
    
    _instance = None
    _client = None
    _db = None
    _connected = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establish connection to MongoDB."""
        if self._client is None:
            config = get_config()
            try:
                # Add connection timeout settings
                self._client = MongoClient(
                    config.MONGODB_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000
                )
                # Test connection
                self._client.admin.command('ping')
                self._db = self._client.get_database()
                self._create_indexes()
                self._connected = True
                print("[OK] Connected to MongoDB successfully!")
            except (ConnectionFailure, ConfigurationError) as e:
                print(f"[WARNING] MongoDB connection failed: {e}")
                print("[INFO] Running in offline mode - some features may not work")
                self._connected = False
                self._db = None
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                self._connected = False
                self._db = None
        return self._db
    
    def _create_indexes(self):
        """Create necessary indexes for collections."""
        if self._db is not None:
            try:
                self._db.users.create_index('email', unique=True)
            except Exception as e:
                print(f"[WARNING] Could not create indexes: {e}")
    
    def get_db(self):
        """Get the database instance."""
        if self._db is None and not self._connected:
            self.connect()
        return self._db
    
    def is_connected(self):
        """Check if database is connected."""
        return self._connected
    
    def close(self):
        """Close the database connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._connected = False


# Global database instance
db = Database()


def get_database():
    """Get the database instance."""
    return db.get_db()
