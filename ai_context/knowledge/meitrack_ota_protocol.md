# Meitrack Over-The-Air (OTA) Protocol Specification

## 1. Overview
The Meitrack Over-The-Air (OTA) protocol defines the command sequence and binary transport mechanism for updating tracker firmware wirelessly over GPRS/cellular connections.

Firmware update files have the extension `.OTA` and consist of:
1. OTA Header & Encryption Key
2. Firmware Binary Payload
3. Firmware Version String (located at offset `HexLen + 256` from the file start; must match the file name)

---

## 2. OTA Update Workflow & State Machine

The OTA update follows a strict two-stage sequential workflow:

```text
[Stage 1: Negotiation & Handshake on Main Server]
   1. Server queries Device Code:        FC5  -->  FC5,DeviceCode
   2. Server verifies Firmware Name:     FC6  -->  FC6,ACK (OK / 1 / 2)
   3. Server directs tracker to OTA IP:  FC7  -->  FC7,OK (or FC7,OTA heartbeat)

[Stage 2: Transfer on Dedicated OTA Server]
   4. Server/Tracker Authorizes OTA:     FC0  -->  FC0,DeviceCode,OK,PacketSize,FW,FileName
   5. Server pushes chunks in loop:      FC1  -->  FC1,AckIndex/AckLen/01
   6. Server verifies total checksum:    FC2  -->  FC2,Checksum
   7. Server issues start update command:FC3  -->  FC3,1 (entering update mode)
                                         Tracker reboots into bootloader & flashes
                                         FC3,2 (sent on reboot if success)
```

At any point during the process, sending **`FC4`** cancels the update immediately.
Commands must not be skipped. If a command is sent out of order, the tracker responds with:
`CMD,NOT` or `<CMD>,NOT`.

---

## 3. Command Specifications

### 3.1 `FC5` — Checking Device Code
- **Server -> Tracker:**
  `FC5`
- **Tracker -> Server:**
  `FC5,<DeviceCode>`
- **Description:**
  `DeviceCode`: 2 bytes in hexadecimal (e.g. `000A`). Identifies the tracker hardware model according to the Meitrack Product Code Table.
  Not restricted by OTA authorization timeouts.

---

### 3.2 `FC6` — Checking Firmware Version
- **Server -> Tracker:**
  `FC6,<OTAFileName>`
  - `OTAFileName`: ASCII string (max 32 chars), e.g. `T333_Y39V083.OTA`.
- **Tracker -> Server:**
  `FC6,<ACK>`
- **ACK Values:**
  - `OK`: Firmware file matches device hardware; proceed to next step.
  - `1`: Firmware version to update is identical to current device firmware.
  - `2`: Firmware file does NOT match tracker model (upgrade dangerous; device could brick).

---

### 3.3 `FC7` — Setting Dedicated OTA Server
- **Server -> Tracker:**
  `FC7,<IPAddress>,<Port>`
  - `IPAddress`: IPv4 address or domain name (max 32 bytes).
  - `Port`: Decimal port (up to 5 digits, e.g. `6100`).
- **Tracker -> Server:**
  - `FC7,OK`: Valid address received; device connects to specified OTA server.
  - `FC7,Err` or `FC7,FFFF`: Invalid IP/port syntax.
  - `FC7,OTA`: Uplink heartbeat reported by tracker while waiting on OTA server.

---

### 3.4 `FC0` — Authorizing OTA Update
- **Server -> Tracker:**
  `FC0,AUTH`
- **Tracker -> Server:**
  - Success: `FC0,<DeviceCode>,OK,<DataPacketSize>,<CurrentFirmware>,<OTAFileName>`
  - Failure: `FC0,<DeviceCode>,Err`
- **Parameters:**
  - `DataPacketSize`: Maximum chunk size supported by the tracker in decimal (at most 1408 bytes; typically 1024 bytes).
  - `CurrentFirmware`: Currently installed firmware string (same as returned by `E91`).
  - `OTAFileName`: Active OTA file name.
- **Timeout Rule:**
  If no subsequent OTA command is received within **30 minutes** after authorization, the device cancels authorization and will refuse commands until re-authorized by `FC0`.

---

### 3.5 `FC1` — Sending OTA Data Chunks
- **Server -> Tracker:**
  `FC1,<INDEX><DataLength><OTAData>`
  - `INDEX`: Byte offset of this chunk in the OTA binary; 4 bytes (hex / big-endian in binary).
  - `DataLength`: Length of OTA data bytes in this packet; 2 bytes (hex / big-endian).
  - `OTAData`: Raw binary firmware bytes (between 1 and 1024 bytes).
- **Tracker -> Server:**
  - Success: `FC1,<AckIndex><AckDataLength><Result>`
    - `Result`: `0x01` (success), `0x00` (failure).
  - Timeout / Unauthorized: `FC1,NOT`

---

### 3.6 `FC2` — Obtaining OTA Data Checksum
- **Server -> Tracker:**
  `FC2,<INDEX><DataLength>`
  - `INDEX`: Start offset in OTA file (4 bytes).
  - `DataLength`: Length of bytes to verify (4 bytes).
- **Tracker -> Server:**
  - `FC2,<OTAChecksum>`
    - `OTAChecksum`: 2-byte hexadecimal checksum computed by the device over the received bytes.
  - Timeout / Unauthorized: `FC2,NOT`

---

### 3.7 `FC3` — Starting the Firmware Flash
- **Server -> Tracker:**
  `FC3`
- **Tracker -> Server:**
  - `FC3,1`: Tracker received command and is restarting into bootloader to flash firmware.
  - `FC3,2`: Tracker successfully flashed firmware and powered back on (sent on first post-update boot).
  - `FC3,3`: Checksum / verification error; update aborted.
  - `FC3,NOT`: Unauthorized or session expired.

---

### 3.8 `FC4` — Canceling OTA Update
- **Server -> Tracker:**
  `FC4`
- **Tracker -> Server:**
  `FC4,OK`
- **Description:**
  Immediately cancels the OTA update process and restores normal tracking operations. Not restricted by authorization timeouts.

---

## 4. Implementation Findings & Critical Gotchas

### 4.1 Specification vs Codebase Endianness Difference
- **Official Specification Note:**
  In `MEITRACK_OTA_Protocol_V1.0--20160422.docx` (Section 2.6):
  `INDEX`: *4 bytes (little-endian); hexadecimal*
  `Data length`: *4 bytes (little-endian); hexadecimal*
  `OTA data checksum`: *2 bytes (little-endian); hexadecimal*
- **Existing Python Codebase Implementation:**
  In `meitrack/command/command_FC1.py` and `meitrack/command/command_FC2.py`:
  ```python
  # FC1:
  self.index.to_bytes(4, byteorder='big')
  len(file_contents).to_bytes(2, byteorder='big')

  # FC2:
  start_index.to_bytes(4, byteorder='big')
  length.to_bytes(4, byteorder='big')
  ```
  *Refactoring Directive:* During pipeline refactoring, maintain compatibility with the verified byte layout tested against production devices, and make endianness explicitly configurable.
