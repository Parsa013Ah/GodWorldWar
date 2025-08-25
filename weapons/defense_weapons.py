
# سلاح‌های دفاعی

DEFENSE_WEAPONS = {
    'air_defense': {
        'name': 'پدافند هوایی',
        'cost': 8000,
        'power': 1500,
        'range': 1000,
        'speed': 0,
        'armor': 600,
        'resources': {'iron': 25, 'aluminum': 15, 'copper': 12},
        'category': 'defense',
        'description': 'سیستم دفاع ضدهوایی',
        'requirements': ['weapon_factory'],
        'production_time': 90,
        'defense_bonus': 150
    },
    'missile_shield': {
        'name': 'سپر موشکی',
        'cost': 15000,
        'power': 2500,
        'range': 1500,
        'speed': 0,
        'armor': 1000,
        'resources': {'titanium': 20, 'aluminum': 25, 'uranium': 5},
        'category': 'defense',
        'description': 'سیستم رهگیری موشک‌ها',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 150,
        'defense_bonus': 250
    },
    'cyber_shield': {
        'name': 'سپر سایبری',
        'cost': 9000,
        'power': 800,
        'range': 0,
        'speed': 0,
        'armor': 0,
        'resources': {'lithium': 15, 'gold': 8, 'copper': 20},
        'category': 'defense',
        'description': 'سیستم دفاع سایبری',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 120,
        'defense_bonus': 200
    },

    # سیستم‌های دفاعی جدید
    's500_defense': {
        'name': 'پدافند S-500',
        'cost': 30000,
        'power': 5000,
        'range': 2000,
        'speed': 0,
        'armor': 1500,
        'resources': {'simple_missile': 6, 'sulfur': 60, 'nitro': 60, 'iron': 150, 'copper': 60, 'aluminum': 30},
        'category': 'defense',
        'description': 'سیستم دفاع پیشرفته روسی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 200,
        'defense_bonus': 500
    },
    'thaad_defense': {
        'name': 'پدافند THAAD',
        'cost': 21000,
        'power': 4500,
        'range': 1800,
        'speed': 0,
        'armor': 1400,
        'resources': {'simple_missile': 3, 'sulfur': 60, 'nitro': 60, 'iron': 150, 'copper': 60, 'aluminum': 30},
        'category': 'defense',
        'description': 'سیستم دفاع موشکی آمریکایی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 180,
        'defense_bonus': 450
    },
    's400_defense': {
        'name': 'پدافند S-400',
        'cost': 18000,
        'power': 4000,
        'range': 1600,
        'speed': 0,
        'armor': 1300,
        'resources': {'simple_missile': 3, 'sulfur': 60, 'nitro': 60, 'iron': 120, 'copper': 60, 'aluminum': 30},
        'category': 'defense',
        'description': 'سیستم دفاع متوسط روسی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 160,
        'defense_bonus': 400
    },
    'iron_dome': {
        'name': 'پدافند Iron Dome',
        'cost': 15000,
        'power': 3600,
        'range': 1400,
        'speed': 0,
        'armor': 1200,
        'resources': {'simple_missile': 3, 'sulfur': 30, 'nitro': 30, 'iron': 90, 'copper': 60, 'aluminum': 30},
        'category': 'defense',
        'description': 'سیستم دفاع کوتاه برد اسرائیلی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 140,
        'defense_bonus': 360
    },
    'slq32_ew': {
        'name': 'پدافند جنگ الکترونیک SLQ-32',
        'cost': 21000,
        'power': 4000,
        'range': 1500,
        'speed': 0,
        'armor': 1000,
        'resources': {'uranium': 3, 'iron': 150, 'copper': 120, 'aluminum': 60},
        'category': 'defense',
        'description': 'سیستم جنگ الکترونیک دریایی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 180,
        'defense_bonus': 400
    },
    'phalanx_ciws': {
        'name': 'توپخانه Phalanx CIWS',
        'cost': 21000,
        'power': 4000,
        'range': 800,
        'speed': 0,
        'armor': 1100,
        'resources': {'iron': 150, 'copper': 120, 'aluminum': 60, 'sulfur': 150, 'nitro': 60},
        'category': 'defense',
        'description': 'سیستم دفاع نزدیک دریایی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 170,
        'defense_bonus': 400
    }
}
