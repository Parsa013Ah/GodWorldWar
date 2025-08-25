
import asyncio
import logging
from database import Database
from admin import AdminPanel
from game_logic import GameLogic
from economy import Economy
from combat import CombatSystem
from convoy import ConvoySystem
from marketplace import Marketplace
from alliance import AllianceSystem
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotTester:
    def __init__(self):
        self.db = Database()
        self.admin = AdminPanel(self.db)
        self.game_logic = GameLogic(self.db)
        self.economy = Economy(self.db)
        self.combat = CombatSystem(self.db)
        self.convoy = ConvoySystem(self.db)
        self.marketplace = Marketplace(self.db)
        self.alliance = AllianceSystem(self.db)
        
        # Test user IDs
        self.test_users = [
            {'user_id': 123456, 'username': 'test_user1', 'country': 'IR'},
            {'user_id': 123457, 'username': 'test_user2', 'country': 'TR'},
            {'user_id': 123458, 'username': 'test_user3', 'country': 'US'}
        ]

    def log_test(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
        return success

    def test_database_initialization(self):
        """Test database initialization"""
        try:
            self.db.initialize()
            return self.log_test("Database Initialization", True, "Database tables created successfully")
        except Exception as e:
            return self.log_test("Database Initialization", False, str(e))

    def test_player_creation(self):
        """Test player creation"""
        success_count = 0
        for user in self.test_users:
            try:
                result = self.db.create_player(user['user_id'], user['username'], user['country'])
                if result:
                    success_count += 1
                    self.log_test(f"Player Creation - {user['username']}", True, "Player created successfully")
                else:
                    self.log_test(f"Player Creation - {user['username']}", False, "Failed to create player")
            except Exception as e:
                self.log_test(f"Player Creation - {user['username']}", False, str(e))
        
        return success_count == len(self.test_users)

    def test_building_construction(self):
        """Test building construction"""
        user_id = self.test_users[0]['user_id']
        
        # Give player enough money first
        player = self.db.get_player(user_id)
        if player:
            self.db.update_player_money(user_id, player['money'] + 500000)
        
        # Test all building types
        buildings_to_test = ['iron_mine', 'weapon_factory', 'wheat_farm', 'military_base']
        success_count = 0
        
        for building in buildings_to_test:
            try:
                result = self.game_logic.build_structure(user_id, building)
                if result and result.get('success', False):
                    success_count += 1
                    self.log_test(f"Building Construction - {building}", True, result.get('message', 'Built successfully'))
                else:
                    message = result.get('message', 'Unknown error') if result else 'No result returned'
                    self.log_test(f"Building Construction - {building}", False, message)
            except Exception as e:
                self.log_test(f"Building Construction - {building}", False, str(e))
        
        return success_count == len(buildings_to_test)

    def test_weapon_production(self):
        """Test weapon production"""
        user_id = self.test_users[0]['user_id']
        
        # Add some resources first
        self.db.add_resources(user_id, 'iron', 1000)
        self.db.add_resources(user_id, 'copper', 1000)
        
        weapons_to_test = ['rifle', 'tank', 'drone']
        success_count = 0
        
        for weapon in weapons_to_test:
            try:
                result = self.game_logic.produce_weapon(user_id, weapon)
                if result['success']:
                    success_count += 1
                    self.log_test(f"Weapon Production - {weapon}", True, result['message'])
                else:
                    self.log_test(f"Weapon Production - {weapon}", False, result['message'])
            except Exception as e:
                self.log_test(f"Weapon Production - {weapon}", False, str(e))
        
        return success_count == len(weapons_to_test)

    def test_economy_calculations(self):
        """Test economy calculations"""
        user_id = self.test_users[0]['user_id']
        
        try:
            # Test income calculation
            income = self.economy.calculate_income(user_id)
            self.log_test("Economy - Income Calculation", True, f"Income calculated: ${income}")
            
            # Test population increase
            pop_increase = self.economy.calculate_population_increase(user_id)
            self.log_test("Economy - Population Increase", True, f"Population increase: {pop_increase}")
            
            # Test soldier increase
            soldier_increase = self.economy.calculate_soldier_increase(user_id)
            self.log_test("Economy - Soldier Increase", True, f"Soldier increase: {soldier_increase}")
            
            return True
        except Exception as e:
            return self.log_test("Economy Calculations", False, str(e))

    def test_convoy_system(self):
        """Test convoy system"""
        sender_id = self.test_users[0]['user_id']
        receiver_id = self.test_users[1]['user_id']
        
        try:
            # Give sender some money first
            sender = self.db.get_player(sender_id)
            if sender:
                self.db.update_player_money(sender_id, sender['money'] + 10000)
                self.db.add_resources(sender_id, 'iron', 1000)
            
            # Create convoy
            resources = {'money': 1000, 'iron': 500}
            result = self.convoy.create_convoy(sender_id, receiver_id, resources)
            
            if result.get('success', False):
                convoy_id = result['convoy_id']
                self.log_test("Convoy Creation", True, f"Convoy created with ID: {convoy_id}")
                
                # Test convoy details
                convoy = self.db.get_convoy(convoy_id)
                if convoy:
                    self.log_test("Convoy Retrieval", True, "Convoy details retrieved successfully")
                    return True
                else:
                    return self.log_test("Convoy Retrieval", False, "Failed to retrieve convoy details")
            else:
                return self.log_test("Convoy Creation", False, result.get('message', 'Unknown error'))
                
        except Exception as e:
            return self.log_test("Convoy System", False, str(e))

    def test_marketplace(self):
        """Test marketplace functionality"""
        seller_id = self.test_users[0]['user_id']
        buyer_id = self.test_users[1]['user_id']
        
        try:
            # Add some resources to seller
            self.db.add_resources(seller_id, 'iron', 2000)
            
            # Create listing
            result = self.marketplace.create_listing(seller_id, 'iron', 'resources', 1000, 10)
            
            if result['success']:
                self.log_test("Marketplace - Create Listing", True, "Listing created successfully")
                
                # Get listings
                listings = self.marketplace.get_listings_by_category('resources')
                if listings:
                    listing_id = listings[0]['id']
                    self.log_test("Marketplace - Get Listings", True, f"Found {len(listings)} listings")
                    
                    # Add money to buyer
                    buyer = self.db.get_player(buyer_id)
                    self.db.update_player_money(buyer_id, buyer['money'] + 50000)
                    
                    # Test purchase
                    purchase_result = self.marketplace.purchase_item(buyer_id, listing_id, 100)
                    
                    if purchase_result['success']:
                        self.log_test("Marketplace - Purchase Item", True, "Item purchased successfully")
                        return True
                    else:
                        return self.log_test("Marketplace - Purchase Item", False, purchase_result['message'])
                else:
                    return self.log_test("Marketplace - Get Listings", False, "No listings found")
            else:
                return self.log_test("Marketplace - Create Listing", False, result['message'])
                
        except Exception as e:
            return self.log_test("Marketplace", False, str(e))

    def test_admin_functions(self):
        """Test admin functions"""
        admin_id = self.test_users[0]['user_id']
        target_id = self.test_users[1]['user_id']
        
        try:
            # Test giving resources
            result = self.admin.give_resources_to_player(target_id, 'gold', 100)
            if result['success']:
                self.log_test("Admin - Give Resources", True, result['message'])
            else:
                return self.log_test("Admin - Give Resources", False, result['message'])
            
            # Test giving money
            result = self.admin.give_money_to_player(target_id, 50000)
            if result['success']:
                self.log_test("Admin - Give Money", True, result['message'])
            else:
                return self.log_test("Admin - Give Money", False, result['message'])
            
            # Test giving weapons
            result = self.admin.give_weapons_to_player(target_id, 'rifle', 10)
            if result['success']:
                self.log_test("Admin - Give Weapons", True, result['message'])
                return True
            else:
                return self.log_test("Admin - Give Weapons", False, result['message'])
                
        except Exception as e:
            return self.log_test("Admin Functions", False, str(e))

    def test_combat_system(self):
        """Test combat system"""
        attacker_id = self.test_users[0]['user_id']
        defender_id = self.test_users[1]['user_id']
        
        try:
            # Add some weapons to attacker
            self.db.add_weapon(attacker_id, 'rifle', 100)
            self.db.add_weapon(attacker_id, 'tank', 10)
            
            # Get available targets
            targets = self.combat.get_available_targets(attacker_id)
            if targets:
                self.log_test("Combat - Get Targets", True, f"Found {len(targets)} available targets")
                
                # Test attack power calculation
                attack_power = self.combat.calculate_attack_power(attacker_id)
                self.log_test("Combat - Attack Power", True, f"Attack power: {attack_power}")
                
                # Test defense power calculation
                defense_power = self.combat.calculate_defense_power(defender_id)
                self.log_test("Combat - Defense Power", True, f"Defense power: {defense_power}")
                
                return True
            else:
                return self.log_test("Combat - Get Targets", False, "No available targets found")
                
        except Exception as e:
            return self.log_test("Combat System", False, str(e))

    def test_alliance_system(self):
        """Test alliance system"""
        leader_id = self.test_users[0]['user_id']
        member_id = self.test_users[1]['user_id']
        
        try:
            # Create alliance
            result = self.alliance.create_alliance(leader_id, "Test Alliance")
            if result['success']:
                self.log_test("Alliance - Create", True, result['message'])
                
                # Invite member
                invite_result = self.alliance.invite_to_alliance(leader_id, member_id)
                if invite_result['success']:
                    self.log_test("Alliance - Invite", True, invite_result['message'])
                    
                    # Get invitations
                    invitations = self.alliance.get_pending_invitations(member_id)
                    if invitations:
                        invitation_id = invitations[0]['id']
                        self.log_test("Alliance - Get Invitations", True, f"Found {len(invitations)} invitations")
                        
                        # Accept invitation
                        accept_result = self.alliance.respond_to_invitation(member_id, invitation_id, 'accept')
                        if accept_result['success']:
                            self.log_test("Alliance - Accept Invitation", True, accept_result['message'])
                            return True
                        else:
                            return self.log_test("Alliance - Accept Invitation", False, accept_result['message'])
                    else:
                        return self.log_test("Alliance - Get Invitations", False, "No invitations found")
                else:
                    return self.log_test("Alliance - Invite", False, invite_result['message'])
            else:
                return self.log_test("Alliance - Create", False, result['message'])
                
        except Exception as e:
            return self.log_test("Alliance System", False, str(e))

    def test_first_build_tracking(self):
        """Test first build tracking system"""
        user_id = self.test_users[2]['user_id']  # Use third user for clean test
        
        try:
            # Give user money for building
            player = self.db.get_player(user_id)
            if player:
                self.db.update_player_money(user_id, player['money'] + 200000)
                
                # Test first build
                is_first = self.db.check_first_build(user_id, 'iron_mine')
                self.log_test("First Build Check - Before", is_first, f"Is first build: {is_first}")
                
                if is_first:
                    # Record first build
                    self.db.record_first_build(user_id, 'iron_mine')
                    self.log_test("First Build Record", True, "First build recorded")
                    
                    # Check again
                    is_still_first = self.db.check_first_build(user_id, 'iron_mine')
                    if not is_still_first:
                        self.log_test("First Build Check - After", True, f"Is first build after recording: {is_still_first}")
                        return True
                    else:
                        return self.log_test("First Build Check - After", False, "Still showing as first build")
                else:
                    return self.log_test("First Build Check - Before", False, "Should be first build but isn't")
            else:
                return self.log_test("First Build Tracking", False, "Player not found")
                
        except Exception as e:
            return self.log_test("First Build Tracking", False, str(e))

    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting comprehensive bot tests...")
        
        # Clear any existing test data first
        logger.info("🧹 Clearing existing test data...")
        self.db.clear_test_data()
        
        tests = [
            ("Database Initialization", self.test_database_initialization),
            ("Player Creation", self.test_player_creation),
            ("Building Construction", self.test_building_construction),
            ("Weapon Production", self.test_weapon_production),
            ("Economy Calculations", self.test_economy_calculations),
            ("Convoy System", self.test_convoy_system),
            ("Marketplace", self.test_marketplace),
            ("Admin Functions", self.test_admin_functions),
            ("Combat System", self.test_combat_system),
            ("Alliance System", self.test_alliance_system),
            ("First Build Tracking", self.test_first_build_tracking)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing: {test_name}")
            logger.info('='*50)
            
            try:
                result = test_func()
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {e}")
        
        logger.info(f"\n{'='*50}")
        logger.info(f"TEST SUMMARY")
        logger.info('='*50)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.warning(f"⚠️  {total - passed} tests failed. Check logs above.")

if __name__ == "__main__":
    tester = BotTester()
    asyncio.run(tester.run_all_tests())
