import random
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class CombatSystem:
    def __init__(self, database):
        self.db = database
    
    def calculate_attack_power(self, user_id, attack_type='mixed'):
        """Calculate total attack power based on weapons"""
        weapons = self.db.get_player_weapons(user_id)
        total_power = 0
        
        attack_weapons = {
            'ground': ['rifle', 'tank'],
            'air': ['fighter_jet', 'drone'],
            'naval': ['warship'],
            'missile': ['missile'],
            'mixed': ['rifle', 'tank', 'fighter_jet', 'drone', 'missile', 'warship']
        }
        
        relevant_weapons = attack_weapons.get(attack_type, attack_weapons['mixed'])
        
        for weapon_type in relevant_weapons:
            count = weapons.get(weapon_type, 0)
            if weapon_type in Config.WEAPONS and count > 0:
                weapon_power = Config.WEAPONS[weapon_type]['power']
                total_power += weapon_power * count
        
        return total_power
    
    def calculate_defense_power(self, user_id, attack_type='mixed'):
        """Calculate defense power against specific attack type"""
        weapons = self.db.get_player_weapons(user_id)
        total_defense = 0
        
        # Base defense from all weapons
        base_defense = 0
        for weapon_type, count in weapons.items():
            if weapon_type in Config.WEAPONS and count > 0:
                weapon_power = Config.WEAPONS[weapon_type]['power']
                base_defense += weapon_power * count * 0.3  # 30% of weapon power for defense
        
        # Specific defense bonuses
        defense_bonuses = {
            'air': weapons.get('air_defense', 0) * 100,
            'missile': weapons.get('missile_shield', 0) * 120,
            'cyber': weapons.get('cyber_shield', 0) * 80
        }
        
        # Apply specific defense bonus
        if attack_type in defense_bonuses:
            total_defense = base_defense + defense_bonuses[attack_type]
        else:
            total_defense = base_defense
        
        return int(total_defense)
    
    def calculate_weapon_range(self, user_id):
        """Calculate maximum attack range based on weapons"""
        weapons = self.db.get_player_weapons(user_id)
        max_range = 50  # Base range for ground weapons
        
        weapon_ranges = {
            'fighter_jet': 1000,
            'drone': 1500,
            'missile': 3000,
            'warship': 1000
        }
        
        for weapon_type, range_km in weapon_ranges.items():
            if weapons.get(weapon_type, 0) > 0:
                max_range = max(max_range, range_km)
        
        return max_range
    
    def can_reach_target(self, attacker_id, defender_id):
        """Check if attacker can reach defender"""
        attacker = self.db.get_player(attacker_id)
        defender = self.db.get_player(defender_id)
        
        if not attacker or not defender:
            return False, "کشور یافت نشد"
        
        attacker_country = attacker['country_code']
        defender_country = defender['country_code']
        
        # Check if countries are neighbors (always can attack)
        if self.are_neighbors(attacker_country, defender_country):
            return True, "کشورهای همسایه"
        
        # Check weapon range
        max_range = self.calculate_weapon_range(attacker_id)
        distance = self.get_country_distance(attacker_country, defender_country)
        
        if max_range >= distance:
            return True, f"برد کافی: {max_range}km >= {distance}km"
        else:
            return False, f"برد ناکافی: {max_range}km < {distance}km"
    
    def are_neighbors(self, country1, country2):
        """Check if countries are neighbors"""
        # Simplified neighbor relationships
        neighbors = {
            'IR': ['TR', 'IQ', 'AF'],  # Iran
            'TR': ['IR', 'SY', 'GR'],  # Turkey  
            'RU': ['CN', 'KP', 'DE'],  # Russia
            'CN': ['RU', 'KP', 'JP'],  # China
            'US': ['MX'],  # USA
            'MX': ['US'],  # Mexico
            'FR': ['DE', 'ES', 'BE'],  # France
            'DE': ['FR', 'RU', 'BE'],  # Germany
            'ES': ['FR'],  # Spain
            'BE': ['FR', 'DE'],  # Belgium
            'JP': ['CN', 'KP'],  # Japan
            'KP': ['CN', 'RU', 'JP'],  # North Korea
            'EG': [],  # Egypt
            'AR': [],  # Argentina
        }
        
        return country2 in neighbors.get(country1, [])
    
    def get_country_distance(self, country1, country2):
        """Get distance between countries in km"""
        # Simplified distance matrix
        distances = {
            ('IR', 'US'): 12000,
            ('IR', 'CN'): 3000,
            ('IR', 'JP'): 6000,
            ('US', 'CN'): 11000,
            ('US', 'RU'): 8000,
            ('DE', 'RU'): 1600,
            ('FR', 'US'): 6000,
            # Add more distances as needed
        }
        
        # Try both directions
        distance = distances.get((country1, country2)) or distances.get((country2, country1))
        return distance or 5000  # Default distance
    
    def execute_battle(self, attacker_id, defender_id, attack_type='mixed'):
        """Execute a complete battle"""
        # Check if attack is possible
        can_attack, reason = self.can_reach_target(attacker_id, defender_id)
        if not can_attack:
            return {
                'success': False,
                'message': f"حمله امکان‌پذیر نیست: {reason}"
            }
        
        # Get player info
        attacker = self.db.get_player(attacker_id)
        defender = self.db.get_player(defender_id)
        
        # Calculate powers
        attack_power = self.calculate_attack_power(attacker_id, attack_type)
        defense_power = self.calculate_defense_power(defender_id, attack_type)
        
        if attack_power == 0:
            return {
                'success': False,
                'message': "شما تسلیحات کافی برای حمله ندارید!"
            }
        
        # Battle calculation with randomness
        battle_result = self.simulate_battle(attack_power, defense_power)
        
        # Apply consequences
        consequences = self.apply_battle_consequences(
            attacker_id, defender_id, battle_result, attack_type
        )
        
        # Log the battle
        self.log_battle(attacker_id, defender_id, battle_result, consequences)
        
        # Prepare result message
        result = {
            'success': battle_result['attacker_wins'],
            'attacker': attacker['country_name'],
            'defender': defender['country_name'],
            'attack_power': attack_power,
            'defense_power': defense_power,
            'damage_dealt': battle_result['damage'],
            'attacker_losses': consequences['attacker_losses'],
            'defender_losses': consequences['defender_losses'],
            'resources_stolen': consequences.get('resources_stolen', {}),
            'message': self.generate_battle_message(attacker, defender, battle_result, consequences)
        }
        
        return result
    
    def simulate_battle(self, attack_power, defense_power):
        """Simulate the battle with randomness"""
        # Add randomness factors
        attack_modifier = random.uniform(0.8, 1.2)
        defense_modifier = random.uniform(0.8, 1.2)
        
        effective_attack = attack_power * attack_modifier
        effective_defense = defense_power * defense_modifier
        
        # Calculate damage
        raw_damage = effective_attack - effective_defense
        
        # Determine winner
        attacker_wins = raw_damage > 0
        
        # Calculate actual damage (minimum 10% of attack power)
        if attacker_wins:
            damage = max(raw_damage, attack_power * 0.1)
        else:
            damage = max(abs(raw_damage), defense_power * 0.1)
        
        return {
            'attacker_wins': attacker_wins,
            'damage': int(damage),
            'attack_modifier': attack_modifier,
            'defense_modifier': defense_modifier
        }
    
    def apply_battle_consequences(self, attacker_id, defender_id, battle_result, attack_type):
        """Apply consequences of the battle"""
        damage = battle_result['damage']
        attacker_wins = battle_result['attacker_wins']
        
        attacker_losses = {}
        defender_losses = {}
        resources_stolen = {}
        
        if attacker_wins:
            # Defender suffers major losses
            defender_losses = self.calculate_defender_losses(defender_id, damage)
            self.apply_losses(defender_id, defender_losses)
            
            # Attacker suffers minor losses
            attacker_losses = self.calculate_attacker_losses(attacker_id, damage * 0.2)
            self.apply_losses(attacker_id, attacker_losses)
            
            # Steal resources
            resources_stolen = self.steal_resources(attacker_id, defender_id, damage)
            
        else:
            # Attacker suffers major losses
            attacker_losses = self.calculate_attacker_losses(attacker_id, damage)
            self.apply_losses(attacker_id, attacker_losses)
            
            # Defender suffers minor losses
            defender_losses = self.calculate_defender_losses(defender_id, damage * 0.3)
            self.apply_losses(defender_id, defender_losses)
        
        return {
            'attacker_losses': attacker_losses,
            'defender_losses': defender_losses,
            'resources_stolen': resources_stolen
        }
    
    def calculate_defender_losses(self, user_id, damage):
        """Calculate losses for defender"""
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)
        
        losses = {
            'soldiers': min(player['soldiers'], int(damage * 10)),
            'weapons': {}
        }
        
        # Random weapon losses
        for weapon_type, count in weapons.items():
            if count > 0 and weapon_type in Config.WEAPONS:
                loss_chance = min(0.3, damage / 1000)  # Up to 30% loss chance
                if random.random() < loss_chance:
                    lost = min(count, random.randint(1, max(1, count // 5)))
                    losses['weapons'][weapon_type] = lost
        
        return losses
    
    def calculate_attacker_losses(self, user_id, damage):
        """Calculate losses for attacker"""
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)
        
        losses = {
            'soldiers': min(player['soldiers'], int(damage * 5)),
            'weapons': {}
        }
        
        # Smaller weapon losses for attacker
        for weapon_type, count in weapons.items():
            if count > 0 and weapon_type in Config.WEAPONS:
                loss_chance = min(0.15, damage / 2000)  # Up to 15% loss chance
                if random.random() < loss_chance:
                    lost = min(count, random.randint(1, max(1, count // 10)))
                    losses['weapons'][weapon_type] = lost
        
        return losses
    
    def apply_losses(self, user_id, losses):
        """Apply calculated losses to player"""
        player = self.db.get_player(user_id)
        
        # Apply soldier losses
        new_soldiers = max(0, player['soldiers'] - losses['soldiers'])
        self.db.update_player_income(
            user_id, player['money'], player['population'], new_soldiers
        )
        
        # Apply weapon losses
        for weapon_type, lost_count in losses.get('weapons', {}).items():
            # Reduce weapon count (would need a new DB method)
            pass
    
    def steal_resources(self, attacker_id, defender_id, damage):
        """Steal resources from defender to attacker"""
        defender_resources = self.db.get_player_resources(defender_id)
        stolen = {}
        
        steal_factor = min(0.3, damage / 1000)  # Up to 30% based on damage
        
        for resource, amount in defender_resources.items():
            if resource != 'user_id' and amount > 0:
                stolen_amount = int(amount * steal_factor * random.uniform(0.5, 1.0))
                if stolen_amount > 0:
                    stolen[resource] = stolen_amount
                    
                    # Remove from defender
                    self.db.consume_resources(defender_id, {resource: stolen_amount})
                    
                    # Add to attacker
                    self.db.add_resources(attacker_id, resource, stolen_amount)
        
        return stolen
    
    def generate_battle_message(self, attacker, defender, battle_result, consequences):
        """Generate detailed battle report message"""
        if battle_result['attacker_wins']:
            message = f"🎯 حمله موفق!\n\n"
            message += f"🏴 {attacker['country_name']} با موفقیت به {defender['country_name']} حمله کرد!\n\n"
            
            message += "💥 تلفات:\n"
            message += f"⚔️ {defender['country_name']}: {consequences['defender_losses']['soldiers']} سرباز\n"
            message += f"🛡 {attacker['country_name']}: {consequences['attacker_losses']['soldiers']} سرباز\n\n"
            
            if consequences.get('resources_stolen'):
                message += "💰 منابع غارت شده:\n"
                for resource, amount in consequences['resources_stolen'].items():
                    message += f"• {resource}: {amount:,}\n"
        else:
            message = f"🛡 دفاع موفق!\n\n"
            message += f"🏴 {defender['country_name']} حمله {attacker['country_name']} را دفع کرد!\n\n"
            
            message += "💥 تلفات:\n"
            message += f"⚔️ {attacker['country_name']}: {consequences['attacker_losses']['soldiers']} سرباز\n"
            message += f"🛡 {defender['country_name']}: {consequences['defender_losses']['soldiers']} سرباز\n"
        
        return message
    
    def log_battle(self, attacker_id, defender_id, battle_result, consequences):
        """Log battle in database"""
        # This would save detailed battle information to database
        # Implementation depends on your wars table structure
        pass
