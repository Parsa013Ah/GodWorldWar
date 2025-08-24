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
        return Config.COUNTRY_NEIGHBORS.get(country_code, [])
    
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
            'CA': 'آمریکای شمالی',
            'AR': 'آمریکای جنوبی',
            'BR': 'آمریکای جنوبی',
            'FR': 'اروپا',
            'DE': 'اروپا',
            'ES': 'اروپا',
            'BE': 'اروپا',
            'IT': 'اروپا',
            'GB': 'اروپا',
            'EG': 'آفریقا',
            'SA': 'آسیا',
            'PK': 'آسیا',
            'AF': 'آسیا',
            'IQ': 'آسیا',
            'IN': 'آسیا',
            'AU': 'اقیانوسیه'
        }
        
        return continents.get(country_code, 'نامشخص')
    
    def calculate_distance(self, country1, country2):
        """Calculate approximate distance between countries"""
        return Config.get_country_distance(country1, country2)
    
    def are_neighbors(self, country1, country2):
        """Check if two countries are neighbors"""
        return Config.are_countries_neighbors(country1, country2)