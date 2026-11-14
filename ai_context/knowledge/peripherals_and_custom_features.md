# Peripherals & Customized Firmware Features

## 1. Overview
Meitrack vehicle trackers (especially T333, T366, MVT600) support serial peripherals via RS-232 and RS-485 interfaces. This document details the specific peripheral protocols integrated with Meitrack devices found in firmware releases (e.g., firmware `T333_Y39V083_20180619` and related variants).

---

## 2. GWP Taxi Meter Protocol

### 2.1 Serial Interface Specification
- **Physical Layer:** RS-232 Asynchronous Serial
- **Baud Rate:** 115,200 bps
- **Data Bits:** 8
- **Stop Bits:** 1
- **Parity:** None (N)
- **Flow Control:** None (One-way transmission from Meter to Tracker)
- **Character Encoding:** ASCII for English characters, BIG5 for Chinese characters, null-padded.

### 2.2 Low-Level Meter Framing Format
```text
STX (0x02) | Command (1 byte) | Len (4 bytes) | Data (n bytes) | ETX (0x03) | DLE (0x10)
```

| Token | Hex Value | Description |
|---|---|---|
| `STX` | `0x02` | Start of Text |
| `Command` | 1 byte | Command opcode (`0xC1`, `0xC2`, `0xB4`) |
| `Len` | 4 bytes | Length of following data packet |
| `Data` | n bytes | Record attributes (little-endian uint16, uint32, float, char arrays) |
| `ETX` | `0x03` | End of Text |
| `DLE` | `0x10` | Data Link Escape (Transmission End) |

### 2.3 Taxi Meter Command Types
1. **`0xC1` — Vacancy Output (Last Trip Record):**
   Triggered after pressing the "VACANCY" button on the meter. Outputs the last occupation record every second.
2. **`0xC2` — Occupied Status Output:**
   Triggered after pressing the "OCCUPIED" button. Outputs real-time progress every second.
3. **`0xB4` — Print Trip Record:**
   Triggered when pressing the "PRINT" button. Outputs final receipt record for the completed trip.

### 2.4 Raw Meter Record Binary Layout (0xC1 / 0xB4)

| Byte Address | Attribute | Data Type | Units | Description |
|---|---|---|---|---|
| `00..03` | Date / Time | UInt32 | Unix Epoch | Current meter timestamp |
| `04..11` | Meter Serial Number | Char[8] | ASCII | Serial number of tracker/meter |
| `12..15` | Passenger On Board Time | UInt32 | Unix Epoch | Start time of passenger hire |
| `16..19` | Passenger Exit Time | UInt32 | Unix Epoch | End time of passenger hire |
| `20..23` | Travel Distance | UInt32 | Meters | Trip distance |
| `24..25` | Travel Time | UInt16 | Seconds | Difference between exit and hire times |
| `26..27` | Wait Time | UInt16 | Seconds | Total idling/waiting duration |
| `28..29` | Total Fare (16-bit) | UInt16 | Baht / Currency | Total trip fare |
| `30..31` | Instant Speed | UInt16 | km/h | Vehicle speed |
| `32..35` | On Board Longitude | Float | Degrees | Pickup longitude |
| `36..39` | On Board Latitude | Float | Degrees | Pickup latitude |
| `40..43` | Exit Longitude | Float | Degrees | Dropoff longitude |
| `44..47` | Exit Latitude | Float | Degrees | Dropoff latitude |
| `48..55` | Taxi Meter Device No. | Char[8] | ASCII | Hardware meter ID |
| `56..59` | Receipt No. | UInt32 | Count | Consecutive trip receipt number |
| `60..63` | Total Fare (32-bit) | UInt32 | Baht / Currency | Extended 32-bit positive integer fare |
| `64..79` | Driver Identification No.| Char[16] | ASCII | Driver license / badge ID |
| `80..83` | K-Constant | UInt32 | Pulses/km | Meter calibration constant |

---

### 2.5 Meitrack Formatted Taxi Meter Telemetry (Event 109)

When the taxi meter transmits data to the tracker over RS-232, the tracker packages the trip details into an `AAA` message with **Event Code 109**.

#### Payload Format:
```text
Assistedinfo|Startingtime|Endingtime|Distance|Fare|Triptime|Waitingtime
```

Example payload:
`01|171122124509|171122130748|48700|37500|002200|000200`

#### Field Definitions:
- **`Assistedinfo`** (1 byte hex):
  - Bit 0: Meter state:
    - `0`: Meter started (hire begins)
    - `1`: Meter stopped (trip ends)
  - Bit 4: Meter protocol type:
    - `0`: Type `G_TAX`
    - `1`: Type `3TM`
  *(Note: When meter is started, only Startingtime is populated; Endingtime and fare are empty or omitted).*
- **`Startingtime`**: 12 ASCII characters in `YYMMDDHHMMSS` format.
- **`Endingtime`**: 12 ASCII characters in `YYMMDDHHMMSS` format.
- **`Distance`**: Decimal integer in meters.
- **`Fare`**: Decimal integer in 1/100th unit of currency (e.g. cents / satang). `37500` = 375.00 Baht.
- **`Triptime`**: 6 ASCII characters in `HHMMSS` format (e.g., `002200` = 22 minutes).
- **`Waitingtime`**: 6 ASCII characters in `HHMMSS` format (e.g., `000200` = 2 minutes).

---

## 3. AAMVA Magnetic Driver's License Reader

Vehicle trackers with magnetic stripe readers enforce driver identification. When ACC turns ON, the reader's integrated buzzer sounds unless an authorized driver license card is swiped.

### 3.1 Raw Card Reader String Structure
```text
%  ^PROMSAKHA NA SAKONNAKAMOL$PROMPAN$.^?;6007643800600106231=150519870412=?#21            2            0000455  70100                     ?
```
1. **Track 1 (`% ... ?`):** Driver Name:
   - Delimited by `^...^?`
   - Format: `^SURNAME$GIVEN_NAMES$^?`
2. **Track 2 (`; ... ?`):** Driver ID & Expiry:
   - Contains card number, separator `=`, expiry date (`YYMM`), and DOB.
3. **Track 3 (`# ... ?`):** Card Type & Identification:
   - Prefix digits define the card type (`21` in example above).

### 3.2 Authorization & Buzzer Configuration Commands
- **`C50` — Authorize Driving License Type:**
  - Downlink: `C50,<Type1>,<Type2>,...,<Typen>` (values 0–65535, up to 16 types).
  - Uplink: `C50,OK`
  - Sending `C50` alone reads all authorized types.
- **`C51` — Buzzer Beep Duration:**
  - Downlink: `C51,<Minutes>` (0–255 min; 0 = continuous alarm; default 10 min).
  - Uplink: `C51,OK`
- **`C52` — Pre-Ignition Valid Swipe Window:**
  - Downlink: `C52,<Minutes>` (valid grace period for swiping before ACC is turned on; default 10 min).
  - Uplink: `C52,OK`

---

## 4. Camera Snapshot & Automated SOS Capture (`B46`)

Automates photo capture when alarms (such as SOS) occur.

### Command Syntax:
```text
B46,E,T,S,U,D
```
- **`E` (Event Code):** Event triggering camera snapshot (e.g. `1` for SOS button).
- **`T` (Interval):** Time interval between consecutive photos in seconds/minutes (`0`–`65535`).
- **`S` (Quantity):** Number of photos to take (`0`–`65535`).
- **`U` (Upload):** Automatically upload images over GPRS:
  - `0`: Yes (Upload)
  - `1`: No (Do not upload)
- **`D` (Delete):** Automatically delete images from device after upload:
  - `0`: Yes (Delete)
  - `1`: No (Keep on storage)

---

## 5. Serial Peripheral Assignment Configuration (`C91`)

Configures which peripheral hardware is attached to tracker serial ports (RS-232 / RS-485).

### Command Syntax:
```text
C91,X,Serial Y1:Peripheral K1,Serial Y2:Peripheral K2,...
```
- **`X` (Host Adapter Box):**
  - `PC`: Direct RS232 connection without multiplexer box.
  - `A78`: Multiplexer interface box A78.
  - `A84`: Multiplexer interface box A84.
- **`Yn` (Physical Serial Port ID):**
  - `1`: `RS232-EX1`
  - `2`: `RS232-EX2`
  - `3`: `RS232-EX3`
  - `4`: `RS485-EX1`
  - `5`: `RS485-EX2`
- **`Kn` (Peripheral Device Type ID):**
  - `0`: RS232 Camera
  - `1`: Handset
  - `2`: LED Screen
  - `3`: A21 Display
  - `4`: RFID Reader
  - `5`: Garmin PND Device
  - `6`: LLS Fuel Level Sensor
  - `8`: Ultrasonic Fuel/Distance Sensor
  - `9`: A78 Interface Box
  - `10`: A79 LED Screen
  - `11`: AMMVA Magnetic Card Reader
  - `13`: RS485 Camera
  - `15`: Wireless Temperature Sensor
  - `16`: A84 Interface Box
  - `17`: Meter GTAX (Taxi Meter)
  - `18`: Meter 3TM (Taxi Meter)
  - `19`: A86 LED Screen
  - `20`: Meter GWP (Taxi Meter)
