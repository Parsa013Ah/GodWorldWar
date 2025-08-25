import logging
from config import Config

logger = logging.getLogger(__name__)

class Economy:
    def __init__(self, database):
        self.db = database

    def calculate_income(self, user_id):
        """Calculate 6-hour income from buildings"""
        buildings = self.db.get_player_buildings(user_id)
        total_income = 0

        for building_type, count in buildings.items():
            if building_type in Config.BUILDINGS and count > 0:
                building_config = Config.BUILDINGS[building_type]
                building_income = building_config.get('income', 0)
                total_income += building_income * count

        return total_income

    def calculate_population_increase(self, user_id):
        """Calculate population increase from farms"""
        buildings = self.db.get_player_buildings(user_id)
        wheat_farms = buildings.get('wheat_farm', 0)

        return wheat_farms * 10000  # Each farm adds 10,000 population

    def calculate_soldier_increase(self, user_id):
        """Calculate soldier increase from military bases"""
        buildings = self.db.get_player_buildings(user_id)
        military_bases = buildings.get('military_base', 0)
        return military_bases * 5000  # Each base produces 5000 soldiers per cycle

    def update_player_income(self, user_id, new_money, new_population, new_soldiers):
        """Update player income data"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET money = ?, population = ?, soldiers = ?
                WHERE user_id = ?
            ''', (new_money, new_population, new_soldiers, user_id))
            conn.commit()

    def distribute_mine_resources(self, user_id):
        """Distribute resources from mines"""
        buildings = self.db.get_player_buildings(user_id)

        resource_production = {
            'iron_mine': ('iron', 1000),
            'copper_mine': ('copper', 800),
            'oil_mine': ('oil', 600),
            'gas_mine': ('gas', 700),
            'aluminum_mine': ('aluminum', 500),
            'gold_mine': ('gold', 200),
            'uranium_mine': ('uranium', 100),
            'lithium_mine': ('lithium', 300),
            'coal_mine': ('coal', 1200),
            'silver_mine': ('silver', 400),
            'nitro_mine': ('nitro', 100),
            'sulfur_mine': ('sulfur', 150),
            'titanium_mine': ('titanium', 3)
        }

        for building_type, (resource_type, production_amount) in resource_production.items():
            mine_count = buildings.get(building_type, 0)
            if mine_count > 0:
                total_production = production_amount * mine_count
                self.db.add_resources(user_id, resource_type, total_production)

        # Convert oil to fuel in refineries
        refineries = buildings.get('refinery', 0)
        if refineries > 0:
            player_resources = self.db.get_player_resources(user_id)
            oil_available = player_resources.get('oil', 0)

            # Each refinery can process 500 oil to fuel per cycle
            max_processing = refineries * 500
            oil_to_process = min(oil_available, max_processing)

            if oil_to_process > 0:
                # Convert oil to fuel (1:1 ratio)
                self.db.consume_resources(user_id, {'oil': oil_to_process})
                self.db.add_resources(user_id, 'fuel', oil_to_process)

    def get_income_report(self, user_id):
        """Get detailed income report"""
        buildings = self.db.get_player_buildings(user_id)

        report = "📊 گزارش درآمد شش‌ساعته:\n\n"
        total_income = 0

        # Building income
        for building_type, count in buildings.items():
            if building_type in Config.BUILDINGS and count > 0:
                building_config = Config.BUILDINGS[building_type]
                building_income = building_config.get('income', 0) * count
                if building_income > 0:
                    building_name = building_config['name']
                    report += f"💰 {building_name} ({count}x): ${building_income:,}\n"
                    total_income += building_income

        report += f"\n💵 درآمد کل: ${total_income:,}\n\n"

        # Resource production
        report += "📦 تولید منابع:\n"
        resource_production = {
            'iron_mine': ('iron', 1000, '🔩'),
            'copper_mine': ('copper', 800, '🥉'),
            'oil_mine': ('oil', 600, '🛢'),
            'gas_mine': ('gas', 700, '⛽'),
            'aluminum_mine': ('aluminum', 500, '🔗'),
            'gold_mine': ('gold', 200, '🏆'),
            'uranium_mine': ('uranium', 100, '☢️'),
            'lithium_mine': ('lithium', 300, '🔋'),
            'coal_mine': ('coal', 1200, '⚫'),
            'silver_mine': ('silver', 400, '🥈')
        }

        for building_type, (resource_type, production, emoji) in resource_production.items():
            mine_count = buildings.get(building_type, 0)
            if mine_count > 0:
                total_production = production * mine_count
                resource_name = Config.RESOURCES[resource_type]['name']
                report += f"{emoji} {resource_name}: +{total_production:,}\n"

        # Population and soldiers
        population_increase = self.calculate_population_increase(user_id)
        soldier_increase = self.calculate_soldier_increase(user_id)

        if population_increase > 0:
            report += f"\n👥 افزایش جمعیت: +{population_increase:,}"

        if soldier_increase > 0:
            report += f"\n⚔️ آموزش سرباز: +{soldier_increase:,}"

        return report

    def get_building_requirements_text(self, building_type):
        """Get building requirements text"""
        if building_type not in Config.BUILDINGS:
            return "ساختمان نامعتبر"

        building_config = Config.BUILDINGS[building_type]
        text = f"🏗 {building_config['name']}\n"
        text += f"💰 هزینه: ${building_config['cost']:,}\n"

        if 'income' in building_config:
            text += f"💵 درآمد هر 6 ساعت: ${building_config['income']:,}\n"

        if 'resource' in building_config:
            resource_name = Config.RESOURCES[building_config['resource']]['name']
            text += f"📦 تولید: {resource_name}\n"

        if 'population_increase' in building_config:
            text += f"👥 افزایش جمعیت: +{building_config['population_increase']:,}\n"

        if 'soldier_production' in building_config:
            text += f"⚔️ تولید سرباز: {building_config['soldier_production']:,} در 6 ساعت\n"

        if 'requirements' in building_config:
            req_names = []
            for req in building_config['requirements']:
                req_name = Config.BUILDINGS.get(req, {}).get('name', req)
                req_names.append(req_name)
            text += f"⚠️ نیازمندی: {', '.join(req_names)}\n"

        return text

    def can_afford_building(self, user_id, building_type):
        """Check if player can afford building"""
        player = self.db.get_player(user_id)
        if not player:
            return False, "بازیکن یافت نشد"

        building_config = Config.BUILDINGS.get(building_type)
        if not building_config:
            return False, "نوع ساختمان نامعتبر"

        if player['money'] < building_config['cost']:
            return False, f"پول کافی ندارید! نیاز: ${building_config['cost']:,}"

        # Check requirements
        requirements = building_config.get('requirements', [])
        if requirements:
            buildings = self.db.get_player_buildings(user_id)
            for req in requirements:
                if buildings.get(req, 0) == 0:
                    req_name = Config.BUILDINGS.get(req, {}).get('name', req)
                    return False, f"ابتدا باید {req_name} بسازید"

        return True, "OK"

    def calculate_total_resource_value(self, user_id):
        """Calculate total value of all resources"""
        resources = self.db.get_player_resources(user_id)
        total_value = 0

        for resource_type, amount in resources.items():
            if resource_type in Config.RESOURCES and amount > 0:
                market_value = Config.RESOURCES[resource_type]['market_value']
                total_value += amount * market_value

        return total_value

    def get_economy_stats(self, user_id):
        """Get comprehensive economy statistics"""
        player = self.db.get_player(user_id)
        buildings = self.db.get_player_buildings(user_id)
        resources = self.db.get_player_resources(user_id)

        stats = {
            'money': player['money'],
            'population': player['population'],
            'soldiers': player['soldiers'],
            'total_income': self.calculate_income(user_id),
            'total_buildings': sum(buildings.values()),
            'resource_value': self.calculate_total_resource_value(user_id)
        }

        return stats