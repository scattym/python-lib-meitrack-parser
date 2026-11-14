# Meitrack Event Codes Specification

## 1. Overview
Meitrack devices communicate events (alarms, status notifications, periodic reports, peripheral triggers) through numeric event codes in the **`AAA`** (Automatic Event Report) command and query replies (e.g. `A10`).

Depending on tracker hardware models (e.g., T333 vs T366 vs MVT600), certain digital input lines map to different semantics (such as Ignition On/Off vs Door Open/Close).

---

## 2. Complete Event Code Catalog

| Event Code | Event Name | Default SMS Header | Description / Hardware Trigger |
|---|---|---|---|
| **1** | SOS Button Pressed | `SOS` | Emergency SOS panic button pressed (Input 1 active). |
| **2** | Input 2 Active | `In2 Active` / `Ignition On` / `Door Open` | **Ignition On**: MVT100, MVT340, T322X, T366, T366G.<br>**Door Open**: MVT380, MVT600, T1, MVT800, T333, T3.<br>**In2 Active**: Other models. |
| **3** | Input 3 Active | `In3 Active` / `Ignition On` / `Door Open` | **Ignition On**: MVT600, T1, T333, T3.<br>**Door Open**: MVT800, T322X.<br>**In3 Active**: Other models. |
| **4** | Input 4 Active | `In4 Active` / `Ignition On` | **Ignition On**: MVT380, MVT800.<br>**In4 Active**: Other models. |
| **5** | Input 5 Active | `In5 Active` | Digital Input 5 activated. |
| **9** | Input 1 Inactive | `In1 Inactive` / `SOS Released` | SOS emergency button released. |
| **10** | Input 2 Inactive | `In2 Inactive` / `Ignition Off` / `Door Close`| **Ignition Off**: MVT100, MVT340, T322X, T366, T366G.<br>**Door Close**: MVT380, MVT600, T1, MVT800, T333, T3.<br>**In2 Inactive**: Other models. |
| **11** | Input 3 Inactive | `In3 Inactive` / `Ignition Off` / `Door Close`| **Ignition Off**: MVT600, T1, T333, T3.<br>**Door Close**: MVT800, T322X.<br>**In3 Inactive**: Other models. |
| **12** | Input 4 Inactive | `In4 Inactive` / `Ignition Off` | **Ignition Off**: MVT380, MVT800.<br>**In4 Inactive**: Other models. |
| **13** | Input 5 Inactive | `In5 Inactive` | Digital Input 5 deactivated. |
| **17** | Low Battery | `Low Battery` | Internal backup battery voltage is low. |
| **18** | Low External Battery | `Low Ext-Battery` | Main external vehicle power voltage is low. |
| **19** | Speeding Alarm | `Speeding` | Vehicle speed exceeded configured threshold (`B07`). |
| **20** | Enter Geo-fence | `Enter Fence N` | Tracker entered Geo-fence $N$ ($N \in [1..8]$). |
| **21** | Exit Geo-fence | `Exit Fence N` | Tracker exited Geo-fence $N$ ($N \in [1..8]$). |
| **22** | External Battery On | `Ext-Battery On` | External vehicle power connected/restored (or tracker connected for TC68S). |
| **23** | External Battery Cut | `Ext-Battery Cut` | External vehicle power disconnected/cut (or tracker removed for TC68S). |
| **24** | GPS Signal Lost | `GPS Signal Lost` | GPS signal lock lost. |
| **25** | GPS Signal Recovery | `GPS Recovery` | GPS signal lock re-acquired. |
| **26** | Enter Sleep | `Enter Sleep` | Tracker entered sleep / low-power mode (`A73`). |
| **27** | Exit Sleep | `Exit Sleep` | Tracker woke up from sleep mode. |
| **28** | GPS Antenna Cut | `GPS Antenna Cut` | External GPS antenna disconnected or damaged. |
| **29** | Device Reboot | `Power On` | Device powered on or restarted. |
| **31** | Heartbeat | `/` | Periodic heartbeat packet while in sleep mode (`A11`). |
| **32** | Cornering Report | `Cornering` | Heading/bearing changed beyond configured angle (`A13`). |
| **33** | Track By Distance | `Distance` | Scheduled reporting interval reached by distance (`A14`). |
| **34** | Reply Current (Passive)| `Now` | Response to on-demand location query (`A10`). |
| **35** | Track By Time Interval | `Interval` | Scheduled reporting interval reached by time (`A12` / `A15`). |
| **36** | Tow Alarm | `Tow` | Vehicle moved or vibrated while parked (`B08`). |
| **37** | RFID / iButton / Card | `(only for GPRS)` | RFID card, iButton key, or Driver's License swipe detected. |
| **39** | Photo / Picture Report | `(only for GPRS)` | Photo captured and uploaded / notified (`B46` / `D03`). |
| **40** | Power Off | `Power Off` | Tracker explicitly powered off. |
| **41** | Stop Moving | `Stop moving` | Vehicle stopped moving (speed dropped to 0). |
| **42** | Start Moving | `Start Moving` | Vehicle began moving from standstill. |
| **44** | GSM Jamming | `GSM Jamming` | Cellular GSM jamming signal detected. |
| **50** | Temperature High | `Temp High` | Temperature exceeded high alarm threshold (`C43`). |
| **51** | Temperature Low | `Temp Low` | Temperature dropped below low alarm threshold (`C43`). |
| **52** | Full Fuel | `Full Fuel` | Fuel tank refilled to full threshold (`C47`). |
| **53** | Low Fuel | `Low Fuel` | Fuel level dropped below warning threshold (`C47`). |
| **54** | Fuel Theft | `Fuel Theft` | Rapid fuel decrease detected indicating fuel theft (`C49`). |
| **56** | Armed | `Armed` | Anti-theft / security mode activated (`B21`). |
| **57** | Disarmed | `Disarmed` | Anti-theft / security mode deactivated (`B21`). |
| **58** | Vehicle Theft | `Vehicle Theft` | Theft alarm triggered (door open or ignition while armed). |
| **63** | No GSM Jamming | `No GSM Jamming` | GSM jamming signal ceased. |
| **65** | Press Input 1 (SOS) Call| `/` | Call triggered by Input 1 (SOS). |
| **66** | Press Input 2 to Call | `/` | Call triggered by Input 2. |
| **67** | Press Input 3 to Call | `/` | Call triggered by Input 3. |
| **68** | Press Input 4 to Call | `/` | Call triggered by Input 4. |
| **69** | Press Input 5 to Call | `/` | Call triggered by Input 5. |
| **70** | Reject Incoming Call | `/` | Tracker rejected incoming voice call. |
| **71** | Get Location by Call | `/` | Tracker received call and sent location reply. |
| **72** | Auto Answer Incoming | `/` | Tracker auto-answered incoming voice call. |
| **73** | Listen-in (Voice Mon.) | `/` | Silent voice monitoring mode initiated (`A72`). |
| **79** | Fall Down Alarm | `Fall` | Fall sensor triggered (personal trackers like MT90). |
| **80** | Install Alarm | `Install` | Device installed / tamper sensor reset. |
| **81** | Drop Off Alarm | `Drop Off` | Device removed / dropped (tamper sensor triggered). |
| **109**| Taxi Meter Data | `Taxi Data` | GWP / 3TM / GTAX taxi meter trip or fare report. |
| **129**| Harsh Braking | `Harsh Braking` | Rapid deceleration threshold exceeded. |
| **130**| Harsh Acceleration | `Harsh Acceleration` | Rapid acceleration threshold exceeded. |
| **133**| Idle Overtime | `Idle Overtime` | Vehicle engine idling past allowable time (`D34`). |
| **134**| Idle Recovery | `Idle Recovery` | Vehicle resumed movement after idling. |
| **135**| Fatigue Driving | `Fatigue Driving` | Driver continuous driving duration exceeded threshold. |
| **136**| Rest After Fatigue | `Enough Rest` | Driver completed mandatory rest period. |
| **139**| Maintenance Notice | `Maintenance` | Maintenance mileage or service date reached (`D65`/`D66`). |
| **144**| Ignition On | `Ignition On` | Dedicated ignition-on telemetry event code. |
| **145**| Ignition Off | `Ignition Off` | Dedicated ignition-off telemetry event code (includes trip stats in assisted info). |

---

## 3. Model-Specific Hardware Input Mappings

Differences between device families are critical when interpreting digital inputs:

### 3.1 Ignition Detection Input Pin

| Device Family | Ignition Line | Ignition ON Event | Ignition OFF Event | Door Line | Door Open Event | Door Close Event |
|---|---|---|---|---|---|---|
| **T333, T1, MVT600, T3** | **Input 3** | Event `3` (or `144`) | Event `11` (or `145`) | Input 2 | Event `2` | Event `10` |
| **T366, T366G** | **Input 2** | Event `2` (or `144`) | Event `10` (or `145`) | Input 3 | Event `3` | Event `11` |
| **MVT100, MVT340, T322X** | **Input 2** | Event `2` | Event `10` | Input 3 | Event `3` | Event `11` |
| **MVT380** | **Input 4** | Event `4` | Event `12` | Input 2 | Event `2` | Event `10` |
| **MVT800** | **Input 4** | Event `4` | Event `12` | Input 3 | Event `3` | Event `11` |
| **TC68S / OBD** | Battery Voltage | Event `144` | Event `145` | N/A | N/A | N/A |
