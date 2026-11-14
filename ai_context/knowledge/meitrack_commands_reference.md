# Meitrack Commands Reference Specification

## 1. Overview
Meitrack devices use 3-character ASCII command types sent within the standard envelope:
- Downlink (Server to Device): `@@<ID><Len>,<IMEI>,<CMD>,<Params>*<CS>\r\n`
- Uplink (Device to Server): `$$<ID><Len>,<IMEI>,<CMD>,<Params>*<CS>\r\n`

---

## 2. Command Index

| Command | Direction | Name | Function Summary | Supported Models |
|---|---|---|---|---|
| **AAA** | Uplink | Automatic Event Report | Periodic & alarm telemetry reporting | All |
| **A10** | Downlink/Uplink | Real-Time Location Query | On-demand position query (replies with AAA event 34) | All |
| **A11** | Downlink/Uplink | Set Heartbeat Interval | Keep-alive heartbeat interval during deep sleep | All |
| **A12** | Downlink/Uplink | Track By Time Interval | Periodic tracking interval (x10 seconds) | All |
| **A13** | Downlink/Uplink | Cornering Report Function | Heading change trigger threshold (1–359°) | All |
| **A14** | Downlink/Uplink | Tracking by Distance | Distance report interval (meters) | All |
| **A15** | Downlink/Uplink | Parking Scheduled Tracking | Periodic interval when engine is OFF | MVT100/340/380/600, T1, MVT800, T333, T3 |
| **A16** | Downlink/Uplink | Enable Parking Tracking | Enable/disable parking tracking mode | MVT100/340/380/600, T1, MVT800, T333, T3 |
| **A17** | Downlink/Uplink | RFID Output 1 Control | Immobilize/control output 1 via RFID swipe | MVT600, T1, T333, T3 |
| **A19** | Downlink/Uplink | 3D-Shake Wake Up | Wakeup on vibration in sleep mode | MT90 |
| **A21** | Downlink/Uplink | Set GPRS Parameters | Set mode (TCP/UDP), IP, Port, APN, User, Pass | All |
| **A22** | Downlink/Uplink | Set DNS Server IP | Primary DNS server IP address | All except T322X, T355 |
| **A23** | Downlink/Uplink | Set Standby Server | Backup IP and Port if primary fails | All except T322X |
| **A70** | Downlink/Uplink | Read Authorized Numbers | Retrieve 3 SOS numbers + 2 Listen-in numbers | All |
| **A71** | Downlink/Uplink | Set Authorized Numbers | Configure SOS phone numbers 1, 2, 3 | All |
| **A72** | Downlink/Uplink | Set Listen-in Numbers | Configure 2 silent voice monitor numbers | All except T322X, T355, MVT340 |
| **A73** | Downlink/Uplink | Set Smart Sleep Mode | Sleep modes: 0=Disabled, 1=Normal, 2=Deep | All |
| **AFF** | Downlink/Uplink | Clear GPRS Buffer | Delete cached GPRS events (UDP mode) | All except T322X |
| **B05** | Downlink/Uplink | Set Geo-Fence | Configure circular fence 1–8 | All |
| **B06** | Downlink/Uplink | Delete Geo-Fence | Remove fence 1–8 | All |
| **B07** | Downlink/Uplink | Set Speeding Alarm | Speed threshold in km/h | All |
| **B08** | Downlink/Uplink | Set Towing Alarm | Vibration duration threshold in seconds | All except T311, T355 |
| **B21** | Downlink/Uplink | Set Anti-Theft | Arm/disarm anti-theft security mode | MVT100/340/380/600, T1, TC68S, T333, T3, T355, T311 |
| **B31** | Downlink/Uplink | LED Indicator Control | Enable/disable device LED indicators | All except T322, T355 |
| **B34** | Downlink/Uplink | Set Log Interval | Local flash storage logging interval | All except T322X, MVT340, T355 |
| **B35** | Downlink/Uplink | Set SMS Time Zone | UTC offset for SMS timestamps | All |
| **B36** | Downlink/Uplink | Set GPRS Time Zone | UTC offset for GPRS reports | All except T355 |
| **B46** | Downlink/Uplink | SOS Snapshot Config | Configure photo count & upload on SOS | T333, MVT600, T1, T3 |
| **B60** | Downlink/Uplink | Engine Status Check | Determine running status by engine input | MVT100/340/380/600, T1, MVT800, T333, T3 |
| **B91** | Downlink/Uplink | Set SMS Event Chars | Custom SMS notification characters | All |
| **B92** | Downlink/Uplink | Set GPRS Event Flags | Bitmask of events reported over GPRS | All |
| **B93** | Downlink/Uplink | Read GPRS Event Flags | Read current GPRS event bitmask | All |
| **B96** | Downlink/Uplink | Set Photo Event Flag | Bitmask of events triggering camera snap | MVT600, T1, T333, T3 |
| **B97** | Downlink/Uplink | Read Photo Event Flag | Read photo event bitmask | MVT600, T1, T333 |
| **B99** | Downlink/Uplink | Event Authorization | Configure event authorizations | All |
| **C01** | Downlink/Uplink | Control Output Status | Control digital output lines (relays/buzzers)| MVT100/340/380/600, T1, MVT800, T333, T3 |
| **C02** | Downlink/Uplink | Trigger SMS Sending | Instruct device to send SMS | All |
| **C03** | Downlink/Uplink | GPRS Transmission Mode | Real-time vs cache vs batch transmission | All except T322, T355 |
| **C13** | Downlink/Uplink | LCD Message Display | Display text on connected cabin LCD | MVT600, T1, T333, T3 |
| **C40** | Downlink/Uplink | Register Temp Sensor | Pair 1-Wire temperature sensor SN to ID | T1, MVT600, MVT800, T333, T3 |
| **C41** | Downlink/Uplink | Delete Temp Sensor | Unpair temperature sensor | T1, MVT600, MVT800, T333, T3 |
| **C42** | Downlink/Uplink | Read Temp Sensor SN | Query sensor serial numbers | T1, MVT600, MVT800, T333, T3 |
| **C43** | Downlink/Uplink | Set Temp Alarm Limits | High/low temp alarm thresholds & names | T1, MVT600, MVT800, T333, T3 |
| **C44** | Downlink/Uplink | Read Temp Limits | Read temperature alarm parameters | T1, MVT600, MVT800, T333, T3 |
| **C46** | Downlink/Uplink | Check Temp Sensor | Real-time query of sensor readings | T1, MVT600, MVT800, T333, T3 |
| **C47** | Downlink/Uplink | Set Fuel Parameters | Fuel sensor type (R/C/V) and alarm levels | T1, MVT600, MVT800, T333, T3 |
| **C48** | Downlink/Uplink | Read Fuel Parameters | Read fuel sensor settings | T1, MVT600, MVT800, T333, T3 |
| **C49** | Downlink/Uplink | Set Fuel Theft Alarm | Fuel drop percentage and time window | T1, MVT600, MVT800, T333 |
| **C50** | Downlink/Uplink | Set Driver License Type| Authorize license card types (AMMVA) | T330G, T333 |
| **C51** | Downlink/Uplink | Set Reader Buzzer Time | Buzzer duration if unauthorized card swiped | T330G, T333 |
| **C52** | Downlink/Uplink | Valid Swipe Time Before ACC| Grace period for swiping card before ACC ON | T330G, T333 |
| **C91** | Downlink/Uplink | Serial Peripheral Config| Configure RS232/RS485 peripheral assignment| T333, T366, T366G |
| **D00** | Downlink/Uplink | File Download / Chunk | Download camera photos or logs chunk by chunk | MVT600, T1, T333, T3 |
| **D01** | Downlink/Uplink | File List Query | Retrieve list of stored photos/files | MVT600, T1, T333, T3 |
| **D02** | Downlink/Uplink | Delete Picture/File | Delete photo by name from memory card | MVT600, T1, T333, T3 |
| **D03** | Downlink/Uplink | Take Photo On Demand | Trigger camera snapshot immediately | MVT600, T1, T333, T3 |
| **D10** | Downlink/Uplink | Authorize RFID Card | Add RFID / iButton ID to whitelist | MVT600, T1, T333, T3 |
| **D11** | Downlink/Uplink | Batch Authorize RFID | Add sequence of RFID tags in bulk | MVT600, T1, T333, T3 |
| **D12** | Downlink/Uplink | Check RFID Authorized | Query whitelist authorization status | MVT600, T1, T333, T3 |
| **D13** | Downlink/Uplink | Read Authorized RFID | Dump whitelisted RFID cards | MVT600, T1, T333, T3 |
| **D14** | Downlink/Uplink | Delete Authorized RFID | Remove single RFID card from whitelist | MVT600, T1, T333, T3 |
| **D15** | Downlink/Uplink | Batch Delete RFID | Remove multiple RFID cards from whitelist | MVT600, T1, T333, T3 |
| **D16** | Downlink/Uplink | Checksum of RFID Whitelist | Compute XOR checksum of RFID whitelist | MVT600, T1, T333, T3 |
| **D65** | Downlink/Uplink | Set Maintenance Mileage| Schedule 8 service mileage trigger points | TC68S |
| **D66** | Downlink/Uplink | Set Maintenance Dates | Schedule 8 service days from 1990-01-01 | TC68S |
| **E91** | Downlink/Uplink | Read Firmware & SN | Query firmware version string & hardware SN| All |
| **FC0–FC7**| Both | OTA Firmware Update | Over-the-air firmware update suite | All |
| **F01** | Downlink/Uplink | Restart GSM Module | Soft restart cellular baseband | All |
| **F02** | Downlink/Uplink | Restart GPS Module | Soft restart GNSS receiver | All |
| **F08** | Downlink/Uplink | Set Mileage & Run Time | Override odometer (meters) and runtime (sec)| All |
| **F09** | Downlink/Uplink | Clear Cache Data | Clear SMS cache (1), GPRS cache (2), or both (3)| All |
| **F11** | Downlink/Uplink | Factory Reset | Reset configuration to initial defaults | All |

---

## 3. Core Command Deep Dives

### 3.1 `AAA` — Automatic Event Report (Telemetry Uplink)

The core telemetry packet transmitted by trackers on scheduled intervals or events.

#### Standard Field Order (Comma-separated within payload):
1. `command`: `AAA`
2. `event_code`: Numeric event code (e.g., `1`, `35`, `37`, `39`, `50`, `109`)
3. `latitude`: Latitude in decimal degrees `(-)yy.dddddd` (negative = South)
4. `longitude`: Longitude in decimal degrees `(-)xxx.dddddd` (negative = West)
5. `date_time`: UTC timestamp in `yymmddHHMMSS` format (e.g., `180701062919` = 2018-07-01 06:29:19 UTC)
6. `pos_status`: GPS lock status (`A` = Valid fix, `V` = Invalid / last known fix)
7. `num_sats`: Number of satellites in view (e.g., `8`)
8. `gsm_signal_strength`: Cellular RSSI value `0`–`31` (e.g., `15`)
9. `speed`: Ground speed in km/h (integer, e.g., `60`)
10. `direction`: Heading in degrees `0`–`359` (`0` = North)
11. `horizontal_accuracy` (HDOP): Dilution of precision `0.5`–`99.9` (smaller is more accurate)
12. `altitude`: Altitude above sea level in meters (integer)
13. `mileage`: Cumulative odometer reading in meters (uint32)
14. `run_time`: Cumulative runtime in seconds (uint32)
15. `base_station_info`: Cellular tower ID formatted as `MCC|MNC|LAC|CI` (MCC/MNC decimal, LAC/CI hex)
16. `io_port_status`: 16-bit hex string (4 characters, e.g., `0421`):
    - Bits 0–7: Output ports 1–8
    - Bits 8–15: Input ports 1–8
17. `analog_input_value`: 5 pipe-delimited hex channels: `AD1|AD2|AD3|AD4_Battery|AD5_ExtPower`
    - T333/T366 voltage formula: $\text{Voltage} = \text{hex\_val} / 100 \text{ V}$
18. `assisted_event_info` / Event-Specific Payload:
    - Normal report: Assisted trip / geo-fence stats.
    - Event 37: RFID serial number or AAMVA magnetic driver's license swipe text.
    - Event 39: Camera image filename (e.g. `180427100921_C1E1_N2U1D1.jpg`).
    - Event 50/51: Temperature sensor ID.
    - Event 109: Empty or reserved prefix followed by taxi meter record.
19. `customized_data`: Reserved vendor parameters.
20. `protocol_version`: Decimal protocol version (e.g. `1` or `108`).
21. `fuel_percentage`: 4 hex digits: high byte integer, low byte decimal (`241E` = 36.30%).
22. `temp_sensors`: Multi-sensor readings separated by `|`. Each 6 hex characters: `SSII.DD` (Sensor ID [2 hex], Integer temp [2 hex], Decimal temp [2 hex]).
23. `max_acceleration_value`: Peak acceleration reading.
24. `max_deceleration_value`: Peak deceleration reading.
25. Extended fields / taxi data (field 28 for event 109).

---

### 3.2 `A10` — Real-Time Location Query

- **Request (Downlink):**
  `@@Q25,353358017784062,A10*6A\r\n`
- **Reply (Uplink):**
  Sends an immediate `AAA` packet with Event Code `34` (Reply Current / Passive Query):
  `$$Q128,353358017784062,AAA,34,22.543176,114.078448,100313093738,A,5,22,2,205,5,-14,0,60,0|0|10133|4110,0000,149|153|173|2707|914,*91\r\n`

---

### 3.3 `A13` — Cornering Report Function

Triggers position reports when vehicle cornering/heading changes abruptly:
- **Request (Downlink):**
  `@@X29,353358017784062,A13,<Angle>*37\r\n`
  - `Angle`: `0` disables cornering report; `1`–`359` enables threshold angle (30° recommended).
- **Reply (Uplink):**
  `$$X28,353358017784062,A13,OK*05\r\n`
- **Trigger Report:**
  Device sends `AAA` with Event Code `32` (Cornering Report).

---

### 3.4 `C01` — Controlling Output Status (Relay / Immobilizer)

Controls digital outputs (e.g., fuel pump cut-off relay, buzzer):
- **Request (Downlink):**
  `@@b22,353358017784062,C01,<Speed>,<Out1><Out2><Out3><Out4><Out5>*BA\r\n`
  - `Speed`: Maximum vehicle speed (km/h) below which the output state is allowed to switch (safety protection).
  - Pin states: `0` = Inactive / OFF, `1` = Active / ON, `2` = Unchanged / Maintain.
- **Reply (Uplink):**
  `$$b28,353358017784062,C01,OK*..\r\n`

---

### 3.5 `E91` — Device Firmware Version & Hardware Serial Number

Queries tracker hardware identity:
- **Request (Downlink):**
  `@@W25,353358017784062,E91*7D\r\n`
- **Reply (Uplink):**
  `$$W38,353358017784062,E91,<FirmwareVersion>,<SerialNumber>*1C\r\n`
  Example:
  `$$W38,353358017784062,E91,T333_Y39H1412V137beta2_T,46281520253*..\r\n`

---

### 3.6 `D00`, `D01`, `D02` — Picture / File Management

Handles camera snapshot retrieval from tracker internal flash / SD card:
- **`D01` (List Pictures):**
  - Downlink: `@@A27,353358017784062,D01,<StartPacketNo>*BB\r\n`
  - Uplink: `$$A480,353358017784062,D01,<TotalPackets>,<CurrentPacketNo>,<File1>|<File2>|...*..\r\n`
- **`D00` (Download Picture Chunk):**
  - Downlink: `@@O48,353358017784062,D00,<FileName>,<StartPacketNo>*..\r\n`
  - Uplink: `$$n1084,353358017784062,D00,<FileName>,<TotalPackets>,<CurrentPacketNo>,<BinaryFileData>*..\r\n`
- **`D02` (Delete Picture):**
  - Downlink: `@@E110,353358017784062,D02,<FileName1>|<FileName2>|...*..\r\n`
  - Uplink: `$$F28,353358017784062,D02,OK*..\r\n`
