# Pinout

Diagrams: [project page](https://peterjburke.github.io/stackf765/#pinout). This file is generated from `gen/upper.py`, `gen/lower.py` and `gen/pinmap.py`.

TX and RX are named from the flight controller's side: connect a device's TX to an RX pin.

## Upper board, 3 x 12 header (J1)

Seen from above with the header pointing away from you. Column 1 is on the left.

| Row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C: front edge, lowest pins | G | 5V | TX6 | RX6 | G | 5V | TX7 | RX7 | G | 5V | TX8 | RX8 |
| B: middle | G | 4V5 | TX2 | RX2 | G | 5V | TX3 | RX3 | G | 5V | TX4 | RX4 |
| A: inner row, highest pins | G | 4V5 | TX1 | RX1 | SDA | SCL | G | 5V | CAM | G | 5V | VTX |

Looking into the pins from the front, the order is mirrored (column 12 on the left) and row A is on top.

| Label | Meaning |
|---|---|
| G | Ground |
| 5V | 5 V from the battery regulator (off on USB power) |
| 4V5 | 5 V that is also live on USB power |
| TXn / RXn | UART n (3.3 V logic). ArduPilot SERIAL1-7 = UART 1, 2, 3, 4, 6, 7, 8 |
| SDA / SCL | I2C bus for an external compass etc. (3.3 V, 2.2 k pull-ups fitted) |
| CAM | Analog video in from the camera |
| VTX | Analog video out to the transmitter, with OSD |

Suggested use (any UART can be given any role with `SERIALn_PROTOCOL`):

| Pins | Typical device |
|---|---|
| A1-A6: G 4V5 TX1 RX1 SDA SCL | GPS + compass module (6-wire) |
| B1-B4: G 4V5 TX2 RX2 | Radio receiver (CRSF / ELRS) |
| A7-A9, A10-A12 | Camera (G 5V CAM) and video transmitter (G 5V VTX) |
| other G 5V TX RX groups | Telemetry radio, ESC telemetry, VTX control, companion computer |

## Lower board, 2 x 10 header (J2)

Seen from above with the header pointing away from you.

| Row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| top row (signal) | M1 | M2 | M3 | M4 | M5 | M6 | LED | 5V | PI5V | PI5V |
| bottom row | G | G | G | G | G | G | G | G | G | G |

M1-M6: motor or servo outputs (PWM, OneShot, DShot). LED: addressable LED data (ArduPilot output 7). 5V: flight-controller 5 V rail. PI5V: separate 5 V / 3 A regulator for a companion computer.

## Lower board, power pads

Rear edge, seen from above: `BAT+  ESC+  ESC-  BAT-`. 2S-3S LiPo, 50 A continuous.

## Service cable (J5 on the upper board, J2 on the service board)

| Pin | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Signal | VBUS | D- | D+ | GND | BUZ | BOOT |

JST-SH 1.0 mm, wired pin 1 to pin 1.

## Microcontroller pins

| MCU pin | ArduPilot function | Net | Goes to |
|---|---|---|---|
| PA0 | TIM2_CH1 | M1 | lower header pin M1 |
| PA1 | TIM2_CH2 | M2 | lower header pin M2 |
| PA2 | TIM5_CH3 | M3 | lower header pin M3 |
| PA3 | TIM5_CH4 | M4 | lower header pin M4 |
| PA5 | SPI1_SCK | IMU_SCK | IMU (U2) |
| PA6 | SPI1_MISO | IMU_MISO | IMU (U2) |
| PA7 | SPI1_MOSI | IMU_MOSI | IMU (U2) |
| PA8 | TIM1_CH1 | LED_STRIP | lower header, LED pin |
| PA9 | USART1_TX | TX1 | upper header pin TX1 |
| PA10 | USART1_RX | RX1 | upper header pin RX1 |
| PA11 | OTG_FS_DM | USB_DM | service cable pin 2 |
| PA12 | OTG_FS_DP | USB_DP | service cable pin 3 |
| PA13 | JTMS-SWDIO | SWDIO | test pad TP4 |
| PA14 | JTCK-SWCLK | SWCLK | test pad TP5 |
| PB0 | TIM8_CH2N | M5 | lower header pin M5 |
| PB1 | TIM8_CH3N | M6 | lower header pin M6 |
| PB6 | I2C1_SCL | SCL | upper header pin SCL |
| PB7 | I2C1_SDA | SDA | upper header pin SDA |
| PB9 | TIM11_CH1 | BUZZER | buzzer switch Q1 |
| PB10 | I2C2_SCL | BARO_SCL | barometer (U3) |
| PB11 | I2C2_SDA | BARO_SDA | barometer (U3) |
| PB12 | MAX7456_CS | OSD_CS | OSD chip (U4) |
| PB13 | SPI2_SCK | OSD_SCK | OSD chip (U4) |
| PB14 | SPI2_MISO | OSD_MISO | OSD chip (U4) |
| PB15 | SPI2_MOSI | OSD_MOSI | OSD chip (U4) |
| PC2 | BATT_VOLTAGE_SENS | VBAT_ADC | battery voltage divider (lower board) |
| PC3 | BATT_CURRENT_SENS | CURR_ADC | current-sense amplifier (lower board) |
| PC4 | IMU1_CS | IMU_CS | IMU (U2) |
| PC5 | IMU1_INT | IMU_INT | IMU (U2) |
| PC6 | USART6_TX | TX6 | upper header pin TX6 |
| PC7 | USART6_RX | RX6 | upper header pin RX6 |
| PC8 | SDMMC_D0 | SD_D0 | microSD socket (J4) |
| PC9 | SDMMC_D1 | SD_D1 | microSD socket (J4) |
| PC10 | SDMMC_D2 | SD_D2 | microSD socket (J4) |
| PC11 | SDMMC_D3 | SD_D3 | microSD socket (J4) |
| PC12 | SDMMC_CK | SD_CK | microSD socket (J4) |
| PD0 | UART4_RX | RX4 | upper header pin RX4 |
| PD1 | UART4_TX | TX4 | upper header pin TX4 |
| PD2 | SDMMC_CMD | SD_CMD | microSD socket (J4) |
| PD5 | USART2_TX | TX2 | upper header pin TX2 |
| PD6 | USART2_RX | RX2 | upper header pin RX2 |
| PD8 | USART3_TX | TX3 | upper header pin TX3 |
| PD9 | USART3_RX | RX3 | upper header pin RX3 |
| PD10 | LED0 | LED_BLUE | blue LED |
| PD11 | LED1 | LED_GREEN | green LED |
| PE0 | UART8_RX | RX8 | upper header pin RX8 |
| PE1 | UART8_TX | TX8 | upper header pin TX8 |
| PE7 | UART7_RX | RX7 | upper header pin RX7 |
| PE8 | UART7_TX | TX7 | upper header pin TX7 |
