# DragonRP Telegram Bot

## Overview

DragonRP is a strategic Telegram bot game where players take control of countries and engage in economic, military, and diplomatic activities. Players can build infrastructure, produce weapons, manage resources, and interact with other nations in a real-time multiplayer environment. The game features a comprehensive economy system, combat mechanics, and administrative tools for game management.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (August 26, 2025)

### Bug Fixes and Improvements:
1. **Fixed marketplace delivery system**: Improved weapon delivery success rates from 50% minimum to 70% minimum, with partial refunds (50%) for failed deliveries
2. **Enhanced marketplace transparency**: Added delivery success chance indicators (🟢🟡🔴) in weapon listings
3. **Added purchase history feature**: Players can now view their transaction history to see why weapons may not have been delivered
4. **Fixed AttributeError**: Resolved 'NoneType' error in handle_message function
5. **Added comprehensive logging**: Enhanced weapon production debugging to track the exact flow of weapon additions to player inventory

### Current Issue Being Diagnosed:
- User reports weapons not being added after production despite success messages
- Added detailed logging to track weapon production flow and identify root cause
- Investigating potential database transaction issues or weapon table structure problems

## System Architecture

### Core Architecture Pattern
The application follows a modular architecture with clear separation of concerns. Each major game system is implemented as a separate class with its own responsibilities:

- **Database Layer**: SQLite-based persistence with a dedicated Database class handling all data operations
- **Game Logic Layer**: Business logic separated into specialized managers (GameLogic, Economy, CombatSystem, CountryManager)
- **Bot Interface Layer**: Telegram bot integration with keyboard handlers and command processors
- **Admin Layer**: Administrative tools with role-based access control

### Data Storage Design
The system uses SQLite as the primary database with the following key tables:
- **Players**: Core player information including country assignments, money, population, and soldiers
- **Resources**: Natural resources like iron, oil, uranium with quantity tracking
- **Buildings**: Infrastructure tracking (mines, factories, military bases)
- **Weapons**: Military equipment inventory (tanks, jets, missiles)
- **Combat Logs**: Historical battle records and outcomes

### Game Systems Architecture

**Economic System**: 
- Automated income calculation every 6 hours based on building ownership
- Resource production from mines with realistic yield rates
- Population growth mechanics tied to wheat farm construction
- Building cost/benefit analysis with percentage-based returns

**Military System**:
- Combat power calculation combining multiple weapon types
- Defense mechanisms with type-specific bonuses (air defense, missile shields)
- Attack type categorization (ground, air, naval, missile, mixed)
- Soldier recruitment through military base infrastructure

**Administrative System**:
- Role-based admin access with hardcoded admin user IDs
- Game statistics monitoring and player management tools
- Data reset capabilities for game maintenance
- Comprehensive logging for audit trails

### Bot Interface Design
The Telegram integration uses the python-telegram-bot library with:
- **Inline Keyboards**: Dynamic menu systems for game interactions
- **Callback Handlers**: Asynchronous event processing for user actions
- **Scheduled Tasks**: APScheduler for periodic income distribution and game updates
- **News Broadcasting**: Automated announcements to a dedicated Telegram channel

### Country Management
Players select from 24 predefined countries with realistic geographic relationships:
- **Unique Assignment**: Each country can only be controlled by one player
- **Neighbor System**: Geographic proximity affects diplomatic and military interactions
- **Cultural Localization**: All content presented in Persian language with appropriate country flags

## External Dependencies

### Core Framework Dependencies
- **python-telegram-bot**: Telegram Bot API integration for user interface and messaging
- **APScheduler**: Asynchronous task scheduling for periodic game events (income distribution, updates)
- **SQLite3**: Built-in database engine for persistent data storage

### Game Configuration
- **Static Configuration**: All game constants (weapon stats, building costs, country data) defined in Config class
- **No External APIs**: Game operates independently without external service dependencies
- **Local File Storage**: Database and logs stored locally on the server

### Communication Infrastructure
- **Telegram Bot API**: Primary interface for player interactions
- **News Channel Integration**: Broadcasts game events to @Dragon0RP Telegram channel
- **Logging System**: Python logging module for debugging and audit trails

### Scalability Considerations
The current architecture uses SQLite which is suitable for small to medium player bases. The modular design allows for future migration to PostgreSQL or other databases if needed. The bot token and admin configurations are environment-variable ready for deployment flexibility.