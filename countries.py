from config import Config

class CountryManager:
    def __init__(self, database):
        self.db = database
    
    def get_available_countries(self):
        """Get list of available (untaken) countries"""
        taken_countries = self.get_taken_countries()
        available = {}
        
        for code, name in Config.COUNTRIES.items():
            if code not in taken_countries:
                available[code] = name
        
        return available
    
    def get_taken_countries(self):
        """Get list of taken country codes"""
        players = self.db.get_all_players()
        return [player['country_code'] for player in players]
    
    def get_country_info(self, country_code):
        """Get detailed country information"""
        if country_code not in Config.COUNTRIES:
            return None
        
        return {
            'code': country_code,
            'name': Config.COUNTRIES[country_code],
            'flag': Config.COUNTRY_FLAGS.get(country_code, '🏳'),
            'neighbors': self.get_country_neighbors(country_code),
            'continent': self.get_country_continent(country_code)
        }
    
    def get_country_neighbors(self, country_code):
        """Get neighboring countries"""
        neighbors_map = {
            'IR': ['TR', 'IQ', 'AF', 'PK'],  # Iran
            'TR': ['IR', 'IQ', 'SY', 'GR'],  # Turkey
            'RU': ['CN', 'KP', 'DE', 'FI'],  # Russia
            'CN': ['RU', 'KP', 'JP', 'IN'],  # China
            'US': ['MX', 'CA'],  # USA
            'MX': ['US', 'GT'],  # Mexico
            'FR': ['DE', 'ES', 'BE', 'IT'],  # France
            'DE': ['FR', 'RU', 'BE', 'PL'],  # Germany
            'ES': ['FR', 'PT'],  # Spain
            'BE': ['FR', 'DE', 'NL'],  # Belgium
            'JP': ['CN', 'KP'],  # Japan
            'KP': ['CN', 'RU', 'JP'],  # North Korea
            'EG': ['SA', 'LY', 'SD'],  # Egypt
            'AR': ['BR', 'CL', 'UY'],  # Argentina
        }
        
        return neighbors_map.get(country_code, [])
    
    def get_country_continent(self, country_code):
        """Get country continent"""
        continents = {
            'IR': 'آسیا',
            'TR': 'آسیا/اروپا',
            'RU': 'آسیا/اروپا',
            'CN': 'آسیا',
            'JP': 'آسیا',
            'KP': 'آسیا',
            'US': 'آمریکای شمالی',
            'MX': 'آمریکای شمالی',
            'AR': 'آمریکای جنوبی',
            'FR': 'اروپا',
            'DE': 'اروپا',
            'ES': 'اروپا',
            'BE': 'اروپا',
            'EG': 'آفریقا'
        }
        
        return continents.get(country_code, 'نامشخص')
    
    def calculate_distance(self, country1, country2):
        """Calculate approximate distance between countries"""
        # Simplified distance matrix (in km)
        distances = {
            ('IR', 'TR'): 800,
            ('IR', 'RU'): 2000,
            ('IR', 'CN'): 3000,
            ('IR', 'US'): 12000,
            ('IR', 'JP'): 6000,
            ('IR', 'DE'): 4000,
            ('IR', 'FR'): 4500,
            ('IR', 'EG'): 2000,
            ('IR', 'AR'): 15000,
            ('US', 'MX'): 500,
            ('US', 'RU'): 8000,
            ('US', 'CN'): 11000,
            ('US', 'JP'): 10000,
            ('US', 'DE'): 6000,
            ('US', 'FR'): 6000,
            ('RU', 'CN'): 3000,
            ('RU', 'JP'): 4000,
            ('RU', 'DE'): 1600,
            ('RU', 'FR'): 2500,
            ('CN', 'JP'): 1500,
            ('DE', 'FR'): 600,
            ('DE', 'BE'): 300,
            ('FR', 'ES'): 700,
            ('FR', 'BE'): 400,
        }
        
        # Try both directions
        distance = distances.get((country1, country2)) or distances.get((country2, country1))
        
        # Default distance if not found
        if not distance:
            if country1 == country2:
                return 0
            else:
                return 5000  # Default 5000km for unknown distances
        
        return distance
    
    def get_world_map_text(self):
        """Generate world map text representation"""
        players = self.db.get_all_players()
        
        map_text = "🗺 نقشه جهان DragonRP\n\n"
        
        # Group by continent
        continents = {}
        for player in players:
            continent = self.get_country_continent(player['country_code'])
            if continent not in continents:
                continents[continent] = []
            continents[continent].append(player)
        
        for continent, countries in continents.items():
            map_text += f"🌍 {continent}:\n"
            for player in countries:
                flag = Config.COUNTRY_FLAGS.get(player['country_code'], '🏳')
                map_text += f"  {flag} {player['country_name']} - {player['username']}\n"
            map_text += "\n"
        
        return map_text
    
    def get_country_relations(self, country_code):
        """Get relations with other countries"""
        # This would be expanded to include alliances, wars, etc.
        neighbors = self.get_country_neighbors(country_code)
        
        relations = {
            'neighbors': neighbors,
            'allies': [],  # Would be stored in database
            'enemies': [],  # Would be stored in database
            'neutral': []   # All others
        }
        
        return relations
    
    def validate_country_selection(self, user_id, country_code):
        """Validate country selection"""
        # Check if country exists
        if country_code not in Config.COUNTRIES:
            return False, "کشور نامعتبر"
        
        # Check if already taken
        if self.db.is_country_taken(country_code):
            return False, "این کشور قبلاً انتخاب شده است"
        
        # Check if user already has a country
        existing_player = self.db.get_player(user_id)
        if existing_player:
            return False, "شما قبلاً کشوری انتخاب کرده‌اید"
        
        return True, "انتخاب معتبر"
    
    def get_country_statistics(self, country_code):
        """Get statistics for a specific country"""
        player = None
        players = self.db.get_all_players()
        
        for p in players:
            if p['country_code'] == country_code:
                player = p
                break
        
        if not player:
            return None
        
        stats = {
            'country_name': player['country_name'],
            'username': player['username'],
            'population': player['population'],
            'money': player['money'],
            'soldiers': player['soldiers'],
            'founded': player['created_at'],
            'last_active': player['last_active']
        }
        
        return stats
