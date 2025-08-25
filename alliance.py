
import logging
from datetime import datetime
from config import Config

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
