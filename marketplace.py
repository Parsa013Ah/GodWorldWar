import logging
from datetime import datetime
import json
from config import Config

logger = logging.getLogger(__name__)

class Marketplace:
    def __init__(self, database):
        self.db = database
        self.setup_marketplace_tables()

    def setup_marketplace_tables(self):
        """Setup marketplace tables"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Market listings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    item_category TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price_per_unit INTEGER NOT NULL,
                    total_price INTEGER NOT NULL,
                    security_level INTEGER DEFAULT 50,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (seller_id) REFERENCES players (user_id)
                )
            ''')

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

            conn.commit()

    def create_listing(self, seller_id, item_type, item_category, quantity, price_per_unit):
        """Create new market listing"""
        # Verify seller has the items
        if not self.verify_seller_inventory(seller_id, item_category, item_type, quantity):
            return {'success': False, 'message': 'موجودی کافی ندارید!'}

        # Calculate security based on seller's military power
        security_level = self.calculate_seller_security(seller_id)
        total_price = quantity * price_per_unit

        # Remove items from seller's inventory
        if not self.remove_from_inventory(seller_id, item_category, item_type, quantity):
            return {'success': False, 'message': 'خطا در کسر موجودی!'}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO market_listings 
                (seller_id, item_type, item_category, quantity, price_per_unit, total_price, security_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (seller_id, item_type, item_category, quantity, price_per_unit, total_price, security_level))

            listing_id = cursor.lastrowid
            conn.commit()

        return {
            'success': True,
            'message': 'آگهی فروش ثبت شد!',
            'listing_id': listing_id,
            'security_level': security_level
        }

    def purchase_item(self, buyer_id, listing_id, quantity_to_buy):
        """Purchase item from marketplace"""
        listing = self.get_listing(listing_id)

        if not listing or listing['status'] != 'active':
            return {'success': False, 'message': 'آگهی فروش یافت نشد!'}

        if listing['seller_id'] == buyer_id:
            return {'success': False, 'message': 'نمی‌توانید از خودتان خرید کنید!'}

        if quantity_to_buy > listing['quantity']:
            return {'success': False, 'message': 'موجودی کافی نیست!'}

        total_cost = quantity_to_buy * listing['price_per_unit']
        buyer = self.db.get_player(buyer_id)

        if buyer['money'] < total_cost:
            return {'success': False, 'message': 'پول کافی ندارید!'}

        # Process transaction
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Create transaction record
            cursor.execute('''
                INSERT INTO market_transactions 
                (listing_id, buyer_id, seller_id, item_type, quantity, total_paid)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (listing_id, buyer_id, listing['seller_id'], listing['item_type'], 
                  quantity_to_buy, total_cost))

            transaction_id = cursor.lastrowid

            # Deduct money from buyer
            self.db.update_player_money(buyer_id, buyer['money'] - total_cost)

            # Add money to seller
            seller = self.db.get_player(listing['seller_id'])
            self.db.update_player_money(listing['seller_id'], seller['money'] + total_cost)

            # Update listing quantity
            remaining_quantity = listing['quantity'] - quantity_to_buy
            if remaining_quantity <= 0:
                cursor.execute('UPDATE market_listings SET status = "sold_out" WHERE id = ?', (listing_id,))
            else:
                cursor.execute('UPDATE market_listings SET quantity = ? WHERE id = ?', 
                              (remaining_quantity, listing_id))

            conn.commit()

        # Check if this is first purchase for news
        is_first_purchase = self.db.check_first_purchase(buyer_id, listing['item_type'])
        if is_first_purchase:
            self.db.record_first_purchase(buyer_id, listing['item_type'])

        # Add items to buyer (will be delivered based on security)
        delivery_success = self.process_delivery(buyer_id, listing, quantity_to_buy, transaction_id)

        return {
            'success': True,
            'message': 'خرید انجام شد! در صورت موفقیت تحویل، اقلام به شما تحویل داده می‌شود.',
            'transaction_id': transaction_id,
            'delivery_status': delivery_success,
            'is_first_purchase': is_first_purchase
        }

    def process_delivery(self, buyer_id, listing, quantity, transaction_id):
        """Process delivery of purchased items"""
        security_level = listing['security_level']

        # Higher security = higher delivery success chance
        base_success_chance = min(security_level + 20, 90)

        import random
        if random.randint(1, 100) <= base_success_chance:
            # Successful delivery
            self.add_to_inventory(buyer_id, listing['item_category'], listing['item_type'], quantity)

            # Update transaction status
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE market_transactions 
                    SET status = "delivered", delivery_date = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (transaction_id,))
                conn.commit()

            return {'success': True, 'message': 'کالا با موفقیت تحویل شد!'}
        else:
            # Failed delivery - money lost, items lost
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE market_transactions 
                    SET status = "failed" 
                    WHERE id = ?
                ''', (transaction_id,))
                conn.commit()

            return {'success': False, 'message': 'محموله در راه دزدیده شد!'}

    def calculate_seller_security(self, seller_id):
        """Calculate seller security level"""
        weapons = self.db.get_player_weapons(seller_id)

        security_points = 0
        security_points += weapons.get('tank', 0) * 10
        security_points += weapons.get('fighter_jet', 0) * 15
        security_points += weapons.get('drone', 0) * 12
        security_points += weapons.get('warship', 0) * 20
        security_points += weapons.get('air_defense', 0) * 8

        # Convert to percentage (max 95%)
        security_level = min(30 + (security_points / 10), 95)
        return int(security_level)

    def verify_seller_inventory(self, seller_id, category, item_type, quantity):
        """Verify seller has required inventory"""
        if category == 'resource':
            resources = self.db.get_player_resources(seller_id)
            return resources.get(item_type, 0) >= quantity
        elif category == 'weapon':
            weapons = self.db.get_player_weapons(seller_id)
            return weapons.get(item_type, 0) >= quantity
        elif category == 'money':
            player = self.db.get_player(seller_id)
            return player['money'] >= quantity

        return False

    def remove_from_inventory(self, seller_id, category, item_type, quantity):
        """Remove items from seller inventory"""
        if category == 'resource':
            return self.db.consume_resources(seller_id, {item_type: quantity})
        elif category == 'weapon':
            weapons = self.db.get_player_weapons(seller_id)
            current = weapons.get(item_type, 0)
            if current >= quantity:
                self.db.update_weapon_count(seller_id, item_type, current - quantity)
                return True
        elif category == 'money':
            player = self.db.get_player(seller_id)
            if player['money'] >= quantity:
                self.db.update_player_money(seller_id, player['money'] - quantity)
                return True

        return False

    def add_to_inventory(self, buyer_id, category, item_type, quantity):
        """Add items to buyer inventory"""
        if category == 'resource':
            self.db.add_resources(buyer_id, item_type, quantity)
        elif category == 'weapon':
            self.db.add_weapon(buyer_id, item_type, quantity)
        elif category == 'money':
            player = self.db.get_player(buyer_id)
            self.db.update_player_money(buyer_id, player['money'] + quantity)

    def get_listing(self, listing_id):
        """Get listing details"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM market_listings WHERE id = ?', (listing_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_active_listings(self, category=None, limit=20):
        """Get active market listings"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            if category:
                cursor.execute('''
                    SELECT ml.*, p.country_name as seller_country
                    FROM market_listings ml
                    JOIN players p ON ml.seller_id = p.user_id
                    WHERE ml.status = "active" AND ml.item_category = ?
                    ORDER BY ml.created_at DESC
                    LIMIT ?
                ''', (category, limit))
            else:
                cursor.execute('''
                    SELECT ml.*, p.country_name as seller_country
                    FROM market_listings ml
                    JOIN players p ON ml.seller_id = p.user_id
                    WHERE ml.status = "active"
                    ORDER BY ml.created_at DESC
                    LIMIT ?
                ''', (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_player_listings(self, seller_id):
        """Get player's listings"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM market_listings 
                WHERE seller_id = ? AND status IN ("active", "sold_out")
                ORDER BY created_at DESC
            ''', (seller_id,))

            return [dict(row) for row in cursor.fetchall()]

    def cancel_listing(self, seller_id, listing_id):
        """Cancel a listing and return items"""
        listing = self.get_listing(listing_id)

        if not listing or listing['seller_id'] != seller_id:
            return {'success': False, 'message': 'آگهی فروش یافت نشد!'}

        if listing['status'] != 'active':
            return {'success': False, 'message': 'این آگهی قابل لغو نیست!'}

        # Return items to seller
        self.add_to_inventory(seller_id, listing['item_category'], listing['item_type'], listing['quantity'])

        # Update listing status
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE market_listings SET status = "cancelled" WHERE id = ?', (listing_id,))
            conn.commit()

        return {'success': True, 'message': 'آگهی لغو شد و اقلام بازگردانده شد.'}

    def delete_listing(self, seller_id, listing_id):
        """Delete a listing (for admins or after sold out/cancelled)"""
        listing = self.get_listing(listing_id)

        if not listing:
            return {'success': False, 'message': 'آگهی فروش یافت نشد!'}

        # Only allow deletion if not active, or by admin (assuming seller_id could be admin if special logic)
        if listing['status'] == 'active':
             return {'success': False, 'message': 'آگهی فعال را نمی‌توان حذف کرد!'}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM market_listings WHERE id = ?', (listing_id,))
            conn.commit()

        return {'success': True, 'message': 'آگهی با موفقیت حذف شد.'}

    def get_listings_by_category(self, category):
        """Get marketplace listings by category"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ml.*, p.country_name as seller_country
                FROM market_listings ml
                JOIN players p ON ml.seller_id = p.user_id
                WHERE ml.item_category = ? AND ml.status = 'active'
                ORDER BY ml.created_at DESC
            ''', (category,))
            results = cursor.fetchall()
            return [dict(row) for row in results]

