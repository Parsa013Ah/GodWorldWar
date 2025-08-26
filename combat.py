import logging
import random
from config import Config
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class CombatSystem:
    def __init__(self, database):
        self.db = database

    def can_attack_country(self, attacker_id, defender_id):
        """Check if attacker can attack defender based on distance and available weapons"""
        attacker = self.db.get_player(attacker_id)
        defender = self.db.get_player(defender_id)

        if not attacker or not defender:
            return False, "کشور یافت نشد"

        if attacker_id == defender_id:
            return False, "نمی‌توانید به خودتان حمله کنید"

        attacker_country = attacker['country_code']
        defender_country = defender['country_code']
        
        # Get player weapons
        weapons = self.db.get_player_weapons(attacker_id)
        
        # Check for range extenders
        has_tanker = weapons.get('tanker_aircraft', 0) > 0
        has_carrier = weapons.get('aircraft_carrier_transport', 0) > 0
        
        # Get available weapons for this distance (with range extension if applicable)
        available_weapons = Config.get_available_weapons_for_attack(
            attacker_country, defender_country, weapons, has_tanker, has_carrier
        )
        
        if not available_weapons:
            distance_type = Config.get_country_distance_type(attacker_country, defender_country)
            if distance_type == 'neighbor':
                return False, "تسلیحات کافی برای حمله به همسایه ندارید"
            elif distance_type == 'regional':
                if has_tanker or has_carrier:
                    return False, "حتی با سوخت‌رسان/ناوبر، جت‌های شما برد کافی ندارند"
                else:
                    return False, "برای حمله منطقه‌ای نیاز به جت یا موشک دارید"
            else:
                if has_tanker or has_carrier:
                    return False, "حتی با سوخت‌رسان/ناوبر، فاصله خیلی زیاد است"
                else:
                    return False, "برای حمله بین‌قاره‌ای فقط موشک‌های دوربرد استفاده کنید"
        
        range_bonus_text = ""
        if has_carrier and has_tanker:
            range_bonus_text = " (با ناوبر و سوخت‌رسان)"
        elif has_carrier:
            range_bonus_text = " (با ناوبر)"
        elif has_tanker:
            range_bonus_text = " (با سوخت‌رسان)"
            
        return True, f"حمله مجاز - {len(available_weapons)} نوع سلاح در دسترس{range_bonus_text}"

    def are_neighbors(self, country1, country2):
        """Check if two countries are neighbors"""
        neighbors = Config.COUNTRY_NEIGHBORS.get(country1, [])
        return country2 in neighbors

    def get_country_region(self, country_code):
        """Get the region of a country"""
        for region, countries in Config.COUNTRY_DISTANCE_CATEGORY.items():
            if country_code in countries:
                return region
        return 'unknown'

    def calculate_travel_time(self, attacker_id, attacker_country, defender_country):
        """Calculate travel time for attack based on distance and equipment"""
        base_time = 0

        # Check if neighbors (10 minutes)
        if self.are_neighbors(attacker_country, defender_country):
            base_time = Config.COMBAT_TIMING['neighbor_time']
        else:
            # Check if same region (25 minutes)
            attacker_region = self.get_country_region(attacker_country)
            defender_region = self.get_country_region(defender_country)

            if attacker_region == defender_region and attacker_region != 'unknown':
                base_time = Config.COMBAT_TIMING['regional_time']
            else:
                # Different continents (40 minutes)
                base_time = Config.COMBAT_TIMING['intercontinental_time']

        # Calculate speed bonuses from equipment
        weapons = self.db.get_player_weapons(attacker_id)
        speed_reduction = 0

        # Fast jets reduce travel time
        fast_jets = ['f22', 'f35', 'su57', 'j20', 'f15ex', 'su35s', 'fighter', 'jet']
        for jet_type in fast_jets:
            count = weapons.get(jet_type, 0)
            speed_reduction += count * Config.COMBAT_TIMING['speed_bonus_per_jet']

        # Transport equipment reduces travel time
        transport_equipment = ['cargo_helicopter', 'cargo_plane', 'stealth_transport', 'logistics_drone']
        for transport_type in transport_equipment:
            count = weapons.get(transport_type, 0)
            speed_reduction += count * Config.COMBAT_TIMING['speed_bonus_per_transport']

        # Apply speed reduction (minimum 5 minutes)
        final_time = max(5, base_time - speed_reduction)

        return int(final_time)

    def process_pending_attacks(self):
        """Process all pending attacks that are due"""
        pending_attacks = self.db.get_pending_attacks_due()

        results = []
        for attack in pending_attacks:
            try:
                # Mark as executing
                self.db.update_pending_attack_status(attack['id'], 'executing')

                # Execute the attack
                result = self.execute_attack(attack['attacker_id'], attack['defender_id'])

                # Mark as completed
                self.db.update_pending_attack_status(attack['id'], 'completed')

                results.append({
                    'attack_id': attack['id'],
                    'result': result,
                    'attacker_id': attack['attacker_id'],
                    'defender_id': attack['defender_id']
                })

            except Exception as e:
                logger.error(f"Error executing pending attack {attack['id']}: {e}")
                self.db.update_pending_attack_status(attack['id'], 'failed')

        return results

    def calculate_attack_power(self, user_id):
        """Calculate total attack power"""
        weapons = self.db.get_player_weapons(user_id)
        total_power = 0

        # Only offensive weapons count for attack
        for weapon_type, count in weapons.items():
            if weapon_type != 'user_id' and count > 0:
                # Check if weapon exists in config
                if weapon_type in Config.WEAPONS:
                    weapon_info = Config.WEAPONS[weapon_type]
                    
                    # Skip transport and pure defense weapons
                    if weapon_info.get('category') in ['transport', 'defense']:
                        continue
                        
                    # Skip specific defensive weapons
                    if weapon_type in ['air_defense', 'missile_shield', 'cyber_shield', 
                                      's500_defense', 'thaad_defense', 's400_defense',
                                      'iron_dome', 'slq32_ew', 'phalanx_ciws']:
                        continue
                    
                    weapon_power = weapon_info.get('power', 0)
                    total_power += weapon_power * count

        return total_power

    def calculate_defense_power(self, user_id):
        """Calculate total defense power"""
        weapons = self.db.get_player_weapons(user_id)
        defense_power = 0

        # Defense weapons
        defense_weapons = ['air_defense', 'missile_shield', 'cyber_shield', 's500_defense',
                          'thaad_defense', 's400_defense', 'iron_dome', 'slq32_ew', 'phalanx_ciws']

        for weapon_type in defense_weapons:
            count = weapons.get(weapon_type, 0)
            if count > 0 and weapon_type in Config.WEAPONS:
                weapon_power = Config.WEAPONS[weapon_type]['power']
                defense_power += weapon_power * count

        # Add some defensive value from other weapons
        for weapon_type, count in weapons.items():
            if weapon_type not in defense_weapons and weapon_type != 'user_id' and count > 0:
                if weapon_type in Config.WEAPONS:
                    weapon_power = Config.WEAPONS[weapon_type]['power']
                    defense_power += weapon_power * count * 0.3  # 30% defensive value

        return defense_power

    def calculate_military_power(self, user_id):
        """Calculate total military power for display purposes"""
        weapons = self.db.get_player_weapons(user_id)
        total_power = 0

        # Calculate total power from all weapons
        for weapon_type, count in weapons.items():
            if weapon_type != 'user_id' and count > 0:
                if weapon_type in Config.WEAPONS:
                    weapon_power = Config.WEAPONS[weapon_type]['power']
                    total_power += weapon_power * count

        return total_power

    def schedule_delayed_attack(self, attacker_id, defender_id, attack_type="mixed"):
        """Schedule a delayed attack based on travel time"""
        can_attack, reason = self.can_attack_country(attacker_id, defender_id)
        if not can_attack:
            return {'success': False, 'message': reason}

        attacker = self.db.get_player(attacker_id)
        defender = self.db.get_player(defender_id)

        # Calculate travel time
        travel_time = self.calculate_travel_time(attacker_id, attacker['country_code'], defender['country_code'])
        attack_time = datetime.now() + timedelta(minutes=travel_time)

        # Create pending attack
        attack_data = {
            'attacker_id': attacker_id,
            'defender_id': defender_id,
            'attack_type': attack_type,
            'travel_time': travel_time,
            'attack_time': attack_time.isoformat(),
            'status': 'traveling'
        }

        attack_id = self.db.create_pending_attack(attack_data)

        return {
            'success': True,
            'attack_id': attack_id,
            'travel_time': travel_time,
            'attack_time': attack_time,
            'message': f'نیروهای شما به سمت {defender["country_name"]} در حرکت هستند! زمان رسیدن: {travel_time} دقیقه'
        }

    def execute_attack(self, attacker_id, defender_id):
        """Execute attack between countries"""
        can_attack, reason = self.can_attack_country(attacker_id, defender_id)
        if not can_attack:
            return {'success': False, 'message': reason}

        attacker = self.db.get_player(attacker_id)
        defender = self.db.get_player(defender_id)

        attack_power = self.calculate_attack_power(attacker_id)
        defense_power = self.calculate_defense_power(defender_id)

        if attack_power == 0:
            return {'success': False, 'message': 'شما هیچ تسلیحاتی برای حمله ندارید!'}

        # Battle calculation with randomness
        random_factor = random.uniform(0.8, 1.2)
        effective_attack = attack_power * random_factor
        effective_defense = defense_power * random.uniform(0.9, 1.1)

        damage = effective_attack - effective_defense

        result = {
            'attacker_country': attacker['country_name'],
            'defender_country': defender['country_name'],
            'attack_power': attack_power,
            'defense_power': defense_power,
            'damage': damage,
            'attacker_losses': {},
            'defender_losses': {},
            'stolen_resources': {}
        }

        if damage > 0:
            # Attack successful
            result['success'] = True
            result['winner'] = attacker['country_name']

            # Apply battle consequences
            self._apply_successful_attack(attacker_id, defender_id, damage, result)

        else:
            # Attack failed
            result['success'] = False
            result['winner'] = defender['country_name']

            # Attacker suffers losses
            self._apply_failed_attack(attacker_id, abs(damage), result)

        # Log the war
        self._log_war(attacker_id, defender_id, result)

        return result

    def _apply_successful_attack(self, attacker_id, defender_id, damage, result):
        """Apply consequences of successful attack"""
        defender = self.db.get_player(defender_id)
        defender_resources = self.db.get_player_resources(defender_id)
        defender_weapons = self.db.get_player_weapons(defender_id)
        defender_buildings = self.db.get_player_buildings(defender_id)

        # Calculate attack and defense power for percentage calculations
        attack_power = self.calculate_attack_power(attacker_id)
        defense_power = self.calculate_defense_power(defender_id)
        
        # Calculate power ratio for determining loot and destruction percentages
        if defense_power > 0:
            power_ratio = attack_power / defense_power
        else:
            power_ratio = float('inf')  # No defense means maximum damage

        # Calculate resource loot percentage (10% to 75%)
        if power_ratio <= 0.5:
            loot_percentage = 0.10  # Weak attack vs strong defense
        elif power_ratio <= 1.0:
            loot_percentage = 0.15
        elif power_ratio <= 1.5:
            loot_percentage = 0.25
        elif power_ratio <= 2.0:
            loot_percentage = 0.35
        elif power_ratio <= 3.0:
            loot_percentage = 0.45
        elif power_ratio <= 5.0:
            loot_percentage = 0.55
        elif power_ratio <= 10.0:
            loot_percentage = 0.65
        else:
            # Very powerful attack (like 10+ Trident II nuclear missiles)
            loot_percentage = 0.75

        # Calculate building destruction percentage (5% to 60%)
        if power_ratio <= 0.5:
            destruction_percentage = 0.05
        elif power_ratio <= 1.0:
            destruction_percentage = 0.08
        elif power_ratio <= 1.5:
            destruction_percentage = 0.12
        elif power_ratio <= 2.0:
            destruction_percentage = 0.18
        elif power_ratio <= 3.0:
            destruction_percentage = 0.25
        elif power_ratio <= 5.0:
            destruction_percentage = 0.35
        elif power_ratio <= 10.0:
            destruction_percentage = 0.45
        else:
            # Very powerful attack
            destruction_percentage = 0.60

        # Apply soldier losses
        soldier_losses = min(defender['soldiers'], int(damage * 100))
        
        # Enhanced weapon losses based on power ratio
        weapon_loss_chance = min(0.4, 0.1 + (power_ratio * 0.05))
        for weapon_type, count in defender_weapons.items():
            if count > 0 and random.random() < weapon_loss_chance:
                loss_percentage = min(0.3, 0.05 + (power_ratio * 0.03))
                losses = min(count, max(1, int(count * loss_percentage)))
                result['defender_losses'][weapon_type] = losses
                # Remove weapons from defender
                new_count = count - losses
                self.db.update_weapon_count(defender_id, weapon_type, new_count)

        # Steal resources based on calculated percentage
        for resource_type, amount in defender_resources.items():
            if resource_type != 'user_id' and amount > 0:
                steal_amount = int(amount * loot_percentage)
                if steal_amount > 0:
                    result['stolen_resources'][resource_type] = steal_amount
                    # Transfer resources
                    self.db.add_resources(attacker_id, resource_type, steal_amount)
                    self.db.consume_resources(defender_id, {resource_type: steal_amount})

        # Destroy buildings (mines and refineries)
        result['destroyed_buildings'] = {}
        destructible_buildings = ['iron_mine', 'copper_mine', 'oil_mine', 'gas_mine', 
                                'aluminum_mine', 'gold_mine', 'uranium_mine', 'lithium_mine',
                                'coal_mine', 'silver_mine', 'nitro_mine', 'sulfur_mine', 
                                'titanium_mine', 'refinery']
        
        for building_type in destructible_buildings:
            building_count = defender_buildings.get(building_type, 0)
            if building_count > 0:
                destroyed_count = max(1, int(building_count * destruction_percentage))
                destroyed_count = min(destroyed_count, building_count)
                
                if destroyed_count > 0:
                    result['destroyed_buildings'][building_type] = destroyed_count
                    new_count = building_count - destroyed_count
                    self.db.update_building_count(defender_id, building_type, new_count)

        # Update defender soldiers
        new_soldiers = max(0, defender['soldiers'] - soldier_losses)
        self.db.update_player_soldiers(defender_id, new_soldiers)
        result['defender_losses']['soldiers'] = soldier_losses
        result['loot_percentage'] = loot_percentage * 100
        result['destruction_percentage'] = destruction_percentage * 100
        result['power_ratio'] = power_ratio

    def _apply_failed_attack(self, attacker_id, damage, result):
        """Apply consequences of failed attack"""
        attacker = self.db.get_player(attacker_id)
        attacker_weapons = self.db.get_player_weapons(attacker_id)

        # Attacker losses
        soldier_losses = min(attacker['soldiers'], int(damage * 50))
        weapon_loss_chance = 0.15

        # Attacker weapon losses
        for weapon_type, count in attacker_weapons.items():
            if count > 0 and random.random() < weapon_loss_chance:
                losses = min(count, max(1, int(count * 0.05)))
                result['attacker_losses'][weapon_type] = losses
                # Remove weapons from attacker
                new_count = count - losses
                self.db.update_weapon_count(attacker_id, weapon_type, new_count)

        # Update attacker soldiers
        new_soldiers = max(0, attacker['soldiers'] - soldier_losses)
        self.db.update_player_soldiers(attacker_id, new_soldiers)
        result['attacker_losses']['soldiers'] = soldier_losses

    def _log_war(self, attacker_id, defender_id, result):
        """Log war in database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wars (attacker_id, defender_id, attack_power, defense_power, result, damage_dealt)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    attacker_id, defender_id,
                    result['attack_power'], result['defense_power'],
                    'success' if result['success'] else 'failed',
                    result['damage']
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging war: {e}")

    def get_available_targets(self, attacker_id):
        """Get list of countries that can be attacked"""
        all_players = self.db.get_all_players()
        available_targets = []

        for player in all_players:
            if player['user_id'] != attacker_id:
                can_attack, reason = self.can_attack_country(attacker_id, player['user_id'])
                if can_attack:
                    available_targets.append(player)

        return available_targets

    def format_battle_report(self, result):
        """Format battle report for display"""
        attacker_flag = ""
        defender_flag = ""

        # Find flags
        for code, name in Config.COUNTRIES.items():
            if name == result['attacker_country']:
                attacker_flag = Config.COUNTRY_FLAGS.get(code, '🏳')
            elif name == result['defender_country']:
                defender_flag = Config.COUNTRY_FLAGS.get(code, '🏳')

        report = f"""⚔️ گزارش جنگ

{attacker_flag} {result['attacker_country']} VS {defender_flag} {result['defender_country']}

🔥 قدرت حمله: {result['attack_power']:,}
🛡 قدرت دفاع: {result['defense_power']:,}
💥 خسارت: {result['damage']:,.0f}

🏆 برنده: {result['winner']}
"""

        if result['success']:
            # Show power ratio and percentages
            if 'power_ratio' in result:
                if result['power_ratio'] == float('inf'):
                    report += f"\n📊 نسبت قدرت: بی‌نهایت (بدون دفاع)\n"
                else:
                    report += f"\n📊 نسبت قدرت: {result['power_ratio']:.2f}:1\n"
            
            if 'loot_percentage' in result:
                report += f"💰 درصد غارت: {result['loot_percentage']:.0f}%\n"
            
            if 'destruction_percentage' in result:
                report += f"💥 درصد تخریب: {result['destruction_percentage']:.0f}%\n"

            if result['stolen_resources']:
                report += "\n💰 منابع غارت شده:\n"
                total_value = 0
                for resource, amount in result['stolen_resources'].items():
                    resource_name = Config.RESOURCES.get(resource, {}).get('name', resource)
                    report += f"• {resource_name}: {amount:,}\n"

            if result.get('destroyed_buildings'):
                report += "\n🏭 ساختمان‌های تخریب شده:\n"
                for building_type, count in result['destroyed_buildings'].items():
                    building_name = Config.BUILDINGS.get(building_type, {}).get('name', building_type)
                    report += f"• {building_name}: {count:,}\n"

            if result['defender_losses']:
                report += "\n💀 تلفات مدافع:\n"
                for loss_type, amount in result['defender_losses'].items():
                    if loss_type == 'soldiers':
                        report += f"• سربازان: {amount:,}\n"
                    else:
                        weapon_name = Config.WEAPONS.get(loss_type, {}).get('name', loss_type)
                        report += f"• {weapon_name}: {amount:,}\n"
        else:
            if result['attacker_losses']:
                report += "\n💀 تلفات مهاجم:\n"
                for loss_type, amount in result['attacker_losses'].items():
                    if loss_type == 'soldiers':
                        report += f"• سربازان: {amount:,}\n"
                    else:
                        weapon_name = Config.WEAPONS.get(loss_type, {}).get('name', loss_type)
                        report += f"• {weapon_name}: {amount:,}\n"

        return report