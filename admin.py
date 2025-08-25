import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from keyboards import Keyboards
from config import Config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
            await query.edit_message_text("❌ شما مجاز به این عمل نیستید!")
            return

        action = query.data.replace("admin_", "")

        if action == "panel":
            await self.show_admin_panel(query)
        elif action == "stats":
            await self.show_game_stats(query)
        elif action == "players":
            await self.show_players_management(query)
        elif action == "logs":
            await self.show_admin_logs(query)
        elif action == "reset":
            await self.show_reset_confirmation(query)
        elif action == "reset_confirm":
            await self.reset_game_data(query)
        elif action == "infinite_resources":
            await self.give_infinite_resources(query)
        elif action == "country_reset":
            await self.show_country_reset_menu(query)
        elif action == "give_items":
            await self.show_give_items_menu(query)
        elif action.startswith("player_"):
            player_id = int(action.replace("player_", ""))
            await self.show_player_actions(query, player_id)
        elif action.startswith("delete_"):
            player_id = int(action.replace("delete_", ""))
            await self.delete_player_confirm(query, player_id)
        elif action.startswith("view_"):
            player_id = int(action.replace("view_", ""))
            await self.view_player_full(query, player_id)
        else:
            await query.edit_message_text("❌ دستور نامعتبر!")
            return

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
⚔️سربازان: {player['soldiers']:,}

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

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ بله، ریست کن", callback_data="admin_reset_confirm"),
                InlineKeyboardButton("❌ انصراف", callback_data="admin_panel")
            ]
        ])

        await query.edit_message_text(warning_text, reply_markup=keyboard)

    async def reset_game_data(self, query, context):
        """Reset all game data"""
        user_id = query.from_user.id

        try:
            success = self.db.reset_all_data()

            if success:
                # Log admin action
                self.db.log_admin_action(
                    user_id,
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

        except Exception as e:
            logger.error(f"Error in reset_game_data: {e}")
            await query.edit_message_text(
                "❌ خطای سیستمی در ریست!",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )
            
    async def give_infinite_resources(self, query):
        """Give infinite resources to all players"""
        user_id = query.from_user.id

        try:
            success = self.db.give_infinite_resources_to_all_players()

            if success:
                self.db.log_admin_action(user_id, "GIVE_INFINITE_RESOURCES", None, "Infinite resources to all players")
                await query.edit_message_text(
                    "✅ منابع و پول بینهایت به همه بازیکنان داده شد!\n\n"
                    "💰 پول: 1,000,000,000 دلار\n"
                    "📊 منابع: 1,000,000 از هر نوع\n"
                    "👥 جمعیت: 50,000,000\n"
                    "⚔️ سربازان: 10,000,000\n"
                    "🏗 ساختمان‌ها: 100 از هر نوع معدن، 50 از بقیه",
                    reply_markup=self.keyboards.back_to_main_keyboard()
                )
            else:
                await query.edit_message_text(
                    "❌ خطا در دادن منابع بینهایت!",
                    reply_markup=self.keyboards.back_to_main_keyboard()
                )

        except Exception as e:
            logger.error(f"Error in give_infinite_resources: {e}")
            await query.edit_message_text(
                "❌ خطای سیستمی!",
                reply_markup=self.keyboards.back_to_main_keyboard()
            )


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
        country_code = data.replace("admin_penalty_", "") # Corrected to use country_code directly

        # Find player by country code
        all_players = self.db.get_all_players() # Assuming get_all_players returns list of players with country_name
        player = None
        for p in all_players:
            # Assuming player dict has 'country_name' and Config.COUNTRIES maps country_code to country_name
            # If your DB stores country_code directly in player, adjust this logic
            if Config.COUNTRIES.get(country_code) == p['country_name']:
                player = p
                break

        if not player:
            await query.edit_message_text(f"❌ کشور با کد {country_code} یافت نشد!")
            return

        user_id = player['user_id']

        # Halve money
        new_money = player['money'] // 2
        self.db.update_player_money(user_id, new_money)

        # Halve population and soldiers
        new_population = player['population'] // 2
        new_soldiers = player['soldiers'] // 2
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
        country_name = Config.COUNTRIES.get(country_code, country_code)
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

    async def handle_penalty_action(self, query, context, data):
        """Handle specific penalty actions"""
        parts = data.split('_')
        penalty_type = parts[1]
        user_id = int(parts[2])
        player = self.db.get_player(user_id)

        if not player:
            await query.edit_message_text("❌ بازیکن یافت نشد!")
            return

        if penalty_type == "money":
            # Execute penalty
            penalty_amount = min(player['money'] * 0.1, 100000)  # 10% or max 100k
            new_money = max(0, player['money'] - penalty_amount)
            self.db.update_player_money(player['user_id'], new_money)

            # Send notification to penalized player
            try:
                await context.bot.send_message(
                    chat_id=player['user_id'],
                    text=f"⚠️ کشور {player['country_name']} به دلیل رعایت نکردن قوانین جریمه شد!\n💰 مبلغ جریمه: ${penalty_amount:,}"
                )
            except:
                pass

            await query.edit_message_text(
                f"✅ جریمه مالی اعمال شد!\n"
                f"🎯 هدف: {player['country_name']}\n"
                f"💰 مبلغ جریمه: ${penalty_amount:,}\n"
                f"📱 کاربر مطلع شد."
            )
        elif penalty_type == "resources":
            # Halve all resources
            resources = self.db.get_player_resources(user_id)
            for resource, amount in resources.items():
                if resource != 'user_id' and amount > 0:
                    new_amount = amount // 2
                    self.db.update_resource(user_id, resource, new_amount)

            await query.edit_message_text(
                f"✅ کسر منابع اعمال شد!\n"
                f"🎯 هدف: {player['country_name']}\n"
                f"📦 تمام منابع این کشور نصف شدند."
            )
        elif penalty_type == "weapons":
            # Halve all weapons
            weapons = self.db.get_player_weapons(user_id)
            for weapon, amount in weapons.items():
                if weapon != 'user_id' and amount > 0:
                    new_amount = amount // 2
                    self.db.update_weapon_count(user_id, weapon, new_amount)

            await query.edit_message_text(
                f"✅ کسر تسلیحات اعمال شد!\n"
                f"🎯 هدف: {player['country_name']}\n"
                f"⚔️ تمام تسلیحات این کشور نصف شدند."
            )
        else:
            await query.edit_message_text("❌ نوع جریمه نامعتبر!")