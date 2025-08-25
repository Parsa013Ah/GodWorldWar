import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from keyboards import Keyboards
from config import Config

logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self, database):
        self.db = database
        self.keyboards = Keyboards()
        # List of admin user IDs - add your admin IDs here
        # Add the user ID for @PO0AH013
        self.admin_ids = [5283015101]  # Your actual admin user ID
    
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
        elif data.startswith("penalty_"):
            await self.handle_penalty_country(query, context, data)
        elif data.startswith("reset_country_"):
            await self.reset_country(query, context, data)
        elif data.startswith("confirm_reset_"):
            user_id = int(data.replace("confirm_reset_", ""))
            await self.confirm_country_reset(query, context, user_id)
        elif data == "country_reset":
            await self.show_country_reset_menu(query, context)
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
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_stats"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
            ]
        ])
        
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
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_logs"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
            ]
        ])
        
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
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ بله، ریست کن", callback_data="admin_reset_confirm"),
                InlineKeyboardButton("❌ انصراف", callback_data="admin_panel")
            ]
        ])
        
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
    
    def give_resources_to_player(self, user_id, resource_type, amount):
        """Give resources to a player"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد'}
        
        # Add resources
        self.db.add_resources(user_id, resource_type, amount)
        
        resource_config = Config.RESOURCES.get(resource_type, {})
        resource_name = resource_config.get('name', resource_type)
        
        return {
            'success': True,
            'message': f"{amount:,} {resource_name} به {player['country_name']} اضافه شد"
        }
    
    def give_weapons_to_player(self, user_id, weapon_type, amount):
        """Give weapons to a player"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد'}
        
        # Add weapons
        self.db.add_weapon(user_id, weapon_type, amount)
        
        weapon_config = Config.WEAPONS.get(weapon_type, {})
        weapon_name = weapon_config.get('name', weapon_type)
        
        return {
            'success': True,
            'message': f"{amount:,} {weapon_name} به {player['country_name']} اضافه شد"
        }
    
    def give_money_to_player(self, user_id, amount):
        """Give money to a player"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد'}
        
        # Add money
        new_money = player['money'] + amount
        self.db.update_player_money(user_id, new_money)
        
        return {
            'success': True,
            'message': f"${amount:,} به {player['country_name']} اضافه شد"
        }
    
    def give_population_to_player(self, user_id, amount):
        """Give population to a player"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد'}
        
        new_population = player['population'] + amount
        self.db.update_player_population(user_id, new_population)
        
        return {
            'success': True,
            'message': f"{amount:,} نفر جمعیت به {player['country_name']} اضافه شد"
        }
    
    def give_soldiers_to_player(self, user_id, amount):
        """Give soldiers to a player"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد'}
        
        new_soldiers = player['soldiers'] + amount
        self.db.update_player_soldiers(user_id, new_soldiers)
        
        return {
            'success': True,
            'message': f"{amount:,} سرباز به {player['country_name']} اضافه شد"
        }
    
    def give_buildings_to_player(self, user_id, building_type, amount):
        """Give buildings to a player"""
        player = self.db.get_player(user_id)
        if not player:
            return {'success': False, 'message': 'بازیکن یافت نشد'}
        
        # Add buildings
        for _ in range(amount):
            self.db.add_building(user_id, building_type)
        
        building_config = Config.BUILDINGS.get(building_type, {})
        building_name = building_config.get('name', building_type)
        
        return {
            'success': True,
            'message': f"{amount:,} {building_name} به {player['country_name']} اضافه شد"
        }
    
    async def handle_penalty_country(self, query, context, data):
        """Handle country penalty - halve all resources"""
        country_name = data.replace("penalty_", "")
        
        # Find player by country name
        players = self.db.get_all_players()
        target_player = None
        for player in players:
            if player['country_name'] == country_name:
                target_player = player
                break
        
        if not target_player:
            await query.edit_message_text(f"❌ کشور {country_name} یافت نشد!")
            return
        
        user_id = target_player['user_id']
        
        # Halve money
        new_money = target_player['money'] // 2
        self.db.update_player_money(user_id, new_money)
        
        # Halve population and soldiers
        new_population = target_player['population'] // 2
        new_soldiers = target_player['soldiers'] // 2
        self.db.update_player_population(user_id, new_population)
        self.db.update_player_soldiers(user_id, new_soldiers)
        
        # Halve all resources
        resources = self.db.get_player_resources(user_id)
        for resource, amount in resources.items():
            if resource != 'user_id' and amount > 0:
                new_amount = amount // 2
                self.db.update_resource(user_id, resource, new_amount)
        
        # Halve all weapons
        weapons = self.db.get_player_weapons(user_id)
        for weapon, amount in weapons.items():
            if weapon != 'user_id' and amount > 0:
                new_amount = amount // 2
                self.db.update_weapon_count(user_id, weapon, new_amount)
        
        # Halve all buildings
        buildings = self.db.get_player_buildings(user_id)
        for building, amount in buildings.items():
            if amount > 0:
                new_amount = amount // 2
                self.db.update_building_count(user_id, building, new_amount)
        
        # Log admin action
        admin_id = query.from_user.id
        self.db.log_admin_action(
            admin_id,
            "PENALTY_COUNTRY",
            user_id,
            f"Penalized country {country_name} - halved all resources"
        )
        
        await query.edit_message_text(f"⚠️ کشور {country_name} جریمه شد!\n\nتمام منابع، تسلیحات و ساختمان‌های این کشور نصف شدند.")
    
    async def show_country_reset_menu(self, query, context):
        """Show menu to select country for reset"""
        players = self.db.get_all_players()
        
        if not players:
            await query.edit_message_text(
                "👥 هیچ کشوری برای ریست موجود نیست!",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )
            return
        
        reset_text = "🔄 انتخاب کشور برای ریست\n\nکشور مورد نظر را انتخاب کنید:"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []
        
        for player in players[:10]:  # Show first 10 countries
            keyboard.append([InlineKeyboardButton(
                f"🏴 {player['country_name']}",
                callback_data=f"admin_reset_country_{player['user_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")])
        
        await query.edit_message_text(reset_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def reset_country(self, query, context, data):
        """Reset a specific country"""
        user_id = int(data.replace("reset_country_", ""))
        player = self.db.get_player(user_id)
        
        if not player:
            await query.edit_message_text("❌ کشور یافت نشد!")
            return
        
        # Show confirmation
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ بله، ریست کن", callback_data=f"admin_confirm_reset_{user_id}"),
                InlineKeyboardButton("❌ انصراف", callback_data="admin_country_reset")
            ]
        ])
        
        warning_text = f"""⚠️ تأیید ریست کشور

🏴 کشور: {player['country_name']}
👤 بازیکن: {player['username']}

❗ این عمل کشور را به حالت اولیه بازگرداند:
• پول: $100,000
• جمعیت: 1,000,000
• سربازان: 0
• تمام منابع، تسلیحات و ساختمان‌ها حذف می‌شوند

❗ این عمل قابل برگشت نیست!

آیا مطمئن هستید؟"""
        
        await query.edit_message_text(warning_text, reply_markup=keyboard)
    
    async def confirm_country_reset(self, query, context, user_id):
        """Confirm and execute country reset"""
        player = self.db.get_player(user_id)
        
        if not player:
            await query.edit_message_text("❌ کشور یافت نشد!")
            return
        
        # Reset player to initial state
        success = self.db.reset_player_data(user_id)
        
        if success:
            # Log admin action
            admin_id = query.from_user.id
            self.db.log_admin_action(
                admin_id,
                "RESET_COUNTRY",
                user_id,
                f"Reset country {player['country_name']}"
            )
            
            await query.edit_message_text(
                f"✅ کشور {player['country_name']} با موفقیت ریست شد!\n\n"
                f"این کشور به حالت اولیه بازگشت.",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )
        else:
            await query.edit_message_text("❌ خطا در ریست کشور!")
