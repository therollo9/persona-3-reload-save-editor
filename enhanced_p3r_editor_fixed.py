#!/usr/bin/env python
"""
Enhanced Persona 3 Reload Save Editor Launcher (v2.0)
----------------------------------------------------
This updated launcher includes:
1. Colorful terminal output for better readability
2. More detailed save information display
3. Better error handling and validation
4. Enhanced save format detection
5. Support for all party members

This launcher properly handles both old and new save formats with the ID offset (+4)
detection system, ensuring compatibility with all versions of Persona 3 Reload saves.
"""
import os
import sys
import time
import traceback
import tempfile
import json
from SavConverter import sav_to_json, read_sav, json_to_sav, load_json
from Editor import Encryption, Persona3Save

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def colored(text, color):
    """Apply color to text"""
    return f"{color}{text}{Colors.ENDC}"

def print_header(text):
    """Print a header with formatting"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER} {text.center(58)} {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
def print_section(text):
    """Print a section header with formatting"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*len(text)}{Colors.ENDC}")
    
def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")
    
def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")
    
def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def load_save_file(save_dir, save_file, make_backup=False):
    """Improved save file loader that handles errors properly"""
    save_path = os.path.join(save_dir, save_file)
    temp_sav_path = None
    temp_json_path = None
    
    try:
        # First try to decrypt the save file
        print_section("Loading Save File")
        print(f"Attempting to load save file: {colored(save_file, Colors.CYAN)}")
        try:
            # Try to decrypt the file
            key = "ae5zeitaix1joowooNgie3fahP5Ohph"
            print("Decrypting save file...")
            dec_data = Encryption().XORshift(save_path, key, "dec")
            
            # Write decrypted data to temp file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.sav', delete=False) as temp_file:
                temp_file.write(dec_data)
                temp_sav_path = temp_file.name
                
            # Convert to JSON
            print("Converting save data to JSON format...")
            json_data = sav_to_json(read_sav(temp_sav_path), string=True)
            os.remove(temp_sav_path)
            temp_sav_path = None
            encrypted = True
            print_success("Successfully decrypted save file")
            
        except Exception as e:
            # If decryption fails, try as unencrypted
            if temp_sav_path and os.path.exists(temp_sav_path):
                os.remove(temp_sav_path)
                temp_sav_path = None
                
            print_warning(f"Decryption failed, trying as unencrypted save file")
            print(f"Error details: {str(e)}")
            
            with open(save_path, "rb") as f:
                dec_data = f.read()
                
            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.sav', delete=False) as temp_file:
                temp_file.write(dec_data)
                temp_sav_path = temp_file.name
                
            # Convert to JSON
            print("Converting unencrypted save data to JSON format...")
            json_data = sav_to_json(read_sav(temp_sav_path), string=True)
            os.remove(temp_sav_path)
            temp_sav_path = None
            encrypted = False
            print_success("Successfully processed unencrypted save file")
        
        # Write JSON to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write(json_data)
            temp_json_path = temp_file.name
        
        # Create save editor instance
        print("Creating save editor instance...")
        editor = Persona3Save(temp_json_path, 0, save_dir, save_file, make_backup, encrypted)
        
        # Print save information
        print_section("Save File Information")
        try:
            char_name = f"{editor.SaveHeader['firstname']} {editor.SaveHeader['lastname']}"
            print(f"Character Name: {colored(char_name, Colors.CYAN)}")
        except:
            print("Character Name: Unable to detect")
            
        try:
            money = editor.LoadByNameN(editor.js, "UInt32Property", 0, 7257 + editor.id_offset)
            if money is not None:
                print(f"Money: {colored(f'{money:,}', Colors.CYAN)} yen")
        except:
            pass
            
        # Try to get playtime
        try:
            playtime = editor.Data.get("playtime")
            if playtime is not None:
                hours = playtime // 3600
                minutes = (playtime % 3600) // 60
                seconds = playtime % 60
                print(f"Playtime: {colored(f'{hours}h {minutes}m {seconds}s', Colors.CYAN)}")
        except:
            pass
        
        # Try to get game completion status
        try:
            status, _ = editor.CheckCompletionStatus()
            print(f"Game Progress: {colored(status, Colors.CYAN)}")
        except:
            pass
            
        # Print save format information
        format_type = "New (+4 offset)" if editor.id_offset == 4 else "Old (original)"
        print(f"Save Format: {colored(format_type, Colors.CYAN)}")
        
        return editor
        
    except Exception as e:
        # Clean up any temp files
        if temp_sav_path and os.path.exists(temp_sav_path):
            os.remove(temp_sav_path)
        if temp_json_path and os.path.exists(temp_json_path):
            os.remove(temp_json_path)
        raise e

def main():
    """Main function for the enhanced save editor launcher"""
    print_header("PERSONA 3 RELOAD SAVE EDITOR")
    print(colored("  Enhanced Edition (v2.0) with Support for All Characters  ", Colors.BOLD + Colors.YELLOW))
    print("\nThis launcher helps you use the save editor with proper arguments.")
    
    print(f"\n{Colors.CYAN}FEATURES:{Colors.ENDC}")
    print(f"• {Colors.GREEN}Automatic save format detection{Colors.ENDC} (Old vs New +4 offset)")
    print(f"• Support for all party members including Aigis, Ken, Koromaru")
    print(f"• Enhanced error handling and validation")
    
    # Check if SavConverter directory exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'SavConverter')):
        print_error("SavConverter folder not found!")
        print("Make sure the SavConverter folder is in the same directory as this script.")
        return 1
    
    # Get the save directory path from the user
    print_section("SAVE DIRECTORY SELECTION")
    
    # Get the save directory
    save_dir = input("Enter the directory path containing save files: ")
    if not os.path.isdir(save_dir):
        print_error(f"Directory '{save_dir}' does not exist!")
        return 1
    
    # Get save files in the directory
    save_files = [f for f in os.listdir(save_dir) if f.endswith('.sav')]
    if not save_files:
        print_error("No .sav files found in the specified directory!")
        return 1
    
    # Display save files
    print_section("AVAILABLE SAVE FILES")
    for i, save_file in enumerate(save_files):
        # Try to get file size and modification time for additional info
        try:
            file_path = os.path.join(save_dir, save_file)
            file_size = os.path.getsize(file_path) // 1024  # KB
            mod_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(file_path)))
            print(f"  {Colors.BOLD}{i+1}.{Colors.ENDC} {save_file} ({file_size} KB, Modified: {mod_time})")
        except:
            print(f"  {Colors.BOLD}{i+1}.{Colors.ENDC} {save_file}")
    
    # Get user selection
    try:
        choice = int(input(f"\nSelect a save file {colored('(number)', Colors.CYAN)}: "))
        if choice < 1 or choice > len(save_files):
            print_error("Invalid selection!")
            return 1
        selected_file = save_files[choice-1]
    except ValueError:
        print_error("Please enter a valid number!")
        return 1
    
    # Ask about backup
    make_backup = input(f"\nCreate backup of the save file? {colored('(y/n)', Colors.CYAN)}: ").lower().startswith('y')
    
    # Load the save file
    try:
        print_header("LOADING SAVE FILE")
        print(f"Save File: {colored(selected_file, Colors.CYAN)}")
        print(f"Directory: {colored(save_dir, Colors.CYAN)}")
        print(f"Backup: {colored('Yes' if make_backup else 'No', Colors.CYAN)}")
        
        # Load the save file with our custom loader
        editor = load_save_file(save_dir, selected_file, make_backup)
        
        print_success("Save file loaded successfully!")
        
        # Display save format detection prominently with colors
        format_type = "NEW (+4 offset)" if editor.id_offset == 4 else "OLD (original)"
        format_color = Colors.YELLOW if editor.id_offset == 4 else Colors.CYAN
        print_header("SAVE FORMAT INFORMATION")
        print(f"Format Type: {colored(format_type, Colors.BOLD + format_color)}")
        print(f"ID Offset: {colored(str(editor.id_offset), Colors.BOLD + format_color)}")
        print(f"{Colors.CYAN}This information is important when reporting issues or comparing save files.{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}Editor is now ready to use. Type 'help' to see available commands.{Colors.ENDC}")
        
    except Exception as e:
        print_error(f"Failed to load save file: {str(e)}")
        print("\nDetailed error information:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
