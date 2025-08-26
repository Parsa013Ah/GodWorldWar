"""
DragonRP Game Configuration
Contains all game constants, and specifications
"""

class Config:
    """Main configuration class for DragonRP game"""

    # Admin configuration
    ADMIN_CONFIG = {
        'default_admin_ids': [123456789, 5283015101]  # Replace with actual admin user IDs
    }

    # Countries with flags
    COUNTRIES = {
        'AR': 'آرژانتین',
        'IR': 'ایران',
        'JP': 'ژاپن',
        'RU': 'روسیه',
        'EG': 'مصر',
        'ES': 'اسپانیا',
        'US': 'آمریکا',
        'MX': 'مکزیک',
        'FR': 'فرانسه',
        'DE': 'آلمان',
        'BE': 'بلژیک',
        'CN': 'چین',
        'KP': 'کره شمالی',
        'TR': 'ترکیه',
        'CA': 'کانادا',
        'BR': 'برزیل',
        'IT': 'ایتالیا',
        'GB': 'انگلیس',
        'SA': 'عربستان',
        'PK': 'پاکستان',
        'AF': 'افغانستان',
        'IQ': 'عراق',
        'IN': 'هند',
        'AU': 'استرالیا'
    }

    # Country flags
    COUNTRY_FLAGS = {
        'AR': '🇦🇷', 'IR': '🇮🇷', 'JP': '🇯🇵', 'RU': '🇷🇺', 'EG': '🇪🇬',
        'ES': '🇪🇸', 'US': '🇺🇸', 'MX': '🇲🇽', 'FR': '🇫🇷', 'DE': '🇩🇪',
        'BE': '🇧🇪', 'CN': '🇨🇳', 'KP': '🇰🇵', 'TR': '🇹🇷', 'CA': '🇨🇦',
        'BR': '🇧🇷', 'IT': '🇮🇹', 'GB': '🇬🇧', 'SA': '🇸🇦', 'PK': '🇵🇰',
        'AF': '🇦🇫', 'IQ': '🇮🇶', 'IN': '🇮🇳', 'AU': '🇦🇺'
    }

    # Building costs and stats (Updated with provided prices)
    BUILDINGS = {
        'iron_mine': {'name': 'معدن آهن', 'cost': 80000, 'production': {'iron': 1000}, 'income': 50000},
        'copper_mine': {'name': 'معدن مس', 'cost': 100000, 'production': {'copper': 800}, 'income': 60000},
        'oil_mine': {'name': 'معدن نفت', 'cost': 120000, 'production': {'oil': 600}, 'income': 80000},
        'gas_mine': {'name': 'معدن گاز', 'cost': 110000, 'production': {'gas': 700}, 'income': 70000},
        'aluminum_mine': {'name': 'معدن آلومینیوم', 'cost': 90000, 'production': {'aluminum': 500}, 'income': 55000},
        'gold_mine': {'name': 'معدن طلا', 'cost': 150000, 'production': {'gold': 200}, 'income': 120000},
        'uranium_mine': {'name': 'معدن اورانیوم', 'cost': 690000, 'production': {'uranium': 18}, 'income': 276000},
        'lithium_mine': {'name': 'معدن لیتیوم', 'cost': 180000, 'production': {'lithium': 300}, 'income': 100000},
        'coal_mine': {'name': 'معدن زغال‌سنگ', 'cost': 85000, 'production': {'coal': 1200}, 'income': 45000},
        'silver_mine': {'name': 'معدن نقره', 'cost': 140000, 'production': {'silver': 400}, 'income': 90000},
        'nitro_mine': {'name': 'معدن نیتر', 'cost': 95000, 'production': {'nitro': 100}, 'income': 65000},
        'sulfur_mine': {'name': 'معدن گوگرد', 'cost': 75000, 'production': {'sulfur': 150}, 'income': 40000},
        'titanium_mine': {'name': 'معدن تیتانیوم', 'cost': 250000, 'production': {'titanium': 60}, 'income': 100000},
        'weapon_factory': {'name': 'کارخانه اسلحه', 'cost': 15000, 'production': {}},
        'refinery': {'name': 'پالایشگاه نفت', 'cost': 10000, 'production': {}},
        'power_plant': {'name': 'نیروگاه برق', 'cost': 9000, 'production': {}},
        'wheat_farm': {'name': 'مزرعه گندم', 'cost': 5000, 'population_bonus': 10000},
        'military_base': {'name': 'پادگان آموزشی', 'cost': 5000, 'soldier_bonus': 5000},
        'housing': {'name': 'مسکن', 'cost': 5000, 'capacity': 10000}
    }

    # Import weapons from modular system
    try:
        from weapons import ALL_WEAPONS, WEAPON_CATEGORIES
        WEAPONS = ALL_WEAPONS
        WEAPON_CATS = WEAPON_CATEGORIES
    except ImportError:
        # Fallback to basic weapons if modular system not available
        WEAPONS = {
            'rifle': {'name': 'تفنگ', 'cost': 1500, 'power': 5, 'range': 300, 'resources': {'iron': 5, 'copper': 2}, 'category': 'basic'},
            'tank': {'name': 'تانک', 'cost': 850000, 'power': 1200, 'range': 500, 'resources': {'iron': 50, 'copper': 15, 'aluminum': 10}, 'category': 'basic'},
            'helicopter': {'name': 'هلیکوپتر', 'cost': 2800000, 'power': 2400, 'range': 1500, 'resources': {'aluminum': 30, 'iron': 20, 'copper': 10}, 'category': 'air'},
        'jet': {'name': 'جت جنگی', 'cost': 4500000, 'power': 3200, 'range': 2000, 'resources': {'aluminum': 40, 'iron': 25, 'copper': 15, 'titanium': 5}, 'category': 'air'},
        'drone': {'name': 'پهپاد نظامی', 'cost': 180000, 'power': 800, 'range': 1000, 'resources': {'aluminum': 10, 'copper': 8, 'lithium': 5}, 'category': 'air'},

        # Naval weapons
        'warship': {'name': 'ناو جنگی', 'cost': 2500000, 'power': 3500, 'range': 1500, 'resources': {'iron': 100, 'aluminum': 50, 'copper': 30}, 'category': 'naval'},
        'submarine': {'name': 'زیردریایی', 'cost': 4200000, 'power': 4800, 'range': 2000, 'resources': {'iron': 80, 'aluminum': 40, 'uranium': 5}, 'category': 'naval'},
        'destroyer': {'name': 'ناوشکن', 'cost': 3800000, 'power': 5200, 'range': 1800, 'resources': {'iron': 90, 'aluminum': 45, 'copper': 25, 'titanium': 3}, 'category': 'naval'},
        'aircraft_carrier': {'name': 'ناو هواپیمابر', 'cost': 12500000, 'power': 15000, 'range': 2500, 'resources': {'iron': 200, 'aluminum': 100, 'titanium': 20, 'uranium': 10}, 'category': 'naval'},

        # Defense systems
        'air_defense': {'name': 'پدافند هوایی', 'cost': 1800000, 'power': 3200, 'defense_type': 'air', 'resources': {'iron': 40, 'aluminum': 25, 'copper': 15}, 'category': 'defense'},
        'missile_shield': {'name': 'سپر موشکی', 'cost': 2850000, 'power': 4500, 'defense_type': 'missile', 'resources': {'uranium': 3, 'iron': 20}, 'category': 'defense'},
        'cyber_shield': {'name': 'سپر سایبری', 'cost': 1200000, 'power': 2800, 'defense_type': 'cyber', 'resources': {'lithium': 10, 'copper': 8}, 'category': 'defense'},

        # Bombs
        'simple_bomb': {'name': 'بمب ساده', 'cost': 2000, 'power': 60, 'range': 0, 'resources': {'nitro': 10, 'copper': 10, 'iron': 20, 'sulfur': 20}, 'category': 'bombs'},
        'nuclear_bomb': {'name': 'بمب هسته‌ای ساده', 'cost': 60000, 'power': 2000, 'range': 0, 'resources': {'iron': 30, 'uranium': 6, 'sulfur': 36}, 'category': 'bombs'},

        # Basic missiles
        'simple_missile': {'name': 'موشک ساده', 'cost': 3000, 'power': 60, 'range': 500, 'resources': {'nitro': 10, 'copper': 10, 'iron': 20, 'sulfur': 20, 'coal': 10}, 'category': 'missiles'},
        'ballistic_missile': {'name': 'موشک بالستیک ساده', 'cost': 9000, 'power': 80, 'range': 2000, 'resources': {'nitro': 15, 'copper': 15, 'iron': 40, 'sulfur': 40, 'coal': 20}, 'category': 'missiles'},
        'nuclear_missile': {'name': 'موشک هسته‌ای ساده', 'cost': 9000, 'power': 2000, 'range': 2000, 'resources': {'nuclear_bomb': 1, 'ballistic_missile': 1, 'iron': 30, 'sulfur': 30}, 'category': 'missiles'},

        # Special missiles
        'trident2_conventional': {'name': 'Trident 2 غیر هسته‌ای', 'cost': 0, 'power': 1000, 'range': 5000, 'resources': {'simple_bomb': 13, 'ballistic_missile': 1, 'coal': 140}, 'category': 'special_missiles'},
        'trident2_nuclear': {'name': 'Trident 2 هسته‌ای', 'cost': 190000, 'power': 30000, 'range': 5000, 'resources': {'nuclear_bomb': 13, 'ballistic_missile': 1, 'coal': 140}, 'category': 'special_missiles'},
        'satan2_conventional': {'name': 'Satan2 غیر هسته‌ای', 'cost': 0, 'power': 940, 'range': 4500, 'resources': {'simple_bomb': 10, 'ballistic_missile': 1, 'coal': 140}, 'category': 'special_missiles'},
        'satan2_nuclear': {'name': 'Satan2 هسته‌ای', 'cost': 160000, 'power': 21000, 'range': 4500, 'resources': {'nuclear_bomb': 10, 'ballistic_missile': 1, 'coal': 140}, 'category': 'special_missiles'},
        'df41_nuclear': {'name': 'DF-41 هسته‌ای', 'cost': 130000, 'power': 18000, 'range': 4000, 'resources': {'nuclear_bomb': 8, 'ballistic_missile': 1, 'coal': 140}, 'category': 'special_missiles'},
        'tomahawk_conventional': {'name': 'Tomahawk غیر هسته‌ای', 'cost': 12000, 'power': 700, 'range': 1500, 'resources': {'ballistic_missile': 1, 'simple_bomb': 1, 'iron': 10, 'sulfur': 120}, 'category': 'special_missiles'},
        'tomahawk_nuclear': {'name': 'Tomahawk هسته‌ای', 'cost': 18000, 'power': 3000, 'range': 1500, 'resources': {'nuclear_bomb': 1, 'ballistic_missile': 1, 'iron': 30, 'coal': 20}, 'category': 'special_missiles'},
        'kalibr_conventional': {'name': 'Kalibr غیر هسته‌ای', 'cost': 12000, 'power': 650, 'range': 1500, 'resources': {'ballistic_missile': 1, 'simple_bomb': 1, 'iron': 10, 'sulfur': 30}, 'category': 'special_missiles'},

        # Advanced fighter jets
        'f22': {'name': 'F-22', 'cost': 20000, 'power': 980, 'range': 3000, 'resources': {'titanium': 9, 'iron': 15, 'aluminum': 30, 'copper': 9, 'gold': 3}, 'category': 'advanced_jets'},
        'strategic_bomber': {'name': 'بمب‌افکن استراتژیک', 'cost': 8500000, 'power': 4500, 'range': 4500, 'resources': {'aluminum': 60, 'titanium': 25, 'fuel': 50}, 'category': 'air'},
        'icbm': {'name': 'موشک قاره‌پیما', 'cost': 25000000, 'power': 6000, 'range': 15000, 'resources': {'uranium': 30, 'titanium': 20, 'fuel': 40}, 'category': 'special_missiles'},
        'f35': {'name': 'F-35', 'cost': 18000, 'power': 950, 'range': 2800, 'resources': {'titanium': 9, 'iron': 10, 'aluminum': 21, 'copper': 6, 'gold': 2}, 'category': 'advanced_jets'},
        'su57': {'name': 'Su-57', 'cost': 18000, 'power': 940, 'range': 2700, 'resources': {'titanium': 9, 'iron': 10, 'aluminum': 21, 'copper': 6, 'gold': 2}, 'category': 'advanced_jets'},
        'j20': {'name': 'J-20', 'cost': 15000, 'power': 920, 'range': 2500, 'resources': {'titanium': 9, 'iron': 10, 'aluminum': 21, 'copper': 6, 'gold': 2}, 'category': 'advanced_jets'},
        'f15ex': {'name': 'F-15EX', 'cost': 15000, 'power': 910, 'range': 2400, 'resources': {'titanium': 6, 'iron': 15, 'aluminum': 30, 'copper': 9, 'gold': 3}, 'category': 'advanced_jets'},
        'su35s': {'name': 'Su-35S', 'cost': 15000, 'power': 900, 'range': 2300, 'resources': {'titanium': 6, 'iron': 10, 'aluminum': 21, 'copper': 6, 'gold': 2}, 'category': 'advanced_jets'},

        # Transport and Logistics Equipment
        'armored_truck': {
        'name': 'کامیون زرهی',
        'cost': 90000,
        'category': 'transport',
        'power': 0,
        'defense': 15,
        'transport_capacity': 1000,
        'security_bonus': 20,
        'emoji': '🚚'
    },
    'cargo_helicopter': {
        'name': 'هلیکوپتر باری',
        'cost': 120000,
        'category': 'transport',
        'power': 0,
        'defense': 25,
        'transport_capacity': 2000,
        'security_bonus': 35,
        'emoji': '🚁'
    },
    'cargo_plane': {
        'name': 'هواپیمای باری',
        'cost': 240000,
        'category': 'transport',
        'power': 0,
        'defense': 40,
        'transport_capacity': 5000,
        'security_bonus': 50,
        'emoji': '✈️'
    },
    'escort_frigate': {
        'name': 'ناوچه اسکورت',
        'cost': 300000,
        'category': 'transport',
        'power': 30,
        'defense': 60,
        'transport_capacity': 3000,
        'security_bonus': 45,
        'emoji': '🚢'
    },
    'logistics_drone': {
        'name': 'پهپاد لجستیک',
        'cost': 120000,
        'category': 'transport',
        'power': 15,
        'defense': 20,
        'transport_capacity': 800,
        'security_bonus': 25,
        'emoji': '🚁'
    },
    'heavy_transport': {
        'name': 'ترابری سنگین',
        'cost': 210000,
        'category': 'transport',
        'power': 0,
        'defense': 30,
        'transport_capacity': 4000,
        'security_bonus': 30,
        'emoji': '🚛'
    },
    'supply_ship': {
        'name': 'کشتی تدارکات',
        'cost': 450000,
        'category': 'transport',
        'power': 25,
        'defense': 50,
        'transport_capacity': 8000,
        'security_bonus': 40,
        'emoji': '🚢'
    },
    'stealth_transport': {
        'name': 'ترابری پنهان‌کار',
        'cost': 240000,
        'category': 'transport',
        'power': 0,
        'defense': 40,
        'transport_capacity': 5000,
        'security_bonus': 35,
        'emoji': '✈️'
    },
    'tanker_aircraft': {
        'name': 'هواپیمای سوخت‌رسان',
        'cost': 5800000,
        'power': 1000,
        'range': 4000,
        'speed': 450,
        'armor': 300,
        'resources': {'aluminum': 60, 'iron': 40, 'copper': 20, 'titanium': 8},
        'category': 'transport',
        'description': 'هواپیمای سوخت‌رسان که برد جت‌ها را افزایش می‌دهد',
        'requirements': ['weapon_factory', 'power_plant', 'refinery'],
        'production_time': 250,
        'emoji': '✈️'
    },
    'aircraft_carrier_transport': {
        'name': 'ناو هواپیمابر (حمل‌ونقل)',
        'cost': 12500000,
        'power': 8000,
        'range': 5000,
        'speed': 30,
        'armor': 6000,
        'resources': {'iron': 200, 'aluminum': 100, 'titanium': 25, 'uranium': 15, 'copper': 80},
        'category': 'transport',
        'description': 'ناو هواپیمابر که جت‌ها را به مناطق دوردست می‌برد',
        'requirements': ['weapon_factory', 'power_plant', 'refinery'],
        'production_time': 400,
        'emoji': '🚢'
    },
    }

    # Resources configuration
    RESOURCES = {
        'iron': {'name': 'آهن', 'emoji': '🔩', 'market_value': 10},
        'copper': {'name': 'مس', 'emoji': '🥉', 'market_value': 15},
        'oil': {'name': 'نفت خام', 'emoji': '🛢', 'market_value': 25},
        'gas': {'name': 'گاز', 'emoji': '⛽', 'market_value': 20},
        'aluminum': {'name': 'آلومینیوم', 'emoji': '🔗', 'market_value': 30},
        'gold': {'name': 'طلا', 'emoji': '🏆', 'market_value': 50},
        'uranium': {'name': 'اورانیوم', 'emoji': '☢️', 'market_value': 100},
        'lithium': {'name': 'لیتیوم', 'emoji': '🔋', 'market_value': 40},
        'coal': {'name': 'زغال‌سنگ', 'emoji': '⚫', 'market_value': 12},
        'silver': {'name': 'نقره', 'emoji': '🥈', 'market_value': 45},
        'fuel': {'name': 'سوخت', 'emoji': '⛽', 'market_value': 20},
        'nitro': {'name': 'نیتر', 'emoji': '💥', 'market_value': 35},
        'sulfur': {'name': 'گوگرد', 'emoji': '🌫', 'market_value': 18},
        'titanium': {'name': 'تیتانیوم', 'emoji': '🛡', 'market_value': 80}
    }

    # Country neighbors for war system
    COUNTRY_NEIGHBORS = {
        'IR': ['TR', 'IQ', 'AF', 'PK'],
        'TR': ['IR', 'IQ'],
        'RU': ['CN', 'KP', 'DE'],
        'CN': ['RU', 'KP', 'JP', 'IN'],
        'US': ['MX', 'CA'],
        'MX': ['US'],
        'FR': ['DE', 'ES', 'BE', 'IT'],
        'DE': ['FR', 'RU', 'BE'],
        'ES': ['FR'],
        'BE': ['FR', 'DE'],
        'JP': ['CN', 'KP'],
        'KP': ['CN', 'RU', 'JP'],
        'EG': ['SA'],
        'SA': ['EG', 'IQ'],
        'PK': ['IR', 'AF', 'IN'],
        'AF': ['IR', 'PK'],
        'IQ': ['IR', 'TR', 'SA'],
        'IN': ['CN', 'PK'],
        'AR': ['BR'],
        'BR': ['AR'],
        'IT': ['FR'],
        'GB': [],
        'CA': ['US'],
        'AU': []
    }

    # Admin configuration
    ADMIN_CONFIG = {
        'default_admin_ids': [123456789],  # Replace with actual admin user IDs
        'max_logs_display': 50,
        'reset_confirmation_required': True
    }

    # Combat configuration
    COMBAT_CONFIG = {
        'neighbor_attack_always_allowed': True,
        'long_range_threshold_km': 3000,
        'base_defense_multiplier': 0.3,
        'weapon_loss_chance': 0.2
    }

    # Distance-based combat timing (in minutes)
    COMBAT_TIMING = {
        'neighbor_time': 10,        # همسایه - 10 دقیقه
        'regional_time': 25,        # منطقه‌ای - 25 دقیقه  
        'intercontinental_time': 40, # بین قاره‌ای - 40 دقیقه
        'speed_bonus_per_jet': 0.5,  # کاهش زمان برای هر جت
        'speed_bonus_per_transport': 0.3  # کاهش زمان برای تجهیزات حمل‌ونقل
    }

    # Country distance categories
    COUNTRY_DISTANCE_CATEGORY = {
        # Regional groups (25 minutes base travel time)
        'middle_east': ['IR', 'TR', 'IQ', 'SA', 'EG', 'AF', 'PK'],
        'north_america': ['US', 'CA', 'MX'],
        'europe': ['FR', 'DE', 'ES', 'BE', 'IT', 'GB'],
        'east_asia': ['CN', 'JP', 'KP'],
        'south_america': ['AR', 'BR'],
        'oceania': ['AU'],
        'eurasia': ['RU'],
        'south_asia': ['IN']
    }

    # Weapon range categories for distance-based combat
    WEAPON_RANGES = {
        'neighbor_only': ['rifle', 'tank', 'drone', 'air_defense', 'missile_shield', 'cyber_shield'],  # فقط همسایه
        'regional': ['fighter_jet', 'jet', 'f22', 'f35', 'su57', 'j20', 'f15ex', 'su35s', 'warship', 'submarine', 'destroyer'],  # تا منطقه‌ای
        'intercontinental': ['missile', 'ballistic_missile', 'nuclear_missile', 'simple_missile', 'trident2_conventional', 'trident2_nuclear', 'satan2_conventional', 'satan2_nuclear', 'df41_nuclear', 'tomahawk_conventional', 'tomahawk_nuclear', 'kalibr_conventional']  # بین قاره‌ای
    }

    @classmethod
    def get_country_distance_type(cls, country1, country2):
        """Get distance type between two countries"""
        if cls.are_countries_neighbors(country1, country2):
            return 'neighbor'

        # Find regions for both countries
        region1 = None
        region2 = None

        for region, countries in cls.COUNTRY_DISTANCE_CATEGORY.items():
            if country1 in countries:
                region1 = region
            if country2 in countries:
                region2 = region

        if region1 == region2:
            return 'regional'
        else:
            return 'intercontinental'

    @classmethod 
    def are_countries_neighbors(cls, country1, country2):
        """Check if two countries are neighbors"""
        return country2 in cls.COUNTRY_NEIGHBORS.get(country1, [])

    @classmethod
    def can_attack_with_weapon(cls, weapon_type, country1, country2):
        """Check if a weapon can attack from country1 to country2"""
        distance_type = cls.get_country_distance_type(country1, country2)

        # همسایه - همه سلاح‌ها
        if distance_type == 'neighbor':
            return True

        # منطقه‌ای - فقط جت‌ها و موشک‌ها
        elif distance_type == 'regional':
            return weapon_type in cls.WEAPON_RANGES['regional'] + cls.WEAPON_RANGES['intercontinental']

        # بین قاره‌ای - فقط موشک‌های دوربرد
        elif distance_type == 'intercontinental':
            return weapon_type in cls.WEAPON_RANGES['intercontinental']

        return False

    @classmethod
    def get_available_weapons_for_attack(cls, attacker_country, defender_country, weapons, has_tanker=False, has_carrier=False):
        """Get weapons available for attack based on distance and range extenders"""
        distance_type = Config.get_country_distance_type(attacker_country, defender_country)
        available_weapons = []

        # Calculate range bonus from extenders
        range_bonus = 0
        if has_carrier:
            range_bonus = max(range_bonus, 3000)  # ناوبر 3000 کیلومتر اضافه می‌کنه
        if has_tanker:
            range_bonus = max(range_bonus, 2000)  # سوخت‌رسان 2000 کیلومتر اضافه می‌کنه
        if has_carrier and has_tanker:
            range_bonus = 4000  # ترکیب هردو 4000 کیلومتر

        for weapon_type, count in weapons.items():
            if weapon_type == 'user_id' or count <= 0:
                continue

            if weapon_type not in Config.WEAPONS:
                continue

            weapon_info = Config.WEAPONS[weapon_type]
            base_range = weapon_info.get('range', 0)
            weapon_category = weapon_info.get('category', '')

            # Skip transport weapons for attack (but carrier transport has attack power)
            if weapon_category == 'transport' and weapon_type != 'aircraft_carrier_transport':
                continue

            # Calculate effective range for jets
            effective_range = base_range
            if weapon_category == 'air' and range_bonus > 0:
                effective_range = base_range + range_bonus

            if distance_type == 'neighbor':
                # All weapons work for neighbors
                available_weapons.append(weapon_type)
            elif distance_type == 'regional':
                # Jets and missiles for regional, with range extension
                if weapon_category in ['air', 'missile'] or effective_range >= 1500:
                    available_weapons.append(weapon_type)
            else:  # intercontinental
                # Long-range missiles and extended-range jets
                if effective_range >= 3000:
                    available_weapons.append(weapon_type)

        return available_weapons

    # Bot configuration
    BOT_CONFIG = {
        'news_channel': '@Dragon0RP',
        'income_cycle_hours': 6
    }