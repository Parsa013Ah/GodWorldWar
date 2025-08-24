import logging
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class Economy:
    def __init__(self, database):
        self.db = database
    
    def calculate_income(self, user_id):
        """Calculate 6-hour income for a player"""
        buildings = self.db.get_player_buildings(user_id)
        total_income = 0
        
        # Income from mines (40% of building cost every 6 hours)
        mine_types = [
            'iron_mine', 'copper_mine', 'oil_mine', 'gas_mine', 'aluminum_mine',
            'gold_mine', 'uranium_mine', 'lithium_mine', 'coal_mine', 'silver_mine'
        ]
        
        for mine_type in mine_types:
            count = buildings.get(mine_type, 0)
            if count > 0 and mine_type in Config.BUILDINGS:
                building_cost = Config.BUILDINGS[mine_type]['cost']
                income_per_mine = int(building_cost * 0.4)  # 40% of cost
                total_income += income_per_mine * count
        
        logger.info(f"Calculated income for user {user_id}: ${total_income}")
        return total_income
    
    def calculate_population_increase(self, user_id):
        """Calculate population increase from wheat farms"""
        buildings = self.db.get_player_buildings(user_id)
        wheat_farms = buildings.get('wheat_farm', 0)
        
        # Each wheat farm adds 10,000 population every 6 hours
        population_increase = wheat_farms * 10000
        
        return population_increase
    
    def calculate_soldier_increase(self, user_id):
        """Calculate soldier increase from military bases"""
        buildings = self.db.get_player_buildings(user_id)
        military_bases = buildings.get('military_base', 0)
        player = self.db.get_player(user_id)
        
        # Each military base converts 5,000 population to soldiers every 6 hours
        potential_soldiers = military_bases * 5000
        
        # Can't exceed available population
        available_population = player['population'] - player['soldiers']
        actual_soldiers = min(potential_soldiers, available_population)
        
        return max(0, actual_soldiers)
    
    def distribute_mine_resources(self, user_id):
        """Distribute resources from mines"""
        buildings = self.db.get_player_buildings(user_id)
        
        # Resource production rates (per mine per 6 hours)
        mine_production = {
            'iron_mine': ('iron', 1000),
            'copper_mine': ('copper', 800),
            'oil_mine': ('oil', 1200),
            'gas_mine': ('gas', 1000),
            'aluminum_mine': ('aluminum', 900),
            'gold_mine': ('gold', 500),
            'uranium_mine': ('uranium', 200),
            'lithium_mine': ('lithium', 300),
            'coal_mine': ('coal', 1500),
            'silver_mine': ('silver', 400)
        }
        
        for mine_type, (resource, production) in mine_production.items():
            count = buildings.get(mine_type, 0)
            if count > 0:
                total_production = production * count
                self.db.add_resources(user_id, resource, total_production)
                logger.info(f"Added {total_production} {resource} to user {user_id}")
    
    def process_refinery_operations(self, user_id):
        """Process oil refinery operations"""
        buildings = self.db.get_player_buildings(user_id)
        refineries = buildings.get('refinery', 0)
        
        if refineries > 0:
            resources = self.db.get_player_resources(user_id)
            oil_available = resources.get('oil', 0)
            
            # Each refinery can process 500 oil to 400 fuel per 6 hours
            processing_capacity = refineries * 500
            oil_to_process = min(oil_available, processing_capacity)
            
            if oil_to_process > 0:
                fuel_produced = int(oil_to_process * 0.8)  # 80% conversion rate
                
                # Consume oil and produce fuel
                self.db.consume_resources(user_id, {'oil': oil_to_process})
                self.db.add_resources(user_id, 'fuel', fuel_produced)
                
                logger.info(f"Refined {oil_to_process} oil to {fuel_produced} fuel for user {user_id}")
    
    def calculate_building_requirements(self, building_type):
        """Get building requirements and costs"""
        if building_type not in Config.BUILDINGS:
            return None
        
        building_info = Config.BUILDINGS[building_type]
        
        requirements = {
            'cost': building_info['cost'],
            'name': building_info['name'],
            'description': building_info.get('description', ''),
            'special_requirements': []
        }
        
        # Special requirements for certain buildings
        if building_type == 'weapon_factory':
            requirements['special_requirements'].append('نیروگاه (برای تأمین برق)')
        elif building_type == 'refinery':
            requirements['special_requirements'].append('نیروگاه (برای تأمین برق)')
        
        return requirements
    
    def calculate_weapon_requirements(self, weapon_type):
        """Get weapon production requirements"""
        if weapon_type not in Config.WEAPONS:
            return None
        
        weapon_info = Config.WEAPONS[weapon_type]
        
        requirements = {
            'cost': weapon_info['cost'],
            'name': weapon_info['name'],
            'resources': weapon_info['resources'],
            'power': weapon_info['power'],
            'range': weapon_info.get('range', 0),
            'type': weapon_info.get('type', 'ground')
        }
        
        return requirements
    
    def get_resource_market_value(self, resource_type):
        """Get market value of resources for trading"""
        # Base market values per unit
        market_values = {
            'iron': 10,
            'copper': 12,
            'oil': 15,
            'gas': 13,
            'aluminum': 11,
            'gold': 50,
            'uranium': 100,
            'lithium': 80,
            'coal': 8,
            'silver': 45,
            'fuel': 20
        }
        
        return market_values.get(resource_type, 1)
    
    def calculate_convoy_time(self, sender_country, receiver_country, cargo_size):
        """Calculate convoy travel time based on distance and cargo"""
        # Base travel time calculation
        base_time_hours = 2  # Minimum 2 hours
        
        # Distance factor (simplified)
        distance_factor = 1.0
        if sender_country != receiver_country:
            distance_factor = 1.5  # 50% longer for international transfers
        
        # Cargo factor (larger shipments take longer)
        cargo_factor = max(1.0, cargo_size / 10000)  # Factor based on cargo size
        
        total_time = base_time_hours * distance_factor * cargo_factor
        return max(1, int(total_time))  # Minimum 1 hour
    
    def get_economic_report(self, user_id):
        """Generate comprehensive economic report"""
        player = self.db.get_player(user_id)
        buildings = self.db.get_player_buildings(user_id)
        resources = self.db.get_player_resources(user_id)
        
        # Calculate various metrics
        income = self.calculate_income(user_id)
        population_growth = self.calculate_population_increase(user_id)
        soldier_production = self.calculate_soldier_increase(user_id)
        
        # Calculate total resource value
        total_resource_value = 0
        for resource, amount in resources.items():
            if resource != 'user_id':
                market_value = self.get_resource_market_value(resource)
                total_resource_value += amount * market_value
        
        # Calculate building value
        total_building_value = 0
        for building, count in buildings.items():
            if building != 'user_id' and building in Config.BUILDINGS:
                building_cost = Config.BUILDINGS[building]['cost']
                total_building_value += building_cost * count
        
        report = {
            'country_name': player['country_name'],
            'total_wealth': player['money'] + total_resource_value + total_building_value,
            'liquid_money': player['money'],
            'resource_value': total_resource_value,
            'building_value': total_building_value,
            'income_per_cycle': income,
            'population_growth': population_growth,
            'soldier_production': soldier_production,
            'economic_power_rank': 0  # Would need to compare with other players
        }
        
        return report
    
    def validate_resource_transfer(self, sender_id, resources_to_send):
        """Validate if player can send specified resources"""
        sender_resources = self.db.get_player_resources(sender_id)
        
        for resource, amount in resources_to_send.items():
            if sender_resources.get(resource, 0) < amount:
                return False, f"منابع کافی ندارید: {resource}"
        
        return True, "منابع قابل ارسال"
    
    def execute_resource_transfer(self, sender_id, receiver_id, resources):
        """Execute resource transfer between players"""
        # Validate transfer
        valid, message = self.validate_resource_transfer(sender_id, resources)
        if not valid:
            return {'success': False, 'message': message}
        
        # Execute transfer
        success = self.db.consume_resources(sender_id, resources)
        if success:
            for resource, amount in resources.items():
                self.db.add_resources(receiver_id, resource, amount)
            
            return {'success': True, 'message': 'انتقال منابع موفق بود'}
        else:
            return {'success': False, 'message': 'خطا در انتقال منابع'}
import logging
from config import Config

logger = logging.getLogger(__name__)

class Economy:
    def __init__(self, database):
        self.db = database
    
    def calculate_income(self, user_id):
        """Calculate player income from buildings"""
        buildings = self.db.get_player_buildings(user_id)
        total_income = 0
        
        for building_type, quantity in buildings.items():
            if building_type == 'user_id':
                continue
            
            building_config = Config.BUILDINGS.get(building_type, {})
            income_per_cycle = building_config.get('income_per_cycle', 0)
            total_income += income_per_cycle * quantity
        
        return total_income
    
    def calculate_population_increase(self, user_id):
        """Calculate population increase from wheat farms"""
        buildings = self.db.get_player_buildings(user_id)
        wheat_farms = buildings.get('wheat_farm', 0)
        
        return wheat_farms * 10000  # 10k per farm per cycle
    
    def calculate_soldier_increase(self, user_id):
        """Calculate soldier increase from military bases"""
        buildings = self.db.get_player_buildings(user_id)
        military_bases = buildings.get('military_base', 0)
        
        return military_bases * 5000  # 5k soldiers per base per cycle
    
    def distribute_mine_resources(self, user_id):
        """Distribute resources from mines"""
        buildings = self.db.get_player_buildings(user_id)
        
        for building_type, quantity in buildings.items():
            if building_type == 'user_id':
                continue
            
            building_config = Config.BUILDINGS.get(building_type, {})
            resource_production = building_config.get('resource_production')
            
            if resource_production:
                resource_type, amount_per_building = resource_production
                total_amount = amount_per_building * quantity
                
                if total_amount > 0:
                    self.db.add_resources(user_id, resource_type, total_amount)
    
    def can_afford_building(self, user_id, building_type):
        """Check if player can afford building"""
        player = self.db.get_player(user_id)
        building_cost = Config.get_building_cost(building_type)
        
        return player['money'] >= building_cost
    
    def can_afford_weapon(self, user_id, weapon_type):
        """Check if player can afford weapon"""
        player = self.db.get_player(user_id)
        weapon_config = Config.WEAPONS.get(weapon_type, {})
        
        # Check money
        weapon_cost = weapon_config.get('cost', 0)
        if player['money'] < weapon_cost:
            return False, "پول کافی ندارید"
        
        # Check resources
        required_resources = weapon_config.get('resources', {})
        current_resources = self.db.get_player_resources(user_id)
        
        for resource, amount in required_resources.items():
            if current_resources.get(resource, 0) < amount:
                return False, f"منابع کافی ندارید: {resource}"
        
        # Check weapon factory requirement
        buildings = self.db.get_player_buildings(user_id)
        if buildings.get('weapon_factory', 0) == 0:
            return False, "نیاز به کارخانه اسلحه دارید"
        
        return True, "قابل تولید"
