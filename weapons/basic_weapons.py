
# سلاح‌های پایه

BASIC_WEAPONS = {
    'rifle': {
        'name': 'تفنگ جنگی',
        'cost': 1500,
        'power': 5,
        'range': 300,
        'speed': 0,
        'armor': 0,
        'resources': {'iron': 5, 'copper': 2},
        'category': 'basic',
        'description': 'سلاح پایه پیاده‌نظام',
        'requirements': [],
        'production_time': 1  # دقیقه
    },
    'tank': {
        'name': 'تانک جنگی',
        'cost': 8500,
        'power': 1200,
        'range': 500,
        'speed': 60,
        'armor': 800,
        'resources': {'iron': 50, 'copper': 15, 'aluminum': 10},
        'category': 'basic',
        'description': 'تانک سنگین برای نبرد زمینی',
        'requirements': ['weapon_factory'],
        'production_time': 60
    },
    'fighter_jet': {
        'name': 'جنگنده',
        'cost': 25000,
        'power': 2000,
        'range': 1200,
        'speed': 800,
        'armor': 300,
        'resources': {'aluminum': 30, 'titanium': 15, 'copper': 20},
        'category': 'basic',
        'description': 'جنگنده چندمنظوره',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 120
    },
    'helicopter': {
        'name': 'هلیکوپتر جنگی',
        'cost': 18000,
        'power': 2400,
        'range': 1500,
        'resources': {'aluminum': 30, 'iron': 20, 'copper': 10},
        'category': 'basic',
        'description': 'هلیکوپتر نظامی',
        'requirements': ['weapon_factory'],
        'production_time': 90
    },
    'jet': {
        'name': 'جت جنگی',
        'cost': 35000,
        'power': 3200,
        'range': 2000,
        'speed': 1200,
        'armor': 400,
        'resources': {'aluminum': 40, 'iron': 25, 'copper': 15, 'titanium': 5},
        'category': 'basic',
        'description': 'جت پیشرفته',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 150
    },
    'drone': {
        'name': 'پهپاد نظامی',
        'cost': 1800,
        'power': 800,
        'range': 1000,
        'speed': 200,
        'armor': 50,
        'resources': {'aluminum': 10, 'copper': 8, 'lithium': 5},
        'category': 'basic',
        'description': 'پهپاد مسلح با قابلیت نظارت',
        'requirements': ['weapon_factory'],
        'production_time': 30
    },
    'strategic_bomber': {
        'name': 'بمب‌افکن استراتژیک',
        'cost': 85000,
        'power': 4500,
        'range': 4500,
        'speed': 900,
        'armor': 600,
        'resources': {'aluminum': 60, 'titanium': 25, 'fuel': 50},
        'category': 'basic',
        'description': 'بمب‌افکن سنگین برای حملات استراتژیک',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 300
    },

    # تانک‌های مدرن
    'kf51_panther': {
        'name': 'KF51 Panther',
        'cost': 9000,
        'power': 100,
        'range': 600,
        'speed': 70,
        'armor': 900,
        'resources': {'iron': 30, 'copper': 3, 'aluminum': 30},
        'category': 'basic',
        'description': 'تانک مدرن آلمانی',
        'requirements': ['weapon_factory'],
        'production_time': 45
    },
    'abrams_x': {
        'name': 'AbramsX',
        'cost': 9000,
        'power': 99,
        'range': 580,
        'speed': 68,
        'armor': 880,
        'resources': {'iron': 21, 'copper': 3, 'titanium': 1},
        'category': 'basic',
        'description': 'تانک پیشرفته آمریکایی',
        'requirements': ['weapon_factory'],
        'production_time': 45
    },
    'm1e3_abrams': {
        'name': 'M1E3 Abrams',
        'cost': 6000,
        'power': 98,
        'range': 570,
        'speed': 65,
        'armor': 850,
        'resources': {'iron': 21, 'copper': 3, 'titanium': 1},
        'category': 'basic',
        'description': 'نسخه بهبود یافته ابرامز',
        'requirements': ['weapon_factory'],
        'production_time': 40
    },
    't90ms_proryv': {
        'name': 'T-90MS Proryv',
        'cost': 6000,
        'power': 95,
        'range': 550,
        'speed': 62,
        'armor': 820,
        'resources': {'iron': 21, 'copper': 3, 'titanium': 1},
        'category': 'basic',
        'description': 'تانک مدرن روسی',
        'requirements': ['weapon_factory'],
        'production_time': 40
    },
    'm1a2_abrams_sepv3': {
        'name': 'M1A2 Abrams SEPv3',
        'cost': 3000,
        'power': 80,
        'range': 500,
        'speed': 55,
        'armor': 750,
        'resources': {'iron': 18, 'copper': 3},
        'category': 'basic',
        'description': 'تانک استاندارد آمریکایی',
        'requirements': ['weapon_factory'],
        'production_time': 35
    }
}
