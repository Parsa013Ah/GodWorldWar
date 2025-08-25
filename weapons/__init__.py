
from .basic_weapons import BASIC_WEAPONS
from .defense_weapons import DEFENSE_WEAPONS
from .advanced_jets import ADVANCED_JETS
from .missiles import MISSILES
from .special_missiles import SPECIAL_MISSILES
from .transport_equipment import TRANSPORT_EQUIPMENT
from .bombs import BOMBS
from .naval_weapons import NAVAL_WEAPONS

# ترکیب تمام سلاح‌ها
ALL_WEAPONS = {}
ALL_WEAPONS.update(BASIC_WEAPONS)
ALL_WEAPONS.update(DEFENSE_WEAPONS)
ALL_WEAPONS.update(ADVANCED_JETS)
ALL_WEAPONS.update(MISSILES)
ALL_WEAPONS.update(SPECIAL_MISSILES)
ALL_WEAPONS.update(TRANSPORT_EQUIPMENT)
ALL_WEAPONS.update(BOMBS)
ALL_WEAPONS.update(NAVAL_WEAPONS)

# دسته‌بندی سلاح‌ها برای نمایش در منو
WEAPON_CATEGORIES = {
    'basic': {
        'name': 'سلاح‌های پایه',
        'weapons': BASIC_WEAPONS
    },
    'defense': {
        'name': 'سیستم‌های دفاعی', 
        'weapons': DEFENSE_WEAPONS
    },
    'naval': {
        'name': 'تسلیحات دریایی',
        'weapons': NAVAL_WEAPONS
    },
    'advanced_jets': {
        'name': 'جت‌های پیشرفته',
        'weapons': ADVANCED_JETS
    },
    'missiles': {
        'name': 'موشک‌های ساده',
        'weapons': MISSILES
    },
    'special_missiles': {
        'name': 'موشک‌های مخصوص',
        'weapons': SPECIAL_MISSILES
    },
    'transport': {
        'name': 'تجهیزات حمل و نقل',
        'weapons': TRANSPORT_EQUIPMENT
    },
    'bombs': {
        'name': 'بمب‌ها و مواد منفجره',
        'weapons': BOMBS
    }
}

def get_weapon_info(weapon_key):
    """دریافت اطلاعات کامل یک سلاح"""
    return ALL_WEAPONS.get(weapon_key)

def get_weapons_by_category(category):
    """دریافت سلاح‌های یک دسته"""
    return WEAPON_CATEGORIES.get(category, {}).get('weapons', {})

def get_all_categories():
    """دریافت تمام دسته‌بندی‌ها"""
    return WEAPON_CATEGORIES

def get_weapon_requirements(weapon_key):
    """دریافت پیش‌نیازهای ساخت یک سلاح"""
    weapon = ALL_WEAPONS.get(weapon_key)
    if weapon:
        return weapon.get('requirements', [])
    return []

def calculate_weapon_cost(weapon_key, quantity=1):
    """محاسبه کل هزینه ساخت سلاح"""
    weapon = ALL_WEAPONS.get(weapon_key)
    if weapon:
        return weapon.get('cost', 0) * quantity
    return 0

def get_weapon_resources(weapon_key):
    """دریافت منابع مورد نیاز برای ساخت سلاح"""
    weapon = ALL_WEAPONS.get(weapon_key)
    if weapon:
        return weapon.get('resources', {})
    return {}
