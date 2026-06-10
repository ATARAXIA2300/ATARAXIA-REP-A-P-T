import dns.resolver
import requests
import argparse
import os
import pyfiglet
import time
from faker import Faker
import re
import whois
import time

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
     blacklist_urls = ["https://api."]
     url = args.URL
     print(f"\nStarting information gathering on {url}...")
     if "api" in url:
         print(f"\nThe target: {url}, is an API, so i can't scan it because it will be an attack or massive scansion to a API.")
         blacklist_urls.append(url)
     time.sleep(2)
     regex_emails = r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
     regex_html_title = r"<title>(.*?)</title>"
     regex_hashes = r"(?<![a-zA-Z0-9])[a-fA-F0-9]{32}(?![a-zA-Z0-9])|(?<![a-zA-Z0-9])[a-fA-F0-9]{40}(?![a-zA-Z0-9])|(?<![a-zA-Z0-9])[a-fA-F0-9]{64}(?![a-zA-Z0-9])|(?<![a-zA-Z0-9])[a-fA-F0-9]{128}(?![a-zA-Z0-9])"
     headers = {
         "User-Agent": user_agent,
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
         "Content-Type": "application/x-www-form-urlencoded"
     }
     options_resp = requests.options(url, headers=headers, allow_redirects=True, timeout=10)
     print(f"\nHTTP Methods: {options_resp.headers.get('Allow')}")
     response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
     redirects = [response.url for response in response.history]
     final_url = response.url
     try:
      w = whois.whois(url)
      print(f"\nWHOIS: {w}")
     except whois.exceptions.WhoisDomainNotFoundError:
         print("\nWHOIS: Domain not found!")
     print(f"\nServer: {response.headers.get('Server')}")
     print(f"\nX-Powered-By: {response.headers.get('X-Powered-By')}")
     print(f"\nSet-Cookie: {response.headers.get('Set-Cookie')}")
     print(f"\nEmails: {re.findall(regex_emails, response.text)}")
     print(f"\nHashes / CMS Fingerprints: {re.findall(regex_hashes, response.text)}")       
     print(f"\nTitle: {re.findall(regex_html_title, response.text)}")
     print(f"\nStatus Code: {response.status_code}")
     print(f"\nWebsite Headers: {response.headers}")
     print(f"\nRequest Headers: {response.request.headers}")
     print(f"\nEncoding: {response.encoding}")
     print(f"\nHTTP Version: {response.raw.version}")
     print(f"\nHTTP Reason: {response.status_code} {response.reason}")
     print(f"\nRedirects: {redirects} --> Final URL: {final_url}")
     if "cloudflare" in response.headers or "cf-ray" in response.headers:
         print("\nCDN Detected: Cloudflare!")
     elif "AkamaiGHost" in response.headers or "X-Cache-Remote" in response.headers:
         print("\nCDN Detected: Akamai!")
     elif "fastly" in response.headers or "X-Served-By" in response.headers:
         print("\nCDN Detected: Fastly!")
     else:
         print("\nNo CDN Detected!")
     if "<!DOCTYPE html>" in response.text:
         print("\nThe target is using HTML5")
     elif """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" ...>""" in response.text:
          print("\nThe target is using XHTML 1.0 (Today is deprecated)")
     elif """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">""" in response.text:
         print("\nThe target is using HTML 4.01 (Today is deprecated)")
     elif """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">""" in response.text:
         print("\nThe target is using HTML 2.0 (Today is deprecated)")
     elif """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">""" in response.text:
         print("\nThe target is using XHTML 1.1 (Today is deprecated)")
     else:
         print("\nI couldn't detect the html version of the target.")
     

     scoring = 0

     if "wixstatic" in url or "wixsite" in url or """<meta name="generator" content="Wix.com Website Builder">""" in response.text:
         scoring += 1.5
         if scoring == 1.5:
             print(f"\nThe target is using Wix! | Scoring: {str(scoring)}")
         else:
             if scoring == 0:
                 print(f"\nThe target is not using Wix! | Scoring: {str(scoring)}")
                 
     
     elif "wp-content" in response.text or "wp-admin" in response.text:
         scoring += 0.7
         print(f"\nThe target has the keywords: wp-content / wp-admin in the HTML structure! | Scoring: {str(scoring)}")
         response = requests.get(url + "/wp-json", headers=headers, allow_redirects=True, timeout=10)
         if response.status_code in (200, 403, 401, 426):
          scoring += 1
          print(f"\nThe target has a WordPress has a wp-json page! | URL: {url}/wp-admin | Status Code: {response.status_code} | Scoring: {str(scoring)}")
         if scoring > 1.5 or scoring > 1.6:
             print(f"\nThe target is using WordPress! | Scoring: {str(scoring)}")
         elif scoring == 0.7 or scoring == 1:
             print(f"\nTarget may be using WordPress, but is not sure yet | Scoring: {str(scoring)}")
         else:
             if scoring == 0:
                 print(f"\nThe target is not using WordPress! | Scoring: {str(scoring)}")
             
     elif "Joomla" in response.text:
         scoring += 0.5
         print(f"\nThe target has the keyword: Joomla in the HTML structure! | Scoring: {str(scoring)}")
         response = requests.get(url + "/administrator", headers=headers, allow_redirects=True, timeout=10)
         if response.status_code in (200, 403, 401, 426, 301, 302):
          scoring += 1.5
          print(f"\nThe target has a Joomla login page! | URL: {url}/administrator | Status Code: {response.status_code} | Scoring: {str(scoring)}")
          print(f"\nThe target is using Joomla! | Scoring: {str(scoring)}")
         else:
             if response.status_code in (404, 410):
                 scoring -= 0.2
                 print(f"\nThe target has not a Joomla login page! | URL: {url}/administrator | Status Code: {response.status_code} | Scoring: {str(scoring)}")
             else:
                      if scoring == 0.3:
                       print(f"\nTarget may be using Joomla, but is not sure yet | Scoring: {str(scoring)}")
                      else:
                          if scoring == 0:
                              print(f"\nThe target is not using Joomla! | Scoring: {str(scoring)}")
         
     elif "Drupal" in response.text:
         scoring += 0.4
         print(f"\nThe target has the keyword: Drupal in the HTML structure! | Scoring: {str(scoring)}")
         response = requests.get(url + "/core/", headers=headers, allow_redirects=True, timeout=10)
         if response.status_code in (200, 403, 401):
          scoring += 1.2
          if scoring == 1.6:
           print(f"\nThe target has a Drupal directory core! | URL: {url}/core/ | Status Code: {response.status_code} | Scoring: {str(scoring)}")
           print(f"\nThe target is using Drupal! | Scoring: {str(scoring)}")
          elif scoring == 0.4:
              print(f"\nTarget may be using Drupal, but is not sure yet | Scoring: {str(scoring)}")
          else:
              if scoring == 0:
                  print(f"\nThe target is not using Drupal! | Scoring: {str(scoring)}")
     else:
         if scoring == 0:
          print(f"\nThe target is not using WordPress, Joomla or Drupal | Scoring: {str(scoring)}")
     previous_hash = set()
     while True:
         response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
         current_hash = set(re.findall(regex_hashes, response.text))
         if previous_hash and current_hash != previous_hash:
              print(f"\nHTML structure has changed! (probably anti-scraping / anti-bot detected!) | NEW HASHES: {current_hash - previous_hash} | OLD HASHES: {previous_hash - current_hash}")
              previous_hash = current_hash
              user_input = input("\nDo you want to continue? (y/n): ")
              if user_input.lower() == "n":
                  print("\nOk, exiting...")
                  break
              elif user_input.lower() == "y":
                  print("\nOk, continuing...")
                  continue
         else:
             print("\nOk, No HTML structure changes detected!")
             previous_hash = current_hash
             user_input = input("\nDo you want to continue? (y/n): ")
             if user_input.lower() == "n":
                   print("\nOk, exiting...")
                   break
             elif user_input.lower() == "y":
                   print("\nOk, continuing...")
                   continue
         time.sleep(25)