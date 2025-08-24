import logging
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class GameLogic:
    def __init__(self, database):
        self.db = database
    
    def get_player_stats(self, user_id):
        """Get comprehensive player statistics"""
        player = self.db.get_player(user_id)
        if not player:
            return None
        
        resources = self.db.get_player_resources(user_id)
        buildings = self.db.get_player_buildings(user_id)
        weapons = self.db.get_player_weapons(user_id)
        
        return {
            'country_name': player['country_name'],
            'population': player['population'],
            'money': player['money'],
            'soldiers': player['soldiers'],
            'resources': resources,
            'buildings': buildings,
            'weapons': weapons
        }
    
    def build_structure(self, user_id, building_type):
        """Handle building construction"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد!'}
        
        building_info = Config.BUILDINGS.get(building_type)
        if not building_info:
            return {'success': False, 'message': 'نوع ساختمان نامعتبر است!'}
        
        # Check if player has enough money
        if player['money'] < building_info['cost']:
            return {
                'success': False, 
                'message': f"پول کافی ندارید! نیاز: ${building_info['cost']:,}, موجود: ${player['money']:,}"
            }
        
        # Check special requirements
        if building_type == 'weapon_factory':
            # Need power plant for weapon factory
            buildings = self.db.get_player_buildings(user_id)
            if buildings.get('power_plant', 0) == 0:
                return {
                    'success': False,
                    'message': 'برای ساخت کارخانه اسلحه ابتدا باید نیروگاه بسازید!'
                }
        
        # Deduct money and add building
        new_money = player['money'] - building_info['cost']
        self.db.update_player_money(user_id, new_money)
        self.db.add_building(user_id, building_type)
        
        return {
            'success': True,
            'message': f"✅ {building_info['name']} با موفقیت ساخته شد!",
            'building_name': building_info['name'],
            'remaining_money': new_money
        }
    
    def produce_weapon(self, user_id, weapon_type):
        """Handle weapon production"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد!'}
        
        weapon_info = Config.WEAPONS.get(weapon_type)
        if not weapon_info:
            return {'success': False, 'message': 'نوع سلاح نامعتبر است!'}
        
        # Check if player has weapon factory
        buildings = self.db.get_player_buildings(user_id)
        if buildings.get('weapon_factory', 0) == 0:
            return {
                'success': False,
                'message': 'برای تولید سلاح ابتدا باید کارخانه اسلحه بسازید!'
            }
        
        # Check money
        if player['money'] < weapon_info['cost']:
            return {
                'success': False,
                'message': f"پول کافی ندارید! نیاز: ${weapon_info['cost']:,}"
            }
        
        # Check resources
        resources = self.db.get_player_resources(user_id)
        for resource, amount in weapon_info['resources'].items():
            if resources.get(resource, 0) < amount:
                return {
                    'success': False,
                    'message': f"منابع کافی ندارید! کمبود: {amount} {resource}"
                }
        
        # Consume resources and money
        new_money = player['money'] - weapon_info['cost']
        self.db.update_player_money(user_id, new_money)
        self.db.consume_resources(user_id, weapon_info['resources'])
        self.db.add_weapon(user_id, weapon_type)
        
        return {
            'success': True,
            'message': f"✅ {weapon_info['name']} تولید شد!",
            'weapon_name': weapon_info['name'],
            'remaining_money': new_money
        }
    
    def calculate_military_power(self, user_id):
        """Calculate total military power"""
        weapons = self.db.get_player_weapons(user_id)
        total_power = 0
        
        for weapon_type, count in weapons.items():
            if weapon_type in Config.WEAPONS:
                weapon_power = Config.WEAPONS[weapon_type]['power']
                total_power += weapon_power * count
        
        return total_power
    
    def calculate_defense_power(self, user_id):
        """Calculate total defense power"""
        weapons = self.db.get_player_weapons(user_id)
        defense_power = 0
        
        # Only defensive weapons count for defense
        defensive_weapons = ['air_defense', 'missile_shield', 'cyber_shield']
        
        for weapon_type in defensive_weapons:
            count = weapons.get(weapon_type, 0)
            if weapon_type in Config.WEAPONS:
                weapon_power = Config.WEAPONS[weapon_type]['power']
                defense_power += weapon_power * count
        
        return defense_power
    
    def can_attack_country(self, attacker_id, defender_id):
        """Check if attacker can reach defender"""
        attacker = self.db.get_player(attacker_id)
        defender = self.db.get_player(defender_id)
        
        if not attacker or not defender:
            return False, "کشور یافت نشد!"
        
        attacker_country = attacker['country_code']
        defender_country = defender['country_code']
        
        # Check if countries are neighbors
        if self.are_countries_neighbors(attacker_country, defender_country):
            return True, "کشورهای همسایه - حمله مجاز"
        
        # Check if attacker has long-range weapons
        weapons = self.db.get_player_weapons(attacker_id)
        long_range_weapons = ['missile', 'drone', 'fighter_jet']
        
        has_long_range = any(weapons.get(weapon, 0) > 0 for weapon in long_range_weapons)
        
        if has_long_range:
            return True, "دارای تسلیحات با برد بالا"
        
        return False, "فاصله زیاد - نیاز به تسلیحات با برد بالا"
    
    def are_countries_neighbors(self, country1, country2):
        """Check if two countries are neighbors (simplified)"""
        # This is a simplified version - in reality would need complex geography data
        neighbors = {
            'IR': ['TR', 'IQ', 'AF', 'PK'],  # Iran
            'TR': ['IR', 'IQ', 'SY', 'GR'],  # Turkey
            'US': ['MX', 'CA'],  # USA
            'MX': ['US'],  # Mexico
            'RU': ['CN', 'KP'],  # Russia
            'CN': ['RU', 'KP', 'JP'],  # China
            'FR': ['DE', 'ES'],  # France
            'DE': ['FR'],  # Germany
            'ES': ['FR'],  # Spain
            'EG': ['SA'],  # Egypt
            'JP': ['CN', 'KP'],  # Japan
            'AR': [],  # Argentina (island nation for game purposes)
            'BE': ['FR', 'DE'],  # Belgium
            'KP': ['CN', 'RU', 'JP'],  # North Korea
        }
        
        return country2 in neighbors.get(country1, [])
    
    def execute_attack(self, attacker_id, defender_id, attack_type='mixed'):
        """Execute attack between two countries"""
        # Check if attack is possible
        can_attack, reason = self.can_attack_country(attacker_id, defender_id)
        if not can_attack:
            return {'success': False, 'message': f"حمله امکان‌پذیر نیست: {reason}"}
        
        # Calculate powers
        attack_power = self.calculate_military_power(attacker_id)
        defense_power = self.calculate_defense_power(defender_id)
        
        if attack_power == 0:
            return {'success': False, 'message': 'شما هیچ تسلیحاتی برای حمله ندارید!'}
        
        # Battle calculation with randomness
        import random
        random_factor = random.uniform(0.8, 1.2)
        effective_attack = attack_power * random_factor
        
        damage = effective_attack - defense_power
        
        attacker = self.db.get_player(attacker_id)
        defender = self.db.get_player(defender_id)
        
        result = {
            'attacker': attacker['country_name'],
            'defender': defender['country_name'],
            'attack_power': attack_power,
            'defense_power': defense_power,
            'damage': damage
        }
        
        if damage > 0:
            # Attack successful
            result['success'] = True
            result['winner'] = attacker['country_name']
            
            # Calculate losses and stolen resources
            self._apply_battle_consequences(attacker_id, defender_id, damage)
            
        else:
            # Attack failed
            result['success'] = False
            result['winner'] = defender['country_name']
            
            # Attacker suffers losses
            self._apply_failed_attack_consequences(attacker_id, abs(damage))
        
        # Log the war
        self._log_war(attacker_id, defender_id, attack_power, defense_power, result)
        
        return result
    
    def _apply_battle_consequences(self, attacker_id, defender_id, damage):
        """Apply consequences of successful attack"""
        # Defender loses soldiers and some weapons
        defender = self.db.get_player(defender_id)
        defender_weapons = self.db.get_player_weapons(defender_id)
        defender_resources = self.db.get_player_resources(defender_id)
        
        # Calculate losses based on damage
        soldier_losses = min(defender['soldiers'], int(damage * 10))
        
        # Attacker steals some resources
        stolen_resources = {}
        for resource, amount in defender_resources.items():
            if amount > 0 and resource != 'user_id':
                stolen_amount = min(amount, int(damage * 5))
                if stolen_amount > 0:
                    stolen_resources[resource] = stolen_amount
                    # Remove from defender
                    self.db.consume_resources(defender_id, {resource: stolen_amount})
                    # Add to attacker
                    self.db.add_resources(attacker_id, resource, stolen_amount)
        
        # Update defender's soldiers
        new_soldiers = max(0, defender['soldiers'] - soldier_losses)
        self.db.update_player_income(defender_id, defender['money'], defender['population'], new_soldiers)
    
    def _apply_failed_attack_consequences(self, attacker_id, damage):
        """Apply consequences of failed attack"""
        attacker = self.db.get_player(attacker_id)
        
        # Attacker loses some soldiers and weapons
        soldier_losses = min(attacker['soldiers'], int(damage * 5))
        new_soldiers = max(0, attacker['soldiers'] - soldier_losses)
        
        self.db.update_player_income(attacker_id, attacker['money'], attacker['population'], new_soldiers)
    
    def _log_war(self, attacker_id, defender_id, attack_power, defense_power, result):
        """Log war in database"""
        # This would be implemented to store war history
        pass
    
    def get_country_ranking(self):
        """Get ranking of all countries by power"""
        players = self.db.get_all_players()
        rankings = []
        
        for player in players:
            military_power = self.calculate_military_power(player['user_id'])
            rankings.append({
                'country_name': player['country_name'],
                'military_power': military_power,
                'population': player['population'],
                'money': player['money']
            })
        
        # Sort by military power
        rankings.sort(key=lambda x: x['military_power'], reverse=True)
        return rankings
import logging
from config import Config

logger = logging.getLogger(__name__)

class GameLogic:
    def __init__(self, database):
        self.db = database
    
    def get_player_stats(self, user_id):
        """Get comprehensive player statistics"""
        player = self.db.get_player(user_id)
        if not player:
            return None
        
        resources = self.db.get_player_resources(user_id)
        buildings = self.db.get_player_buildings(user_id)
        weapons = self.db.get_player_weapons(user_id)
        
        return {
            'user_id': user_id,
            'country_name': player['country_name'],
            'country_code': player['country_code'],
            'money': player['money'],
            'population': player['population'],
            'soldiers': player['soldiers'],
            'resources': resources,
            'buildings': buildings,
            'weapons': weapons
        }
    
    def build_structure(self, user_id, building_type):
        """Build a structure for player"""
        player = self.db.get_player(user_id)
        building_config = Config.BUILDINGS.get(building_type)
        
        if not building_config:
            return {'success': False, 'message': 'نوع ساختمان نامعتبر است'}
        
        building_cost = building_config['cost']
        building_name = building_config['name']
        
        if player['money'] < building_cost:
            return {
                'success': False, 
                'message': f'پول کافی ندارید! نیاز: ${building_cost:,}, موجود: ${player["money"]:,}'
            }
        
        # Check requirements
        requirements = building_config.get('requirements', [])
        if requirements:
            buildings = self.db.get_player_buildings(user_id)
            for req in requirements:
                if buildings.get(req, 0) == 0:
                    req_name = Config.BUILDINGS.get(req, {}).get('name', req)
                    return {
                        'success': False,
                        'message': f'ابتدا باید {req_name} بسازید'
                    }
        
        # Deduct money and add building
        new_money = player['money'] - building_cost
        self.db.update_player_money(user_id, new_money)
        self.db.add_building(user_id, building_type)
        
        return {
            'success': True,
            'message': f'{building_name} با موفقیت ساخته شد!',
            'building_name': building_name,
            'remaining_money': new_money
        }
    
    def produce_weapon(self, user_id, weapon_type):
        """Produce a weapon for player"""
        player = self.db.get_player(user_id)
        weapon_config = Config.WEAPONS.get(weapon_type)
        
        if not weapon_config:
            return {'success': False, 'message': 'نوع سلاح نامعتبر است'}
        
        weapon_cost = weapon_config['cost']
        weapon_name = weapon_config['name']
        required_resources = weapon_config.get('resources', {})
        
        # Check weapon factory
        buildings = self.db.get_player_buildings(user_id)
        if buildings.get('weapon_factory', 0) == 0:
            return {'success': False, 'message': 'برای تولید سلاح به کارخانه اسلحه نیاز دارید!'}
        
        # Check money
        if player['money'] < weapon_cost:
            return {
                'success': False,
                'message': f'پول کافی ندارید! نیاز: ${weapon_cost:,}, موجود: ${player["money"]:,}'
            }
        
        # Check resources
        if not self.db.consume_resources(user_id, required_resources):
            return {'success': False, 'message': 'منابع کافی ندارید!'}
        
        # Deduct money and add weapon
        new_money = player['money'] - weapon_cost
        self.db.update_player_money(user_id, new_money)
        self.db.add_weapon(user_id, weapon_type, 1)
        
        return {
            'success': True,
            'message': f'{weapon_name} با موفقیت تولید شد!',
            'weapon_name': weapon_name,
            'remaining_money': new_money
        }
