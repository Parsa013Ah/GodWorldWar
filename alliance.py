import logging
from datetime import datetime
from config import Config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class AllianceSystem:
    def __init__(self, database):
        self.db = database
        self.setup_alliance_tables()

    def setup_alliance_tables(self):
        """Setup alliance tables in database"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Alliances table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alliances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    leader_id INTEGER NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (leader_id) REFERENCES players (user_id)
                )
            ''')

            # Alliance members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alliance_members (
                    alliance_id INTEGER NOT NULL,
                    player_id INTEGER NOT NULL,
                    role TEXT DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (alliance_id, player_id),
                    FOREIGN KEY (alliance_id) REFERENCES alliances (id),
                    FOREIGN KEY (player_id) REFERENCES players (user_id)
                )
            ''')

            # Alliance invitations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alliance_invitations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alliance_id INTEGER NOT NULL,
                    inviter_id INTEGER NOT NULL,
                    invitee_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (alliance_id) REFERENCES alliances (id),
                    FOREIGN KEY (inviter_id) REFERENCES players (user_id),
                    FOREIGN KEY (invitee_id) REFERENCES players (user_id)
                )
            ''')

            conn.commit()

    def create_alliance(self, leader_id, alliance_name, description=""):
        """Create new alliance"""
        # Check if player is already in an alliance
        if self.get_player_alliance(leader_id):
            return {'success': False, 'message': 'شما قبلاً عضو یک اتحاد هستید!'}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Create alliance
            cursor.execute('''
                INSERT INTO alliances (name, leader_id, description)
                VALUES (?, ?, ?)
            ''', (alliance_name, leader_id, description))

            alliance_id = cursor.lastrowid

            # Add leader as member
            cursor.execute('''
                INSERT INTO alliance_members (alliance_id, player_id, role)
                VALUES (?, ?, 'leader')
            ''', (alliance_id, leader_id))

            conn.commit()

            return {
                'success': True,
                'message': f'اتحاد "{alliance_name}" با موفقیت تشکیل شد!',
                'alliance_id': alliance_id
            }

    def invite_to_alliance(self, inviter_id, invitee_id):
        """Invite player to alliance"""
        inviter_alliance = self.get_player_alliance(inviter_id)

        if not inviter_alliance:
            return {'success': False, 'message': 'شما عضو هیچ اتحادی نیستید!'}

        # Check if inviter has permission (leader or officer)
        if inviter_alliance['role'] not in ['leader', 'officer']:
            return {'success': False, 'message': 'شما اجازه دعوت کردن ندارید!'}

        # Check if invitee is already in an alliance
        if self.get_player_alliance(invitee_id):
            return {'success': False, 'message': 'این بازیکن قبلاً عضو یک اتحاد است!'}

        # Check for existing invitation
        existing = self.get_pending_invitation(inviter_alliance['alliance_id'], invitee_id)
        if existing:
            return {'success': False, 'message': 'دعوت‌نامه قبلاً ارسال شده!'}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alliance_invitations (alliance_id, inviter_id, invitee_id)
                VALUES (?, ?, ?)
            ''', (inviter_alliance['alliance_id'], inviter_id, invitee_id))
            conn.commit()

        return {
            'success': True,
            'message': 'دعوت‌نامه ارسال شد!',
            'alliance_name': inviter_alliance['alliance_name']
        }

    def respond_to_invitation(self, player_id, invitation_id, response):
        """Respond to alliance invitation"""
        invitation = self.get_invitation(invitation_id)

        if not invitation or invitation['invitee_id'] != player_id:
            return {'success': False, 'message': 'دعوت‌نامه یافت نشد!'}

        if invitation['status'] != 'pending':
            return {'success': False, 'message': 'این دعوت‌نامه قبلاً پاسخ داده شده!'}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            if response == 'accept':
                # Add to alliance
                cursor.execute('''
                    INSERT INTO alliance_members (alliance_id, player_id)
                    VALUES (?, ?)
                ''', (invitation['alliance_id'], player_id))

                # Update invitation status
                cursor.execute('''
                    UPDATE alliance_invitations 
                    SET status = 'accepted' 
                    WHERE id = ?
                ''', (invitation_id,))

                conn.commit()

                return {
                    'success': True,
                    'message': f'شما با موفقیت به اتحاد "{invitation["alliance_name"]}" پیوستید!'
                }
            else:
                # Reject invitation
                cursor.execute('''
                    UPDATE alliance_invitations 
                    SET status = 'rejected' 
                    WHERE id = ?
                ''', (invitation_id,))

                conn.commit()

                return {
                    'success': True,
                    'message': 'دعوت‌نامه رد شد.'
                }

    def get_player_alliance(self, player_id):
        """Get player's current alliance"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.id as alliance_id, a.name as alliance_name, 
                       am.role, a.leader_id, a.description
                FROM alliances a
                JOIN alliance_members am ON a.id = am.alliance_id
                WHERE am.player_id = ?
            ''', (player_id,))

            result = cursor.fetchone()
            return dict(result) if result else None

    def get_alliance_members(self, alliance_id):
        """Get alliance members"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.user_id, p.country_name, p.username, am.role, am.joined_at
                FROM alliance_members am
                JOIN players p ON am.player_id = p.user_id
                WHERE am.alliance_id = ?
                ORDER BY am.role DESC, am.joined_at
            ''', (alliance_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_pending_invitations(self, player_id):
        """Get pending invitations for player"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ai.id, a.name as alliance_name, p.country_name as inviter_country,
                       ai.created_at
                FROM alliance_invitations ai
                JOIN alliances a ON ai.alliance_id = a.id
                JOIN players p ON ai.inviter_id = p.user_id
                WHERE ai.invitee_id = ? AND ai.status = 'pending'
                ORDER BY ai.created_at DESC
            ''', (player_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_pending_invitation(self, alliance_id, invitee_id):
        """Check for existing pending invitation"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM alliance_invitations
                WHERE alliance_id = ? AND invitee_id = ? AND status = 'pending'
            ''', (alliance_id, invitee_id))

            return cursor.fetchone() is not None

    def get_invitation(self, invitation_id):
        """Get invitation details"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ai.*, a.name as alliance_name
                FROM alliance_invitations ai
                JOIN alliances a ON ai.alliance_id = a.id
                WHERE ai.id = ?
            ''', (invitation_id,))

            result = cursor.fetchone()
            return dict(result) if result else None

    def leave_alliance(self, player_id):
        """Leave alliance"""
        alliance = self.get_player_alliance(player_id)

        if not alliance:
            return {'success': False, 'message': 'شما عضو هیچ اتحادی نیستید!'}

        if alliance['role'] == 'leader':
            # Check if there are other members
            members = self.get_alliance_members(alliance['alliance_id'])
            if len(members) > 1:
                return {'success': False, 'message': 'رهبر اتحاد نمی‌تواند اتحاد را ترک کند تا اعضای دیگر موجود باشند!'}
            else:
                # Disband alliance
                return self.disband_alliance(alliance['alliance_id'])

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM alliance_members 
                WHERE alliance_id = ? AND player_id = ?
            ''', (alliance['alliance_id'], player_id))
            conn.commit()

        return {
            'success': True,
            'message': f'شما اتحاد "{alliance["alliance_name"]}" را ترک کردید.'
        }

    def disband_alliance(self, alliance_id):
        """Disband alliance"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Remove all members
            cursor.execute('DELETE FROM alliance_members WHERE alliance_id = ?', (alliance_id,))

            # Remove all invitations
            cursor.execute('DELETE FROM alliance_invitations WHERE alliance_id = ?', (alliance_id,))

            # Remove alliance
            cursor.execute('DELETE FROM alliances WHERE id = ?', (alliance_id,))

            conn.commit()

        return {'success': True, 'message': 'اتحاد منحل شد.'}

    def get_all_players(self):
        """Get all players"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, country_name FROM players')
            return [dict(row) for row in cursor.fetchall()]

    def get_player(self, player_id):
        """Get player details"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, country_name FROM players WHERE user_id = ?', (player_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    async def handle_statement_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle statement text input"""
        try:
            user_id = update.effective_user.id
            text = update.message.text

            if not text or len(text.strip()) == 0:
                await update.message.reply_text("❌ متن بیانیه نمی‌تواند خالی باشد!")
                return

            if len(text) > 500:
                await update.message.reply_text("❌ متن بیانیه نمی‌تواند بیش از 500 کاراکتر باشد!")
                return

            # Get alliance
            alliance = self.db.get_player_alliance(user_id)
            if not alliance:
                await update.message.reply_text("❌ شما عضو هیچ اتحادی نیستید!")
                return

            # Check if user is leader
            if alliance['leader_id'] != user_id:
                await update.message.reply_text("❌ فقط رهبر اتحاد می‌تواند بیانیه ارسال کند!")
                return

            # Send statement to all alliance members
            members = self.db.get_alliance_members(alliance['id'])
            sent_count = 0

            statement_text = f"""📢 بیانیه اتحاد {alliance['name']}

{text}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}
👤 رهبر اتحاد"""

            for member in members:
                try:
                    await context.bot.send_message(
                        chat_id=member['user_id'], 
                        text=statement_text
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send statement to {member['user_id']}: {e}")

            await update.message.reply_text(
                f"✅ بیانیه به {sent_count} عضو ارسال شد!"
            )

        except Exception as e:
            logger.error(f"Error in handle_statement_text: {e}")
            await update.message.reply_text("❌ خطا در ارسال بیانیه!")

    async def handle_alliance_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle alliance related queries"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        if query.data == "alliance_menu":
            alliance = self.db.get_player_alliance(user_id)
            if not alliance:
                await query.edit_message_text("❌ شما عضو هیچ اتحادی نیستید!")
                return

            keyboard = [
                [InlineKeyboardButton("اعضای اتحاد", callback_data="alliance_members")],
                [InlineKeyboardButton("دعوت به اتحاد", callback_data="alliance_invite_list")],
                [InlineKeyboardButton("درخواست‌های ورود", callback_data="alliance_requests")],
                [InlineKeyboardButton("بیانیه اتحاد", callback_data="alliance_statement")],
                [InlineKeyboardButton("ترک اتحاد", callback_data="leave_alliance")],
            ]
            if alliance['role'] == 'leader':
                keyboard.append([InlineKeyboardButton("انحلال اتحاد", callback_data="disband_alliance")])
            
            await query.edit_message_text(
                f"🏛 منوی اتحاد: {alliance['name']}\n\n"
                f"توضیحات: {alliance.get('description', 'بدون توضیحات')}\n"
                f"رهبر: {alliance.get('leader_name', 'نامشخص')}\n"
                f"نقش شما: {alliance['role']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif query.data == "alliance_members":
            alliance = self.db.get_player_alliance(user_id)
            if not alliance:
                await query.edit_message_text("❌ شما عضو هیچ اتحادی نیستید!")
                return

            members = self.db.get_alliance_members(alliance['id'])
            if not members:
                await query.edit_message_text("❌ هیچ عضوی در اتحاد یافت نشد!")
                return

            member_list = "👥 اعضای اتحاد:\n\n"
            for member in members:
                member_list += f"- {member['country_name']} ({member['role']})\n"

            await query.edit_message_text(member_list, reply_markup=self.keyboards.back_to_alliance_keyboard())

        elif query.data == "alliance_invite_list":
            alliance = self.db.get_player_alliance(user_id)
            if not alliance:
                await query.edit_message_text("❌ شما عضو هیچ اتحادی نیستید!")
                return

            if alliance['leader_id'] != user_id:
                await query.edit_message_text("❌ فقط رهبر اتحاد می‌تواند دعوت‌نامه ارسال کند!")
                return

            # Get all players not in alliance
            all_players = self.db.get_all_players()
            available_players = []

            for player in all_players:
                if not self.db.get_player_alliance(player['user_id']) and player['user_id'] != user_id:
                    available_players.append(player)

            if not available_players:
                await query.edit_message_text(
                    "❌ هیچ کشوری برای دعوت یافت نشد!",
                    reply_markup=self.keyboards.alliance_invite_keyboard()
                )
                return

            await query.edit_message_text(
                "👥 کشوری را برای دعوت انتخاب کنید:",
                reply_markup=self.keyboards.alliance_invite_keyboard(available_players)
            )

        elif query.data.startswith("alliance_invite_"):
            try:
                target_id = int(query.data.split("_")[-1])
                alliance = self.db.get_player_alliance(user_id)

                if not alliance or alliance['leader_id'] != user_id:
                    await query.edit_message_text("❌ شما مجاز به ارسال دعوت‌نامه نیستید!")
                    return

                # Check if target already in alliance
                if self.db.get_player_alliance(target_id):
                    await query.edit_message_text("❌ این کشور قبلاً عضو اتحادی است!")
                    return

                # Send invitation
                target_player = self.db.get_player(target_id)
                if not target_player:
                    await query.edit_message_text("❌ کشور یافت نشد!")
                    return

                sender_player = self.db.get_player(user_id)

                invite_text = f"""📨 دعوت‌نامه اتحاد

🏛 اتحاد: {alliance['name']}
👤 دعوت‌کننده: {sender_player['country_name']}

آیا می‌خواهید به این اتحاد بپیوندید؟"""

                invite_keyboard = [
                    [
                        InlineKeyboardButton("✅ پذیرش", callback_data=f"accept_alliance_{alliance['id']}"),
                        InlineKeyboardButton("❌ رد", callback_data="reject_alliance")
                    ]
                ]

                try:
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=invite_text,
                        reply_markup=InlineKeyboardMarkup(invite_keyboard)
                    )
                    await query.edit_message_text(
                        f"✅ دعوت‌نامه به {target_player['country_name']} ارسال شد!"
                    )
                except:
                    await query.edit_message_text("❌ خطا در ارسال دعوت‌نامه!")

            except ValueError:
                await query.edit_message_text("❌ ID نامعتبر!")

        elif query.data == "leave_alliance":
            result = self.leave_alliance(user_id)
            await query.edit_message_text(result['message'])
            if result['success']:
                # Optionally, redirect to main menu or show a confirmation
                pass # Or handle redirect to main menu

        elif query.data == "disband_alliance":
            alliance = self.db.get_player_alliance(user_id)
            if not alliance or alliance['role'] != 'leader':
                await query.edit_message_text("❌ شما رهبر اتحاد نیستید!")
                return

            result = self.disband_alliance(alliance['id'])
            await query.edit_message_text(result['message'])

        elif query.data.startswith("accept_alliance_"):
            try:
                alliance_id = int(query.data.split("_")[-1])
                result = self.respond_to_invitation(user_id, self.get_last_invitation_id(user_id, alliance_id), 'accept')
                await query.edit_message_text(result['message'])
            except Exception as e:
                logger.error(f"Error accepting alliance invitation: {e}")
                await query.edit_message_text("❌ خطا در پذیرش دعوت‌نامه!")

        elif query.data == "reject_alliance":
            try:
                result = self.respond_to_invitation(user_id, self.get_last_invitation_id(user_id, None), 'reject')
                await query.edit_message_text(result['message'])
            except Exception as e:
                logger.error(f"Error rejecting alliance invitation: {e}")
                await query.edit_message_text("❌ خطا در رد دعوت‌نامه!")

    def get_last_invitation_id(self, invitee_id, alliance_id=None):
        """Get the ID of the last pending invitation for a player."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id FROM alliance_invitations WHERE invitee_id = ? AND status = 'pending'"
            params = [invitee_id]
            if alliance_id is not None:
                query += " AND alliance_id = ?"
                params.append(alliance_id)
            query += " ORDER BY created_at DESC LIMIT 1"
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return result[0] if result else None