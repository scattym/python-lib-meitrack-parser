# Meitrack GPRS Protocol Specification

## 1. Overview
The Meitrack GPRS protocol is an ASCII-based and binary-hybrid telematics communication protocol used by Meitrack GPS trackers and telematic devices (e.g., T333, T366, T366G, MT90, MVT-series) to transmit tracking telemetry, alarms, device configuration, and peripheral data between devices and a central telematic server.

Communication can occur over TCP/IP or UDP. All multi-byte data adheres to network byte order (Big-Endian: high bytes prior to low bytes) unless explicitly specified otherwise by firmware extensions.

---

## 2. Packet Framing & Structure

Every Meitrack GPRS packet follows a strict envelope structure:

### 2.1 Packet Format

#### Server to Tracker (Downlink / Request)
```text
@@<Data Identifier><Data Length>,<IMEI>,<Command Type>,<Command Data><*Checksum>\r\n
```

#### Tracker to Server (Uplink / Response / Event Report)
```text
$$<Data Identifier><Data Length>,<IMEI>,<Command Type>,<Command Data><*Checksum>\r\n
```

### 2.2 Packet Fields Definition

| Field Name | Bytes / Length | Data Type | Description | Example |
|---|---|---|---|---|
| **Prefix / Header** | 2 bytes | ASCII (`@@` or `$$`) | `@@` (0x40 0x40) indicates server-to-device downlink.<br>`$$` (0x24 0x24) indicates device-to-server uplink. | `$$` |
| **Data Identifier** | 1 byte | ASCII (`A`-`z`, 0x41–0x7A) | Packet sequence / transaction identifier tag. Incremented or cycled per transmission. | `Q` |
| **Data Length** | Variable (2–4 digits) | Decimal ASCII | Length of characters measured from the first comma (`,`) immediately after the Data Length field up to and including the closing `\r\n`. | `128` |
| **First Comma** | 1 byte | ASCII (`,`, 0x2C) | Delimiter marking start of data length measurement. | `,` |
| **IMEI** | Typically 15 digits | Numeric ASCII string | Unique device identifier (IMEI) of the tracker. | `353358017784062` |
| **Command Delimiter**| 1 byte | ASCII (`,`, 0x2C) | Delimiter separating IMEI from Command Type. | `,` |
| **Command Type** | 3 bytes | Alphanumeric ASCII | 3-character command code (e.g., `AAA`, `A10`, `A13`, `D00`, `E91`, `FC0`). | `AAA` |
| **Command Payload** | Variable | ASCII / Raw Bytes | Arguments or telemetry fields for the command, typically comma-delimited. | `,1,22.540113,...` |
| **Checksum Delimiter**| 1 byte | ASCII (`*`, 0x2A) | Marks end of command payload and start of checksum. | `*` |
| **Checksum** | 2 bytes | Hex ASCII | 2-character uppercase hexadecimal representation of the 8-bit checksum. | `BE` |
| **Terminator** | 2 bytes | ASCII (`\r\n`, 0x0D 0x0A)| Carriage Return + Line Feed marking end of frame. | `\r\n` |

---

## 3. Data Length Calculation Rule

The `Data Length` field indicates the total count of bytes starting from the comma immediately following `<Data Length>` up to and including `\r\n`:

$$\text{Data Length} = \operatorname{len}(b"," + \text{IMEI} + b"," + \text{Command Payload} + b"*" + \text{Checksum} + b"\r\n")$$

### Maximum Permissible Length
- Standard protocol packets: ~160 to 256 bytes.
- File / picture transfer / OTA packets: Up to 1024–1408 bytes payload data.
- Absolute software protocol maximum: 2048 bytes (`MAX_DATA_LENGTH = 2048`).

---

## 4. Checksum Algorithm

The Meitrack protocol uses an **8-bit summation checksum** formatted as a 2-character hexadecimal string.

### 4.1 Checksum Rules
1. Sum all character bytes starting from the very first character of the packet (`@` or `$`) up to and including the asterisk (`*`) delimiter.
2. The checksum does **not** include the 2-digit checksum hex characters or the final `\r\n`.
3. Take the sum modulo 256 (`sum & 0xFF`).
4. Format the result as a 2-digit uppercase hexadecimal string (zero-padded, e.g., `0A`, `FD`, `BE`).

### 4.2 Mathematical Formula
$$\text{Checksum} = \left( \sum_{i=0}^{\text{index of '*'} } \text{byte}[i] \right) \pmod{256}$$

### 4.3 Reference Python Implementation
```python
def calc_checksum(payload: bytes) -> str:
    """
    Calculate Meitrack 2-byte hexadecimal checksum.
    Includes all bytes from the frame prefix up to and including '*'.
    """
    star_index = payload.rfind(b'*')
    if star_index == -1:
        raise ValueError("Payload missing '*' checksum separator")
    
    checksum_val = sum(payload[:star_index + 1]) & 0xFF
    return f"{checksum_val:02X}"
```

---

## 5. Packet Serialization & Framing Flow

### Inbound Parsing:
1. Scan buffer for prefix `@@` (downlink) or `$$` (uplink).
2. Extract Data Identifier (byte at index 2).
3. Locate first comma `,`. Data length digits sit between index 3 and the first comma index.
4. Parse `data_length` integer.
5. Slice frame of length `(first_comma_index + data_length)`.
6. Verify frame ends with `\r\n` (0x0D 0x0A).
7. Extract checksum characters between `*` and `\r\n`.
8. Verify computed checksum against extracted checksum.
9. Parse IMEI, Command Type, and Command Payload.

### Outbound Generation:
1. Construct body: `direction + identifier + [placeholder_length] + b',' + imei + b',' + payload + b'*'`.
2. Compute actual data length from `,` to `\r\n`.
3. Re-assemble string with valid length.
4. Calculate 8-bit checksum over all bytes up to `*`.
5. Append 2-char hex checksum + `\r\n`.
