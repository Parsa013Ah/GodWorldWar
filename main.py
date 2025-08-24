import logging
import asyncio
import os
from telegram import Update
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
        await query.answer()
        
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
            elif data.startswith("attack_"):
                await self.handle_attack(query, context)
            elif data == "send_resources":
                await self.show_send_resources_menu(query, context)
            elif data == "official_statement":
                await self.handle_official_statement(query, context)
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
    
    async def handle_attack(self, query, context):
        """Handle attack initiation"""
        user_id = query.from_user.id
        target_country = query.data.replace("attack_", "")
        
        # This would show attack options and handle combat
        # Implementation would be quite complex with range checking, etc.
        await query.edit_message_text("🚧 سیستم حمله در حال توسعه است...")
    
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
        
        menu_text = f"""📬 ارسال منابع - {player['country_name']}

این بخش به زودی فعال می‌شود...

💡 قابلیت‌های آینده:
• ارسال پول به کشورهای دیگر
• ارسال منابع خام
• ارسال تسلیحات
• حمله به کاروان‌ها"""
        
        keyboard = self.keyboards.back_to_main_keyboard()
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
