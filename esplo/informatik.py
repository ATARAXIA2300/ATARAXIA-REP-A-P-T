import dns.resolver
import requests
import argparse
import os
import pyfiglet
import time
from faker import Faker
import re
import whois

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
parser.add_argument('-info', '--information', help='this is used for studying the target and collecting information about it like http methods, banner grabbing, http probing, etc. - INFORMATION')
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
                         print(f"\nYou have to upgrade your request to HTTPS or use HTTP/2. Another reason: your HTTP version is not supported: {full_url} | Status code: {response.status_code}")

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
elif args.information and args.URL:
     url = args.URL
     print(f"\nStarting information gathering on {url}...")
     time.sleep(2)
     regex_emails = r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
     regex_links = r"https?://[^\s\"'<>]+"
     regex_html_title = r"<title>(.*?)</title>"
     headers = {
         "User-Agent": user_agent,
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
         "Content-Type": "application/x-www-form-urlencoded"
     }
     options_resp = requests.options(url, headers=headers, allow_redirects=True, timeout=10)
     print(f"\nHTTP Methods: {options_resp.headers.get('Allow')}")
     response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
     w = whois.whois(url)
     print(f"\nWHOIS: {w}")
     print(f"\nServer: {response.headers.get('Server')}")
     print(f"\nX-Powered-By: {response.headers.get('X-Powered-By')}")
     print(f"\nSet-Cookie: {response.headers.get('Set-Cookie')}")
     print(f"\nEmails: {re.findall(regex_emails, response.text)}")
     print(f"\nLinks: {re.findall(regex_links, response.text)}")
     print(f"\nTitle: {re.findall(regex_html_title, response.text)}")
     print(f"\nStatus Code: {response.status_code}")
     print(f"\nWebsite Headers: {response.headers}")
     print(f"\nRequest Headers: {response.request.headers}")
     print(f"\nEncoding: {response.encoding}")
     print(f"\nHTTP Version: {response.raw.version}")
     print(f"\nHTTP Reason: {response.status_code} {response.reason}")
     if "<!DOCTYPE html>" in response.text:
         print("\nThe target is using HTML5")
     elif """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" ...>""" in response.text:
          print("\nThe target is using XHTML")
     elif """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">""" in response.text:
         print("\nThe target is using HTML 4.01 (Today is deprecated)")
     elif """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN""" in response.text:
         print("\nThe target is using HTML 4.01 Transitional (Today is deprecated)")
     else:
         print("\nI couldn't detect the html version of the target.")
     
     if "wp-content" in response.text or "wp-admin" in response.text:
         print("\nThe target is using WordPress!")
     elif "Joomla" in response.text:
         print("\nThe target is using Joomla!")
     elif "Drupal" in response.text:
         print("\nThe target is using Drupal!")
     else:
         print("\nThe target is not using WordPress, Joomla or Drupal.")