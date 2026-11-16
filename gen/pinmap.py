"""STM32F765VIT6 pin assignment: single table used by the schematic generator
and by tools/check_hwdef.py (which compares it with the ArduPilot hwdef.dat).

MCU pin -> (net name on the upper board, ArduPilot hwdef function label)
"""
PINMAP = {
    # USB + debug
    "PA11": ("USB_DM", "OTG_FS_DM"),
    "PA12": ("USB_DP", "OTG_FS_DP"),
    "PA13": ("SWDIO", "JTMS-SWDIO"),
    "PA14": ("SWCLK", "JTCK-SWCLK"),
    # UARTs (header labels TXn / RXn)
    "PA9":  ("TX1", "USART1_TX"), "PA10": ("RX1", "USART1_RX"),
    "PD5":  ("TX2", "USART2_TX"), "PD6":  ("RX2", "USART2_RX"),
    "PD8":  ("TX3", "USART3_TX"), "PD9":  ("RX3", "USART3_RX"),
    "PD1":  ("TX4", "UART4_TX"),  "PD0":  ("RX4", "UART4_RX"),
    "PC6":  ("TX6", "USART6_TX"), "PC7":  ("RX6", "USART6_RX"),
    "PE8":  ("TX7", "UART7_TX"),  "PE7":  ("RX7", "UART7_RX"),
    "PE1":  ("TX8", "UART8_TX"),  "PE0":  ("RX8", "UART8_RX"),
    # SPI1 - IMU
    "PA5": ("IMU_SCK", "SPI1_SCK"), "PA6": ("IMU_MISO", "SPI1_MISO"), "PA7": ("IMU_MOSI", "SPI1_MOSI"),
    "PC4": ("IMU_CS", "IMU1_CS"), "PC5": ("IMU_INT", "IMU1_INT"),
    # SPI2 - OSD
    "PB13": ("OSD_SCK", "SPI2_SCK"), "PB14": ("OSD_MISO", "SPI2_MISO"), "PB15": ("OSD_MOSI", "SPI2_MOSI"),
    "PB12": ("OSD_CS", "MAX7456_CS"),
    # I2C
    "PB6": ("SCL", "I2C1_SCL"), "PB7": ("SDA", "I2C1_SDA"),
    "PB10": ("BARO_SCL", "I2C2_SCL"), "PB11": ("BARO_SDA", "I2C2_SDA"),
    # analog
    "PC2": ("VBAT_ADC", "BATT_VOLTAGE_SENS"), "PC3": ("CURR_ADC", "BATT_CURRENT_SENS"),
    # LEDs, buzzer
    "PD10": ("LED_BLUE", "LED0"), "PD11": ("LED_GREEN", "LED1"),
    "PB9": ("BUZZER", "TIM11_CH1"),
    # outputs
    "PA0": ("M1", "TIM2_CH1"), "PA1": ("M2", "TIM2_CH2"), "PA2": ("M3", "TIM5_CH3"), "PA3": ("M4", "TIM5_CH4"),
    "PB0": ("M5", "TIM8_CH2N"), "PB1": ("M6", "TIM8_CH3N"),
    "PA8": ("LED_STRIP", "TIM1_CH1"),
    # microSD
    "PC8": ("SD_D0", "SDMMC_D0"), "PC9": ("SD_D1", "SDMMC_D1"), "PC10": ("SD_D2", "SDMMC_D2"),
    "PC11": ("SD_D3", "SDMMC_D3"), "PC12": ("SD_CK", "SDMMC_CK"), "PD2": ("SD_CMD", "SDMMC_CMD"),
}
