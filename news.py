import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsChannel:
    def __init__(self):
        self.channel_id = Config.BOT_CONFIG['news_channel']
        self.bot = None

    def set_bot(self, bot):
        """Set bot instance"""
        self.bot = bot

    async def send_news(self, message):
        """Send news to channel"""
        if not self.bot:
            logger.error("Bot not set for news channel")
            return False

        try:
            await self.bot.send_message(chat_id=self.channel_id, text=message, parse_mode='HTML')
            logger.info(f"📢 News sent to {self.channel_id}: {message[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send news to channel: {e}")
            return False

    async def send_player_joined(self, country_name, username):
        """Send player joined news"""
        # Find country flag
        country_flag = "🏳"
        for code, name in Config.COUNTRIES.items():
            if name == country_name:
                country_flag = Config.COUNTRY_FLAGS.get(code, "🏳")
                break

        message = f"""🎮 بازیکن جدید!

{country_flag} <b>{country_name}</b> توسط {username} تصرف شد!

جمعیت اولیه: 1,000,000 نفر
سرمایه اولیه: $100,000

خوش آمدید به جنگ جهانی! 🌍

───────────────"""

        await self.send_news(message)

    async def send_building_constructed(self, country_name, building_name):
        """Send building construction news"""
        country_flag = self.get_country_flag(country_name)

        message = f"""🏗 توسعه زیرساخت

{country_flag} <b>{country_name}</b> یک <b>{building_name}</b> جدید ساخت!

اقتصاد این کشور در حال رشد است... 📈

───────────────"""

        await self.send_news(message)

    async def send_weapon_produced(self, country_name, weapon_name):
        """Send weapon production news"""
        country_flag = self.get_country_flag(country_name)

        message = f"""⚔️ تقویت ارتش

{country_flag} <b>{country_name}</b> یک <b>{weapon_name}</b> جدید تولید کرد!

قدرت نظامی این کشور افزایش یافت! 💪

───────────────"""

        await self.send_news(message)

    async def send_war_report(self, battle_result):
        """Send war report"""
        attacker_flag = self.get_country_flag(battle_result['attacker_country'])
        defender_flag = self.get_country_flag(battle_result['defender_country'])

        if battle_result['success']:
            result_emoji = "🏆"
            result_text = f"{attacker_flag} <b>{battle_result['attacker_country']}</b> برنده شد!"
        else:
            result_emoji = "🛡"
            result_text = f"{defender_flag} <b>{battle_result['defender_country']}</b> حمله را دفع کرد!"

        message = f"""⚔️ گزارش جنگ {result_emoji}

{attacker_flag} <b>{battle_result['attacker_country']}</b> 
🆚 
{defender_flag} <b>{battle_result['defender_country']}</b>

🔥 قدرت حمله: {battle_result['attack_power']:,}
🛡 قدرت دفاع: {battle_result['defense_power']:,}

{result_text}"""

        # Add losses information
        if battle_result['success'] and battle_result.get('stolen_resources'):
            message += "\n\n💰 منابع غارت شده:"
            for resource, amount in battle_result['stolen_resources'].items():
                resource_config = Config.RESOURCES.get(resource, {})
                resource_name = resource_config.get('name', resource)
                resource_emoji = resource_config.get('emoji', '📦')
                message += f"\n{resource_emoji} {resource_name}: {amount:,}"

        message += "\n\n───────────────"
        await self.send_news(message)

    async def send_official_statement(self, country_name, statement):
        """Send official statement"""
        country_flag = self.get_country_flag(country_name)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        message = f"""📢 بیانیه رسمی

{country_flag} کشور: <b>{country_name}</b>
📅 {current_time}

"{statement}"

───────────────"""

        await self.send_news(message)

    async def send_resource_transfer(self, sender_country, receiver_country, resources, travel_time):
        """Send resource transfer news"""
        sender_flag = self.get_country_flag(sender_country)
        receiver_flag = self.get_country_flag(receiver_country)

        message = f"""📬 انتقال منابع

{sender_flag} <b>{sender_country}</b> در حال ارسال منابع به {receiver_flag} <b>{receiver_country}</b>

📦 محموله شامل:"""

        for resource, amount in resources.items():
            resource_config = Config.RESOURCES.get(resource, {})
            resource_name = resource_config.get('name', resource)
            resource_emoji = resource_config.get('emoji', '📦')
            message += f"\n{resource_emoji} {resource_name}: {amount:,}"

        message += f"\n\n⏱ زمان رسیدن: {travel_time} ساعت"
        message += "\n💥 محموله قابل حمله است!"
        message += "\n\n───────────────"

        await self.send_news(message)

    async def send_convoy_attacked(self, attacker_country, convoy_route, stolen_resources):
        """Send convoy attack news"""
        attacker_flag = self.get_country_flag(attacker_country)

        message = f"""💥 حمله به کاروان!

{attacker_flag} <b>{attacker_country}</b> به کاروان {convoy_route} حمله کرد!

🏴‍☠️ منابع دزدیده شده:"""

        for resource, amount in stolen_resources.items():
            resource_config = Config.RESOURCES.get(resource, {})
            resource_name = resource_config.get('name', resource)
            resource_emoji = resource_config.get('emoji', '📦')
            message += f"\n{resource_emoji} {resource_name}: {amount:,}"

        message += "\n\n───────────────"
        await self.send_news(message)

    async def send_income_cycle_complete(self):
        """Send income cycle completion news"""
        message = f"""💰 چرخه درآمد شش‌ساعته

✅ درآمد همه کشورها محاسبه شد
📈 منابع معادن توزیع گردید
👥 جمعیت از مزارع افزایش یافت
⚔️ سربازان جدید آموزش دیدند

───────────────"""

        await self.send_news(message)

    async def send_alliance_formed(self, country1, country2):
        """Send alliance formation news"""
        flag1 = self.get_country_flag(country1)
        flag2 = self.get_country_flag(country2)

        message = f"""🤝 تشکیل اتحاد

{flag1} <b>{country1}</b> و {flag2} <b>{country2}</b> اتحاد تشکیل دادند!

قدرت ترکیبی آنها افزایش یافت 💪

───────────────"""

        await self.send_news(message)

    async def send_peace_treaty(self, country1, country2):
        """Send peace treaty news"""
        flag1 = self.get_country_flag(country1)
        flag2 = self.get_country_flag(country2)

        message = f"""🕊 پیمان صلح

{flag1} <b>{country1}</b> و {flag2} <b>{country2}</b> پیمان صلح امضا کردند!

جنگ بین این دو کشور متوقف شد ✋

───────────────"""

        await self.send_news(message)

    def get_country_flag(self, country_name):
        """Get country flag by name"""
        for code, name in Config.COUNTRIES.items():
            if name == country_name:
                return Config.COUNTRY_FLAGS.get(code, "🏳")
        return "🏳"

    async def send_game_event(self, event_type, **kwargs):
        """Send generic game event"""
        event_messages = {
            'nuclear_weapon': f"☢️ {kwargs['country']} سلاح هسته‌ای تولید کرد!",
            'economic_boom': f"📈 {kwargs['country']} رشد اقتصادی بالایی داشته!",
            'military_exercise': f"🪖 {kwargs['country']} رزمایش نظامی برگزار کرد!",
            'trade_agreement': f"📋 {kwargs['country1']} و {kwargs['country2']} توافق تجاری امضا کردند!",
        }

        message = event_messages.get(event_type, "🎮 رویداد جدید در بازی!")
        message += "\n\n───────────────"

        await self.send_news(message)

    async def send_marketplace_purchase(self, result):
        """Send marketplace purchase news"""
        try:
            if not self.bot:
                return

            purchase_text = f"""🛒 خرید از فروشگاه

{result.get('buyer_country', 'کشور خریدار')} کالایی را از {result.get('seller_country', 'کشور فروشنده')} خریداری کرد.

🚚 محموله در حال ارسال است..."""

            await self.bot.send_message(chat_id=self.channel_id, text=purchase_text)

        except Exception as e:
            logger.error(f"Error sending marketplace news: {e}")