import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class NewsChannel:
    def __init__(self):
        self.channel_username = "@Dragon0RP"
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8264945069:AAE2WYv463Sk0a52sS6hTvR6tzEs8WCmJtI")
    
    async def send_news(self, message):
        """Send news to the channel"""
        try:
            # This would send message to the news channel
            # Implementation would use telegram bot API
            logger.info(f"📢 News sent to {self.channel_username}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send news: {e}")
            return False
    
    async def send_player_joined(self, country_name, username):
        """Send news about new player joining"""
        message = f"""🎉 بازیکن جدید به DragonRP پیوست!

🏴 کشور: {country_name}
👤 رهبر: {username}
📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}

به جنگ جهانی خوش آمدید! 🎮"""
        
        await self.send_news(message)
    
    async def send_building_constructed(self, country_name, building_name):
        """Send news about building construction"""
        message = f"""🏗 ساخت و ساز جدید!

🏴 کشور: {country_name}
🏭 ساختمان: {building_name}
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

توسعه اقتصادی در حال انجام است! 📈"""
        
        await self.send_news(message)
    
    async def send_weapon_produced(self, country_name, weapon_name):
        """Send news about weapon production"""
        message = f"""⚔️ تولید تسلیحات جدید!

🏴 کشور: {country_name}
🔫 سلاح: {weapon_name}
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

قدرت نظامی در حال افزایش! 💪"""
        
        await self.send_news(message)
    
    async def send_attack_news(self, attacker_country, defender_country, result):
        """Send news about military attack"""
        if result['success']:
            message = f"""💥 حمله موفق!

⚔️ مهاجم: {attacker_country}
🛡 مدافع: {defender_country}
🎯 نتیجه: پیروزی {attacker_country}

💀 تلفات:
• {defender_country}: {result.get('defender_losses', {}).get('soldiers', 0)} سرباز
• {attacker_country}: {result.get('attacker_losses', {}).get('soldiers', 0)} سرباز

📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        else:
            message = f"""🛡 دفاع موفق!

⚔️ مهاجم: {attacker_country}
🛡 مدافع: {defender_country}
🎯 نتیجه: پیروزی {defender_country}

💀 تلفات:
• {attacker_country}: {result.get('attacker_losses', {}).get('soldiers', 0)} سرباز
• {defender_country}: {result.get('defender_losses', {}).get('soldiers', 0)} سرباز

📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        await self.send_news(message)
    
    async def send_convoy_departed(self, sender_country, receiver_country, resources, arrival_time):
        """Send news about resource convoy"""
        resource_list = ""
        for resource, amount in resources.items():
            resource_list += f"• {resource}: {amount:,}\n"
        
        message = f"""🚛 ارسال محموله!

📤 فرستنده: {sender_country}
📥 گیرنده: {receiver_country}

📦 محتویات:
{resource_list}
⏰ زمان رسیدن: {arrival_time}

⚠️ محموله در معرض حمله قرار دارد!
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        await self.send_news(message)
    
    async def send_convoy_attacked(self, attacker_country, convoy_info, success):
        """Send news about convoy attack"""
        if success:
            message = f"""💥 حمله به کاروان!

🏴 مهاجم: {attacker_country}
🚛 مسیر: {convoy_info['sender']} → {convoy_info['receiver']}
🎯 نتیجه: موفق

💰 غنائم دزدیده شد!
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        else:
            message = f"""🛡 دفاع از کاروان!

🏴 مهاجم: {attacker_country}
🚛 مسیر: {convoy_info['sender']} → {convoy_info['receiver']}
🎯 نتیجه: ناموفق

کاروان به مسیر خود ادامه داد.
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        await self.send_news(message)
    
    async def send_official_statement(self, country_name, statement):
        """Send official country statement"""
        message = f"""📢 بیانیه رسمی

🏴 کشور: {country_name}
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

"{statement}"

───────────────"""
        
        await self.send_news(message)
    
    async def send_alliance_formed(self, country1, country2):
        """Send news about alliance formation"""
        message = f"""🤝 اتحاد جدید!

🏴 {country1} و {country2} اتحاد تشکیل دادند!

این اتحاد ممکن است تعادل قدرت را تغییر دهد...
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        await self.send_news(message)
    
    async def send_peace_treaty(self, country1, country2):
        """Send news about peace treaty"""
        message = f"""🕊 پیمان صلح!

🏴 {country1} و {country2} پیمان صلح امضا کردند.

جنگ به پایان رسید و صلح برقرار شد.
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        await self.send_news(message)
    
    async def send_income_cycle_complete(self):
        """Send news about income cycle completion"""
        message = f"""💰 چرخه درآمد 6 ساعته

تمام کشورها درآمد خود را دریافت کردند:
• درآمد از معادن
• افزایش جمعیت از مزارع
• تبدیل جمعیت به سرباز

📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        await self.send_news(message)
    
    async def send_special_event(self, event_title, event_description):
        """Send news about special events"""
        message = f"""🎪 رویداد ویژه!

🎯 {event_title}

{event_description}

📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        await self.send_news(message)
    
    async def send_top_countries_ranking(self, rankings):
        """Send weekly top countries ranking"""
        message = "🏆 رتبه‌بندی هفتگی کشورها\n\n"
        
        for i, country in enumerate(rankings[:10], 1):
            message += f"{i}. {country['country_name']} - ${country['money']:,}\n"
        
        message += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        await self.send_news(message)
        
        for i, country in enumerate(rankings[:10], 1):
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            message += f"{medal} {country['country_name']}\n"
            message += f"   💪 قدرت نظامی: {country['military_power']:,}\n"
            message += f"   👥 جمعیت: {country['population']:,}\n\n"
        
        message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        await self.send_news(message)
    
    async def send_admin_announcement(self, announcement):
        """Send admin announcement"""
        message = f"""📣 اعلامیه مدیریت

{announcement}

📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
👑 مدیریت DragonRP"""
        
        await self.send_news(message)
