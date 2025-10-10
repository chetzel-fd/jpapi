# SOLID Dashboard Architecture Plan

## Current Problems:
1. **File too large** (800+ lines)
2. **Mixed responsibilities** (UI + data + business logic)
3. **Hard to test** (tightly coupled)
4. **Hard to extend** (monolithic structure)
5. **Environment switching broken** (complex logic)

## Proposed SOLID Architecture:

### 1. Data Layer (SRP)
```
src/apps/streamlit/dashboards/
├── data/
│   ├── __init__.py
│   ├── data_loader.py          # Interface
│   ├── csv_loader.py          # CSV implementation
│   ├── cache_manager.py       # Caching logic
│   └── data_validator.py      # Data validation
```

### 2. Business Logic Layer (SRP)
```
├── services/
│   ├── __init__.py
│   ├── environment_service.py  # Environment management
│   ├── object_type_service.py  # Object type logic
│   └── export_service.py       # Export functionality
```

### 3. UI Layer (SRP)
```
├── ui/
│   ├── __init__.py
│   ├── components/
│   │   ├── header.py          # Header component
│   │   ├── controls.py        # Control components
│   │   ├── object_cards.py    # Object display
│   │   └── settings.py        # Settings popover
│   └── pages/
│       └── dashboard.py       # Main dashboard
```

### 4. Configuration (DIP)
```
├── config/
│   ├── __init__.py
│   ├── settings.py            # App settings
│   └── paths.py              # Path configuration
```

## SOLID Compliance:

### Single Responsibility Principle ✅
- **DataLoader**: Only loads data
- **EnvironmentService**: Only manages environments
- **ObjectCards**: Only renders object cards
- **CacheManager**: Only handles caching

### Open/Closed Principle ✅
- **DataLoader Interface**: Easy to add new data sources
- **Component System**: Easy to add new UI components
- **Service Layer**: Easy to add new business logic

### Liskov Substitution Principle ✅
- **DataLoaders**: All implement same interface
- **Services**: All implement same contracts

### Interface Segregation Principle ✅
- **Small interfaces**: Each interface has one purpose
- **Focused contracts**: No fat interfaces

### Dependency Inversion Principle ✅
- **Depend on abstractions**: Services depend on interfaces
- **Injection**: Dependencies injected, not hardcoded
- **Testable**: Easy to mock dependencies

## Implementation Plan:

### Phase 1: Extract Data Layer
1. Create `DataLoader` interface
2. Create `CSVLoader` implementation
3. Create `CacheManager`
4. Update main dashboard to use new data layer

### Phase 2: Extract Services
1. Create `EnvironmentService`
2. Create `ObjectTypeService`
3. Create `ExportService`
4. Update dashboard to use services

### Phase 3: Extract UI Components
1. Create component classes
2. Extract styling
3. Create page structure
4. Update main dashboard

### Phase 4: Configuration
1. Create configuration system
2. Environment-specific settings
3. Path management
4. Feature flags

## Benefits:
- **Maintainable**: Each class has one responsibility
- **Testable**: Easy to unit test each component
- **Extensible**: Easy to add new features
- **Readable**: Clear separation of concerns
- **Debuggable**: Easy to isolate issues
