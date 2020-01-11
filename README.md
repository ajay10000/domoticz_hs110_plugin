# TP-Link HS100/110/v2 plugin.py
Log TP-Link HS100/110/v2 switch, voltage, current and power readings to Domoticz.

Based on the original plugin by Dan Hallgren:
https://github.com/dahallgren/domoticz-tplink-smartplug/blob/master/plugin.py

A good reference also by lordzurp:
https://github.com/lordzurp/domoticz-tplink-smartplug/blob/master/plugin.py

### Installation
You must have the Domoticz Python Plugin Manager installed for this plugin to work.  Refer to https://www.domoticz.com/wiki/Python_Plugin_Manager

To install or update your current TP-Link HS100/110/v2 plugin script, do the following.
* Set your user defined variables in plugin.py.
* Copy plugin.py to the Domoticz plugins folder
Example: /home/pi/domoticz/plugins/hs110

### NOTES:
* Change any Domoticz.Debug(...) lines to Domoticz.Log(...) to log specific lines to Domoticz without turning on Debug mode. 

* If you modify plugin.py after it is installed, restart the hardware plugin on the Domoticz Hardware page.  Do this by clicking the Update button with the plugin hardware selected.

* Turn Debug on for the plugin hardware in the Domoticz Hardware page to help sort out any issues.

* Refer to the Domoticz hardwaretypes.h source code to find and/or experiment with different hardware types and subtypes. Use a hex to decimal converter (or vice versa) if required.
https://github.com/domoticz/domoticz/blob/development/hardware/hardwaretypes.h

* Refer to the Dommoticz 'Developing a Python plugin' wiki for useful information when modifying a plugin.
https://www.domoticz.com/wiki/Developing_a_Python_plugin

### Change log for v0.2.5 2020-01-11
* Added the 'create_device' flag to allow new devices to be created. Required on first run for plugin. Domoticz log will show device creation errors on subsequent plugin startup if this is left on, but this should not cause any issues.  Set to True if you wish to add a device.  Set to False once all devices are created.  Restart the plugin Hardware each time it is changed.

Note that you must delete a device if you wish to change its type or subtype or any other parameters.  You don't need to delete all of the Devices created by the plugin.

* Updated some of the Domoticz.Debug(...) lines for consistency.