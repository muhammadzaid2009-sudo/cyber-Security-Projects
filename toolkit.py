"""
This is my tookit that i made from my python jouney 


A menu-driven toolkit that integrates subdomain enumeration,
directory enumeration, and port scanning into a single cohesive
interface. Demonstrates code reuse, dispatch dictionaries, and
separation of concerns.

Usage:
    python3 toolkit.py
"""

import requests
import socket
import sys


# ----- Reused functions from earlier tasks -----

def load_wordlist(filepath):
    """Read a wordlist file and return a list of stripped lines."""
    try:
        with open(filepath, "r") as f:
            words = [line.strip() for line in f if line.strip()]
        print(f"[*] Loaded {len(words)} entries from {filepath}")
        return words
    except FileNotFoundError:
        print(f"[!] Error: '{filepath}' not found.")
        return []


def enumerate_subdomains(domain, wordlist):
    """Test each subdomain candidate against the target domain."""
    found = []
    for sub in wordlist:
        url = f"http://{sub}.{domain}"
        try:
            requests.get(url, timeout=3)
            print(f"[+] Found: {url}")
            found.append(url)
        except (requests.ConnectionError, requests.Timeout):
            pass
    return found


def enumerate_directories(target_url, wordlist, extension=".html"):
    """Test each directory/file candidate against the target URL."""
    found = []
    for entry in wordlist:
        url = f"{target_url}/{entry}{extension}"
        try:
            r = requests.get(url, timeout=3)
            if r.status_code != 404:
                print(f"[+] {r.status_code} - {url}")
                found.append(url)
        except (requests.ConnectionError, requests.Timeout):
            pass
    return found


def resolve_target(target):
    """Resolve a hostname to an IP address."""
    try:
        ip = socket.gethostbyname(target)
        if ip != target:
            print(f"[*] Resolved {target} to {ip}")
        return ip
    except socket.gaierror:
        print(f"[!] Could not resolve {target}")
        return None


def probe_port(ip, port, timeout=0.5):
    """Attempt a TCP connection to ip:port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except socket.error:
        return False


def scan_ports(ip, port_range, timeout=0.5):
    """Scan a range of ports on the target IP."""
    open_ports = []
    for port in port_range:
        if probe_port(ip, port, timeout):
            print(f"[+] Port {port} is open")
            open_ports.append(port)
    return open_ports


# ----- Toolkit menu functions -----

def run_subdomain_enum():
    """Gather input and run subdomain enumeration."""
    domain = input("Enter target domain: ").strip()
    wordlist_path = input("Enter wordlist path: ").strip()

    wordlist = load_wordlist(wordlist_path)
    if not wordlist:
        return

    results = enumerate_subdomains(domain, wordlist)
    print(f"\n[*] Found {len(results)} subdomain(s).")


def run_directory_enum():
    """Gather input and run directory enumeration."""
    target_url = input("Enter target URL (e.g., http://10.10.10.5): ").strip()
    wordlist_path = input("Enter wordlist path: ").strip()
    extension = input("Enter file extension (default: .html): ").strip() or ".html"

    wordlist = load_wordlist(wordlist_path)
    if not wordlist:
        return

    results = enumerate_directories(target_url, wordlist, extension)
    print(f"\n[*] Found {len(results)} valid path(s).")


def run_port_scan():
    """Gather input and run a port scan."""
    target = input("Enter target IP or hostname: ").strip()
    max_port_str = input("Enter max port to scan (default: 1024): ").strip() or "1024"

    try:
        max_port = int(max_port_str)
    except ValueError:
        print("[!] Invalid port number.")
        return

    ip = resolve_target(target)
    if not ip:
        return

    print(f"\n[*] Scanning {ip} (ports 1-{max_port})...\n")
    open_ports = scan_ports(ip, range(1, max_port + 1))

    if open_ports:
        common_services = {
            21: "FTP", 22: "SSH", 23: "Telnet",
            25: "SMTP", 53: "DNS", 80: "HTTP",
            443: "HTTPS", 445: "SMB", 3306: "MySQL",
            3389: "RDP", 8080: "HTTP Proxy"
        }
        print(f"\n{'Port':<10}{'Likely Service':<20}")
        print("-" * 30)
        for port in sorted(open_ports):
            service = common_services.get(port, "Unknown")
            print(f"{port:<10}{service:<20}")
    else:
        print("[!] No open ports found.")


def show_menu():
    """Display the toolkit menu."""
    print("\n" + "=" * 40)
    print("   Python Pentester Toolkit")
    print("=" * 40)
    print("  1. Subdomain Enumeration")
    print("  2. Directory Enumeration")
    print("  3. Port Scan")
    print("  4. Exit")
    print("=" * 40)


# ----- Main loop -----

def main():
    actions = {
        "1": run_subdomain_enum,
        "2": run_directory_enum,
        "3": run_port_scan,
    }

    while True:
        show_menu()
        choice = input("\nSelect an option: ").strip()

        if choice == "4":
            print("[*] Exiting toolkit. Goodbye.")
            break
        elif choice in actions:
            print()
            actions[choice]()
        else:
            print("[!] Invalid option. Enter 1-4.")


main()
