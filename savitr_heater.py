# App to control the electric heater by Savitr with WiFi module.
#
# Main script.
#
# Version: 1.0.0.0
# Author: antonwantstosleep, 2020.
# License: MIT

import socket
import select
import time
import appdaemon.plugins.hass.hassapi as hass
import savitr_dicts as dicts


class SavitrHeater(hass.Hass):
    """
    Savitr Heater.
    """

    def initialize(self):
        """
        Start app.
        """

        self.log("Initializing Savitr Heater instance.", level="INFO")

        self.device_name = self.args['device_name']
        self.update_interval = int(self.args["update_interval"])

        self.host = self.args['host']
        self.port = self.args['port']
        self.timeout = self.args['timeout']
        self.socket = None

        self.ingoing_message = None
        self.outgoing_message = None
        self.state = {}

        # Init methods
        self.connect()
        self.subscribe_on_entities()

        # Run every
        if self.update_interval < 5:
            raise Exception("Update interval ({}) must be at least 5 second".format(self.update_interval))
        self.run_every(self.update_state, "now", self.update_interval)

        self.log("Successfully created Savitr Heater %s instance.", self.device_name, level="INFO")

    def terminate(self):
        """
        Terminate app.
        """
        self.log("Terminating Savitr Heater instance.", level="INFO")
        self.disconnect()

    """CONNECTION"""

    def connect(self):
        """
        Open connection.
        """

        self.log("Connecting to %s at %s:%s.", self.device_name, self.host, self.port, level="INFO")

        # Create connection
        self.socket = socket.create_connection((self.host, self.port), self.timeout)

        # Test connection
        self.test_connection()

    def disconnect(self):
        """
        Close connection.
        """

        self.log("Disconnecting from %s at %s:%s.", self.device_name, self.host, self.port, level="INFO")

        # Delete connection
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()

        self.socket = None

    def reconnect(self):
        """
        Close and open connection.
        """

        self.log("Reconnecting to %s at %s:%s.", self.device_name, self.host, self.port, level="INFO")

        self.disconnect()
        time.sleep(self.timeout)
        self.connect()

    def test_connection(self):
        """
        Test connection.
        """

        try:
            chunk = self.socket.recv(192)  # returns a string
            if chunk == b'':
                self.log("Connection to device is broken, please check everything.", level="ERROR")
                raise Exception("Connection to device is broken, please check everything.")
        except Exception as e:
            self.log("Can`t read from device. Error: %s. Reconnecting after %s.", e, self.timeout, level="ERROR")
            self.reconnect()

        self.log("Connected to %s at %s:%s.", self.device_name, self.host, self.port, level="INFO")

    def read(self):
        """
        Read and process message from device.
        """

        if not self.socket:
            self.reconnect()

        try:
            # Read one message
            self.log("Reading message.", level="DEBUG")
            # The return value is a string representing the data received.
            self.ingoing_message = bytearray(self.socket.recv(192))
            self.log("Got a %s byte message. Processing ingoing message...", len(self.ingoing_message), level="INFO")

            # Process it with some magic stuff
            self.ingoing_message = self.process_ingoing_message(self.ingoing_message)

            # Drain input buffer
            self.empty_input_buffer(self.socket)

        except Exception as e:
            self.log("Can`t read from device. Error: %s. Reconnecting after %s.", e, self.timeout, level="ERROR")
            self.reconnect()

    def write(self):
        """
        Process and write message to device.
        """

        if not self.socket:
            self.reconnect()

        try:
            # Process it with some magic stuff
            self.outgoing_message = self.process_outgoing_message(self.outgoing_message)

            # Write one message
            self.log("Writing message.", level="DEBUG")
            bytes_quantity = self.socket.send(self.outgoing_message)  # Returns the number of bytes sent.
            self.log("Message of %s bytes was written.", bytes_quantity, level="INFO")
        except Exception as e:
            self.log("Can`t write to device. Error: %s. Reconnecting after %s.", e, self.timeout, level="ERROR")
            self.reconnect()

    """MAIN"""

    def subscribe_on_entities(self):
        """
        Update Home Assistant entity.
        """

        # Iterate over file dicts.py
        for name, param in dicts.PARAMETERS.items():

            # Check if this can`t be entity - skip
            if 'hass_entity_type' not in param:
                continue

            # Check if we need to listen its state
            if param['hass_entity_type'] not in ['input_number', 'input_select', 'input_boolean']:
                continue

            # Create entity_id
            entity_id = param['hass_entity_type'] + "." + self.device_name + "_" + name

            # Check if this entity does not exist in Home Assistant - skip
            if not self.entity_exists(entity_id):
                continue

            # Register callback
            self.listen_state(self.listen_state_callback, entity=entity_id, attribute='all')

            self.log("Callback for entity %s is registered.", entity_id, level="DEBUG")

    def update_state(self, kwargs=None):
        """
        Decode input message and update the status of this Savitr.
        """

        # Read from device
        self.read()

        # Iterate over file dicts.py
        for name, param in dicts.PARAMETERS.items():

            # Get data from message by address
            # b[start:stop] the start index is inclusive and the end index is exclusive.
            # https://medium.com/python-features/slicing-tricks-lists-str-bytes-6db10066bd23
            bytearray_value = self.ingoing_message[param['read']['byte_start']:param['read']['byte_finish'] + 1]
            self.log("Got raw %s as %s.", name, bytearray_value, level="DEBUG")

            # Convert parameters into readable format
            if param['type'] == 'string':
                value = bytearray_value.decode()
            elif param['type'] == 'int':
                value = int.from_bytes(bytearray_value, param['read']['byte_order'], signed=False)
            elif param['type'] == 'float':
                value = int.from_bytes(bytearray_value, param['read']['byte_order'], signed=False)

                # Protocol maker`s magic for negative temps
                if name in ['coolant_temp', 'air_indoor_temp', 'air_outdoor_temp']:
                    if value > 32767:
                        value |= -65536

                # Also we need to make some calculations (for ex. divide 10)
                if 'evaluate' in param['read']:
                    self.log("Calculating %s with %s...", name, param['read']['evaluate'], level="DEBUG")
                    value = eval(str(value) + param['read']['evaluate'])
                    value = float(value)
            else:
                value = False
            self.log("Decoded %s, value is %s.", name, value, level="DEBUG")

            # Convert some parameters into understandable format
            if 'dictionary' in param:
                self.log("Param dictionary %s, value is %s.", param['dictionary'], value, level="DEBUG")
                value = param['dictionary'][value]['name']

            if name == 'power_supply_state':
                if value == 85:
                    value = 'on'
                else:
                    value = 'off'

            if name == 'air_indoor_temp_control':
                if value == 257:
                    value = 'on'
                else:
                    value = 'off'

            # Updating self.state
            self.state[name] = value

            # Updating entities
            self.update_entity(name, param, value)

    def update_entity(self, name, param, value):
        """
        Update Home Assistant entity.
        """

        # If this can`t be entity - skip
        if 'hass_entity_type' not in param:
            return

        # Create entity_id
        entity_id = param['hass_entity_type'] + "." + self.device_name + "_" + name

        # If this entity does not exist in Home Assistant - skip
        if not self.entity_exists(entity_id):
            return

        # Get entity attributes
        entity = self.get_state(entity_id, attribute="all")
        attributes = entity.get("attributes", {})

        # Add changes reason to attributes
        attributes['reason'] = 'device'

        # Update entity
        self.set_state(entity_id, state=value, attributes=attributes)

        self.log("Entity %s is updated with %s.", entity_id, value, level="DEBUG")

    def listen_state_callback(self, entity, attribute, old, new, kwargs):
        """
        Listen state callback.

        """

        self.log("We are in setter for %s. Attributes: %s. Old: %s. New: %s. Kwargs: %s",
                 entity, attribute, old, new, kwargs, level="DEBUG")

        # If we are here because the device had changed something - return
        if 'reason' in new['attributes']:
            return

        # Get values (maybe strings, floats, ints)
        old_value = old['state']
        new_value = new['state']

        self.log("Setting %s from %s to %s. Creating and sending message.",
                 entity, old_value, new_value, level="INFO")

        # Construct cmd name
        param = entity.split('.')[1]
        param_name = param.replace(self.device_name + '_', '')
        cmd = 'set_' + param_name

        self.log("Param %s. Param_name %s. Cmd is %s.", param, param_name, cmd, level="DEBUG")

        # Execute cmd
        self.execute_cmd(cmd, new_value)

        # Clean input buffer for all queued messages
        self.empty_input_buffer(self.socket)

        # Update everything
        self.update_state()

    def execute_cmd(self, cmd, value):
        """
        Cmd selector.

        """

        if cmd == 'set_wifi':
            self.set_wifi(value)
        elif cmd == 'set_mail':
            self.set_mail(value)
        elif cmd == 'set_heating_mode':
            self.set_heating_mode(value)
        elif cmd == 'set_heating_power':
            self.set_heating_power(value)
        elif cmd == 'set_air_indoor_temp_min':
            self.set_air_indoor_temp_min_max(value, self.state['air_indoor_temp_max'])
        elif cmd == 'set_air_indoor_temp_max':
            self.set_air_indoor_temp_min_max(self.state['air_indoor_temp_min'], value)
        elif cmd == 'set_coolant_temp_min':
            self.set_coolant_temp_min_max(value, self.state['coolant_temp_max'])
        elif cmd == 'set_coolant_temp_max':
            self.set_coolant_temp_min_max(self.state['coolant_temp_min'], value)
        elif cmd == 'set_air_indoor_temp_setpoint':
            self.set_air_indoor_temp_setpoint(value)
        elif cmd == 'set_air_indoor_temp_control':
            self.set_air_indoor_temp_control(value)
        elif cmd == 'reset_to_defaults':
            self.reset_to_defaults(value)
        elif cmd == 'set_coolant_temp_setpoint':
            self.set_coolant_temp_setpoint(value)

    def create_empty_message(self):
        """
        Create empty message.

        - http://pythonlearn.ru/stroki-python/tip-dannyx-bytearray-python/
        """

        # Create empty bytearray
        self.outgoing_message = bytearray(192)

        # TODO: check this out
        self.outgoing_message[66] = 0  # 66 - Should write 0 everytime?

        # Write preamble
        msg_preamble = dicts.PARAMETERS['msg_preamble']
        self.outgoing_message[msg_preamble['write']['byte_start']:msg_preamble['write']['byte_finish'] + 1] = str.encode(msg_preamble['default_value'])

    def add_cmd_code(self, cmd):
        """
        Set cmd code.

        """

        # Get parameter
        param = dicts.PARAMETERS['cmd_code']

        # Get code by name.
        value = dicts.CMD[cmd]['code']

        self.outgoing_message[param['write']['byte_start']] = value
        self.log("Cmd code was set to %s.", value, level="INFO")

    def add_cmd_count(self):
        """
        Set cmd count.

        """

        # Get parameter
        param = dicts.PARAMETERS['cmd_count']

        # Get current counter and increment it. The biggest value is 255.
        value = self.state['cmd_count']
        if value == 255:
            value = 0
        value = value + 1

        self.outgoing_message[param['write']['byte_start']] = value
        self.log("Cmd count was set to %s.", value, level="INFO")

    def add_checksum(self):
        """
        Calculate and add checksum to an outgoing message.
        """

        checksum = self.calculate_checksum(self.outgoing_message, 123)
        self.outgoing_message[124] = checksum & 0xff
        self.outgoing_message[125] = checksum >> 8 & 0xff
        self.outgoing_message[126] = checksum >> 16 & 0xff
        self.outgoing_message[127] = checksum >> 24 & 0xff

    """SETTERS"""

    def set_wifi(self, value):
        """
        Set wifi SSID and password.

        TODO: Implement this.
        """

        # Create message
        self.create_empty_message()
        self.add_cmd_code('set_wifi')
        self.add_cmd_count()

        # Get parameters
        param_ssid = dicts.PARAMETERS['wifi_ssid']
        param_ssid_length = dicts.PARAMETERS['wifi_ssid_length']
        param_password = dicts.PARAMETERS['wifi_password']

        # TODO: get this from input_texts (value)
        ssid = "test"
        ssid_len = len(ssid)
        password = "12345678"
        password_len = len(password)

        # Check values
        if ssid_len > 15:
            raise Exception("SSID name must be 15 symbols max, got %s.", ssid_len)

        if password_len != 8:
            raise Exception("Password must be exactly 8 symbols, got %s.", password_len)

        # Write values
        for i in range(ssid_len):
            self.outgoing_message[param_ssid['write']['byte_start'] + i] = ssid[i]

        self.outgoing_message[param_ssid_length['write']['byte_start']] = ssid_len

        for i in range(password_len):
            self.outgoing_message[param_password['write']['byte_start'] + i] = password[i]

        # Add checksum and write message
        self.add_checksum()
        self.write()

        self.log("SSID was set to %s.", ssid, level="INFO")

    def set_mail(self, value):
        """
        Set mail.

        TODO: Implement this.
        """

        self.log("Mail was set to %s.", value, level="INFO")

    def set_heating_mode(self, value):
        """
        Set heating mode.

        In:
         - value - string
        """

        # Create message
        self.create_empty_message()
        self.add_cmd_code('set_heating_mode')
        self.add_cmd_count()

        # Get parameter
        param = dicts.PARAMETERS['heating_mode']

        # Get code
        for code, mode in param['dictionary'].items():
            if mode['name'] == value:
                value = int(code)
                break

        self.outgoing_message[param['write']['byte_start']] = value

        # Add checksum and write message
        self.add_checksum()
        self.write()

        self.log("Heating mode was set to %s.", value, level="INFO")

    def set_heating_power(self, value):
        """
        Set heating power (heating elements quantity).

        In:
         - value - string
           - 33 - 1 element
           - 66 - 2 elements
           - 100 - 3 elements
        """

        # Create message
        self.create_empty_message()
        self.add_cmd_code('set_heating_power')
        self.add_cmd_count()

        # Convert value to int
        value = int(float(value))

        # Get parameter
        param = dicts.PARAMETERS['heating_power']

        self.outgoing_message[param['write']['byte_start']] = value

        # Add checksum and write message
        self.add_checksum()
        self.write()

        self.log("Heating power was set to %s.", value, level="INFO")

    def set_air_indoor_temp_min_max(self, value_min, value_max):
        """
        Set air indoor minimum and maximum temperature for mail alarms from wifi module.
        We need to set them both at the same time ¯\_(ツ)_/¯

        In:
         - value_min - string, eg. '11.0'
         - value_max - string, eg. '11.0'
        """

        # Create message
        self.create_empty_message()
        self.add_cmd_code('set_air_indoor_temp_min_max')
        self.add_cmd_count()

        # Convert values to int
        value_min = int(float(value_min))
        value_max = int(float(value_max))

        # Get parameter
        param_min = dicts.PARAMETERS['air_indoor_temp_min']
        param_max = dicts.PARAMETERS['air_indoor_temp_max']

        # Also we need to make some calculations (for ex. multiply 10)
        calculated_value_min = value_min
        if 'evaluate' in param_min['write']:
            calculated_value_min = eval(str(value_min) + param_min['write']['evaluate'])
        calculated_value_max = value_max
        if 'evaluate' in param_max['write']:
            calculated_value_max = eval(str(value_max) + param_max['write']['evaluate'])

        # Convert to bytes
        bytes_value_min = calculated_value_min.to_bytes(
            param_min['write']['byte_length'], byteorder=param_min['write']['byte_order'])
        bytes_value_max = calculated_value_max.to_bytes(
            param_max['write']['byte_length'], byteorder=param_max['write']['byte_order'])

        self.outgoing_message[param_min['write']['byte_start']:param_min['write']['byte_finish'] + 1] = bytes_value_min
        self.outgoing_message[param_max['write']['byte_start']:param_max['write']['byte_finish'] + 1] = bytes_value_max

        # Add checksum and write message
        self.add_checksum()
        self.write()

        self.log("Air indoor temp limits were set to min %s, max %s.", value_min, value_max, level="INFO")

    def set_coolant_temp_min_max(self, value_min, value_max):
        """
        Set coolant minimum and maximum temperature for mail alarms from wifi module.
        We need to set them both at the same time ¯\_(ツ)_/¯

        In:
         - value_min - string, eg. '11.0'
         - value_max - string, eg. '11.0'
        """

        # Create message
        self.create_empty_message()
        self.add_cmd_code('set_coolant_temp_min_max')
        self.add_cmd_count()

        # Convert values to int
        value_min = int(float(value_min))
        value_max = int(float(value_max))

        # Get parameter
        param_min = dicts.PARAMETERS['coolant_temp_min']
        param_max = dicts.PARAMETERS['coolant_temp_max']

        # Also we need to make some calculations (for ex. multiply 10)
        calculated_value_min = value_min
        if 'evaluate' in param_min['write']:
            calculated_value_min = eval(str(value_min) + param_min['write']['evaluate'])
        calculated_value_max = value_max
        if 'evaluate' in param_max['write']:
            calculated_value_max = eval(str(value_max) + param_max['write']['evaluate'])

        # Convert to bytes
        bytes_value_min = calculated_value_min.to_bytes(
            param_min['write']['byte_length'], byteorder=param_min['write']['byte_order'])
        bytes_value_max = calculated_value_max.to_bytes(
            param_max['write']['byte_length'], byteorder=param_max['write']['byte_order'])

        self.outgoing_message[param_min['write']['byte_start']:param_min['write']['byte_finish'] + 1] = bytes_value_min
        self.outgoing_message[param_max['write']['byte_start']:param_max['write']['byte_finish'] + 1] = bytes_value_max

        # Add checksum and write message
        self.add_checksum()
        self.write()

        self.log("Coolant temp limits were set to min %s, max %s.", value_min, value_max, level="INFO")

    def set_air_indoor_temp_setpoint(self, value):
        """
        Set air indoor temperature setpoint.

        In:
         - value - string, eg. '11.0'
        """

        # Create message
        self.create_empty_message()
        self.add_cmd_code('set_air_indoor_temp_setpoint')
        self.add_cmd_count()

        # Convert value to int
        value = int(float(value))

        # Get parameter
        param = dicts.PARAMETERS['air_indoor_temp_setpoint']

        self.outgoing_message[param['write']['byte_start']] = value

        # Add checksum and write message
        self.add_checksum()
        self.write()

        self.log("Air indoor temp setpoint was set to %s.", value, level="INFO")

    def set_coolant_temp_setpoint(self, value):
        """
        Set coolant temperature setpoint.

        In:
         - value - string, eg. '11.0'
        """

        # Create message
        self.create_empty_message()
        self.add_cmd_code('set_coolant_temp_setpoint')
        self.add_cmd_count()

        # Convert value to int
        value = int(float(value))

        # Get parameter
        param = dicts.PARAMETERS['coolant_temp_setpoint']

        self.outgoing_message[param['write']['byte_start']] = value

        # Add checksum and write message
        self.add_checksum()
        self.write()

        self.log("Coolant temp setpoint was set to %s.", value, level="INFO")

    def set_air_indoor_temp_control(self, value):
        """
        Set air indoor temperature control on and off.

        In:
         - value - string, eg. 'on' or 'off'
        """
        if value == 'off':
            # Need to send empty message with cmd_code
            self.create_empty_message()
            self.add_cmd_code('set_air_indoor_temp_control')
            self.add_cmd_count()

            self.add_checksum()
            self.write()
        elif value == 'on':
            # Need to set air indoor temp setpoint again ¯\_(ツ)_/¯
            self.set_air_indoor_temp_setpoint(self.state['air_indoor_temp_setpoint'])

        self.log("Air indoor temperature control was set to %s.", value, level="INFO")

    def reset_to_defaults(self, value):
        """
        Reset to defaults.

        TODO: Implement this.
        """

        self.log("WiFi module was reset to defaults.", level="INFO")

    """HELPERS"""

    @staticmethod
    def empty_input_buffer(sock):
        """
        Remove the data present on the socket.

        https://stackoverflow.com/questions/1097974/how-to-empty-a-socket-in-python
        """
        input_list = [sock]
        while True:
            input_ready, o, e = select.select(input_list, [], [], 0.0)
            if len(input_ready) == 0:
                break
            for s in input_ready:
                s.recv(1)

    @staticmethod
    def process_ingoing_message(message):
        """
        Process 192-byte packet and clean it by WiFi module`s developer rules.
        Returns: bytearray
        """

        # 1. Magic cleaning.
        # https://stackoverflow.com/questions/35372700/whats-0xff-for-in-cv2-waitkey1
        # Don`t think it`s needed.

        i = 64
        while i < 192:
            message[i] = message[i] & 0xff
            i = i + 1

        # 2. Recover temperatures.

        i = 128
        while i < 192:
            if message[i] == 127:
                message[i - 64] = message[i - 64] + 128
            i = i + 1

        return message

    @staticmethod
    def process_outgoing_message(message):
        """
        Process 192-byte packet and clean it by WiFi module`s developer rules.
        Returns: bytearray
        """

        # 1. Magic packing temperatures.

        i = 64
        while i < 128:
            if message[i] > 127:
                message[i] = message[i] & 0x7f
                message[i + 64] = 127
            else:
                message[i + 64] = 0
            i = i + 1

        return message

    @staticmethod
    def calculate_checksum(msg, size):
        """
        Calculate checksum.
        """
        checksum = 0

        while size != 0:
            checksum = checksum + (msg[size] * size)
            # print 'Size:', size
            size = size - 1

        checksum = checksum & 0xffffffff

        return checksum
