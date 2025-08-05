import sys
import struct
import tempfile
import os
import time
import binascii
import json
from SavConverter import sav_to_json, read_sav, json_to_sav, load_json
CREDITS = "https://github.com/afkaf/Python-GVAS-JSON-Converter"


class Encryption:
    def __init__(self):
        pass

    def XORshift(self, file, key, mode):
        keylen = len(key)
        with open(file, 'rb') as f:
            data1 = f.read()
        filesize = os.path.getsize(file)
        crypt_data = bytearray(filesize)

        for i in range(filesize):
            key_idx = i % keylen
            if mode == "dec":
                bVar1 = data1[i] ^ ord(key[key_idx])
                crypt_data[i] = (bVar1 >> 4 & 3 | (
                    bVar1 & 3) << 4 | bVar1 & 0xcc)
            elif mode == "enc":
                crypt_data[i] = ((((data1[i] & 0xff) >> 4) & 3 | (
                    data1[i] & 3) << 4 | data1[i] & 0xcc) ^ ord(key[key_idx]))
        return crypt_data


class OpenSave:
    def __init__(self):
        pass

    def Load(self, i, e, mdd, make_bak):
        temp_file_path = None
        try:
            # Try to decrypt the save file
            save_path = os.path.join(i, e)
            dec_data = Encryption().XORshift(save_path, "ae5zeitaix1joowooNgie3fahP5Ohph", "dec")
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.sav', delete=False) as temp_file:
                temp_file.write(dec_data)
                temp_file_path = temp_file.name
                temp_file.flush()
            json_data = sav_to_json(read_sav(temp_file_path), string=True)
            if temp_file_path:
                os.remove(temp_file_path)
                temp_file_path = None
            comp = True
        except Exception as ex:
            print(f"Encrypted format failed, trying unencrypted: {str(ex)}")
            # If decryption fails, try reading as unencrypted
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                temp_file_path = None
                
            save_path = os.path.join(i, e)
            try:
                with open(save_path, "rb") as f:
                    dec_data = f.read()
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.sav', delete=False) as temp_file:
                    temp_file.write(dec_data)
                    temp_file_path = temp_file.name
                    temp_file.flush()
                json_data = sav_to_json(read_sav(temp_file_path), string=True)
                if temp_file_path:
                    os.remove(temp_file_path)
                    temp_file_path = None
                comp = False
            except Exception as ex:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise Exception(f"Failed to read save file: {str(ex)}")

        json_temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_file.write(json_data)
                json_temp_path = temp_file.name
                temp_file.flush()
            
            return Persona3Save(json_temp_path, mdd, i, e, make_bak, comp)
        except Exception as ex:
            if json_temp_path and os.path.exists(json_temp_path):
                os.remove(json_temp_path)
            raise ex


class Persona3Save:
    def __init__(self, i, mdd, ww, qq, make_bak, comp):
        self.padding = {"UInt32Property": "04000000",
                        "Int8Property": "01000000", "UInt16Property": "02000000"}
        self.encrypted = comp
        self.make_bak_file = make_bak
        self.filenamestart = ww
        self.filenameend = qq
        with open(i, "r") as f:
            self.js = json.load(f)
        os.remove(i)
        
        # Detect if this is a new save format or old save format
        # New saves have ID values offset by +4
        self.id_offset = self.DetectSaveFormatVersion()
        
        # Print save format detection in a more prominent way
        format_type = "NEW (+4 offset)" if self.id_offset == 4 else "OLD (original)"
        print("\n" + "="*50)
        print(f" SAVE FORMAT DETECTED: {format_type}")
        print(f" ID OFFSET: {self.id_offset}")
        print("="*50)
        
        self.LoadData()
        if mdd == 0:
            self.ShowCurrentInfo()
            while True:
                command = input("(type help to see comand): ").lower()
                if command == None:
                    pass
                elif command == "edit lastname":
                    self.LastName()
                elif command == "edit money":
                    self.Money()
                elif command == "edit date":
                    self.Date()
                elif command == "edit persona" or command == "edit personas":
                    self.Personas()
                elif command == "edit playtime":
                    self.Playtime()
                elif command == "edit difficulty":
                    self.Difficulty()
                elif command == "edit sociallink" or command == "edit sociallinks" or command == "edit social-link" or command == "edit social-links" or command == "edit social link" or command == "edit social links":
                    self.Sociallink()
                elif command == "edit firstname":
                    self.FirstName()
                elif command == "edit characters" or command == "edit character":
                    self.Characters()
                elif command == "edit socialrank" or command == "edit socialranks":
                    self.Socialrank()
                elif command == "edit dangerous":
                    self.Dangerous()
                elif command == "completion" or command == "check completion":
                    self.ShowCompletionStatus()
                elif command == "get" or command[0:4] == "get ":
                    a = command.split(" ")
                    if len(a) == 2:
                        try:
                            z = self.SaveHeader[a[1]]
                            print("")
                            print(z)
                        except:
                            try:
                                if type(self.Data[a[1]]) != dict:
                                    print("")
                                    print(self.Data[a[1]])
                                else:
                                    print("")
                                    print(None)
                            except:
                                pass
                elif command == "print":
                    print("")
                    for i in self.SaveHeader.keys():
                        if not "len" in i.lower():
                            print(i)
                    for i in self.Data.keys():
                        print(i)
                elif command == "json":
                    with open("n_json.txt", "w") as f:
                        json.dump(self.js, f, indent=4)
                elif command == "save":
                    self.SaveChange()
                elif command == "help":
                    print("")
                    print("exit|quit : to exit")
                    print("save : save edited data in the save file")
                    print("print : show editable value")
                    print("edit 'value_name' : edit the value of 'value_name'")
                    print("get 'value_name' : get the value of 'value_name'")
                    print("completion : check game completion status")
                elif command == "exit" or command == "quit":
                    print("Exiting...")
                    import sys
                    sys.exit(0)
                else:
                    print("Invalid | type help to see possible commnad/value to modify")

    def LoadData(self):
        self.filename = self.LoadByName(
            self.js[1]["value"], "SaveSlotName", 1, 1)
        self.SaveHeader = {}

        self.SaveHeader["lastname"] = self.LoadByName(
            self.js[1]["value"], "LastName", 1, 1)
        self.SaveHeader["firstname"] = self.LoadByName(
            self.js[1]["value"], "FirstName", 1, 1)
        self.SaveHeader["LenLastName"] = len(self.SaveHeader["lastname"])
        self.SaveHeader["LenFirstName"] = len(self.SaveHeader["firstname"])
        self.Data = {}
        self.Data["money"] = self.LoadByNameN(
            self.js, "UInt32Property", 0, 7257 + self.id_offset)
        # Get playtime from primary location or try alternative location
        playtime = self.LoadByNameN(self.js, "UInt32Property", 0, 12833 + self.id_offset)
        if playtime is None:
            playtime = self.LoadByName(self.js[1]["value"], "PlayTime", 0, 1)
        self.Data["playtime"] = playtime
        # Apply offset to all character IDs
        self.Data["characters"] = {
            self.SaveHeader["firstname"].lower(): {
                "current_pv": 13070 + self.id_offset, 
                "current_pc": 13071 + self.id_offset, 
                "level": 13078 + self.id_offset, 
                "exp": 13075 + self.id_offset,
                "social_link_id": None  # Protagonist doesn't have a social link with themselves
            }, 
            "yukari": {
                "current_pv": 13246 + self.id_offset, 
                "current_pc": 13247 + self.id_offset, 
                "level": 13263 + self.id_offset, 
                "exp": 13264 + self.id_offset,
                "social_link_id": 5312 + self.id_offset  # Takeba social link
            }, 
            "junpei": {
                "current_pv": 13422 + self.id_offset, 
                "current_pc": 13423 + self.id_offset, 
                "level": 13439 + self.id_offset, 
                "exp": 13440 + self.id_offset,
                "social_link_id": 5302 + self.id_offset  # Tomochika social link
            }, 
            "akihiko": {
                "current_pv": 13598 + self.id_offset, 
                "current_pc": 13599 + self.id_offset, 
                "level": 13615 + self.id_offset, 
                "exp": 13616 + self.id_offset,
                "social_link_id": None  # No direct social link with Akihiko
            }, 
            "mitsuru": {
                "current_pv": 13774 + self.id_offset, 
                "current_pc": 13775 + self.id_offset, 
                "level": 13791 + self.id_offset, 
                "exp": 13792 + self.id_offset,
                "social_link_id": 5306 + self.id_offset  # Kirijo social link
            }, 
            "fuuka": {
                "current_pv": 13950 + self.id_offset, 
                "current_pc": 13951 + self.id_offset, 
                "level": 13967 + self.id_offset, 
                "exp": 13968 + self.id_offset,
                "social_link_id": 5304 + self.id_offset  # Yamagishi social link
            },
            "aigis": {
                "current_pv": 14126 + self.id_offset, 
                "current_pc": 14127 + self.id_offset, 
                "level": 14143 + self.id_offset, 
                "exp": 14144 + self.id_offset,
                "social_link_id": 5342 + self.id_offset  # Aigis social link
            },
            "ken": {
                "current_pv": 14302 + self.id_offset, 
                "current_pc": 14303 + self.id_offset, 
                "level": 14319 + self.id_offset, 
                "exp": 14320 + self.id_offset,
                "social_link_id": None  # No direct social link with Ken
            },
            "koromaru": {
                "current_pv": 14478 + self.id_offset, 
                "current_pc": 14479 + self.id_offset, 
                "level": 14495 + self.id_offset, 
                "exp": 14496 + self.id_offset,
                "social_link_id": None  # No direct social link with Koromaru
            },
            "shinjiro": {
                "current_pv": 14654 + self.id_offset, 
                "current_pc": 14655 + self.id_offset, 
                "level": 14671 + self.id_offset, 
                "exp": 14672 + self.id_offset,
                "social_link_id": None  # No direct social link with Shinjiro
            }
        }
        
        # Apply offset to dangerous IDs
        self.Data["dangerous"] = {
            "player_x": self.LoadByNameN(self.js, "UInt32Property", 0, 5219 + self.id_offset), 
            "player_y": self.LoadByNameN(self.js, "UInt32Property", 0, 5220 + self.id_offset), 
            "player_direction": self.LoadByNameN(self.js, "UInt32Property", 0, 5218 + self.id_offset)
            # "player_z": self.LoadByNameN(self.js, "UInt32Property", 0, 5221 + self.id_offset)
        }
        
        # Apply offset to social ranks
        self.Data["socialrank"] = {
            "academics": 5352 + self.id_offset, 
            "charm": 5354 + self.id_offset, 
            "courage": 5356 + self.id_offset
        }
        
        # Apply offset to date IDs
        self.Data["date"] = {
            "time": 1929 + self.id_offset, 
            "day": 1928 + self.id_offset
        }  # dayskip = 1930 + self.id_offset
        # Apply offset to all persona IDs
        self.Data["personavalueid"] = {
            "persona": [13086 + self.id_offset, 13098 + self.id_offset, 13110 + self.id_offset, 13122 + self.id_offset, 13134 + self.id_offset, 13146 + self.id_offset, 13158 + self.id_offset], 
            "level": [13087 + self.id_offset, 13099 + self.id_offset, 13111 + self.id_offset, 13123 + self.id_offset, 13135 + self.id_offset, 13147 + self.id_offset, 13159 + self.id_offset], 
            "exp": [13088 + self.id_offset, 13100 + self.id_offset, 13112 + self.id_offset, 13124 + self.id_offset, 13136 + self.id_offset, 13148 + self.id_offset, 13160 + self.id_offset], 
            "skill_slot_1": [13089 + self.id_offset, 13101 + self.id_offset, 13113 + self.id_offset, 13125 + self.id_offset, 13137 + self.id_offset, 13149 + self.id_offset, 13161 + self.id_offset], 
            "skill_slot_2": [13090 + self.id_offset, 13102 + self.id_offset, 13114 + self.id_offset, 13126 + self.id_offset, 13138 + self.id_offset, 13150 + self.id_offset, 13162 + self.id_offset], 
            "skill_slot_3": [13091 + self.id_offset, 13103 + self.id_offset, 13115 + self.id_offset, 13127 + self.id_offset, 13139 + self.id_offset, 13151 + self.id_offset, 13163 + self.id_offset], 
            "skill_slot_4": [13092 + self.id_offset, 13104 + self.id_offset, 13116 + self.id_offset, 13128 + self.id_offset, 13140 + self.id_offset, 13152 + self.id_offset, 13164 + self.id_offset], 
            "fo_ma_en_ag": [13093 + self.id_offset, 13105 + self.id_offset, 13117 + self.id_offset, 13129 + self.id_offset, 13141 + self.id_offset, 13153 + self.id_offset, 13165 + self.id_offset], 
            "ch": [13094 + self.id_offset, 13106 + self.id_offset, 13118 + self.id_offset, 13130 + self.id_offset, 13142 + self.id_offset, 13154 + self.id_offset, 13166 + self.id_offset]
        }
        self.Data["sociallink"] = {"aigis": 5342 + self.id_offset, "nyx annihilation team": 5340 + self.id_offset, "kamiki": 5338 + self.id_offset, "suemitsu": 5336 + self.id_offset, "hayase": 5334 + self.id_offset, "mutatsu": 5332 + self.id_offset, "tanaka": 5330 + self.id_offset, "bebe": 5328 + self.id_offset, "pharos": 5326 + self.id_offset, "maiko": 5324 + self.id_offset,
                                   "nishiwaki": 5322 + self.id_offset, "hiraga": 5320 + self.id_offset, "maya": 5318 + self.id_offset, "fushimi": 5316 + self.id_offset, "miyamoto": 5314 + self.id_offset, "takeba": 5312 + self.id_offset, "kitamura": 5310 + self.id_offset, "odagiri": 5308 + self.id_offset, "kirijo": 5306 + self.id_offset, "yamagishi": 5304 + self.id_offset, "tomochika": 5302 + self.id_offset, "sees": 5300 + self.id_offset}

    def CheckCompletionStatus(self):
        """Check if the save file represents a completed game"""
        completion_indicators = {
            "nyx_annihilation_team": False,
            "aigis_social_link": False,
            "high_level": False,
            "high_playtime": False
        }

        # Check Nyx Annihilation Team social link (ID 5340)
        nyx_team_value = self.LoadByNameN(self.js, "UInt32Property", 0, 5340 + self.id_offset)
        if nyx_team_value is not None and nyx_team_value > 0:
            level = nyx_team_value & 0xFFFF
            if level >= 1:  # If the social link is unlocked, it suggests late game
                completion_indicators["nyx_annihilation_team"] = True

        # Check Aigis social link (ID 5342) - another late-game social link
        aigis_value = self.LoadByNameN(self.js, "UInt32Property", 0, 5342 + self.id_offset)
        if aigis_value is not None and aigis_value > 0:
            level = aigis_value & 0xFFFF
            if level >= 1:
                completion_indicators["aigis_social_link"] = True

        # Check character level (main character level 60+ suggests late game)
        mc_level = self.LoadByNameN(self.js, "UInt32Property", 0, 13078 + self.id_offset)
        if mc_level is not None and mc_level >= 60:
            completion_indicators["high_level"] = True

        # Check playtime (100+ hours suggests significant progress)
        playtime = self.LoadByNameN(self.js, "UInt32Property", 0, 12833 + self.id_offset)
        # Try alternative playtime location
        if playtime is None:
            playtime = self.LoadByName(self.js[1]["value"], "PlayTime", 0, 1)
        
        if playtime is not None and playtime >= 360000:  # 100 hours in seconds
            completion_indicators["high_playtime"] = True

        # Determine completion status
        completion_score = sum(completion_indicators.values())
        total_indicators = len(completion_indicators)

        if completion_score >= 3:
            return "COMPLETED", completion_indicators
        elif completion_score >= 2:
            return "LATE GAME", completion_indicators
        elif completion_score >= 1:
            return "MID GAME", completion_indicators
        else:
            return "EARLY GAME", completion_indicators

    def ShowCompletionStatus(self):
        """Display detailed completion status information"""
        print("\n" + "="*50)
        print("GAME COMPLETION STATUS ANALYSIS")
        print("="*50)

        completion_status, indicators = self.CheckCompletionStatus()
        status_emoji = {"COMPLETED": "🏆", "LATE GAME": "⚡",
                        "MID GAME": "📈", "EARLY GAME": "🌱"}

        print(
            f"\n🎮 Overall Status: {status_emoji.get(completion_status, '❓')} {completion_status}")

        print(f"\n📊 Completion Indicators:")
        print(
            f"   {'✅' if indicators['nyx_annihilation_team'] else '❌'} Nyx Annihilation Team Social Link")
        print(
            f"   {'✅' if indicators['aigis_social_link'] else '❌'} Aigis Social Link")
        print(
            f"   {'✅' if indicators['high_level'] else '❌'} High Character Level (60+)")
        print(
            f"   {'✅' if indicators['high_playtime'] else '❌'} Significant Playtime (100+ hours)")

        # Show specific values
        print(f"\n📈 Detailed Values:")

        # Nyx Annihilation Team
        nyx_team_value = self.LoadByNameN(self.js, "UInt32Property", 0, 5340 + self.id_offset)
        if nyx_team_value is not None:
            level = nyx_team_value & 0xFFFF
            points = (nyx_team_value >> 16) & 0xFFFF
            print(f"   Nyx Annihilation Team: Rank {level} (Points: {points})")
        else:
            print(f"   Nyx Annihilation Team: Not unlocked")

        # Aigis
        aigis_value = self.LoadByNameN(self.js, "UInt32Property", 0, 5342 + self.id_offset)
        if aigis_value is not None:
            level = aigis_value & 0xFFFF
            points = (aigis_value >> 16) & 0xFFFF
            print(f"   Aigis Social Link: Rank {level} (Points: {points})")
        else:
            print(f"   Aigis Social Link: Not unlocked")

        # Character level
        mc_level = self.LoadByNameN(self.js, "UInt32Property", 0, 13078 + self.id_offset)
        if mc_level is not None:
            print(f"   Main Character Level: {mc_level}")
        else:
            print(f"   Main Character Level: Unknown")

        # Playtime
        playtime = self.LoadByNameN(self.js, "UInt32Property", 0, 12833 + self.id_offset)
        # Try alternative playtime location
        if playtime is None:
            playtime = self.LoadByName(self.js[1]["value"], "PlayTime", 0, 1)
            
        if playtime is not None:
            hours = playtime // 3600
            minutes = (playtime % 3600) // 60
            seconds = playtime % 60
            print(f"   Total Playtime: {hours}h {minutes}m {seconds}s")
            print(f"   Raw Playtime (seconds): {playtime}")
        else:
            print(f"   Total Playtime: Unknown")

        # Date
        day_value = self.LoadByNameN(self.js, "UInt32Property", 0, 1928 + self.id_offset)
        if day_value is not None:
            daydata = [[30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 28, 4], {2009: [
                "April", "May", "June", "July", "August", "September", "October", "November", "December"], 2010: ["January", "February", "March"]}]
            current_day = day_value + 1
            month = 0
            year = 2009

            for i, days_in_month in enumerate(daydata[0]):
                if current_day <= days_in_month:
                    month = i
                    break
                current_day -= days_in_month
                if i == 8:
                    year = 2010

            if month < len(daydata[1][year]):
                month_name = daydata[1][year][month]
                print(f"   Current Date: {month_name} {current_day}, {year}")
            else:
                print(f"   Current Date: Day {day_value}")
        else:
            print(f"   Current Date: Unknown")

        print("\n" + "="*50)
        print("Note: This analysis is based on common completion indicators.")
        print("A save file showing 'COMPLETED' likely represents a finished game.")
        print("="*50 + "\n")

    def ShowCurrentInfo(self):
        print("\n" + "="*50)
        print("PERSONA 3 RELOAD SAVE FILE INFORMATION")
        print("="*50)

        # Show save format information
        format_type = "New (+4 offset)" if self.id_offset == 4 else "Old (original)"
        print(f"\n💾 SAVE FORMAT: {format_type}")
        
        # Check completion status
        completion_status, indicators = self.CheckCompletionStatus()
        status_emoji = {"COMPLETED": "🏆", "LATE GAME": "⚡",
                        "MID GAME": "📈", "EARLY GAME": "🌱"}
        print(
            f"🎮 GAME STATUS: {status_emoji.get(completion_status, '❓')} {completion_status}")

        # Show completion indicators
        if any(indicators.values()):
            print("   Completion Indicators:")
            if indicators["nyx_annihilation_team"]:
                print("   ✅ Nyx Annihilation Team social link unlocked")
            if indicators["aigis_social_link"]:
                print("   ✅ Aigis social link unlocked")
            if indicators["high_level"]:
                print("   ✅ High character level (60+)")
            if indicators["high_playtime"]:
                print("   ✅ Significant playtime (100+ hours)")

        # Basic character info
        print(f"\n📝 CHARACTER INFO:")
        print(
            f"   Name: {self.SaveHeader['firstname']} {self.SaveHeader['lastname']}")

        # Money and playtime
        money = self.LoadByNameN(self.js, "UInt32Property", 0, 7257 + self.id_offset)
        
        # Enhanced playtime detection with multiple fallback locations
        playtime = None
        playtime_source = None
        
        # First try standard location with offset
        playtime = self.LoadByNameN(self.js, "UInt32Property", 0, 12833 + self.id_offset)
        if playtime is not None:
            playtime_source = "primary"
            
        # If not found, try alternative standard location (some game versions use this)
        if playtime is None:
            playtime = self.LoadByNameN(self.js, "UInt32Property", 0, 12833)  # Try without offset
            if playtime is not None:
                playtime_source = "alternate"
                
        # If still not found, try the header section
        if playtime is None:
            playtime = self.LoadByName(self.js[1]["value"], "PlayTime", 0, 1)
            if playtime is not None:
                playtime_source = "header"
        
        # Final fallback: Try a different UInt32 property that might contain playtime
        if playtime is None:
            for i in range(12830, 12840):  # Try a range of nearby values
                test_playtime = self.LoadByNameN(self.js, "UInt32Property", 0, i)
                if test_playtime is not None and 3600 <= test_playtime <= 3600 * 999:  # Reasonable playtime range
                    playtime = test_playtime
                    playtime_source = f"discovered at offset {i}"
                    break
        
        if money is not None:
            print(f"   💰 Money: {money:,} yen")
            
        if playtime is not None:
            hours = playtime // 3600
            minutes = (playtime % 3600) // 60
            seconds = playtime % 60
            print(f"   ⏱️  Playtime: {hours}h {minutes}m {seconds}s")
            print(f"   📊 Raw Playtime: {playtime} seconds")
            print(f"   🔍 Playtime source: {playtime_source}")
        else:
            print(f"   ⏱️  Playtime: Not found in save file")
            print(f"   ❌ Could not detect playtime in any known location")

        # Social ranks
        print(f"\n📊 SOCIAL RANKS:")
        academics = self.LoadByNameN(self.js, "UInt32Property", 0, 5352 + self.id_offset)
        charm = self.LoadByNameN(self.js, "UInt32Property", 0, 5354 + self.id_offset)
        courage = self.LoadByNameN(self.js, "UInt32Property", 0, 5356 + self.id_offset)
        if academics is not None:
            print(f"   📚 Academics: {academics}")
        if charm is not None:
            print(f"   💖 Charm: {charm}")
        if courage is not None:
            print(f"   💪 Courage: {courage}")

        # Date and time
        print(f"\n📅 DATE & TIME:")
        day_value = self.LoadByNameN(self.js, "UInt32Property", 0, 1928 + self.id_offset)
        time_value = self.LoadByNameN(self.js, "UInt32Property", 0, 1929 + self.id_offset)

        if day_value is not None:
            # Convert day value to actual date
            daydata = [[30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 28, 4], {2009: [
                "April", "May", "June", "July", "August", "September", "October", "November", "December"], 2010: ["January", "February", "March"]}]
            current_day = day_value + 1
            month = 0
            year = 2009

            # Calculate month and day
            for i, days_in_month in enumerate(daydata[0]):
                if current_day <= days_in_month:
                    month = i
                    break
                current_day -= days_in_month
                if i == 8:  # After September, switch to 2010
                    year = 2010

            if month < len(daydata[1][year]):
                month_name = daydata[1][year][month]
                print(f"   📅 Date: {month_name} {current_day}, {year}")
            else:
                print(f"   📅 Date: Day {day_value}")
        else:
            print(f"   📅 Date: Unknown")

        if time_value is not None:
            timedata = ["Very early morning", "Early morning", "Morning", "Lunch break",
                        "Afternoon", "After school", "Evening", "Dark Hour", "Late evening"]
            time_index = time_value - 257
            if 0 <= time_index < len(timedata):
                print(f"   ⏰ Time: {timedata[time_index]}")
            else:
                print(f"   ⏰ Time: Unknown ({time_value})")
        else:
            print(f"   ⏰ Time: Unknown")

        # Character stats
        print(f"\n⚔️  CHARACTER STATS:")
        
        # Dictionary of all characters with their display names
        characters = {
            self.SaveHeader["firstname"].lower(): self.SaveHeader["firstname"],
            "yukari": "Yukari",
            "junpei": "Junpei",
            "akihiko": "Akihiko", 
            "mitsuru": "Mitsuru",
            "fuuka": "Fuuka",
            "aigis": "Aigis",
            "ken": "Ken",
            "koromaru": "Koromaru",
            "shinjiro": "Shinjiro"
        }
        
        # Show only unlocked characters
        unlocked_count = 0
        unlocked_first = []  # Track earlier party members
        unlocked_later = []  # Track later party members
        
        for char_key, char_display in characters.items():
            if self.IsCharacterUnlocked(char_key):
                unlocked_count += 1
                # Get character stats
                if char_key == self.SaveHeader["firstname"].lower():
                    # Main character
                    pv = self.LoadByNameN(self.js, "UInt32Property", 0, 13070 + self.id_offset)
                    pc = self.LoadByNameN(self.js, "UInt32Property", 0, 13071 + self.id_offset)
                    level = self.LoadByNameN(self.js, "UInt32Property", 0, 13078 + self.id_offset)
                    exp = self.LoadByNameN(self.js, "UInt32Property", 0, 13075 + self.id_offset)
                    
                    # Always show protagonist first
                    if level is not None:
                        print(f"   {char_display} (Protagonist): Level {level} (PV: {pv}, PC: {pc})")
                else:
                    # Other characters
                    char_data = self.Data["characters"].get(char_key)
                    if char_data:
                        pv = self.LoadByNameN(self.js, "UInt32Property", 0, char_data["current_pv"])
                        pc = self.LoadByNameN(self.js, "UInt32Property", 0, char_data["current_pc"])
                        level = self.LoadByNameN(self.js, "UInt32Property", 0, char_data["level"])
                        exp = self.LoadByNameN(self.js, "UInt32Property", 0, char_data["exp"])
                        
                        # Build display string
                        if level is not None:
                            char_info = f"   {char_display}: Level {level} (PV: {pv}, PC: {pc})"
                            
                            # Group characters by when they join (early vs late game)
                            if char_key in ["yukari", "junpei", "akihiko", "mitsuru", "fuuka"]:
                                unlocked_first.append(char_info)
                            else:
                                unlocked_later.append(char_info)
                
        # Display early characters first, then later ones
        for char_info in unlocked_first:
            print(char_info)
            
        for char_info in unlocked_later:
            print(char_info)
        
        if unlocked_count == 0:
            print("   No characters found in the save file.")

        # Personas
        print(f"\n👹 PERSONAS:")
        for i in range(6):
            persona_id = self.LoadByNameN(
                self.js, "UInt32Property", 0, 13086 + i*12 + self.id_offset)
            persona_level = self.LoadByNameN(
                self.js, "UInt32Property", 0, 13087 + i*12 + self.id_offset)
            if persona_id is not None and persona_id > 0:
                print(
                    f"   Slot {i+1}: ID {persona_id} (Level {persona_level})")

        # Social Links
        print(f"\n💕 SOCIAL LINKS:")
        social_links = [
            "SEES", "Tomochika", "Yamagishi", "Kirijo", "Odagiri", "Kitamura",
            "Takeba", "Miyamoto", "Fushimi", "Maya", "Hiraga", "Nishiwaki",
            "Maiko", "Pharos", "Bebe", "Tanaka", "Mutatsu", "Hayase",
            "Suemitsu", "Kamiki", "Nyx Annihilation Team", "Aigis"
        ]
        social_link_ids = [5300, 5302, 5304, 5306, 5308, 5310, 5312, 5314, 5316, 5318,
                           5320, 5322, 5324, 5326, 5328, 5330, 5332, 5334, 5336, 5338, 5340, 5342]

        for i, (name, link_id) in enumerate(zip(social_links, social_link_ids)):
            link_value = self.LoadByNameN(
                self.js, "UInt32Property", 0, link_id + self.id_offset)
            if link_value is not None and link_value > 0:
                # Extract level and points from the 32-bit value
                level = link_value & 0xFFFF
                points = (link_value >> 16) & 0xFFFF
                if level > 0:
                    print(f"   {name}: Rank {level} (Points: {points})")

        print("\n" + "="*50)
        print("Type 'help' to see available commands")
        print("Type 'print' to see all editable values")
        print("="*50 + "\n")

    def SaveChange(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(self.js, temp_file, indent=2)
            temp_file_path = temp_file.name
            temp_file.flush
        binary_save = json_to_sav(load_json(temp_file_path))

        os.remove(temp_file_path)
        if self.encrypted == True:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.sav', delete=False) as temp_file:
                temp_file.write(binary_save)
                temp_file_path = temp_file.name
                temp_file.flush
            enc_data = Encryption().XORshift(
                temp_file_path, "ae5zeitaix1joowooNgie3fahP5Ohph", "enc")
            os.remove(temp_file_path)
        else:
            enc_data = binary_save
        if self.make_bak_file == True:
            if os.path.isdir(self.filenamestart+"\\backup") == False:
                os.mkdir(self.filenamestart+"\\backup")
            with open(f"{self.filenamestart}\\{self.filenameend}", "rb") as fr:
                back_data = fr.read()
            with open(f"{self.filenamestart}\\backup\\{str(int(time.time()))+'_'+self.filenameend}", "wb") as fb:
                fb.write(back_data)
        with open(f"{self.filenamestart}\\{self.filenameend}", "wb") as f:
            f.write(enc_data)

    def int_to_hex(self, int_value):
        return ''.join([(hex(int_value)[2:].zfill(8))[i:i+2] for i in range(6, -2, -2)])

    def debug_GetIdByValue(self, js, name, header, value):
        d = []
        if header == 0:
            for i in js[:]:
                if i["type"] == name:
                    if i["value"] == value:
                        d.append((int.from_bytes(binascii.unhexlify(
                            i["padding"]), byteorder="little")))
        return d

    def SaveByNameN(self, js, name, header, nvar, n, after=None):
        xx = False
        padd = 0
        if header == 0:
            for i in js[:]:
                padd += 1
                if i["type"] == name:
                    if xx == True:
                        js.insert(padd, {
                            "type": "UInt32Property",
                            "name": "SaveDataArea",
                            "padding_static": "04000000",
                            "padding": self.int_to_hex(n),
                            "value": nvar
                        })
                        xx == False
                    if int.from_bytes(binascii.unhexlify(str(i["padding"])), byteorder="little") == n:
                        i["value"] = nvar
                        return js
                    elif int.from_bytes(binascii.unhexlify(str(i["padding"])), byteorder="little") == after:
                        xx = True
        if after == None:
            js.insert(len(js)-1, {
                "type": "UInt32Property",
                "name": "SaveDataArea",
                "padding_static": "04000000",
                "padding": self.int_to_hex(n),
                "value": nvar
            })
        return js

    def DelByNameN(self, js, name, header, n):
        if header == 0:
            for i in js[:]:
                if i["type"] == name:
                    if int.from_bytes(binascii.unhexlify(str(i["padding"])), byteorder="little") == n:
                        js.remove(i)
            return js

    def SaveByName(self, js, name, mode, header, nvar, typee, lenn=None, dummy=None):
        c = 0
        d = 0
        r = False
        x_hex = -1
        for i in js[:]:
            try:
                if i["name"] == name:
                    js.remove(i)
            except:
                pass
        x_padding = -1
        x_value = -1
        if mode == 0:
            nbr = 1
        elif mode == 1:
            nbr = len(nvar)
        for i in range(nbr):
            try:
                if mode == 1:
                    x_value += 1
                    number = hex(ord(nvar[x_value])).replace("0x", "")
                    if len(number) % 2 == 1:
                        number = f"0{number}"
                    number = self.split_string(number, 2)
                    for ise in number:
                        x_padding += 1
                        js.insert(len(js)-1, {"type": typee, "name": name, "padding_static": self.padding[typee], "padding": self.int_to_hex(
                            x_padding), "value": int.from_bytes(binascii.unhexlify(ise), byteorder="big", signed=True)})

                elif mode == 0:
                    js.insert(len(js)-1, {"type": typee, "name": name,
                              "padding_static": self.padding[typee], "padding": self.int_to_hex(0), "value": nvar})
            except:
                pass
        return js

    def LoadByNameN(self, js, name, header, n):
        if header == 0:
            for i in js[:]:
                if i["type"] == name:
                    if int.from_bytes(binascii.unhexlify(i["padding"]), byteorder="little") == n:
                        return i["value"]
        return None

    def LoadByName(self, js, name, mode, header):
        tmp = []
        c = 0
        for i in js:
            if header == 1:
                try:
                    if i["name"] == name:
                        if i["type"] == "StrProperty":
                            return i["value"]
                        tmp.append([int.from_bytes(binascii.unhexlify(i["padding"]), byteorder="little"), binascii.hexlify(
                            (i["value"]).to_bytes(1, byteorder='big', signed=True)).decode()])

                except:
                    pass
            else:
                if c > 1:
                    try:
                        if i["name"] == name:
                            tmp += format((i["value"] & 0xFFFFFFFF), '08x')
                    except:
                        pass
                c += 1
        a = sorted(tmp, key=lambda x: x[0])
        tmp = ""
        for i in a:
            tmp += i[1]
        if len(tmp) > 0:
            if mode == 1:
                return binascii.unhexlify(tmp).decode("utf-8", errors="ignore")
            return binascii.unhexlify(tmp)
        return None

    def str_to_int(self, i):
        strr = ""
        for a in i:
            strr += hex(ord(a))[2:].zfill(2)
        return int.from_bytes(binascii.unhexlify(strr), byteorder="little")

    def split_string(self, string, nbr, val=False):
        if val == True:
            string = binascii.hexlify(string.encode()).decode()
        new_lst = []
        iq = 0
        strr = ""
        for i in string:
            iq += 1
            strr += i
            if iq == nbr:
                iq = 0
                new_lst.append(strr)
                strr = ""
        if strr != "":
            new_lst.append(strr)
        return new_lst

    """ Method """

    def LastName(self):
        while True:
            new_name = input(
                "New LastName (10 char max | put nothing to cancel): ")
            if len(new_name) <= 10 and len(new_name) > 0:
                aaa = True
                for i in new_name:
                    if len(binascii.hexlify(i.encode()).decode()) > 2:
                        aaa = False
                if aaa == True:
                    self.js[1]["value"] = self.SaveByName(self.js[1]["value"], "LastName", 1, 1, new_name, "Int8Property", self.SaveHeader["LenLastName"],
                                                          '{"type": "Int8Property", "name": name,"padding_static":static,"padding":self.int_to_hex(x_hex), "value": ord(nvar[c - 1])}')
                    self.SaveHeader["lastname"] = new_name
                    self.SaveHeader["LenLastName"] = len(new_name)
                    new_name = self.split_string(new_name, 8, True)
                    counter = 0
                    for i in [0, 0, 0, 0, 0, 0, 0, 0]:
                        self.js = self.DelByNameN(
                            self.js, "UInt32Property", 0, 17950+counter)
                    counter = 0
                    for i in new_name:
                        counter += 1
                        self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int.from_bytes(
                            binascii.unhexlify(i), byteorder="little"), 17950+counter)
                    print(new_name)
                    break
            elif len(new_name) == 0:
                break

    def FirstName(self):
        while True:
            new_name = input(
                "New FirstName (10 char max | put nothing to cancel): ")
            if len(new_name) <= 10 and len(new_name) > 0:
                aaa = True
                for i in new_name:
                    if len(binascii.hexlify(i.encode()).decode()) > 2:
                        aaa = False
                if aaa == True:
                    self.js[1]["value"] = self.SaveByName(self.js[1]["value"], "FirstName", 1, 1, new_name, "Int8Property", self.SaveHeader["LenFirstName"],
                                                          '{"type": "Int8Property", "name": name,"padding_static":static,"padding":self.int_to_hex(x_hex), "value": ord(nvar[c - 1])}')
                    self.SaveHeader["firstname"] = new_name
                    self.SaveHeader["LenFirstName"] = len(new_name)
                    new_name = self.split_string(new_name, 8, True)
                    counter = 0
                    for i in [0, 0, 0, 0, 0, 0, 0, 0]:
                        self.js = self.DelByNameN(
                            self.js, "UInt32Property", 0, 17934+counter)
                    counter = 0
                    for i in new_name:
                        counter += 1
                        self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int.from_bytes(
                            binascii.unhexlify(i), byteorder="little"), 17934+counter)
                    print(new_name)
                    break
            elif len(new_name) == 0:
                break

    def Characters(self):
        # Get all potential characters
        all_characters = [
            self.SaveHeader["firstname"].lower(), 
            "yukari", 
            "junpei",
            "akihiko",
            "mitsuru",
            "fuuka",
            "aigis",
            "ken",
            "koromaru",
            "shinjiro"
        ]
        
        # Filter to only show unlocked characters
        unlocked_characters = []
        for char in all_characters:
            if self.IsCharacterUnlocked(char):
                unlocked_characters.append(char)
        
        if not unlocked_characters:
            print("\nNo characters available to edit.")
            return
            
        while True:
            print("\nChoose the character to edit (put nothing to exit 'Characters' editing):")
            
            # Display available characters
            for i, char in enumerate(unlocked_characters):
                if char == self.SaveHeader["firstname"].lower():
                    display_name = self.SaveHeader["firstname"]
                else:
                    display_name = char[0:1].upper() + char[1:]
                print(f"    {i+1} : {display_name}")
                
            a = input().lower()
            
            # Check if the input is a valid character number
            if a.isdigit() and int(a) >= 1 and int(a) <= len(unlocked_characters):
                char_index = int(a) - 1
                char_key = unlocked_characters[char_index]
                
                if char_key == self.SaveHeader["firstname"].lower():
                    bbc = self.SaveHeader['firstname']
                else:
                    bbc = char_key[0:1].upper() + char_key[1:]
                while True:
                    command = input(
                        f"(type help to see comand) ('{bbc}' stats editing) :  ").lower()
                    if command == "edit current_pv":
                        while True:
                            z = input(
                                F"New {bbc} PV (to increase Max PV, increase the Level) (999 max | put nothing to cancel): ")
                            if z == "":
                                break
                            else:
                                try:
                                    z = int(z)
                                    if z > 0 and z < 1000:
                                        self.js = self.SaveByNameN(
                                            self.js, "UInt32Property", 0, z, self.Data["characters"][char_key]["current_pv"])
                                        break
                                except:
                                    pass
                    elif command == "edit current_pc":
                        while True:
                            z = input(
                                F"New {bbc} PC (to increase Max PC, increase the Level) (999 max | put nothing to cancel): ")
                            if z == "":
                                break
                            else:
                                try:
                                    z = int(z)
                                    if z > 0 and z < 1000:
                                        self.js = self.SaveByNameN(
                                            self.js, "UInt32Property", 0, z, self.Data["characters"][char_key]["current_pc"])
                                        break
                                except:
                                    pass
                    elif command == "edit level":
                        while True:
                            z = input(
                                F"New {bbc} Level (99 max | put nothing to cancel): ")
                            if z == "":
                                break
                            else:
                                try:
                                    z = int(z)
                                    if z > 0 and z < 100:
                                        if char_key == self.SaveHeader["firstname"].lower():
                                            self.js[1]["value"] = self.SaveByName(
                                                self.js[1]["value"], "PlayerLevel", 0, 1, z, "UInt32Property")
                                        self.js = self.SaveByNameN(
                                            self.js, "UInt32Property", 0, z, self.Data["characters"][char_key]["level"])
                                        break
                                except:
                                    pass
                    elif command == "edit exp":
                        while True:
                            z = input(
                                F"New {bbc} Exp (4294967295 max | put nothing to cancel): ")
                            if z == "":
                                break
                            else:
                                try:
                                    z = int(z)
                                    if z > 0 and z < 4294967296:
                                        self.js = self.SaveByNameN(
                                            self.js, "UInt32Property", 0, z, self.Data["characters"][char_key]["exp"])
                                        break
                                except:
                                    pass

                    elif command == "print":
                        for i in self.Data["characters"][char_key].keys():
                            print(i)
                    elif command == "get" or command[0:4] == "get ":
                        av = command.split(" ")
                        if len(av) == 2:
                            try:
                                print("")
                                print(self.LoadByNameN(self.js, "UInt32Property", 0,
                                      self.Data["characters"][char_key][av[1]]))
                            except Exception as e:
                                pass
                    elif command == "back":
                        break
                    elif command == "help":
                        print("")
                        print(
                            f"back : to exit {bbc} editing\nprint : show editable value name\nedit 'value_name' : edit the value of 'value_name'\nget 'value_name' : get the value of 'value_name'")
            elif a == None:
                pass

            elif a == "":
                break

    def Sociallink(self):
        character_name = ['SEES', 'Tomochika', 'Yamagishi', 'Kirijo', 'Odagiri', 'Kitamura', 'Takeba', 'Miyamoto', 'Fushimi', 'Maya', 'Hiraga',
                          'Nishiwaki', 'Maiko', 'Pharos', 'Bebe', 'Tanaka', 'Mutatsu', 'Hayase', 'Suemitsu', 'Kamiki', 'Nyx Annihilation Team', 'Aigis']

        while True:
            print(
                f"\nChose the social-link to edit (put nothing to exit 'Social-Link' editing) :")
            counter = 0
            for i in character_name:
                counter += 1
                print(f"    {counter} : {i}")
            a = input().lower()
            if a in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']:
                bbc = character_name[int(a)-1].lower()
                bbc2 = character_name[int(a)-1]
                while True:
                    command = input(
                        f"(type help to see comand) (Social-Link editing {bbc2}): ")
                    int("00000032", 16)
                    if command == "edit level":
                        integer = self.LoadByNameN(
                            self.js, "UInt32Property", 0, self.Data["sociallink"][bbc])
                        if integer == None:
                            integer = 0
                        load = binascii.hexlify(int.to_bytes(
                            integer, 4, byteorder="big")).decode()
                        level_load = load[4:len(load)]
                        point_load = load[0:4]
                        while True:
                            new_level = input(
                                f"New {bbc2} relation level (10 max | put nothing to cancel): ")
                            try:
                                new_level = int(new_level)
                                if new_level > 0 and new_level <= 10:
                                    if new_level == 10:
                                        point_load = "0000"
                                    load = point_load + \
                                        binascii.hexlify(int.to_bytes(
                                            new_level, 2, byteorder="big")).decode()
                                    self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int(
                                        load, 16), self.Data["sociallink"][bbc])
                                elif new_level == 0:
                                    self.js = self.DelByNameN(
                                        self.js, "UInt32Property", 0, self.Data["sociallink"][bbc])
                                new_bin = "0b"
                                for iuesn in self.Data["sociallink"].values():
                                    tempp = self.LoadByNameN(
                                        self.js, "UInt32Property", 0, iuesn)
                                    if tempp != None and tempp > 0:
                                        new_bin += "1"
                                    else:
                                        new_bin += "0"
                                new_bin = eval(new_bin)
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, new_bin, 103)
                                break
                            except:
                                if new_level == "":
                                    break
                    elif command == "edit point":
                        integer = self.LoadByNameN(
                            self.js, "UInt32Property", 0, self.Data["sociallink"][bbc])
                        if integer == None:
                            integer = 0
                        load = binascii.hexlify(int.to_bytes(
                            integer, 4, byteorder="big")).decode()
                        level_load = load[4:len(load)]
                        point_load = load[0:4]
                        while True:
                            new_point = input(
                                f"New {bbc2} relation points (100 max | put nothing to cancel): ")
                            try:
                                new_point = int(new_point)
                                if new_point > 0 and new_point <= 100:
                                    if int(level_load, 16) < 10 and int(level_load, 16) > 0:
                                        load = binascii.hexlify(int.to_bytes(
                                            new_point, 2, byteorder="big")).decode()+level_load
                                        self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int(
                                            load, 16), self.Data["sociallink"][bbc])
                                        break
                                    else:
                                        print(
                                            "Can't edit point if relation level is 10 or 0")
                                        break

                            except Exception as e:
                                print(e)
                                if new_point == "":
                                    break
                    elif command == "print":
                        print("level\npoints")
                    elif command == "get" or command[0:4] == "get ":
                        integer = self.LoadByNameN(
                            self.js, "UInt32Property", 0, self.Data["sociallink"][bbc])
                        load = binascii.hexlify(int.to_bytes(
                            integer, 4, byteorder="big")).decode()
                        level_load = load[4:len(load)]
                        point_load = load[0:4]
                        av = command.split(" ")
                        if len(av) == 2:
                            if av[1] == "level" or av[1] == "levels":
                                print(f'\n{int(level_load, 16)}')
                            elif av[1] == "point" or av[1] == "points":
                                print(f"\n{int(point_load, 16)}")
                    elif command == "back":
                        break
                    elif command == "help":
                        print("")
                        print(
                            f"back : to exit {bbc2} relation editing\nprint : show editable value name\nedit 'value_name' : edit the value of 'value_name'\nget 'value_name' : get the value of 'value_name'")
            elif a == "":
                break

    def Socialrank(self):
        while True:
            command = input(
                f"(type help to see comand) (social-rank editing) :  ")
            if command == "edit charm":
                while True:
                    z = input(F"New charm (100 max | put nothing to cancel): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z > 0 and z < 101:
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, z, self.Data["socialrank"]["charm"])
                                break
                        except:
                            pass
            elif command == "edit academics":
                while True:
                    z = input(
                        F"New academics (230 max | put nothing to cancel): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z > 0 and z < 231:
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, z, self.Data["socialrank"]["academics"])
                                break
                        except:
                            pass
            elif command == "edit courage":
                while True:
                    z = input(F"New courage (80 max | put nothing to cancel): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z > 0 and z < 81:
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, z, self.Data["socialrank"]["courage"])
                                break
                        except:
                            pass

            elif command == "print":
                for i in self.Data["socialrank"].keys():
                    print(i)
            elif command == "get" or command[0:4] == "get ":
                av = command.split(" ")
                if len(av) == 2:
                    try:
                        print("")
                        print(self.LoadByNameN(self.js, "UInt32Property",
                              0, self.Data["socialrank"][av[1]]))
                    except Exception as e:
                        pass
            elif command == "back":
                break
            elif command == "help":
                print("")
                print(f"back : to exit social-rank editing\nprint : show editable value name\nedit 'value_name' : edit the value of 'value_name'\nget 'value_name' : get the value of 'value_name'")

    def Playtime(self):
        # Get current playtime and source location
        current_playtime = None
        playtime_location = None
        
        # Try primary location
        primary_location = 12833 + self.id_offset
        current_playtime = self.LoadByNameN(self.js, "UInt32Property", 0, primary_location)
        if current_playtime is not None:
            playtime_location = primary_location
        
        # Try header location
        if current_playtime is None:
            header_playtime = self.LoadByName(self.js[1]["value"], "PlayTime", 0, 1)
            if header_playtime is not None:
                current_playtime = header_playtime
                playtime_location = "header"
                
        # If we found a playtime value, show it
        if current_playtime is not None:
            hours = current_playtime // 3600
            minutes = (current_playtime % 3600) // 60
            seconds = current_playtime % 60
            print(f"\nCurrent playtime: {hours}h {minutes}m {seconds}s ({current_playtime} seconds)")
            if playtime_location == "header":
                print("Playtime is stored in the save header")
            else:
                print(f"Playtime is stored at offset: {playtime_location}")
                
        # Edit playtime
        while True:
            try:
                # Offer to input in hours/minutes/seconds format
                print("\nEnter new playtime (max ~30,000 hours):")
                print("1. Enter raw seconds")
                print("2. Enter as hours:minutes:seconds")
                print("3. Cancel")
                choice = input("Choose option (1/2/3): ")
                
                if choice == "3" or choice == "":
                    break
                    
                play = 0
                if choice == "1":
                    play = int(input("Enter seconds: "))
                elif choice == "2":
                    h = int(input("Hours: "))
                    m = int(input("Minutes (0-59): "))
                    s = int(input("Seconds (0-59): "))
                    if m < 0 or m > 59 or s < 0 or s > 59:
                        print("Invalid minutes or seconds!")
                        continue
                    play = h * 3600 + m * 60 + s
                else:
                    print("Invalid choice!")
                    continue
                
                if play >= 0 and play <= 107998200:  # ~30,000 hours
                    # Update in header
                    self.js[1]["value"] = self.SaveByName(
                        self.js[1]["value"], "PlayTime", 0, 1, play, "UInt32Property")
                    
                    # Update in primary location
                    self.js = self.SaveByNameN(
                        self.js, "UInt32Property", 0, play, 12833 + self.id_offset)
                    
                    # Update data
                    self.Data["playtime"] = play
                    
                    # Show the new playtime
                    hours = play // 3600
                    minutes = (play % 3600) // 60
                    seconds = play % 60
                    print(f"Playtime updated to: {hours}h {minutes}m {seconds}s ({play} seconds)")
                    break
                else:
                    print("Playtime must be between 0 and 107,998,200 seconds!")
            except ValueError:
                print("Please enter a valid number!")
            except Exception as e:
                print(f"Error: {str(e)}")
                if input("Try again? (y/n): ").lower() != "y":
                    break

    def Dangerous(self):
        while True:
            command = input(
                f"(type help to see comand) (unkwnown|dangerous|could break save) editing :  ").lower()
            if command == "edit player_x":
                while True:
                    z = input(
                        F"New player_x (4294967295 max | put nothing to cancel): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z > 0 and z <= 4294967295:
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, z, 5219 + self.id_offset)
                                break
                        except:
                            pass
            elif command == "edit player_y":
                while True:
                    z = input(
                        F"New player_y (4294967295 max | put nothing to cancel): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z > 0 and z <= 4294967295:
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, z, 5220 + self.id_offset)
                                break
                        except:
                            pass
            elif command == None:  # "edit player_z":
                while True:
                    z = input(
                        F"New player_z (4294967295 max | put nothing to cancel | UNCONFIRMED VALUE ID !): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z > 0 and z <= 4294967295:
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, z, 5221)
                                break
                        except:
                            pass
            elif command == "edit player_direction":
                while True:
                    z = input(
                        F"New player_z (4294967295 max | put nothing to cancel): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z > 0 and z <= 4294967295:
                                self.js = self.SaveByNameN(
                                    self.js, "UInt32Property", 0, z, 5218)
                                break
                        except:
                            pass
            elif command == "print":
                for i in self.Data["dangerous"].keys():
                    print(i)
            elif command == "get" or command[0:4] == "get ":
                a = command.split(" ")
                if len(a) == 2:
                    try:
                        print("")
                        print(self.Data["dangerous"][a[1]])
                    except:
                        pass
            elif command == "back":
                break
            elif command == "help":
                print("")
                print(f"back : to exit |dangerous editing\nprint : show editable value name\nedit 'value_name' : edit the value of 'value_name'\nget 'value_name' : get the value of 'value_name'")
            self.Data["dangerous"] = {"player_x": self.LoadByNameN(self.js, "UInt32Property", 0, 5219 + self.id_offset), "player_y": self.LoadByNameN(
                self.js, "UInt32Property", 0, 5220 + self.id_offset), "player_z": self.LoadByNameN(self.js, "UInt32Property", 0, 5221 + self.id_offset), "player_direction": self.LoadByNameN(self.js, "UInt32Property", 0, 5218 + self.id_offset)}

    def Difficulty(self):
        difficultydata = {"Beginner": 2166366214, "Easy": 2166374406,
                          "Normal": 2166390790, "Hard": 2166423558, "Maniac": 100794368}
        difficultychoose = ["Beginner", "Easy", "Normal", "Hard", "Maniac"]
        while True:
            print("Choose Difficulty (put nothing to cancel :")
            counter = 0
            for i in difficultychoose:
                counter += 1
                print(f"    {counter} : {i}")
            ss = input()
            if ss == "":
                break
            else:
                try:
                    ss = int(ss)
                    if ss > 0 and ss <= 5:
                        self.js = self.SaveByNameN(
                            self.js, "UInt32Property", 0, difficultydata[difficultychoose[ss-1]], 384)
                        break
                except:
                    pass

    def Date(self):
        timedata = [["Very early morning", 257], ["Early morning", 258], ["Morning", 259], ["Lunch break", 260], [
            "Afternoon", 261], ["After school", 262], ["Evening", 263], ["Dark Hour", 264], ["Late evening", 265]]
        daydata = [[30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 28, 4], {2009: [
            "April", "May", "Juin", "July", "August", "September", "October", "November", "December"], 2010: ["January", "Febuary", "March"]}]
        while True:
            command = input(f"(type help to see comand) (date editing) :  ")
            if command == "edit day":
                while True:
                    z = input(
                        F"Choose Year (2009-2010) (put nothing to cancel): ")
                    if z == "":
                        break
                    else:
                        try:
                            z = int(z)
                            if z == 2009 or z == 2010:
                                while True:
                                    print(
                                        "Choose Month (put nothing to cancel) :")
                                    counter = 0
                                    for az in daydata[1][z]:
                                        counter += 1
                                        print(f"    {counter} : {az}")
                                    z2 = input()
                                    if z2 == "":
                                        break
                                    else:
                                        try:
                                            z2 = int(z2)
                                            if (z == 2009 and (z2 > 0 and z2 < 10)) or (z == 2010 and (z2 > 0 and z2 < 4)):
                                                z2 -= 1
                                                if z == 2010:
                                                    z2 += 9
                                                while True:
                                                    offset = 0
                                                    if z2 > 0:
                                                        for iu in range(z2):
                                                            offset += daydata[0][iu]
                                                    item = input(
                                                        f"Choose Day ({daydata[0][z2]} Max) (put nothing to cancel) :")
                                                    if item == "":
                                                        break
                                                    else:
                                                        try:
                                                            item = int(item)
                                                            if (item > 0 and item <= daydata[0][z2]):
                                                                item = (
                                                                    offset+item)-1
                                                                self.js = self.SaveByNameN(
                                                                    self.js, "UInt32Property", 0, item, 1928 + self.id_offset)
                                                                self.js = self.SaveByNameN(
                                                                    self.js, "UInt32Property", 0, item, 1930 + self.id_offset)
                                                                break
                                                        except:
                                                            pass

                                                break
                                        except:
                                            pass
                                break
                        except:
                            pass
            elif command == "edit time":
                while True:
                    print(
                        f"Chosse new hour (put nothing to cancel) (bad modification could break/soft-lock the game but you may fix it (not sure) by re-editing the save)\n    1 : {timedata[0][0]}\n    2 : {timedata[1][0]}\n    3 : {timedata[2][0]}\n    4 : {timedata[3][0]}\n    5 : {timedata[4][0]}\n    6 : {timedata[5][0]}\n    7 : {timedata[6][0]}\n    8 : {timedata[7][0]}\n    9 : {timedata[8][0]}")
                    z = input()
                    try:
                        z = int(z)
                        if z > 0 and z < 10:
                            self.js = self.SaveByNameN(
                                self.js, "UInt32Property", 0, timedata[z-1][1], self.Data["date"]["time"])
                            break
                    except:
                        try:
                            if len(z) == 0:
                                break
                        except:
                            pass
            elif command == "print":
                for i in self.Data["date"].keys():
                    print(i)
            elif command == "get" or command[0:4] == "get ":
                av = command.split(" ")
                if len(av) == 2:
                    try:
                        print("")
                        if av[1] == "time":
                            print(timedata[(self.LoadByNameN(
                                self.js, "UInt32Property", 0, self.Data["date"][av[1]])-257)][0])
                        else:
                            print(self.LoadByNameN(
                                self.js, "UInt32Property", 0, self.Data["date"][av[1]]))
                    except Exception as e:
                        pass
            elif command == "back":
                break
            elif command == "help":
                print("")
                print(f"back : to exit date editing\nprint : show editable value name\nedit 'value_name' : edit the value of 'value_name'\nget 'value_name' : get the value of 'value_name'")

    def Personas(self):
        personaid = [["( You'r Skill ID )", -1], ["Io", 1], ["Isis", 2],
                     ["Hermès", 3], ["Trismégiste", 4], ["Oni", 60]]
        skillid = [["( You'r Skill ID )", -1], ["Agi", 10], ["Nu", 89]]
        skillname = {-1: "( You'r Skill ID )", 10: "Agi", 89: "Nu"}
        while True:
            try:
                answer = input(
                    "Choose personas slot (1-6) (put nothing to cancel): ")
                answer = int(answer)
                if answer >= 1 and answer <= 6:
                    while True:
                        command = input(
                            f"(type help to see comand) (Personas slot {answer} editing): ").lower()
                        if command == None:
                            pass
                        elif command == "edit persona":
                            while True:
                                counter = 0
                                print(
                                    "Choose new personas (put nothing to cancel):")
                                for i in personaid:
                                    counter += 1
                                    print(f"    {counter} : {i[0]}")
                                persona_answer = input("")
                                try:
                                    persona_answer = int(persona_answer)
                                    if persona_answer > 0 and persona_answer <= len(personaid) and personaid[persona_answer-1][1] != -1:
                                        personas_new_value = int.from_bytes(binascii.unhexlify(
                                            (personaid[persona_answer-1][1]).to_bytes(2, byteorder='little').hex()+"01"), byteorder="big")
                                    elif persona_answer > 0 and persona_answer <= len(personaid):
                                        while True:
                                            persona_input_id = input(
                                                "Persona ID (put nothing to cancle) (bad Persona ID could crash the game): ")
                                            try:
                                                persona_input_id = int(
                                                    persona_input_id)
                                                if persona_input_id >= 0:
                                                    personas_new_value = int.from_bytes(binascii.unhexlify(
                                                        (persona_input_id).to_bytes(2, byteorder='little').hex()+"01"), byteorder="big")
                                                    break
                                            except:
                                                if persona_input_id == "":
                                                    break
                                    verify_bool = False
                                    for verify in self.Data["personavalueid"]["persona"]:
                                        if verify != self.Data["personavalueid"]["persona"][answer-1]:
                                            if self.LoadByNameN(self.js, "UInt32Property", 0, verify) == personas_new_value:
                                                verify_bool = True
                                    if verify_bool == False:
                                        self.js = self.SaveByNameN(
                                            self.js, "UInt32Property", 0, personas_new_value, self.Data["personavalueid"]["persona"][answer-1])
                                        break
                                    elif verify_bool == True:
                                        print("\n\nCan't have double persona")
                                except Exception as e:
                                    if persona_answer == "":
                                        break
                        elif command == "edit level":
                            while True:
                                new_level = input(
                                    "Choose persona's level (99 max) (put nothing to cancel): ")
                                try:
                                    new_level = int(new_level)
                                    if new_level > 0 and new_level <= 99:
                                        self.js = self.SaveByNameN(
                                            self.js, "UInt32Property", 0, new_level, self.Data["personavalueid"]["level"][answer-1])
                                        break
                                except Exception as e:
                                    print(e)
                                    if new_level == "":
                                        break
                        elif command == "edit exp":
                            while True:
                                new_exp = input(
                                    "Choose persona's exp (4294967295 max) (put nothing to cancel): ")
                                try:
                                    new_exp = int(new_exp)
                                    if new_exp > 0 and new_exp <= 4294967295:
                                        self.js = self.SaveByNameN(
                                            self.js, "UInt32Property", 0, new_exp, self.Data["personavalueid"]["exp"][answer-1])
                                        break
                                except:
                                    if new_exp == "":
                                        break
                        elif command == "edit skill":
                            skill_process = [
                                "skill_slot_1", "skill_slot_2", "skill_slot_3", "skill_slot_4"]
                            skill_list = []
                            try:
                                for skill_i in skill_process:
                                    if skill_i == "skill_slot_4":
                                        pass
                                    skill_tmp = self.LoadByNameN(
                                        self.js, "UInt32Property", 0, self.Data["personavalueid"][skill_i][answer-1])
                                    skill_tmp = binascii.hexlify(int.to_bytes(
                                        skill_tmp, 4, byteorder="big")).decode()
                                    if skill_tmp[0:4] != "0000":
                                        skill_list.append(
                                            int(skill_tmp[0:4], 16))
                                    if skill_tmp[4:len(skill_tmp)] != "0000":
                                        skill_list.append(
                                            int(skill_tmp[4:len(skill_tmp)], 16))
                            except:
                                pass
                            while True:
                                print(
                                    "Skills : (type ('add' to add skill and 'del 'numero'' to remove skill) (you can't add to an non-empty place)")
                                counter = 0
                                for iss in skill_list:
                                    counter += 1
                                    try:
                                        print(
                                            f"    {counter} : {skillname[iss]}")
                                    except:
                                        print(f"    {counter} : {iss}")
                                command2 = input("Add or Del skill: ")
                                try:
                                    if command2.split(" ")[0].lower() == "del":
                                        if len(command2.split(" ")) > 1:
                                            if int(command2.split(" ")[1]) > 0 and int(command2.split(" ")[1]) <= len(skill_list):
                                                counter2 = 0
                                                lenn = len(skill_list)
                                                for ibn in range(lenn):
                                                    counter2 += 1
                                                    if counter2 == int(command2.split(" ")[1]):
                                                        del skill_list[ibn]
                                                        break
                                    elif command2 == "add" and len(skill_list) < 8:
                                        while True:
                                            counter2 = 0
                                            for ibn in skillid:
                                                counter2 += 1
                                                print(
                                                    f"    {counter2} : {ibn[0]}")
                                            skill2_answer = input()
                                            try:
                                                skill2_answer = int(
                                                    skill2_answer)
                                                if skill2_answer > 0 and skill2_answer <= len(skillid):
                                                    if skillid[skill2_answer-1][1] > -1:
                                                        skill_list.append(
                                                            skillid[skill2_answer-1][1])
                                                    else:
                                                        while True:
                                                            skill_input_id = input(
                                                                "Skill ID (put nothing to cancle) (bad Skill ID could crash the game): ")
                                                            try:
                                                                skill_input_id = int(
                                                                    skill_input_id)
                                                                if skill_input_id >= 0:
                                                                    skill_list.append(
                                                                        skill_input_id)
                                                                    break
                                                            except:
                                                                if skill_input_id == "":
                                                                    break
                                                   
                                                    break
                                            except Exception as e:
                                                print(e)
                                                if skill2_answer == "":
                                                    break
                                    elif command2 == "":
                                        print(True)
                                        counter = 0
                                        val1 = ""
                                        val2 = ""
                                        val3 = ""
                                        val4 = ""
                                        for iuio in skill_list:
                                            counter += 1
                                            if counter < 3:
                                                val1 += (iuio).to_bytes(2,
                                                                        byteorder='big').hex()
                                            elif counter < 5:
                                                val2 += (iuio).to_bytes(2,
                                                                        byteorder='big').hex()
                                            elif counter < 7:
                                                val3 += (iuio).to_bytes(2,
                                                                        byteorder='big').hex()
                                            else:
                                                val4 += (iuio).to_bytes(2,
                                                                        byteorder='big').hex()

                                        if val1 != "":
                                            self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int(
                                                val1, 16), self.Data["personavalueid"]["skill_slot_1"][answer-1])
                                        else:
                                            self.js = self.DelByNameN(
                                                self.js, "UInt32Property", 0, self.Data["personavalueid"]["skill_slot_1"][answer-1])
                                        if val2 != "":
                                            self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int(
                                                val2, 16), self.Data["personavalueid"]["skill_slot_2"][answer-1])
                                        else:
                                            self.js = self.DelByNameN(
                                                self.js, "UInt32Property", 0, self.Data["personavalueid"]["skill_slot_2"][answer-1])
                                        if val3 != "":
                                            self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int(
                                                val3, 16), self.Data["personavalueid"]["skill_slot_3"][answer-1])
                                        else:
                                            self.js = self.DelByNameN(
                                                self.js, "UInt32Property", 0, self.Data["personavalueid"]["skill_slot_3"][answer-1])
                                        if val4 != "":
                                            print(True)
                                            self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int(
                                                val4, 16), self.Data["personavalueid"]["skill_slot_4"][answer-1])
                                            print(False)
                                        else:
                                            self.js = self.DelByNameN(
                                                self.js, "UInt32Property", 0, self.Data["personavalueid"]["skill_slot_4"][answer-1])
                                        break
                                except:
                                    pass
                        elif command == "edit stats":
                            varr = ["Fo", "Ma", "En", "Ag", "Ch"]
                            fomaenag = ""
                            ch = ""
                            for inns in varr:
                                while True:  # _ch
                                    inputt = input(
                                        f"Set new {inns} (max 99): ")
                                    try:
                                        inputt = int(inputt)
                                        if inputt > 0 and inputt < 100:
                                            if inns == "Ch":
                                                ch = self.js = self.SaveByNameN(
                                                    self.js, "UInt32Property", 0, inputt, self.Data["personavalueid"]["ch"][answer-1])
                                                break
                                            else:
                                                fomaenag += (inputt).to_bytes(1,
                                                                              byteorder='little').hex()
                                                break
                                    except:
                                        pass

                            self.js = self.SaveByNameN(self.js, "UInt32Property", 0, int.from_bytes(binascii.unhexlify(
                                fomaenag), byteorder="big"), self.Data["personavalueid"]["fo_ma_en_ag"][answer-1])

                        elif command == "print":
                            print("")
                            stat_show = False
                            skill_show = False
                            for i in self.Data["personavalueid"].keys():
                                if (i == "fo_ma_en_ag" or i == "ch"):
                                    if (stat_show == False):
                                        print("stats")
                                        stat_show = True
                                elif ("skill_slot_" in i):
                                    if (skill_show == False):
                                        print("skill")
                                        skill_show = True
                                else:
                                    print(i)
                        elif command == "help":
                            print("")
                            print(
                                "back : to exit persona slot {answer} editing\nprint : show editable value\nedit 'value_name' : edit the value of 'value_name'")
                        elif command == "back":
                            break
            except:
                if answer == "":
                    break

    def Money(self):
        while True:
            try:
                new_name = input(
                    "New Money (9999999 max | put nothing to cancel): ")
                new_name = int(new_name)
                if new_name >= 0 and new_name <= 9999999:
                    self.js = self.SaveByNameN(
                        self.js, "UInt32Property", 0, new_name, 7257 + self.id_offset)
                    self.Data["money"] = new_name
                    print(new_name)
                    break
            except:
                try:
                    if len(new_name) == 0:
                        break
                except:
                    pass

    def DetectSaveFormatVersion(self):
        """
        Enhanced method to detect save format version with multiple check points.
        Returns 4 for new format, 0 for old format.
        
        Detection strategy:
        - Check multiple important values at both old and new locations
        - Use a voting system to determine the most likely format
        - Validate detection with cross-checks
        
        This improved method should work reliably across all game versions and updates.
        """
        # Dictionary to track detection results
        detection_points = {
            "old_format": 0,
            "new_format": 0
        }
        
        # Check 1: Money value
        money_old = self.LoadByNameN(self.js, "UInt32Property", 0, 7257)
        money_new = self.LoadByNameN(self.js, "UInt32Property", 0, 7261)  # 7257+4
        
        if money_old is not None and money_old > 0:
            detection_points["old_format"] += 2
        if money_new is not None and money_new > 0:
            detection_points["new_format"] += 2
            
        # Check 2: Main character level
        mc_level_old = self.LoadByNameN(self.js, "UInt32Property", 0, 13078)
        mc_level_new = self.LoadByNameN(self.js, "UInt32Property", 0, 13082)  # 13078+4
        
        if mc_level_old is not None and 1 <= mc_level_old <= 99:
            detection_points["old_format"] += 3  # Higher weight for level check
        if mc_level_new is not None and 1 <= mc_level_new <= 99:
            detection_points["new_format"] += 3  # Higher weight for level check
            
        # Check 3: Date value (should be within reasonable range)
        date_old = self.LoadByNameN(self.js, "UInt32Property", 0, 1928)
        date_new = self.LoadByNameN(self.js, "UInt32Property", 0, 1932)  # 1928+4
        
        if date_old is not None and 0 <= date_old <= 365:  # Roughly a year's worth of days
            detection_points["old_format"] += 1
        if date_new is not None and 0 <= date_new <= 365:
            detection_points["new_format"] += 1
            
        # Check 4: Time value (should be within valid range, typically 257-265)
        time_old = self.LoadByNameN(self.js, "UInt32Property", 0, 1929)
        time_new = self.LoadByNameN(self.js, "UInt32Property", 0, 1933)  # 1929+4
        
        if time_old is not None and 256 <= time_old <= 270:
            detection_points["old_format"] += 1
        if time_new is not None and 256 <= time_new <= 270:
            detection_points["new_format"] += 1
            
        # Check 5: Social rank values (should be 1-6)
        academics_old = self.LoadByNameN(self.js, "UInt32Property", 0, 5352)
        academics_new = self.LoadByNameN(self.js, "UInt32Property", 0, 5356)  # 5352+4
        
        if academics_old is not None and 1 <= academics_old <= 6:
            detection_points["old_format"] += 1
        if academics_new is not None and 1 <= academics_new <= 6:
            detection_points["new_format"] += 1
            
        # Cross-validation: Check playtime value for sanity (should be positive but not absurdly large)
        playtime_old = self.LoadByNameN(self.js, "UInt32Property", 0, 12833)
        playtime_new = self.LoadByNameN(self.js, "UInt32Property", 0, 12837)  # 12833+4
        
        # Reasonable playtime range (up to 999 hours in seconds)
        if playtime_old is not None and 0 < playtime_old < 3600 * 999:
            detection_points["old_format"] += 1
        if playtime_new is not None and 0 < playtime_new < 3600 * 999:
            detection_points["new_format"] += 1
        
        # Check 6: Check some social link values (should be positive and below 2^32)
        sees_old = self.LoadByNameN(self.js, "UInt32Property", 0, 5300)
        sees_new = self.LoadByNameN(self.js, "UInt32Property", 0, 5304)  # 5300+4
        
        if sees_old is not None and sees_old > 0:
            detection_points["old_format"] += 1
        if sees_new is not None and sees_new > 0:
            detection_points["new_format"] += 1
            
        # Log the detection results
        print(f"Save format detection results: Old format: {detection_points['old_format']} points, New format: {detection_points['new_format']} points")
            
        # Determine result based on detection points
        if detection_points["new_format"] > detection_points["old_format"]:
            return 4
        else:
            return 0

    def IsCharacterUnlocked(self, character_name):
        """
        Enhanced method to check if a character is unlocked in the save file
        Uses multiple detection strategies including:
        - Character level check
        - Social link status
        - Story progression (using SEES social link)
        - Special character-specific checks
        
        Returns True if the character is unlocked, False otherwise
        """
        # Main character is always unlocked
        if character_name.lower() == self.SaveHeader["firstname"].lower():
            return True
            
        # Get character data
        char_data = self.Data["characters"].get(character_name.lower())
        if not char_data:
            return False
        
        # Primary check: Character level (most reliable)
        level = self.LoadByNameN(self.js, "UInt32Property", 0, char_data["level"])
        if level is not None and level > 0:
            return True
        
        # Secondary check: Social link status (for characters with social links)
        if char_data["social_link_id"] is not None:
            social_link = self.LoadByNameN(self.js, "UInt32Property", 0, char_data["social_link_id"])
            if social_link is not None and social_link > 0:
                return True
        
        # Tertiary check: Story progression based on SEES social link
        sees_link = self.LoadByNameN(self.js, "UInt32Property", 0, 5300 + self.id_offset)
        if sees_link is not None:
            sees_rank = sees_link & 0xFFFF
            
            # Early characters (available after first full moon)
            if sees_rank >= 1 and character_name.lower() in ["yukari", "junpei"]:
                return True
                
            # Characters available after a few full moons
            if sees_rank >= 2 and character_name.lower() in ["mitsuru", "akihiko", "fuuka"]:
                return True
                
            # Mid-game characters
            if sees_rank >= 4 and character_name.lower() in ["shinjiro", "ken", "koromaru"]:
                return True
                
            # Late-game character (Aigis)
            if sees_rank >= 7 and character_name.lower() == "aigis":
                return True
        
        # Character-specific checks (some characters join at specific story points)
        
        # Special check for Aigis: Check Aigis social link as well
        if character_name.lower() == "aigis":
            aigis_link = self.LoadByNameN(self.js, "UInt32Property", 0, 5342 + self.id_offset)
            if aigis_link is not None and aigis_link > 0:
                return True
        
        # Default to false if no detection method succeeded
        return False
