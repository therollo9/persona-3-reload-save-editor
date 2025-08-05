#!/usr/bin/env python
"""
Persona 3 Reload Save Editor Launcher
------------------------------------
This script provides a more user-friendly interface to launch
the Persona 3 Reload Save Editor and fixes issues with save file loading.

This launcher properly handles both old and new save formats with the ID offset (+4)
detection system, ensuring compatibility with all versions of Persona 3 Reload saves.
It also includes improved error handling to prevent crashes during save loading.
"""
import os
import sys
import traceback
import tempfile
import binascii
import json
from SavConverter import sav_to_json, read_sav, json_to_sav, load_json
from Editor import Encryption, Persona3Save

def load_save_file(save_dir, save_file, make_backup=False):
    """Improved save file loader that handles errors properly"""
    save_path = os.path.join(save_dir, save_file)
    temp_sav_path = None
    temp_json_path = None
    
    try:
        # First try to decrypt the save file
        print(f"Attempting to load encrypted save file: {save_file}")
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
            json_data = sav_to_json(read_sav(temp_sav_path), string=True)
            os.remove(temp_sav_path)
            temp_sav_path = None
            encrypted = True
            
        except Exception as e:
            # If decryption fails, try as unencrypted
            if temp_sav_path and os.path.exists(temp_sav_path):
                os.remove(temp_sav_path)
                temp_sav_path = None
                
            print(f"Decryption failed, trying as unencrypted save file: {str(e)}")
            with open(save_path, "rb") as f:
                dec_data = f.read()
                
            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.sav', delete=False) as temp_file:
                temp_file.write(dec_data)
                temp_sav_path = temp_file.name
                
            # Convert to JSON
            json_data = sav_to_json(read_sav(temp_sav_path), string=True)
            os.remove(temp_sav_path)
            temp_sav_path = None
            encrypted = False
        
        # Write JSON to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write(json_data)
            temp_json_path = temp_file.name
        
        # Create save editor instance
        print("Creating save editor instance...")
        return Persona3Save(temp_json_path, 0, save_dir, save_file, make_backup, encrypted)
        
    except Exception as e:
        # Clean up any temp files
        if temp_sav_path and os.path.exists(temp_sav_path):
            os.remove(temp_sav_path)
        if temp_json_path and os.path.exists(temp_json_path):
            os.remove(temp_json_path)
        raise e

def main():
    """Main function for the save editor launcher"""
    print("\n" + "="*50)
    print(" PERSONA 3 RELOAD SAVE EDITOR LAUNCHER ")
    print("="*50)
    print("\nThis launcher helps you use the save editor with proper arguments.")
    print("\nKey Features:")
    print("• Automatic save format detection (Old vs New +4 offset)")
    print("• Support for all party members")
    print("• Improved error handling")
    
    # Check if SavConverter directory exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'SavConverter')):
        print("\nERROR: SavConverter folder not found!")
        print("Make sure the SavConverter folder is in the same directory as this script.")
        return 1
    
    # Get the save directory path from the user
    print("\nPLEASE ENTER YOUR SAVE FILE PATH")
    print("---------------------------------")
    
    # Get the save directory
    save_dir = input("Enter the directory path containing save files: ")
    if not os.path.isdir(save_dir):
        print(f"\nERROR: Directory '{save_dir}' does not exist!")
        return 1
    
    # Get save files in the directory
    save_files = [f for f in os.listdir(save_dir) if f.endswith('.sav')]
    if not save_files:
        print("\nERROR: No .sav files found in the specified directory!")
        return 1
    
    # Display save files
    print("\nAVAILABLE SAVE FILES:")
    print("--------------------")
    for i, save_file in enumerate(save_files):
        print(f"  {i+1}. {save_file}")
    
    # Get user selection
    try:
        choice = int(input("\nSelect a save file (number): "))
        if choice < 1 or choice > len(save_files):
            print("\nERROR: Invalid selection!")
            return 1
        selected_file = save_files[choice-1]
    except ValueError:
        print("\nERROR: Please enter a valid number!")
        return 1
    
    # Ask about backup
    make_backup = input("\nCreate backup of the save file? (y/n): ").lower().startswith('y')
    
    # Load the save file
    try:
        print("\n" + "="*50)
        print(" LOADING SAVE FILE ")
        print("="*50)
        print(f"Save File: {selected_file}")
        print(f"Directory: {save_dir}")
        print(f"Backup: {'Yes' if make_backup else 'No'}")
        print("="*50)
          # Load the save file with our custom loader
        editor = load_save_file(save_dir, selected_file, make_backup)
        
        print("\nSave file loaded successfully.")
        
        # Display save format detection prominently
        format_type = "NEW (+4 offset)" if editor.id_offset == 4 else "OLD (original)"
        print("\n" + "="*50)
        print(f" SAVE FORMAT DETECTED: {format_type}")
        print("="*50)
        
        print("\nEditor closed successfully.")
        
    except Exception as e:
        print(f"\nERROR: Failed to load save file: {str(e)}")
        print("\nDetailed error information:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
