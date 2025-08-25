import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
import json
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class ConvoySystem:
    def __init__(self, database):
        self.db = database

    def calculate_convoy_security(self, sender_id, resources_value):
        """Calculate convoy security based on sender's military power and transport equipment"""
        weapons = self.db.get_player_weapons(sender_id)

        # Calculate escort power from military weapons
        escort_power = 0
        escort_power += weapons.get('tank', 0) * 15
        escort_power += weapons.get('fighter_jet', 0) * 25
        escort_power += weapons.get('warship', 0) * 40
        escort_power += weapons.get('drone', 0) * 20

        # Calculate transport equipment bonus
        transport_bonus = 0
        transport_bonus += weapons.get('armored_truck', 0) * 25        # Direct convoy security
        transport_bonus += weapons.get('cargo_helicopter', 0) * 40
        transport_bonus += weapons.get('cargo_plane', 0) * 60
        transport_bonus += weapons.get('escort_frigate', 0) * 80
        transport_bonus += weapons.get('logistics_drone', 0) * 30
        transport_bonus += weapons.get('heavy_transport', 0) * 45
        transport_bonus += weapons.get('supply_ship', 0) * 70
        transport_bonus += weapons.get('stealth_transport', 0) * 90

        # Base security from resources value
        base_security = min(resources_value / 1000, 100)

        # Total security (0-95%)
        total_security = min(base_security + (escort_power / 10) + (transport_bonus / 10), 95)

        return int(total_security)

    def can_intercept_convoy(self, interceptor_id, convoy_security, convoy_id=None):
        """Check if player can intercept convoy"""
        # If convoy_id is provided, check if user is sender or receiver
        if convoy_id:
            convoy = self.db.get_convoy(convoy_id)
            if convoy and (convoy['sender_id'] == interceptor_id or convoy['receiver_id'] == interceptor_id):
                return False  # Cannot intercept own convoy

        weapons = self.db.get_player_weapons(interceptor_id)

        # Calculate interception power
        intercept_power = 0
        intercept_power += weapons.get('fighter_jet', 0) * 30
        intercept_power += weapons.get('drone', 0) * 25
        intercept_power += weapons.get('simple_missile', 0) * 50
        intercept_power += weapons.get('warship', 0) * 35

        # Advanced jets are better at interception
        intercept_power += weapons.get('f22', 0) * 60
        intercept_power += weapons.get('f35', 0) * 55
        intercept_power += weapons.get('su57', 0) * 58
        intercept_power += weapons.get('j20', 0) * 52
        intercept_power += weapons.get('f15ex', 0) * 50
        intercept_power += weapons.get('su35s', 0) * 48

        # Need minimum power to attempt interception
        min_power_needed = convoy_security * 2

        return intercept_power >= min_power_needed

    def attempt_convoy_interception(self, interceptor_id, convoy_id, action_type):
        """Attempt to intercept convoy (stop or steal)"""
        convoy = self.db.get_convoy(convoy_id)
        if not convoy or convoy['status'] != 'in_transit':
            return {'success': False, 'message': 'محموله یافت نشد یا قبلاً رسیده!'}

        # Check if convoy is still in transit
        arrival_time = datetime.fromisoformat(convoy['arrival_time'])
        if datetime.now() >= arrival_time:
            return {'success': False, 'message': 'محموله قبلاً به مقصد رسیده!'}

        convoy_security = convoy['security_level']

        if not self.can_intercept_convoy(interceptor_id, convoy_security):
            return {'success': False, 'message': 'قدرت نظامی شما برای رهگیری این محموله کافی نیست!'}

        # Calculate success chance
        interceptor_weapons = self.db.get_player_weapons(interceptor_id)
        intercept_power = (
            interceptor_weapons.get('fighter_jet', 0) * 30 +
            interceptor_weapons.get('drone', 0) * 25 +
            interceptor_weapons.get('simple_missile', 0) * 50 +
            interceptor_weapons.get('warship', 0) * 35
        )

        success_chance = min((intercept_power / (convoy_security * 2)) * 60, 85)

        # Random success
        if random.randint(1, 100) <= success_chance:
            if action_type == 'stop':
                # Stop convoy - return to sender
                self.db.update_convoy_status(convoy_id, 'stopped')
                return {
                    'success': True,
                    'message': f'محموله با موفقیت متوقف شد! منابع به فرستنده بازگردانده می‌شود.',
                    'action': 'stopped'
                }
            else:  # steal
                # Steal convoy resources
                resources = json.loads(convoy['resources'])
                self.db.update_convoy_status(convoy_id, 'stolen')

                # Add resources to interceptor
                for resource, amount in resources.items():
                    if resource == 'money':
                        player = self.db.get_player(interceptor_id)
                        self.db.update_player_money(interceptor_id, player['money'] + amount)
                    else:
                        self.db.add_resources(interceptor_id, resource, amount)

                return {
                    'success': True,
                    'message': f'محموله با موفقیت سرقت شد! منابع به شما اضافه شد.',
                    'action': 'stolen',
                    'stolen_resources': resources
                }
        else:
            # Failed interception - lose some weapons
            self.lose_weapons_in_failed_interception(interceptor_id)
            return {
                'success': False,
                'message': f'رهگیری ناموفق! بخشی از تجهیزات شما در عملیات از دست رفت.',
                'action': 'failed'
            }

    def lose_weapons_in_failed_interception(self, player_id):
        """Player loses some weapons in failed interception"""
        weapons = self.db.get_player_weapons(player_id)

        # Lose 10-30% of attacking weapons
        loss_weapons = ['fighter_jet', 'drone', 'simple_missile']
        for weapon in loss_weapons:
            current = weapons.get(weapon, 0)
            if current > 0:
                loss = max(1, int(current * random.uniform(0.1, 0.3)))
                new_count = max(0, current - loss)
                self.db.update_weapon_count(player_id, weapon, new_count)

    def release_stopped_convoy(self, player_id, convoy_id):
        """Release a stopped convoy"""
        convoy = self.db.get_convoy(convoy_id)

        if not convoy or convoy['status'] != 'stopped':
            return {'success': False, 'message': 'محموله متوقف شده‌ای یافت نشد!'}

        if convoy['sender_id'] != player_id:
            return {'success': False, 'message': 'شما مالک این محموله نیستید!'}

        # Resume convoy with new arrival time
        new_arrival = datetime.now() + timedelta(hours=2)
        self.db.update_convoy_arrival(convoy_id, new_arrival.isoformat(), 'in_transit')

        return {
            'success': True,
            'message': 'محموله آزاد شد و مجدداً در حال حرکت است!'
        }

    def get_active_convoys(self):
        """Get all active convoys that are in transit"""
        return self.db.get_active_convoys()

    def create_convoy_with_transport(self, sender_id, receiver_id, resources, transport_type, transfer_type="resources"):
        """Create a new convoy with specific transport equipment"""
        # Validate sender has enough resources before creating convoy
        if not self.validate_sender_resources(sender_id, resources):
            return {'success': False, 'message': 'منابع کافی برای ارسال ندارید!'}

        # Validate sender has the transport equipment
        if transport_type != 'none':
            weapons = self.db.get_player_weapons(sender_id)
            if weapons.get(transport_type, 0) < 1:
                transport_names = {
                    'armored_truck': 'کامیون زرهی',
                    'cargo_helicopter': 'هلیکوپتر باری',
                    'cargo_plane': 'هواپیمای باری',
                    'logistics_drone': 'پهپاد لجستیک',
                    'heavy_transport': 'ترابری سنگین',
                    'supply_ship': 'کشتی تدارکات',
                    'stealth_transport': 'ترابری پنهان‌کار'
                }
                transport_name = transport_names.get(transport_type, transport_type)
                return {'success': False, 'message': f'شما {transport_name} ندارید!'}

        # Consume resources from sender
        if not self.consume_sender_resources(sender_id, resources):
            return {'success': False, 'message': 'خطا در کسر منابع!'}

        # Calculate travel time based on specific transport
        travel_time = self.calculate_convoy_travel_time_with_transport(sender_id, transport_type)

        # Calculate convoy security with transport bonus
        total_value = sum(amount * Config.RESOURCES.get(res_type, {}).get('market_value', 10) 
                         for res_type, amount in resources.items() if res_type != 'money')
        if 'money' in resources:
            total_value += resources['money']

        security_level = self.calculate_convoy_security_with_transport(sender_id, total_value, transport_type)

        # Create convoy in database
        convoy_id = self.db.create_convoy(sender_id, receiver_id, resources, travel_time, security_level)

        return {
            'success': True,
            'convoy_id': convoy_id,
            'travel_time': travel_time,
            'security_level': security_level,
            'estimated_arrival': datetime.now() + timedelta(minutes=travel_time)
        }

    def calculate_convoy_travel_time_with_transport(self, sender_id, transport_type):
        """Calculate convoy travel time with specific transport"""
        # Check if player has the transport equipment
        if transport_type != 'none':
            weapons = self.db.get_player_weapons(sender_id)
            if weapons.get(transport_type, 0) < 1:
                return 30  # Default time if transport not available
        
        transport_times = {
            'none': 30,
            'armored_truck': 25,
            'cargo_helicopter': 20,
            'cargo_plane': 15,
            'logistics_drone': 18,
            'heavy_transport': 22,
            'supply_ship': 35,
            'stealth_transport': 12
        }

        return transport_times.get(transport_type, 30)

    def calculate_convoy_security_with_transport(self, sender_id, resources_value, transport_type):
        """Calculate convoy security with specific transport"""
        weapons = self.db.get_player_weapons(sender_id)

        # Calculate escort power from military weapons
        escort_power = 0
        escort_power += weapons.get('tank', 0) * 15
        escort_power += weapons.get('fighter_jet', 0) * 25
        escort_power += weapons.get('warship', 0) * 40
        escort_power += weapons.get('drone', 0) * 20

        # Transport specific bonuses
        transport_bonuses = {
            'none': 0,
            'armored_truck': 70,
            'cargo_helicopter': 75,
            'cargo_plane': 85,
            'logistics_drone': 80,
            'heavy_transport': 75,
            'supply_ship': 80,
            'stealth_transport': 95
        }

        transport_bonus = transport_bonuses.get(transport_type, 50)

        # Base security from resources value
        base_security = min(resources_value / 1000, 30)

        # Total security
        total_security = min(base_security + (escort_power / 10) + (transport_bonus / 2), 95)

        return int(total_security)

    def create_convoy(self, sender_id, receiver_id, resources, transfer_type="resources"):
        """Create a new convoy with calculated travel time"""
        # Default to no specific transport for backwards compatibility
        return self.create_convoy_with_transport(sender_id, receiver_id, resources, 'none', transfer_type)

    def calculate_convoy_travel_time(self, sender_id):
        """Calculate convoy travel time based on transport equipment (10-30 minutes)"""
        weapons = self.db.get_player_weapons(sender_id)

        # Base travel time: 30 minutes
        base_time = 30

        # Calculate speed reduction from transport equipment
        speed_reduction = 0
        speed_reduction += weapons.get('armored_truck', 0) * 1      # 1 min reduction per truck
        speed_reduction += weapons.get('cargo_helicopter', 0) * 2   # 2 min reduction per heli
        speed_reduction += weapons.get('cargo_plane', 0) * 3        # 3 min reduction per plane
        speed_reduction += weapons.get('escort_frigate', 0) * 2.5   # 2.5 min reduction per frigate
        speed_reduction += weapons.get('logistics_drone', 0) * 1.5  # 1.5 min reduction per drone
        speed_reduction += weapons.get('heavy_transport', 0) * 2    # 2 min reduction per heavy transport
        speed_reduction += weapons.get('supply_ship', 0) * 2.5      # 2.5 min reduction per ship
        speed_reduction += weapons.get('stealth_transport', 0) * 4  # 4 min reduction per stealth transport

        # Minimum time is 10 minutes, maximum is 30 minutes
        final_time = max(10, base_time - int(speed_reduction))

        return final_time

    def create_convoy_news_keyboard(self, convoy_id, security_level, bot_username):
        """Create keyboard for convoy news with interception options"""
        keyboard = [
            [
                InlineKeyboardButton("🛑 توقف محموله", url=f"https://t.me/{bot_username}?start=convoy_stop_{convoy_id}"),
                InlineKeyboardButton("💰 سرقت محموله", url=f"https://t.me/{bot_username}?start=convoy_steal_{convoy_id}")
            ],
            [
                InlineKeyboardButton("🛡 اسکورت محموله", url=f"https://t.me/{bot_username}?start=convoy_escort_{convoy_id}")
            ],
            [
                InlineKeyboardButton(f"🛡 امنیت: {security_level}%", callback_data="convoy_info")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def provide_convoy_escort(self, escorter_id, convoy_id, escort_weapons):
        """Provide escort for convoy to increase security"""
        convoy = self.db.get_convoy(convoy_id)
        if not convoy or convoy['status'] != 'in_transit':
            return {'success': False, 'message': 'محموله یافت نشد یا قبلاً رسیده!'}

        # Check if convoy is still in transit
        arrival_time = datetime.fromisoformat(convoy['arrival_time'])
        if datetime.now() >= arrival_time:
            return {'success': False, 'message': 'محموله قبلاً به مقصد رسیده!'}

        # Don't allow sender/receiver to escort their own convoy
        if convoy['sender_id'] == escorter_id or convoy['receiver_id'] == escorter_id:
            return {'success': False, 'message': 'نمی‌توانید محموله خودتان را اسکورت کنید!'}

        # Calculate escort bonus
        escort_bonus = 0
        escorter_weapons = self.db.get_player_weapons(escorter_id)

        for weapon, count in escort_weapons.items():
            available = escorter_weapons.get(weapon, 0)
            if available >= count:
                if weapon == 'fighter_jet':
                    escort_bonus += count * 20
                elif weapon == 'tank':
                    escort_bonus += count * 15
                elif weapon == 'warship':
                    escort_bonus += count * 30
                elif weapon == 'drone':
                    escort_bonus += count * 18
            else:
                return {'success': False, 'message': f'تعداد کافی {weapon} ندارید!'}

        # Apply escort bonus to convoy security
        new_security = min(convoy['security_level'] + escort_bonus, 99)
        self.db.update_convoy_security(convoy_id, new_security)

        return {
            'success': True,
            'message': f'اسکورت با موفقیت انجام شد! امنیت محموله از {convoy["security_level"]}% به {new_security}% افزایش یافت.',
            'old_security': convoy['security_level'],
            'new_security': new_security,
            'escort_bonus': escort_bonus
        }

    def validate_sender_resources(self, sender_id, resources):
        """Validate that sender has enough resources"""
        current_resources = self.db.get_player_resources(sender_id)
        player = self.db.get_player(sender_id)
        
        for resource, amount in resources.items():
            if resource == 'money':
                if player['money'] < amount:
                    return False
            else:
                if current_resources.get(resource, 0) < amount:
                    return False
        return True

    def consume_sender_resources(self, sender_id, resources):
        """Remove resources from sender when creating convoy"""
        try:
            player = self.db.get_player(sender_id)
            
            # Handle money separately
            if 'money' in resources:
                money_amount = resources['money']
                new_money = player['money'] - money_amount
                self.db.update_player_money(sender_id, new_money)
            
            # Handle other resources
            other_resources = {k: v for k, v in resources.items() if k != 'money'}
            if other_resources:
                return self.db.consume_resources(sender_id, other_resources)
            
            return True
        except Exception as e:
            logger.error(f"Error consuming sender resources: {e}")
            return False

    def process_convoy_arrivals(self):
        """Process all convoys that have arrived at their destination"""
        arrived_convoys = self.db.get_arrived_convoys()
        results = []
        
        for convoy in arrived_convoys:
            try:
                result = self.deliver_convoy(convoy)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing convoy {convoy['id']}: {e}")
                # Mark convoy as failed
                self.db.update_convoy_status(convoy['id'], 'failed')
        
        return results

    def deliver_convoy(self, convoy):
        """Deliver convoy resources to receiver"""
        convoy_id = convoy['id']
        receiver_id = convoy['receiver_id']
        sender_id = convoy['sender_id']
        resources = json.loads(convoy['resources'])
        security_level = convoy['security_level']
        
        # Calculate delivery success chance based on security
        success_chance = min(security_level + 10, 95)
        
        if random.randint(1, 100) <= success_chance:
            # Successful delivery
            try:
                # Add resources to receiver
                player = self.db.get_player(receiver_id)
                
                # Handle money separately
                if 'money' in resources:
                    money_amount = resources['money']
                    new_money = player['money'] + money_amount
                    self.db.update_player_money(receiver_id, new_money)
                
                # Handle other resources
                for resource, amount in resources.items():
                    if resource != 'money':
                        self.db.add_resources(receiver_id, resource, amount)
                
                # Mark convoy as delivered
                self.db.update_convoy_status(convoy_id, 'delivered')
                
                return {
                    'convoy_id': convoy_id,
                    'success': True,
                    'message': 'محموله با موفقیت تحویل شد!',
                    'resources': resources
                }
                
            except Exception as e:
                logger.error(f"Error delivering convoy {convoy_id}: {e}")
                self.db.update_convoy_status(convoy_id, 'failed')
                return {
                    'convoy_id': convoy_id,
                    'success': False,
                    'message': 'خطا در تحویل محموله!'
                }
        else:
            # Failed delivery - convoy intercepted/lost
            self.db.update_convoy_status(convoy_id, 'lost')
            return {
                'convoy_id': convoy_id,
                'success': False,
                'message': 'محموله در راه دزدیده شد!',
                'resources_lost': resources
            }