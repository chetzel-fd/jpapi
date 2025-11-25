# JPAPI Relationship Analyzer

A standalone Streamlit dashboard for analyzing JAMF Pro object relationships, finding orphaned objects, and performing pre-deletion impact analysis.

## Features

### 🔍 Individual Analysis
- Analyze relationships for a single object
- See what objects it uses
- See what objects use it
- View dependency tree visualization

### 📊 Batch Analysis
- Analyze multiple objects simultaneously
- Identify shared dependencies
- View dependency matrix
- Export relationship reports

### ⚠️ Orphan Finder
- Find objects with no references (unused groups, scripts, packages)
- Filter by object type and age
- Generate cleanup recommendations
- Export orphan list to CSV

### 💥 Impact Analysis
- Assess pre-deletion impact
- Calculate risk level (Low/Medium/High)
- List all affected objects
- Get recommendations before deletion

## Launch

```bash
# From project root
streamlit run src/apps/streamlit_ui/jpapi_analyzer.py

# Or if in the streamlit_ui directory
streamlit run jpapi_analyzer.py
```

## Architecture

Built with SOLID principles following the same pattern as jpapi_manager:

- **Single Responsibility**: Each component has one job
- **Open/Closed**: Extensible without modification
- **Liskov Substitution**: Interfaces allow swapping implementations
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depends on abstractions, not concrete classes

## Components

### Core Interfaces (`analyzer_interfaces.py`)
- `RelationshipEngine` - Analyzes object relationships
- `OrphanDetector` - Finds unused objects
- `ImpactAnalyzer` - Assesses deletion impact
- `DataProvider` - Loads data from CSV/API
- `AnalyzerUIController` - Renders UI

### Implementations
- `CSVRelationshipEngine` - Analyzes CSV data
- `CSVOrphanDetector` - Finds orphans in CSV data
- `CSVImpactAnalyzer` - Assesses impact from CSV data
- `AnalyzerDataProvider` - Loads data (reuses jpapi_manager code)
- `ReverseObjectAnalyzerController` - Main UI controller

### Configuration (`analyzer_config.json`)
- Relationship mappings (what can use what)
- Orphan detection settings
- Risk level thresholds
- API mode configuration (optional)

### Styles (`analyzer_styles.py`)
- Gabagool Brand theme (navy, blue, yellow)
- Reuses base theme from jpapi_manager
- Analyzer-specific card styles

## Data Sources

### CSV Mode (Default)
- Reads from `storage/exports/` directory
- No API calls required
- Fast and safe

### API Mode (Optional)
- Enable in `analyzer_config.json`
- Set `"api_mode": {"enabled": true}`
- Makes live API calls to JAMF Pro
- Rate limited and cached

## Reused Code from jpapi_manager

The analyzer reuses existing infrastructure:

- ✅ `data_loader.py` - CSV parsing
- ✅ `ui_styles.py` - Base theme
- ✅ `ui_utils.py` - Utility functions
- ✅ `core/config/object_types.json` - Object type definitions
- ✅ `core/services/` - Environment and object type services

## Usage Examples

### Find Orphaned Scripts
1. Select "⚠️ Orphans" mode
2. Choose "Scripts Only"
3. Click "🔍 Scan for Orphans"
4. Review results and export CSV if needed

### Assess Deletion Impact
1. Select "💥 Impact" mode
2. Choose object type (e.g., "policies")
3. Select specific object
4. Click "💥 Assess Impact"
5. Review risk level and recommendations

### Analyze Policy Relationships
1. Select "🔍 Individual" mode
2. Choose "policies"
3. Select a policy
4. Click "🔍 Analyze Relationships"
5. See what groups, scripts, packages it uses
6. See if any other objects reference it

## Configuration

Edit `analyzer_config.json` to customize:

```json
{
  "orphan_detection": {
    "min_age_days": 30,
    "exclude_patterns": ["All Computers", "All Managed"]
  },
  "impact_analysis": {
    "risk_levels": {
      "low": {"max_affected": 5},
      "medium": {"max_affected": 20},
      "high": {"max_affected": 999999}
    }
  }
}
```

## Future Enhancements

- Integration with jpapi_manager (add "Analyze" button)
- Visual dependency graphs (graphviz/mermaid)
- Bulk cleanup automation
- PDF export reports
- Comparison mode (sandbox vs production)
- Change tracking over time

## Troubleshooting

### No data showing
- Ensure CSV exports exist in `storage/exports/`
- Run `jpapi export` commands to generate data

### Relationships not detected
- Check that CSV exports include scope/dependency information
- Verify object type configurations in `analyzer_config.json`

### Performance issues
- Reduce orphan detection age threshold
- Disable API mode if enabled
- Clear cache with environment switch

## Development

To extend the analyzer:

1. Add new interface in `analyzer_interfaces.py`
2. Implement concrete class
3. Inject into controller via constructor
4. Add UI rendering method to controller
5. Update main app to use new mode

Example:

```python
# Add new analyzer interface
class CustomAnalyzer(ABC):
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        pass

# Implement it
class MyCustomAnalyzer(CustomAnalyzer):
    def analyze(self) -> Dict[str, Any]:
        return {"result": "data"}

# Inject into controller
controller = ReverseObjectAnalyzerController(
    custom_analyzer=MyCustomAnalyzer(),
    # ... other dependencies
)
```

## License

Same as jpapi project.








