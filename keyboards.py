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
                InlineKeyboardButton("⛏ معدن آهن - $80K", callback_data="build_iron_mine"),
                InlineKeyboardButton("⛏ معدن مس - $100K", callback_data="build_copper_mine")
            ],
            [
                InlineKeyboardButton("🛢 معدن نفت - $120K", callback_data="build_oil_mine"),
                InlineKeyboardButton("⛽ معدن گاز - $110K", callback_data="build_gas_mine")
            ],
            [
                InlineKeyboardButton("🔗 معدن آلومینیوم - $90K", callback_data="build_aluminum_mine"),
                InlineKeyboardButton("🏆 معدن طلا - $150K", callback_data="build_gold_mine")
            ],
            [
                InlineKeyboardButton("☢️ معدن اورانیوم - $690K", callback_data="build_uranium_mine"),
                InlineKeyboardButton("🔋 معدن لیتیوم - $180K", callback_data="build_lithium_mine")
            ],
            [
                InlineKeyboardButton("⚫ معدن زغال - $85K", callback_data="build_coal_mine"),
                InlineKeyboardButton("🥈 معدن نقره - $140K", callback_data="build_silver_mine")
            ],
            [
                InlineKeyboardButton("💥 معدن نیتر - $95K", callback_data="build_nitro_mine"),
                InlineKeyboardButton("🌫 معدن گوگرد - $75K", callback_data="build_sulfur_mine")
            ],
            [
                InlineKeyboardButton("🛡 معدن تیتانیوم - $250K", callback_data="build_titanium_mine")
            ],
            [
                InlineKeyboardButton("🏭 کارخانه اسلحه - $15K", callback_data="build_weapon_factory"),
                InlineKeyboardButton("⚡ نیروگاه - $9K", callback_data="build_power_plant")
            ],
            [
                InlineKeyboardButton("🏭 پالایشگاه - $10K", callback_data="build_refinery"),
                InlineKeyboardButton("🌾 مزرعه - $5K", callback_data="build_wheat_farm")
            ],
            [
                InlineKeyboardButton("🪖 پادگان - $5K", callback_data="build_military_base"),
                InlineKeyboardButton("🏘 مسکن - $5K", callback_data="build_housing")
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
                InlineKeyboardButton("🔫 سلاح‌های پایه", callback_data="weapon_cat_basic"),
                InlineKeyboardButton("🛡 سیستم‌های دفاعی", callback_data="weapon_cat_defense")
            ],
            [
                InlineKeyboardButton("🚢 تسلیحات دریایی", callback_data="weapon_cat_naval"),
                InlineKeyboardButton("💣 بمب‌ها", callback_data="weapon_cat_bombs")
            ],
            [
                InlineKeyboardButton("🚀 موشک‌های ساده", callback_data="weapon_cat_missiles"),
                InlineKeyboardButton("⚡ موشک‌های مخصوص", callback_data="weapon_cat_special_missiles")
            ],
            [
                InlineKeyboardButton("✈️ جت‌های پیشرفته", callback_data="weapon_cat_advanced_jets"),
                InlineKeyboardButton("🚚 تجهیزات حمل‌ونقل", callback_data="weapon_cat_transport")
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
                    InlineKeyboardButton("🔫 تفنگ", callback_data="select_weapon_rifle"),
                    InlineKeyboardButton("🚗 تانک", callback_data="select_weapon_tank")
                ],
                [
                    InlineKeyboardButton("✈️ جنگنده", callback_data="select_weapon_fighter_jet"),
                    InlineKeyboardButton("🚁 پهپاد", callback_data="select_weapon_drone")
                ],
                [
                    InlineKeyboardButton("🚢 کشتی جنگی", callback_data="select_weapon_warship")
                ]
            ]
        elif category == "defense":
            keyboard = [
                [
                    InlineKeyboardButton("🛡 پدافند هوایی", callback_data="select_weapon_air_defense"),
                    InlineKeyboardButton("🚀 سپر موشکی", callback_data="select_weapon_missile_shield")
                ],
                [
                    InlineKeyboardButton("💻 سپر سایبری", callback_data="select_weapon_cyber_shield")
                ]
            ]
        elif category == "bombs":
            keyboard = [
                [
                    InlineKeyboardButton("💣 بمب ساده", callback_data="select_weapon_simple_bomb"),
                    InlineKeyboardButton("☢️ بمب هسته‌ای", callback_data="select_weapon_nuclear_bomb")
                ]
            ]
        elif category == "missiles":
            keyboard = [
                [
                    InlineKeyboardButton("🚀 موشک ساده", callback_data="select_weapon_simple_missile"),
                    InlineKeyboardButton("🚀 موشک بالستیک", callback_data="select_weapon_ballistic_missile")
                ],
                [
                    InlineKeyboardButton("☢️ موشک هسته‌ای", callback_data="select_weapon_nuclear_missile")
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
                    InlineKeyboardButton("✈️ F-22", callback_data="select_weapon_f22"),
                    InlineKeyboardButton("✈️ F-35", callback_data="select_weapon_f35")
                ],
                [
                    InlineKeyboardButton("✈️ Su-57", callback_data="select_weapon_su57"),
                    InlineKeyboardButton("✈️ J-20", callback_data="select_weapon_j20")
                ],
                [
                    InlineKeyboardButton("✈️ F-15EX", callback_data="select_weapon_f15ex"),
                    InlineKeyboardButton("✈️ Su-35S", callback_data="select_weapon_su35s")
                ]
            ]
        elif category == "transport":
            keyboard = [
                [
                    InlineKeyboardButton("🚛کامیون زرهی", callback_data="select_weapon_armored_truck"),
                    InlineKeyboardButton("🚁 هلیکوپتر باری", callback_data="select_weapon_cargo_helicopter")
                ],
                [
                    InlineKeyboardButton("✈️ هواپیمای باری", callback_data="select_weapon_cargo_plane"),
                    InlineKeyboardButton("🛡 ناوچه اسکورت", callback_data="select_weapon_escort_frigate")
                ],
                [
                    InlineKeyboardButton("🚁 پهپاد لجستیک", callback_data="select_weapon_logistics_drone"),
                    InlineKeyboardButton("🚚 ترابری سنگین", callback_data="select_weapon_heavy_transport")
                ],
                [
                    InlineKeyboardButton("🚢 کشتی تدارکات", callback_data="select_weapon_supply_ship"),
                    InlineKeyboardButton("🥷 ترابری پنهان‌کار", callback_data="select_weapon_stealth_transport")
                ]
            ]
        elif category == "naval":
            keyboard = [
                [
                    InlineKeyboardButton("🚢 ناو هواپیمابر", callback_data="select_weapon_aircraft_carrier"),
                    InlineKeyboardButton("🚢 ناو جنگی", callback_data="select_weapon_warship")
                ],
                [
                    InlineKeyboardButton("🚢 ناوشکن", callback_data="select_weapon_destroyer"),
                    InlineKeyboardButton("🚢 زیردریایی هسته‌ای", callback_data="select_weapon_nuclear_submarine")
                ],
                [
                    InlineKeyboardButton("🚢 کشتی گشتی", callback_data="select_weapon_patrol_boat"),
                    InlineKeyboardButton("🚢 قایق گشتی", callback_data="select_weapon_speed_boat")
                ],
                [
                    InlineKeyboardButton("🚢 کشتی آبی-خاکی", callback_data="select_weapon_amphibious_assault_ship")
                ]
            ]

        keyboard.append([InlineKeyboardButton("🔙 منوی تسلیحات", callback_data="weapons")])
        return InlineKeyboardMarkup(keyboard)

    def diplomacy_menu_keyboard(self, user_id):
        """Create diplomacy menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("⚔️ انتخاب هدف حمله", callback_data="select_attack_target"),
                InlineKeyboardButton("🚚 انتقال منابع", callback_data="send_resources")
            ],
            [
                InlineKeyboardButton("🏴‍☠️ دزدی محموله", callback_data="intercept_convoys"),
                InlineKeyboardButton("📢 بیانیه رسمی", callback_data="official_statement")
            ],
            [
                InlineKeyboardButton("🕊 پیشنهاد صلح", callback_data="propose_peace"),
                InlineKeyboardButton("🤝 اتحادها", callback_data="alliances")
            ],
            [
                InlineKeyboardButton("🛒 فروشگاه", callback_data="marketplace")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def alliance_menu_keyboard(self, has_alliance=False):
        """Create alliance menu keyboard"""
        if has_alliance:
            keyboard = [
                [
                    InlineKeyboardButton("👥 اعضای اتحاد", callback_data="alliance_members"),
                    InlineKeyboardButton("📨 دعوت بازیکن", callback_data="alliance_invite_list") # Changed callback
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
                callback_data=f"select_target_{target['user_id']}"
            )
            keyboard.append([button])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")])
        return InlineKeyboardMarkup(keyboard)

    def attack_type_selection_keyboard(self, target_id):
        """Create keyboard for attack type selection"""
        keyboard = [
            [
                InlineKeyboardButton("🌀 حمله ترکیبی", callback_data=f"attack_type_{target_id}_mixed"),
                InlineKeyboardButton("🏔 حمله زمینی", callback_data=f"attack_type_{target_id}_ground")
            ],
            [
                InlineKeyboardButton("✈️ حمله هوایی", callback_data=f"attack_type_{target_id}_air"),
                InlineKeyboardButton("⚓ حمله دریایی", callback_data=f"attack_type_{target_id}_naval")
            ],
            [
                InlineKeyboardButton("🚀 حمله موشکی", callback_data=f"attack_type_{target_id}_missile"),
                InlineKeyboardButton("⚡ حمله سایبری", callback_data=f"attack_type_{target_id}_cyber")
            ],
            [
                InlineKeyboardButton("🔙 انتخاب هدف دیگر", callback_data=f"select_attack_target")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def weapon_selection_keyboard(self, target_id, attack_type, available_weapons, selected_weapons=None):
        """Create keyboard for weapon selection in attack"""
        if selected_weapons is None:
            selected_weapons = {}

        keyboard = []

        # Filter weapons by attack type
        filtered_weapons = self._filter_weapons_by_attack_type(attack_type, available_weapons)

        row = []
        for weapon_key, weapon_data in filtered_weapons.items():
            count = available_weapons.get(weapon_key, 0)
            selected = selected_weapons.get(weapon_key, 0)

            if count > 0:
                weapon_name = weapon_data['name']
                emoji = self._get_weapon_emoji(weapon_key)

                if selected > 0:
                    button_text = f"✅ {emoji} {weapon_name} ({selected}/{count})"
                else:
                    button_text = f"{emoji} {weapon_name} ({count})"

                callback_data = f"select_weapon_attack_{target_id}_{attack_type}_{weapon_key}"

                row.append(InlineKeyboardButton(button_text, callback_data=callback_data))

                if len(row) == 2:
                    keyboard.append(row)
                    row = []

        if row:
            keyboard.append(row)

        keyboard.extend([
            [InlineKeyboardButton("⚔️ شروع حمله", callback_data=f"execute_attack_{target_id}_{attack_type}")],
            [InlineKeyboardButton("🔙 انتخاب نوع حمله", callback_data=f"select_target_{target_id}")]
        ])

        return InlineKeyboardMarkup(keyboard)

    def _filter_weapons_by_attack_type(self, attack_type, available_weapons):
        """Filter weapons based on attack type"""
        filtered = {}

        for weapon_key, count in available_weapons.items():
            if weapon_key in Config.WEAPONS and count > 0:
                weapon_data = Config.WEAPONS[weapon_key]
                category = weapon_data.get('category', '')

                include_weapon = False

                if attack_type == "mixed":
                    include_weapon = True
                elif attack_type == "ground" and category in ['basic', 'ground', 'defense', 'transport']:
                    include_weapon = True
                elif attack_type == "air" and category in ['air', 'advanced_jets', 'transport']:
                    include_weapon = True
                elif attack_type == "naval" and category in ['naval', 'transport']:
                    include_weapon = True
                elif attack_type == "missile" and category in ['missiles', 'special_missiles']:
                    include_weapon = True
                elif attack_type == "cyber" and category in ['defense']:
                    include_weapon = True

                if include_weapon:
                    filtered[weapon_key] = weapon_data

        return filtered

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

        # Add manual input button
        keyboard.append([InlineKeyboardButton("✏️ مقدار دستی", callback_data=f"manual_transfer_{target_id}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="send_resources")])
        return InlineKeyboardMarkup(keyboard)

    def back_to_main_keyboard(self):
        """Back to main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def back_to_military_keyboard(self):
        """Back to military menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به منوی نظامی", callback_data="military")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def back_to_diplomacy_keyboard(self):
        """Back to diplomacy keyboard"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")]]
        return InlineKeyboardMarkup(keyboard)

    def convoy_action_confirmation_keyboard(self, convoy_id, action_type, can_perform=True):
        """Create convoy action confirmation keyboard"""
        keyboard = []

        if can_perform:
            if action_type == "stop":
                keyboard.append([InlineKeyboardButton("✅ تایید توقف محموله", callback_data=f"confirm_convoy_stop_{convoy_id}")])
            elif action_type == "steal":
                keyboard.append([InlineKeyboardButton("✅ تایید سرقت محموله", callback_data=f"confirm_convoy_steal_{convoy_id}")])
        else:
            keyboard.append([InlineKeyboardButton("❌ امکان انجام عملیات نیست", callback_data="convoy_info")])

        keyboard.append([InlineKeyboardButton("🔙 انصراف", callback_data="intercept_convoys")])
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
                InlineKeyboardButton("♾️ منابع بینهایت", callback_data="admin_infinite_resources"),
                InlineKeyboardButton("🏴 ریست کشور", callback_data="admin_country_reset")
            ],
            [
                InlineKeyboardButton("🎁 هدیه به کشورها", callback_data="admin_give_items")
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
                InlineKeyboardButton("🎁 هدیه آیتم", callback_data=f"admin_give_to_{user_id}"),
                InlineKeyboardButton("❌ حذف بازیکن", callback_data=f"admin_delete_{user_id}")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_players")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def admin_give_items_keyboard(self):
        """Create admin give items keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("💰 پول", callback_data="admin_give_all_to_money_1000000"),
                InlineKeyboardButton("🔩 آهن", callback_data="admin_give_all_to_iron_50000")
            ],
            [
                InlineKeyboardButton("🥉 مس", callback_data="admin_give_all_to_copper_30000"),
                InlineKeyboardButton("🛢 نفت", callback_data="admin_give_all_to_oil_25000")
            ],
            [
                InlineKeyboardButton("🔗 آلومینیوم", callback_data="admin_give_all_to_aluminum_20000"),
                InlineKeyboardButton("🏆 طلا", callback_data="admin_give_all_to_gold_10000")
            ],
            [
                InlineKeyboardButton("☢️ اورانیوم", callback_data="admin_give_all_to_uranium_5000"),
                InlineKeyboardButton("🔋 لیتیوم", callback_data="admin_give_all_to_lithium_8000")
            ],
            [
                InlineKeyboardButton("⚫ زغال‌سنگ", callback_data="admin_give_all_to_coal_15000"),
                InlineKeyboardButton("💥 نیتر", callback_data="admin_give_all_to_nitro_12000")
            ],
            [
                InlineKeyboardButton("🌫 گوگرد", callback_data="admin_give_all_to_sulfur_10000"),
                InlineKeyboardButton("🛡 تیتانیوم", callback_data="admin_give_all_to_titanium_3000")
            ],
            [
                InlineKeyboardButton("🔫 تفنگ", callback_data="admin_give_all_to_rifle_1000"),
                InlineKeyboardButton("🚗 تانک", callback_data="admin_give_all_to_tank_50")
            ],
            [
                InlineKeyboardButton("✈️ جنگنده", callback_data="admin_give_all_to_fighter_20"),
                InlineKeyboardButton("🚁 پهپاد", callback_data="admin_give_all_to_drone_30")
            ],
            [
                InlineKeyboardButton("🚀 جت جنگی", callback_data="admin_give_all_to_jet_15"),
                InlineKeyboardButton("🚢 ناو جنگی", callback_data="admin_give_all_to_warship_10")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_menu")
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
        """Create keyboard for admin weapon gifting"""
        keyboard = []

        # Basic weapons
        keyboard.append([
            InlineKeyboardButton("🔫 1000 تفنگ", callback_data="admin_give_rifle_1000"),
            InlineKeyboardButton("🔫 5000 تفنگ", callback_data="admin_give_rifle_5000")
        ])

        keyboard.append([
            InlineKeyboardButton("🚗 100 تانک", callback_data="admin_give_tank_100"),
            InlineKeyboardButton("🚗 500 تانک", callback_data="admin_give_tank_500")
        ])

        # Aircraft
        keyboard.append([
            InlineKeyboardButton("✈️ 50 جنگنده", callback_data="admin_give_fighter_50"),
            InlineKeyboardButton("🚁 100 پهپاد", callback_data="admin_give_drone_100")
        ])

        # Advanced weapons
        keyboard.append([
            InlineKeyboardButton("🚀 10 موشک", callback_data="admin_give_missile_10"),
            InlineKeyboardButton("💣 5 بمب هسته‌ای", callback_data="admin_give_nuclear_5")
        ])

        # Special jets
        keyboard.append([
            InlineKeyboardButton("✈️ 1 F-22", callback_data="admin_give_f22_1"),
            InlineKeyboardButton("🚀 5 موشک بالستیک", callback_data="admin_give_ballistic_5")
        ])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_give_items")])

        return InlineKeyboardMarkup(keyboard)

    def admin_give_money_keyboard(self):
        """Create keyboard for admin money gifting"""
        keyboard = []

        # Small amounts
        keyboard.append([
            InlineKeyboardButton("💰 $10,000", callback_data="admin_give_money_10000"),
            InlineKeyboardButton("💰 $50,000", callback_data="admin_give_money_50000")
        ])

        # Medium amounts  
        keyboard.append([
            InlineKeyboardButton("💰 $100,000", callback_data="admin_give_money_100000"),
            InlineKeyboardButton("💰 $500,000", callback_data="admin_give_money_500000")
        ])

        # Large amounts
        keyboard.append([
            InlineKeyboardButton("💰 $1,000,000", callback_data="admin_give_money_1000000"),
            InlineKeyboardButton("💰 $5,000,000", callback_data="admin_give_money_5000000")
        ])

        # Very large amounts
        keyboard.append([
            InlineKeyboardButton("💰 $10,000,000", callback_data="admin_give_money_10000000"),
            InlineKeyboardButton("💰 $100,000,000", callback_data="admin_give_money_100000000")
        ])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_give_items")])

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

    def convoy_private_confirmation_keyboard(self, convoy_id, action_type):
        """Create convoy confirmation keyboard for private messages"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تایید", callback_data=f"confirm_convoy_{action_type}_{convoy_id}"),
                InlineKeyboardButton("❌ انصراف", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def quantity_selection_keyboard(self, item_type, item_name):
        """کیبورد انتخاب تعداد برای ساخت سلاح یا ساختمان"""
        keyboard = [
            [
                InlineKeyboardButton("1 عدد", callback_data=f"quantity_{item_type}_{item_name}_1"),
                InlineKeyboardButton("5 عدد", callback_data=f"quantity_{item_type}_{item_name}_5")
            ],
            [
                InlineKeyboardButton("10 عدد", callback_data=f"quantity_{item_type}_{item_name}_10"),
                InlineKeyboardButton("25 عدد", callback_data=f"quantity_{item_type}_{item_name}_25")
            ],
            [
                InlineKeyboardButton("50 عدد", callback_data=f"quantity_{item_type}_{item_name}_50"),
                InlineKeyboardButton("100 عدد", callback_data=f"quantity_{item_type}_{item_name}_100")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="weapons" if item_type == "weapon" else "buildings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def _get_weapon_emoji(self, weapon_key):
        """Get appropriate emoji for weapon"""
        emoji_map = {
            'rifle': '🔫', 'tank': '🚗', 'fighter_jet': '✈️', 'drone': '🚁',
            'warship': '🚢', 'air_defense': '🛡', 'missile_shield': '🚀',
            'cyber_shield': '💻', 'f22': '✈️', 'f35': '✈️', 'su57': '✈️',
            'j20': '✈️', 'missile': '🚀', 'nuclear_missile': '☢️',
            'armored_truck': '🚛', 'cargo_helicopter': '🚁', 'cargo_plane': '✈️',
            'stealth_transport': '🛸', 'aircraft_carrier': '🚢', 'destroyer': '🚢',
            'nuclear_submarine': '🚢', 'patrol_boat': '🚢', 'speed_boat': '🚢',
            'amphibious_assault_ship': '🚢'
        }
        return emoji_map.get(weapon_key, '⚔️')

    def alliance_invite_keyboard(self, all_players=None):
        """Keyboard for alliance invite options"""
        keyboard = []

        if all_players:
            # Show list of countries to invite
            for player in all_players[:10]:  # Limit to 10 players
                country_flag = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳')
                country_name = player['country_name']
                keyboard.append([
                    InlineKeyboardButton(
                        f"{country_flag} {country_name}", 
                        callback_data=f"alliance_invite_{player['user_id']}"
                    )
                ])
        else:
            keyboard.append([InlineKeyboardButton("📧 دعوت عضو جدید", callback_data="alliance_invite_list")])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="alliance_menu")])
        return InlineKeyboardMarkup(keyboard)