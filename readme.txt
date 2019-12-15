
To update your current TP-Link HS100/110/v2 script.
1. Set your user defined variables in plugin.py
# Start user editable variables
base_url = "http://rpi3:8080/"  # Modify with your IP# or domain
interval = 1  # heartbeat in 10 second multiples
HS110_divider = 1000  # 1000 or 1 depending on your hardware version of HS110
suppress_socket_error = True  # Suppress error messages in Domoticz after the first

2. Copy plugin.py to Domoticz plugins folder
Example: /home/pi/domoticz/plugins/hs110

NOTE: Change a Domoticz.Debug(...) line to Domoticz.Log(...) to log specific lines without turning on Debug mode. 