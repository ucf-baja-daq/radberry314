# reg52.py
# header file for generic 80C52 and 80C32 microcontroller.
# Copyright (c) 1988-2002 Keil Elektronik GmbH and Keil Software, Inc.
# All rights reserved.

# BYTE Registers
P0    = 0x80
P1    = 0x90
P2    = 0xA0
P3    = 0xB0
PSW   = 0xD0
ACC   = 0xE0
B     = 0xF0
SP    = 0x81
DPL   = 0x82
DPH   = 0x83
PCON  = 0x87
TCON  = 0x88
TMOD  = 0x89
TL0   = 0x8A
TL1   = 0x8B
TH0   = 0x8C
TH1   = 0x8D
IE    = 0xA8
IP    = 0xB8
SCON  = 0x98
SBUF  = 0x99

# 8052 Extensions
T2CON  = 0xC8
RCAP2L = 0xCA
RCAP2H = 0xCB
TL2    = 0xCC
TH2    = 0xCD


# BIT Registers
# PSW
CY    = PSW^7
AC    = PSW^6
F0    = PSW^5
RS1   = PSW^4
RS0   = PSW^3
OV    = PSW^2
P     = PSW^0 # 8052 only

# TCON
TF1   = TCON^7
TR1   = TCON^6
TF0   = TCON^5
TR0   = TCON^4
IE1   = TCON^3
IT1   = TCON^2
IE0   = TCON^1
IT0   = TCON^0

# IE
EA    = IE^7
ET2   = IE^5 # 8052 only
ES    = IE^4
ET1   = IE^3
EX1   = IE^2
ET0   = IE^1
EX0   = IE^0

# IP
PT2   = IP^5
PS    = IP^4
PT1   = IP^3
PX1   = IP^2
PT0   = IP^1
PX0   = IP^0

# P3
RD    = P3^7
WR    = P3^6
T1    = P3^5
T0    = P3^4
INT1  = P3^3
INT0  = P3^2
TXD   = P3^1
RXD   = P3^0

# SCON
SM0   = SCON^7
SM1   = SCON^6
SM2   = SCON^5
REN   = SCON^4
TB8   = SCON^3
RB8   = SCON^2
TI    = SCON^1
RI    = SCON^0

# P1
T2EX  = P1^1 # 8052 only
T2    = P1^0 # 8052 only

# T2CON
TF2    = T2CON^7
EXF2   = T2CON^6
RCLK   = T2CON^5
TCLK   = T2CON^4
EXEN2  = T2CON^3
TR2    = T2CON^2
C_T2   = T2CON^1
CP_RL2 = T2CON^0
