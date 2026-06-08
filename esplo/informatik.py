import dns.resolver
import requests
import argparse
import os
import pyfiglet
import time
from faker import Faker
import random
import socket
import threading

fake = Faker()
user_agent = fake.user_agent()

green = "\033[32m"

ascii_banner = pyfiglet.figlet_format("INFOTIK")

print(green + ascii_banner)

parser = argparse.ArgumentParser(prog='INFOTIK', description='A tool for subdomain enumeration, HTTP directory discovery and more (about web)')
parser.add_argument('-u', '--URL', help='HTTP domain to scan - ENUMERATION')
parser.add_argument('-wu', '--wordlist-url', help='HTTP wordlist URL')
parser.add_argument('-d', '--domain', help='Domain for subdomain enumeration to scan')
parser.add_argument('-wd', '--wordlist-domain', help='DNS wordlist URL for subdomain enumeration - ENUMERATION')
parser.add_argument('-recon', '--reconnaissance', help='this is used for studying the target and collecting information about it (e.g. port scanning, OSINT, etc.) and you have to use the flag --> "-d" (e.g www.example.com) and above all specify "www" in the domain - INFORMATION GATHERING')
args = parser.parse_args()
if args.URL and args.wordlist_url:
    url = args.URL
    wordlist = args.wordlist_url
    print(f"\nStarting HTTP directory discovery on {url} with wordlist {wordlist}...")
    time.sleep(2)
    if os.path.exists(wordlist):
        with open(wordlist, 'r') as f:
           for line in f:
                line = line.strip()
                if line:
                    full_url = url + '/' + line
                    headers = {
                      "User-Agent": user_agent,
                      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                      "Content-Type": "application/x-www-form-urlencoded"
                    }
                    response = requests.get(full_url, headers=headers, allow_redirects=True, timeout=10)
                    redirects = [response.url for response in response.history]
                    final_url = response.url
                    if response.status_code in (200, 301, 302, 403, 401, 201):
                         print(f"\nFound: {full_url} | Status Code: {response.status_code} | Any Redirects: {redirects} --> Final URL: {final_url}")
                    elif response.status_code in (426, 505):
                         print(f"\nYou have to upgrade your request to HTTPS or use HTTP/2 or your HTTP version is not supported: {full_url} | Status code: {response.status_code}")

                    else:
                        print(f"\nNot Found: {full_url} | Status Code: {response.status_code} | Any Redirects: {redirects} --> Final URL: {final_url}")
    else:
        print(f"Wordlist file not found: {wordlist}!")
        exit()
elif args.domain and args.wordlist_domain:
     domain = args.domain
     wordlist = args.wordlist_domain
     print(f"\nStarting subdomain enumeration on {domain} with wordlist {wordlist}...")
     time.sleep(2)
     if os.path.exists(wordlist):
          with open(wordlist, 'r') as f:
               for line in f:
                    line = line.strip()
                    if line:
                         subdomain = line + '.' + domain
                         try:
                             answers = dns.resolver.resolve(subdomain, 'A')
                             for rdata in answers:
                                 print(f"\nFound: {subdomain} | IP: {rdata}")
                         except dns.resolver.NoAnswer:
                             print(f"\nNot found: {subdomain}")
                         except dns.resolver.NXDOMAIN:
                             print(f"\nNot found: {subdomain}")
                         except dns.resolver.Timeout:
                             print(f"\nTimeout: {subdomain}")
                         except dns.resolver.NoNameservers:
                             print(f"\nNo nameservers for {subdomain}")
elif args.reconnaissance and args.domain:
     web = args.reconnaissance
     print(f"\nStarting reconnaissance on {web}")
     domain = args.domain
     threads = []
     ip = socket.gethostbyname(domain)
     print(f"\nIP address of {domain}: {ip}")
     time.sleep(2)
     try:
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         sock.settimeout(2)
         for port in range(1, 3306):
          result = sock.connect_ex((ip, port))
          if result == 0:
               print(f"\nPort {port} is open")
          elif result in (111, 10061):
              print(f"\nPort {port} is closed")
          elif result == 110:
              print(f"\nPort {port} is filtered / timeout")
          t = threading.Thread(target=sock.connect_ex, args=((ip, port),))
          threads.append(t)
          t.start()
         for t in threads:
             t.join()
     except socket.timeout as e:
          print(f"\nTarget timeout: {e}")
          pass