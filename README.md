# Persona 3 Reload | Save Editor

## UPDATE: Major Enhancement for All Versions
This save editor now features comprehensive improvements for compatibility with different game versions and save formats:

1. **Automatic Save Format Detection**: Intelligently detects whether your save uses the original format or the newer format with +4 offset for all IDs
2. **Complete Party Member Support**: Now supports ALL party members including Aigis, Ken, Koromaru, and Shinjiro
3. **Intelligent Character Detection**: Only shows characters that are actually unlocked in your save file
4. **Enhanced Playtime Handling**: Multiple detection methods to find and display playtime correctly in all save formats
5. **Robust Error Recovery**: Better handling of file operations to prevent crashes

## Project Structure

This project contains several files for different purposes:

- **Editor.py**: Core editor functionality with all logic for reading, editing, and saving files
- **p3r_editor.py**: Standard launcher with good error handling and a simple interface
- **enhanced_p3r_editor_fixed.py**: Enhanced launcher with colorful terminal output
- **SavConverter/**: Libraries for converting between .sav and .json formats
- **run_editor.bat**: Windows batch file for launching the standard editor
- **run_enhanced_editor.bat**: Windows batch file for launching the enhanced editor
- **build.bat**: Build script for creating standalone executables

## User-Friendly Launchers
Two launcher options are available for different user preferences:

### Standard Launcher
The `p3r_editor.py` script makes launching the editor easy and reliable:
- Better error handling to prevent crashes
- Proper handling of file paths
- Automatic save format detection
- Clear, user-friendly prompts

**For Windows users:** Simply run the `run_editor.bat` file to start the standard launcher.
**For other users:** Run `python p3r_editor.py` from your terminal.

### Enhanced Launcher
The `enhanced_p3r_editor_fixed.py` script offers an improved visual experience:
- Colorful terminal output
- More detailed save information
- Enhanced error handling
- Better visualization of save format information

**For Windows users:** Simply run the `run_enhanced_editor.bat` file to start the enhanced launcher.
**For other users:** Run `python enhanced_p3r_editor_fixed.py` from your terminal.

## Creating Standalone Executables

If you want to create standalone executable files (no Python installation required):

### Prerequisites
1. Python 3.6 or higher installed
2. PyInstaller package installed (`pip install pyinstaller`)

### Automatic Build Process
1. Open a command prompt in the project directory
2. Run `build.bat`
3. Wait for the build process to complete
4. Find the executables in the `build` folder:
   - `P3R_Save_Editor.exe` (Standard version)
   - `P3R_Enhanced_Editor.exe` (Enhanced version)

### Manual Build Process
If you prefer to build manually or are on a non-Windows platform:

```
# For Standard Editor
pyinstaller --clean --onefile --name "P3R_Save_Editor" p3r_editor.py

# For Enhanced Editor
pyinstaller --clean --onefile --name "P3R_Enhanced_Editor" enhanced_p3r_editor_fixed.py
```

### Troubleshooting Builds
- Ensure PyInstaller is properly installed: `pip install --upgrade pyinstaller`
- Check for dependency issues by running the Python scripts directly
- Try removing the `--clean` flag for more detailed output

## Cross-Platform Compatibility
The editor should work with saves from various platforms:
- Steam version
- Microsoft Store version
- PS4/PS5 saves (requires external decryption first)
- Xbox saves

For console saves (PS4/PS5/Xbox), you'll need to decrypt the save file first. PS4 users can follow [this method](https://www.youtube.com/watch?v=QA1lLxn_klA).

## Features

The editor allows you to modify:
- Money
- Character name (First and Last)
- Character stats (all party members)
- Playtime (now with hours:minutes:seconds input)
- Social ranks
- Social links
- Character position (dangerous - use with caution!)
- Persona attributes
- Difficulty setting
- Date and time

## How to Use the Save Editor

1. Run `p3r_editor.py` (the SavConverter folder must be in the same directory)
2. Enter the path to your save file directory when prompted
3. Select your save file from the list
4. Choose whether to create a backup (recommended)
5. Use the editor to modify values (type "help" to see available commands)
6. When finished, type "save" to save your changes

### Available Commands
- `edit money` - Change your money
- `edit firstname` / `edit lastname` - Change your character's name
- `edit characters` - Edit any unlocked character's stats
- `edit playtime` - Modify your playtime
- `edit socialrank` - Change academics, charm, and courage
- `edit sociallink` - Change social link levels
- `edit persona` - Modify your personas
- `edit difficulty` - Change game difficulty
- `edit date` - Change the current date
- `completion` - Check game completion status
- `print` - Show all editable values
- `save` - Save changes to file
- `help` - Show commands
- `exit` / `quit` - Exit the editor

## Backups
For safety, the editor automatically creates backups when saving changes. These are stored at:
`{original-file-path}/backup/{timestamp}_{filename}.sav`

## Technical Details
The game saves data in GVAS format, which can be complex to work with. The editor handles this complexity and properly manages different save formats and offsets.

## Future Plans

Planned improvements for future versions:

1. **Advanced Features**
   - Support for editing inventory items
   - Enhanced equipment management
   - More social stats improvements
   - Quest status tracking
   - Calendar events tracking

2. **Enhanced User Interface**
   - Add "preview changes" feature
   - Implement confirmation dialogs for dangerous operations
   - Additional data visualization

3. **Save File Integrity**
   - Add checksums validation
   - Improved backup system with restore capabilities
   - Automated validation of edited values

## Credits
- Save Converter: https://github.com/afkaf/Python-GVAS-JSON-Converter

## Warning
Any external modification of a save file may damage it or cause game issues. By using this tool, you accept responsibility for any potential problems. Always use the backup feature to protect your saves.
