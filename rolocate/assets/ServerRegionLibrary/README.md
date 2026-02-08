# Tools Used by RoLocate to Find Server Regions on Roblox

## How It Works

1. A modified version of **RoLocate** scans Roblox servers at a rate of ~2000 servers per minute.  
   - In the official build, this scanning code is commented out.  
   - Userscripts can bypass most rate limits by using `GM_xmlhttpRequest`, making the scan very fast.

2. The discovered server IPs are compared against `serverregion.js`.

3. Any unmatched (unknown) server IPs are collected into a list.

4. This list of unknown IPs is saved to `input.txt`.

5. `main.py` is executed to determine the regions of the unknown servers.

6. Once found, `main.py` automatically updates `serverregion.js` with the new server region data.

