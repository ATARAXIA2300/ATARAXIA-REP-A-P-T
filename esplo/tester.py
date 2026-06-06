import pyshark

capture = pyshark.LiveCapture(interface='eth0')
capture.sniff(timeout=5)
for packet in capture:
    print(f"Captured: {packet}")