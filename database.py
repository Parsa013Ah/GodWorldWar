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
                    nitro INTEGER DEFAULT 0,
                    sulfur INTEGER DEFAULT 0,
                    titanium INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')

            # Add new resource columns if they don't exist
            try:
                cursor.execute('ALTER TABLE resources ADD COLUMN nitro INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass  # Column already exists

            try:
                cursor.execute('ALTER TABLE resources ADD COLUMN sulfur INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass  # Column already exists

            try:
                cursor.execute('ALTER TABLE resources ADD COLUMN titanium INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass  # Column already exists

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
                    nitro_mine INTEGER DEFAULT 0,
                    sulfur_mine INTEGER DEFAULT 0,
                    titanium_mine INTEGER DEFAULT 0,
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
                    jet INTEGER DEFAULT 0,
                    drone INTEGER DEFAULT 0,
                    warship INTEGER DEFAULT 0,
                    submarine INTEGER DEFAULT 0,
                    destroyer INTEGER DEFAULT 0,
                    aircraft_carrier INTEGER DEFAULT 0,
                    air_defense INTEGER DEFAULT 0,
                    missile_shield INTEGER DEFAULT 0,
                    cyber_shield INTEGER DEFAULT 0,
                    simple_bomb INTEGER DEFAULT 0,
                    nuclear_bomb INTEGER DEFAULT 0,
                    simple_missile INTEGER DEFAULT 0,
                    ballistic_missile INTEGER DEFAULT 0,
                    nuclear_missile INTEGER DEFAULT 0,
                    trident2_conventional INTEGER DEFAULT 0,
                    trident2_nuclear INTEGER DEFAULT 0,
                    satan2_conventional INTEGER DEFAULT 0,
                    satan2_nuclear INTEGER DEFAULT 0,
                    df41_nuclear INTEGER DEFAULT 0,
                    tomahawk_conventional INTEGER DEFAULT 0,
                    tomahawk_nuclear INTEGER DEFAULT 0,
                    kalibr_conventional INTEGER DEFAULT 0,
                    f22 INTEGER DEFAULT 0,
                    f35 INTEGER DEFAULT 0,
                    su57 INTEGER DEFAULT 0,
                    j20 INTEGER DEFAULT 0,
                    f15ex INTEGER DEFAULT 0,
                    su35s INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')

            # Add new weapon columns if they don't exist
            new_weapon_columns = [
                'helicopter', 'strategic_bomber',
                'jet', 'submarine', 'destroyer', 'aircraft_carrier',
                'simple_bomb', 'nuclear_bomb', 'simple_missile', 'ballistic_missile', 'nuclear_missile',
                'trident2_conventional', 'trident2_nuclear', 'satan2_conventional', 'satan2_nuclear',
                'df41_nuclear', 'tomahawk_conventional', 'tomahawk_nuclear', 'kalibr_conventional',
                'f22', 'f35', 'su57', 'j20', 'f15ex', 'su35s',
                'armored_truck', 'cargo_helicopter', 'cargo_plane', 'escort_frigate',
                'logistics_drone', 'heavy_transport', 'supply_ship', 'stealth_transport',
                # New tanks
                'kf51_panther', 'abrams_x', 'm1e3_abrams', 't90ms_proryv', 'm1a2_abrams_sepv3',
                # New defense systems
                's500_defense', 'thaad_defense', 's400_defense', 'iron_dome', 'slq32_ew', 'phalanx_ciws',
                # New naval weapons
                'aircraft_carrier_full', 'warship', 'nuclear_submarine', 'patrol_ship', 'patrol_boat', 'amphibious_ship'
            ]

            for column in new_weapon_columns:
                try:
                    cursor.execute(f'ALTER TABLE weapons ADD COLUMN {column} INTEGER DEFAULT 0')
                except sqlite3.OperationalError:
                    pass  # Column already exists

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
                    security_level INTEGER DEFAULT 50,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES players (user_id),
                    FOREIGN KEY (receiver_id) REFERENCES players (user_id)
                )
            ''')

            # Add security_level column if it doesn't exist
            try:
                cursor.execute('ALTER TABLE convoys ADD COLUMN security_level INTEGER DEFAULT 50')
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Add created_at column if it doesn't exist
            try:
                cursor.execute('ALTER TABLE convoys ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Pending attacks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_attacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attacker_id INTEGER NOT NULL,
                    defender_id INTEGER NOT NULL,
                    attack_type TEXT DEFAULT 'mixed',
                    travel_time INTEGER NOT NULL,
                    departure_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    attack_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'traveling',
                    FOREIGN KEY (attacker_id) REFERENCES players (user_id),
                    FOREIGN KEY (defender_id) REFERENCES players (user_id)
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

            # Marketplace listings
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES players (user_id)
            )
            """)

            # Market transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id INTEGER NOT NULL,
                    buyer_id INTEGER NOT NULL,
                    seller_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_paid INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_date TIMESTAMP,
                    FOREIGN KEY (listing_id) REFERENCES market_listings (id),
                    FOREIGN KEY (buyer_id) REFERENCES players (user_id),
                    FOREIGN KEY (seller_id) REFERENCES players (user_id)
                )
            ''')

            # Purchase tracking table for preventing duplicate news
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchase_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    buyer_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    first_purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(buyer_id, item_type),
                    FOREIGN KEY (buyer_id) REFERENCES players (user_id)
                )
            ''')

            # Build tracking table for preventing duplicate news
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS build_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    builder_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    first_build_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(builder_id, item_type),
                    FOREIGN KEY (builder_id) REFERENCES players (user_id)
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

    def set_player_building(self, user_id, building_type, count):
        """Set player building count to specific value"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE buildings 
                    SET {building_type} = ?
                    WHERE user_id = ?
                ''', (count, user_id))
                conn.commit()
                logger.info(f"Set {building_type} to {count} for player {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error setting building count: {e}")
            return False

    def update_player_income(self, user_id, new_money, new_population, new_soldiers):
        """Update player money, population, and soldiers (for income cycle)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE players 
                    SET money = ?, population = ?, soldiers = ?
                    WHERE user_id = ?
                ''', (new_money, new_population, new_soldiers, user_id))
                conn.commit()
                logger.info(f"Updated income for player {user_id}: ${new_money:,}, population: {new_population:,}, soldiers: {new_soldiers:,}")
                return True
        except Exception as e:
            logger.error(f"Error updating player income: {e}")
            return False

    def get_all_countries(self):
        """Get all countries with players"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username, country_name, country_code FROM players ORDER BY country_name')
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

    def update_player_money(self, user_id, new_amount):
        """Update player money"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE players SET money = ? WHERE user_id = ?
                """, (new_amount, user_id))
                conn.commit()
                logger.info(f"Updated player {user_id} money to {new_amount}")
                return True
        except Exception as e:
            logger.error(f"Error updating player money: {e}")
            return False

    def update_player_population(self, user_id, new_population):
        """Update player population"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE players SET population = ? WHERE user_id = ?",
                    (new_population, user_id)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating player population: {e}")
            return False

    def update_player_soldiers(self, user_id, new_soldiers):
        """Update player's soldiers count"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET soldiers = ?
                WHERE user_id = ?
            ''', (new_soldiers, user_id))
            conn.commit()
            cursor.close()

    def update_resource(self, user_id, resource_type, new_amount):
        """Update specific resource amount"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE resources 
                SET {resource_type} = ?
                WHERE user_id = ?
            ''', (new_amount, user_id))
            conn.commit()
            cursor.close()

    def update_building_count(self, user_id, building_type, new_count):
        """Update building count"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE buildings 
                SET {building_type} = ?
                WHERE user_id = ?
            ''', (new_count, user_id))
            conn.commit()
            cursor.close()

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
            cursor.close()

    def add_weapon(self, user_id, weapon_type, quantity=1):
        """Add weapons to player"""
        logger.info(f"add_weapon called: user_id={user_id}, weapon_type={weapon_type}, quantity={quantity}")
        
        # Map weapon names to database column names
        weapon_column_map = {
            'rifle': 'rifle',
            'tank': 'tank',
            'fighter': 'fighter_jet',
            'fighter_jet': 'fighter_jet',
            'helicopter': 'helicopter',
            'jet': 'jet',
            'drone': 'drone',
            'strategic_bomber': 'strategic_bomber',
            'warship': 'warship',
            'submarine': 'submarine',
            'destroyer': 'destroyer',
            'aircraft_carrier': 'aircraft_carrier',
            'aircraft_carrier_full': 'aircraft_carrier_full',
            'nuclear_submarine': 'nuclear_submarine',
            'patrol_ship': 'patrol_ship',
            'patrol_boat': 'patrol_boat',
            'amphibious_ship': 'amphibious_ship',
            'air_defense': 'air_defense',
            'missile_shield': 'missile_shield',
            'cyber_shield': 'cyber_shield',
            's500_defense': 's500_defense',
            'thaad_defense': 'thaad_defense',
            's400_defense': 's400_defense',
            'iron_dome': 'iron_dome',
            'slq32_ew': 'slq32_ew',
            'phalanx_ciws': 'phalanx_ciws',
            'simple_bomb': 'simple_bomb',
            'nuclear_bomb': 'nuclear_bomb',
            'simple_missile': 'simple_missile',
            'ballistic_missile': 'ballistic_missile',
            'nuclear_missile': 'nuclear_missile',
            'trident2_conventional': 'trident2_conventional',
            'trident2_nuclear': 'trident2_nuclear',
            'satan2_conventional': 'satan2_conventional',
            'satan2_nuclear': 'satan2_nuclear',
            'df41_nuclear': 'df41_nuclear',
            'tomahawk_conventional': 'tomahawk_conventional',
            'tomahawk_nuclear': 'tomahawk_nuclear',
            'kalibr_conventional': 'kalibr_conventional',
            'f22': 'f22',
            'f35': 'f35',
            'su57': 'su57',
            'j20': 'j20',
            'f15ex': 'f15ex',
            'su35s': 'su35s',
            'kf51_panther': 'kf51_panther',
            'abrams_x': 'abrams_x',
            'm1e3_abrams': 'm1e3_abrams',
            't90ms_proryv': 't90ms_proryv',
            'm1a2_abrams_sepv3': 'm1a2_abrams_sepv3',
            'armored_truck': 'armored_truck',
            'cargo_helicopter': 'cargo_helicopter',
            'cargo_plane': 'cargo_plane',
            'escort_frigate': 'escort_frigate',
            'logistics_drone': 'logistics_drone',
            'heavy_transport': 'heavy_transport',
            'supply_ship': 'supply_ship',
            'stealth_transport': 'stealth_transport'
        }

        column_name = weapon_column_map.get(weapon_type, weapon_type)
        logger.info(f"Mapped weapon_type '{weapon_type}' to column '{column_name}'")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists in weapons table
            cursor.execute('SELECT COUNT(*) FROM weapons WHERE user_id = ?', (user_id,))
            user_exists = cursor.fetchone()[0] > 0
            logger.info(f"User {user_id} exists in weapons table: {user_exists}")
            
            if not user_exists:
                logger.info(f"Creating weapons entry for user {user_id}")
                # Create a new weapons entry for this user
                cursor.execute('INSERT INTO weapons (user_id) VALUES (?)', (user_id,))
            
            # Check current value before update
            cursor.execute(f'SELECT {column_name} FROM weapons WHERE user_id = ?', (user_id,))
            current_value = cursor.fetchone()
            if current_value:
                current_value = current_value[0] or 0
            else:
                current_value = 0
            logger.info(f"Current {column_name} value for user {user_id}: {current_value}")
            
            # Update weapons
            cursor.execute(f'''
                UPDATE weapons 
                SET {column_name} = {column_name} + ? 
                WHERE user_id = ?
            ''', (quantity, user_id))
            
            # Check after update
            cursor.execute(f'SELECT {column_name} FROM weapons WHERE user_id = ?', (user_id,))
            new_value = cursor.fetchone()
            if new_value:
                new_value = new_value[0] or 0
            else:
                new_value = 0
            logger.info(f"New {column_name} value for user {user_id}: {new_value}")
            
            conn.commit()
            cursor.close()

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
            cursor.close()

    def subtract_resources(self, user_id, resource_type, quantity):
        """Subtract resources from player"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE resources 
                SET {resource_type} = {resource_type} - ? 
                WHERE user_id = ?
            ''', (quantity, user_id))
            conn.commit()
            cursor.close()

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
            cursor.close()
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
            cursor.close()

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
            cursor.execute('DELETE FROM marketplace_listings WHERE seller_id = ?', (user_id,))
            cursor.execute('DELETE FROM market_transactions WHERE buyer_id = ? OR seller_id = ?', (user_id, user_id))

            conn.commit()
            cursor.close()
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
            cursor.close()

    def get_weapon_count(self, user_id, weapon_type):
        """Get specific weapon count"""
        weapons = self.get_player_weapons(user_id)
        return weapons.get(weapon_type, 0)

    def get_active_convoys(self):
        """Get all active convoys in transit"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.*, 
                       s.country_name as sender_country,
                       r.country_name as receiver_country
                FROM convoys c
                JOIN players s ON c.sender_id = s.user_id
                JOIN players r ON c.receiver_id = r.user_id
                WHERE c.status = 'in_transit'
                AND c.arrival_time > datetime('now')
                ORDER BY c.created_at DESC
            ''')
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results] if results else []

    def create_convoy(self, sender_id, receiver_id, resources, travel_minutes=30, security_level=50):
        """Create a new convoy"""
        import json
        from datetime import datetime, timedelta

        arrival_time = datetime.now() + timedelta(minutes=travel_minutes)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO convoys (sender_id, receiver_id, resources, arrival_time, security_level, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'in_transit', datetime('now'))
            ''', (sender_id, receiver_id, json.dumps(resources), arrival_time.isoformat(), security_level))

            convoy_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            return convoy_id

    def get_convoy(self, convoy_id):
        """Get convoy details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM convoys WHERE id = ?', (convoy_id,))
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None

    def update_convoy_status(self, convoy_id, new_status):
        """Update convoy status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE convoys SET status = ? WHERE id = ?', (new_status, convoy_id))
            conn.commit()
            cursor.close()

    def update_convoy_arrival(self, convoy_id, new_arrival_time, new_status):
        """Update convoy arrival time and status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE convoys 
                SET arrival_time = ?, status = ? 
                WHERE id = ?
            ''', (new_arrival_time, new_status, convoy_id))
            conn.commit()
            cursor.close()

    def update_convoy_security(self, convoy_id, new_security_level):
        """Update convoy security level"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE convoys 
                SET security_level = ? 
                WHERE id = ?
            ''', (new_security_level, convoy_id))
            conn.commit()
            cursor.close()

    def get_arrived_convoys(self):
        """Get all convoys that have arrived at their destination"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.*, 
                       s.country_name as sender_country,
                       r.country_name as receiver_country
                FROM convoys c
                JOIN players s ON c.sender_id = s.user_id
                JOIN players r ON c.receiver_id = r.user_id
                WHERE c.status = 'in_transit'
                AND c.arrival_time <= datetime('now')
                ORDER BY c.arrival_time ASC
            ''')
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results] if results else []

    def create_pending_attack(self, attack_data):
        """Create a new pending attack"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pending_attacks (attacker_id, defender_id, attack_type, travel_time, attack_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                attack_data['attacker_id'],
                attack_data['defender_id'], 
                attack_data['attack_type'],
                attack_data['travel_time'],
                attack_data['attack_time'],
                attack_data['status']
            ))
            conn.commit()
            cursor.close()
            return cursor.lastrowid

    def get_pending_attack(self, attack_id):
        """Get pending attack details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pending_attacks WHERE id = ?', (attack_id,))
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None

    def get_pending_attacks_due(self):
        """Get all pending attacks that are due for execution"""
        from datetime import datetime
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            cursor.execute('''
                SELECT * FROM pending_attacks 
                WHERE attack_time <= ? AND status = 'traveling'
            ''', (current_time,))
            return [dict(row) for row in cursor.fetchall()]

    def update_pending_attack_status(self, attack_id, new_status):
        """Update pending attack status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE pending_attacks SET status = ? WHERE id = ?', (new_status, attack_id))
            conn.commit()
            cursor.close()

    def reset_all_data(self):
        """Reset all game data (admin function)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Drop and recreate all game tables
            tables = ['players', 'resources', 'buildings', 'weapons', 'wars', 'convoys', 'pending_attacks', 
                     'alliances', 'alliance_members', 'alliance_invitations',
                     'market_listings', 'market_transactions', 'purchase_tracking']
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS {table}')

            conn.commit()
            cursor.close()

        # Reinitialize database
        self.initialize()
        return True

    def check_first_purchase(self, user_id, item_type):
        """Check if this is user's first purchase of this item type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM purchase_tracking WHERE buyer_id = ? AND item_type = ?',
                (user_id, item_type)
            )
            return cursor.fetchone() is None

    def record_first_purchase(self, user_id, item_type):
        """Record first purchase of an item type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO purchase_tracking (buyer_id, item_type)
                VALUES (?, ?)
            ''', (user_id, item_type))
            conn.commit()
            cursor.close()

    def check_first_build(self, user_id, item_type):
        """Check if this is user's first build of this item type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM build_tracking WHERE builder_id = ? AND item_type = ?',
                (user_id, item_type)
            )
            return cursor.fetchone() is None

    def record_first_build(self, user_id, item_type):
        """Record first build of an item type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO build_tracking (builder_id, item_type)
                VALUES (?, ?)
            ''', (user_id, item_type))
            conn.commit()
            cursor.close()

    def give_infinite_resources_to_all_players(self):
        """Give infinite money and resources to all players for testing"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Give 1 billion money to all players
                cursor.execute("UPDATE players SET money = 1000000000, population = 50000000, soldiers = 10000000")
                
                # Give massive resources to all players
                cursor.execute("""
                    UPDATE resources SET 
                    iron = 1000000,
                    copper = 1000000,
                    oil = 1000000,
                    gas = 1000000,
                    aluminum = 1000000,
                    gold = 1000000,
                    uranium = 1000000,
                    lithium = 1000000,
                    coal = 1000000,
                    silver = 1000000,
                    fuel = 1000000,
                    nitro = 1000000,
                    sulfur = 1000000,
                    titanium = 1000000
                """)
                
                # Give lots of buildings to all players
                cursor.execute("""
                    UPDATE buildings SET 
                    iron_mine = 100,
                    copper_mine = 100,
                    oil_mine = 100,
                    gas_mine = 100,
                    aluminum_mine = 100,
                    gold_mine = 100,
                    uranium_mine = 100,
                    lithium_mine = 100,
                    coal_mine = 100,
                    silver_mine = 100,
                    nitro_mine = 100,
                    sulfur_mine = 100,
                    titanium_mine = 100,
                    weapon_factory = 50,
                    refinery = 50,
                    power_plant = 50,
                    wheat_farm = 50,
                    military_base = 50,
                    housing = 50
                """)
                
                conn.commit()
                logger.info("Infinite resources given to all players for testing")
                return True
        except Exception as e:
            logger.error(f"Error giving infinite resources: {e}")
            return False

    def clear_test_data(self):
        """Clear test data from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Delete test players
                cursor.execute("DELETE FROM players WHERE user_id IN (123456, 123457, 123458)")
                cursor.execute("DELETE FROM buildings WHERE user_id IN (123456, 123457, 123458)")
                cursor.execute("DELETE FROM resources WHERE user_id IN (123456, 123457, 123458)")
                cursor.execute("DELETE FROM weapons WHERE user_id IN (123456, 123457, 123458)")
                cursor.execute("DELETE FROM convoys WHERE sender_id IN (123456, 123457, 123458) OR receiver_id IN (123456, 123457, 123458)")
                # The original code had 'marketplace' which is not a table name, corrected to 'marketplace_listings'
                cursor.execute("DELETE FROM marketplace_listings WHERE seller_id IN (123456, 123457, 123458)")
                # The original code had 'alliances' and 'alliance_members' which are not defined in the initialize method, assuming they exist or should be handled.
                # For now, commented out as they are not in the provided initialize schema.
                # cursor.execute("DELETE FROM alliances WHERE leader_id IN (123456, 123457, 123458)")
                # cursor.execute("DELETE FROM alliance_members WHERE user_id IN (123456, 123457, 123458)")
                # The original code had 'first_builds' which is not a table name, corrected to 'build_tracking'
                cursor.execute("DELETE FROM build_tracking WHERE builder_id IN (123456, 123457, 123458)")
                conn.commit()
                cursor.close()
                logger.info("Test data cleared successfully")
                return True
        except Exception as e:
            logger.error(f"Error clearing test data: {e}")
            return False