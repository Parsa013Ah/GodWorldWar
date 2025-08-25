import logging
import asyncio
import os
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime

from database import Database
from game_logic import GameLogic
from keyboards import Keyboards
from admin import AdminPanel
from economy import Economy
from news import NewsChannel
from combat import CombatSystem
from countries import CountryManager
from config import Config
from convoy import ConvoySystem
from alliance import AllianceSystem
from marketplace import Marketplace

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DragonRPBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "8264945069:AAE2WYv463Sk0a52sS6hTvR6tzEs8WCmJtI")
        self.db = Database()
        self.game_logic = GameLogic(self.db)
        self.keyboards = Keyboards()
        self.admin = AdminPanel(self.db)
        self.economy = Economy(self.db)
        self.combat = CombatSystem(self.db)
        self.countries = CountryManager(self.db)
        self.news = NewsChannel()
        self.convoy = ConvoySystem(self.db)
        self.alliance = AllianceSystem(self.db)
        self.marketplace = Marketplace(self.db)
        self.scheduler = AsyncIOScheduler()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        # Log user info for admin setup
        logger.info(f"User started bot - ID: {user_id}, Username: {username}")

        # Check if there's a convoy action parameter
        if context.args and len(context.args) > 0:
            action_param = context.args[0]
            if action_param.startswith("convoy_stop_"):
                convoy_id = int(action_param.replace("convoy_stop_", ""))
                await self.handle_convoy_action_from_start(update, context, convoy_id, "stop")
                return
            elif action_param.startswith("convoy_steal_"):
                convoy_id = int(action_param.replace("convoy_steal_", ""))
                await self.handle_convoy_action_from_start(update, context, convoy_id, "steal")
                return

        # Check if user already has a country
        player = self.db.get_player(user_id)
        if player:
            await self.show_main_menu(update, context)
            return

        # Show welcome message and country selection
        welcome_text = """🎮 خوش آمدید به جنگ جهانی - DragonRP!

در این بازی استراتژیک، شما یک کشور را کنترل می‌کنید.
هدف: ساختن اقتصاد، تولید منابع، ایجاد ارتش و تسلط بر دیگر کشورها

لطفاً کشور خود را انتخاب کنید:"""

        keyboard = self.keyboards.country_selection_keyboard()
        await update.message.reply_text(welcome_text, reply_markup=keyboard)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query

        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Failed to answer callback query: {e}")

        user_id = query.from_user.id
        data = query.data

        try:
            if data.startswith("select_country_"):
                await self.handle_country_selection(query, context)
            elif data == "main_menu":
                await self.show_main_menu_callback(query, context)
            elif data == "economy":
                await self.show_economy_menu(query, context)
            elif data == "military":
                await self.show_military_menu(query, context)
            elif data == "diplomacy":
                await self.show_diplomacy_menu(query, context)
            elif data == "resources":
                await self.show_resources_menu(query, context)
            elif data == "buildings":
                await self.show_buildings_menu(query, context)
            elif data == "weapons" or data == "weapon_production":
                await self.show_weapons_menu(query, context)
            elif data.startswith("weapon_cat_"):
                await self.show_weapon_category(query, context)
            elif data.startswith("build_"):
                await self.handle_building_construction(query, context)
            elif data.startswith("produce_") or data.startswith("select_weapon_"):
                # Check if it's quantity selection or direct production
                if data.count("_") > 1:  # select_weapon_rifle format
                    await self.show_weapon_quantity_selection(query, context)
                else:  # produce_rifle format
                    await self.handle_weapon_production(query, context)
            elif data.startswith("select_building_"):
                await self.show_building_quantity_selection(query, context)
            elif data.startswith("quantity_"):
                await self.handle_quantity_selection(query, context)
            elif data == "select_attack_target":
                await self.show_attack_targets(query, context)
            elif data == "attack_menu":
                await self.show_attack_targets(query, context)
            elif data.startswith("select_target_"):
                await self.show_attack_type_selection(query, context)
            elif data.startswith("attack_type_"):
                await self.show_weapon_selection_for_attack(query, context)
            elif data.startswith("execute_attack_"):
                await self.handle_attack_execution(query, context)
            elif data == "send_resources":
                await self.show_send_resources_menu(query, context)
            elif data == "official_statement":
                await self.handle_official_statement(query, context)
            elif data == "income_report":
                await self.show_income_report(query, context)
            elif data == "defense_status":
                await self.show_defense_status(query, context)
            elif data == "military_power":
                await self.show_military_power(query, context)
            elif data == "propose_peace":
                await self.show_propose_peace(query, context)
            elif data == "intercept_convoys":
                await self.show_convoy_interception_menu(query, context)
            elif data.startswith("send_to_"):
                await self.handle_resource_transfer_target(query, context)
            elif data.startswith("transfer_"):
                await self.handle_resource_transfer(query, context)
            elif data.startswith("convoy_"):
                await self.handle_convoy_action(query, context)
            elif data.startswith("confirm_convoy_"):
                await self.handle_convoy_confirmation(query, context)
            elif data == "alliances":
                await self.show_alliance_menu(query, context)
            elif data.startswith("alliance_"):
                await self.handle_alliance_action(query, context)
            elif data == "marketplace":
                await self.show_marketplace_menu(query, context)
            elif data.startswith("market_"):
                await self.handle_marketplace_action(query, context)
            elif data.startswith("invite_"):
                await self.handle_alliance_invite(query, context)
            elif data.startswith("accept_inv_"):
                await self.handle_invitation_response(query, context, "accept")
            elif data.startswith("reject_inv_"):
                await self.handle_invitation_response(query, context, "reject")
            elif data.startswith("buy_"):
                await self.handle_marketplace_purchase(query, context)
            elif data.startswith("sell_cat_"):
                await self.handle_sell_category(query, context)
            elif data.startswith("remove_"):
                await self.handle_remove_listing(query, context)
            elif data.startswith("admin_give_cat_"):
                await self.show_admin_give_category(query, context)
            elif data.startswith("admin_give_all_"):
                await self.handle_admin_give_item(query, context)
            elif data.startswith("admin_"):
                await self.admin.handle_admin_action(query, context)
            else:
                await query.edit_message_text("❌ دستور نامعتبر است!")

        except Exception as e:
            logger.error(f"Error handling callback {data}: {e}")
            await query.edit_message_text("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")

    async def handle_country_selection(self, query, context):
        """Handle country selection"""
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        country_code = query.data.replace("select_country_", "")

        # Check if country is already taken
        if self.db.is_country_taken(country_code):
            await query.edit_message_text("❌ این کشور قبلاً انتخاب شده است. لطفاً کشور دیگری انتخاب کنید.")
            return

        # Create new player
        success = self.db.create_player(user_id, username, country_code)
        if success:
            country_name = Config.COUNTRIES[country_code]
            await query.edit_message_text(
                f"🎉 تبریک! شما با موفقیت کشور {country_name} را انتخاب کردید.\n\n"
                f"جمعیت اولیه: 1,000,000 نفر\n"
                f"پول اولیه: 100,000 دلار\n\n"
                f"حالا می‌توانید شروع به ساختن اقتصاد خود کنید!"
            )

            # Send news to channel
            await self.news.send_player_joined(country_name, username)

            # Show main menu
            await asyncio.sleep(2)
            await self.show_main_menu_callback(query, context)
        else:
            await query.edit_message_text("❌ خطایی در ایجاد کشور رخ داد. لطفاً دوباره تلاش کنید.")

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu after /start"""
        user_id = update.effective_user.id
        player = self.db.get_player(user_id)

        if not player:
            await update.message.reply_text("❌ ابتدا باید کشور خود را انتخاب کنید. /start")
            return

        stats = self.game_logic.get_player_stats(user_id)
        if not stats:
            await update.message.reply_text("❌ خطا در دریافت اطلاعات بازیکن")
            return

        menu_text = f"""🏛 {stats['country_name']} - پنل مدیریت

👥 جمعیت: {stats['population']:,}
💰 پول: ${stats['money']:,}
⚔️سربازان: {stats['soldiers']:,}

📊 منابع:
🔩 آهن: {stats['resources'].get('iron', 0):,}
🥉 مس: {stats['resources'].get('copper', 0):,}
🛢 نفت: {stats['resources'].get('oil', 0):,}
🔗 آلومینیوم: {stats['resources'].get('aluminum', 0):,}
🏆 طلا: {stats['resources'].get('gold', 0):,}
☢️ اورانیوم: {stats['resources'].get('uranium', 0):,}
🔋 لیتیوم: {stats['resources'].get('lithium', 0):,}
⚫ زغال‌سنگ: {stats['resources'].get('coal', 0):,}
💥 نیتر: {stats['resources'].get('nitro', 0):,}
🌫 گوگرد: {stats['resources'].get('sulfur', 0):,}
🛡 تیتانیوم: {stats['resources'].get('titanium', 0):,}

انتخاب کنید:"""

        is_admin = self.admin.is_admin(update.effective_user.id)
        keyboard = self.keyboards.main_menu_keyboard(is_admin)
        await update.message.reply_text(menu_text, reply_markup=keyboard)

    async def show_main_menu_callback(self, query, context):
        """Show main menu from callback"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        if not player:
            await query.edit_message_text("❌ ابتدا باید کشور خود را انتخاب کنید. /start")
            return

        stats = self.game_logic.get_player_stats(user_id)
        if not stats:
            await query.edit_message_text("❌ خطا در دریافت اطلاعات بازیکن")
            return

        menu_text = f"""🏛 {stats['country_name']} - پنل مدیریت

👥 جمعیت: {stats['population']:,}
💰 پول: ${stats['money']:,}
⚔️سربازان: {stats['soldiers']:,}

📊 منابع:
🔩 آهن: {stats['resources'].get('iron', 0):,}
🥉 مس: {stats['resources'].get('copper', 0):,}
🛢 نفت: {stats['resources'].get('oil', 0):,}
🔗 آلومینیوم: {stats['resources'].get('aluminum', 0):,}
🏆 طلا: {stats['resources'].get('gold', 0):,}
☢️ اورانیوم: {stats['resources'].get('uranium', 0):,}
🔋 لیتیوم: {stats['resources'].get('lithium', 0):,}
⚫ زغال‌سنگ: {stats['resources'].get('coal', 0):,}
💥 نیتر: {stats['resources'].get('nitro', 0):,}
🌫 گوگرد: {stats['resources'].get('sulfur', 0):,}
🛡 تیتانیوم: {stats['resources'].get('titanium', 0):,}

انتخاب کنید:"""

        is_admin = self.admin.is_admin(user_id)
        keyboard = self.keyboards.main_menu_keyboard(is_admin)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_economy_menu(self, query, context):
        """Show economy management menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        buildings = self.db.get_player_buildings(user_id)
        income = self.economy.calculate_income(user_id)

        menu_text = f"""📈 مدیریت اقتصاد - {player['country_name']}

💰 درآمد هر 6 ساعت: ${income:,}

🏗 ساختمان‌های موجود:
⛏ معادن آهن: {buildings.get('iron_mine', 0)}
⛏ معادن مس: {buildings.get('copper_mine', 0)}
🛢 معادن نفت: {buildings.get('oil_mine', 0)}
⛽ معادن گاز: {buildings.get('gas_mine', 0)}
🔗 معادن آلومینیوم: {buildings.get('aluminum_mine', 0)}
🏆 معادن طلا: {buildings.get('gold_mine', 0)}
☢️ معادن اورانیوم: {buildings.get('uranium_mine', 0)}
🔋 معادن لیتیوم: {buildings.get('lithium_mine', 0)}
⚫ معادن زغال: {buildings.get('coal_mine', 0)}
🥈 معادن نقره: {buildings.get('silver_mine', 0)}

🏭 کارخانه اسلحه: {buildings.get('weapon_factory', 0)}
🏭 پالایشگاه: {buildings.get('refinery', 0)}
⚡ نیروگاه: {buildings.get('power_plant', 0)}
🌾 مزرعه گندم: {buildings.get('wheat_farm', 0)}
🪖 پادگان: {buildings.get('military_base', 0)}
🏘 مسکن: {buildings.get('housing', 0)}"""

        keyboard = self.keyboards.economy_menu_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_buildings_menu(self, query, context):
        """Show building construction menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        menu_text = f"""🏗 ساخت و ساز - {player['country_name']}

💰 پول شما: ${player['money']:,}

انتخاب کنید:

⛏ معادن (تولید در ساعت):
• معدن آهن - $8,000 (53 واحد/ساعت)
• معدن مس - $10,000 (67 واحد/ساعت)
• معدن نفت - $12,000 (80 واحد/ساعت)
• معدن گاز - $11,000 (73 واحد/ساعت)
• معدن آلومینیوم - $9,000 (60 واحد/ساعت)
• معدن طلا - $15,000 (100 واحد/ساعت)
• معدن اورانیوم - $20,000 (133 واحد/ساعت)
• معدن لیتیوم - $18,000 (120 واحد/ساعت)
• معدن زغال‌سنگ - $8,500 (57 واحد/ساعت)
• معدن نقره - $14,000 (93 واحد/ساعت)

🏭 ساختمان‌های تولیدی:
• کارخانه اسلحه - $15,000 (امکان تولید سلاح)
• پالایشگاه نفت - $10,000 (پردازش نفت)
• نیروگاه برق - $9,000 (تامین برق)
• مزرعه گندم - $5,000 (+10,000 جمعیت)
• پادگان آموزشی - $5,000 (+5,000 سرباز)
• مسکن - $5,000 (ظرفیت: 10,000 نفر)"""

        keyboard = self.keyboards.buildings_menu_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_building_construction(self, query, context):
        """Handle building construction"""
        user_id = query.from_user.id
        building_type = query.data.replace("build_", "")

        result = self.game_logic.build_structure(user_id, building_type)

        if result['success']:
            await query.edit_message_text(
                f"✅ {result['message']}\n\n"
                f"💰 پول باقی‌مانده: ${result['remaining_money']:,}"
            )

            # Send news to channel
            player = self.db.get_player(user_id)
            await self.news.send_building_constructed(player['country_name'], result['building_name'])
        else:
            await query.edit_message_text(f"❌ {result['message']}")

    async def show_military_menu(self, query, context):
        """Show military management menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)

        menu_text = f"""⚔️ مدیریت نظامی - {player['country_name']}

👥 جمعیت: {player['population']:,}
⚔️سربازان: {player['soldiers']:,}

🔫 تسلیحات موجود:
🔫 تفنگ: {weapons.get('rifle', 0)}
🚗 تانک: {weapons.get('tank', 0)}
✈️ جنگنده: {weapons.get('fighter_jet', 0)}
🚁 پهپاد: {weapons.get('drone', 0)}
🚀 موشک بالستیک: {weapons.get('missile', 0)}
🚢 کشتی جنگی: {weapons.get('warship', 0)}
🛡 پدافند هوایی: {weapons.get('air_defense', 0)}
🚀 سپر موشکی: {weapons.get('missile_shield', 0)}
💻 سپر سایبری: {weapons.get('cyber_shield', 0)}

انتخاب کنید:"""

        keyboard = self.keyboards.military_menu_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_weapons_menu(self, query, context):
        """Show weapon production categories menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        resources = self.db.get_player_resources(user_id)

        menu_text = f"""🔫 تولید تسلیحات - {player['country_name']}

💰 پول: ${player['money']:,}

📊 منابع موجود:
🔩 آهن: {resources['iron']:,}
🥉 مس: {resources['copper']:,}
🛢 نفت: {resources['oil']:,}
🔗 آلومینیوم: {resources['aluminum']:,}
🏆 طلا: {resources['gold']:,}
☢️ اورانیوم: {resources['uranium']:,}
🔋 لیتیوم: {resources['lithium']:,}
⚫ زغال‌سنگ: {resources['coal']:,}
💥 نیتر: {resources['nitro']:,}
🌫 گوگرد: {resources['sulfur']:,}
🛡 تیتانیوم: {resources['titanium']:,}

💡 برای تولید تسلیحات به کارخانه اسلحه نیاز دارید!

🎯 دسته‌بندی سلاح‌ها:
• سلاح‌های پایه: تفنگ، تانک، جنگنده، پهپاد
• بمب‌ها: بمب ساده، بمب هسته‌ای
• موشک‌ها: موشک ساده، بالستیک، هسته‌ای
• موشک‌های مخصوص: Trident، Satan2، DF-41، Tomahawk
• جت‌های پیشرفته: F-22، F-35، Su-57، J-20"""

        keyboard = self.keyboards.weapons_menu_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_weapon_category(self, query, context):
        """Show weapons in specific category"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        resources = self.db.get_player_resources(user_id)

        category = query.data.replace("weapon_cat_", "")

        category_names = {
            'basic': 'سلاح‌های پایه',
            'defense': 'سیستم‌های دفاعی',
            'bombs': 'بمب‌ها',
            'missiles': 'موشک‌های ساده',
            'special_missiles': 'موشک‌های مخصوص',
            'advanced_jets': 'جت‌های پیشرفته',
            'naval': 'تسلیحات دریایی'
        }

        category_name = category_names.get(category, category)
        weapons_in_category = [
            weapon for weapon, config in Config.WEAPONS.items()
            if config.get('category') == category
        ]

        menu_text = f"""🔫 {category_name}

💰 پول شما: ${player['money']:,}

🔧 برای تولید به کارخانه اسلحه نیاز دارید!

🎯 سلاح‌های موجود:"""

        # Resource name mapping
        resource_names = {
            'iron': '🔩 آهن',
            'copper': '🥉 مس', 
            'aluminum': '🔗 آلومینیوم',
            'titanium': '🛡 تیتانیوم',
            'uranium': '☢️ اورانیوم',
            'lithium': '🔋 لیتیوم',
            'coal': '⚫ زغال‌سنگ',
            'nitro': '💥 نیتر',
            'sulfur': '🌫 گوگرد',
            'gold': '🏆 طلا'
        }

        for weapon in weapons_in_category[:6]:  # نمایش حداکثر 6 سلاح برای فضای بیشتر
            config = Config.WEAPONS[weapon]
            materials_text = ""

            # Show required materials
            if 'resources' in config:
                materials = []
                for resource, amount in config['resources'].items():
                    if resource in resource_names:
                        materials.append(f"{resource_names[resource]}: {amount:,}")
                    elif resource in Config.WEAPONS:
                        # If it's another weapon requirement
                        weapon_name = Config.WEAPONS[resource]['name']
                        materials.append(f"🔫 {weapon_name}: {amount}")

                if materials:
                    materials_text = f"\n   📋 مواد: {' | '.join(materials)}"

            menu_text += f"\n• {config['name']}: ${config['cost']:,}{materials_text}"

        keyboard = self.keyboards.weapon_category_keyboard(category)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_weapon_production(self, query, context):
        """Handle weapon production"""
        user_id = query.from_user.id
        callback_data = query.data
        
        # Handle different callback formats
        if callback_data.startswith("produce_"):
            weapon_type = callback_data.replace("produce_", "")
        elif callback_data.startswith("select_weapon_"):
            weapon_type = callback_data.replace("select_weapon_", "")
        else:
            await query.edit_message_text("❌ داده نامعتبر!")
            return

        result = self.game_logic.produce_weapon(user_id, weapon_type)

        if result['success']:
            await query.edit_message_text(
                f"✅ {result['message']}\n\n"
                f"💰 پول باقی‌مانده: ${result['remaining_money']:,}"
            )

            # Send news to channel
            player = self.db.get_player(user_id)
            await self.news.send_weapon_produced(player['country_name'], result['weapon_name'])
        else:
            await query.edit_message_text(f"❌ {result['message']}")

    async def show_weapon_quantity_selection(self, query, context):
        """Show quantity selection for weapon production"""
        user_id = query.from_user.id
        weapon_type = query.data.replace("select_weapon_", "")
        
        player = self.db.get_player(user_id)
        weapon_config = Config.WEAPONS.get(weapon_type)
        
        if not weapon_config:
            await query.edit_message_text("❌ نوع سلاح نامعتبر است!")
            return
            
        weapon_name = weapon_config['name']
        weapon_cost = weapon_config['cost']
        
        menu_text = f"""🔫 انتخاب تعداد - {weapon_name}
        
💰 پول شما: ${player['money']:,}
💲 قیمت هر واحد: ${weapon_cost:,}

چند عدد می‌خواهید تولید کنید؟"""

        keyboard = self.keyboards.quantity_selection_keyboard("weapon", weapon_type)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_building_quantity_selection(self, query, context):
        """Show quantity selection for building construction"""
        user_id = query.from_user.id
        building_type = query.data.replace("select_building_", "")
        
        player = self.db.get_player(user_id)
        building_config = Config.BUILDINGS.get(building_type)
        
        if not building_config:
            await query.edit_message_text("❌ نوع ساختمان نامعتبر است!")
            return
            
        building_name = building_config['name']
        building_cost = building_config['cost']
        
        menu_text = f"""🏗 انتخاب تعداد - {building_name}
        
💰 پول شما: ${player['money']:,}
💲 قیمت هر واحد: ${building_cost:,}

چند عدد می‌خواهید بسازید؟"""

        keyboard = self.keyboards.quantity_selection_keyboard("building", building_type)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_quantity_selection(self, query, context):
        """Handle quantity selection for production/construction"""
        user_id = query.from_user.id
        data_parts = query.data.split("_")
        
        if len(data_parts) < 4:
            await query.edit_message_text("❌ داده نامعتبر!")
            return
            
        # Format: quantity_type_item_amount (may have underscores in item name)
        item_type = data_parts[1]  # weapon or building
        quantity = int(data_parts[-1])  # amount (last part)
        item_name = "_".join(data_parts[2:-1])  # everything between type and amount
        
        if item_type == "weapon":
            result = self.game_logic.produce_weapon(user_id, item_name, quantity)
            
            if result['success']:
                await query.edit_message_text(
                    f"✅ {result['message']}\n\n"
                    f"💰 پول باقی‌مانده: ${result['remaining_money']:,}"
                )
                
                # Send news to channel
                player = self.db.get_player(user_id)
                await self.news.send_weapon_produced(player['country_name'], result['weapon_name'], quantity)
            else:
                await query.edit_message_text(f"❌ {result['message']}")
                
        elif item_type == "building":
            result = self.game_logic.build_structure(user_id, item_name, quantity)
            
            if result['success']:
                await query.edit_message_text(
                    f"✅ {result['message']}\n\n"
                    f"💰 پول باقی‌مانده: ${result['remaining_money']:,}"
                )
                
                # Send news to channel
                player = self.db.get_player(user_id)
                await self.news.send_building_constructed(player['country_name'], result['building_name'], quantity)
            else:
                await query.edit_message_text(f"❌ {result['message']}")

    async def show_diplomacy_menu(self, query, context):
        """Show diplomacy menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        all_countries = self.db.get_all_countries()
        menu_text = f"""🤝 دیپلماسی - {player['country_name']}

🌍 کشورهای موجود:
"""

        for country in all_countries:
            if country['user_id'] != user_id:
                menu_text += f"🏴 {country['country_name']} - {country['username']}\n"

        menu_text += "\n💡 قابلیت‌های دیپلماسی:"
        menu_text += "\n• ارسال منابع امن"
        menu_text += "\n• دزدی محموله‌های درحال انتقال"
        menu_text += "\n• بیانیه رسمی"
        menu_text += "\n• پیشنهاد صلح"

        menu_text += "\nانتخاب کنید:"

        keyboard = self.keyboards.diplomacy_menu_keyboard(user_id)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_attack_targets(self, query, context):
        """Show available attack targets"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        available_targets = self.combat.get_available_targets(user_id)

        if not available_targets:
            await query.edit_message_text(
                "⚔️ هیچ کشور قابل حمله‌ای یافت نشد!\n\n"
                "💡 برای حمله به کشورهای دور، به تسلیحات دوربرد نیاز دارید."
            )
            return

        menu_text = f"⚔️ انتخاب هدف حمله - {player['country_name']}\n\n"
        menu_text += "کشورهای قابل حمله:\n"

        for target in available_targets:
            flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')
            menu_text += f"{flag} {target['country_name']}\n"

        menu_text += "\nانتخاب کنید:"

        keyboard = self.keyboards.attack_targets_keyboard(available_targets)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_attack_type_selection(self, query, context):
        """Show attack type selection menu"""
        user_id = query.from_user.id
        target_id = int(query.data.replace("select_target_", ""))
        
        target = self.db.get_player(target_id)
        if not target:
            await query.edit_message_text("❌ کشور هدف یافت نشد!")
            return
            
        menu_text = f"⚔️ نوع حمله به {target['country_name']}\n\nنوع حمله را انتخاب کنید:"
        
        keyboard = self.keyboards.attack_type_selection_keyboard(target_id)
        await query.edit_message_text(menu_text, reply_markup=keyboard)
    
    async def show_weapon_selection_for_attack(self, query, context):
        """Show weapon selection for attack"""
        user_id = query.from_user.id
        data_parts = query.data.split("_")
        target_id = int(data_parts[2])
        attack_type = data_parts[3]
        
        available_weapons = self.db.get_player_weapons(user_id)
        
        menu_text = f"⚔️ انتخاب تسلیحات برای حمله {attack_type}\n\nتسلیحات خود را انتخاب کنید:"
        
        keyboard = self.keyboards.weapon_selection_keyboard(target_id, attack_type, available_weapons)
        await query.edit_message_text(menu_text, reply_markup=keyboard)
    
    async def handle_attack_execution(self, query, context):
        """Handle actual attack execution"""
        user_id = query.from_user.id
        data_parts = query.data.split("_")
        target_id = int(data_parts[2])
        attack_type = data_parts[3]

        attacker = self.db.get_player(user_id)
        target = self.db.get_player(target_id)

        if not target:
            await query.edit_message_text("❌ کشور هدف یافت نشد!")
            return

        # Execute attack
        result = self.combat.schedule_delayed_attack(user_id, target_id, attack_type)

        if not result['success']:
            await query.edit_message_text(f"❌ {result['message']}")
            return

        await query.edit_message_text(f"✅ {result['message']}")

        # Send news to channel about attack preparation
        attacker_flag = Config.COUNTRY_FLAGS.get(attacker['country_code'], '🏳')
        target_flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')
        
        attack_news = f"""⚔️ آماده‌سازی حمله!

🔥 {attacker_flag} <b>{attacker['country_name']}</b> 
🎯 {target_flag} <b>{target['country_name']}</b>

⏱ زمان رسیدن: {result['travel_time']} دقیقه
🔥 نوع حمله: {attack_type}

💀 جنگ در راه است..."""

        await self.news.send_text_message(attack_news)

    async def show_resources_menu(self, query, context):
        """Show resources overview menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        resources = self.db.get_player_resources(user_id)

        total_value = 0
        for resource, amount in resources.items():
            if resource != 'user_id' and isinstance(amount, int):
                total_value += amount * 10

        menu_text = f"""📊 منابع - {player['country_name']}

🔩 آهن: {resources.get('iron', 0):,}
🥉 مس: {resources.get('copper', 0):,}
🛢 نفت خام: {resources.get('oil', 0):,}
⛽ گاز: {resources.get('gas', 0):,}
🔗 آلومینیوم: {resources.get('aluminum', 0):,}
🏆 طلا: {resources.get('gold', 0):,}
☢️ اورانیوم: {resources.get('uranium', 0):,}
🔋 لیتیوم: {resources.get('lithium', 0):,}
⚫ زغال‌سنگ: {resources.get('coal', 0):,}
🥈 نقره: {resources.get('silver', 0):,}
⛽ سوخت: {resources.get('fuel', 0):,}

📊 ارزش کل منابع: ${total_value:,}"""

        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_send_resources_menu(self, query, context):
        """Show resource transfer menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        resources = self.db.get_player_resources(user_id)
        weapons = self.db.get_player_weapons(user_id)

        all_countries = self.db.get_all_countries()
        other_countries = [c for c in all_countries if c['user_id'] != user_id]

        if not other_countries:
            await query.edit_message_text("❌ هیچ کشور دیگری برای ارسال منابع یافت نشد!")
            return

        # Calculate estimated travel time based on transport equipment
        travel_time = self.convoy.calculate_convoy_travel_time(user_id)

        menu_text = f"""🚚 انتقال منابع - {player['country_name']}

💰 پول شما: ${player['money']:,}
⏱ زمان انتقال تخمینی: {travel_time} دقیقه

📊 منابع موجود:
🔩 آهن: {resources.get('iron', 0):,}
🥉 مس: {resources.get('copper', 0):,}
🛢 نفت: {resources.get('oil', 0):,}
⛽ گاز: {resources.get('gas', 0):,}
🔗 آلومینیوم: {resources.get('aluminum', 0):,}
🏆 طلا: {resources.get('gold', 0):,}
☢️ اورانیوم: {resources.get('uranium', 0):,}
🔋 لیتیوم: {resources.get('lithium', 0):,}

🚛 تجهیزات حمل‌ونقل:
🚚 کامیون زرهی: {weapons.get('armored_truck', 0)}
🚁 هلیکوپتر باری: {weapons.get('cargo_helicopter', 0)}
✈️ هواپیمای باری: {weapons.get('cargo_plane', 0)}
🚢 کشتی تدارکات: {weapons.get('supply_ship', 0)}

💡 محموله در طول مسیر قابل رهگیری است!

کشور مقصد را انتخاب کنید:"""

        keyboard = self.keyboards.send_resources_targets_keyboard(other_countries)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_official_statement(self, query, context):
        """Handle official statement"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        await query.edit_message_text(
            f"📢 بیانیه رسمی - {player['country_name']}\n\n"
            "لطفاً متن بیانیه خود را ارسال کنید (حداکثر 300 کاراکتر):"
        )

        # Store state for message handler
        context.user_data['awaiting_statement'] = True

    async def show_income_report(self, query, context):
        """Show detailed income report"""
        user_id = query.from_user.id
        report = self.economy.get_income_report(user_id)

        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(report, reply_markup=keyboard)

    async def show_defense_status(self, query, context):
        """Show defense status"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)

        defense_text = f"""🛡 وضعیت دفاعی - {player['country_name']}

🛡 تسلیحات دفاعی:
🛡 پدافند هوایی: {weapons.get('air_defense', 0)}
🚀 سپر موشکی: {weapons.get('missile_shield', 0)}
💻 سپر سایبری: {weapons.get('cyber_shield', 0)}

⚔️سربازان دفاعی: {player['soldiers']:,}

💡 برای بهبود دفاع، تسلیحات دفاعی بیشتری تولید کنید."""

        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(defense_text, reply_markup=keyboard)

    async def show_military_power(self, query, context):
        """Show military power calculation"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)

        total_power = 0
        power_breakdown = f"""📊 قدرت نظامی - {player['country_name']}

⚔️سربازان: {player['soldiers']:,} × 1 = {player['soldiers']:,}
"""
        total_power += player['soldiers']

        for weapon_type, count in weapons.items():
            if weapon_type != 'user_id' and count > 0:
                weapon_config = Config.WEAPONS.get(weapon_type, {})
                weapon_power = weapon_config.get('power', 0)
                weapon_name = weapon_config.get('name', weapon_type)
                weapon_total = count * weapon_power
                power_breakdown += f"{weapon_name}: {count} × {weapon_power} = {weapon_total:,}\n"
                total_power += weapon_total

        power_breakdown += f"\n🔥 قدرت کل: {total_power:,}"

        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(power_breakdown, reply_markup=keyboard)

    async def handle_resource_transfer_target(self, query, context):
        """Handle resource transfer target selection"""
        user_id = query.from_user.id
        target_id = int(query.data.replace("send_to_", ""))

        player = self.db.get_player(user_id)
        target = self.db.get_player(target_id)
        resources = self.db.get_player_resources(user_id)

        menu_text = f"""📬 ارسال منابع به {target['country_name']}

💰 پول شما: ${player['money']:,}

منابع قابل ارسال:
"""

        # Show available resources with transfer options
        transfer_options = []
        if player['money'] >= 10000:
            transfer_options.append(('money_10k', '💰 10,000 دلار'))
        if player['money'] >= 50000:
            transfer_options.append(('money_50k', '💰 50,000 دلار'))

        for resource, amount in resources.items():
            if resource != 'user_id' and amount >= 1000:
                resource_config = Config.RESOURCES.get(resource, {})
                resource_name = resource_config.get('name', resource)
                resource_emoji = resource_config.get('emoji', '📦')
                transfer_options.append((f'{resource}_1k', f'{resource_emoji} 1,000 {resource_name}'))

        if not transfer_options:
            await query.edit_message_text("❌ منابع کافی برای ارسال ندارید!")
            return

        keyboard = self.keyboards.resource_transfer_keyboard(target_id, transfer_options)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_resource_transfer(self, query, context):
        """Handle actual resource transfer with convoy system"""
        user_id = query.from_user.id
        data_parts = query.data.replace("transfer_", "").split("_")
        target_id = int(data_parts[0])
        transfer_type = "_".join(data_parts[1:])

        player = self.db.get_player(user_id)
        target = self.db.get_player(target_id)

        transfer_resources = {}
        transfer_description = ""
        can_transfer = False

        if transfer_type == "money_10k":
            if player['money'] >= 10000:
                transfer_resources = {'money': 10000}
                transfer_description = "💰 10,000 دلار"
                can_transfer = True
        elif transfer_type == "money_50k":
            if player['money'] >= 50000:
                transfer_resources = {'money': 50000}
                transfer_description = "💰 50,000 دلار"
                can_transfer = True
        elif transfer_type.endswith("_1k"):
            resource_type = transfer_type.replace("_1k", "")
            resources = self.db.get_player_resources(user_id)
            if resources.get(resource_type, 0) >= 1000:
                transfer_resources = {resource_type: 1000}
                resource_config = Config.RESOURCES.get(resource_type, {})
                resource_name = resource_config.get('name', resource_type)
                resource_emoji = resource_config.get('emoji', '📦')
                transfer_description = f"{resource_emoji} 1,000 {resource_name}"
                can_transfer = True

        if can_transfer:
            # Deduct resources from sender
            if 'money' in transfer_resources:
                self.db.update_player_money(user_id, player['money'] - transfer_resources['money'])
            else:
                self.db.consume_resources(user_id, transfer_resources)

            # Create convoy
            convoy_result = self.convoy.create_convoy(user_id, target_id, transfer_resources)
            
            await query.edit_message_text(
                f"🚚 محموله آماده شد!\n\n"
                f"📤 در حال ارسال: {transfer_description}\n"
                f"📍 مقصد: {target['country_name']}\n"
                f"⏱ زمان رسیدن: {convoy_result['travel_time']} دقیقه\n"
                f"🛡 سطح امنیت: {convoy_result['security_level']}%\n\n"
                f"💡 محموله در طول مسیر قابل رهگیری است!"
            )

            # Send convoy news to channel with action buttons
            sender_flag = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳')
            receiver_flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')
            
            convoy_message = f"""📤 {sender_flag} <b>{player['country_name']}</b> 
📥 {receiver_flag} <b>{target['country_name']}</b>

📦 محتویات: {transfer_description}
⏱ زمان رسیدن: {convoy_result['travel_time']} دقیقه
🛡 امنیت: {convoy_result['security_level']}%"""

            # Create keyboard for convoy actions
            convoy_keyboard = self.convoy.create_convoy_news_keyboard(
                convoy_result['convoy_id'], 
                convoy_result['security_level'],
                "DragonRPBot"  # Replace with your bot username
            )
            
            await self.news.send_convoy_news(convoy_message, convoy_keyboard)
        else:
            await query.edit_message_text("❌ منابع کافی برای این انتقال ندارید!")

    async def handle_convoy_action(self, query, context):
        """Handle convoy interception actions - show confirmation"""
        user_id = query.from_user.id
        action_data = query.data.replace("convoy_", "")

        if action_data.startswith("stop_"):
            convoy_id = int(action_data.replace("stop_", ""))
            action_type = "stop"
        elif action_data.startswith("steal_"):
            convoy_id = int(action_data.replace("steal_", ""))
            action_type = "steal"
        else:
            await query.edit_message_text("❌ دستور نامعتبر!")
            return

        # Get convoy details
        convoy = self.db.get_convoy(convoy_id)
        if not convoy:
            await query.edit_message_text("❌ محموله یافت نشد!")
            return

        # Check if player can intercept
        convoy_security = convoy['security_level']
        can_intercept = self.convoy.can_intercept_convoy(user_id, convoy_security)
        
        # Calculate required power
        weapons = self.db.get_player_weapons(user_id)
        intercept_power = 0
        intercept_power += weapons.get('fighter_jet', 0) * 30
        intercept_power += weapons.get('drone', 0) * 25
        intercept_power += weapons.get('simple_missile', 0) * 50
        intercept_power += weapons.get('warship', 0) * 35
        
        min_power_needed = convoy_security * 2

        if action_type == "stop":
            action_name = "توقف محموله"
            description = "محموله متوقف شده و منابع به فرستنده بازگردانده می‌شود"
        else:
            action_name = "سرقت محموله"
            description = "محتویات محموله به شما انتقال پیدا می‌کند"

        confirmation_text = f"""🎯 تایید {action_name}

🛡 امنیت محموله: {convoy_security}%
⚔️ قدرت رهگیری شما: {intercept_power:,}
📊 قدرت مورد نیاز: {min_power_needed:,}

💡 {description}

⚠️ در صورت شکست، بخشی از تجهیزاتتان از دست خواهد رفت!

آیا مطمئن هستید؟"""

        keyboard = self.keyboards.convoy_action_confirmation_keyboard(convoy_id, action_type, can_intercept)
        await query.edit_message_text(confirmation_text, reply_markup=keyboard)

    async def handle_convoy_confirmation(self, query, context):
        """Handle convoy action confirmation"""
        user_id = query.from_user.id
        action_data = query.data.replace("confirm_convoy_", "")

        if action_data.startswith("stop_"):
            convoy_id = int(action_data.replace("stop_", ""))
            result = self.convoy.attempt_convoy_interception(user_id, convoy_id, "stop")
        elif action_data.startswith("steal_"):
            convoy_id = int(action_data.replace("steal_", ""))
            result = self.convoy.attempt_convoy_interception(user_id, convoy_id, "steal")
        else:
            await query.edit_message_text("❌ دستور نامعتبر!")
            return

        await query.edit_message_text(f"{'✅' if result['success'] else '❌'} {result['message']}")

        # Send news about the action result
        await self.send_convoy_action_news(user_id, convoy_id, result)

    async def handle_convoy_action_from_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE, convoy_id: int, action_type: str):
        """Handle convoy action initiated from start command"""
        user_id = update.effective_user.id
        
        # Check if user has a country
        player = self.db.get_player(user_id)
        if not player:
            await update.message.reply_text("❌ ابتدا باید کشور خود را انتخاب کنید. /start")
            return

        # Get convoy details
        convoy = self.db.get_convoy(convoy_id)
        if not convoy:
            await update.message.reply_text("❌ محموله یافت نشد!")
            return

        # Check if convoy is still valid
        if convoy['status'] != 'in_transit':
            await update.message.reply_text("❌ محموله قبلاً تحویل داده شده یا متوقف شده!")
            return

        # Check if player can intercept (including sender/receiver check)
        convoy_security = convoy['security_level']
        can_intercept = self.convoy.can_intercept_convoy(user_id, convoy_security, convoy_id)
        
        if not can_intercept:
            # Check if it's because they're sender/receiver
            if convoy['sender_id'] == user_id or convoy['receiver_id'] == user_id:
                await update.message.reply_text("❌ شما نمی‌توانید محموله خود را رهگیری کنید!")
            else:
                await update.message.reply_text("❌ قدرت نظامی شما برای رهگیری این محموله کافی نیست!")
            return

        # Show confirmation
        action_name = "توقف محموله" if action_type == "stop" else "سرقت محموله"
        description = "محموله متوقف شده و منابع به فرستنده بازگردانده می‌شود" if action_type == "stop" else "محتویات محموله به شما انتقال پیدا می‌کند"

        # Calculate interception power for display
        weapons = self.db.get_player_weapons(user_id)
        intercept_power = (
            weapons.get('fighter_jet', 0) * 30 +
            weapons.get('drone', 0) * 25 +
            weapons.get('simple_missile', 0) * 50 +
            weapons.get('warship', 0) * 35
        )

        confirmation_text = f"""🎯 تایید {action_name}

🛡 امنیت محموله: {convoy_security}%
⚔️ قدرت رهگیری شما: {intercept_power:,}

💡 {description}

⚠️ در صورت شکست، بخشی از تجهیزاتتان از دست خواهد رفت!

آیا مطمئن هستید؟"""

        keyboard = self.keyboards.convoy_private_confirmation_keyboard(convoy_id, action_type)
        await update.message.reply_text(confirmation_text, reply_markup=keyboard)

    async def send_convoy_action_news(self, user_id: int, convoy_id: int, result: dict):
        """Send news about convoy action result"""
        try:
            player = self.db.get_player(user_id)
            convoy = self.db.get_convoy(convoy_id)
            
            if not player or not convoy:
                return

            sender = self.db.get_player(convoy['sender_id'])
            receiver = self.db.get_player(convoy['receiver_id'])
            
            if not sender or not receiver:
                return

            country_flag = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳')
            sender_flag = Config.COUNTRY_FLAGS.get(sender['country_code'], '🏳')
            receiver_flag = Config.COUNTRY_FLAGS.get(receiver['country_code'], '🏳')
            
            if result['success']:
                if result['action'] == 'stopped':
                    news_text = f"""🛑 توقف محموله!

{country_flag} <b>{player['country_name']}</b> محموله {sender_flag} {sender['country_name']} → {receiver_flag} {receiver['country_name']} را متوقف کرد!

✅ محموله با موفقیت متوقف شد
🔄 منابع به فرستنده بازگردانده شد"""
                else:  # stolen
                    news_text = f"""💰 دزدی محموله!

{country_flag} <b>{player['country_name']}</b> محموله {sender_flag} {sender['country_name']} → {receiver_flag} {receiver['country_name']} را دزدید!

💎 محتویات محموله به دزد انتقال یافت"""
            else:
                news_text = f"""⚔️ تلاش ناموفق برای رهگیری!

{country_flag} <b>{player['country_name']}</b> سعی کرد محموله {sender_flag} {sender['country_name']} → {receiver_flag} {receiver['country_name']} را رهگیری کند!

❌ تلاش شکست خورد
💥 بخشی از تجهیزات مهاجم از دست رفت"""

            await self.news.send_text_message(news_text)
            
        except Exception as e:
            logger.error(f"Error sending convoy action news: {e}")

    async def show_alliance_menu(self, query, context):
        """Show alliance menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        alliance = self.alliance.get_player_alliance(user_id)

        if alliance:
            menu_text = f"""🤝 اتحاد - {player['country_name']}

🏛 اتحاد: {alliance['alliance_name']}
👑 نقش: {alliance['role']}

انتخاب کنید:"""
        else:
            menu_text = f"""🤝 اتحادها - {player['country_name']}

شما عضو هیچ اتحادی نیستید.

انتخاب کنید:"""

        keyboard = self.keyboards.alliance_menu_keyboard(alliance is not None)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_alliance_action(self, query, context):
        """Handle alliance actions"""
        user_id = query.from_user.id
        action = query.data.replace("alliance_", "")

        if action == "create":
            await query.edit_message_text("نام اتحاد جدید را ارسال کنید:")
            context.user_data['awaiting_alliance_name'] = True
        elif action == "invite":
            await self.show_alliance_invite_menu(query, context)
        elif action == "members":
            await self.show_alliance_members(query, context)
        elif action == "invitations":
            await self.show_alliance_invitations(query, context)
        elif action == "leave":
            result = self.alliance.leave_alliance(user_id)
            await query.edit_message_text(f"{'✅' if result['success'] else '❌'} {result['message']}")
        else:
            await query.edit_message_text("❌ دستور نامعتبر!")

    async def show_marketplace_menu(self, query, context):
        """Show marketplace menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        menu_text = f"""🛒 فروشگاه - {player['country_name']}

💰 پول شما: ${player['money']:,}

در فروشگاه می‌توانید:
• کالاهای دیگران را خریداری کنید
• اقلام خود را برای فروش عرضه کنید
• امنیت بالاتر = احتمال تحویل بیشتر

انتخاب کنید:"""

        keyboard = self.keyboards.marketplace_menu_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_marketplace_action(self, query, context):
        """Handle marketplace actions"""
        user_id = query.from_user.id
        action = query.data.replace("market_", "")

        if action == "browse":
            await self.show_market_categories(query, context)
        elif action == "sell":
            await self.show_sell_categories(query, context)
        elif action == "my_listings":
            await self.show_my_listings(query, context)
        elif action.startswith("cat_"):
            category = action.replace("cat_", "")
            await self.show_market_listings(query, context, category)
        else:
            await query.edit_message_text("❌ دستور نامعتبر!")

    async def show_market_categories(self, query, context):
        """Show market categories for browsing"""
        menu_text = """🛒 دسته‌بندی کالاها

کدام دسته را می‌خواهید مرور کنید؟"""

        keyboard = self.keyboards.market_categories_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def show_market_listings(self, query, context, category):
        """Show market listings for specific category"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        listings = self.marketplace.get_listings_by_category(category)

        if not listings:
            await query.edit_message_text(
                f"""🛒 فروشگاه - {category}

❌ هیچ کالایی در این دسته یافت نشد!

💡 بعداً دوباره بررسی کنید."""
            )
            return

        menu_text = f"""🛒 فروشگاه - {category}

💰 پول شما: ${player['money']:,}

📦کالاهای موجود:"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []

        for listing in listings[:10]:  # Show first 10 listings
            try:
                seller_country = listing.get('seller_country', 'نامشخص')
                item_type = listing.get('item_type', 'unknown')
                item_category = listing.get('item_category', 'unknown')
                quantity = listing.get('quantity', 0)
                price_per_unit = listing.get('price_per_unit', 0)
                total_price = listing.get('total_price', 0)
                security_level = listing.get('security_level', 50)
                listing_id = listing.get('id', 0)
                
                item_emoji = '📦'
                if item_category == 'weapon':
                    item_emoji = {
                        'rifle': '🔫', 'tank': '🚗', 'fighter_jet': '✈️',
                        'drone': '🚁', 'missile': '🚀', 'warship': '🚢',
                        'air_defense': '🛡', 'missile_shield': '🚀', 'cyber_shield': '💻'
                    }.get(item_type, '⚔️')
                elif item_category == 'resource':
                    from config import Config
                    resource_config = Config.RESOURCES.get(item_type, {})
                    item_emoji = resource_config.get('emoji', '📦')

                menu_text += f"""
{item_emoji} {item_type} x{quantity:,}
💰 ${price_per_unit:,} واحد (کل: ${total_price:,})
🏴 فروشنده: {seller_country}
🛡 امنیت: {security_level}%"""

                # Create safe button text and callback data
                button_text = f"{item_emoji} خرید {item_type} - ${total_price:,}"
                if len(button_text) > 64:  # Telegram button text limit
                    button_text = f"{item_emoji} خرید - ${total_price:,}"
                
                callback_data = f"buy_{listing_id}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
                
            except Exception as e:
                logger.error(f"Error processing listing {listing}: {e}")
                continue

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="market_browse")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(menu_text, reply_markup=reply_markup)

    async def show_sell_categories(self, query, context):
        """Show selling categories"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        menu_text = f"""💰 فروش کالا - {player['country_name']}

💰 پول شما: ${player['money']:,}

کدام نوع کالا را می‌خواهید بفروشید؟"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("⚔️ تسلیحات", callback_data="sell_cat_weapons"),
                InlineKeyboardButton("📊 منابع", callback_data="sell_cat_resources")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="marketplace")
            ]
        ]

        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_my_listings(self, query, context):
        """Show player's marketplace listings"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        listings = self.marketplace.get_player_listings(user_id)

        if not listings:
            await query.edit_message_text(
                f"""📋 آگهی‌های من - {player['country_name']}

❌ شما هیچ آگهی فروشی ندارید!

💡 از بخش "فروش کالا" آگهی جدید ثبت کنید."""
            )
            return

        menu_text = f"""📋 آگهی‌های من - {player['country_name']}

💰 پول شما: ${player['money']:,}

📦 آگهی‌های شما:"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []

        for listing in listings:
            status_emoji = {
                'active': '🟢', 'sold_out': '🔴', 'cancelled': '⚫'
            }.get(listing['status'], '🔘')

            item_emoji = '📦'
            if listing['item_category'] == 'weapon':
                item_emoji = {
                    'rifle': '🔫', 'tank': '🚗', 'fighter_jet': '✈️',
                    'drone': '🚁', 'missile': '🚀', 'warship': '🚢'
                }.get(listing['item_type'], '⚔️')
            elif listing['item_category'] == 'resource':
                from config import Config
                resource_config = Config.RESOURCES.get(listing['item_type'], {})
                item_emoji = resource_config.get('emoji', '📦')

            menu_text += f"""
{status_emoji} {item_emoji} {listing['item_type']} x{listing['quantity']:,}
💰 ${listing['price_per_unit']:,}/unit (Total: ${listing['total_price']:,})
🛡 Security: {listing['security_level']}%
📅 {listing['created_at'][:10]}"""

            if listing['status'] == 'active':
                keyboard.append([InlineKeyboardButton(f"❌ Cancel {listing['item_type']}", callback_data=f"remove_{listing['id']}")])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="marketplace")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(menu_text, reply_markup=reply_markup)

    async def show_convoy_interception_menu(self, query, context):
        """Show convoy interception menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        # Get active convoys
        active_convoys = self.convoy.get_active_convoys()
        
        if not active_convoys:
            await query.edit_message_text(
                f"""🏴‍☠️ دزدی محموله - {player['country_name']}

❌ هیچ محموله‌ای درحال انتقال نیست!

💡 محموله‌ها هنگام ارسال منابع بین کشورها ایجاد می‌شوند.
شما می‌توانید آنها را متوقف کرده یا محتویاتشان را بدزدید.

🔙 برای بازگشت دکمه زیر را فشار دهید.""",
                reply_markup=self.keyboards.back_to_diplomacy_keyboard()
            )
            return

        menu_text = f"""🏴‍☠️ دزدی محموله - {player['country_name']}

🚛 محموله‌های فعال:

"""

        keyboard = []
        for convoy in active_convoys[:10]:  # نمایش حداکثر 10 محموله
            try:
                sender_country = convoy.get('sender_country', 'نامعتبر')
                receiver_country = convoy.get('receiver_country', 'نامعتبر')
                resource_type = convoy.get('resource_type', 'نامعتبر')
                amount = convoy.get('amount', 0)
                security_level = convoy.get('security_level', 0)
                
                menu_text += f"""
🚛 {sender_country} → {receiver_country}
📦 {resource_type}: {amount:,}
🛡 امنیت: {security_level}%
"""

                convoy_id = convoy.get('id', 0)
                keyboard.extend([
                    [
                        InlineKeyboardButton(f"⛔ توقف محموله", callback_data=f"convoy_stop_{convoy_id}"),
                        InlineKeyboardButton(f"🏴‍☠️ دزدی محموله", callback_data=f"convoy_steal_{convoy_id}")
                    ]
                ])
                
            except Exception as e:
                logger.error(f"Error processing convoy {convoy}: {e}")
                continue

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="diplomacy")])
        
        from telegram import InlineKeyboardMarkup
        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def propose_peace(self, query, context):
        """Show propose peace menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        peace_text = f"""🕊 پیشنهاد صلح - {player['country_name']}

این بخش به زودی فعال می‌شود...

💡 قابلیت‌های آینده:
• ارسال پیشنهاد صلح به کشورهای دیگر
• مذاکرات دیپلماتیک
• قراردادهای تجاری
• اتحادهای نظامی"""

        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(peace_text, reply_markup=keyboard)

    async def show_alliance_invite_menu(self, query, context):
        """Show alliance invite menu"""
        user_id = query.from_user.id
        all_countries = self.db.get_all_countries()
        other_countries = [c for c in all_countries if c['user_id'] != user_id]

        if not other_countries:
            await query.edit_message_text("❌ هیچ بازیکن دیگری برای دعوت یافت نشد!")
            return

        menu_text = "👥 دعوت به اتحاد\n\nکدام بازیکن را می‌خواهید دعوت کنید؟\n\n"

        for country in other_countries[:10]:  # محدود به 10 کشور
            menu_text += f"🏴 {country['country_name']} - {country['username']}\n"

        keyboard = []
        for country in other_countries[:10]:
            keyboard.append([InlineKeyboardButton(
                f"{country['country_name']}", 
                callback_data=f"invite_{country['user_id']}"
            )])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="alliances")])

        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_alliance_members(self, query, context):
        """Show alliance members"""
        user_id = query.from_user.id
        alliance = self.alliance.get_player_alliance(user_id)

        if not alliance:
            await query.edit_message_text("❌ شما عضو هیچ اتحادی نیستید!")
            return

        members = self.alliance.get_alliance_members(alliance['alliance_id'])

        menu_text = f"👥 اعضای اتحاد {alliance['alliance_name']}\n\n"

        for member in members:
            role_emoji = "👑" if member['role'] == 'leader' else "⚔️" if member['role'] == 'officer' else "👤"
            menu_text += f"{role_emoji} {member['country_name']} - {member['username']}\n"

        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="alliances")]]
        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_alliance_invitations(self, query, context):
        """Show pending alliance invitations"""
        user_id = query.from_user.id
        invitations = self.alliance.get_pending_invitations(user_id)

        if not invitations:
            await query.edit_message_text("📋 شما هیچ دعوت‌نامه‌ای ندارید!")
            return

        menu_text = "📋 دعوت‌نامه‌های اتحاد\n\n"

        keyboard = []
        for inv in invitations:
            menu_text += f"🤝 {inv['alliance_name']} از {inv['inviter_country']}\n"
            keyboard.append([
                InlineKeyboardButton(f"✅ پذیرش {inv['alliance_name']}", callback_data=f"accept_inv_{inv['id']}"),
                InlineKeyboardButton(f"❌ رد", callback_data=f"reject_inv_{inv['id']}")
            ])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="alliances")])
        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_market_listings(self, query, context, category):
        """Show market listings for category"""
        listings = self.marketplace.get_listings_by_category(category)

        if not listings:
            await query.edit_message_text("❌ در این دسته کالایی برای فروش وجود ندارد!")
            return

        menu_text = f"🛒 کالاهای {category}\n\n"

        keyboard = []
        for listing in listings[:10]:
            price_text = f"${listing['price']:,}"
            menu_text += f"{listing['item_name']} - {price_text} - {listing['seller_country']}\n"
            keyboard.append([InlineKeyboardButton(
                f"خرید {listing['item_name']} - {price_text}", 
                callback_data=f"buy_{listing['id']}"
            )])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="market_browse")])
        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_sell_categories(self, query, context):
        """Show categories for selling items"""
        menu_text = "💰 فروش کالا\n\nچه چیزی می‌خواهید بفروشید؟"

        keyboard = [
            [
                InlineKeyboardButton("⚔️ تسلیحات", callback_data="sell_cat_weapons"),
                InlineKeyboardButton("📊 منابع", callback_data="sell_cat_resources")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="marketplace")
            ]
        ]

        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_my_listings(self, query, context):
        """Show user's market listings"""
        user_id = query.from_user.id
        listings = self.marketplace.get_player_listings(user_id)

        if not listings:
            await query.edit_message_text("📋 شما هیچ کالایی برای فروش ندارید!")
            return

        menu_text = "📋 آگهی‌های شما\n\n"

        keyboard = []
        for listing in listings:
            menu_text += f"{listing['item_name']} - ${listing['price']:,} - {listing['status']}\n"
            if listing['status'] == 'active':
                keyboard.append([InlineKeyboardButton(
                    f"❌ حذف {listing['item_name']}", 
                    callback_data=f"remove_{listing['id']}"
                )])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="marketplace")])
        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_alliance_invite(self, query, context):
        """Handle alliance invitation"""
        user_id = query.from_user.id
        invitee_id = int(query.data.replace("invite_", ""))

        result = self.alliance.invite_to_alliance(user_id, invitee_id)
        await query.edit_message_text(f"{'✅' if result['success'] else '❌'} {result['message']}")

    async def handle_invitation_response(self, query, context, response):
        """Handle alliance invitation response"""
        user_id = query.from_user.id
        invitation_id = int(query.data.replace(f"{response}_inv_", ""))

        result = self.alliance.respond_to_invitation(user_id, invitation_id, response)
        await query.edit_message_text(f"{'✅' if result['success'] else '❌'} {result['message']}")

    async def handle_marketplace_purchase(self, query, context):
        """Handle marketplace purchase"""
        try:
            user_id = query.from_user.id
            callback_data = query.data
            
            # Extract listing ID from callback data
            if not callback_data.startswith("buy_"):
                await query.edit_message_text("❌ داده نامعتبر!")
                return
                
            listing_id_str = callback_data.replace("buy_", "")
            if not listing_id_str.isdigit():
                await query.edit_message_text("❌ شناسه کالا نامعتبر!")
                return
                
            listing_id = int(listing_id_str)
            
            # Check if listing exists
            listing = self.marketplace.get_listing(listing_id)
            if not listing:
                await query.edit_message_text("❌ کالا یافت نشد!")
                return

            result = self.marketplace.purchase_item(user_id, listing_id, 1)

            if result['success']:
                # Send convoy news if applicable
                try:
                    await self.news.send_marketplace_purchase(result)
                except:
                    pass  # Don't fail purchase if news fails

            await query.edit_message_text(f"{'✅' if result['success'] else '❌'} {result['message']}")
            
        except ValueError:
            await query.edit_message_text("❌ شناسه کالا نامعتبر!")
        except Exception as e:
            logger.error(f"Error in marketplace purchase: {e}")
            await query.edit_message_text("❌ خطایی در خرید رخ داد! لطفاً دوباره تلاش کنید.")

    async def handle_sell_category(self, query, context):
        """Handle sell category selection"""
        user_id = query.from_user.id
        category = query.data.replace("sell_cat_", "")

        # Show player's items for selling in this category
        player = self.db.get_player(user_id)

        if category == "resources":
            resources = self.db.get_player_resources(user_id)
            items_text = f"""📊 فروش منابع - {player['country_name']}

💰 پول شما: ${player['money']:,}

منابع قابل فروش:"""

            sellable_resources = []
            for resource, amount in resources.items():
                if resource != 'user_id' and amount >= 100:
                    from config import Config
                    resource_config = Config.RESOURCES.get(resource, {})
                    resource_name = resource_config.get('name', resource)
                    resource_emoji = resource_config.get('emoji', '📦')
                    sellable_resources.append(f"{resource_emoji} {resource_name}: {amount:,}")

            if sellable_resources:
                items_text += "\n" + "\n".join(sellable_resources)
                items_text += "\n\n💡 برای فروش، ابتدا مقدار و قیمت را تعیین کنید"
            else:
                items_text += "\n❌ منابع کافی برای فروش ندارید!"

        elif category == "weapons":
            weapons = self.db.get_player_weapons(user_id)
            items_text = f"""⚔️ فروش تسلیحات - {player['country_name']}

💰 پول شما: ${player['money']:,}

تسلیحات قابل فروش:"""

            sellable_weapons = []
            for weapon, amount in weapons.items():
                if weapon != 'user_id' and amount >= 1:
                    weapon_emoji = {
                        'rifle': '🔫', 'tank': '🚗', 'fighter_jet': '✈️',
                        'drone': '🚁', 'missile': '🚀', 'warship': '🚢'
                    }.get(weapon, '⚔️')
                    sellable_weapons.append(f"{weapon_emoji} {weapon}: {amount:,}")

            if sellable_weapons:
                items_text += "\n" + "\n".join(sellable_weapons)
                items_text += "\n\n💡 برای فروش، ابتدا مقدار و قیمت را تعیین کنید"
            else:
                items_text += "\n❌ تسلیحات کافی برای فروش ندارید!"

        await query.edit_message_text(items_text)

    async def handle_remove_listing(self, query, context):
        """Handle removing marketplace listing"""
        user_id = query.from_user.id
        listing_id = int(query.data.replace("remove_", ""))

        result = self.marketplace.cancel_listing(user_id, listing_id)
        await query.edit_message_text(f"{'✅' if result['success'] else '❌'} {result['message']}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id

        # Check if user is awaiting official statement
        if context.user_data.get('awaiting_statement'):
            message = update.message.text
            if len(message) > 300:
                await update.message.reply_text("❌ متن بیانیه نباید بیش از 300 کاراکتر باشد.")
                return

            player = self.db.get_player(user_id)
            await self.news.send_official_statement(player['country_name'], message)
            await update.message.reply_text("✅ بیانیه رسمی شما منتشر شد.")

            context.user_data['awaiting_statement'] = False

            # Show main menu
            await asyncio.sleep(1)
            await self.show_main_menu(update, context)

        # Check if user is creating alliance
        elif context.user_data.get('awaiting_alliance_name'):
            alliance_name = update.message.text
            if len(alliance_name) > 50:
                await update.message.reply_text("❌ نام اتحاد نباید بیش از 50 کاراکتر باشد.")
                return

            result = self.alliance.create_alliance(user_id, alliance_name)
            await update.message.reply_text(f"{'✅' if result['success'] else '❌'} {result['message']}")

            context.user_data['awaiting_alliance_name'] = False

            # Show main menu
            await asyncio.sleep(1)
            await self.show_main_menu(update, context)

    async def income_cycle(self):
        """6-hour automated income cycle"""
        logger.info("Starting income cycle...")

        players = self.db.get_all_players()
        for player in players:
            try:
                # Calculate and distribute income
                income = self.economy.calculate_income(player['user_id'])
                new_money = player['money'] + income

                # Update population from farms
                population_increase = self.economy.calculate_population_increase(player['user_id'])
                new_population = player['population'] + population_increase

                # Convert population to soldiers from military bases
                soldier_increase = self.economy.calculate_soldier_increase(player['user_id'])
                new_soldiers = player['soldiers'] + soldier_increase

                # Update database
                self.db.update_player_income(
                    player['user_id'],
                    new_money,
                    new_population,
                    new_soldiers
                )

                # Distribute mine resources
                self.economy.distribute_mine_resources(player['user_id'])

                logger.info(f"Income distributed to {player['country_name']}: ${income}")

            except Exception as e:
                logger.error(f"Error in income cycle for player {player['user_id']}: {e}")

        # Send global news about income cycle
        await self.news.send_income_cycle_complete()
        logger.info("Income cycle completed")

    async def process_pending_attacks(self):
        """Process pending attacks that are due"""
        try:
            results = self.combat.process_pending_attacks()
            
            for result in results:
                # Send news about completed attacks
                attacker = self.db.get_player(result['attacker_id'])
                defender = self.db.get_player(result['defender_id'])
                
                if result['result']['success']:
                    await self.news.send_war_news(
                        attacker['country_name'], 
                        defender['country_name'], 
                        result['result']
                    )
                    
        except Exception as e:
            logger.error(f"Error processing pending attacks: {e}")

    def setup_scheduler(self):
        """Setup the automated scheduler"""
        # 6-hour income cycle
        self.scheduler.add_job(
            func=self.income_cycle,
            trigger=IntervalTrigger(hours=6),
            id='income_cycle',
            name='6-hour income cycle',
            replace_existing=True
        )
        
        # Process pending attacks every minute
        self.scheduler.add_job(
            func=self.process_pending_attacks,
            trigger=IntervalTrigger(minutes=1),
            id='pending_attacks',
            name='Process pending attacks',
            replace_existing=True
        )
        
        logger.info("Scheduler configured - 6-hour income cycle and pending attacks active")

    async def start_scheduler(self):
        """Start the scheduler within async context"""
        self.scheduler.start()
        logger.info("Scheduler started")

    async def post_init(self, application):
        """Post initialization callback"""
        await self.start_scheduler()

    async def show_admin_give_category(self, query, context):
        """Show admin give category"""
        user_id = query.from_user.id
        if not self.admin.is_admin(user_id):
            await query.edit_message_text("❌ شما مجاز به این کار نیستید!")
            return

        category = query.data.replace("admin_give_cat_", "")

        if category == "money":
            menu_text = """💰 هدیه پول به کشور

انتخاب کنید که چه مقداری پول هدیه دهید:
(پول به تمام کشورها اضافه می‌شود)"""
            keyboard = self.keyboards.admin_give_money_keyboard()
        elif category == "resources":
            menu_text = """📦 هدیه منابع به کشور

انتخاب کنید که چه مقدار از کدام منبع هدیه دهید:
(آیتم‌ها به تمام کشورها اضافه می‌شود)"""
            keyboard = self.keyboards.admin_give_resources_keyboard()
        elif category == "weapons":
            menu_text = """⚔️ هدیه سلاح‌ها به کشور

انتخاب کنید که چه مقدار از کدام سلاح هدیه دهید:
(آیتم‌ها به تمام کشورها اضافه می‌شود)"""
            keyboard = self.keyboards.admin_give_weapons_keyboard()
        elif category == "buildings":
            menu_text = "🏗 هدیه ساختمان به کشور\n\n❌ این بخش هنوز پیاده‌سازی نشده!"
            keyboard = self.keyboards.admin_give_items_keyboard()
        elif category == "population":
            menu_text = "👥 هدیه جمعیت به کشور\n\n❌ این بخش هنوز پیاده‌سازی نشده!"
            keyboard = self.keyboards.admin_give_items_keyboard()
        elif category == "soldiers":
            menu_text = "🪖 هدیه سرباز به کشور\n\n❌ این بخش هنوز پیاده‌سازی نشده!"
            keyboard = self.keyboards.admin_give_items_keyboard()
        else:
            menu_text = "❌ دسته نامعتبر!"
            keyboard = self.keyboards.admin_give_items_keyboard()

        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_admin_give_item(self, query, context):
        """Handle admin giving items"""
        user_id = query.from_user.id
        if not self.admin.is_admin(user_id):
            await query.edit_message_text("❌ شما مجاز به این کار نیستید!")
            return

        # Parse data: admin_give_all_to_iron_1000
        data_parts = query.data.split("_")
        if len(data_parts) < 5:
            await query.edit_message_text("❌ فرمت دستور نامعتبر!")
            return

        # Skip 'to' part: [admin, give, all, to, iron, 1000]
        if data_parts[3] != "to":
            await query.edit_message_text("❌ فرمت دستور نامعتبر!")
            return

        item_type = data_parts[4]  # e.g., "iron", "rifle", etc.
        try:
            amount = int(data_parts[5])
        except (ValueError, IndexError):
            await query.edit_message_text("❌ مقدار نامعتبر!")
            return

        # Handle money gifting
        if item_type == "money":
            players = self.db.get_all_players()
            if not players:
                await query.edit_message_text("❌ هیچ بازیکنی وجود ندارد!")
                return

            success_count = 0
            for player in players:
                try:
                    result = self.admin.give_money_to_player(player['user_id'], amount)
                    if result['success']:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error giving money to {player['country_name']}: {e}")

            await query.edit_message_text(
                f"✅ پول با موفقیت به {success_count} کشور هدیه داده شد!\n\n"
                f"💰 مقدار: {amount:,}",
                reply_markup=self.keyboards.admin_give_items_keyboard()
            )
            return


        # Give to all players for resources and weapons
        players = self.db.get_all_players()
        if not players:
            await query.edit_message_text("❌ هیچ بازیکنی وجود ندارد!")
            return

        success_count = 0
        error_count = 0

        for player in players:
            try:
                result = None

                # Check if it's a resource
                if item_type in ['iron', 'copper', 'oil', 'aluminum', 'gold', 'uranium', 'lithium', 'coal', 'nitro', 'sulfur', 'titanium']:
                    result = self.admin.give_resources_to_player(player['user_id'], item_type, amount)
                    if result['success']:
                        success_count += 1

                # Check if it's a weapon
                elif item_type in ['rifle', 'tank', 'fighter', 'jet', 'drone', 'simple', 'bomb', 'nuclear', 'ballistic', 'missile', 'f22']:
                    weapon_map = {
                        'rifle': 'rifle',
                        'tank': 'tank', 
                        'fighter': 'fighter_jet',
                        'jet': 'fighter_jet',
                        'drone': 'drone',
                        'simple': 'bomb',
                        'bomb': 'bomb',
                        'nuclear': 'nuclear_bomb',
                        'ballistic': 'missile',
                        'missile': 'missile',
                        'f22': 'F-22'
                    }
                    weapon_name = weapon_map.get(item_type, item_type)
                    result = self.admin.give_weapons_to_player(player['user_id'], weapon_name, amount)
                    if result['success']:
                        success_count += 1

                else:
                    logger.error(f"Unknown item type: {item_type}")
                    error_count += 1
                    continue

            except Exception as e:
                logger.error(f"Error giving {item_type} to {player['country_name']}: {e}")
                error_count += 1

        # Create result message
        if success_count > 0:
            result_text = f"✅ آیتم با موفقیت به {success_count} کشور هدیه داده شد!\n\n"
            result_text += f"📦 آیتم: {item_type}\n"
            result_text += f"🔢 مقدار: {amount:,}"

            if error_count > 0:
                result_text += f"\n\n⚠️ {error_count} خطا رخ داد"
        else:
            result_text = f"❌ خطا در هدیه دادن آیتم!\n\n"
            result_text += f"📦 آیتم: {item_type}\n"
            result_text += f"🔢 مقدار: {amount:,}\n"
            result_text += f"❌ تعداد خطاها: {error_count}"

        await query.edit_message_text(
            result_text,
            reply_markup=self.keyboards.admin_give_items_keyboard()
        )

    def run(self):
        """Run the bot"""
        logger.info("Starting DragonRP Bot...")

        # Initialize database
        self.db.initialize()

        # Set bot for news channel
        bot = Bot(token=self.token)
        self.news.set_bot(bot)

        # Setup application
        application = Application.builder().token(self.token).post_init(self.post_init).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Setup scheduler (but don't start yet)
        self.setup_scheduler()

        # Add admin handlers
        self.admin.setup_handlers(application)

        logger.info("Bot is ready!")

        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = DragonRPBot()
    bot.run()