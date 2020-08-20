from subprocess import check_output, CalledProcessError
import json
import sys
import os

cache_fn = 'dns-cache.json'
hostname = sys.argv[1]

cache = {}

if os.path.exists(cache_fn):
    with open(cache_fn) as f:
        cache = json.load(f)

if hostname not in cache:
    try:
        raw = check_output(['powershell.exe', 'Resolve-DnsName ' + hostname + ' | ConvertTo-Json'])
    except:
        exit(1)
    data = json.loads(raw)
    for entry in data:
        if 'IP4Address' in entry:
            cache[hostname] = entry['IP4Address']
            break

if hostname not in cache:
    exit(1)

print(cache[hostname])

with open(cache_fn, 'w') as f:
    json.dump(cache, f)