"""
Allowed protocols on a given Equipment.

Protocols:

  0: SSH
  1: seedlink
  2: HTTP
  3: HTTPS
  4: SNMP
  5: ICMP
  6: TELNET
  7: FTP
"""

SSH = 0
SEED_LINK = 1
HTTP = 2
HTTPS = 3
SNMP = 4
ICMP = 5
TELNET = 6
FTP = 7

PROTOCOL_CHOICES = (
    (SSH, 'SSH protocol'),
    (SEED_LINK, 'Seed link protocol'),
    (HTTP, 'HTTP'),
    (HTTPS, 'HTTPS'),
    (SNMP, 'SNMP'),
    (ICMP, 'ICMP'),
    (TELNET, 'Telnet'),
    (FTP, 'FTP'),
)
