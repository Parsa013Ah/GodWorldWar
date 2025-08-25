
# پایه‌ای‌ترین سلاح‌ها

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
        'cost': 850000,
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
        'cost': 2500000,
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
    'drone': {
        'name': 'پهپاد نظامی',
        'cost': 180000,
        'power': 300,
        'range': 800,
        'speed': 200,
        'armor': 50,
        'resources': {'aluminum': 8, 'lithium': 5, 'copper': 10},
        'category': 'basic',
        'description': 'پهپاد مسلح با قابلیت نظارت',
        'requirements': ['weapon_factory'],
        'production_time': 30
    },
    'warship': {
        'name': 'کشتی جنگی',
        'cost': 5000000,
        'power': 3500,
        'range': 2000,
        'speed': 45,
        'armor': 1500,
        'resources': {'iron': 100, 'aluminum': 40, 'copper': 25},
        'category': 'basic',
        'description': 'کشتی جنگی سنگین',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 180
    }
}
