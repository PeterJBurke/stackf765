"""Part catalogue: every component used on the three boards, with manufacturer
part number and LCSC/JLCPCB order code.  Sources and stock notes: research/parts.md
"""
from kigen.design import box

# ---------------------------------------------------------------- passives
# (kind, value, size) -> (LCSC, MPN, manufacturer, description, unit price USD)
_PASSIVES = {
    ("C", "100n", "0402"): ("C1525", "CL05B104KO5NNNC", "Samsung", "100 nF 16 V X7R", 0.002),
    ("C", "100n 50V", "0402"): ("C307331", "CL05B104KB54PNC", "Samsung", "100 nF 50 V X7R", 0.004),
    ("C", "10n", "0402"): ("C15195", "CL05B103KB5NNNC", "Samsung", "10 nF 50 V X7R", 0.002),
    ("C", "33n", "0402"): ("C1532", "CL05B333KO5NNNC", "Samsung", "33 nF 16 V X7R", 0.003),
    ("C", "15p", "0402"): ("C1548", "0402CG150J500NT", "FH", "15 pF 50 V C0G", 0.002),
    ("C", "1u", "0402"): ("C52923", "CL05A105KA5NQNC", "Samsung", "1 uF 25 V X5R", 0.004),
    ("C", "2.2u", "0402"): ("C12530", "CL05A225MQ5NSNC", "Samsung", "2.2 uF 6.3 V X5R", 0.005),
    ("C", "4.7u", "0603"): ("C19666", "CL10A475KO8NNNC", "Samsung", "4.7 uF 16 V X5R", 0.008),
    ("C", "10u", "0603"): ("C96446", "CL10A106MA8NRNC", "Samsung", "10 uF 25 V X5R", 0.012),
    ("C", "10u", "0805"): ("C15850", "CL21A106KAYNNNE", "Samsung", "10 uF 25 V X5R", 0.015),
    ("C", "22u", "0805"): ("C45783", "CL21A226MAQNNNE", "Samsung", "22 uF 25 V X5R", 0.03),
    ("C", "22u", "1206"): ("C12891", "CL31A226KAHNNNE", "Samsung", "22 uF 25 V X5R", 0.04),
    ("R", "0R", "0402"): ("C17168", "0402WGF0000TCE", "UNI-ROYAL", "0 ohm jumper", 0.001),
    ("R", "10R", "0402"): ("C25077", "0402WGF100JTCE", "UNI-ROYAL", "10 ohm 1%", 0.001),
    ("R", "22R", "0402"): ("C25092", "0402WGF220JTCE", "UNI-ROYAL", "22 ohm 1%", 0.001),
    ("R", "75R", "0402"): ("C25133", "0402WGF750JTCE", "UNI-ROYAL", "75 ohm 1%", 0.001),
    ("R", "100R", "0402"): ("C25076", "0402WGF1000TCE", "UNI-ROYAL", "100 ohm 1%", 0.001),
    ("R", "470R", "0402"): ("C25117", "0402WGF4700TCE", "UNI-ROYAL", "470 ohm 1%", 0.001),
    ("R", "1k", "0402"): ("C11702", "0402WGF1001TCE", "UNI-ROYAL", "1 k 1%", 0.001),
    ("R", "2.2k", "0402"): ("C25879", "0402WGF2201TCE", "UNI-ROYAL", "2.2 k 1%", 0.001),
    ("R", "4.7k", "0402"): ("C25900", "0402WGF4701TCE", "UNI-ROYAL", "4.7 k 1%", 0.001),
    ("R", "5.1k", "0402"): ("C25905", "0402WGF5101TCE", "UNI-ROYAL", "5.1 k 1%", 0.001),
    ("R", "10k", "0402"): ("C25744", "0402WGF1002TCE", "UNI-ROYAL", "10 k 1%", 0.001),
    ("R", "51k", "0402"): ("C25794", "0402WGF5102TCE", "UNI-ROYAL", "51 k 1%", 0.001),
    ("R", "100k", "0402"): ("C25741", "0402WGF1003TCE", "UNI-ROYAL", "100 k 1%", 0.001),
    ("R", "4.7R", "0805"): ("C2933459", "FRC0805F4R70TS", "FOJAN", "4.7 ohm 1% 1/8 W", 0.005),
    ("R", "10R", "1206"): ("C42460620", "MFCR1206F10R0QHR", "(high-power thick film)", "10 ohm 1% 1 W, 1206", 0.09),
}


def passive(kind, value, size):
    try:
        lcsc, mpn, mfr, descr, price = _PASSIVES[(kind, value, size)]
    except KeyError:
        raise SystemExit(f"parts.py: no catalogue entry for {kind} {value} {size}")
    return dict(LCSC=lcsc, MPN=mpn, Manufacturer=mfr, Description=descr, Price=price)


# ---------------------------------------------------------------- symbols drawn here
def _sot583_buck():
    return box("TPS62933", left=[(3, "VIN", "power_in"), (2, "EN", "input"), (1, "RT", "passive"), (7, "SS", "passive")],
               right=[(6, "BST", "passive"), (5, "SW", "power_out"), (8, "FB", "input"), (4, "GND", "power_in")])


def _ina214():
    return box("INA214", left=[(4, "IN+", "input"), (5, "IN-", "input"), (1, "REF", "input")],
               right=[(3, "V+", "power_in"), (6, "OUT", "output"), (2, "GND", "power_in")])


def _ldo():
    return box("LDO_SOT23-5", left=[(1, "IN", "power_in"), (3, "EN", "input")],
               right=[(5, "OUT", "power_out"), (4, "NC", "no_connect"), (2, "GND", "power_in")])


def _lm66200():
    return box("LM66200", left=[(3, "VIN1", "power_in"), (6, "VIN2", "power_in"), (4, "~{ON}", "input")],
               right=[(2, "VOUT", "power_out"), (7, "VOUT", "passive"), (8, "ST", "output"), (1, "GND", "power_in"),
                      (5, "GND", "power_in")], width=17.78)


def _icm42688():
    return box("ICM-45686", left=[(13, "SCLK", "input"), (14, "SDI", "input"), (1, "SDO", "output"), (12, "CS", "input"),
                                   (4, "INT1", "output"), (9, "INT2/FSYNC", "passive")],
               right=[(8, "VDD", "power_in"), (5, "VDDIO", "power_in"), (2, "RESV2", "no_connect"),
                      (3, "RESV3", "no_connect"), (10, "RESV10", "no_connect"), (11, "RESV11", "no_connect"),
                      (7, "RESV7", "passive"), (6, "GND", "power_in")])


def _bmp388():
    return box("BMP388", left=[(2, "SCK", "input"), (4, "SDI", "bidirectional"), (5, "SDO", "passive"),
                               (6, "CSB", "input"), (7, "INT", "output")],
               right=[(10, "VDD", "power_in"), (1, "VDDIO", "power_in"), (3, "VSS", "power_in"), (8, "VSS", "power_in"),
                      (9, "VSS", "power_in")])


def _at7456e():
    return box("AT7456E", left=[(8, "~{CS}", "input"), (9, "SDIN", "input"), (10, "SCLK", "input"), (11, "SDOUT", "output"),
                               (19, "~{RESET}", "input"), None, (5, "CLKIN", "passive"), (6, "XFB", "passive"),
                               (7, "CLKOUT", "output"), None, (12, "LOS", "open_collector"),
                               (17, "~{VSYNC}", "open_collector"), (18, "~{HSYNC}", "open_collector"),
                               (13, "SYNC_IN", "passive")],
               right=[(3, "DVDD", "power_in"), (21, "AVDD", "power_in"), (24, "PVDD", "power_in"), None,
                      (22, "VIN", "input"), (26, "VOUT", "output"), (25, "SAG", "input"), None,
                      (4, "DGND", "power_in"), (20, "AGND", "power_in"), (23, "PGND", "power_in"),
                      (29, "EP", "power_in")], width=25.4)


def _nc_pins(sym_fn, pins):
    return sym_fn


# ---------------------------------------------------------------- catalogue
PARTS = {
    # --- power board
    "buck": dict(symbol=_sot583_buck, footprint="Package_TO_SOT_SMD:SOT-583-8", value="TPS62933DRLR",
                 MPN="TPS62933DRLR", Manufacturer="Texas Instruments", LCSC="C3200405", Price=0.53,
                 Description="3.8-30 V 3 A synchronous buck, 500 kHz, SOT-583",
                 Datasheet="https://www.ti.com/lit/ds/symlink/tps62933.pdf"),
    "inductor": dict(symbol="Device:L", footprint="fc:L_SXN_SMMS0530", value="4.7uH 5A",
                     MPN="SMMS0530-4R7M", Manufacturer="SXN (Shun Xiang Nuo)", LCSC="C181722", Price=0.11,
                     Description="4.7 uH shielded moulded inductor, Isat 5 A, 50 mohm, 5.5x5.2x3.0 mm",
                     Datasheet="https://www.lcsc.com/datasheet/C181722.pdf"),
    "ina": dict(symbol=_ina214, footprint="Package_TO_SOT_SMD:SOT-363_SC-70-6", value="INA214AIDCKR",
                MPN="INA214AIDCKR", Manufacturer="Texas Instruments", LCSC="C105240", Price=0.86,
                Description="Zero-drift current-sense amplifier, gain 100 V/V, SC-70-6",
                Datasheet="https://www.ti.com/lit/ds/symlink/ina214.pdf"),
    "shunt": dict(symbol="Device:R", footprint="fc:R_Shunt_2512_ASR-M-3", value="0.5mR 1% 6W",
                  MPN="ASR-M-3-0.5F", Manufacturer="Yezhan", LCSC="C469426", Price=0.28,
                  Description="0.5 mohm 1% 6 W metal-strip current shunt, 2512",
                  Datasheet="https://www.lcsc.com/datasheet/C469426.pdf"),
    "tvs": dict(symbol="Device:D_TVS", footprint="Diode_SMD:D_SMB", value="SMBJ15CA",
                MPN="SMBJ15CA", Manufacturer="various", LCSC="C211759", Price=0.065,
                Description="600 W bidirectional TVS, 15 V stand-off, 24.4 V clamp, SMB",
                Datasheet="https://www.lcsc.com/datasheet/C211759.pdf"),
    "tvs5": dict(symbol="Device:D_TVS", footprint="Diode_SMD:D_SOD-123F", value="SMF5.0CA",
                 MPN="SMF5.0CA-TP", Manufacturer="MCC", LCSC="C914432", Price=0.053,
                 Description="200 W bidirectional TVS, 5 V stand-off, SOD-123FL",
                 Datasheet="https://www.lcsc.com/datasheet/C914432.pdf"),
    "nettie": dict(symbol="Device:NetTie_2", footprint="NetTie:NetTie-2_SMD_Pad0.5mm", value="Kelvin",
                   BOM="no", Description="Kelvin sense tap (copper only, no component)"),
    "wirepad": dict(symbol="Connector:TestPoint", footprint="fc:WirePad_5x4mm", value="WIRE PAD", BOM="no",
                    Description="Solder pad for power wire"),
    "hdr2x10": dict(symbol="Connector_Generic:Conn_02x10_Odd_Even",
                    footprint="Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Horizontal", value="2x10 RA 2.54mm",
                    MPN="PZ254R-12-20P", Manufacturer="XFCN", LCSC="C492438", Price=0.18,
                    Description="2x10 right-angle pin header, 2.54 mm (hand-soldered)", Assembly="hand",
                    Datasheet="https://www.lcsc.com/datasheet/C492438.pdf"),
    "hdr3x9": dict(symbol=None, footprint="fc:PinHeader_3x09_P2.54mm_Horizontal", value="3x9 RA 2.54mm",
                   MPN="PZ254-3-03-W-2.5-G0 (x3)", Manufacturer="HCTL", LCSC="C7429379", Price=0.72,
                   Description="3x9 right-angle pin header, 2.54 mm: three 3x3 pieces (hand-soldered)",
                   Assembly="hand", Datasheet="https://www.lcsc.com/datasheet/C7429379.pdf"),
    "b2b_socket": dict(symbol="Connector_Generic:Conn_02x10_Odd_Even", footprint="fc:Samtec_SFMC-110-02-x-D",
                       value="SFMC-110-02-L-D", MPN="SFMC-110-02-L-D", Manufacturer="Samtec", LCSC="C3323057",
                       Price=5.50, Assembly="hand",
                       Description="2x10 SMT socket, 1.27 mm, 4.70 mm tall (buy from a distributor; hand-solder or consign)",
                       Datasheet="https://suddendocs.samtec.com/catalog_english/sfmc.pdf"),
    "b2b_header": dict(symbol="Connector_Generic:Conn_02x10_Odd_Even", footprint="fc:Samtec_FTSH-110-xx-x-DV",
                       value="FTSH-110-04-L-DV", MPN="FTSH-110-04-L-DV", Manufacturer="Samtec", LCSC="C7279869",
                       Price=4.19, Assembly="hand",
                       Description="2x10 SMT terminal strip, 1.27 mm, 3.81 mm posts (buy from a distributor; hand-solder or consign)",
                       Datasheet="https://suddendocs.samtec.com/catalog_english/ftsh_smt.pdf"),
    "standoff": dict(symbol="Mechanical:MountingHole_Pad", footprint="fc:Standoff_SMT_M2_H8.0", value="M2 x 8 mm",
                     MPN="SMTSO2080CTJ", Manufacturer="Sinhoo", LCSC="C2916357", Price=0.17,
                     Description="Reflow-solder M2 standoff, 8.0 mm",
                     Datasheet="https://www.lcsc.com/datasheet/C2916357.pdf"),
    "led_red": dict(symbol="Device:LED", footprint="LED_SMD:LED_0603_1608Metric", value="RED",
                    MPN="KT-0603R", Manufacturer="Hubei Kento", LCSC="C2286", Price=0.007, Description="Red LED 0603"),
    "led_green": dict(symbol="Device:LED", footprint="LED_SMD:LED_0603_1608Metric", value="GREEN",
                      MPN="NCD0603G1", Manufacturer="Nationstar", LCSC="C84267", Price=0.016,
                      Description="Green LED 0603"),
    "led_blue": dict(symbol="Device:LED", footprint="LED_SMD:LED_0603_1608Metric", value="BLUE",
                     MPN="NCD0603B1", Manufacturer="Nationstar", LCSC="C84266", Price=0.017,
                     Description="Blue LED 0603"),
    # --- logic board
    "mcu": dict(symbol="MCU_ST_STM32F7:STM32F765VITx", footprint="Package_QFP:LQFP-100_14x14mm_P0.5mm",
                value="STM32F765VIT6", MPN="STM32F765VIT6", Manufacturer="STMicroelectronics", LCSC="C710319",
                Price=16.34, Description="Cortex-M7 216 MHz, 2 MB flash, LQFP-100",
                Datasheet="https://www.st.com/resource/en/datasheet/stm32f765vi.pdf"),
    "imu": dict(symbol=_icm42688, footprint="Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y", value="ICM-45686",
                MPN="ICM-45686", Manufacturer="TDK InvenSense", LCSC="C22459454", Price=14.35,
                Description="6-axis IMU, SPI, LGA-14 2.5x3 mm (ICM-42688-P is a drop-in alternative)",
                Datasheet="https://www.lcsc.com/datasheet/C22459454.pdf"),
    "baro": dict(symbol=_bmp388, footprint="fc:Bosch_LGA-10_2x2mm_P0.5mm",
                 value="BMP388", MPN="BMP388", Manufacturer="Bosch Sensortec", LCSC="C779278", Price=2.39,
                 Description="Barometric pressure sensor, I2C, LGA-10 2x2 mm",
                 Datasheet="https://www.lcsc.com/datasheet/C779278.pdf"),
    "osd": dict(symbol=_at7456e, footprint="Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.75x6.2mm", value="AT7456E",
                MPN="AT7456E", Manufacturer="Zhongkewei", LCSC="C82351", Price=3.29,
                Description="Single-channel monochrome OSD generator (MAX7456 compatible)",
                Datasheet="https://www.lcsc.com/datasheet/C82351.pdf"),
    "ldo_main": dict(symbol=_ldo, footprint="Package_TO_SOT_SMD:SOT-23-5", value="TLV75533PDBVR",
                     MPN="TLV75533PDBVR", Manufacturer="Texas Instruments", LCSC="C404027", Price=0.15,
                     Description="3.3 V 500 mA LDO", Datasheet="https://www.ti.com/lit/ds/symlink/tlv755p.pdf"),
    "ldo_sens": dict(symbol=_ldo, footprint="Package_TO_SOT_SMD:SOT-23-5", value="TPS7A2033PDBVR",
                     MPN="TPS7A2033PDBVR", Manufacturer="Texas Instruments", LCSC="C2862740", Price=0.23,
                     Description="3.3 V 300 mA ultra-low-noise LDO",
                     Datasheet="https://www.ti.com/lit/ds/symlink/tps7a20.pdf"),
    "oring": dict(symbol=_lm66200, footprint="Package_TO_SOT_SMD:SOT-583-8", value="LM66200DRLR",
                  MPN="LM66200DRLR", Manufacturer="Texas Instruments", LCSC="C3235556", Price=0.49,
                  Description="Dual ideal diode OR, 2.5 A, 40 mohm",
                  Datasheet="https://www.ti.com/lit/ds/symlink/lm66200.pdf"),
    "xtal8": dict(symbol="Device:Crystal_GND24", footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", value="8MHz 12pF",
                  MPN="XL2EL89COI-111YLC-8M", Manufacturer="YXC", LCSC="C2973805", Price=0.16,
                  Description="8 MHz crystal, CL 12 pF, 3225", Datasheet="https://www.lcsc.com/datasheet/C2973805.pdf"),
    "xtal27": dict(symbol="Device:Crystal_GND24", footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
                   value="27MHz 10pF", MPN="X322527MMB4SI", Manufacturer="YXC", LCSC="C5210645", Price=0.09,
                   Description="27 MHz fundamental crystal, 3225",
                   Datasheet="https://www.lcsc.com/datasheet/C5210645.pdf"),
    "ferrite": dict(symbol="Device:FerriteBead", footprint="Inductor_SMD:L_0603_1608Metric", value="120R@100MHz",
                    MPN="BLM18PG121SN1D", Manufacturer="Murata", LCSC="C14709", Price=0.015,
                    Description="Ferrite bead 120 ohm, 2 A, 0603"),
    "nmos": dict(symbol="Transistor_FET:2N7002", footprint="Package_TO_SOT_SMD:SOT-23", value="2N7002",
                 MPN="2N7002", Manufacturer="JSCJ", LCSC="C8545", Price=0.016, Description="N-MOSFET 60 V SOT-23"),
    "pmos": dict(symbol="Transistor_FET:AO3401A", footprint="Package_TO_SOT_SMD:SOT-23", value="AO3401A",
                 MPN="AO3401A", Manufacturer="AOS", LCSC="C15127", Price=0.07, Description="P-MOSFET -30 V 4 A SOT-23"),
    "sd": dict(symbol="Connector:Micro_SD_Card_Det2", footprint="Connector_Card:microSD_HC_Molex_104031-0811",
               value="microSD", MPN="104031-0811", Manufacturer="Molex", LCSC="C585350", Price=0.68,
               Description="microSD push-push socket", Datasheet="https://www.lcsc.com/datasheet/C585350.pdf"),
    "jst6": dict(symbol="Connector_Generic_MountingPin:Conn_01x06_MountingPin",
                 footprint="Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal", value="JST-SH 6P",
                 MPN="SM06B-SRSS-TB(LF)(SN)", Manufacturer="JST", LCSC="C160405", Price=0.30,
                 Description="JST SH 6-pin side-entry header, 1.0 mm"),
    "hdr3x12": dict(symbol=None, footprint="fc:PinHeader_3x12_P2.54mm_Horizontal", value="3x12 RA 2.54mm",
                    MPN="PZ254-3-03-W-2.5-G0 (x4) or TSW-112-08-G-T-RA", Manufacturer="HCTL / Samtec", LCSC="C7429379",
                    Price=0.96, Description="3x12 right-angle pin header, 2.54 mm: four 3x3 pieces or one Samtec TSW (hand-soldered)",
                    Assembly="hand",
                    Datasheet="https://www.lcsc.com/datasheet/C7429379.pdf"),
    "testpad": dict(symbol="Connector:TestPoint", footprint="TestPoint:TestPoint_Pad_D1.0mm", value="TP", BOM="no",
                    Description="Test pad"),
    # --- service board
    "usbc": dict(symbol="Connector:USB_C_Receptacle_USB2.0_16P", footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
                 value="USB-C", MPN="TYPE-C-31-M-12", Manufacturer="Korean Hroparts", LCSC="C165948", Price=0.19,
                 Description="USB Type-C 2.0 receptacle, 16-pin", Datasheet="https://www.lcsc.com/datasheet/C165948.pdf"),
    "usbesd": dict(symbol="Power_Protection:USBLC6-2SC6", footprint="Package_TO_SOT_SMD:SOT-23-6", value="USBLC6-2SC6",
                   MPN="USBLC6-2SC6", Manufacturer="STMicroelectronics", LCSC="C7519", Price=0.18,
                   Description="USB ESD protection"),
    "buzzer": dict(symbol="Device:Buzzer", footprint="Buzzer_Beeper:MagneticBuzzer_CUI_CMT-8504-100-SMT", value="MLT-8530",
                   MPN="KLJ-8530-3627 / MLT-8530", Manufacturer="Keliking / Huaneng", LCSC="C189206", Price=0.57,
                   Description="Passive magnetic buzzer 8.5x8.5 mm, 2.7 kHz, 16 ohm",
                   Datasheet="https://www.lcsc.com/datasheet/C189206.pdf"),
    "button": dict(symbol="Switch:SW_Push", footprint="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", value="BOOT",
                   MPN="TS-1187A-B-A-B", Manufacturer="XKB", LCSC="C318884", Price=0.02,
                   Description="Tactile switch 5.1x5.1 mm"),
    "schottky": dict(symbol="Device:D_Schottky", footprint="Diode_SMD:D_SOD-323", value="B5819WS",
                     MPN="B5819WS", Manufacturer="various", LCSC="C916992", Price=0.013,
                     Description="Schottky diode 40 V 1 A SOD-323"),
}
