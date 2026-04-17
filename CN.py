import sys
import logging
import argparse
import dpkt
import socket
import pandas as pd
from tabulate import tabulate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def load_pcap(file_path):
    try:
        f = open(file_path, "rb")
        return dpkt.pcap.Reader(f)
    except FileNotFoundError:
        log.error(f"File not found: {file_path}")
        sys.exit(1)

def ip_to_str(address):
    return socket.inet_ntoa(address)

def extract_packet_info(pcap):
    rows = []

    for ts, buf in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            if not isinstance(eth.data, dpkt.ip.IP):
                continue

            ip = eth.data
            src_ip = ip_to_str(ip.src)
            dst_ip = ip_to_str(ip.dst)
            size = len(buf)

            protocol = "Other"
            src_port = None
            dst_port = None

            if isinstance(ip.data, dpkt.tcp.TCP):
                protocol = "TCP"
                src_port = ip.data.sport
                dst_port = ip.data.dport
            elif isinstance(ip.data, dpkt.udp.UDP):
                protocol = "UDP"
                src_port = ip.data.sport
                dst_port = ip.data.dport
            elif isinstance(ip.data, dpkt.icmp.ICMP):
                protocol = "ICMP"

            rows.append({
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "src_port": src_port,
                "dst_port": dst_port,
                "size": size,
            })

        except Exception:
            continue

    return pd.DataFrame(rows)

def show_protocol_distribution(df):
    proto_counts = df["protocol"].value_counts()
    total = proto_counts.sum()

    table = []
    for protocol, count in proto_counts.items():
        percentage = (count / total) * 100
        table.append([protocol, count, f"{percentage:.1f}%"])

    print(tabulate(table, headers=["Protocol", "Count", "Percentage"]))

def detect_port_scan(df, threshold=20):
    port_df = df[df["dst_port"].notna()]

    unique_ports = (
        port_df.groupby("src_ip")["dst_port"]
        .nunique()
        .reset_index(name="unique_ports")
    )

    suspicious = unique_ports[unique_ports["unique_ports"] >= threshold]

    if not suspicious.empty:
        log.warning("Potential port scanning detected:")
        print(suspicious)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap_file")
    args = parser.parse_args()

    pcap = load_pcap(args.pcap_file)
    df = extract_packet_info(pcap)

    if df.empty:
        log.warning("No IP packets found")
        return

    show_protocol_distribution(df)
    detect_port_scan(df)

if __name__ == "__main__":
    main()