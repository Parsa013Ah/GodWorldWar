import logging
import asyncio
import os
from telegram import Update, Bot
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
        self.scheduler = AsyncIOScheduler()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        
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
            elif data == "weapons":
                await self.show_weapons_menu(query, context)
            elif data.startswith("build_"):
                await self.handle_building_construction(query, context)
            elif data.startswith("produce_"):
                await self.handle_weapon_production(query, context)
            elif data == "select_attack_target":
                await self.show_attack_targets(query, context)
            elif data == "attack_menu":
                await self.show_attack_targets(query, context)
            elif data.startswith("attack_"):
                await self.handle_attack(query, context)
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
            elif data.startswith("send_to_"):
                await self.handle_resource_transfer_target(query, context)
            elif data.startswith("transfer_"):
                await self.handle_resource_transfer(query, context)
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
⚔️ سربازان: {stats['soldiers']:,}

📊 منابع:
🔩 آهن: {stats['resources'].get('iron', 0):,}
🥉 مس: {stats['resources'].get('copper', 0):,}
🛢 نفت خام: {stats['resources'].get('oil', 0):,}
⛽ گاز: {stats['resources'].get('gas', 0):,}
🔗 آلومینیوم: {stats['resources'].get('aluminum', 0):,}
🏆 طلا: {stats['resources'].get('gold', 0):,}
☢️ اورانیوم: {stats['resources'].get('uranium', 0):,}
🔋 لیتیوم: {stats['resources'].get('lithium', 0):,}
⚫ زغال‌سنگ: {stats['resources'].get('coal', 0):,}
🥈 نقره: {stats['resources'].get('silver', 0):,}

انتخاب کنید:"""
        
        keyboard = self.keyboards.main_menu_keyboard()
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
⚔️ سربازان: {stats['soldiers']:,}

📊 منابع:
🔩 آهن: {stats['resources'].get('iron', 0):,}
🥉 مس: {stats['resources'].get('copper', 0):,}
🛢 نفت خام: {stats['resources'].get('oil', 0):,}
⛽ گاز: {stats['resources'].get('gas', 0):,}
🔗 آلومینیوم: {stats['resources'].get('aluminum', 0):,}
🏆 طلا: {stats['resources'].get('gold', 0):,}
☢️ اورانیوم: {stats['resources'].get('uranium', 0):,}
🔋 لیتیوم: {stats['resources'].get('lithium', 0):,}
⚫ زغال‌سنگ: {stats['resources'].get('coal', 0):,}
🥈 نقره: {stats['resources'].get('silver', 0):,}

انتخاب کنید:"""
        
        keyboard = self.keyboards.main_menu_keyboard()
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

⛏ معادن (تولید منابع):
• معدن آهن - $80,000
• معدن مس - $100,000  
• معدن نفت - $120,000
• معدن گاز - $110,000
• معدن آلومینیوم - $90,000
• معدن طلا - $150,000
• معدن اورانیوم - $200,000
• معدن لیتیوم - $180,000
• معدن زغال‌سنگ - $85,000
• معدن نقره - $140,000

🏭 ساختمان‌های تولیدی:
• کارخانه اسلحه - $150,000
• پالایشگاه نفت - $100,000
• نیروگاه برق - $90,000
• مزرعه گندم - $50,000
• پادگان آموزشی - $50,000
• مسکن (10,000 نفر) - $50,000"""
        
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
⚔️ سربازان: {player['soldiers']:,}

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
        """Show weapon production menu"""
        user_id = query.from_user.id
        player = self.db.get_player(user_id)
        resources = self.db.get_player_resources(user_id)
        
        menu_text = f"""🔫 تولید تسلیحات - {player['country_name']}

💰 پول: ${player['money']:,}

📊 منابع موجود:
🔩 آهن: {resources['iron']:,}
🥉 مس: {resources['copper']:,}
🛢 نفت: {resources['oil']:,}
⛽ گاز: {resources['gas']:,}
🔗 آلومینیوم: {resources['aluminum']:,}
☢️ اورانیوم: {resources['uranium']:,}
🔋 لیتیوم: {resources['lithium']:,}

💡 برای تولید تسلیحات به کارخانه اسلحه نیاز دارید!

🔫 تسلیحات قابل تولید:
• تفنگ - $1,000 + آهن
• تانک - $10,000 + آهن + سوخت
• جنگنده - $25,000 + آلومینیوم + سوخت
• پهپاد - $20,000 + لیتیوم + سوخت
• موشک - $50,000 + اورانیوم + سوخت
• کشتی جنگی - $40,000 + آهن + سوخت
• پدافند هوایی - $30,000 + مس + آهن
• سپر موشکی - $35,000 + اورانیوم + آهن
• سپر سایبری - $20,000 + لیتیوم + مس"""
        
        keyboard = self.keyboards.weapons_menu_keyboard()
        await query.edit_message_text(menu_text, reply_markup=keyboard)
    
    async def handle_weapon_production(self, query, context):
        """Handle weapon production"""
        user_id = query.from_user.id
        weapon_type = query.data.replace("produce_", "")
        
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
    
    async def handle_attack(self, query, context):
        """Handle attack execution"""
        user_id = query.from_user.id
        target_id = int(query.data.replace("attack_", ""))
        
        attacker = self.db.get_player(user_id)
        target = self.db.get_player(target_id)
        
        if not target:
            await query.edit_message_text("❌ کشور هدف یافت نشد!")
            return
        
        # Execute attack
        result = self.combat.execute_attack(user_id, target_id)
        
        if not result['success'] and 'message' in result:
            await query.edit_message_text(f"❌ {result['message']}")
            return
        
        # Format battle report
        battle_report = self.combat.format_battle_report(result)
        
        await query.edit_message_text(battle_report)
        
        # Send news to channel
        await self.news.send_war_report(result)
    
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
        
        all_countries = self.db.get_all_countries()
        other_countries = [c for c in all_countries if c['user_id'] != user_id]
        
        if not other_countries:
            await query.edit_message_text("❌ هیچ کشور دیگری برای ارسال منابع یافت نشد!")
            return
        
        menu_text = f"""📬 ارسال منابع - {player['country_name']}

💰 پول شما: ${player['money']:,}

📊 منابع موجود:
🔩 آهن: {resources.get('iron', 0):,}
🥉 مس: {resources.get('copper', 0):,}
🛢 نفت: {resources.get('oil', 0):,}
⛽ گاز: {resources.get('gas', 0):,}
🔗 آلومینیوم: {resources.get('aluminum', 0):,}
🏆 طلا: {resources.get('gold', 0):,}

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

⚔️ سربازان دفاعی: {player['soldiers']:,}

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

⚔️ سربازان: {player['soldiers']:,} × 1 = {player['soldiers']:,}
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
        """Handle actual resource transfer"""
        user_id = query.from_user.id
        data_parts = query.data.replace("transfer_", "").split("_")
        target_id = int(data_parts[0])
        transfer_type = "_".join(data_parts[1:])
        
        player = self.db.get_player(user_id)
        target = self.db.get_player(target_id)
        
        success = False
        transfer_description = ""
        
        if transfer_type == "money_10k":
            if player['money'] >= 10000:
                self.db.update_player_money(user_id, player['money'] - 10000)
                self.db.update_player_money(target_id, target['money'] + 10000)
                transfer_description = "10,000 دلار"
                success = True
        elif transfer_type == "money_50k":
            if player['money'] >= 50000:
                self.db.update_player_money(user_id, player['money'] - 50000)
                self.db.update_player_money(target_id, target['money'] + 50000)
                transfer_description = "50,000 دلار"
                success = True
        elif transfer_type.endswith("_1k"):
            resource_type = transfer_type.replace("_1k", "")
            resources = self.db.get_player_resources(user_id)
            if resources.get(resource_type, 0) >= 1000:
                self.db.consume_resources(user_id, {resource_type: 1000})
                self.db.add_resources(target_id, resource_type, 1000)
                resource_config = Config.RESOURCES.get(resource_type, {})
                resource_name = resource_config.get('name', resource_type)
                transfer_description = f"1,000 {resource_name}"
                success = True
        
        if success:
            await query.edit_message_text(
                f"✅ انتقال موفق!\n\n"
                f"📤 {transfer_description} به {target['country_name']} ارسال شد."
            )
            
            # Send news to channel
            await self.news.send_resource_transfer(
                player['country_name'], 
                target['country_name'], 
                {transfer_type: transfer_description},
                "فوری"
            )
        else:
            await query.edit_message_text("❌ منابع کافی برای این انتقال ندارید!")

    async def show_propose_peace(self, query, context):
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
        logger.info("Scheduler configured - 6-hour income cycle active")
    
    async def start_scheduler(self):
        """Start the scheduler within async context"""
        self.scheduler.start()
        logger.info("Scheduler started")
    
    async def post_init(self, application):
        """Post initialization hook"""
        await self.start_scheduler()
    
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
