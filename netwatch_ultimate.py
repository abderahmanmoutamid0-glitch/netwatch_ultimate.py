#!/usr/bin/env python3
# =========================================
# Tool Name : NetWatch ULTIMATE
# Version   : 3.0
# Type      : Network Scan & Monitoring
# =========================================

import socket, threading, time, json
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

NETWORK_PREFIX = "192.168.1."
START_IP = 1
END_IP = 254
COMMON_PORTS = [21, 22, 80, 443]
CHECK_INTERVAL = 10

LOG_FILE = "netwatch.log"
JSON_FILE = "results.json"

online_hosts = set()
results = {}
lock = threading.Lock()

def banner():
    print(Fore.CYAN + """
███╗   ██╗███████╗████████╗██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗
████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║███████║   ██║   ██║     ███████║
██║╚██╗██║██╔══╝     ██║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║
██║ ╚████║███████╗   ██║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║
╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝

NetWatch ULTIMATE v3.0
Authorized Use Only
""")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} | {msg}\n")

def save_json():
    with open(JSON_FILE, "w") as f:
        json.dump(results, f, indent=4)

def is_online(ip):
    try:
        socket.gethostbyaddr(ip)
        return True
    except:
        return False

def scan_ports(ip):
    open_ports = []
    for p in COMMON_PORTS:
        try:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0:
                open_ports.append(p)
            s.close()
        except:
            pass
    return open_ports

def check_ip(ip):
    global results
    if is_online(ip):
        with lock:
            if ip not in online_hosts:
                online_hosts.add(ip)
                ports = scan_ports(ip)
                print(Fore.GREEN + f"[+] ONLINE {ip} | Ports {ports}")
                log(f"ONLINE {ip} Ports {ports}")
                results[ip] = {"ports": ports, "time": str(datetime.now())}
                save_json()
    else:
        with lock:
            if ip in online_hosts:
                online_hosts.remove(ip)
                print(Fore.RED + f"[-] OFFLINE {ip}")
                log(f"OFFLINE {ip}")

def network_monitor():
    print(Fore.YELLOW + "[*] Live monitoring started...\n")
    while True:
        threads = []
        for i in range(START_IP, END_IP + 1):
            ip = NETWORK_PREFIX + str(i)
            t = threading.Thread(target=check_ip, args=(ip,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        time.sleep(CHECK_INTERVAL)

def domain_scan():
    domain = input("Domain/IP: ")
    try:
        ip = socket.gethostbyname(domain)
        print(Fore.GREEN + f"[+] Resolved IP: {ip}")
        ports = scan_ports(ip)
        print(Fore.CYAN + f"Open Ports: {ports}")
    except:
        print(Fore.RED + "Failed to resolve")

def menu():
    print(Fore.MAGENTA + """
[1] Live Network Monitoring
[2] Scan Domain / IP
[3] Show Saved Results
[0] Exit
""")

def main():
    banner()
    while True:
        menu()
        c = input(Fore.YELLOW + "NetWatch > ")
        if c == "1":
            network_monitor()
        elif c == "2":
            domain_scan()
        elif c == "3":
            print(json.dumps(results, indent=4))
        elif c == "0":
            break
        else:
            print("Invalid")

if __name__ == "__main__":
    main()
