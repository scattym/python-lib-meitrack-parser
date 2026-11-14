# Codebase Architecture & Core Dependencies Analysis

## 1. Overview
The codebase located at `<repo>` is a Python library named **`meitrackparser`** (version `2.11.dev0`), authored to parse, construct, and manage binary/ASCII telematics streams from Meitrack GPS tracking units.

### Package Metadata
- **Package Name:** `meitrackparser`
- **Current Version:** `2.11.dev0`
- **Target Devices:** Meitrack 4G/3G/2G GPS Trackers (T333, T366, T366G primary; also compatible with T711L, T633L, T622, T399, TS299L, TC68L, TC68SG).
- **Primary Script:** `scripts/mtparse` (CLI parsing utility for standard input streams).

---

## 2. Dependencies & Environment Requirements

### 2.1 Core Runtime Dependencies (`requirements.txt`, `setup.py`)
- **`licenseparser`**: Proprietary / external library providing AAMVA driver license magnetic stripe parsing via:
  ```python
  from license.cardreader import License
  ```
  *(Used in `meitrack/command/common.py` within `Command.get_license_data()`)*.
- **Python Standard Library:**
  - `datetime` (UTC conversion, parsing `yymmddHHMMSS`)
  - `binascii` (hexadecimal encode/decode, `unhexlify`, `hexlify`)
  - `logging`
  - `functools.singledispatch`
  - `copy.deepcopy`

### 2.2 Test & Linting Dependencies (`test-requirements.txt`)
- `pytest`
- `pytest-cov`
- `pytest-pylint`
- `pylint`

---

## 3. Module Hierarchy & Architecture

```text
meitrack/
├── __init__.py                 # Package root
├── common.py                   # Global constants (@@, $$, \r\n, MAX_DATA_LENGTH), helpers (s2b, b2s)
├── devices.py                  # Dictionary of known device names: T333 (0), T366G (1), T366 (2)
├── error.py                    # Exception hierarchy: GPRSError -> GPRSParseError, GPRSParameterError
├── gprs_protocol.py            # Primary packet framer: GPRS class, parse_data_payload, calc_signature
├── build_message.py            # Factory functions for building downlink (STC) & uplink (CTS) frames
├── file_download.py            # Chunk reassembly: FileDownload, FileDownloadAggregator
├── file_list.py                # Multi-packet file listing aggregator: FileListing, FileListingError
├── firmware_update.py          # OTA state machine: FirmwareUpdate (stage1, stage2)
├── event.py                    # Event mapping helpers (EVENT dictionary, event_id_to_name)
└── command/                    # Command-specific parsers and models
    ├── __init__.py             # Exports command factory functions
    ├── common.py               # Base Command class, TaxiMeterData, pin decoders, date converters
    ├── command_to_object.py    # Dispatch table COMMAND_LIST and factory command_to_object()
    ├── command_AAA.py          # Automatic Event Report (TrackerCommand) with variant field layouts
    ├── command_A10.py          # Real-time Location Query stub
    ├── command_A13.py          # SetCorneringCommand
    ├── command_C91.py          # SetIOParamsCommand (Serial peripheral configuration)
    ├── command_D00.py          # FileDownloadCommand (Photo/file chunk transfer)
    ├── command_D01.py          # FileListCommand (Directory listing)
    ├── command_E91.py          # RequestDeviceInfoCommand (Firmware version & SN)
    ├── command_FC0.py          # AuthOtaUpdateCommand
    ├── command_FC1.py          # SendOtaDataCommand
    ├── command_FC2.py          # ObtainOtaChecksumCommand
    ├── command_FC3.py          # StartOtaUpdateCommand
    ├── command_FC4.py          # CancelOtaUpdateCommand
    ├── command_FC5.py          # CheckDeviceCodeCommand
    ├── command_FC6.py          # CheckFirmwareVersionCommand
    ├── command_FC7.py          # SetOtaServerCommand
    └── event.py                # Device-specific event maps (EVENT_MAP_T333, EVENT_MAP_T366, EVENT_MAP_T366G)
```

---

## 4. Data Processing Pipelines

### 4.1 Inbound Parsing Pipeline (Raw Bytes -> Command Object)
1. **Raw Byte Ingestion:** `parse_data_payload(payload, direction, device_type)` in `meitrack/gprs_protocol.py`.
2. **Framing & Length Extraction:**
   - Detects `@@` or `$$`.
   - Reads Data Length between byte index 3 and the first comma.
   - Slices message from start to `(first_comma + data_length)`.
   - Validates trailing `\r\n`.
3. **Envelope Unpacking:**
   - Instantiates `GPRS(message, device_type)`.
   - Extracts `data_identifier`, `imei`, `command_type`, and `checksum`.
4. **Command Polymorphism (`command_to_object.py`):**
   - Looks up `command_type` in `COMMAND_LIST`.
   - If specialized class exists (e.g. `TrackerCommand` for `AAA`), instantiates it with command payload.
   - For `AAA`: dynamically adapts field selectors based on `event_code`:
     - Events `50`, `51` -> `field_names_50_51` (includes `temperature_sensor_number`)
     - Event `37` -> `field_names_37` (includes `rfid`)
     - Event `39` -> `field_names_39` (includes `file_name`)
     - Event `109` -> `field_names_109` (includes `taxi_meter_data`)
     - Default -> `field_names` (includes `assisted_event_info`)

### 4.2 Outbound Construction Pipeline (Object -> Network Bytes)
1. **Command Generation:** Factory in `build_message.py` creates specific `Command` object.
2. **Envelope Attachment:** Wraps command in `GPRS` object, assigning `imei`, `direction`, and sequence counter.
3. **Length Calculation:** `GPRS.data_length` computes exact byte length from first comma to `\r\n`.
4. **Signature Calculation:** `calc_signature(string_to_sign)` sums all character bytes up to `*`, masked with `& 0xFF`.
5. **Byte Formatting:** Formats `*<XX>\r\n` and outputs complete byte string.

---

## 5. Technical Debt, Bugs & Refactoring Opportunities

During our thorough audit of the codebase against official protocol specifications, several key defects and technical debt items were identified:

### 5.1 Hardcoded Values / Serious Bugs
1. **Hardcoded Analogue Input in `Command.get_analogue_pin_states()` (`meitrack/command/common.py:422`):**
   ```python
   # CURRENT CODE (BUG):
   if self.field_dict.get("analog_input_value"):
       return meitrack_analogue_pins_to_dict(b"0000|0000|0000|018D|0579")  # HARDCODED!
   ```
   The method ignores `self.field_dict["analog_input_value"]` and passes a hardcoded sample string!
2. **Missing Implementation in `command_A10.py`:**
   `command_A10.py` is only a docstring (3 lines) and has no class implementation, while `COMMAND_LIST` maps `b"A10"` to `class: None`.
3. **Empty / Stubbed Modules:**
   - `meitrack/__init__.py`: Completely empty (0 bytes).
   - `meitrack/fromdevice.py`: Unused stub (10 lines).
   - `meitrack/stub_processor.py`: Incomplete placeholder.
   - In `command_to_object.py`: Over 40 commands (A11, A12, A14-A73, B05-B99, C01-C49, D10-D16, F01-F11) have `"class": None`, defaulting to generic `Command`.

### 5.2 Endianness Inconsistency in OTA Protocol
- Official specification (`MEITRACK_OTA_Protocol_V1.0`) states that `INDEX`, `Data length`, and `OTA data checksum` in `FC2` are **little-endian**.
- Codebase implements them as **big-endian** (`to_bytes(4, byteorder='big')`).

### 5.3 Type Annotations & Python 3 Modernization
- The codebase uses legacy Python 2/3 compatibility shims (`s2b`, `b2s`, raw string manipulation, `.decode()`, `.encode()`).
- No modern Python type annotations (`typing`, `dataclasses`, `Pydantic` or `Enum`).
- Test suite files are missing in the repo (`repo/` has `test-requirements.txt` and `unittest.cfg`, but no `tests/` directory).
