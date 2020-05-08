# Domoticz TP-Link Wi-Fi Smart Plug plugin
#
# Plugin based on reverse engineering of the TP-Link HS110, courtesy of Lubomir Stroetmann and Tobias Esser.
# https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/
#
# Original Author: Dan Hallgren
# Modified by: Andrew P
#
"""
<plugin key="tplinksmartplug" name="TP-Link Wi-Fi Smart Plug HS100/HS110/v2" version="0.2.6">
    <description>
        <h2>TP-Link Wi-Fi Smart Plug</h2>
        <ul style="list-style-type:square">
            <li>On/off switching (HS100 and HS110/HS110v2)</li>
            <li>Realtime power, current and voltage (HS110/HS110v2 only)</li>
        </ul>
        <h3>Devices added to Domoticz:</h3>
        <ul style="list-style-type:square">
            <li>switch - On/Off (All models)</li>
            <li>Realtime power in Watts (HS110/HS110v2)</li>
            <li>Realtime current in Amps (HS110/HS110v2)</li>
            <li>Realtime voltage in Volts (HS110/HS110v2)</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true"/>
        <param field="Mode1" label="Model" width="150px" required="false">
             <options>
                <option label="HS100" value="HS100" default="true"/>
                <option label="HS110/HS110v2" value="HS110"  default="false" />
             </options>
        </param>
        <param field="Mode2" label="Add devices? (Only required on install then can be turned off)" width="75px">
            <options>
                <option label="True" value="True"/>
                <option label="False" value="False"  default="true" />
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import json, socket, Domoticz

# Start user editable variables
base_url = "http://rpi4:8080/"  # Modify with your IP# or domain
interval = 1  # heartbeat in 10 second multiples
HS110_divider = 1000  # 1000 or 1 depending on your firmware version of HS110
suppress_socket_error = True  # Suppress error messages in Domoticz after the first
# End user editable variables

PORT = 9999
STATES = ('off', 'on', 'unknown')

class TpLinkSmartPlugPlugin:
    enabled = False
    connection = None

    def __init__(self):
        self.interval = interval  # *10 seconds
        self.heartbeatcounter = 0
        self.socket_error_suppress = suppress_socket_error
        self.last_state = STATES[2]
        self.state_flag = False
          
    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()
 
        if len(Devices) == 0:
            # Create a switch, suitable for all models
            Domoticz.Device(Name="switch", Unit=1, TypeName="Switch", Used=1).Create()
            Domoticz.Log("Tp-Link smart plug switch created")

        if "HS110" in Parameters["Mode1"] and Parameters["Mode2"] == "True":
            # Create measuring devices here
            Domoticz.Device(Name="current (A)", Unit=2, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="voltage (V)", Unit=3, Type=243, Subtype=8).Create()
            Domoticz.Device(Name="power (W)", Unit=4, Type=243, Subtype=29).Create()  # Subtype 29 is kWh
          
        Domoticz.Debug("Number of devices: {}".format(str(len(Devices))))            
        state = self.get_switch_state()
        self.last_state = state
        self.set_domoticz_state(state)
    
    def onStop(self):
        Domoticz.Debug("onStop called")
        pass

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        pass

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Debug("onMessage called")
        pass

    def onCommand(self, unit, command, level, hue):
        Domoticz.Debug("onCommand called for Unit {}: Parameter {}, Level {}".format(str(unit), str(command), str(level)))

        if command.lower() == 'on':
            new_state = 1
            state = (1, '100')
        else:
            new_state = 0
            state = (0, '0')
        cmd = {
            "system": {
                "set_relay_state": {"state": new_state}
            }
        }
        
        result = self._send_json_cmd(json.dumps(cmd))
        Domoticz.Debug("got response: {}".format(result))

        err_code = result.get('system', {}).get('set_relay_state', {}).get('err_code', 1)

        if err_code == 0:
            # Update Domoticz
            Devices[1].Update(*state)

        # Reset counter so we trigger emeter poll next heartbeat
        self.heartbeatcounter = 0

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: {}, {}, {}, {}, {}, {}, {}".format(Name, Subject, Text, Status, str(Priority), Sound, ImageFile))

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")
        pass

    def onHeartbeat(self):
        if self.heartbeatcounter % self.interval == 0:
            self.update_emeter_values()
        state = self.get_switch_state()
        Domoticz.Debug("Last state: {}, Switch state: {}, Domoticz device state: {}".format(self.last_state, state, STATES[Devices[1].nValue]))
        if (self.last_state == STATES[2]) and (state != STATES[2]):
            Domoticz.Log("Switch device is available, state is {}".format(state))
            self.state_flag = False
        if self.last_state != state:
            self.last_state = state
        if (state != STATES[2]) and (STATES[Devices[1].nValue] != state):
            self.set_domoticz_state(state)
        if (state == STATES[2]) and (self.state_flag == False):  # device state unknown
            self.set_domoticz_state(STATES[0])  # turn off Domoticz switch
            Domoticz.Log("Switch device unavailable, Domoticz device switched off")
            self.state_flag = True
        self.heartbeatcounter += 1

    def _encrypt(self, data):
        key = 171
        result = b"\x00\x00\x00" + chr(len(data)).encode('latin-1')
        for i in data.encode('latin-1'):
            a = key ^ i
            key = a
            result += bytes([a])
        return result

    def _decrypt(self, data):
        key = 171
        result = ""
        for i in data:
            a = key ^ i
            key = i
            result += bytes([a]).decode('latin-1')
        return result

    def _send_json_cmd(self, cmd):
        ret = {}
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5)
            sock.connect((Parameters["Address"], PORT))
            data = self._encrypt(cmd)
            sock.send(data)
            data = sock.recv(1024)
            Domoticz.Debug('data len: {}'.format(len(data)))
            self.socket_error_suppress = False
        except socket.error as e:
            if self.socket_error_suppress == False:
                Domoticz.Log('Send command error: {}'.format(str(e)))
                if suppress_socket_error == True:
                    self.socket_error_suppress = True
                    # Switch is probably off/unavailable, so reflect this in Domoticz
                    Domoticz.Log("Switching Domoticz device off as hardware is not responding")
                    self.set_domoticz_state(STATES[2])
                    self.last_state = STATES[2]
            sock.close()
            return ret
            
        try:
            json_resp = self._decrypt(data[4:])
            ret = json.loads(json_resp)
        except (TypeError, JSONDecodeError) as e:
            Domoticz.Log('Decode error: {}'.format(str(e)))
            Domoticz.Log('Data: {}'.format(str(data)))

        return ret

    def update_emeter_values(self):
        if "HS110" in Parameters["Mode1"]:
            cmd = {
                "emeter": {
                    "get_realtime": {}
                }
            }

            result = self._send_json_cmd(json.dumps(cmd))
            Domoticz.Debug("got response: {}".format(result))
            
            if result != {}:
              realtime_result = result.get('emeter', {}).get('get_realtime', {})
              err_code = realtime_result.get('err_code', 1)

              if err_code == 0:
                  if HS110_divider == 1000:
                      Devices[2].Update(nValue=0, sValue=str(round(realtime_result['current_ma'] / 1000,2)))
                      Devices[3].Update(nValue=0, sValue=str(round(realtime_result['voltage_mv'] / 1000,2)))
                      Devices[4].Update(nValue=0, sValue=str(round(realtime_result['power_mw'] / 1000,2)) + ";" + str(realtime_result['total_wh']))
                  else:
                      Devices[2].Update(nValue=0, sValue=str(round(realtime_result['current'],2)))
                      Devices[3].Update(nValue=0, sValue=str(round(realtime_result['voltage'],2)))
                      Devices[4].Update(nValue=0, sValue=str(round(realtime_result['power'],2)) + ";" + str(realtime_result['total']*1000))

    def get_switch_state(self):
        cmd = {
            "system": {
                "get_sysinfo": "null"
            }
        }
        result = self._send_json_cmd(json.dumps(cmd))
        Domoticz.Debug("Result: {}".format(str(result)))
        err_code = result.get('system', {}).get('get_sysinfo', {}).get('err_code', 1)
        if err_code == 0:
            state = result['system']['get_sysinfo']['relay_state']
        else:
            state = 2
        return STATES[state]

    def set_domoticz_state(self, state):
        if state in 'off':
            Devices[1].Update(0, '0')
        elif state in 'on':
            Devices[1].Update(1, '100')
        else:
            Devices[1].Update(0, '50')
        
global _plugin
_plugin = TpLinkSmartPlugPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'{}:{}'".format(x, str(Parameters[x])))
    Domoticz.Debug("Device count: {}".format(str(len(Devices))))
    for x in Devices:
        Domoticz.Debug("Device:           {}-{}".format(str(x), str(Devices[x])))
        Domoticz.Debug("Device ID:       '{}".format(str(Devices[x].ID)))
        Domoticz.Debug("Device Name:     '{}".format(Devices[x].Name))
        Domoticz.Debug("Device nValue:    {}".format(str(Devices[x].nValue)))
        Domoticz.Debug("Device sValue:   '{}".format(Devices[x].sValue))
        Domoticz.Debug("Device LastLevel: {}".format(str(Devices[x].LastLevel)))
    return
