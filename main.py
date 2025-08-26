import logging
import asyncio
import os
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime

# Updated database imports
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
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "7315307921:AAHZGyLUDCR4XudiqdQCRtjYqjeODfdwChE")
        
        # Initialize Database
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
                await self.propose_peace(query, context)
            elif data == "intercept_convoys":
                await self.show_convoy_interception_menu(query, context)
            elif data.startswith("send_to_"):
                await self.handle_resource_transfer_transport_select(query, context)
            elif data.startswith("transfer_"):
                await self.handle_transport_selection(query, context)
            elif data.startswith("use_transport_"):
                await self.handle_transport_selection(query, context)
            elif data.startswith("convoy_"):
                if data.startswith("convoy_escort_"):
                    await self.handle_convoy_escort(query, context)
                else:
                    await self.handle_convoy_action(query, context)
            elif data.startswith("confirm_convoy_"):
                await self.handle_convoy_confirmation(query, context)
            elif data == "alliances":
                await self.show_alliance_menu(query, context)
            elif data.startswith("alliance_"):
                if data == "alliance_create":
                    await self.handle_alliance_create(query, context)
                elif data == "alliance_invite":
                    await self.handle_alliance_invite(query, context)
                elif data.startswith("alliance_invite_"):
                    target_id = int(data.replace("alliance_invite_", ""))
                    await self.process_alliance_invitation(query, context, target_id)
                elif data == "alliance_members":
                    await self.handle_alliance_members(query, context)
                elif data == "alliance_invitations":
                    await self.handle_alliance_invitations(query, context)
                elif data == "alliance_leave":
                    await self.handle_alliance_leave(query, context)
            elif data == "marketplace":
                await self.show_marketplace_menu(query, context)
            elif data.startswith("market_"):
                await self.handle_marketplace_action(query, context)
            elif data.startswith("sell_resource_") or data.startswith("sell_weapon_"):
                await self.handle_sell_item_dialog(query, context, data)
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
            elif data.startswith("confirm_sell_"):
                await self.handle_confirm_sell(query, context)
            elif data.startswith("manual_transfer_"):
                await self.handle_manual_transfer(query, context)
            elif data.startswith("manual_sell_"):
                await self.handle_manual_sell(query, context)
            elif data.startswith("admin_give_cat_"):
                await self.show_admin_give_category(query, context)
            elif data.startswith("penalty_money_") or data.startswith("penalty_resources_") or data.startswith("penalty_weapons_"):
                await self.admin.handle_penalty_action(query, context, data)
            elif data.startswith("admin_"):
                await self.admin.handle_admin_action(query, context)
            else:
                logger.warning(f"Unhandled callback query: {query.data}")
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

⛏ معادن (تولید هر 6 ساعت):
• معدن آهن - $90,000 (210 واحد/6ساعت، درآمد: $50K)
• معدن مس - $100,000 (120 واحد/6ساعت، درآمد: $60K)
• معدن نفت - $120,000 (600 واحد/6ساعت، درآمد: $60K)
• معدن آلومینیوم - $150,000 (200 واحد/6ساعت، درآمد: $70K)
• معدن طلا - $300,000 (18 واحد/6ساعت، درآمد: $210K)
• معدن اورانیوم - $1,000,000 (24 واحد/6ساعت، درآمد: $100K)
• معدن لیتیوم - $180,000 (30 واحد/6ساعت، درآمد: $100K)
• معدن زغال‌سنگ - $80,000 (1000 واحد/6ساعت، درآمد: $10K)
• معدن نیتر - $120,000 (600 واحد/6ساعت، درآمد: $60K)
• معدن گوگرد - $75,000 (900 واحد/6ساعت، درآمد: $30K)
• معدن تیتانیوم - $300,000 (18 واحد/6ساعت، درآمد: $90K)

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

        # Add back button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به ساختمان‌ها", callback_data="buildings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if result['success']:
            await query.edit_message_text(
                f"✅ {result['message']}\n\n"
                f"💰 پول باقی‌مانده: ${result['remaining_money']:,}",
                reply_markup=reply_markup
            )

            # Send news to channel only for first build
            player = self.db.get_player(user_id)
            if result.get('is_first_build', False):
                await self.news.send_building_constructed(player['country_name'], result['building_name'])
        else:
            await query.edit_message_text(f"❌ {result['message']}", reply_markup=reply_markup)

    async def show_military_menu(self, query, context):
        """Show military management menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)
        logger.info(f"Military menu for user {user_id}: rifle={weapons.get('rifle', 0)}, weapons={weapons}")

        # Count total weapons for summary
        weapon_counts = {}
        basic_weapons = ['missile', 'warship']
        defense_weapons = []
        bombs = ['simple_bomb', 'nuclear_bomb']
        missiles = ['simple_missile', 'ballistic_missile', 'nuclear_missile', 'trident2_conventional', 'trident2_nuclear', 'satan2_conventional', 'satan2_nuclear', 'df41_nuclear', 'tomahawk_conventional', 'tomahawk_nuclear', 'kalibr_conventional']
        jets = ['f22', 'f35', 'su57', 'j20', 'f15ex', 'su35s']
        naval = ['submarine', 'destroyer', 'aircraft_carrier', 'patrol_ship', 'patrol_boat', 'amphibious_ship', 'aircraft_carrier_full', 'nuclear_submarine']
        transport = ['armored_truck', 'cargo_helicopter', 'cargo_plane', 'escort_frigate', 'logistics_drone', 'heavy_transport', 'supply_ship', 'stealth_transport']
        tanks = ['kf51_panther', 'abrams_x', 'm1e3_abrams', 't90ms_proryv', 'm1a2_abrams_sepv3']
        advanced_defense = ['s500_defense', 'thaad_defense', 's400_defense', 'iron_dome', 'slq32_ew', 'phalanx_ciws']
        other = []

        weapon_counts['basic'] = sum(weapons.get(w, 0) for w in basic_weapons)
        weapon_counts['defense'] = sum(weapons.get(w, 0) for w in defense_weapons + advanced_defense)
        weapon_counts['bombs'] = sum(weapons.get(w, 0) for w in bombs)
        weapon_counts['missiles'] = sum(weapons.get(w, 0) for w in missiles)
        weapon_counts['jets'] = sum(weapons.get(w, 0) for w in jets)
        weapon_counts['naval'] = sum(weapons.get(w, 0) for w in naval)
        weapon_counts['transport'] = sum(weapons.get(w, 0) for w in transport)
        weapon_counts['tanks'] = sum(weapons.get(w, 0) for w in tanks)
        weapon_counts['other'] = sum(weapons.get(w, 0) for w in other)

        menu_text = f"""⚔️ مدیریت نظامی - {player['country_name']}

👥 جمعیت: {player['population']:,}
⚔️سربازان: {player['soldiers']:,}

🔫 خلاصه تسلیحات:
🔫 سلاح‌های پایه: {weapon_counts['basic']:,}
🛡 سیستم‌های دفاعی: {weapon_counts['defense']:,}
💣 بمب‌ها: {weapon_counts['bombs']:,}
🚀 موشک‌ها: {weapon_counts['missiles']:,}
✈️ جنگنده‌ها: {weapon_counts['jets']:,}
🚢 نیروی دریایی: {weapon_counts['naval']:,}
🚚 نقل و انتقال: {weapon_counts['transport']:,}
🛡 تانک‌های پیشرفته: {weapon_counts['tanks']:,}
🚁 سایر: {weapon_counts['other']:,}

📊 جزئیات اصلی:
🚀 موشک: {weapons.get('missile', 0):,}
🚢 کشتی جنگی: {weapons.get('warship', 0):,}
💣 بمب هسته‌ای: {weapons.get('nuclear_bomb', 0):,}
🚀 موشک بالستیک: {weapons.get('ballistic_missile', 0):,}
🚀 Trident 2 هسته‌ای: {weapons.get('trident2_nuclear', 0):,}
🚀 Satan 2 هسته‌ای: {weapons.get('satan2_nuclear', 0):,}
✈️ F-22: {weapons.get('f22', 0):,}

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
        parts = query.data.split('_')
        if len(parts) < 3:
            await query.edit_message_text("❌ خطا در پردازش درخواست!")
            return

        weapon_type = '_'.join(parts[2:])  # Handle multi-part weapon names
        user_id = query.from_user.id

        # Check if weapon exists in config
        if weapon_type not in Config.WEAPONS:
            available_weapons = list(Config.WEAPONS.keys())[:10]
            await query.edit_message_text(
                f"❌ نوع سلاح نامعتبر: {weapon_type}\n\n"
                f"سلاح‌های موجود: {', '.join(available_weapons)}"
            )
            return

        weapon_config = Config.WEAPONS[weapon_type]
        result = self.game_logic.produce_weapon(user_id, weapon_type, 1)

        if result['success']:
            weapon_name = weapon_config.get('name', weapon_type)

            await query.edit_message_text(
                f"✅ {weapon_name} با موفقیت تولید شد!\n\n"
                f"💰 هزینه: ${weapon_config.get('cost', 0):,}\n"
                f"💰 پول باقی‌مانده: ${result['remaining_money']:,}",
                reply_markup=self.keyboards.back_to_military_keyboard()
            )

            # Send news to channel only for special weapons
            player = self.db.get_player(user_id)
            await self.news.send_weapon_produced(player['country_name'], result['weapon_name'], 1)
        else:
            await query.edit_message_text(
                f"❌ {result['message']}",
                reply_markup=self.keyboards.back_to_military_keyboard()
            )

    async def show_weapon_quantity_selection(self, query, context):
        """Show quantity selection for weapon production"""
        user_id = query.from_user.id
        weapon_type = query.data.replace("select_weapon_", "")

        player = self.db.get_player(user_id)
        weapon_config = Config.WEAPONS.get(weapon_type, {})

        if not weapon_config:
            await query.edit_message_text("❌ نوع سلاح نامعتبر است!")
            return

        weapon_name = weapon_config.get('name', weapon_type)
        weapon_cost = weapon_config.get('cost', 0)

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
        building_config = Config.BUILDINGS.get(building_type, {})

        if not building_config:
            await query.edit_message_text("❌ نوع ساختمان نامعتبر است!")
            return

        building_name = building_config.get('name', building_type)
        building_cost = building_config.get('cost', 0)

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

                # Send news to channel only for special weapons
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
        """Show available attack targets based on distance and available weapons"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)
        attacker_country = player['country_code']

        # Get all countries
        all_countries = self.db.get_all_countries()
        available_targets = []

        for target in all_countries:
            if target['user_id'] != user_id:  # Can't attack yourself
                target_country = target['country_code']

                # Check what weapons can attack this target
                available_weapons = Config.get_available_weapons_for_attack(
                    attacker_country, target_country, weapons
                )

                if available_weapons:
                    distance_type = Config.get_country_distance_type(attacker_country, target_country)
                    target['distance_type'] = distance_type
                    target['available_weapons_count'] = len(available_weapons)
                    available_targets.append(target)

        if not available_targets:
            await query.edit_message_text(
                "⚔️ هیچ کشور قابل حمله‌ای یافت نشد!\n\n"
                "💡 برای حمله به کشورهای مختلف نیاز دارید:\n"
                "🔫 همسایه‌ها: همه سلاح‌ها\n"
                "✈️ منطقه‌ای: جت‌ها و موشک‌ها\n"
                "🚀 بین‌قاره‌ای: فقط موشک‌های دوربرد",
                reply_markup=self.keyboards.back_to_military_keyboard()
            )
            return

        menu_text = f"⚔️ انتخاب هدف حمله - {player['country_name']}\n\n"

        # Group targets by distance
        neighbors = [t for t in available_targets if t['distance_type'] == 'neighbor']
        regional = [t for t in available_targets if t['distance_type'] == 'regional'] 
        intercontinental = [t for t in available_targets if t['distance_type'] == 'intercontinental']

        if neighbors:
            menu_text += "🔫 همسایه‌ها (همه سلاح‌ها):\n"
            for target in neighbors:
                flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')
                menu_text += f"{flag} {target['country_name']} ({target['available_weapons_count']} نوع سلاح)\n"
            menu_text += "\n"

        if regional:
            menu_text += "✈️ منطقه‌ای (جت‌ها و موشک‌ها):\n"
            for target in regional:
                flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')
                menu_text += f"{flag} {target['country_name']} ({target['available_weapons_count']} نوع سلاح)\n"
            menu_text += "\n"

        if intercontinental:
            menu_text += "🚀 بین‌قاره‌ای (فقط موشک‌های دوربرد):\n"
            for target in intercontinental:
                flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')
                menu_text += f"{flag} {target['country_name']} ({target['available_weapons_count']} نوع سلاح)\n"
            menu_text += "\n"

        menu_text += "انتخاب کنید:"

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
        """Show weapon selection for attack based on distance and range"""
        user_id = query.from_user.id
        data_parts = query.data.split("_")
        target_id = int(data_parts[2])
        attack_type = data_parts[3]

        # Check if this is conquest mode
        conquest_mode = attack_type == "conquest"

        # Get player and target information
        player = self.db.get_player(user_id)
        target = self.db.get_player(target_id)

        if not target:
            await query.edit_message_text("❌ کشور هدف یافت نشد!")
            return

        # Get player weapons
        player_weapons = self.db.get_player_weapons(user_id)

        # Check for range extenders
        has_tanker = player_weapons.get('tanker_aircraft', 0) > 0
        has_carrier = player_weapons.get('aircraft_carrier_transport', 0) > 0

        # Get weapons that can attack this target based on distance
        available_weapon_types = Config.get_available_weapons_for_attack(
            player['country_code'], target['country_code'], player_weapons, has_tanker, has_carrier
        )

        # Convert list to dictionary with quantities
        available_weapons = {}
        for weapon_type in available_weapon_types:
            if weapon_type in player_weapons and player_weapons[weapon_type] > 0:
                available_weapons[weapon_type] = player_weapons[weapon_type]

        if not available_weapons:
            distance_type = Config.get_country_distance_type(player['country_code'], target['country_code'])
            keyboard = self.keyboards.back_to_military_keyboard()

            if distance_type == 'neighbor':
                message = f"❌ تسلیحات کافی برای حمله به {target['country_name']} ندارید!"
            elif distance_type == 'regional':
                if has_tanker or has_carrier:
                    message = f"❌ حتی با سوخت‌رسان/ناوبر، جت‌های شما برد کافی ندارند"
                else:
                    message = f"❌ برای حمله به {target['country_name']} نیاز به جت یا موشک دارید!"
            else:
                if has_tanker or has_carrier:
                    message = f"❌ حتی با سوخت‌رسان/ناوبر، فاصله خیلی زیاد است"
                else:
                    message = f"❌ برای حمله به {target['country_name']} فقط موشک‌های دوربرد استفاده کنید!"

            await query.edit_message_text(message, reply_markup=keyboard)
            return

        # Display available weapons for this distance
        distance_type = Config.get_country_distance_type(player['country_code'], target['country_code'])

        menu_text = f"⚔️ انتخاب تسلیحات برای حمله به {target['country_name']}\n\n"

        range_bonus_text = ""
        if has_carrier and has_tanker:
            range_bonus_text = " (با ناوبر و سوخت‌رسان)"
        elif has_carrier:
            range_bonus_text = " (با ناوبر)"
        elif has_tanker:
            range_bonus_text = " (با سوخت‌رسان)"

        if distance_type == 'neighbor':
            menu_text += f"🔫 همسایه - همه سلاح‌ها قابل استفاده{range_bonus_text}:\n"
        elif distance_type == 'regional':
            menu_text += f"✈️ منطقه‌ای - جت‌ها و موشک‌ها{range_bonus_text}:\n"
        else:
            menu_text += f"🚀 بین‌قاره‌ای - فقط موشک‌های دوربرد{range_bonus_text}:\n"

        # List available weapons
        for weapon_type, quantity in available_weapons.items():
            weapon_config = Config.WEAPONS.get(weapon_type, {})
            weapon_name = weapon_config.get('name', weapon_type)
            emoji = weapon_config.get('emoji', '⚔️')
            menu_text += f"{emoji} {weapon_name}: {quantity:,}\n"

        menu_text += f"\nنوع حمله: {attack_type}\nانتخاب کنید:"

        keyboard = self.keyboards.weapon_selection_keyboard(target_id, attack_type, available_weapons)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_attack_execution(self, query, context):
        """Handle actual attack execution"""
        user_id = query.from_user.id
        data_parts = query.data.split("_")

        if len(data_parts) < 4:
            await query.edit_message_text("❌ داده‌های حمله نامعتبر!")
            return

        target_id = int(data_parts[2])
        attack_type = data_parts[3]
        weapon_selection = data_parts[4] if len(data_parts) > 4 else "all"

        # Check if this is conquest mode
        conquest_mode = attack_type == "conquest"

        attacker = self.db.get_player(user_id)
        target = self.db.get_player(target_id)

        if not target:
            await query.edit_message_text("❌ کشور هدف یافت نشد!")
            return

        # Check if attacker has any offensive weapons
        available_weapons = self.db.get_player_weapons(user_id)
        has_offensive_weapons = False
        offensive_weapons = []

        for weapon_type, count in available_weapons.items():
            if weapon_type != 'user_id' and count > 0:
                # Check if weapon exists in config
                if weapon_type in Config.WEAPONS:
                    weapon_config = Config.WEAPONS[weapon_type]
                    # Skip pure transport and defense weapons
                    if weapon_config.get('category') not in ['transport', 'defense']:
                        has_offensive_weapons = True
                        offensive_weapons.append(f"{weapon_config.get('name', weapon_type)}: {count}")

        if not has_offensive_weapons:
            await query.edit_message_text(
                "❌ شما هیچ سلاح تهاجمی برای حمله ندارید!\n\n"
                "ابتدا از بخش تسلیحات، سلاح‌های تهاجمی تولید کنید.\n\n"
                f"سلاح‌های موجود: {', '.join(offensive_weapons) if offensive_weapons else 'هیچکدام'}"
            )
            return

        # Execute attack
        result = self.combat.schedule_delayed_attack(user_id, target_id, attack_type, conquest_mode)

        if not result['success']:
            await query.edit_message_text(f"❌ {result['message']}")
            return

        await query.edit_message_text(f"✅ {result['message']}")

        # Send news to channel about attack preparation
        attacker_flag = Config.COUNTRY_FLAGS.get(attacker['country_code'], '🏳')
        target_flag = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳')

        mode_text = " 🏴‍☠️ (حالت فتح)" if conquest_mode else ""
        attack_news = f"""⚔️ آماده‌سازی حمله{mode_text}!

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
        # Default to 0 if no transports are present
        transport_options = [
            ('none', 'بدون وسیله', '🚶‍♂️'),
            ('armored_truck', 'کامیون زرهی', '🚚'),
            ('cargo_helicopter', 'هلیکوپتر باری', '🚁'),
            ('cargo_plane', 'هواپیمای باری', '✈️'),
            ('logistics_drone', 'پهپاد لجستیک', '🛸'),
            ('heavy_transport', 'ترابری سنگین', '🚛'),
            ('supply_ship', 'کشتی تدارکات', '🚢'),
            ('stealth_transport', 'ترابری پنهان‌کار', '🥷')
        ]

        menu_text = f"""🚚 انتقال منابع - {player['country_name']}

💰 پول شما: ${player['money']:,}
⏱ زمان انتقال تخمینی: (با توجه به انتخاب وسیله نقلیه)

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
🛸 پهپاد لجستیک: {weapons.get('logistics_drone', 0)}
🚛 ترابری سنگین: {weapons.get('heavy_transport', 0)}
🚢 کشتی تدارکات: {weapons.get('supply_ship', 0)}
🥷 ترابری پنهان‌کار: {weapons.get('stealth_transport', 0)}

💡 محموله در طول مسیر قابل رهگیری است!

کشور مقصد را انتخاب کنید:"""

        keyboard = self.keyboards.send_resources_targets_keyboard(other_countries)
        await query.edit_message_text(menu_text, reply_markup=keyboard)

    async def handle_resource_transfer_transport_select(self, query, context):
        """Handle transport selection for resource transfer"""
        user_id = query.from_user.id
        target_id = int(query.data.replace("send_to_", ""))

        player = self.db.get_player(user_id)
        target_player = self.db.get_player(target_id)
        resources = self.db.get_player_resources(user_id)
        weapons = self.db.get_player_weapons(user_id)

        menu_text = f"""🚚 انتخاب وسیله نقلیه - انتقال به {target_player['country_name']}

💰 پول شما: ${player['money']:,}

منابع قابل انتقال (حداکثر 1000 واحد):
"""

        available_resources_for_transfer = []
        for resource, amount in resources.items():
            if resource != 'user_id' and amount >= 1000:
                resource_config = Config.RESOURCES.get(resource, {})
                resource_name = resource_config.get('name', resource)
                resource_emoji = resource_config.get('emoji', '📦')
                available_resources_for_transfer.append(f"{resource_emoji} {resource_name} ({amount:,} موجود)")

        if available_resources_for_transfer:
            menu_text += "\n" + "\n".join(available_resources_for_transfer)
        else:
            menu_text += "\n❌ منابع کافی برای انتقال ندارید!"

        menu_text += """

🚛 وسایل نقلیه موجود:"""

        transport_options = [
            ('none', 'بدون وسیله', '🚶‍♂️', 0),
            ('armored_truck', 'کامیون زرهی', '🚚', weapons.get('armored_truck', 0)),
            ('cargo_helicopter', 'هلیکوپتر باری', '🚁', weapons.get('cargo_helicopter', 0)),
            ('cargo_plane', 'هواپیمای باری', '✈️', weapons.get('cargo_plane', 0)),
            ('escort_frigate', 'ناوچه اسکورت', '🚢', weapons.get('escort_frigate', 0)),
            ('logistics_drone', 'پهپاد لجستیک', '🛸', weapons.get('logistics_drone', 0)),
            ('heavy_transport', 'ترابری سنگین', '🚛', weapons.get('heavy_transport', 0)),
            ('supply_ship', 'کشتی تدارکات', '🚢', weapons.get('supply_ship', 0)),
            ('stealth_transport', 'ترابری پنهان‌کار', '🥷', weapons.get('stealth_transport', 0))
        ]

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []
        for transport_id, transport_name, transport_emoji, count in transport_options:
            if count > 0 or transport_id == 'none':
                keyboard.append([InlineKeyboardButton(
                    f"{transport_emoji} {transport_name} ({count} موجود)",
                    callback_data=f"transfer_{target_id}_{transport_id}"
                )])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="send_resources")])
        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))


    async def handle_transport_selection(self, query, context):
        """Handle the actual transport selection and resource transfer"""
        user_id = query.from_user.id

        # Handle both transfer_ and use_transport_ formats
        if query.data.startswith("transfer_"):
            data_parts = query.data.replace("transfer_", "").split("_")
        elif query.data.startswith("use_transport_"):
            data_parts = query.data.replace("use_transport_", "").split("_")
        else:
            await query.edit_message_text("❌ داده نامعتبر!")
            return

        if len(data_parts) < 2:
            await query.edit_message_text("❌ داده نامعتبر!")
            return

        try:
            target_id = int(data_parts[0])
            transport_type = "_".join(data_parts[1:])  # Join all remaining parts for multi-word transport names
        except (ValueError, IndexError):
            await query.edit_message_text("❌ داده‌های نامعتبر!", reply_markup=self.keyboards.back_to_main_keyboard())
            return

        player = self.db.get_player(user_id)
        target = self.db.get_player(target_id)

        if not player or not target:
            await query.edit_message_text("❌ کشور یافت نشد!", reply_markup=self.keyboards.back_to_main_keyboard())
            return
        resources = self.db.get_player_resources(user_id)

        # Select 1000 units of the first available resource or money
        transfer_resources = {}
        transfer_description = ""
        can_transfer = False

        # Prioritize money if available and no other resources
        if player['money'] >= 10000: # Use a higher threshold for money transfer as it's a different category
            transfer_resources = {'money': 10000}
            transfer_description = "💰 10,000 دلار"
            can_transfer = True
        else:
            # Find the first resource with at least 1000 units
            for resource_type, amount in resources.items():
                if resource_type != 'user_id' and amount >= 1000:
                    transfer_resources = {resource_type: 1000}
                    resource_config = Config.RESOURCES.get(resource_type, {})
                    transfer_description = f"{resource_config.get('emoji', '📦')} 1,000 {resource_config.get('name', resource_type)}"
                    can_transfer = True
                    break # Transfer only one resource type at a time

        if not can_transfer:
            await query.edit_message_text("❌ منابع کافی برای انتقال ندارید!", reply_markup=self.keyboards.back_to_main_keyboard())
            return

        # Check if selected transport is available
        if transport_type != 'none':
            weapons = self.db.get_player_weapons(user_id)
            available_count = weapons.get(transport_type, 0)
            if available_count < 1:
                # Debug info for the user - show all transport weapons for debugging
                all_transports = {
                    'armored_truck': weapons.get('armored_truck', 0),
                    'cargo_helicopter': weapons.get('cargo_helicopter', 0), 
                    'cargo_plane': weapons.get('cargo_plane', 0),
                    'escort_frigate': weapons.get('escort_frigate', 0),
                    'logistics_drone': weapons.get('logistics_drone', 0),
                    'heavy_transport': weapons.get('heavy_transport', 0),
                    'supply_ship': weapons.get('supply_ship', 0),
                    'stealth_transport': weapons.get('stealth_transport', 0)
                }

                debug_text = f"""❌ وسیله حمل‌ونقل انتخابی در دسترس نیست!

🔍 جزئیات:
• وسیله انتخابی: {transport_type}
• تعداد موجود: {available_count}

📊 تمام وسایل حمل‌ونقل شما:
🚚 کامیون زرهی: {all_transports['armored_truck']}
🚁 هلیکوپتر باری: {all_transports['cargo_helicopter']}
✈️ هواپیمای باری: {all_transports['cargo_plane']}
🚢 ناوچه اسکورت: {all_transports['escort_frigate']}
🛸 پهپاد لجستیک: {all_transports['logistics_drone']}
🚛 ترابری سنگین: {all_transports['heavy_transport']}
🚢 کشتی تدارکات: {all_transports['supply_ship']}
🥷 ترابری پنهان‌کار: {all_transports['stealth_transport']}"""

                await query.edit_message_text(debug_text, reply_markup=self.keyboards.back_to_main_keyboard())
                return

        # Create convoy with selected transport (resources will be deducted automatically)
        convoy_result = self.convoy.create_convoy_with_transport(user_id, target_id, transfer_resources, transport_type)

        # Check if convoy creation was successful
        if not convoy_result.get('success', False):
            await query.edit_message_text(f"❌ {convoy_result.get('message', 'خطا در ایجاد محموله!')}", reply_markup=self.keyboards.back_to_main_keyboard())
            return

        # Get transport info
        transport_info = {
            'none': ('بدون وسیله', '🚶‍♂️'),
            'armored_truck': ('کامیون زرهی', '🚚'),
            'cargo_helicopter': ('هلیکوپتر باری', '🚁'),
            'cargo_plane': ('هواپیمای باری', '✈️'),
            'logistics_drone': ('پهپاد لجستیک', '🛸'),
            'heavy_transport': ('ترابری سنگین', '🚛'),
            'supply_ship': ('کشتی تدارکات', '🚢'),
            'stealth_transport': ('ترابری پنهان‌کار', '🥷')
        }.get(transport_type, ('نامشخص', '🚛'))

        # Add news
        sender_country = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳') + ' ' + player['country_name']
        receiver_country = Config.COUNTRY_FLAGS.get(target['country_code'], '🏳') + ' ' + target['country_name']

        news_text = f"""🚚 انتقال منابع جدید!

📤 فرستنده: {sender_country}
📥 گیرنده: {receiver_country}
📦 محموله: {transfer_description}
🚛 وسیله نقلیه: {transport_info[1]} {transport_info[0]}
🛡 سطح امنیت: {convoy_result['security_level']}%
⏰ زمان تحویل: {convoy_result['estimated_arrival'].strftime('%H:%M')}

محموله در حال حرکت است..."""

        keyboard = self.convoy.create_convoy_news_keyboard(
            convoy_result['convoy_id'],
            convoy_result['security_level'],
            context.bot.username
        )

        # Send news to channel
        await context.bot.send_message(
            chat_id=Config.BOT_CONFIG['news_channel'],
            text=news_text,
            reply_markup=keyboard
        )

        success_text = f"""✅ منابع با موفقیت ارسال شد!

📦 محموله: {transfer_description}
🚛 وسیله نقلیه: {transport_info[1]} {transport_info[0]}
🎯 مقصد: {receiver_country}
🛡 سطح امنیت: {convoy_result['security_level']}%
⏰ زمان رسیدن: {convoy_result['estimated_arrival'].strftime('%H:%M')}

محموله در کانال اخبار منتشر شد."""

        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(success_text, reply_markup=keyboard)



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

    async def handle_convoy_escort(self, query, context):
        """Handle convoy escort request"""
        user_id = query.from_user.id
        convoy_id = int(query.data.replace("convoy_escort_", ""))

        # Get convoy details
        convoy = self.db.get_convoy(convoy_id)
        if not convoy:
            await query.edit_message_text("❌ محموله یافت نشد!")
            return

        # Check if convoy is still in transit
        if convoy['status'] != 'in_transit':
            await query.edit_message_text("❌ این محموله دیگر در حال حرکت نیست!")
            return

        # Check if user can escort (not sender/receiver)
        if convoy['sender_id'] == user_id or convoy['receiver_id'] == user_id:
            await query.edit_message_text("❌ نمی‌توانید محموله خودتان را اسکورت کنید!")
            return

        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)

        # Check available escort equipment
        escort_equipment = {
            'fighter_jet': weapons.get('fighter_jet', 0),
            'tank': weapons.get('tank', 0),
            'warship': weapons.get('warship', 0),
            'drone': weapons.get('drone', 0)
        }

        has_equipment = any(count > 0 for count in escort_equipment.values())

        if not has_equipment:
            await query.edit_message_text("❌ شما تجهیزات مناسب برای اسکورت ندارید!")
            return

        escort_text = f"""🛡 اسکورت محموله

🚚 محموله #{convoy_id}
🛡 امنیت فعلی: {convoy['security_level']}%

💪 تجهیزات اسکورت شما:
✈️ جنگنده: {escort_equipment['fighter_jet']}
🚗 تانک: {escort_equipment['tank']}
🚢 کشتی جنگی: {escort_equipment['warship']}
🚁 پهپاد: {escort_equipment['drone']}

⚠️ اسکورت محموله هزینه سوخت دارد!

آیا می‌خواهید این محموله را اسکورت کنید؟"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("✅ شروع اسکورت", callback_data=f"confirm_escort_{convoy_id}"),
                InlineKeyboardButton("❌ انصراف", callback_data="main_menu")
            ]
        ]

        await query.edit_message_text(escort_text, reply_markup=InlineKeyboardMarkup(keyboard))

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

    async def show_defense_status(self, query, context):
        """Show defense status"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)

        # Calculate defense power
        defense_power = self.combat.calculate_defense_power(user_id)

        defense_text = f"""🛡 وضعیت دفاعی - {player['country_name']}

💪 قدرت دفاع کل: {defense_power:,}

🛡 سیستم‌های دفاعی:
🛡 پدافند S-500: {weapons.get('s500_defense', 0)}
🛡 پدافند THAAD: {weapons.get('thaad_defense', 0)}
🛡 پدافند S-400: {weapons.get('s400_defense', 0)}
🛡 پدافند Iron Dome: {weapons.get('iron_dome', 0)}
🛡 پدافند SLQ-32: {weapons.get('slq32_ew', 0)}
🛡 توپخانه Phalanx: {weapons.get('phalanx_ciws', 0)}

💡 سیستم‌های دفاعی از کشور شما در برابر حملات محافظت می‌کنند."""

        keyboard = self.keyboards.back_to_military_keyboard()
        await query.edit_message_text(defense_text, reply_markup=keyboard)

    async def show_military_power(self, query, context):
        """Show military power calculation"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        weapons = self.db.get_player_weapons(user_id)

        # Calculate total military power
        total_power = self.combat.calculate_military_power(user_id)

        power_text = f"""⚔️ قدرت نظامی - {player['country_name']}

👥 جمعیت: {player['population']:,}
⚔️سربازان: {player['soldiers']:,}
💪 قدرت کل: {total_power:,}

🔫 تسلیحات:
🚀 موشک: {weapons.get('missile', 0)}
🚢 کشتی جنگی: {weapons.get('warship', 0)}
🛡 پدافند S-500: {weapons.get('s500_defense', 0)}
🛡 پدافند THAAD: {weapons.get('thaad_defense', 0)}
🛡 پدافند S-400: {weapons.get('s400_defense', 0)}"""

        keyboard = self.keyboards.back_to_military_keyboard()
        await query.edit_message_text(power_text, reply_markup=keyboard)

    async def show_alliance_invite_menu(self, query, context):
        """Show alliance invite menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        alliance = self.alliance.get_player_alliance(user_id)

        if not alliance or alliance['role'] not in ['leader', 'officer']:
            await query.edit_message_text("❌ شما اجازه دعوت کردن ندارید!")
            return

        invite_text = f"""🤝 دعوت به اتحاد - {alliance['alliance_name']}

لطفاً ID کاربری کشوری که می‌خواهید دعوت کنید را ارسال کنید."""

        await query.edit_message_text(invite_text)
        context.user_data['awaiting_alliance_invite'] = True

    async def show_alliance_members(self, query, context):
        """Show alliance members"""
        user_id = query.from_user.id
        alliance = self.alliance.get_player_alliance(user_id)

        if not alliance:
            await query.edit_message_text("❌ شما عضو هیچ اتحادی نیستید!")
            return

        members = self.alliance.get_alliance_members(alliance['alliance_id'])

        members_text = f"""👥 اعضای اتحاد - {alliance['alliance_name']}

"""

        for member in members:
            role_emoji = "👑" if member['role'] == 'leader' else "⭐" if member['role'] == 'officer' else "👤"
            members_text += f"{role_emoji} {member['country_name']} ({member['role']})\n"

        keyboard = self.keyboards.back_to_alliance_keyboard()
        await query.edit_message_text(members_text, reply_markup=keyboard)

    async def show_alliance_invitations(self, query, context):
        """Show pending alliance invitations"""
        user_id = query.from_user.id
        invitations = self.alliance.get_pending_invitations(user_id)

        if not invitations:
            await query.edit_message_text("📭 شما هیچ دعوت‌نامه‌ای ندارید!")
            return

        invite_text = "📬 دعوت‌نامه‌های شما:\n\n"

        for invite in invitations:
            invite_text += f"🏛 {invite['alliance_name']}\n"
            invite_text += f"📨 از: {invite['inviter_country']}\n\n"

        keyboard = self.keyboards.back_to_alliance_keyboard()
        await query.edit_message_text(invite_text, reply_markup=keyboard)

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
        elif action == "history":
            await self.show_purchase_history(query, context)
        elif action.startswith("cat_"):
            category = action.replace("cat_", "")
            await self.show_market_listings(query, context, category)
        elif action.startswith("sell_resource_") or action.startswith("sell_weapon_"):
            await self.handle_sell_item_dialog(query, context, action)
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

                # Calculate delivery success chance
                delivery_chance = min(max(security_level + 30, 70), 95)

                if delivery_chance >= 90:
                    delivery_status = "🟢 بالا"
                elif delivery_chance >= 80:
                    delivery_status = "🟡 متوسط"
                else:
                    delivery_status = "🔴 پایین"

                menu_text += f"""
{item_emoji} {item_type} x{quantity:,}
💰 ${price_per_unit:,} واحد (کل: ${total_price:,})
فروشنده: {seller_country}
🛡 امنیت: {security_level}% | شانس تحویل: {delivery_status} ({delivery_chance}%)"""

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

    async def show_purchase_history(self, query, context):
        """Show user's purchase history"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        transactions = self.marketplace.get_buyer_transactions(user_id, 10)

        if not transactions:
            await query.edit_message_text(
                f"""📊 تاریخچه خرید - {player['country_name']}

❌ شما هنوز هیچ خریدی انجام نداده‌اید!

💡 از بخش "خرید کالا" اولین خرید خود را انجام دهید.""",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="marketplace")]])
            )
            return

        menu_text = f"""📊 تاریخچه خرید - {player['country_name']}

💰 پول شما: ${player['money']:,}

📦 آخرین خریدهای شما:"""

        for transaction in transactions:
            status_emoji = {
                'delivered': '✅', 
                'failed': '❌', 
                'pending': '⏳'
            }.get(transaction['status'], '❓')

            status_text = {
                'delivered': 'تحویل شد',
                'failed': 'ناموفق',
                'pending': 'در انتظار'
            }.get(transaction['status'], 'نامشخص')

            item_emoji = '📦'
            if transaction['item_type'] in ['rifle', 'tank', 'fighter_jet', 'drone', 'missile', 'warship']:
                item_emoji = {
                    'rifle': '🔫', 'tank': '🚗', 'fighter_jet': '✈️',
                    'drone': '🚁', 'missile': '🚀', 'warship': '🚢'
                }.get(transaction['item_type'], '⚔️')

            menu_text += f"""

{status_emoji} {item_emoji} {transaction['item_type']} x{transaction['quantity']:,}
💰 ${transaction['total_paid']:,} از {transaction['seller_country']}
📅 {transaction['transaction_date'][:16]} - {status_text}"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="marketplace")]]
        await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard))

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

    async def handle_alliance_invite(self, query, context):
        """Handle alliance invitation"""
        user_id = query.from_user.id

        # Check if player has alliance and can invite
        alliance = self.alliance.get_player_alliance(user_id)
        if not alliance:
            await query.edit_message_text("❌ شما عضو هیچ اتحادی نیستید!")
            return

        if alliance['role'] not in ['leader', 'officer']:
            await query.edit_message_text("❌ شما اجازه دعوت کردن ندارید!")
            return

        # Get all countries to invite
        all_players = self.db.get_all_players()
        available_players = [p for p in all_players if p['user_id'] != user_id]

        if not available_players:
            await query.edit_message_text("❌ هیچ کشور دیگری برای دعوت یافت نشد!")
            return

        # Create keyboard with countries
        keyboard = []
        for player in available_players[:20]:  # Limit to 20 players
            flag = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳')
            button = InlineKeyboardButton(
                f"{flag} {player['country_name']}",
                callback_data=f"alliance_invite_{player['user_id']}"
            )
            keyboard.append([button])

        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="alliances")])

        await query.edit_message_text(
            "👥 انتخاب کشور برای دعوت:\n\n"
            "کشوری را که می‌خواهید به اتحاد دعوت کنید انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def process_alliance_invitation(self, query, context, target_id):
        """Process alliance invitation to specific player"""
        user_id = query.from_user.id

        result = self.alliance.invite_to_alliance(user_id, target_id)

        await query.edit_message_text(
            f"{'✅' if result['success'] else '❌'} {result['message']}",
            reply_markup=self.keyboards.back_to_diplomacy_keyboard()
        )

    async def handle_alliance_leave(self, query, context):
        """Handle leaving alliance"""
        user_id = query.from_user.id

        result = self.alliance.leave_alliance(user_id)

        await query.edit_message_text(
            f"{'✅' if result['success'] else '❌'} {result['message']}",
            reply_markup=self.keyboards.back_to_diplomacy_keyboard()
        )

    async def handle_invitation_response(self, query, context, response):
        """Handle alliance invitation response"""
        user_id = query.from_user.id
        invitation_id = int(query.data.replace(f"{response}_inv_", ""))

        result = self.alliance.respond_to_invitation(user_id, invitation_id, response)
        await query.edit_message_text(f"{'✅' if result['success'] else '❌'} {result['message']}")

    async def show_income_report(self, query, context):
        """Show detailed income report"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)

        if not player:
            await query.edit_message_text("❌ بازیکن یافت نشد!")
            return

        report = self.economy.get_income_report(user_id)
        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(report, reply_markup=keyboard)

    async def show_convoy_interception_menu(self, query, context):
        """Show convoy interception menu"""
        user_id = query.from_user.id
        active_convoys = self.convoy.get_active_convoys()

        if not active_convoys:
            menu_text = "❌ هیچ محموله‌ای در حال حرکت نیست!"
            keyboard = self.keyboards.back_to_main_keyboard()
            await query.edit_message_text(menu_text, reply_markup=keyboard)
            return

        menu_text = "🚚 محموله‌های در حال حرکت:\n\n"

        for convoy in active_convoys:
            if convoy['sender_id'] != user_id and convoy['receiver_id'] != user_id:
                menu_text += f"🆔 {convoy['id']} - از {convoy['sender_country']} به {convoy['receiver_country']}\n"
                menu_text += f"🛡 امنیت: {convoy['security_level']}%\n\n"

        keyboard = self.keyboards.back_to_main_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)

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

            if result['success'] and result.get('is_first_purchase', False):
                # Send convoy news only for first purchases
                try:
                    await self.news.send_marketplace_purchase(result)
                except:
                    pass  # Don't fail purchase if news fails

            # Add back button
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="marketplace")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"{'✅' if result['success'] else '❌'} {result['message']}",
                reply_markup=reply_markup
            )

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

                # Add sell buttons for each resource
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = []
                for resource, amount in resources.items():
                    if resource != 'user_id' and amount >= 100:
                        resource_config = Config.RESOURCES.get(resource, {})
                        resource_name = resource_config.get('name', resource)
                        resource_emoji = resource_config.get('emoji', '📦')
                        keyboard.append([InlineKeyboardButton(
                            f"💰 فروش {resource_emoji} {resource_name}",
                            callback_data=f"sell_resource_{resource}"
                        )])

                keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="market_sell")])
                await query.edit_message_text(items_text, reply_markup=InlineKeyboardMarkup(keyboard))
                return
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

                # Add sell buttons for each weapon
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = []
                for weapon, amount in weapons.items():
                    if weapon != 'user_id' and amount >= 1:
                        weapon_emoji = {
                            'rifle': '🔫', 'tank': '🚗', 'fighter_jet': '✈️',
                            'drone': '🚁', 'missile': '🚀', 'warship': '🚢'
                        }.get(weapon, '⚔️')
                        keyboard.append([InlineKeyboardButton(
                            f"💰 فروش {weapon_emoji} {weapon}",
                            callback_data=f"sell_weapon_{weapon}"
                        )])

                keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="marketplace")])
                await query.edit_message_text(items_text, reply_markup=InlineKeyboardMarkup(keyboard))
                return
            else:
                items_text += "\n❌ تسلیحات کافی for sale ندارید!"

        await query.edit_message_text(items_text)

    async def handle_sell_item_dialog(self, query, context, action):
        """Handle sell item dialog to get quantity and price"""
        user_id = query.from_user.id

        if action.startswith("sell_resource_"):
            item_type = action.replace("sell_resource_", "")
            item_category = "resources"
            resources = self.db.get_player_resources(user_id)
            available_amount = resources.get(item_type, 0)

            from config import Config
            resource_config = Config.RESOURCES.get(item_type, {})
            item_name = resource_config.get('name', item_type)
            item_emoji = resource_config.get('emoji', '📦')
            suggested_price = resource_config.get('market_value', 10)

        elif action.startswith("sell_weapon_"):
            item_type = action.replace("sell_weapon_", "")
            item_category = "weapons"
            weapons = self.db.get_player_weapons(user_id)
            available_amount = weapons.get(item_type, 0)

            weapon_emojis = {
                'rifle': '🔫', 'tank': '🚗', 'fighter_jet': '✈️',
                'drone': '🚁', 'missile': '🚀', 'warship': '🚢'
            }
            item_emoji = weapon_emojis.get(item_type, '⚔️')
            item_name = item_type.replace('_', ' ').title()
            suggested_price = {'rifle': 50, 'tank': 5000, 'fighter_jet': 25000,
                             'drone': 15000, 'missile': 10000, 'warship': 50000}.get(item_type, 1000)

        if available_amount <= 0:
            await query.edit_message_text("❌ این آیتم در موجودی شما نیست!")
            return

        # Show sell dialog with preset options
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        dialog_text = f"""💰 فروش {item_emoji} {item_name}

📦 موجودی شما: {available_amount:,}
💵 قیمت پیشنهادی: ${suggested_price:,}

🔢 مقدار فروش را انتخاب کنید:"""

        keyboard = []

        # Add quantity options
        quantities = []
        if available_amount >= 100:
            quantities.append(100)
        if available_amount >= 500:
            quantities.append(500)
        if available_amount >= 1000:
            quantities.append(1000)
        if available_amount >= 5000:
            quantities.append(5000)

        # Add half and all options
        if available_amount > 10:
            quantities.append(available_amount // 2)  # Half
        quantities.append(available_amount)  # All

        # Remove duplicates and sort
        quantities = sorted(list(set(quantities)))

        for qty in quantities[:6]:  # Max 6 options
            callback_data = f"confirm_sell_{item_category}_{item_type}_{qty}_{suggested_price}"
            keyboard.append([InlineKeyboardButton(
                f"{qty:,} عدد (${qty * suggested_price:,})",
                callback_data=callback_data
            )])

        # Add manual input button
        keyboard.append([InlineKeyboardButton("✏️ مقدار و قیمت دستی", callback_data=f"manual_sell_{item_category}_{item_type}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="market_sell")])

        await query.edit_message_text(dialog_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_confirm_sell(self, query, context):
        """Handle sell confirmation"""
        user_id = query.from_user.id
        data_parts = query.data.replace("confirm_sell_", "").split("_")

        if len(data_parts) < 4:
            await query.edit_message_text("❌ داده‌های فروش نامعتبر!")
            return

        item_category = data_parts[0]
        item_type = data_parts[1]
        quantity = int(data_parts[2])
        price_per_unit = int(data_parts[3])

        # Create listing
        result = self.marketplace.create_listing(user_id, item_type, item_category, quantity, price_per_unit)

        if result['success']:
            total_value = quantity * price_per_unit
            success_text = f"""✅ آگهی فروش ثبت شد!

📦 آیتم: {item_type}
🔢 مقدار: {quantity:,}
💰 قیمت واحد: ${price_per_unit:,}
💵 ارزش کل: ${total_value:,}
🛡 امنیت: {result['security_level']}%

🏪 آگهی شما در بازار قرار گرفت."""
        else:
            success_text = f"❌ {result['message']}"

        # Add back button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="marketplace")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(success_text, reply_markup=reply_markup)

    async def handle_manual_transfer(self, query, context):
        """Handle manual transfer input request"""
        user_id = query.from_user.id
        target_id = int(query.data.replace("manual_transfer_", ""))

        # Store transfer context
        context.user_data['awaiting_manual_transfer'] = True
        context.user_data['transfer_target_id'] = target_id

        player = self.db.get_player(user_id)
        target_player = self.db.get_player(target_id)

        manual_text = f"""✏️ ورود مقدار دستی - انتقال به {target_player['country_name']}

💰 پول شما: ${player['money']:,}

📝 لطفاً مقدار دلخواه خود را به فرمت زیر وارد کنید:

🔹 برای ارسال پول:
money 50000

🔹 برای ارسال منابع:
iron 1000
oil 500
gold 100

شما می‌توانید چندین آیتم را در یک خط جدا
ره وارد کنید:
money 10000
iron 500
oil 300

⚠️ فقط اعداد صحیح استفاده کنید"""

        await query.edit_message_text(manual_text)

    async def handle_manual_sell(self, query, context):
        """Handle manual sell input request"""
        user_id = query.from_user.id
        data_parts = query.data.replace("manual_sell_", "").split("_")

        if len(data_parts) < 2:
            await query.edit_message_text("❌ خطا در پردازش!")
            return

        item_category = data_parts[0]
        item_type = data_parts[1]

        # Store sell context
        context.user_data['awaiting_manual_sell'] = True
        context.user_data['sell_item_category'] = item_category
        context.user_data['sell_item_type'] = item_type

        # Get available amount
        if item_category == "resources":
            resources = self.db.get_player_resources(user_id)
            available_amount = resources.get(item_type, 0)
        else:  # weapons
            weapons = self.db.get_player_weapons(user_id)
            available_amount = weapons.get(item_type, 0)

        manual_text = f"""✏️ ورود مقدار و قیمت دستی

📦 آیتم: {item_type}
📊 موجودی شما: {available_amount:,}

📝 لطفاً مقدار و قیمت دلخواه را به فرمت زیر وارد کنید:

مقدار قیمت_واحد

مثال:
1000 50
(یعنی 1000 عدد به قیمت 50 دلار هر واحد)

⚠️ فقط اعداد صحیح استفاده کنید
⚠️ مقدار نباید بیشتر از موجودی شما باشد"""

        await query.edit_message_text(manual_text)

    async def handle_manual_transfer_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle manual transfer text input"""
        user_id = update.effective_user.id
        message = update.message.text.strip()
        target_id = context.user_data.get('transfer_target_id')

        if not target_id:
            await update.message.reply_text("❌ خطا در پردازش انتقال!")
            context.user_data.pop('awaiting_manual_transfer', None)
            return

        try:
            # Parse input
            lines = message.split('\n')
            transfer_resources = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) != 2:
                    await update.message.reply_text("❌ فرمت نادرست! استفاده کنید: آیتم مقدار")
                    return

                resource_type, amount_str = parts
                amount = int(amount_str)

                if amount <= 0:
                    await update.message.reply_text("❌ مقدار باید بیشتر از صفر باشد!")
                    return

                transfer_resources[resource_type] = amount

            if not transfer_resources:
                await update.message.reply_text("❌ هیچ آیتمی برای انتقال مشخص نشده!")
                return

            # Execute transfer
            result = self.convoy.create_convoy(user_id, target_id, transfer_resources)

            if result['success']:
                target_player = self.db.get_player(target_id)
                convoy_message = f"🚛 محموله جدید آماده ارسال!\n\n📦 مقصد: {target_player['country_name']}\n⏱ زمان تحویل: {result['travel_time']} دقیقه\n🛡 امنیت: {result['security_level']}%"

                # Send convoy news
                await self.news.send_convoy_news(convoy_message, None, transfer_resources)

                await update.message.reply_text(f"✅ محموله با موفقیت ارسال شد!\n{convoy_message}")
            else:
                await update.message.reply_text(f"❌ {result['message']}")

        except ValueError:
            await update.message.reply_text("❌ لطفاً فقط اعداد صحیح وارد کنید!")
        except Exception as e:
            logger.error(f"Error in manual transfer: {e}")
            await update.message.reply_text("❌ خطایی در انتقال رخ داد!")

        # Clear state
        context.user_data.pop('awaiting_manual_transfer', None)
        context.user_data.pop('transfer_target_id', None)

        # Show main menu
        await asyncio.sleep(1)
        await self.show_main_menu(update, context)

    async def handle_manual_sell_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle manual sell text input"""
        user_id = update.effective_user.id
        message = update.message.text.strip()
        item_category = context.user_data.get('sell_item_category')
        item_type = context.user_data.get('sell_item_type')

        if not item_category or not item_type:
            await update.message.reply_text("❌ خطا در پردازش فروش!")
            context.user_data.pop('awaiting_manual_sell', None)
            return

        try:
            parts = message.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ فرمت نادرست! استفاده کنید: مقدار قیمت_واحد")
                return

            quantity = int(parts[0])
            price_per_unit = int(parts[1])

            if quantity <= 0 or price_per_unit <= 0:
                await update.message.reply_text("❌ مقدار و قیمت باید بیشتر از صفر باشد!")
                return

            # Create listing
            result = self.marketplace.create_listing(user_id, item_type, item_category, quantity, price_per_unit)

            if result['success']:
                total_value = quantity * price_per_unit
                success_text = f"""✅ آگهی فروش ثبت شد!

📦 آیتم: {item_type}
🔢 مقدار: {quantity:,}
💰 قیمت واحد: ${price_per_unit:,}
💵 ارزش کل: ${total_value:,}
🛡 امنیت: {result['security_level']}%

🏪 آگهی شما در بازار قرار گرفت."""
                await update.message.reply_text(success_text)
            else:
                await update.message.reply_text(f"❌ {result['message']}")

        except ValueError:
            await update.message.reply_text("❌ لطفاً فقط اعداد صحیح وارد کنید!")
        except Exception as e:
            logger.error(f"Error in manual sell: {e}")
            await update.message.reply_text("❌ خطایی در فروش رخ داد!")

        # Clear state
        context.user_data.pop('awaiting_manual_sell', None)
        context.user_data.pop('sell_item_category', None)
        context.user_data.pop('sell_item_type', None)

        # Show main menu
        await asyncio.sleep(1)
        await self.show_main_menu(update, context)

    async def handle_remove_listing(self, query, context):
        """Handle removing marketplace listing"""
        user_id = query.from_user.id
        listing_id = int(query.data.replace("remove_", ""))

        result = self.marketplace.cancel_listing(user_id, listing_id)

        # Add back button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="marketplace")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"{'✅' if result['success'] else '❌'} {result['message']}",
            reply_markup=reply_markup
        )

    async def handle_official_statement(self, query, context):
        """Handle official statement"""
        await query.edit_message_text(
            "📢 بیانیه رسمی\n\n"
            "لطفاً متن بیانیه رسمی خود را ارسال کنید:",
            reply_markup=self.keyboards.back_to_main_keyboard()
        )

        context.user_data['awaiting_official_statement'] = True

    async def handle_official_statement_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle official statement text input"""
        user_id = update.effective_user.id
        statement_text = update.message.text

        if len(statement_text) > 1000:
            await update.message.reply_text("❌ متن بیانیه نباید بیشتر از 1000 کاراکتر باشد!")
            return

        # Send statement to news channel
        player = self.db.get_player(user_id)
        if player:
            country_flag = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳')
            statement_message = f"""📢 بیانیه رسمی

{country_flag} <b>{player['country_name']}</b>

📝 متن بیانیه:
{statement_text}"""

            await self.news.send_text_message(statement_message)

            is_admin = self.admin.is_admin(user_id)
            await update.message.reply_text(
                "✅ بیانیه شما با موفقیت منتشر شد!",
                reply_markup=self.keyboards.main_menu_keyboard(is_admin)
            )


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if not update.effective_user:
            return
        user_id = update.effective_user.id

        # Handle manual transfer input
        if context.user_data.get('awaiting_manual_transfer'):
            await self.handle_manual_transfer_input(update, context)
            context.user_data.pop('awaiting_manual_transfer', None)
            return

        # Handle official statement
        if context.user_data.get('awaiting_official_statement'):
            await self.handle_official_statement_text(update, context)
            context.user_data.pop('awaiting_official_statement', None)
            return

        # Handle manual sell input
        if context.user_data.get('awaiting_manual_sell'):
            await self.handle_manual_sell_input(update, context)
            context.user_data.pop('awaiting_manual_sell', None)
            return

        # Handle alliance name input
        if context.user_data.get('awaiting_alliance_name'):
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
        else:
            # Default message for unhandled text
            await update.message.reply_text("Use commands like /start or buttons to interact.")


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

    async def process_convoy_arrivals(self):
        """Process convoy arrivals that are due"""
        try:
            results = self.convoy.process_convoy_arrivals()

            for result in results:
                # Send news about convoy delivery
                convoy = self.db.get_convoy(result['convoy_id'])
                if convoy:
                    sender = self.db.get_player(convoy['sender_id'])
                    receiver = self.db.get_player(convoy['receiver_id'])

                    if result['success']:
                        message = f"📦 محموله از {sender['country_name']} به {receiver['country_name']} تحویل شد!"
                        await self.news.send_convoy_news(message, None, result.get('resources', {}))
                    else:
                        message = f"💀 محموله از {sender['country_name']} به {receiver['country_name']} دزدیده شد!"
                        await self.news.send_convoy_news(message, None, result.get('resources_lost', {}))

        except Exception as e:
            logger.error(f"Error processing convoy arrivals: {e}")

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

        # Process convoy arrivals every minute
        self.scheduler.add_job(
            func=self.process_convoy_arrivals,
            trigger=IntervalTrigger(minutes=1),
            id='convoy_arrivals',
            name='Process convoy arrivals',
            replace_existing=True
        )

        logger.info("Scheduler configured - 6-hour income cycle, pending attacks, and convoy arrivals active")

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