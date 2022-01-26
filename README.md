# A library for parsing meitrack gprs protocol data

Tested with meitrack 4G GPS devices:
T333, T366, T366G

Should also work with:
Meitrack T711L
Meitrack T633L
Meitrack T622 Series
Meitrack T399 Series
Meitrack TS299L
Meitrack TC68L
Meitrack TC68SG

Example:
```
b'AAA,109,-33.815773,151.200181,180701062919,A,4,8,0,358,5.3,76,30202,425133,505|3|00FA|04E381F5,0400,0000|0000|0000|018D|0579,,,108,0000,,6,0,,0|0000|0000|0000|0000|0000,,,21|180622110810|180622110810|1000|60|010000|003000'
2022-01-26 14:33:19,546 - __main__ - Level 13 - Fields is b'109'
2022-01-26 14:33:19,546 - __main__ - Level 13 - Setting AAA fields for taxi data event payload
command b'AAA'
event_code b'109'
latitude b'-33.815773'
longitude b'151.200181'
date_time 2018-07-01 06:29:19
pos_status b'A'
num_sats b'4'
gsm_signal_strength b'8'
speed b'0'
direction b'358'
horizontal_accuracy b'5.3'
altitude b'76'
mileage b'30202'
run_time b'425133'
base_station_info b'505|3|00FA|04E381F5'
io_port_status b'0400'
analog_input_value b'0000|0000|0000|018D|0579'
customized_data b''
unknown_data b''
protocol_version b'108'
fuel_percentage b'0000'
temp_sensors b''
max_acceleration_value b'6'
max_deceleration_value b'0'
unknown_1 b''
unknown_2 b'0|0000|0000|0000|0000|0000'
unknown_3 b''
unknown_4 b''
taxi_meter_data b'21|180622110810|180622110810|1000|60|010000|003000'
```
