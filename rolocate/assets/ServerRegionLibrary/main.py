import requests
import time
import re

INPUT_FILE = "input.txt"
OUTPUT_JS = "serverregion.js"

with open(INPUT_FILE, "r") as file:
    content = file.read()

ips = [ip.strip().replace('"','') for ip in content.replace("[","").replace("]","").split(",") if ip.strip()]
unique_ips = list(dict.fromkeys(ips))
print(f"Found {len(unique_ips)} unique IPs in input file.")

with open(OUTPUT_JS, "r", encoding="utf-8") as file:
    js_content = file.read()

existing_ips = set(re.findall(r'"(\d+\.\d+\.\d+\.\d+)"\s*:', js_content))
print(f"Found {len(existing_ips)} existing IPs in {OUTPUT_JS}.")

ips_to_add = [ip for ip in unique_ips if ip not in existing_ips]
print(f"{len(ips_to_add)} new IPs will be queried and added.")

def format_js_entry(ip, info):
    entry = f'"{ip}": {{ city: "{info.get("city")}", country: {{ name: "{info["country"]["name"]}", code: "{info["country"]["code"]}" }}'
    if "region" in info:
        entry += f', region: {{ name: "{info["region"]["name"]}", code: "{info["region"]["code"]}" }}'
    entry += f', latitude: {info.get("latitude")}, longitude: {info.get("longitude")} }},\n'
    return entry

new_entries = {}

for count, ip in enumerate(ips_to_add, start=1):
    while True:
        try:
            print(f"[{count}/{len(ips_to_add)}] Fetching {ip}...")
            response = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,region,city,lat,lon"
            )
            data = response.json()

            if data.get("status") == "success":
                entry = {
                    "city": data.get("city"),
                    "country": {
                        "name": data.get("country"),
                        "code": data.get("countryCode")
                    },
                    "latitude": data.get("lat"),
                    "longitude": data.get("lon")
                }
                if data.get("regionName") and data.get("region"):
                    entry["region"] = {
                        "name": data.get("regionName"),
                        "code": data.get("region")
                    }
                new_entries[ip] = entry
                print(f"Added {ip}: {entry}")
                time.sleep(1.3)  # small delay to be safe
                break

            elif data.get("message") == "rate limited":
                print("Rate limit hit! Waiting 60 seconds...")
                time.sleep(60)  # wait and retry
            else:
                print(f"Failed for {ip}: {data.get('message')}")
                break

        except Exception as e:
            print(f"Error for {ip}: {e}")
            time.sleep(5)  # small retry delay

js_new_entries = ""
for ip, info in new_entries.items():
    js_new_entries += format_js_entry(ip, info)

js_content = re.sub(r'(window\.serverRegionsByIp\s*=\s*{)', r'\1\n' + js_new_entries, js_content, count=1)

with open(OUTPUT_JS, "w", encoding="utf-8") as file:
    file.write(js_content)

print(f"Updated {OUTPUT_JS} with {len(new_entries)} new IP entries.")