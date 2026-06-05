import pyfiglet
import requests
import threading

red = '\033[31m'
banner = pyfiglet.figlet_format("Caesar", font="shadow")
print(red + banner)
print("\nWeb Scanner Framework")
url = input("\nEnter URL: ")

if url == "":
    print("\nPlease enter a URL.")
    exit()

r = requests.options(url, verify=True)
hd = r.headers.get("Allow")
server = r.headers.get("Server")
cors = r.headers.get("Access-Control-Allow-Methods")
print(f"\nAllowed Methods (HTTP Standard): {hd}")
print(f"\nServer: {server}")
print(f"\nCORS (Methods): {cors}")

print("-"*30)

admin_panels = [
  "/admin",
  ":10000",
  "/wp-admin",
  "wp-admin.php",
  "/login",
  "/administrator",
  ":2082",
  "/wp-login",
  "/wp-login.php",
  ":2083",
  ":2086",
  ":2087",
  "/login_up.php",
  "/login.php",
  "/virtualmin",
  "/user/login",
  ":8099",
  ":8083"
]

print("\nChecking for admin panels...")

for panel in admin_panels:
    pnl = requests.get(url + panel, verify=True)
    if pnl.status_code in (200, 301, 302, 403):
         print(f"\nAdmin panel found: {url}{panel}")
    else:
        print(f"\nAdmin panel not found: {url}{panel}")