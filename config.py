"""
DragonRP Game Configuration
Contains all game constants, costs, and specifications
"""

class Config:
    """Main configuration class for DragonRP game"""
    
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
        'weapon_factory': {'name': 'کارخانه اسلحه', 'cost': 150000, 'requirements': ['power_plant']},
        'refinery': {'name': 'پالایشگاه', 'cost': 100000},
        'power_plant': {'name': 'نیروگاه', 'cost': 90000},
        'wheat_farm': {'name': 'مزرعه گندم', 'cost': 50000, 'population_increase': 10000},
        'military_base': {'name': 'پادگان', 'cost': 50000, 'soldier_production': 5000},
        'housing': {'name': 'مسکن', 'cost': 50000, 'capacity': 10000}
    }

    # Weapons configuration
    WEAPONS = {
        'rifle': {'name': 'تفنگ', 'cost': 1000, 'power': 1, 'range': 50, 'resources': {'iron': 1}},
        'tank': {'name': 'تانک', 'cost': 10000, 'power': 50, 'range': 300, 'resources': {'iron': 10, 'fuel': 5}},
        'fighter_jet': {'name': 'جنگنده', 'cost': 25000, 'power': 100, 'range': 1000, 'resources': {'aluminum': 20, 'fuel': 10}},
        'drone': {'name': 'پهپاد', 'cost': 20000, 'power': 80, 'range': 1500, 'resources': {'lithium': 15, 'fuel': 8}},
        'missile': {'name': 'موشک بالستیک', 'cost': 50000, 'power': 200, 'range': 3000, 'resources': {'uranium': 5, 'fuel': 20}},
        'warship': {'name': 'کشتی جنگی', 'cost': 40000, 'power': 120, 'range': 1000, 'resources': {'iron': 30, 'fuel': 15}},
        'air_defense': {'name': 'پدافند هوایی', 'cost': 30000, 'power': 60, 'defense_type': 'air', 'resources': {'copper': 15, 'iron': 10}},
        'missile_shield': {'name': 'سپر موشکی', 'cost': 35000, 'power': 80, 'defense_type': 'missile', 'resources': {'uranium': 3, 'iron': 20}},
        'cyber_shield': {'name': 'سپر سایبری', 'cost': 20000, 'power': 40, 'defense_type': 'cyber', 'resources': {'lithium': 10, 'copper': 8}}
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
        'fuel': {'name': 'سوخت', 'emoji': '⛽', 'market_value': 20}
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

    # Bot configuration
    BOT_CONFIG = {
        'news_channel': '@Dragon0RP',
        'income_cycle_hours': 6
    }