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
    
    def main_menu_keyboard(self, is_admin=False):
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
                InlineKeyboardButton("📢 بیانیه رسمی", callback_data="official_statement")
            ]
        ]
        
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("👑 پنل ادمین", callback_data="admin_panel")
            ])
        
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
                InlineKeyboardButton("⛏ معدن آهن - $32K", callback_data="build_iron_mine"),
                InlineKeyboardButton("⛏ معدن مس - $40K", callback_data="build_copper_mine")
            ],
            [
                InlineKeyboardButton("🛢 معدن نفت - $48K", callback_data="build_oil_mine"),
                InlineKeyboardButton("⛽ معدن گاز - $44K", callback_data="build_gas_mine")
            ],
            [
                InlineKeyboardButton("🔗 معدن آلومینیوم - $36K", callback_data="build_aluminum_mine"),
                InlineKeyboardButton("🏆 معدن طلا - $60K", callback_data="build_gold_mine")
            ],
            [
                InlineKeyboardButton("☢️ معدن اورانیوم - $80K", callback_data="build_uranium_mine"),
                InlineKeyboardButton("🔋 معدن لیتیوم - $72K", callback_data="build_lithium_mine")
            ],
            [
                InlineKeyboardButton("⚫ معدن زغال - $34K", callback_data="build_coal_mine"),
                InlineKeyboardButton("🥈 معدن نقره - $56K", callback_data="build_silver_mine")
            ],
            [
                InlineKeyboardButton("🏭 کارخانه اسلحه", callback_data="build_weapon_factory"),
                InlineKeyboardButton("⚡ نیروگاه", callback_data="build_power_plant")
            ],
            [
                InlineKeyboardButton("🏭 پالایشگاه", callback_data="build_refinery"),
                InlineKeyboardButton("🌾 مزرعه - 10K نفر", callback_data="build_wheat_farm")
            ],
            [
                InlineKeyboardButton("🪖 پادگان - 5K سرباز", callback_data="build_military_base"),
                InlineKeyboardButton("🏘 مسکن - 10K ظرفیت", callback_data="build_housing")
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
                InlineKeyboardButton("🛡 وضعیت دفاعی", callback_data="defense_status"),
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
                InlineKeyboardButton("⚔️ حمله به کشور", callback_data="select_attack_target"),
                InlineKeyboardButton("📬 ارسال منابع", callback_data="send_resources")
            ],
            [
                InlineKeyboardButton("🤝 اتحادها", callback_data="alliances"),
                InlineKeyboardButton("🛒 فروشگاه", callback_data="marketplace")
            ],
            [
                InlineKeyboardButton("🕊 پیشنهاد صلح", callback_data="propose_peace"),
                InlineKeyboardButton("🏴 بیانیه رسمی", callback_data="official_statement")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def alliance_menu_keyboard(self, has_alliance=False):
        """Create alliance menu keyboard"""
        if has_alliance:
            keyboard = [
                [
                    InlineKeyboardButton("👥 اعضای اتحاد", callback_data="alliance_members"),
                    InlineKeyboardButton("📨 دعوت بازیکن", callback_data="alliance_invite")
                ],
                [
                    InlineKeyboardButton("📋 دعوت‌نامه‌ها", callback_data="alliance_invitations"),
                    InlineKeyboardButton("🚪 ترک اتحاد", callback_data="alliance_leave")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")
                ]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("➕ تشکیل اتحاد", callback_data="alliance_create"),
                    InlineKeyboardButton("📋 دعوت‌نامه‌ها", callback_data="alliance_invitations")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")
                ]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def marketplace_menu_keyboard(self):
        """Create marketplace menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🛒 خرید کالا", callback_data="market_browse"),
                InlineKeyboardButton("💰 فروش کالا", callback_data="market_sell")
            ],
            [
                InlineKeyboardButton("📋 آگهی‌های من", callback_data="market_my_listings"),
                InlineKeyboardButton("📊 تاریخچه خرید", callback_data="market_history")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def market_categories_keyboard(self):
        """Create market categories keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("⚔️ تسلیحات", callback_data="market_cat_weapon"),
                InlineKeyboardButton("📦 منابع", callback_data="market_cat_resource")
            ],
            [
                InlineKeyboardButton("💰 پول", callback_data="market_cat_money"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="marketplace")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def attack_targets_keyboard(self, available_targets):
        """Create attack targets keyboard"""
        keyboard = []

        for target in available_targets:
            flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')
            button = InlineKeyboardButton(
                f"{flag} {target['country_name']}",
                callback_data=f"attack_{target['user_id']}"
            )
            keyboard.append([button])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")])
        return InlineKeyboardMarkup(keyboard)

    def send_resources_targets_keyboard(self, countries):
        """Create send resources targets keyboard"""
        keyboard = []
        
        for country in countries:
            flag = Config.COUNTRY_FLAGS.get(country.get('country_code'), '🏳')
            button = InlineKeyboardButton(
                f"{flag} {country['country_name']}",
                callback_data=f"send_to_{country['user_id']}"
            )
            keyboard.append([button])
        
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")])
        return InlineKeyboardMarkup(keyboard)
    
    def resource_transfer_keyboard(self, target_id, transfer_options):
        """Create resource transfer options keyboard"""
        keyboard = []
        
        for option_code, option_text in transfer_options:
            button = InlineKeyboardButton(
                option_text,
                callback_data=f"transfer_{target_id}_{option_code}"
            )
            keyboard.append([button])
        
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="send_resources")])
        return InlineKeyboardMarkup(keyboard)

    def back_to_main_keyboard(self):
        """Simple back to main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_panel_keyboard(self):
        """Create admin panel keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📊 آمار بازی", callback_data="admin_stats"),
                InlineKeyboardButton("👥 مدیریت بازیکنان", callback_data="admin_players")
            ],
            [
                InlineKeyboardButton("📋 لاگ‌ها", callback_data="admin_logs"),
                InlineKeyboardButton("🔄 ریست بازی", callback_data="admin_reset")
            ],
            [
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_players_keyboard(self, players):
        """Create admin players management keyboard"""
        keyboard = []
        
        for player in players[:10]:  # Show max 10 players
            flag = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳')
            button = InlineKeyboardButton(
                f"{flag} {player['country_name']}",
                callback_data=f"admin_player_{player['user_id']}"
            )
            keyboard.append([button])
        
        keyboard.append([InlineKeyboardButton("🔙 پنل ادمین", callback_data="admin_panel")])
        return InlineKeyboardMarkup(keyboard)
    
    def admin_player_actions_keyboard(self, user_id):
        """Create admin actions keyboard for specific player"""
        keyboard = [
            [
                InlineKeyboardButton("💰 اضافه کردن پول", callback_data=f"admin_add_money_{user_id}"),
                InlineKeyboardButton("📊 نمایش کامل", callback_data=f"admin_view_{user_id}")
            ],
            [
                InlineKeyboardButton("❌ حذف بازیکن", callback_data=f"admin_delete_{user_id}")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_players")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)