from scapy.all import sniff

print("In ascolto su eth0...")

packets = sniff(iface="eth0", count=5, timeout=10)

print(f"Catturati {len(packets)} pacchetti:")
for i, pkt in enumerate(packets):
    print(f"[{i+1}] {pkt.summary()}")
