
Based on the original plugin by Dan Hallgren:
https://github.com/dahallgren/domoticz-tplink-smartplug/blob/master/plugin.py

A good reference also by lordzurp:
https://github.com/lordzurp/domoticz-tplink-smartplug/blob/master/plugin.py

To install or update your current TP-Link HS100/110/v2 script, do the following.
1. Set your user defined variables in plugin.py
# Start user editable variables
base_url = "http://rpi3:8080/"  # Modify with your IP# or domain
interval = 1  # heartbeat in 10 second multiples
HS110_divider = 1000  # 1000 or 1 depending on your hardware version of HS110
suppress_socket_error = True  # Suppress error messages in Domoticz after the first
create_device = False # True if you need to create a device. 
# End user editable variables

2. Copy plugin.py to Domoticz plugins folder
Example: /home/pi/domoticz/plugins/hs110

NOTES:
Change a Domoticz.Debug(...) line to Domoticz.Log(...) to log specific lines to Domoticz without turning on Debug mode. 

If you update plugin.py after it is installed, restart the hardware plugin on the Domoticz Hardware page.  Do this by clicking the Update button with the plugin hardware selected.

Turn Debug on for the hardware in the Domoticz Hardware page to help sort out any issues.

Refer to the Domoticz hardwaretypes.h source code to find and/or experiment with different hardware types and subtypes. Use a hex to decimal converter (or vice versa) if required.
https://github.com/domoticz/domoticz/blob/development/hardware/hardwaretypes.h

Refer to the Dommoticz 'Developing a Python plugin' wiki for useful information when modifying a plugin.
https://www.domoticz.com/wiki/Developing_a_Python_plugin

