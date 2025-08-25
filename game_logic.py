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

    def build_structure(self, user_id, building_type, quantity=1):
        """Build a structure"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد!'}

        building_config = Config.BUILDINGS.get(building_type)
        if not building_config:
            return {'success': False, 'message': 'نوع ساختمان نامعتبر!'}

        total_cost = building_config['cost'] * quantity

        if player['money'] < total_cost:
            return {
                'success': False,
                'message': f"پول کافی ندارید! نیاز: ${total_cost:,}, موجودی: ${player['money']:,}"
            }

        # Deduct money and add building
        new_money = player['money'] - total_cost
        self.db.update_player_money(user_id, new_money)

        # Add building to database
        buildings = self.db.get_player_buildings(user_id)
        if buildings is None:
            buildings = {}
        current_count = buildings.get(building_type, 0)
        self.db.set_player_building(user_id, building_type, current_count + quantity)

        # Check if first build for news
        is_first_build = self.db.check_first_build(user_id, building_type)
        if is_first_build:
            self.db.record_first_build(user_id, building_type)

        return {
            'success': True,
            'message': f"✅ {quantity} {building_config['name']} با موفقیت ساخته شد!",
            'building_name': building_config['name'],
            'remaining_money': new_money,
            'is_first_build': is_first_build
        }

    def produce_weapon(self, user_id, weapon_type, quantity=1):
        """Produce weapons"""
        # Check if weapon type exists in config
        if weapon_type not in Config.WEAPONS:
            available_weapons = list(Config.WEAPONS.keys())[:10]  # Show first 10 weapons for debugging
            return {'success': False, 'message': f'نوع سلاح نامعتبر: {weapon_type}\nسلاح‌های موجود: {", ".join(available_weapons)}'}

        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد!'}

        weapon_config = Config.WEAPONS[weapon_type]

        if quantity <= 0:
            return {'success': False, 'message': 'تعداد باید بیشتر از صفر باشد!'}

        total_cost = weapon_config.get('cost', 0) * quantity
        weapon_name = weapon_config.get('name', weapon_type)
        required_resources = weapon_config.get('resources', {})

        # Check weapon factory requirement
        weapon_requirements = weapon_config.get('requirements', [])
        if 'weapon_factory' in weapon_requirements:
            buildings = self.db.get_player_buildings(user_id)
            if buildings.get('weapon_factory', 0) == 0:
                return {'success': False, 'message': 'برای تولید سلاح به کارخانه اسلحه نیاز دارید!'}

        # Check money
        if player['money'] < total_cost:
            return {
                'success': False,
                'message': f'پول کافی ندارید! نیاز: ${total_cost:,} برای {quantity} عدد، موجود: ${player["money"]:,}'
            }

        # Separate weapon requirements from resource requirements
        weapon_requirements = {}
        resource_requirements = {}

        for item, amount in required_resources.items():
            if item in Config.WEAPONS:
                weapon_requirements[item] = amount * quantity
            else:
                resource_requirements[item] = amount * quantity

        # Check weapon requirements
        if weapon_requirements:
            current_weapons = self.db.get_player_weapons(user_id)
            for req_weapon, req_amount in weapon_requirements.items():
                current_amount = current_weapons.get(req_weapon, 0)
                if current_amount < req_amount:
                    req_weapon_name = Config.WEAPONS[req_weapon].get('name', req_weapon)
                    return {
                        'success': False,
                        'message': f'سلاح مورد نیاز کافی نیست! نیاز: {req_amount} {req_weapon_name}, موجود: {current_amount}'
                    }

        # Check resource requirements
        if resource_requirements:
            current_resources = self.db.get_player_resources(user_id)
            for resource, req_amount in resource_requirements.items():
                current_amount = current_resources.get(resource, 0)
                if current_amount < req_amount:
                    resource_name = Config.RESOURCES.get(resource, {}).get('name', resource)
                    return {
                        'success': False,
                        'message': f'منبع کافی نیست! نیاز: {req_amount} {resource_name}, موجود: {current_amount}'
                    }

        # Consume required resources
        if resource_requirements:
            for resource, amount in resource_requirements.items():
                self.db.consume_resources(user_id, {resource: amount})

        # Consume required weapons
        if weapon_requirements:
            for req_weapon, amount in weapon_requirements.items():
                current_count = self.db.get_weapon_count(user_id, req_weapon)
                new_count = current_count - amount
                self.db.update_weapon_count(user_id, req_weapon, new_count)

        # Deduct money
        new_money = player['money'] - total_cost
        self.db.update_player_money(user_id, new_money)

        # Add produced weapons
        self.db.add_weapon(user_id, weapon_type, quantity)

        return {
            'success': True,
            'message': f'{weapon_name} با موفقیت تولید شد! تعداد: {quantity}',
            'weapon_name': weapon_name,
            'quantity': quantity,
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
        self.db.update_player_income(attacker_id, defender['money'], defender['population'], new_soldiers)

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