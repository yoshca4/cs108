import requests
from collections import deque
import time

API     = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "cs108-lab/1.0 (cs108@wallawalla.edu)"}

START  = "Octopus"
TARGET = "Subnautica 2"
MAX_LINKS = 20       # links to follow per page
MAX_DEPTH = 5        # give up after this many hops

def get_links(title):
    params = {
        "action": "query", "titles": title,
        "prop": "links", "pllimit": MAX_LINKS,
        "plnamespace": 0, "format": "json",
    }
    resp = requests.get(API, params=params, headers=HEADERS, timeout=10)
    if not resp.text.strip():
        print(f"  [warn] empty response for '{title}', skipping")
        return []
    page = next(iter(resp.json()["query"]["pages"].values()))
    return [lnk["title"] for lnk in page.get("links", [])]

# BFS: each entry is (current_title, path_so_far)
queue   = deque([(START, [START])])
visited = {START}

while queue:
    current, path = queue.popleft()
    if len(path) > MAX_DEPTH:
        print(f"Gave up — no path within {MAX_DEPTH} hops.")
        break

    print(f"Exploring: {current}  (depth {len(path)})")
    time.sleep(1)

    for link in get_links(current):
        if link == TARGET:
            full_path = path + [link]
            print(f"\nFound in {len(full_path)-1} hop(s):")
            for i, step in enumerate(full_path):
                print(f"  {'→ ' * i}{step}")
            exit()

        if link not in visited:
            visited.add(link)
            queue.append((link, path + [link]))

print("No path found.")