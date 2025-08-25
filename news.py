import logging
import asyncio
import random
from telegram import Bot
from telegram.error import TelegramError
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsChannel:
    def __init__(self):
        self.channel_id = Config.BOT_CONFIG['news_channel']
        self.bot = None

        # Message templates for variety
        self.player_joined_templates = [
            "🎮 بازیکن جدید!\n\n{flag} <b>{country}</b> توسط {username} تصرف شد!\n\nجمعیت اولیه: 1,000,000 نفر\nسرمایه اولیه: $100,000\n\nخوش آمدید به جنگ جهانی! 🌍",
            "🌟 کشور جدید آزاد شد!\n\n{flag} <b>{country}</b> با رهبری {username} استقلال کسب کرد!\n\nجمعیت: 1,000,000 نفر\nبودجه: $100,000\n\nبه دنیای درگون RP خوش آمدید! 🎯",
            "⚡ تولد یک قدرت جدید!\n\n{flag} <b>{country}</b> زیر کنترل {username} آمد!\n\nآمار اولیه:\n👥 جمعیت: 1,000,000\n💰 سرمایه: $100,000\n\nمبارک باشد! 🎊",
            "🚀 ظهور رهبر جدید!\n\n{flag} دولت <b>{country}</b> توسط {username} تشکیل شد!\n\nوضعیت کشور:\n📊 جمعیت: 1,000,000 نفر\n💳 بودجه: $100,000\n\nموفق باشید! 🏆",
            "🌍 کشور تازه‌ای به نقشه اضافه شد!\n\n{flag} <b>{country}</b> با قیادت {username} فعال شد!\n\n📈 آمار:\n- جمعیت: 1,000,000\n- بودجه: $100,000\n\nبه خانواده بزرگ ما خوش آمدید! 🤗",
            "🔥 انقلاب سیاسی!\n\n{flag} <b>{country}</b> تحت فرمان {username} قرار گرفت!\n\nمنابع کشور:\n• جمعیت: 1,000,000\n• بودجه: $100,000\n\nعصری نو آغاز شد! ⭐",
            "👑 تاجگذاری جدید!\n\n{flag} {username} بر تخت <b>{country}</b> تکیه زد!\n\n🏰 امپراتوری:\n📊 جمعیت: 1M نفر\n💰 خزانه: $100K\n\nسلطنت جدید آغاز شد! 👑",
            "🗺 گسترش نقشه!\n\n{flag} <b>{country}</b> با حاکمیت {username} به دنیا پیوست!\n\n📈 پارامترهای اولیه:\n👥 مردم: 1,000,000\n💳 اقتصاد: $100,000\n\nبه مرزهای جدید خوش آمدید! 🌐",
            "💫 ستاره‌ای جدید در افق!\n\n{flag} <b>{country}</b> زیر نظر {username} درخشان شد!\n\n✨ شروع باشکوه:\n• 1,000,000 شهروند\n• $100,000 سرمایه\n\nآینده‌ای روشن در انتظار! 🌅",
            "🌊 موج تغییر!\n\n{flag} <b>{country}</b> با رهبری {username} متحول شد!\n\n⚡ قدرت نوین:\n📊 مردم: 1M\n💰 بودجه: $100K\n\nتحول بزرگ شروع شد! 🚀"
        ]

        self.building_templates = [
            "🏗 توسعه عظیم زیرساخت!\n\n{flag} <b>{country}</b> یک {emoji} <b>{building}</b> مدرن احداث کرد!\n\n📈 اقتصاد قدرتمندتر شد!\n💰 درآمد آینده افزایش یافت!\n🌟 پیشرفت چشمگیر!",
            "🔨 سرمایه‌گذاری بزرگ!\n\n{flag} <b>{country}</b> با ساخت {emoji} <b>{building}</b> اقتصاد خود را تقویت کرد!\n\n📊 ظرفیت تولید افزایش یافت\n⚡ کارایی بهبود پیدا کرد\n💎 آینده‌ای درخشان!",
            "🏭 انقلاب صنعتی!\n\n{flag} در <b>{country}</b> یک {emoji} <b>{building}</b> پیشرفته راه‌اندازی شد!\n\n🚀 تکنولوژی مدرن\n📈 رشد اقتصادی\n🌟 توسعه پایدار",
            "⚡ پروژه ملی کامل شد!\n\n{flag} <b>{country}</b> موفق به تکمیل {emoji} <b>{building}</b> شد!\n\n🎯 هدف‌گذاری موفق\n💪 اقتصاد مقاوم\n🏆 پیشرفت قابل توجه",
            "🌟 دستاورد جدید!\n\n{flag} کشور <b>{country}</b> با افتتاح {emoji} <b>{building}</b> گامی بزرگ برداشت!\n\n🔥 توسعه سریع\n📊 بهره‌وری بالا\n💰 سودآوری مطمئن"
        ]

        self.weapon_templates = {
            'basic': [
                "⚔️ تقویت ارتش\n\n{flag} <b>{country}</b> یک {emoji} <b>{weapon}</b> جدید تولید کرد!\n\n💪 قدرت نظامی افزایش یافت!\n🛡 آمادگی دفاعی بالا رفت!",
                "🔫 ارتقای تسلیحات\n\n{flag} <b>{country}</b> موفق به ساخت {emoji} <b>{weapon}</b> شد!\n\n⚡ قدرت رزمی بهبود یافت\n🎯 ظرفیت دفاعی افزایش یافت",
                "⚔️ تجهیز نیروهای مسلح\n\n{flag} ارتش <b>{country}</b> به {emoji} <b>{weapon}</b> مجهز شد!\n\n🔥 آمادگی رزمی بالا\n💪 قدرت بازدارندگی"
            ],
            'nuclear': [
                "☢️ خبر فوری - سلاح هسته‌ای!\n\n{flag} <b>{country}</b> یک {emoji} <b>{weapon}</b> تولید کرد!\n\n🚨 این کشور به باشگاه هسته‌ای پیوست!\n⚡ قدرت نظامی فوق‌العاده افزایش یافت!\n🌍 تعادل قدرت جهانی تغییر کرد!",
                "☢️ انقلاب هسته‌ای!\n\n{flag} <b>{country}</b> وارد عصر هسته‌ای شد!\n\n💥 {emoji} <b>{weapon}</b> تولید شد\n🌍 قدرت جهانی جدید\n⚡ بازدارندگی نهایی",
                "🚨 هشدار هسته‌ای!\n\n{flag} <b>{country}</b> قدرت هسته‌ای کسب کرد!\n\n☢️ {emoji} <b>{weapon}</b> آماده\n🌟 تکنولوژی پیشرفته\n💪 قدرت استراتژیک"
            ],
            'missile': [
                "🚀 توسعه موشکی پیشرفته!\n\n{flag} <b>{country}</b> یک {emoji} <b>{weapon}</b> مدرن تولید کرد!\n\n🎯 فناوری موشکی پیشرفته\n🌐 قابلیت حمله دوربرد\n💪 قدرت راهبردی بالا",
                "🚀 پیشرفت موشکی!\n\n{flag} <b>{country}</b> به فناوری موشکی دست یافت!\n\n💥 {emoji} <b>{weapon}</b> تکمیل شد\n🎯 دقت بالا\n⚡ سرعت فوق‌صوت",
                "🌐 قدرت موشکی!\n\n{flag} <b>{country}</b> ظرفیت موشکی خود را ارتقا داد!\n\n🚀 {emoji} <b>{weapon}</b> عملیاتی\n💫 تکنولوژی مدرن\n🏆 برتری تاکتیکی"
            ],
            'aircraft': [
                "✈️ جنگنده نسل پنجم!\n\n{flag} <b>{country}</b> یک {emoji} <b>{weapon}</b> فوق پیشرفته تولید کرد!\n\n🔥 فناوری استلث\n⚡ قدرت هوایی برتر\n🌟 تکنولوژی نظامی مدرن",
                "🛩 برتری هوایی!\n\n{flag} <b>{country}</b> نیروی هوایی خود را تقویت کرد!\n\n✈️ {emoji} <b>{weapon}</b> آماده پرواز\n⚡ سرعت فوق‌صوت\n🎯 دقت بالا",
                "🌟 تکنولوژی هوایی!\n\n{flag} <b>{country}</b> به فناوری پیشرفته دست یافت!\n\n✈️ {emoji} <b>{weapon}</b> تحویل شد\n🔥 قابلیت استلث\n💪 قدرت رزمی بالا"
            ]
        }

        self.war_templates = {
            'victory': [
                "🏆 پیروزی قاطع!\n\n{attacker_flag} <b>{attacker}</b> ⚔️ {defender_flag} <b>{defender}</b>\n\n🔥 نیروی حمله: {attack_power:,}\n🛡 نیروی دفاع: {defense_power:,}\n\n✨ حمله موفقیت‌آمیز بود!",
                "⚡ شکست کامل!\n\n{attacker_flag} <b>{attacker}</b> 💥 {defender_flag} <b>{defender}</b>\n\n⚔️ قدرت حمله: {attack_power:,}\n🛡 قدرت دفاع: {defense_power:,}\n\n🎯 پیروزی درخشان!",
                "💥 نبرد تاریخی!\n\n{attacker_flag} <b>{attacker}</b> VS {defender_flag} <b>{defender}</b>\n\n🔥 حمله: {attack_power:,}\n🛡 دفاع: {defense_power:,}\n\n🏆 غلبه کامل!"
            ],
            'defeat': [
                "🛡 دفاع قهرمانانه!\n\n{attacker_flag} <b>{attacker}</b> ⚔️ {defender_flag} <b>{defender}</b>\n\n🔥 نیروی حمله: {attack_power:,}\n🛡 نیروی دفاع: {defense_power:,}\n\n💪 مقاومت موفق!",
                "🏰 مقاومت شکست‌ناپذیر!\n\n{attacker_flag} <b>{attacker}</b> 💥 {defender_flag} <b>{defender}</b>\n\n⚔️ قدرت حمله: {attack_power:,}\n🛡 قدرت دفاع: {defense_power:,}\n\n✋ حمله دفع شد!",
                "⚡ دفاع موفق!\n\n{attacker_flag} <b>{attacker}</b> VS {defender_flag} <b>{defender}</b>\n\n🔥 حمله: {attack_power:,}\n🛡 دفاع: {defense_power:,}\n\n🛡 پایداری کامل!"
            ]
        }

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

    async def send_convoy_news(self, message, keyboard=None):
        """Send convoy news with optional keyboard"""
        try:
            if keyboard:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"🚛 انتقال منابع\n\n{message}",
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            else:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"🚛 انتقال منابع\n\n{message}",
                    parse_mode='HTML'
                )

            logger.info(f"📢 Convoy news sent to {self.channel_id}: 🚛 انتقال منابع...")
        except Exception as e:
            logger.error(f"Failed to send convoy news: {e}")

    async def send_weapon_produced(self, country_name, weapon_name, quantity=1):
        """Send weapon production news with quantity"""
        message = f"""🔫 ارتقای تسلیحات

🇮🇷 <b>{country_name}</b> موفق به ساخت <b>{quantity:,} عدد {weapon_name}</b> شد!

💪 قدرت نظامی این کشور افزایش یافته است."""

        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"📢 News sent to {self.channel_id}: 🔫 ارتقای تسلیحات...")
        except Exception as e:
            logger.error(f"Failed to send news: {e}")

    async def send_building_constructed(self, country_name, building_name, quantity=1):
        """Send building construction news with quantity"""
        message = f"""🏗 توسعه زیرساخت

🇮🇷 <b>{country_name}</b> موفق به ساخت <b>{quantity:,} عدد {building_name}</b> شد!

📈 اقتصاد این کشور تقویت شده است."""

        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"📢 News sent to {self.channel_id}: 🏗 توسعه زیرساخت...")
        except Exception as e:
            logger.error(f"Failed to send news: {e}")


    async def send_player_joined(self, country_name, username):
        """Send player joined news"""
        country_flag = self.get_country_flag(country_name)

        # Select random template
        template = random.choice(self.player_joined_templates)
        message = template.format(
            flag=country_flag,
            country=country_name,
            username=username
        )

        message += "\n\n───────────────"
        await self.send_news(message)

    async def send_building_constructed(self, country_name, building_name, quantity=1):
        """Send building construction news"""
        country_flag = self.get_country_flag(country_name)

        building_emojis = {
            'iron_mine': '⛏', 'copper_mine': '⛏', 'oil_mine': '🛢', 'gas_mine': '⛽',
            'aluminum_mine': '🔗', 'gold_mine': '🏆', 'uranium_mine': '☢️',
            'lithium_mine': '🔋', 'coal_mine': '⚫', 'silver_mine': '🥈',
            'weapon_factory': '🏭', 'refinery': '🏭', 'power_plant': '⚡',
            'wheat_farm': '🌾', 'military_base': '🪖', 'housing': '🏘'
        }

        building_emoji = building_emojis.get(building_name.replace(' ', '_').lower(), '🏗')

        # Select random template
        template = random.choice(self.building_templates)
        message = template.format(
            flag=country_flag,
            country=country_name,
            emoji=building_emoji,
            building=building_name
        )

        message += "\n\n───────────────"
        await self.send_news(message)

    async def send_weapon_produced(self, country_name, weapon_name, quantity=1):
        """Send weapon production news"""
        country_flag = self.get_country_flag(country_name)

        weapon_emojis = {
            'تفنگ': '🔫', 'تانک': '🚗', 'جنگنده': '✈️', 'پهپاد': '🚁',
            'کشتی جنگی': '🚢', 'بمب ساده': '💣', 'بمب هسته‌ای ساده': '☢️',
            'موشک ساده': '🚀', 'موشک بالستیک ساده': '🚀', 'موشک هسته‌ای ساده': '☢️',
            'Trident 2 غیر هسته‌ای': '🚀', 'Trident 2 هسته‌ای': '☢️🚀',
            'Satan2 غیر هسته‌ای': '🚀', 'Satan2 هسته‌ای': '☢️🚀',
            'DF-41 هسته‌ای': '☢️🚀', 'Tomahawk غیر هسته‌ای': '🚀',
            'Tomahawk هسته‌ای': '☢️🚀', 'Kalibr غیر هسته‌ای': '🚀',
            'F-22': '✈️', 'F-35': '✈️', 'Su-57': '✈️', 'J-20': '✈️',
            'F-15EX': '✈️', 'Su-35S': '✈️'
        }

        weapon_emoji = weapon_emojis.get(weapon_name, '⚔️')

        # Determine weapon category and select appropriate template
        if 'هسته‌ای' in weapon_name:
            template = random.choice(self.weapon_templates['nuclear'])
        elif any(name in weapon_name for name in ['Trident', 'Satan2', 'DF-41', 'Tomahawk', 'Kalibr']):
            template = random.choice(self.weapon_templates['missile'])
        elif any(name in weapon_name for name in ['F-22', 'F-35', 'Su-57', 'J-20', 'F-15']):
            template = random.choice(self.weapon_templates['aircraft'])
        else:
            template = random.choice(self.weapon_templates['basic'])

        message = template.format(
            flag=country_flag,
            country=country_name,
            emoji=weapon_emoji,
            weapon=weapon_name
        )

        message += "\n\n───────────────"
        await self.send_news(message)

    async def send_war_report(self, battle_result):
        """Send war report"""
        attacker_flag = self.get_country_flag(battle_result['attacker_country'])
        defender_flag = self.get_country_flag(battle_result['defender_country'])

        # Select appropriate template based on battle outcome
        if battle_result['success']:
            template = random.choice(self.war_templates['victory'])
        else:
            template = random.choice(self.war_templates['defeat'])

        message = template.format(
            attacker_flag=attacker_flag,
            attacker=battle_result['attacker_country'],
            defender_flag=defender_flag,
            defender=battle_result['defender_country'],
            attack_power=battle_result['attack_power'],
            defense_power=battle_result['defense_power']
        )

        # Add losses information
        if battle_result['success'] and battle_result.get('stolen_resources'):
            message += "\n\n💎 غنائم جنگی:"
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

{country_flag}کشور: <b>{country_name}</b>
📅 {current_time}

"{statement}"

───────────────"""

        await self.send_news(message)

    async def send_resource_transfer(self, sender_country, receiver_country, transfer_description, travel_time):
        """Send resource transfer news"""
        sender_flag = self.get_country_flag(sender_country)
        receiver_flag = self.get_country_flag(receiver_country)

        message = f"""📬 انتقال منابع فوری!

🚁 {sender_flag} <b>{sender_country}</b> در حال ارسال منابع به {receiver_flag} <b>{receiver_country}</b>

💰 محموله: {transfer_description}

⚡ انتقال فوری انجام شد!
🛡 محموله با موفقیت تحویل داده شد.

───────────────"""

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
        message = f"""💰 چرخه اقتصادی ۶ ساعته تکمیل شد!

✨ همه کشورها درآمد دریافت کردند
⛏ معادن منابع تولید کردند  
🌾 مزارع جمعیت تولید کردند
🪖 پادگان‌ها سرباز آموزش دادند

🌍 اقتصاد جهانی در حال رشد است!
📊 آماده برای چرخه بعدی...

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