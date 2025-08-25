
from .basic_weapons import BASIC_WEAPONS
from .defense_weapons import DEFENSE_WEAPONS
from .advanced_jets import ADVANCED_JETS
from .missiles import MISSILES
from .transport_equipment import TRANSPORT_EQUIPMENT

# ترکیب تمام سلاح‌ها
ALL_WEAPONS = {}
ALL_WEAPONS.update(BASIC_WEAPONS)
ALL_WEAPONS.update(DEFENSE_WEAPONS)
ALL_WEAPONS.update(ADVANCED_JETS)
ALL_WEAPONS.update(MISSILES)
ALL_WEAPONS.update(TRANSPORT_EQUIPMENT)

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
    'advanced_jets': {
        'name': 'جت‌های پیشرفته',
        'weapons': ADVANCED_JETS
    },
    'missiles': {
        'name': 'موشک‌ها',
        'weapons': MISSILES
    },
    'transport': {
        'name': 'تجهیزات حمل و نقل',
        'weapons': TRANSPORT_EQUIPMENT
    }
}

def get_weapon_info(weapon_key):
    """دریافت اطلاعات کامل یک سلاح"""
    return ALL_WEAPONS.get(weapon_key)

def get_weapons_by_category(category):
    """دریافت سلاح‌های یک دسته"""
    return WEAPON_CATEGORIES.get(category, {}).get('weapons', {})

def get_all_categories():
    """دریافت تمام دسته‌ها"""
    return WEAPON_CATEGORIES
