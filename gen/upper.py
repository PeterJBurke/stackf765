"""UPPER (logic) board: STM32F765, IMU, barometer, analog OSD, microSD,
3x12 right-angle header, board-to-board header, service connector.
"""
import math
from kigen.design import Design, box
from blocks import Blocks
from pinmap import PINMAP
from lower import B2B, STANDOFFS

W, H = 31.5, 48.0

# 3 x 12 header.  Row A = highest pins (holes furthest from the board edge), row C = lowest.
# Each entry: (silk label, net).  Columns 1..12 run left to right seen from the top.
J1_ROWS = {
    "A": [("G", "GND"), ("4V5", "+5V_SYS"), ("TX1", "TX1"), ("RX1", "RX1"), ("SDA", "SDA"), ("SCL", "SCL"),
          ("G", "GND"), ("5V", "+5V"), ("CAM", "CAM_IN"), ("G", "GND"), ("5V", "+5V"), ("VTX", "VTX_OUT")],
    "B": [("G", "GND"), ("4V5", "+5V_SYS"), ("TX2", "TX2"), ("RX2", "RX2"), ("G", "GND"), ("5V", "+5V"),
          ("TX3", "TX3"), ("RX3", "RX3"), ("G", "GND"), ("5V", "+5V"), ("TX4", "TX4"), ("RX4", "RX4")],
    "C": [("G", "GND"), ("5V", "+5V"), ("TX6", "TX6"), ("RX6", "RX6"), ("G", "GND"), ("5V", "+5V"),
          ("TX7", "TX7"), ("RX7", "RX7"), ("G", "GND"), ("5V", "+5V"), ("TX8", "TX8"), ("RX8", "RX8")],
}
# service cable (JST-SH 6): pin -> net
SVC = {1: "VBUS", 2: "USB_DM", 3: "USB_DP", 4: "GND", 5: "BUZ_OUT", 6: "BOOT0"}

MCU_POS = (0.0, 2.5)
MCU_ROT = 180


def _hdr_symbol():
    left = [(f"A{i + 1}", f"A{i + 1} {J1_ROWS['A'][i][0]}") for i in range(12)] + [None] + \
           [(f"C{i + 1}", f"C{i + 1} {J1_ROWS['C'][i][0]}") for i in range(12)]
    right = [(f"B{i + 1}", f"B{i + 1} {J1_ROWS['B'][i][0]}") for i in range(12)]
    return box("HDR_3x12", left=left, right=right, ref="J", width=30.48)


def design():
    d = Design("upper", "StackF765 upper board (flight controller)", rev="A", date="2026-11-16",
               rails=("+5V", "+5V_SYS", "+3V3", "+3V3_SENS", "VBUS"))
    B = Blocks(d)
    d.root_notes = [
        "UPPER BOARD = flight controller.  STM32F765VIT6 running ArduPilot (board name StackF765).",
        "Power: +5V arrives from the lower board; VBUS arrives from the USB service board.  An ideal-diode OR",
        "makes +5V_SYS (silk '4V5'), which feeds the 3.3 V regulators and the OSD, so the board runs from USB alone.",
        "Header pins marked 5V are powered only from the battery; pins marked 4V5 are also powered from USB.",
        "Net names match the silkscreen labels and the ArduPilot hwdef (see firmware/hwdef/StackF765/hwdef.dat).",
    ]

    # ------------------------------------------------------------------ sheet: power
    s = d.sheet("power", "Power: 5 V OR-ing and 3.3 V regulators")
    s.frame(15, 20, 185, 110, "U5: ideal-diode OR of battery 5 V and USB 5 V  ->  +5V_SYS")
    B.part(s, "U5", "oring", 100, 70, nets={"VIN1": "+5V", "VIN2": "VBUS", "~{ON}": "GND", "VOUT": "+5V_SYS",
                                           "GND": "GND"}, nc=("ST",))
    B.C(s, "C1", "10u", "+5V", "GND", 40, 90, 0, "0603")
    B.C(s, "C2", "1u", "VBUS", "GND", 55, 90, 0)
    B.part(s, "D3", "tvs5", 70, 90, 90, nets={"1": "VBUS", "2": "GND"})
    B.C(s, "C3", "10u", "+5V_SYS", "GND", 150, 90, 0, "0603")
    B.C(s, "C4", "10u", "+5V_SYS", "GND", 165, 90, 0, "0603")
    s.text(20, 122, "The higher input wins; reverse current is blocked, so USB never back-feeds the battery rail.", 1.5)

    s.frame(210, 20, 190, 110, "U6: +3V3 for MCU, microSD, I2C pull-ups (500 mA)")
    B.part(s, "U6", "ldo_main", 300, 65, nets={"IN": "LDO_IN", "EN": "LDO_IN", "OUT": "+3V3", "GND": "GND"}, nc=("NC",))
    B.R(s, "R16", "4.7R", "+5V_SYS", "LDO_IN", 230, 45, 90, "0805")
    B.R(s, "R17", "4.7R", "+5V_SYS", "LDO_IN", 230, 62, 90, "0805")
    B.C(s, "C5", "1u", "LDO_IN", "GND", 245, 90, 0)
    s.flag("LDO_IN", 262, 60)
    s.text(215, 122, "R16 || R17 = 2.35 ohm share the heat with U6: at 250 mA they drop 0.6 V (0.15 W),\nU6 dissipates 0.28 W instead of 0.43 W.", 1.4)
    B.C(s, "C6", "1u", "+3V3", "GND", 345, 90, 0)
    B.C(s, "C7", "10u", "+3V3", "GND", 360, 90, 0, "0603")

    s.frame(15, 145, 185, 100, "U7: +3V3_SENS, low-noise supply for IMU and barometer")
    B.part(s, "U7", "ldo_sens", 100, 190, nets={"IN": "+5V_SYS", "EN": "+5V_SYS", "OUT": "+3V3_SENS", "GND": "GND"},
           nc=("NC",))
    B.C(s, "C8", "1u", "+5V_SYS", "GND", 45, 215, 0)
    B.C(s, "C9", "1u", "+3V3_SENS", "GND", 150, 215, 0)

    s.frame(210, 145, 190, 100, "Power flags and test pads")
    for i, n in enumerate(["+5V", "VBUS", "GND"]):
        s.flag(n, 230 + i * 25.4, 180)
    for i, (ref, net) in enumerate([("TP1", "+3V3"), ("TP2", "GND"), ("TP3", "+5V_SYS")]):
        B.part(s, ref, "testpad", 320 + i * 22, 195, 0, nets={"1": net}, value=net)

    # ------------------------------------------------------------------ sheet: MCU
    s = d.sheet("mcu", "Microcontroller STM32F765VIT6")
    u = B.part(s, "U1", "mcu", 210, 150)
    for pin, (net, _) in PINMAP.items():
        u[pin] = net
    u["VDD"] = "+3V3"; u["VSS"] = "GND"; u["VBAT"] = "+3V3"
    u["VDDA"] = "VDDA"; u["VREF+"] = "VDDA"; u["VSSA"] = "GND"
    u["VCAP_1"] = "VCAP1"; u["VCAP_2"] = "VCAP2"
    u["NRST"] = "NRST"; u["BOOT0"] = "BOOT0"
    u["PH0"] = "OSC_IN"; u["PH1"] = "OSC_OUT"
    u.nc_rest()
    s.text(20, 25, "Every connected pin is listed in gen/pinmap.py and checked against the ArduPilot hwdef by "
                   "tools/check_hwdef.py.  Unconnected pins are spare.", 1.6)

    # ------------------------------------------------------------------ sheet: MCU support
    s = d.sheet("support", "MCU support: decoupling, clock, reset, boot, debug, LEDs")
    s.frame(15, 20, 250, 85, "Decoupling: one 100 nF per VDD pin, bulk, VCAP, filtered VDDA")
    for i in range(5):
        B.C(s, f"C{10 + i}", "100n", "+3V3", "GND", 35 + i * 15, 60, 0)
    B.C(s, "C15", "4.7u", "+3V3", "GND", 110, 60, 0, "0603")
    B.C(s, "C16", "100n", "+3V3", "GND", 125, 60, 0)
    B.C(s, "C17", "2.2u", "VCAP1", "GND", 150, 60, 0)
    B.C(s, "C18", "2.2u", "VCAP2", "GND", 170, 60, 0)
    B.part(s, "FB1", "ferrite", 205, 45, 90, nets={"1": "+3V3", "2": "VDDA"})
    B.C(s, "C19", "1u", "VDDA", "GND", 225, 65, 0)
    B.C(s, "C20", "100n", "VDDA", "GND", 240, 65, 0)
    s.text(20, 98, "C16 is the VBAT-pin capacitor.  VREF+ is tied to VDDA.", 1.5)

    s.frame(275, 20, 125, 85, "8 MHz crystal (CL 12 pF, 2 x 15 pF)")
    B.part(s, "Y1", "xtal8", 335, 55, 0, nets={"1": "OSC_IN", "3": "OSC_OUT", "G": "GND"})
    B.C(s, "C21", "15p", "OSC_IN", "GND", 300, 80, 0)
    B.C(s, "C22", "15p", "OSC_OUT", "GND", 375, 80, 0)

    s.frame(15, 115, 180, 125, "Reset, boot and SWD test pads")
    B.C(s, "C23", "100n", "NRST", "GND", 40, 150, 0)
    B.R(s, "R1", "10k", "BOOT0", "GND", 75, 150, 0)
    for i, (ref, net) in enumerate([("TP4", "SWDIO"), ("TP5", "SWCLK"), ("TP6", "NRST")]):
        B.part(s, ref, "testpad", 110 + i * 25, 150, 0, nets={"1": net}, value=net)
    s.text(20, 215, "BOOT0 is pulled high from USB VBUS through the button and 10 k on the service board\n"
                    "(divider 10k/10k = 2.5 V).  Hold the button while plugging USB to enter DFU.", 1.5)

    s.frame(205, 115, 195, 125, "Status LEDs (active low) and I2C pull-ups")
    B.R(s, "R2", "470R", "+3V3", "LEDB_A", 235, 150, 90)
    B.part(s, "D1", "led_blue", 235, 175, 0, nets={"A": "LEDB_A", "K": "LED_BLUE"})
    B.R(s, "R3", "470R", "+3V3", "LEDG_A", 235, 200, 90)
    B.part(s, "D2", "led_green", 235, 225, 0, nets={"A": "LEDG_A", "K": "LED_GREEN"})
    B.R(s, "R4", "2.2k", "+3V3", "SCL", 320, 150, 90)
    B.R(s, "R5", "2.2k", "+3V3", "SDA", 320, 170, 90)
    B.R(s, "R6", "2.2k", "+3V3_SENS", "BARO_SCL", 320, 200, 90)
    B.R(s, "R7", "2.2k", "+3V3_SENS", "BARO_SDA", 320, 220, 90)
    s.flag("VDDA", 255, 45)

    # ------------------------------------------------------------------ sheet: sensors
    s = d.sheet("sensors", "IMU and barometer")
    s.frame(15, 20, 190, 220, "U2: ICM-42688-P 6-axis IMU on SPI1 (ICM-45686 fits the same footprint)")
    B.part(s, "U2", "imu", 110, 90, nets={"SCLK": "IMU_SCK", "SDI": "IMU_MOSI", "SDO": "IMU_MISO", "CS": "IMU_CS",
                                         "INT1": "IMU_INT", "INT2/FSYNC": "GND", "VDD": "+3V3_SENS",
                                         "VDDIO": "+3V3_SENS", "RESV7": "GND", "GND": "GND"},
           nc=("RESV2", "RESV3", "RESV10", "RESV11"))
    B.C(s, "C30", "100n", "+3V3_SENS", "GND", 60, 170, 0)
    B.C(s, "C31", "2.2u", "+3V3_SENS", "GND", 80, 170, 0)
    B.C(s, "C32", "100n", "+3V3_SENS", "GND", 100, 170, 0)
    s.text(20, 230, "FSYNC unused -> GND.  Pin 7 -> GND (required by both IMU variants).", 1.5)
    s.frame(215, 20, 185, 220, "U3: BMP388 barometer on I2C2, address 0x76 (SDO = GND)")
    B.part(s, "U3", "baro", 305, 90, nets={"SCK": "BARO_SCL", "SDI": "BARO_SDA", "SDO": "GND", "CSB": "+3V3_SENS",
                                          "VDD": "+3V3_SENS", "VDDIO": "+3V3_SENS", "VSS": "GND"}, nc=("INT",))
    B.C(s, "C33", "100n", "+3V3_SENS", "GND", 260, 170, 0)
    B.C(s, "C34", "100n", "+3V3_SENS", "GND", 280, 170, 0)

    # ------------------------------------------------------------------ sheet: OSD + SD
    s = d.sheet("osd_sd", "Analog OSD and microSD")
    s.frame(15, 20, 250, 220, "U4: AT7456E on-screen display on SPI2 (video in from camera, out to VTX)")
    B.part(s, "U4", "osd", 130, 95, nets={"~{CS}": "OSD_CS", "SDIN": "OSD_MOSI", "SCLK": "OSD_SCK", "SDOUT": "OSD_MISO",
                                         "~{RESET}": "+5V_SYS", "CLKIN": "OSD_X1", "XFB": "OSD_X2",
                                         "DVDD": "+5V_SYS", "AVDD": "+5V_SYS", "PVDD": "+5V_SYS",
                                         "VIN": "OSD_VIN", "VOUT": "OSD_VOUT", "SAG": "OSD_VOUT",
                                         "DGND": "GND", "AGND": "GND", "PGND": "GND", "EP": "GND"},
           nc=("CLKOUT", "LOS", "~{VSYNC}", "~{HSYNC}", "SYNC_IN"))
    for n in (1, 2, 14, 15, 16, 27, 28):
        pass
    B.part(s, "Y2", "xtal27", 50, 150, 0, nets={"1": "OSD_X1", "3": "OSD_X2", "G": "GND"})
    B.C(s, "C40", "100n", "+5V_SYS", "GND", 40, 200, 0)
    B.C(s, "C41", "100n", "+5V_SYS", "GND", 55, 200, 0)
    B.C(s, "C42", "100n", "+5V_SYS", "GND", 70, 200, 0)
    B.C(s, "C43", "4.7u", "+5V_SYS", "GND", 85, 200, 0, "0603")
    B.C(s, "C44", "100n", "CAM_IN", "OSD_VIN", 205, 150, 90)
    B.R(s, "R10", "75R", "CAM_IN", "GND", 205, 180, 0)
    B.R(s, "R11", "75R", "OSD_VOUT", "VTX_OUT", 205, 215, 90)
    s.text(20, 233, "Input: 75 ohm termination + 100 nF AC coupling (chip clamps internally).  Output: 75 ohm "
                    "back-termination, DC coupled (SAG tied to VOUT).", 1.4)
    s.frame(275, 20, 125, 220, "J4: microSD on SDMMC1 (4-bit)")
    B.part(s, "J4", "sd", 335, 90, nets={"DAT2": "SD_D2", "DAT3/CD": "SD_D3", "CMD": "SD_CMD", "VDD": "+3V3",
                                        "CLK": "SD_CK", "VSS": "GND", "DAT0": "SD_D0", "DAT1": "SD_D1",
                                        "SHIELD": "GND"}, nc=("DET_A", "DET_B"))
    B.C(s, "C45", "100n", "+3V3", "GND", 300, 190, 0)
    B.C(s, "C46", "10u", "+3V3", "GND", 320, 190, 0, "0603")
    s.text(280, 233, "Pull-ups: MCU internal (set by ArduPilot).", 1.4)

    # ------------------------------------------------------------------ sheet: connectors
    s = d.sheet("connectors", "Connectors, buzzer driver, analog filters")
    s.frame(15, 20, 150, 220, "J1: 3 x 12 right-angle header (labels = silkscreen)")
    j = d.part("J1", _hdr_symbol(), "fc:PinHeader_3x12_P2.54mm_Horizontal", "3x12 RA 2.54mm",
               **{k: v for k, v in __import__("parts").PARTS["hdr3x12"].items() if k not in ("symbol", "footprint", "value")})
    for row, cols in J1_ROWS.items():
        for i, (_, net) in enumerate(cols):
            j[f"{row}{i + 1}"] = net
    s.place(j, 90, 120)
    s.frame(175, 20, 110, 105, "J3: board-to-board header (to lower board)")
    j = B.part(s, "J3", "b2b_header", 230, 70)
    for pin, net in B2B.items():
        j[str(pin)] = net
    s.frame(295, 20, 105, 105, "J5: service cable (USB, buzzer, boot)")
    j = B.part(s, "J5", "jst6", 345, 65, nets={"MP": "GND"})
    for pin, net in SVC.items():
        j[str(pin)] = net
    s.frame(175, 135, 110, 105, "Buzzer high-side switch (5 V pulses on BUZ_OUT)")
    B.part(s, "Q1", "nmos", 205, 180, nets={"G": "BUZZER", "S": "GND", "D": "BUZ_G"})
    B.part(s, "Q2", "pmos", 245, 172, nets={"G": "BUZ_G", "S": "+5V_SYS", "D": "BUZ_SW"})
    B.R(s, "R18", "10R", "BUZ_SW", "BUZ_OUT", 268, 200, 0, "1206")
    B.R(s, "R12", "100k", "BUZZER", "GND", 190, 215, 0)
    B.R(s, "R13", "10k", "+5V_SYS", "BUZ_G", 230, 215, 0)
    s.frame(295, 135, 105, 105, "ADC input filters (1 k / 100 nF)")
    B.R(s, "R14", "1k", "VBAT_SENSE", "VBAT_ADC", 325, 165, 90)
    B.C(s, "C50", "100n", "VBAT_ADC", "GND", 365, 175, 0)
    B.R(s, "R15", "1k", "CURR_SENSE", "CURR_ADC", 325, 205, 90)
    B.C(s, "C51", "100n", "CURR_ADC", "GND", 365, 215, 0)
    return d


# ====================================================================== PCB
RULES = dict(
    layers=6,
    netclasses=[
        {"name": "Default", "clearance": 0.127, "track_width": 0.15, "via_diameter": 0.5, "via_drill": 0.3},
        {"name": "Power", "clearance": 0.127, "track_width": 0.4, "via_diameter": 0.5, "via_drill": 0.3},
    ],
    patterns=[("Power", n) for n in ("+5V", "+5V_SYS", "+3V3", "+3V3_SENS", "VBUS", "GND")],
    rules=dict(clearance=0.127, track=0.127, via_dia=0.45, via_drill=0.25, annular=0.09, hole_clearance=0.2,
               edge=0.25, severities={"lib_footprint_mismatch": "ignore", "lib_footprint_issues": "ignore",
                                      "silk_over_copper": "ignore", "silk_overlap": "ignore",
                                      "silk_edge_clearance": "ignore"}),
)

# MCU capacitors: ref -> (pin it sits next to, shift along the pin row in mm)
DECAP = {"C10": (11, -1.6), "C16": (6, -1.05), "C20": (21, 0.0),          # right side: VDD, VBAT, VDDA/VREF+
         "C11": (27, 0.0), "C17": (48, 0.9), "C12": (50, -0.6),         # top row: VDD, VCAP1, VDD
         "C18": (73, 0.9), "C13": (75, -0.6), "C14": (100, 0.0)}        # left: VCAP2, VDD; bottom row: VDD

TOP = [  # ref, x, y, rot
    ("U2", 13.4, 11.3, 0), ("C30", 13.4, 8.9, 0), ("C31", 10.6, 12.5, 0), ("C32", 10.6, 10.9, 0),      # IMU
    ("U3", -13.4, 11.3, 0), ("C33", -11.2, 11.9, 90), ("C34", -13.4, 9.0, 0),                         # barometer
        ("FB1", 13.2, 6.4, 0), ("C19", 13.2, 7.8, 0),                                                      # VDDA filter
    ("Y1", 12.9, -0.9, 0),                                                                             # 8 MHz
    ("D1", -14.3, -1.6, 90), ("R2", -12.9, -1.6, 90), ("D2", -14.3, -4.8, 90), ("R3", -12.9, -4.8, 90),  # LEDs
    ("TP4", -14.2, -8.1, 0), ("TP5", -12.0, -8.1, 0),                                                  # SWD pads
    ("U6", 0.9, -10.4, 0), ("U7", 5.2, -10.4, 0),                                                      # regulators
    ("U4", 5.5, -18.6, 0),                                                    # OSD
    ("C40", 0.2, -15.7, 90), ("C41", 10.5, -19.2, 0), ("C42", 12.6, -19.2, 0), ("C44", 10.5, -20.5, 0),
    ("R10", 12.6, -20.5, 0), ("R11", 10.5, -21.8, 0), ("C43", 13.0, -22.1, 0),
]
BOT = [
    ("U5", 6.5, -10.6, 0), ("C1", 5.8, -5.2, 0), ("C2", 9.0, -10.2, 90), ("C3", 9.6, -12.5, 0), ("C4", 0.0, -13.0, 0),
    ("C5", -1.0, -10.4, 90), ("C6", 2.4, -9.6, 0), ("C7", 2.3, -11.2, 0), ("C8", 3.6, -8.3, 0), ("C9", 6.6, -8.4, 0),
    ("Q1", 9.0, -2.0, 0), ("Q2", 13.3, -6.2, 0), ("R18", 14.2, -10.5, 90), ("D3", 5.8, -13.1, 0),
    ("R16", -2.4, -7.5, 0), ("R17", -4.2, -10.2, 90), ("R12", 8.6, -5.2, 0), ("R13", 10.6, -6.2, 90),
    ("R14", 5.6, 6.2, 0), ("C50", 5.6, 7.3, 0), ("R15", 3.4, 6.2, 0), ("C51", 3.4, 7.3, 0),
    ("C23", 7.8, 5.0, 0), ("R1", 3.0, -6.4, 0), ("C15", -4.0, 6.5, 0),
    ("R4", -3.5, -5.7, 0), ("R5", -1.4, -5.7, 0), ("R6", -8.6, 5.8, 0), ("R7", -8.6, 4.7, 0),
    ("C21", 11.6, -1.0, 90), ("C22", 14.2, -1.0, 90),
    ("Y2", 0.9, -17.3, 90),
    ("C45", -8.5, -20.3, 0), ("C46", -5.4, -20.3, 0),
    ("TP6", -14.0, -3.0, 0), ("TP1", -14.0, -5.4, 0), ("TP2", -11.6, -5.4, 0), ("TP3", -11.6, -3.0, 0),
]


def _outside_mcu(bd, pin, dist, shift=0.0):
    """Position 'dist' mm outside the MCU pad row at the given pin; returns (x, y, rotation along the row)."""
    px, py = bd.padpos("U1", pin)
    cx, cy = MCU_POS
    dx, dy = px - cx, py - cy
    if abs(dx) > abs(dy):
        s = 1 if dx > 0 else -1
        return px + s * dist, py + shift, 90
    s = 1 if dy > 0 else -1
    return px + shift, py + s * dist, 0


def layout(bd):
    bd.outline_roundrect(W, H, 1.5)
    for x, y in STANDOFFS:
        bd.hole(x, y, 2.2)
        bd.circle("User.Comments", x, y, 2.1)
    # --- connectors
    bd.place("J1", -13.97, 14.46, 90)                 # A1 at the left; pins point forward
    bd.place("J3", 0, 0, 270, side="bottom")           # mates with J1 on the lower board
    bd.place("J5", 12.3, -8.0, 90)                    # service connector on the right edge
    bd.place("J4", -8.3, -16.3, 180)                  # microSD, card inserts from the rear edge
    # --- MCU and its capacitors
    bd.place("U1", MCU_POS[0], MCU_POS[1], MCU_ROT)
    for ref, (pin, shift) in DECAP.items():
        x, y, rot = _outside_mcu(bd, pin, 1.85, shift)
        bd.place(ref, x, y, rot)
    for ref, x, y, rot in TOP:
        bd.place(ref, x, y, rot)
    for ref, x, y, rot in BOT:
        bd.place(ref, x, y, rot, side="bottom")
    missing = [r for r in bd.design.parts if r not in bd.fps]
    if missing:
        raise SystemExit(f"unplaced parts: {missing}")
    # --- planes
    full = bd.rect(-W / 2, -H / 2, W / 2, H / 2)
    # 6-layer stack: F signal / In1 GND / In2 signal / In3 signal / In4 +3V3 / B signal
    bd.zone("GND", ["In1.Cu"], full, priority=1, name="GND plane")
    bd.zone("+3V3", ["In4.Cu"], full, priority=1, name="+3V3 plane")
    bd.zone("GND", ["F.Cu", "B.Cu", "In2.Cu", "In3.Cu"], full, priority=0, name="GND pour")
    # --- silkscreen: one label per header pin, printed just in front of its hole
    for r, row in enumerate("ABC"):
        for i, (lab, _) in enumerate(J1_ROWS[row]):
            bd.text(lab, -13.97 + i * 2.54, 14.46 + r * 2.54 + 1.27, size=0.7, thick=0.12)
            bd.text(lab, -13.97 + i * 2.54, 14.46 + r * 2.54 + 1.27, "B.SilkS", size=0.7, thick=0.12)
    bd.text("StackF765 UPPER rev A", 0, -3.6, "B.SilkS", size=0.9)


def router_config(bd):
    full = [(-W / 2, -H / 2, W / 2, H / 2)]
    return dict(layers=["F.Cu", "In2.Cu", "In3.Cu", "B.Cu"], grid=0.05, track=0.15, clear=0.127, via_dia=0.5, via_drill=0.3,
                plane_nets=("GND", "+3V3"),
                widths={"+5V": 0.5, "+5V_SYS": 0.4, "VBUS": 0.4, "LDO_IN": 0.4, "+3V3_SENS": 0.3, "BUZ_OUT": 0.3, "BUZ_SW": 0.3},
                layer_cost=[10, 13, 13, 11])


ROUTER = "sequential"
