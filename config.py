"""
DragonRP Game Configuration
Contains all game constants, costs, and specifications
"""

class Config:
    """Main configuration class for DragonRP game"""
    
    # Countries available in the game with Persian names
    COUNTRIES = {
        'IR': 'ایران',
        'AR': 'آرژانتین', 
        'JP': 'ژاپن',
        'RU': 'روسیه',
        'EG': 'مصر',
        'ES': 'اسپانیا',
        'US': 'آمریکا',
        'MX': 'مکزیک',
        'FR': 'فرانسه',
        'DE': 'آلمان',
        'BE': 'بلژیک',
        'CN': 'چین',
        'KP': 'کره شمالی',
        'TR': 'ترکیه',
        'IT': 'ایتالیا',
        'BR': 'برزیل',
        'IN': 'هند',
        'GB': 'انگلیس',
        'CA': 'کانادا',
        'AU': 'استرالیا',
        'SA': 'عربستان سعودی',
        'PK': 'پاکستان',
        'AF': 'افغانستان',
        'IQ': 'عراق'
    }
    
    # Country flags for display
    COUNTRY_FLAGS = {
        'IR': '🇮🇷',
        'AR': '🇦🇷',
        'JP': '🇯🇵', 
        'RU': '🇷🇺',
        'EG': '🇪🇬',
        'ES': '🇪🇸',
        'US': '🇺🇸',
        'MX': '🇲🇽',
        'FR': '🇫🇷',
        'DE': '🇩🇪',
        'BE': '🇧🇪',
        'CN': '🇨🇳',
        'KP': '🇰🇵',
        'TR': '🇹🇷',
        'IT': '🇮🇹',
        'BR': '🇧🇷',
        'IN': '🇮🇳',
        'GB': '🇬🇧',
        'CA': '🇨🇦',
        'AU': '🇦🇺',
        'SA': '🇸🇦',
        'PK': '🇵🇰',
        'AF': '🇦🇫',
        'IQ': '🇮🇶'
    }
    
    # Buildings configuration with costs and specifications
    BUILDINGS = {
        # Mines - produce resources every 6 hours
        'iron_mine': {
            'name': 'معدن آهن',
            'cost': 80000,
            'description': 'تولید آهن برای ساخت سلاح',
            'income_per_cycle': 32000,  # 40% of cost
            'resource_production': ('iron', 1000)
        },
        'copper_mine': {
            'name': 'معدن مس', 
            'cost': 100000,
            'description': 'تولید مس برای الکترونیک',
            'income_per_cycle': 40000,
            'resource_production': ('copper', 800)
        },
        'oil_mine': {
            'name': 'معدن نفت',
            'cost': 120000,
            'description': 'تولید نفت خام',
            'income_per_cycle': 48000,
            'resource_production': ('oil', 1200)
        },
        'gas_mine': {
            'name': 'معدن گاز',
            'cost': 110000,
            'description': 'تولید گاز طبیعی',
            'income_per_cycle': 44000,
            'resource_production': ('gas', 1000)
        },
        'aluminum_mine': {
            'name': 'معدن آلومینیوم',
            'cost': 90000,
            'description': 'تولید آلومینیوم برای قطعات',
            'income_per_cycle': 36000,
            'resource_production': ('aluminum', 900)
        },
        'gold_mine': {
            'name': 'معدن طلا',
            'cost': 150000,
            'description': 'تولید طلا برای فروش',
            'income_per_cycle': 60000,
            'resource_production': ('gold', 500)
        },
        'uranium_mine': {
            'name': 'معدن اورانیوم',
            'cost': 200000,
            'description': 'تولید اورانیوم برای تسلیحات اتمی',
            'income_per_cycle': 80000,
            'resource_production': ('uranium', 200)
        },
        'lithium_mine': {
            'name': 'معدن لیتیوم',
            'cost': 180000,
            'description': 'تولید لیتیوم برای تجهیزات پیشرفته',
            'income_per_cycle': 72000,
            'resource_production': ('lithium', 300)
        },
        'coal_mine': {
            'name': 'معدن زغال‌سنگ',
            'cost': 85000,
            'description': 'تولید زغال برای انرژی',
            'income_per_cycle': 34000,
            'resource_production': ('coal', 1500)
        },
        'silver_mine': {
            'name': 'معدن نقره',
            'cost': 140000,
            'description': 'تولید نقره برای فروش',
            'income_per_cycle': 56000,
            'resource_production': ('silver', 400)
        },
        
        # Production buildings
        'weapon_factory': {
            'name': 'کارخانه اسلحه',
            'cost': 150000,
            'description': 'ساخت تسلیحات از منابع',
            'requirements': ['power_plant']
        },
        'refinery': {
            'name': 'پالایشگاه نفت',
            'cost': 100000,
            'description': 'تبدیل نفت خام به سوخت',
            'conversion': ('oil', 'fuel', 0.8)  # 80% efficiency
        },
        'power_plant': {
            'name': 'نیروگاه برق',
            'cost': 90000,
            'description': 'تولید برق برای کارخانه‌ها'
        },
        'wheat_farm': {
            'name': 'مزرعه گندم',
            'cost': 50000,
            'description': 'افزایش جمعیت',
            'population_per_cycle': 10000
        },
        'military_base': {
            'name': 'پادگان آموزشی',
            'cost': 50000,
            'description': 'تبدیل جمعیت به سرباز',
            'soldiers_per_cycle': 5000
        },
        'housing': {
            'name': 'مسکن (10,000 نفر)',
            'cost': 50000,
            'description': 'ظرفیت نگهداری سرباز',
            'capacity': 10000
        }
    }
    
    # Weapons configuration with costs, resources, and specifications
    WEAPONS = {
        'rifle': {
            'name': 'تفنگ',
            'cost': 1000,
            'resources': {'iron': 10},
            'power': 10,
            'range': 50,
            'type': 'ground',
            'description': 'سلاح پیاده نظام پایه'
        },
        'tank': {
            'name': 'تانک',
            'cost': 10000,
            'resources': {'iron': 100, 'fuel': 50},
            'power': 100,
            'range': 300,
            'type': 'ground',
            'description': 'نیروی زرهی قدرتمند'
        },
        'fighter_jet': {
            'name': 'هواپیما جنگنده',
            'cost': 25000,
            'resources': {'aluminum': 150, 'fuel': 100},
            'power': 200,
            'range': 1000,
            'type': 'air',
            'description': 'برتری هوایی'
        },
        'drone': {
            'name': 'پهپاد',
            'cost': 20000,
            'resources': {'lithium': 80, 'fuel': 60},
            'power': 150,
            'range': 1500,
            'type': 'air',
            'description': 'جنگ بدون سرنشین'
        },
        'missile': {
            'name': 'موشک بالستیک',
            'cost': 50000,
            'resources': {'uranium': 50, 'fuel': 200, 'iron': 100},
            'power': 500,
            'range': 3000,
            'type': 'missile',
            'description': 'قدرت تخریب بالا'
        },
        'warship': {
            'name': 'کشتی جنگی',
            'cost': 40000,
            'resources': {'iron': 200, 'fuel': 150},
            'power': 300,
            'range': 1000,
            'type': 'naval',
            'description': 'کنترل دریاها'
        },
        'air_defense': {
            'name': 'پدافند هوایی',
            'cost': 30000,
            'resources': {'copper': 100, 'iron': 80},
            'power': 250,
            'range': 0,
            'type': 'defense',
            'defense_bonus': {'air': 0.4},
            'description': 'دفاع در برابر حملات هوایی'
        },
        'missile_shield': {
            'name': 'سپر موشکی',
            'cost': 35000,
            'resources': {'uranium': 30, 'iron': 120},
            'power': 300,
            'range': 0,
            'type': 'defense',
            'defense_bonus': {'missile': 0.5},
            'description': 'دفاع در برابر موشک‌ها'
        },
        'cyber_shield': {
            'name': 'سپر سایبری',
            'cost': 20000,
            'resources': {'lithium': 60, 'copper': 80},
            'power': 180,
            'range': 0,
            'type': 'defense',
            'defense_bonus': {'cyber': 0.6},
            'description': 'دفاع در برابر حملات سایبری'
        }
    }
    
    # Game balance constants
    GAME_BALANCE = {
        'initial_money': 100000,
        'initial_population': 1000000,
        'initial_soldiers': 0,
        'income_cycle_hours': 6,
        'max_convoy_time_hours': 12,
        'battle_randomness_factor': (0.8, 1.2),
        'resource_steal_factor': 0.3,
        'defender_loss_multiplier': 10,
        'attacker_loss_multiplier': 5
    }
    
    # Resource types and their properties
    RESOURCES = {
        'iron': {
            'name': 'آهن',
            'emoji': '🔩',
            'market_value': 10,
            'category': 'metal'
        },
        'copper': {
            'name': 'مس',
            'emoji': '🥉',
            'market_value': 12,
            'category': 'metal'
        },
        'oil': {
            'name': 'نفت خام',
            'emoji': '🛢',
            'market_value': 15,
            'category': 'energy'
        },
        'gas': {
            'name': 'گاز طبیعی',
            'emoji': '⛽',
            'market_value': 13,
            'category': 'energy'
        },
        'aluminum': {
            'name': 'آلومینیوم',
            'emoji': '🔗',
            'market_value': 11,
            'category': 'metal'
        },
        'gold': {
            'name': 'طلا',
            'emoji': '🏆',
            'market_value': 50,
            'category': 'precious'
        },
        'uranium': {
            'name': 'اورانیوم',
            'emoji': '☢️',
            'market_value': 100,
            'category': 'nuclear'
        },
        'lithium': {
            'name': 'لیتیوم',
            'emoji': '🔋',
            'market_value': 80,
            'category': 'tech'
        },
        'coal': {
            'name': 'زغال‌سنگ',
            'emoji': '⚫',
            'market_value': 8,
            'category': 'energy'
        },
        'silver': {
            'name': 'نقره',
            'emoji': '🥈',
            'market_value': 45,
            'category': 'precious'
        },
        'fuel': {
            'name': 'سوخت',
            'emoji': '⛽',
            'market_value': 20,
            'category': 'processed'
        }
    }
    
    # Admin configuration
    ADMIN_CONFIG = {
        'default_admin_ids': [123456789],  # Replace with actual admin user IDs
        'max_logs_display': 50,
        'reset_confirmation_required': True,
        'log_all_actions': True
    }
    
    # Combat system configuration
    COMBAT_CONFIG = {
        'neighbor_attack_always_allowed': True,
        'long_range_threshold_km': 3000,
        'base_defense_multiplier': 0.3,
        'weapon_loss_chance_defender': 0.3,
        'weapon_loss_chance_attacker': 0.15,
        'min_damage_factor': 0.1,
        'convoy_attack_detection_range': 2000
    }
    
    # Country relationships (neighbors)
    COUNTRY_NEIGHBORS = {
        'IR': ['TR', 'IQ', 'AF', 'PK'],  # Iran
        'TR': ['IR', 'IQ', 'SY', 'GR'],  # Turkey
        'RU': ['CN', 'KP', 'DE', 'FI'],  # Russia
        'CN': ['RU', 'KP', 'JP', 'IN'],  # China
        'US': ['MX', 'CA'],  # USA
        'MX': ['US'],  # Mexico
        'FR': ['DE', 'ES', 'BE', 'IT'],  # France
        'DE': ['FR', 'RU', 'BE'],  # Germany
        'ES': ['FR'],  # Spain
        'BE': ['FR', 'DE'],  # Belgium
        'JP': ['CN', 'KP'],  # Japan
        'KP': ['CN', 'RU', 'JP'],  # North Korea
        'EG': ['SA'],  # Egypt
        'AR': [],  # Argentina (isolated for game balance)
        'IT': ['FR'],  # Italy
        'BR': ['AR'],  # Brazil
        'IN': ['CN', 'PK'],  # India
        'GB': [],  # Great Britain (island)
        'CA': ['US'],  # Canada
        'AU': [],  # Australia (isolated)
        'SA': ['EG', 'IQ'],  # Saudi Arabia
        'PK': ['IR', 'IN', 'AF'],  # Pakistan
        'AF': ['IR', 'PK'],  # Afghanistan
        'IQ': ['IR', 'TR', 'SA']  # Iraq
    }
    
    # Country distances (simplified, in kilometers)
    COUNTRY_DISTANCES = {
        ('IR', 'TR'): 800,
        ('IR', 'RU'): 2000,
        ('IR', 'CN'): 3000,
        ('IR', 'US'): 12000,
        ('IR', 'JP'): 6000,
        ('IR', 'DE'): 4000,
        ('IR', 'FR'): 4500,
        ('IR', 'EG'): 2000,
        ('IR', 'AR'): 15000,
        ('IR', 'IQ'): 500,
        ('IR', 'AF'): 600,
        ('IR', 'PK'): 1000,
        ('US', 'MX'): 500,
        ('US', 'RU'): 8000,
        ('US', 'CN'): 11000,
        ('US', 'JP'): 10000,
        ('US', 'DE'): 6000,
        ('US', 'FR'): 6000,
        ('US', 'CA'): 300,
        ('RU', 'CN'): 3000,
        ('RU', 'JP'): 4000,
        ('RU', 'DE'): 1600,
        ('RU', 'FR'): 2500,
        ('RU', 'KP'): 2000,
        ('CN', 'JP'): 1500,
        ('CN', 'KP'): 800,
        ('CN', 'IN'): 2000,
        ('DE', 'FR'): 600,
        ('DE', 'BE'): 300,
        ('FR', 'ES'): 700,
        ('FR', 'BE'): 400,
        ('FR', 'IT'): 900,
        ('JP', 'KP'): 1000,
        ('EG', 'SA'): 1500,
        ('IN', 'PK'): 500,
        ('PK', 'AF'): 400,
        ('IQ', 'SA'): 800,
        ('IQ', 'TR'): 700,
        ('BR', 'AR'): 2000
    }
    
    # Bot configuration
    BOT_CONFIG = {
        'news_channel': '@Dragon0RP',
        'button_timeout_seconds': 300,
        'max_message_length': 4096,
        'income_cycle_interval_hours': 6,
        'convoy_update_interval_minutes': 30,
        'max_players_per_page': 10
    }
    
    # UI Messages in Persian
    MESSAGES = {
        'welcome': """🎮 خوش آمدید به جنگ جهانی - DragonRP!

در این بازی استراتژیک، شما یک کشور را کنترل می‌کنید.
هدف: ساختن اقتصاد، تولید منابع، ایجاد ارتش و تسلط بر دیگر کشورها

لطفاً کشور خود را انتخاب کنید:""",
        
        'country_taken': "❌ این کشور قبلاً انتخاب شده است. لطفاً کشور دیگری انتخاب کنید.",
        
        'country_selected': """🎉 تبریک! شما با موفقیت کشور {country_name} را انتخاب کردید.

جمعیت اولیه: 1,000,000 نفر
پول اولیه: 100,000 دلار

حالا می‌توانید شروع به ساختن اقتصاد خود کنید!""",
        
        'insufficient_funds': "❌ پول کافی ندارید! نیاز: ${cost:,}, موجود: ${available:,}",
        
        'building_constructed': "✅ {building_name} با موفقیت ساخته شد!",
        
        'weapon_produced': "✅ {weapon_name} تولید شد!",
        
        'attack_successful': "🎯 حمله موفق بود!",
        
        'attack_failed': "🛡 حمله دفع شد!",
        
        'invalid_command': "❌ دستور نامعتبر است!"
    }

    @classmethod
    def get_country_distance(cls, country1, country2):
        """Get distance between two countries"""
        if country1 == country2:
            return 0
            
        # Try both directions in the distance matrix
        distance = cls.COUNTRY_DISTANCES.get((country1, country2))
        if distance is None:
            distance = cls.COUNTRY_DISTANCES.get((country2, country1))
            
        # Return default distance if not found
        return distance if distance is not None else 5000
    
    @classmethod
    def are_countries_neighbors(cls, country1, country2):
        """Check if two countries are neighbors"""
        neighbors = cls.COUNTRY_NEIGHBORS.get(country1, [])
        return country2 in neighbors
    
    @classmethod
    def get_resource_emoji(cls, resource_type):
        """Get emoji for resource type"""
        return cls.RESOURCES.get(resource_type, {}).get('emoji', '📦')
    
    @classmethod
    def get_building_cost(cls, building_type):
        """Get cost of a building"""
        return cls.BUILDINGS.get(building_type, {}).get('cost', 0)
    
    @classmethod
    def get_weapon_cost(cls, weapon_type):
        """Get cost of a weapon"""
        return cls.WEAPONS.get(weapon_type, {}).get('cost', 0)
    
    @classmethod
    def get_weapon_power(cls, weapon_type):
        """Get power of a weapon"""
        return cls.WEAPONS.get(weapon_type, {}).get('power', 0)
    
    @classmethod
    def get_weapon_range(cls, weapon_type):
        """Get range of a weapon"""
        return cls.WEAPONS.get(weapon_type, {}).get('range', 0)

