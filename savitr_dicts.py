# App to control the electric heater by Savitr with WiFi module.
#
# Variables and parameters.
#
# Version: 1.0.0.0
# Author: antonwantstosleep, 2020.
# License: MIT

HEATING_MODE = {
    0: {
        "name": "heating_off",
        "name_pretty": "Heating off",
        "description": "Turn off heating.",
    },
    1: {
        "name": "coolant_temp_constant",
        "name_pretty": "Coolant temperature - Constant",
        "description": "Maintain one target coolant temperature.",
    },
    2: {
        "name": "coolant_temp_daily_cycle",
        "name_pretty": "Coolant temperature - Daily cycle",
        "description": "Maintain two target coolant temperatures - for day and night.",
    },
    3: {
        "name": "coolant_temp_weekly_cycle",
        "name_pretty": "Coolant temperature - Weekly cycle",
        "description": "Maintain two target coolant temperatures - for day and night - for each day of the week.",
    },
    4: {
        "name": "coolant_temp_outdoor_air_temp",
        "name_pretty": "Coolant temperature - Outdoor air temperature",
        "description": "Calculate target coolant temperature internally from outdoor air sensor. "
                       "If there is a problem with outdoor air sensor the heater maintains min coolant temp setpoint.",
    },
    5: {
        "name": "remote",
        "name_pretty": "Remote",
        "description": "Remote control from WiFi or GSM module.",
    },
}

HEATER_STATUS = {
    0: {
        "name": "on",
        "name_pretty": "On",
        "description": "Heater is on and working.",
    },
    1: {
        "name": "off_standby",
        "name_pretty": "Off - Standby",
        "description": "Heater is off. Standby mode.",
    },
    2: {
        "name": "off_alarm_overheat",
        "name_pretty": "Off - Alarm - Overheat",
        "description": "Heater is off. Alarm. Overheat.",
    },
    3: {
        "name": "off_alarm_coolant_pressure_flow_sensor",
        "name_pretty": "Off - Alarm - Coolant pressure or flow sensor",
        "description": "Heater is off. Alarm. Check coolant pressure or flow sensor.",
    },
    4: {
        "name": "off_coolant_temp_no_setpoint",
        "name_pretty": "Off - No target coolant temperature setpoint",
        "description": "Heater is off. Target coolant temperature is not set.",
    },
    5: {
        "name": "off_indoor_air_temp_reached",
        "name_pretty": "Off - Indoor air temperature reached",
        "description": "Heater is off. Indoor air temperature is greater than threshold.",
    },
    6: {
        "name": "off_alarm_coolant_temp_sensor",
        "name_pretty": "Off - Alarm - Coolant temperature sensor",
        "description": "Heater is off. Alarm. Check coolant temperature sensor.",
    },
    7: {
        "name": "on_warning_indoor_air_temp_sensor",
        "name_pretty": "On - Warning - Indoor air temperature sensor",
        "description": "Heater is on. Check indoor air temperature sensor.",
    },
    8: {
        "name": "on_warning_outdoor_air_temp_sensor",
        "name_pretty": "On - Warning - Outdoor air sensor",
        "description": "Heater is on. Check outdoor air temperature sensor.",
    },
    9: {
        "name": "unknown_alarm_link",
        "name_pretty": "Unknown - Alarm - Link down",
        "description": "Heater status is unknown. Alarm. Check WiFi module and heater connection. "
                       "Additional status from WiFi module.",
    },
    10: {
        "name": "unknown_alarm_battery",
        "name_pretty": "Unknown - Alarm - Battery",
        "description": "Heater status is unknown. Alarm. Check WiFi module battery. "
                       "Additional status from WiFi module.",
    },
}

CLOCK_WEEKDAY = {
    1: {
        "name": "monday",
    },
    2: {
        "name": "tuesday",
    },
    3: {
        "name": "wednesday",
    },
    4: {
        "name": "thursday",
    },
    5: {
        "name": "friday",
    },
    6: {
        "name": "saturday",
    },
    7: {
        "name": "sunday",
    },
}

CMD = {
    "set_wifi": {
        "code": 17,
        "description": "Set WiFi SSID and password for WiFi module to connect."
                       "MainActivity$11",
    },
    "set_mail": {
        "code": 18,
        "description": "Set username and password for gmail.com or mail.ru SMTP "
                       "server to send mails from WiFi module."
                       "MainActivity$23",
    },
    "set_heating_mode": {
        "code": 20,
        "description": "Set heater working mode."
                       "MainActivity",
    },
    "set_heating_power": {
        "code": 21,
        "description": "Set heating power (elements quantity). 1, 2 or 3 heating elements (phases)."
                       "MainActivity$20",
    },
    "set_air_indoor_temp_min_max": {
        "code": 22,
        "description": "Set min and max indoor air temperature for alarms."
                       "MainActivity$14",
    },
    "set_coolant_temp_min_max": {
        "code": 23,
        "description": "Set min and max coolant temperature for alarms."
                       "MainActivity$15",
    },
    "set_air_indoor_temp_setpoint": {
        "code": 24,
        "description": "Set target indoor air temperature."
                       "MainActivity$2",
    },
    "reset_to_defaults": {
        "code": 25,
        "description": "Reset WiFi module to default settings."
                       "MainActivity$21",
    },
    "unimplemented_32": {
        "code": 32,
        "description": "Unimplemented: unknown cmd cmd_DEBUG."
                       "MainActivity$29, MainActivity",
    },
    "unimplemented_33": {
        "code": 33,
        "description": "Unimplemented: unknown cmd cmd_SVOFF."
                       "MainActivity",
    },
    "set_air_indoor_temp_control": {
        "code": 34,
        "description": "Set air indoor temperature control to off."
                       "MainActivity",
    },
    "set_coolant_temp_setpoint": {
        "code": 84,
        "description": "Set target coolant temperature."
                       "MainActivity$12",
    },
}

PARAMETERS = {

    "msg_preamble": {
        "default_value": "EZAP",
        "read": {
            "byte_start": 0,
            "byte_finish": 3,
        },
        "write": {
            "byte_start": 0,
            "byte_finish": 3,
            "byte_length": 4,
        },
        "type": "string",
        "description": "Message preamble.",
    },

    # Network
    "mac": {
        "default_value": None,
        "read": {
            "byte_start": 4,
            "byte_finish": 15,
        },
        "type": "string",
        "description": "Current WiFi module MAC address.",
        "hass_entity_type": "sensor",
    },
    "port": {
        "default_value": 8558,
        "read": {
            "byte_start": 31,
            "byte_finish": 34,
        },
        "type": "string",
        "description": "Current WiFi module TCP port.",
    },
    "wifi_ssid": {
        "default_value": "SAVITR_WIFI",
        "read": {
            "byte_start": 35,
            "byte_finish": 50,
        },
        "write": {
            "byte_start": 35,
            "byte_finish": 50,
            "byte_length": 15,
        },
        "type": "string",
        "description": "Current / target Wi-Fi net SSID to connect (max 15 symbols). Default: 'SAVITR_WIFI'.",
    },
    "wifi_ssid_length": {
        "default_value": 11,
        "read": {
            "byte_start": 51,
            "byte_finish": 51,
            "byte_order": "big",
        },
        "write": {
            "byte_start": 51,
            "byte_finish": 51,
            "byte_length": 1,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Current / target length of Wi-Fi net SSID to connect. Default: 11. Max: 15.",
    },
    "wifi_password": {
        "default_value": "",
        "read": {
            "byte_start": 52,
            "byte_finish": 59,
        },
        "write": {
            "byte_start": 52,
            "byte_finish": 59,
            "byte_length": 8,
        },
        "type": "string",
        "description": "Current / target password of Wi-Fi net to connect (max 8 symbols). Default: empty.",
    },

    "stat_preamble": {
        "default_value": "STAT",
        "read": {
            "byte_start": 60,
            "byte_finish": 63,
        },
        "type": "string",
        "description": "Status preamble.",
    },

    # Commands
    "cmd_count": {
        "read": {
            "byte_start": 64,
            "byte_finish": 64,
            "byte_order": "big",
        },
        "write": {
            "byte_start": 67,
            "byte_finish": 67,
            "byte_length": 1,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Counter of commands received by WiFi module. From 0 to 255.",
        "hass_entity_type": "sensor",
    },
    "cmd_code": {
        "read": {
            "byte_start": 65,
            "byte_finish": 65,
            "byte_order": "big",
        },
        "write": {
            "byte_start": 68,
            "byte_finish": 68,
            "byte_length": 1,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Last current / target command code.",
        "hass_entity_type": "sensor",
    },

    # Device state
    "power_supply_state": {
        "read": {
            "byte_start": 66,
            "byte_finish": 66,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Current heater power supply state. 85 is OK, others are NOT_OK.",
        "hass_entity_type": "sensor",
    },
    "power_supply_loss_time": {
        "read": {
            "byte_start": 68,
            "byte_finish": 69,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Current heater power supply loss time. Calculated by module if it has battery.",
        "hass_entity_type": "sensor",
    },
    "heating_mode": {
        "read": {
            "byte_start": 72,
            "byte_finish": 72,
            "byte_order": "big",
        },
        "write": {
            "byte_start": 70,
            "byte_finish": 70,
            "byte_length": 1,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Current / target heating mode.",
        "hass_entity_type": "input_select",
        "dictionary": HEATING_MODE,
    },
    "heater_status": {
        "read": {
            "byte_start": 75,
            "byte_finish": 75,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Current heater status. Errors and so on.",
        "hass_entity_type": "sensor",
        "dictionary": HEATER_STATUS,
    },
    "heating_power": {
        "read": {
            "byte_start": 78,
            "byte_finish": 78,
            "byte_order": "big",
        },
        "write": {
            "byte_start": 71,
            "byte_finish": 71,
            "byte_length": 1,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Current / target working heating elements quantity in %."
                       "33 - 1 element, 66 - 2 elements, 100 - 3 elements.",
        "hass_entity_type": "input_select",
    },
    "air_indoor_temp_control": {
        "read": {
            "byte_start": 107,
            "byte_finish": 108,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Air indoor temperature control. 0 (00) - off, 257 (11) - on.",
        "hass_entity_type": "input_boolean",
    },

    # OK - Current temperatures
    "coolant_temp": {
        "read": {
            "byte_start": 80,
            "byte_finish": 81,
            "byte_order": "big",
            "evaluate": "/10",
        },
        "type": "float",
        "description": "Current coolant temperature in °C.",
        "hass_entity_type": "sensor",
    },
    "air_indoor_temp": {
        "read": {
            "byte_start": 83,
            "byte_finish": 84,
            "byte_order": "big",
            "evaluate": "/10",
        },
        "type": "float",
        "description": "Current indoor air temperature in °C.",
        "hass_entity_type": "sensor",
    },
    "air_outdoor_temp": {
        "read": {
            "byte_start": 86,
            "byte_finish": 87,
            "byte_order": "big",
            "evaluate": "/10",
        },
        "type": "float",
        "description": "Current outdoor air temperature in °C.",
        "hass_entity_type": "sensor",
    },

    # Clock
    "clock_weekday": {
        "read": {
            "byte_start": 90,
            "byte_finish": 90,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Weekday from heater's clock.",
        "hass_entity_type": "sensor",
        "dictionary": CLOCK_WEEKDAY,
    },
    "clock_hours": {
        "read": {
            "byte_start": 93,
            "byte_finish": 93,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Hours from heater's clock.",
        "hass_entity_type": "sensor",
    },
    "clock_minutes": {
        "read": {
            "byte_start": 96,
            "byte_finish": 96,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Minutes from heater's clock.",
        "hass_entity_type": "sensor",
    },
    "clock_seconds": {
        "read": {
            "byte_start": 99,
            "byte_finish": 99,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Seconds from heater's clock.",
        "hass_entity_type": "sensor",
    },

    # OK - Setpoints
    "coolant_temp_setpoint": {
        "read": {
            "byte_start": 101,
            "byte_finish": 102,
            "byte_order": "big",
            "evaluate": "/10",
        },
        "write": {
            "byte_start": 69,
            "byte_finish": 69,
            "byte_length": 1,
            "byte_order": "big",
            "evaluate": "*10",
        },
        "type": "float",
        "description": "Current / Target coolant temperature setpoint in °C for 'COOLANT' mode."
                       "From 1.0 to 84.0 °C. Default: 60.0 °C.",
        "hass_entity_type": "input_number",
    },
    "air_indoor_temp_setpoint": {
        "read": {
            "byte_start": 104,
            "byte_finish": 105,
            "byte_order": "big",
            "evaluate": "/10",
        },
        "write": {
            "byte_start": 80,
            "byte_finish": 80,
            "byte_length": 1,
            "byte_order": "big",
            "evaluate": "*10",
        },
        "type": "float",
        "description": "Current / Target indoor air temperature setpoint in °C for 'AIR' mode."
                       "From 1.0 to 35.0 °C. Default: 20.0 °C.",
        "hass_entity_type": "input_number",
    },

    # Max and min values
    "coolant_temp_min": {
        "read": {
            "byte_start": 110,
            "byte_finish": 111,
            "byte_order": "little",
            "evaluate": "/10",
        },
        "write": {
            "byte_start": 76,
            "byte_finish": 77,
            "byte_length": 2,
            "byte_order": "little",
            "evaluate": "*10",
        },
        "type": "float",
        "description": "Current / Target min coolant temperature in °C."
                       "From 0.0 to 95.0 °C. Default: 5.0 °C.",
        "hass_entity_type": "input_number",
    },
    "coolant_temp_max": {
        "read": {
            "byte_start": 112,
            "byte_finish": 113,
            "byte_order": "little",
            "evaluate": "/10",
        },
        "write": {
            "byte_start": 78,
            "byte_finish": 79,
            "byte_length": 2,
            "byte_order": "little",
            "evaluate": "*10",
        },
        "type": "float",
        "description": "Current / Target max coolant temperature in °C."
                       "From 0.0 to 95.0 °C. Default: 90.0 °C.",
        "hass_entity_type": "input_number",
    },
    "air_indoor_temp_min": {
        "read": {
            "byte_start": 114,
            "byte_finish": 115,
            "byte_order": "little",
            "evaluate": "/10",
        },
        "write": {
            "byte_start": 72,
            "byte_finish": 73,
            "byte_length": 2,
            "byte_order": "little",
            "evaluate": "*10",
        },
        "type": "float",
        "description": "Current / Target min indoor air temperature in °C."
                       "From 0.0 to 95.0 °C. Default: 5.0 °C.",
        "hass_entity_type": "input_number",
    },
    "air_indoor_temp_max": {
        "read": {
            "byte_start": 116,
            "byte_finish": 117,
            "byte_order": "little",
            "evaluate": "/10",
        },
        "write": {
            "byte_start": 74,
            "byte_finish": 75,
            "byte_length": 2,
            "byte_order": "little",
            "evaluate": "*10",
        },
        "type": "float",
        "description": "Current / Target max indoor air temperature in °C."
                       "From 0.0 to 95.0 °C. Default: 35.0 °C.",
        "hass_entity_type": "input_number",
    },

    "checksum": {
        "default_value": 0,
        "read": {
            "byte_start": 124,
            "byte_finish": 125,
            "byte_order": "big",
        },
        "write": {
            "byte_start": 124,
            "byte_finish": 127,
            "byte_length": 4,
            "byte_order": "big",
        },
        "type": "int",
        "description": "Message checksum. Is calculated from 0 to 123 bytes.",
    },

}
