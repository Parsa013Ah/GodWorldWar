"""
DragonRP Game Configuration
Contains all game constants, costs, and specifications
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

    # Buildings configuration
    BUILDINGS = {
        'iron_mine': {'name': 'معدن آهن', 'cost': 80000, 'income': 32000, 'resource': 'iron'},
        'copper_mine': {'name': 'معدن مس', 'cost': 100000, 'income': 40000, 'resource': 'copper'},
        'oil_mine': {'name': 'معدن نفت', 'cost': 120000, 'income': 48000, 'resource': 'oil'},
        'gas_mine': {'name': 'معدن گاز', 'cost': 110000, 'income': 44000, 'resource': 'gas'},
        'aluminum_mine': {'name': 'معدن آلومینیوم', 'cost': 90000, 'income': 36000, 'resource': 'aluminum'},
        'gold_mine': {'name': 'معدن طلا', 'cost': 150000, 'income': 60000, 'resource': 'gold'},
        'uranium_mine': {'name': 'معدن اورانیوم', 'cost': 200000, 'income': 80000, 'resource': 'uranium'},
        'lithium_mine': {'name': 'معدن لیتیوم', 'cost': 180000, 'income': 72000, 'resource': 'lithium'},
        'coal_mine': {'name': 'معدن زغال‌سنگ', 'cost': 85000, 'income': 34000, 'resource': 'coal'},
        'silver_mine': {'name': 'معدن نقره', 'cost': 140000, 'income': 56000, 'resource': 'silver'},
        'nitro_mine': {'name': 'معدن نیتر', 'cost': 95000, 'income': 38000, 'resource': 'nitro'},
        'sulfur_mine': {'name': 'معدن گوگرد', 'cost': 75000, 'income': 30000, 'resource': 'sulfur'},
        'titanium_mine': {'name': 'معدن تیتانیوم', 'cost': 250000, 'income': 100000, 'resource': 'titanium'},
        'weapon_factory': {'name': 'کارخانه اسلحه', 'cost': 150000, 'requirements': ['power_plant']},
        'refinery': {'name': 'پالایشگاه', 'cost': 100000},
        'power_plant': {'name': 'نیروگاه', 'cost': 90000},
        'wheat_farm': {'name': 'مزرعه گندم', 'cost': 50000, 'population_increase': 10000},
        'military_base': {'name': 'پادگان', 'cost': 50000, 'soldier_production': 5000},
        'housing': {'name': 'مسکن', 'cost': 50000, 'capacity': 10000}
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
        'trident2_conventional': {'name': 'Trident 2 غیر هسته‌ای', 'cost': 0, 'power': 1000, 'range': 5000, 'resources': {'simple_bomb': 12, 'ballistic_missile': 1, 'coal': 140}, 'category': 'special_missiles'},
        'trident2_nuclear': {'name': 'Trident 2 هسته‌ای', 'cost': 190000, 'power': 30000, 'range': 5000, 'resources': {'nuclear_bomb': 12, 'ballistic_missile': 1, 'coal': 140}, 'category': 'special_missiles'},
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
        'armored_truck': {'name': 'کامیون زرهی', 'cost': 450000, 'power': 200, 'convoy_security': 25, 'capacity': 1000, 'resources': {'iron': 30, 'aluminum': 15}, 'category': 'transport'},
        'cargo_helicopter': {'name': 'هلیکوپتر باری', 'cost': 2200000, 'power': 800, 'convoy_security': 40, 'capacity': 2000, 'speed_bonus': 50, 'resources': {'aluminum': 25, 'iron': 20, 'copper': 10}, 'category': 'transport'},
        'cargo_plane': {'name': 'هواپیمای باری', 'cost': 6500000, 'power': 1500, 'convoy_security': 60, 'capacity': 5000, 'speed_bonus': 75, 'resources': {'aluminum': 40, 'iron': 30, 'titanium': 8}, 'category': 'transport'},
        'escort_frigate': {'name': 'ناوچه اسکورت', 'cost': 3800000, 'power': 2800, 'convoy_security': 80, 'naval_escort': True, 'resources': {'iron': 60, 'aluminum': 30, 'copper': 20}, 'category': 'transport'},
        'logistics_drone': {'name': 'پهپاد لجستیک', 'cost': 850000, 'power': 400, 'convoy_security': 30, 'stealth': True, 'speed_bonus': 40, 'resources': {'aluminum': 15, 'lithium': 8, 'copper': 12}, 'category': 'transport'},
        'heavy_transport': {'name': 'ترابری سنگین', 'cost': 1200000, 'power': 600, 'convoy_security': 45, 'capacity': 3000, 'resources': {'iron': 45, 'aluminum': 20, 'copper': 15}, 'category': 'transport'},
        'supply_ship': {'name': 'کشتی تدارکات', 'cost': 4500000, 'power': 1200, 'convoy_security': 70, 'capacity': 8000, 'naval': True, 'resources': {'iron': 80, 'aluminum': 40, 'copper': 25}, 'category': 'transport'},
        'stealth_transport': {'name': 'ترابری پنهان‌کار', 'cost': 8200000, 'power': 2000, 'convoy_security': 90, 'stealth': True, 'speed_bonus': 60, 'resources': {'titanium': 15, 'aluminum': 50, 'uranium': 5}, 'category': 'transport'}
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

    # Bot configuration
    BOT_CONFIG = {
        'news_channel': '@Dragon0RP',
        'income_cycle_hours': 6
    }