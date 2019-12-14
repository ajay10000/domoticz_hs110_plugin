
To update your current script.
1. Create Domoticz User Variable. 
Example: Variable name = HS110_1_State, Variable type = String, Current value = off
2. Get the User Variable Index from Domoticz to include in plugin.py.

3. Set up user defined variables in plugin.py
# Start user editable variables
base_url = "http://rpi3:8080/"  # Modify with your IP# or domain
interval = 1  # heartbeat in 10 second multiples
user_variable_name = "HS110_1_State"  # Your Domoticz User Variable name
user_variable_idx = 3 # Your User Variable Index
user_variable_value = ""  
user_variable_type = 2 #string
HS110_divider = 1000  # 1000 or 1 depending on your hardware version of HS110
suppress_socket_error = True  # Suppress error messages in Domoticz after the first

4. Copy plugin.py to Domoticz plugins folder
Example: /home/pi/domoticz/plugins/hs110