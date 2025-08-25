import sqlite3
import logging
from datetime import datetime
import json
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="dragonrp.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    country_code TEXT UNIQUE NOT NULL,
                    country_name TEXT NOT NULL,
                    money INTEGER DEFAULT 100000,
                    population INTEGER DEFAULT 1000000,
                    soldiers INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Resources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resources (
                    user_id INTEGER PRIMARY KEY,
                    iron INTEGER DEFAULT 0,
                    copper INTEGER DEFAULT 0,
                    oil INTEGER DEFAULT 0,
                    gas INTEGER DEFAULT 0,
                    aluminum INTEGER DEFAULT 0,
                    gold INTEGER DEFAULT 0,
                    uranium INTEGER DEFAULT 0,
                    lithium INTEGER DEFAULT 0,
                    coal INTEGER DEFAULT 0,
                    silver INTEGER DEFAULT 0,
                    fuel INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            # Buildings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS buildings (
                    user_id INTEGER PRIMARY KEY,
                    iron_mine INTEGER DEFAULT 0,
                    copper_mine INTEGER DEFAULT 0,
                    oil_mine INTEGER DEFAULT 0,
                    gas_mine INTEGER DEFAULT 0,
                    aluminum_mine INTEGER DEFAULT 0,
                    gold_mine INTEGER DEFAULT 0,
                    uranium_mine INTEGER DEFAULT 0,
                    lithium_mine INTEGER DEFAULT 0,
                    coal_mine INTEGER DEFAULT 0,
                    silver_mine INTEGER DEFAULT 0,
                    weapon_factory INTEGER DEFAULT 0,
                    refinery INTEGER DEFAULT 0,
                    power_plant INTEGER DEFAULT 0,
                    wheat_farm INTEGER DEFAULT 0,
                    military_base INTEGER DEFAULT 0,
                    housing INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            # Weapons table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weapons (
                    user_id INTEGER PRIMARY KEY,
                    rifle INTEGER DEFAULT 0,
                    tank INTEGER DEFAULT 0,
                    fighter_jet INTEGER DEFAULT 0,
                    drone INTEGER DEFAULT 0,
                    missile INTEGER DEFAULT 0,
                    warship INTEGER DEFAULT 0,
                    air_defense INTEGER DEFAULT 0,
                    missile_shield INTEGER DEFAULT 0,
                    cyber_shield INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            # Wars table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attacker_id INTEGER NOT NULL,
                    defender_id INTEGER NOT NULL,
                    attack_power INTEGER NOT NULL,
                    defense_power INTEGER NOT NULL,
                    result TEXT NOT NULL,
                    damage_dealt INTEGER DEFAULT 0,
                    resources_stolen TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (attacker_id) REFERENCES players (user_id),
                    FOREIGN KEY (defender_id) REFERENCES players (user_id)
                )
            ''')
            
            # Convoys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS convoys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    resources TEXT NOT NULL,
                    departure_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    arrival_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'in_transit',
                    FOREIGN KEY (sender_id) REFERENCES players (user_id),
                    FOREIGN KEY (receiver_id) REFERENCES players (user_id)
                )
            ''')
            
            # Admin logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    target_id INTEGER,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def create_player(self, user_id, username, country_code):
        """Create a new player"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                country_name = Config.COUNTRIES.get(country_code, country_code)
                
                # Insert player
                cursor.execute('''
                    INSERT INTO players (user_id, username, country_code, country_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, country_code, country_name))
                
                # Initialize resources
                cursor.execute('''
                    INSERT INTO resources (user_id) VALUES (?)
                ''', (user_id,))
                
                # Initialize buildings
                cursor.execute('''
                    INSERT INTO buildings (user_id) VALUES (?)
                ''', (user_id,))
                
                # Initialize weapons
                cursor.execute('''
                    INSERT INTO weapons (user_id) VALUES (?)
                ''', (user_id,))
                
                conn.commit()
                logger.info(f"Player created: {username} - {country_name}")
                return True
                
        except sqlite3.IntegrityError:
            logger.error(f"Country {country_code} already taken")
            return False
        except Exception as e:
            logger.error(f"Error creating player: {e}")
            return False
    
    def get_player(self, user_id):
        """Get player information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_all_players(self):
        """Get all players"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players ORDER BY country_name')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_countries(self):
        """Get all countries with players"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username, country_name FROM players ORDER BY country_name')
            return [dict(row) for row in cursor.fetchall()]
    
    def is_country_taken(self, country_code):
        """Check if country is already taken"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM players WHERE country_code = ?', (country_code,))
            return cursor.fetchone() is not None
    
    def get_player_resources(self, user_id):
        """Get player resources"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM resources WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else {}
    
    def get_player_buildings(self, user_id):
        """Get player buildings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM buildings WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else {}
    
    def get_player_weapons(self, user_id):
        """Get player weapons"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM weapons WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else {}
    
    def update_player_money(self, user_id, new_money):
        """Update player money"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE players SET money = ? WHERE user_id = ?', (new_money, user_id))
            conn.commit()
    
    def update_player_income(self, user_id, money, population, soldiers):
        """Update player stats from income cycle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET money = ?, population = ?, soldiers = ?, last_active = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (money, population, soldiers, user_id))
            conn.commit()
    
    def add_building(self, user_id, building_type):
        """Add a building to player"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE buildings 
                SET {building_type} = {building_type} + 1 
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
    
    def add_weapon(self, user_id, weapon_type, quantity=1):
        """Add weapons to player"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE weapons 
                SET {weapon_type} = {weapon_type} + ? 
                WHERE user_id = ?
            ''', (quantity, user_id))
            conn.commit()
    
    def add_resources(self, user_id, resource_type, quantity):
        """Add resources to player"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE resources 
                SET {resource_type} = {resource_type} + ? 
                WHERE user_id = ?
            ''', (quantity, user_id))
            conn.commit()
    
    def consume_resources(self, user_id, resources_needed):
        """Consume resources from player"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if player has enough resources
            current_resources = self.get_player_resources(user_id)
            for resource, amount in resources_needed.items():
                if current_resources.get(resource, 0) < amount:
                    return False
            
            # Consume resources
            for resource, amount in resources_needed.items():
                cursor.execute(f'''
                    UPDATE resources 
                    SET {resource} = {resource} - ? 
                    WHERE user_id = ?
                ''', (amount, user_id))
            
            conn.commit()
            return True
    
    def log_admin_action(self, admin_id, action, target_id=None, details=None):
        """Log admin action"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO admin_logs (admin_id, action, target_id, details)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, action, target_id, details))
            conn.commit()
    
    def get_admin_logs(self, limit=50):
        """Get admin logs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM admin_logs 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_player(self, user_id):
        """Delete player and all related data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete from all tables
            cursor.execute('DELETE FROM players WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM resources WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM buildings WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM weapons WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM wars WHERE attacker_id = ? OR defender_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM convoys WHERE sender_id = ? OR receiver_id = ?', (user_id, user_id))
            
            conn.commit()
            return True
    
    def update_weapon_count(self, user_id, weapon_type, new_count):
        """Update weapon count"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE weapons 
                SET {weapon_type} = ? 
                WHERE user_id = ?
            ''', (new_count, user_id))
            conn.commit()
    
    def update_player_soldiers(self, user_id, new_soldiers):
        """Update player soldiers"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET soldiers = ? 
                WHERE user_id = ?
            ''', (new_soldiers, user_id))
            conn.commit()
    
    def reset_all_data(self):
        """Reset all game data (admin function)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Drop and recreate all game tables
            tables = ['players', 'resources', 'buildings', 'weapons', 'wars', 'convoys']
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS {table}')
            
            conn.commit()
            
        # Reinitialize database
        self.initialize()
        return True
