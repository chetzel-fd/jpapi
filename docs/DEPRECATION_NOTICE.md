# Deprecation Notice

## Export Command - DEPRECATED as of v2.0

### Summary
The standalone `export` command has been deprecated in favor of the unified `list` command with export functionality.

### Reason for Deprecation
- **Code Duplication**: Export and list had 90% overlapping functionality
- **Maintenance Burden**: Changes needed to be made in two places
- **User Confusion**: Unclear when to use export vs list
- **SOLID Principles**: Violates DRY (Don't Repeat Yourself)

### Migration Guide

#### Old Usage (DEPRECATED)
```bash
jpapi export policies
jpapi export scripts
jpapi export profiles
```

#### New Usage (RECOMMENDED)
```bash
jpapi list policies --export-mode
jpapi list scripts --export-mode
jpapi list profiles --export-mode
```

#### Seamless Transition (Using Alias)
The `export` alias now redirects to `list` automatically:
```bash
jpapi export policies  # Works but shows deprecation warning
# Internally calls: jpapi list policies --export-mode
```

### Changes Required

#### For CLI Users
- **Immediate**: No changes required - backward compatibility maintained
- **Recommended**: Update scripts to use `list` command instead
- **Future**: Export command will be removed in v3.0

#### For Streamlit UI (jpapi_manager)
- ✅ **UPDATED**: `data_exporter.py` now uses `list` with `--export-mode`
- No user-facing changes - works transparently

#### For Integration/Scripts
If you have automation scripts using the export command:
```bash
# Old (still works with deprecation warning)
jpapi --env prod export policies

# New (recommended)
jpapi --env prod list policies --export-mode

# Or use the export alias (auto-enables export mode)
jpapi --env prod export policies
```

### Timeline
- **v2.0** (Current): Export command deprecated, shows warnings
- **v2.x**: Deprecation warnings continue, backward compatibility maintained
- **v3.0** (Future): Export command will be removed entirely

### Technical Details

#### What Changed
1. `list_command.py` now includes all export functionality
2. `export_command.py` is now a thin wrapper that shows deprecation warning
3. `jpapi_main.py` registers "export" as an alias for "list"
4. Streamlit UI updated to use `list` instead of `export`

#### Files Modified
- `src/cli/commands/list_command.py` - Added export functionality
- `src/cli/commands/export_command.py` - Deprecated, shows warning
- `src/jpapi_main.py` - Updated command registration
- `src/apps/streamlit_ui/data_exporter.py` - Updated to use list

### Benefits of Migration
1. **Unified Interface**: Single command for listing and exporting
2. **Less Code**: Reduced duplication and maintenance burden
3. **Consistent Behavior**: All export logic in one place
4. **Better Performance**: No duplicate code execution
5. **Easier Testing**: Single code path to test

### Questions or Issues?
If you encounter any issues with the migration, please:
1. Check this deprecation notice
2. Review the migration guide above
3. Test with the `--export-mode` flag
4. Report any bugs or unexpected behavior

---

**Note**: All functionality remains 100% intact. This is purely a code organization improvement that simplifies the codebase while maintaining full backward compatibility.

