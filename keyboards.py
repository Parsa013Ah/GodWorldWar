from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config

class Keyboards:
    def __init__(self):
        pass
    
    def country_selection_keyboard(self):
        """Create country selection keyboard"""
        keyboard = []
        
        # Create buttons for all countries in rows of 2
        countries = list(Config.COUNTRIES.items())
        for i in range(0, len(countries), 2):
            row = []
            for j in range(i, min(i + 2, len(countries))):
                country_code, country_name = countries[j]
                button = InlineKeyboardButton(
                    f"{Config.COUNTRY_FLAGS.get(country_code, '🏳')} {country_name}",
                    callback_data=f"select_country_{country_code}"
                )
                row.append(button)
            keyboard.append(row)
        
        return InlineKeyboardMarkup(keyboard)
    
    def main_menu_keyboard(self):
        """Create main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📈 اقتصاد", callback_data="economy"),
                InlineKeyboardButton("⚔️ نظامی", callback_data="military")
            ],
            [
                InlineKeyboardButton("🤝 دیپلماسی", callback_data="diplomacy"),
                InlineKeyboardButton("📊 منابع", callback_data="resources")
            ],
            [
                InlineKeyboardButton("📬 ارسال منابع", callback_data="send_resources"),
                InlineKeyboardButton("📢 بیانیه رسمی", callback_data="official_statement")
            ],
            [
                InlineKeyboardButton("👑 پنل ادمین", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def economy_menu_keyboard(self):
        """Create economy menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🏗 ساخت و ساز", callback_data="buildings"),
                InlineKeyboardButton("📊 گزارش درآمد", callback_data="income_report")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def buildings_menu_keyboard(self):
        """Create buildings menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("⛏ معدن آهن", callback_data="build_iron_mine"),
                InlineKeyboardButton("⛏ معدن مس", callback_data="build_copper_mine")
            ],
            [
                InlineKeyboardButton("🛢 معدن نفت", callback_data="build_oil_mine"),
                InlineKeyboardButton("⛽ معدن گاز", callback_data="build_gas_mine")
            ],
            [
                InlineKeyboardButton("🔗 معدن آلومینیوم", callback_data="build_aluminum_mine"),
                InlineKeyboardButton("🏆 معدن طلا", callback_data="build_gold_mine")
            ],
            [
                InlineKeyboardButton("☢️ معدن اورانیوم", callback_data="build_uranium_mine"),
                InlineKeyboardButton("🔋 معدن لیتیوم", callback_data="build_lithium_mine")
            ],
            [
                InlineKeyboardButton("⚫ معدن زغال", callback_data="build_coal_mine"),
                InlineKeyboardButton("🥈 معدن نقره", callback_data="build_silver_mine")
            ],
            [
                InlineKeyboardButton("⚒ کارخانه اسلحه", callback_data="build_weapon_factory"),
                InlineKeyboardButton("🏭 پالایشگاه", callback_data="build_refinery")
            ],
            [
                InlineKeyboardButton("⚡ نیروگاه", callback_data="build_power_plant"),
                InlineKeyboardButton("🌾 مزرعه گندم", callback_data="build_wheat_farm")
            ],
            [
                InlineKeyboardButton("🪖 پادگان", callback_data="build_military_base"),
                InlineKeyboardButton("🏘 مسکن", callback_data="build_housing")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="economy")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def military_menu_keyboard(self):
        """Create military menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔫 تولید تسلیحات", callback_data="weapons"),
                InlineKeyboardButton("⚔️ حمله", callback_data="attack_menu")
            ],
            [
                InlineKeyboardButton("🛡 دفاع", callback_data="defense_status"),
                InlineKeyboardButton("📊 قدرت نظامی", callback_data="military_power")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def weapons_menu_keyboard(self):
        """Create weapons production menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔫 تفنگ", callback_data="produce_rifle"),
                InlineKeyboardButton("🚗 تانک", callback_data="produce_tank")
            ],
            [
                InlineKeyboardButton("✈️ جنگنده", callback_data="produce_fighter_jet"),
                InlineKeyboardButton("🚁 پهپاد", callback_data="produce_drone")
            ],
            [
                InlineKeyboardButton("🚀 موشک", callback_data="produce_missile"),
                InlineKeyboardButton("🚢 کشتی جنگی", callback_data="produce_warship")
            ],
            [
                InlineKeyboardButton("🛡 پدافند هوایی", callback_data="produce_air_defense"),
                InlineKeyboardButton("🚀 سپر موشکی", callback_data="produce_missile_shield")
            ],
            [
                InlineKeyboardButton("💻 سپر سایبری", callback_data="produce_cyber_shield")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="military")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def diplomacy_menu_keyboard(self, user_id):
        """Create diplomacy menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🗺 نقشه جهان", callback_data="world_map"),
                InlineKeyboardButton("📊 رتبه‌بندی", callback_data="rankings")
            ],
            [
                InlineKeyboardButton("⚔️ اعلان جنگ", callback_data="declare_war"),
                InlineKeyboardButton("🤝 پیشنهاد صلح", callback_data="peace_offer")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def back_to_main_keyboard(self):
        """Simple back to main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_panel_keyboard(self):
        """Create admin panel keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("👥 مدیریت بازیکنان", callback_data="admin_players"),
                InlineKeyboardButton("📊 آمار کلی", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("💰 مدیریت پول", callback_data="admin_money"),
                InlineKeyboardButton("🏗 مدیریت ساختمان", callback_data="admin_buildings")
            ],
            [
                InlineKeyboardButton("🔫 مدیریت تسلیحات", callback_data="admin_weapons"),
                InlineKeyboardButton("📰 ارسال خبر", callback_data="admin_news")
            ],
            [
                InlineKeyboardButton("🗂 لاگ‌ها", callback_data="admin_logs"),
                InlineKeyboardButton("⚠️ ریست کامل", callback_data="admin_reset")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_players_keyboard(self, players):
        """Create admin players management keyboard"""
        keyboard = []
        
        # Add buttons for each player
        for player in players[:10]:  # Limit to 10 players per page
            button = InlineKeyboardButton(
                f"{player['country_name']} - {player['username']}",
                callback_data=f"admin_player_{player['user_id']}"
            )
            keyboard.append([button])
        
        keyboard.append([
            InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def admin_player_actions_keyboard(self, user_id):
        """Create admin actions keyboard for specific player"""
        keyboard = [
            [
                InlineKeyboardButton("💰 تغییر پول", callback_data=f"admin_change_money_{user_id}"),
                InlineKeyboardButton("👥 تغییر جمعیت", callback_data=f"admin_change_population_{user_id}")
            ],
            [
                InlineKeyboardButton("⚔️ تغییر سربازان", callback_data=f"admin_change_soldiers_{user_id}"),
                InlineKeyboardButton("📦 افزودن منابع", callback_data=f"admin_add_resources_{user_id}")
            ],
            [
                InlineKeyboardButton("🏗 افزودن ساختمان", callback_data=f"admin_add_building_{user_id}"),
                InlineKeyboardButton("🔫 افزودن سلاح", callback_data=f"admin_add_weapon_{user_id}")
            ],
            [
                InlineKeyboardButton("❌ حذف بازیکن", callback_data=f"admin_delete_player_{user_id}")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_players")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
