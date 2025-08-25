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
        """Create weapons production categories menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔫 سلاح‌های پایه", callback_data="weapon_cat_basic"),
                InlineKeyboardButton("🛡 سیستم‌های دفاعی", callback_data="weapon_cat_defense")
            ],
            [
                InlineKeyboardButton("💣 بمب‌ها", callback_data="weapon_cat_bombs"),
                InlineKeyboardButton("🚀 موشک‌های ساده", callback_data="weapon_cat_missiles")
            ],
            [
                InlineKeyboardButton("☢️ موشک‌های مخصوص", callback_data="weapon_cat_special_missiles"),
                InlineKeyboardButton("✈️ جت‌های پیشرفته", callback_data="weapon_cat_advanced_jets")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="military")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def weapon_category_keyboard(self, category):
        """Create keyboard for specific weapon category"""
        keyboard = []
        
        if category == "basic":
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
                    InlineKeyboardButton("🚢 کشتی جنگی", callback_data="produce_warship")
                ]
            ]
        elif category == "defense":
            keyboard = [
                [
                    InlineKeyboardButton("🛡 پدافند هوایی", callback_data="produce_air_defense"),
                    InlineKeyboardButton("🚀 سپر موشکی", callback_data="produce_missile_shield")
                ],
                [
                    InlineKeyboardButton("💻 سپر سایبری", callback_data="produce_cyber_shield")
                ]
            ]
        elif category == "bombs":
            keyboard = [
                [
                    InlineKeyboardButton("💣 بمب ساده", callback_data="produce_simple_bomb"),
                    InlineKeyboardButton("☢️ بمب هسته‌ای", callback_data="produce_nuclear_bomb")
                ]
            ]
        elif category == "missiles":
            keyboard = [
                [
                    InlineKeyboardButton("🚀 موشک ساده", callback_data="produce_simple_missile"),
                    InlineKeyboardButton("🚀 موشک بالستیک", callback_data="produce_ballistic_missile")
                ],
                [
                    InlineKeyboardButton("☢️ موشک هسته‌ای", callback_data="produce_nuclear_missile")
                ]
            ]
        elif category == "special_missiles":
            keyboard = [
                [
                    InlineKeyboardButton("🚀 Trident 2 غیر هسته‌ای", callback_data="produce_trident2_conventional"),
                    InlineKeyboardButton("☢️ Trident 2 هسته‌ای", callback_data="produce_trident2_nuclear")
                ],
                [
                    InlineKeyboardButton("🚀 Satan2 غیر هسته‌ای", callback_data="produce_satan2_conventional"),
                    InlineKeyboardButton("☢️ Satan2 هسته‌ای", callback_data="produce_satan2_nuclear")
                ],
                [
                    InlineKeyboardButton("☢️ DF-41 هسته‌ای", callback_data="produce_df41_nuclear")
                ],
                [
                    InlineKeyboardButton("🚀 Tomahawk غیر هسته‌ای", callback_data="produce_tomahawk_conventional"),
                    InlineKeyboardButton("☢️ Tomahawk هسته‌ای", callback_data="produce_tomahawk_nuclear")
                ],
                [
                    InlineKeyboardButton("🚀 Kalibr غیر هسته‌ای", callback_data="produce_kalibr_conventional")
                ]
            ]
        elif category == "advanced_jets":
            keyboard = [
                [
                    InlineKeyboardButton("✈️ F-22", callback_data="produce_f22"),
                    InlineKeyboardButton("✈️ F-35", callback_data="produce_f35")
                ],
                [
                    InlineKeyboardButton("✈️ Su-57", callback_data="produce_su57"),
                    InlineKeyboardButton("✈️ J-20", callback_data="produce_j20")
                ],
                [
                    InlineKeyboardButton("✈️ F-15EX", callback_data="produce_f15ex"),
                    InlineKeyboardButton("✈️ Su-35S", callback_data="produce_su35s")
                ]
            ]
        
        keyboard.append([InlineKeyboardButton("🔙 منوی تسلیحات", callback_data="weapon_production")])
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
                InlineKeyboardButton("⚔️ تسلیحات", callback_data="market_cat_weapons"),
                InlineKeyboardButton("📊 منابع", callback_data="market_cat_resources")
            ],
            [
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
                InlineKeyboardButton("🎁 هدیه به کشورها", callback_data="admin_give_items"),
                InlineKeyboardButton("📋 لاگ‌ها", callback_data="admin_logs")
            ],
            [
                InlineKeyboardButton("🔄 ریست بازی", callback_data="admin_reset"),
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
                InlineKeyboardButton("🎁 هدیه آیتم", callback_data=f"admin_give_to_{user_id}"),
                InlineKeyboardButton("❌ حذف بازیکن", callback_data=f"admin_delete_{user_id}")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_players")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_give_items_keyboard(self):
        """Create admin give items category keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("💰 پول", callback_data="admin_give_cat_money"),
                InlineKeyboardButton("📦 منابع", callback_data="admin_give_cat_resources")
            ],
            [
                InlineKeyboardButton("⚔️ سلاح‌ها", callback_data="admin_give_cat_weapons"),
                InlineKeyboardButton("🏗 ساختمان‌ها", callback_data="admin_give_cat_buildings")
            ],
            [
                InlineKeyboardButton("👥 جمعیت", callback_data="admin_give_cat_population"),
                InlineKeyboardButton("🪖 سرباز", callback_data="admin_give_cat_soldiers")
            ],
            [
                InlineKeyboardButton("🔙 پنل ادمین", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_give_resources_keyboard(self):
        """Create keyboard for giving resources"""
        keyboard = [
            [
                InlineKeyboardButton("🔩 آهن (1000)", callback_data="admin_give_iron_1000"),
                InlineKeyboardButton("🥉 مس (1000)", callback_data="admin_give_copper_1000")
            ],
            [
                InlineKeyboardButton("🛢 نفت (1000)", callback_data="admin_give_oil_1000"),
                InlineKeyboardButton("🔗 آلومینیوم (1000)", callback_data="admin_give_aluminum_1000")
            ],
            [
                InlineKeyboardButton("🏆 طلا (100)", callback_data="admin_give_gold_100"),
                InlineKeyboardButton("☢️ اورانیوم (100)", callback_data="admin_give_uranium_100")
            ],
            [
                InlineKeyboardButton("🔋 لیتیوم (500)", callback_data="admin_give_lithium_500"),
                InlineKeyboardButton("⚫ زغال‌سنگ (1000)", callback_data="admin_give_coal_1000")
            ],
            [
                InlineKeyboardButton("💥 نیتر (500)", callback_data="admin_give_nitro_500"),
                InlineKeyboardButton("🌫 گوگرد (500)", callback_data="admin_give_sulfur_500")
            ],
            [
                InlineKeyboardButton("🛡 تیتانیوم (100)", callback_data="admin_give_titanium_100")
            ],
            [
                InlineKeyboardButton("🔙 انتخاب دسته", callback_data="admin_give_items")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_give_weapons_keyboard(self):
        """Create keyboard for giving weapons"""
        keyboard = [
            [
                InlineKeyboardButton("🔫 تفنگ (10)", callback_data="admin_give_rifle_10"),
                InlineKeyboardButton("🚗 تانک (5)", callback_data="admin_give_tank_5")
            ],
            [
                InlineKeyboardButton("✈️ جنگنده (3)", callback_data="admin_give_fighter_jet_3"),
                InlineKeyboardButton("🚁 پهپاد (3)", callback_data="admin_give_drone_3")
            ],
            [
                InlineKeyboardButton("💣 بمب ساده (5)", callback_data="admin_give_simple_bomb_5"),
                InlineKeyboardButton("☢️ بمب هسته‌ای (1)", callback_data="admin_give_nuclear_bomb_1")
            ],
            [
                InlineKeyboardButton("🚀 موشک ساده (3)", callback_data="admin_give_simple_missile_3"),
                InlineKeyboardButton("🚀 موشک بالستیک (2)", callback_data="admin_give_ballistic_missile_2")
            ],
            [
                InlineKeyboardButton("☢️ موشک هسته‌ای (1)", callback_data="admin_give_nuclear_missile_1"),
                InlineKeyboardButton("✈️ F-22 (1)", callback_data="admin_give_f22_1")
            ],
            [
                InlineKeyboardButton("🔙 انتخاب دسته", callback_data="admin_give_items")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def convoy_action_keyboard(self, convoy_id):
        """Create convoy action keyboard for news channel"""
        keyboard = [
            [
                InlineKeyboardButton("⛔ توقف محموله", callback_data=f"convoy_stop_{convoy_id}"),
                InlineKeyboardButton("💰 سرقت محموله", callback_data=f"convoy_steal_{convoy_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)