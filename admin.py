import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from keyboards import Keyboards

logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self, database):
        self.db = database
        self.keyboards = Keyboards()
        # List of admin user IDs - add your admin IDs here
        self.admin_ids = [123456789]  # Replace with actual admin user IDs
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    async def handle_admin_action(self, query, context):
        """Handle admin panel actions"""
        user_id = query.from_user.id
        
        if not self.is_admin(user_id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        data = query.data.replace("admin_", "")
        
        if data == "panel":
            await self.show_admin_panel(query, context)
        elif data == "stats":
            await self.show_game_stats(query, context)
        elif data == "players":
            await self.show_players_management(query, context)
        elif data == "logs":
            await self.show_admin_logs(query, context)
        elif data == "reset":
            await self.show_reset_confirmation(query, context)
        elif data == "reset_confirm":
            await self.reset_game_data(query, context)
        elif data.startswith("player_"):
            await self.show_player_management(query, context, data)
        elif data.startswith("delete_player_"):
            await self.delete_player(query, context, data)
        else:
            await query.edit_message_text("❌ دستور ادمین نامعتبر!")
    
    async def show_admin_panel(self, query, context):
        """Show main admin panel"""
        admin_text = """👑 پنل مدیریت DragonRP

🎮 سیستم مدیریت کامل بازی

انتخاب کنید:"""
        
        keyboard = self.keyboards.admin_panel_keyboard()
        await query.edit_message_text(admin_text, reply_markup=keyboard)
    
    async def show_game_stats(self, query, context):
        """Show game statistics"""
        players = self.db.get_all_players()
        total_players = len(players)
        
        total_money = sum(player['money'] for player in players)
        total_population = sum(player['population'] for player in players)
        total_soldiers = sum(player['soldiers'] for player in players)
        
        # Get most powerful country
        max_money_player = max(players, key=lambda x: x['money']) if players else None
        max_pop_player = max(players, key=lambda x: x['population']) if players else None
        
        stats_text = f"""📊 آمار کلی بازی

👥 تعداد بازیکنان: {total_players}
💰 کل پول: ${total_money:,}
🌍 کل جمعیت: {total_population:,}
⚔️ کل سربازان: {total_soldiers:,}

🏆 ثروتمندترین کشور: {max_money_player['country_name'] if max_money_player else 'ندارد'}
👑 پرجمعیت‌ترین کشور: {max_pop_player['country_name'] if max_pop_player else 'ندارد'}

📈 وضعیت سرور: ✅ فعال
🕐 آخرین آپدیت: اکنون"""
        
        keyboard = [[
            {"text": "🔄 بروزرسانی", "callback_data": "admin_stats"},
            {"text": "🔙 بازگشت", "callback_data": "admin_panel"}
        ]]
        
        await query.edit_message_text(stats_text, reply_markup=keyboard)
    
    async def show_players_management(self, query, context):
        """Show players management"""
        players = self.db.get_all_players()
        
        if not players:
            await query.edit_message_text(
                "👥 هیچ بازیکنی در بازی نیست!",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )
            return
        
        players_text = "👥 مدیریت بازیکنان\n\n"
        
        for player in players[:15]:  # Show first 15 players
            players_text += f"🏴 {player['country_name']}\n"
            players_text += f"👤 {player['username']}\n"
            players_text += f"💰 ${player['money']:,}\n"
            players_text += f"👥 {player['population']:,}\n"
            players_text += f"⚔️ {player['soldiers']:,}\n\n"
        
        keyboard = self.keyboards.admin_players_keyboard(players)
        await query.edit_message_text(players_text, reply_markup=keyboard)
    
    async def show_player_management(self, query, context, data):
        """Show specific player management"""
        user_id = int(data.replace("player_", ""))
        player = self.db.get_player(user_id)
        
        if not player:
            await query.edit_message_text("❌ بازیکن یافت نشد!")
            return
        
        resources = self.db.get_player_resources(user_id)
        buildings = self.db.get_player_buildings(user_id)
        weapons = self.db.get_player_weapons(user_id)
        
        player_text = f"""👤 مدیریت بازیکن
🏴 کشور: {player['country_name']}
👤 نام: {player['username']}

💰 پول: ${player['money']:,}
👥 جمعیت: {player['population']:,}
⚔️ سربازان: {player['soldiers']:,}

📊 منابع اصلی:
🔩 آهن: {resources.get('iron', 0):,}
🥉 مس: {resources.get('copper', 0):,}
🛢 نفت: {resources.get('oil', 0):,}
🏆 طلا: {resources.get('gold', 0):,}

🏗 ساختمان‌های کلیدی:
⛏ معادن: {sum(v for k, v in buildings.items() if 'mine' in k)}
🏭 کارخانه‌ها: {buildings.get('weapon_factory', 0)}
🪖 پادگان: {buildings.get('military_base', 0)}

🔫 تسلیحات کلیدی:
🔫 تفنگ: {weapons.get('rifle', 0)}
🚗 تانک: {weapons.get('tank', 0)}
✈️ جنگنده: {weapons.get('fighter_jet', 0)}"""
        
        keyboard = self.keyboards.admin_player_actions_keyboard(user_id)
        await query.edit_message_text(player_text, reply_markup=keyboard)
    
    async def delete_player(self, query, context, data):
        """Delete a player"""
        user_id = int(data.replace("delete_player_", ""))
        player = self.db.get_player(user_id)
        
        if not player:
            await query.edit_message_text("❌ بازیکن یافت نشد!")
            return
        
        # Delete player
        success = self.db.delete_player(user_id)
        
        if success:
            # Log admin action
            admin_id = query.from_user.id
            self.db.log_admin_action(
                admin_id, 
                "DELETE_PLAYER", 
                user_id, 
                f"Deleted player {player['country_name']}"
            )
            
            await query.edit_message_text(
                f"✅ بازیکن {player['country_name']} حذف شد!",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )
        else:
            await query.edit_message_text("❌ خطا در حذف بازیکن!")
    
    async def show_admin_logs(self, query, context):
        """Show admin logs"""
        logs = self.db.get_admin_logs(20)
        
        if not logs:
            await query.edit_message_text(
                "📝 هیچ لاگ ادمینی موجود نیست!",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )
            return
        
        logs_text = "📝 لاگ‌های ادمین (20 آخرین)\n\n"
        
        for log in logs:
            logs_text += f"🕐 {log['created_at']}\n"
            logs_text += f"👤 Admin ID: {log['admin_id']}\n"
            logs_text += f"🔧 Action: {log['action']}\n"
            if log['details']:
                logs_text += f"📋 Details: {log['details']}\n"
            logs_text += "─────────────\n"
        
        keyboard = [[
            {"text": "🔄 بروزرسانی", "callback_data": "admin_logs"},
            {"text": "🔙 بازگشت", "callback_data": "admin_panel"}
        ]]
        
        await query.edit_message_text(logs_text, reply_markup=keyboard)
    
    async def show_reset_confirmation(self, query, context):
        """Show reset confirmation"""
        warning_text = """⚠️ هشدار: ریست کامل بازی

این عمل تمام داده‌های بازی را حذف می‌کند:
• تمام بازیکنان و کشورها
• تمام منابع و ساختمان‌ها
• تمام تسلیحات و جنگ‌ها
• تاریخچه کامل بازی

❗ این عمل قابل برگشت نیست!

آیا مطمئن هستید؟"""
        
        keyboard = [
            [
                {"text": "✅ بله، ریست کن", "callback_data": "admin_reset_confirm"},
                {"text": "❌ انصراف", "callback_data": "admin_panel"}
            ]
        ]
        
        await query.edit_message_text(warning_text, reply_markup=keyboard)
    
    async def reset_game_data(self, query, context):
        """Reset all game data"""
        admin_id = query.from_user.id
        
        # Perform reset
        success = self.db.reset_all_data()
        
        if success:
            # Log admin action
            self.db.log_admin_action(
                admin_id,
                "RESET_GAME",
                None,
                "Complete game reset performed"
            )
            
            await query.edit_message_text(
                "✅ بازی با موفقیت ریست شد!\n\n"
                "تمام داده‌ها حذف شدند و بازی آماده شروع مجدد است.",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )
        else:
            await query.edit_message_text("❌ خطا در ریست بازی!")
    
    def setup_handlers(self, application):
        """Setup admin-specific handlers"""
        # Add any additional admin-specific message handlers here
        pass
    
    async def send_admin_notification(self, message):
        """Send notification to all admins"""
        # This would send a message to all admin users
        # Implementation depends on bot context
        pass
    
    def add_admin(self, user_id):
        """Add new admin"""
        if user_id not in self.admin_ids:
            self.admin_ids.append(user_id)
            return True
        return False
    
    def remove_admin(self, user_id):
        """Remove admin"""
        if user_id in self.admin_ids:
            self.admin_ids.remove(user_id)
            return True
        return False
import logging
from config import Config

logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self, database):
        self.db = database
        self.admin_ids = Config.ADMIN_CONFIG['default_admin_ids']
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    async def handle_admin_action(self, query, context):
        """Handle admin actions"""
        user_id = query.from_user.id
        
        if not self.is_admin(user_id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        action = query.data.replace("admin_", "")
        
        if action == "stats":
            await self.show_game_stats(query)
        elif action == "reset":
            await self.confirm_reset(query)
        elif action == "logs":
            await self.show_admin_logs(query)
        else:
            await query.edit_message_text("❌ دستور ادمین نامعتبر!")
    
    async def show_game_stats(self, query):
        """Show game statistics"""
        players = self.db.get_all_players()
        total_players = len(players)
        
        stats_text = f"""📊 آمار بازی

👥 تعداد بازیکنان: {total_players}
🏛 کشورهای فعال: {total_players}
🌍 کشورهای باقی‌مانده: {len(Config.COUNTRIES) - total_players}

آخرین بازیکنان:"""
        
        for player in players[-5:]:
            stats_text += f"\n• {player['country_name']} - {player['username']}"
        
        await query.edit_message_text(stats_text)
    
    async def show_admin_logs(self, query):
        """Show admin logs"""
        logs = self.db.get_admin_logs(20)
        
        logs_text = "📋 گزارش عملیات ادمین:\n\n"
        
        if not logs:
            logs_text += "هیچ گزارشی موجود نیست."
        else:
            for log in logs:
                logs_text += f"• {log['action']} - {log['created_at']}\n"
        
        await query.edit_message_text(logs_text)
    
    async def confirm_reset(self, query):
        """Confirm game reset"""
        await query.edit_message_text(
            "⚠️ آیا مطمئن هستید که می‌خواهید تمام داده‌های بازی را پاک کنید؟\n"
            "این عمل غیرقابل بازگشت است!"
        )
    
    def setup_handlers(self, application):
        """Setup admin command handlers"""
        pass
