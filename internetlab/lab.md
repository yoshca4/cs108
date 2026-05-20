# CS 108 Lab — Daily Dose of Internet: Scraping, Graphs, and the Live Web

**Name:** _______________________________ **Date:** _____________

---

## Submission

> Submit only [OBSERVE] questions. Do not submit [REFLECT]s!!

---

## Overview

The internet is not just a place you visit — it is a data source you can query, traverse,
and visualize. Every Reddit post, every Wikipedia article, every Hacker News upvote is
a number waiting to be turned into a picture.

In this lab you will build five models that reach into the live web and pull something
back:

1. **Reddit Word Cloud** — scrape a subreddit's hot posts, visualize word frequency
2. **Wikipedia Link Graph** — follow links N levels deep, draw the structure
3. **Wikipedia Degrees of Separation** — find the shortest path between any two articles
4. **Hacker News Pulse** — chart score vs. comment count for today's top stories

No API keys required. All models use only public, anonymous endpoints.

**Install once:**

```bash
uv add requests beautifulsoup4 wordcloud matplotlib networkx
```

---

## Part 1: Reddit Word Cloud

### Background

Reddit exposes a read-only JSON feed for any subreddit at:

```
https://www.reddit.com/r/TOPIC/hot.json
```

No account, no OAuth. You just need to set a `User-Agent` header so Reddit knows
something is making the request. Pull the post titles, strip common words
(**stop words**), and count what is left. The result is a **word cloud**: words that
appear more often are drawn larger.

Word clouds are crude — they discard grammar and context — but they are surprisingly
good at answering the question *"what is this community talking about right now?"*

### The Code

Save as `wordcloud_reddit.py`:

```python
import requests
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

SUBREDDIT = "technology"          # ← change this
LIMIT     = 50                    # posts to fetch (max 100)
HEADERS   = {"User-Agent": "cs108-lab/1.0"}

url  = f"https://www.reddit.com/r/{SUBREDDIT}/hot.json?limit={LIMIT}"
resp = requests.get(url, headers=HEADERS)
data = resp.json()

titles = [post["data"]["title"] for post in data["data"]["children"]]
text   = " ".join(titles)

extra_stops = {"r", "u", "amp", "x200b", "just", "like", "new", "get"}
stops = STOPWORDS | extra_stops

wc = WordCloud(
    width=1200, height=600,
    background_color="white",
    stopwords=stops,
    max_words=80,
    colormap="plasma",
).generate(text)

plt.figure(figsize=(14, 7))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.title(f"r/{SUBREDDIT} — hot right now", fontsize=16)
plt.tight_layout()
plt.savefig("wordcloud.png", dpi=150)
plt.show()
print("Saved wordcloud.png")
```

Run it:

```bash
python wordcloud_reddit.py
```

**[OBSERVE1]** What are the three biggest words in your word cloud? Do they match
what you would have guessed before running the script?

&nbsp;

&nbsp;

**[OBSERVE2]** Change `SUBREDDIT` to a completely different community — try something
like `"cooking"`, `"dataisbeautiful"`, or `"wallawalla"`. Save both images. Do the
vocabularies overlap at all, or do they look like different languages?

&nbsp;

&nbsp;

**[REFLECT]** The word cloud drops the *structure* of language — it cannot tell
that "not good" and "very good" both contain "good". What would you lose and what
would you gain if you counted **two-word phrases** (bigrams) instead of single words?

&nbsp;

&nbsp;

---

## Part 2: Wikipedia Link Graph

### Background

Every Wikipedia article links to other Wikipedia articles. If you follow those links,
then follow *their* links, and keep going, you trace out a web of related concepts.
Visualized as a graph, this structure is often beautiful and always surprising —
topics you thought were unrelated turn out to share many neighbors.

### The Tool

Instead of a static Python plot, this model uses an **interactive browser-based explorer**
built with D3. Open the file `wiki.html` (included with this lab) directly in
your browser — no Python, no install needed for this part.

```
open wiki_explorer.html       # macOS
start wiki_explorer.html      # Windows
xdg-open wiki_explorer.html   # Linux
```

**What you can do:**

- Type any Wikipedia article name in the seed field and click **Crawl**
- **Click any node** to see its Wikipedia summary, incoming/outgoing link counts, and depth in the panel on the right
- **Click "+ Expand this node"** to grow the graph outward from any leaf node — without re-running the whole crawl
- **Drag nodes** to rearrange the layout
- **Scroll/pinch** to zoom in and out
- Click **↗ Open in Wikipedia** to jump to the actual article

Node colors encode role: blue = seed or expanded, purple = second-level, dark = unexpanded leaf, gold = currently selected.

**[OBSERVE3]** Name two articles that appear in your graph that you would not have
predicted from the seed (start) article. Open the wikipedia page and observe the context. 
Does the connection make sense in hindsight?

&nbsp;

&nbsp;

**[OBSERVE4]** Change `SEED` to an abstract concept like `"Democracy"` or
`"Entropy"`. How does the graph's shape/structure differ from a concrete noun like `"Octopus"`?
Describe the difference.

&nbsp;

&nbsp;

**[REFLECT]** The graph you drew is *directed* — an edge from A to B doesn't mean B
links back to A. What would it mean about a Wikipedia article if it had many incoming
edges but few outgoing ones?

&nbsp;

&nbsp;

---

## Part 3: Wikipedia Degrees of Separation

### Background

There is a popular claim that any two Wikipedia articles are connected within a small
number of clicks. This model tests it directly using **breadth-first search (BFS)**:
starting from one article, expand layer by layer until you reach the other.

BFS guarantees the *shortest* path. The number of edges in that path is the
"degrees of separation" between the two articles.

### The Code

Save as `bfs.py`:

```python
import requests
from collections import deque
import time

API     = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "cs108-lab/1.0 (cs108@wallawalla.edu)"}

START  = "Walla Walla, Washington"
TARGET = "Ancient Rome"
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
    time.sleep(0.1)

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
```

Run it:

```bash
python wiki_bfs.py
```

**[OBSERVE5]** How many hops did BFS find between your two articles? Write out
the full path:

&nbsp;

&nbsp;

**[OBSERVE6]** Change `START` and `TARGET` to two topics you personally find
unrelated — try a local place and an ancient civilization, or a sport and a
scientific concept. How many hops? Is the connecting article surprising?

&nbsp;

&nbsp;

**[REFLECT]** BFS explores articles in order of distance from the start.
What would change — in the path found and in the time taken — if you used
depth-first search instead?

&nbsp;

&nbsp;

---

## Part 4: Hacker News Pulse

### Background

Hacker News (HN) is a tech news aggregator. Its API is completely open and returns
clean JSON. Each story has a **score** (upvotes) and a **comment count** — two
independent signals. A story with high score but few comments might be
beautiful or fascinating but not controversial. A story with many comments but low
score might be contentious.

Plotting score vs. comments as a scatter plot reveals this structure at a glance.

### The Tool

Open `pulse.html` (included with this lab) directly in your browser — no Python needed.

```
open hn_pulse.html       # macOS
start hn_pulse.html      # Windows
xdg-open hn_pulse.html   # Linux
```

**What you can do:**

- Choose a feed: **Top**, **New**, **Best**, **Ask HN**, or **Show HN** — each has a different character
- Fetch 30, 50, or 75 stories at once
- **Click any dot** to see full story details in the sidebar: score, comments, comment/score ratio, author, age, and relative bar charts
- Switch the **color encoding** between age, score, or comments/score ratio to see different patterns
- **Hover** any dot for a quick tooltip
- **Click a domain bar** at the bottom to highlight only stories from that site
- Click **↗ HN thread** or **↗ Article** to open the real links

The dashed diagonal is the `score = comments` line. Stories above it are discussion-heavy; stories below are popular but quiet. Quadrant labels in each corner name the pattern.

**[OBSERVE7]** Find a story that is far above the dashed diagonal line (many more
comments than its score would predict). Read its title. What kind of story tends
to generate this pattern?

&nbsp;

&nbsp;

**[OBSERVE8]** Find a story that is far below the diagonal (high score, few
comments). What kind of content produces that pattern?

&nbsp;

&nbsp;

**[REFLECT]** Score and comment count are both proxies for "importance." Do they
measure the same thing? Can you think of a story type where the two signals would
point in opposite directions?

&nbsp;

&nbsp;

---

## 2nd Overview

The internet is not a collection of documents — it is a collection of
*relationships*. Every film leads to its cast. Every cast member leads to
other films. Every musician is connected to bandmates, influences, and
collaborators. Every concept in human knowledge is linked to other concepts
by a web of typed, labeled relationships stretching back centuries.

In this lab you will build three tools that let you navigate those
relationships directly, one click at a time. Each tool uses a different
knowledge source and a different definition of "connection" — but all
three share the same interaction model: start with a seed, expand outward,
follow what surprises you.

1. **Movie/TV Graph** — cast and crew connections via The Movie Database (TMDB)
2. **Music Artist Graph** — artist relationships via MusicBrainz (no key needed)
3. **Wikidata Entity Graph** — structured knowledge relationships via Wikidata

All three run entirely in the browser. Open each HTML file directly:

```
open tv_graph.html
open music_graph.html
open wikidata_graph.html
```

---

## Part 5: TV Connection Graph

### Background

The **six degrees of Kevin Bacon** game is based on a real phenomenon: the
Hollywood cast network is surprisingly small and tightly connected. Any two
actors can typically be linked through fewer than six shared productions. This is
a property of **small-world networks** — graphs where most nodes are not
directly connected, but can be reached in a small number of steps through
a handful of highly-connected hubs.

This tool uses **TVmaze**, a free and fully open TV database — no account,
no API key, no setup required. Each show expands to its top cast members;
each cast member expands to their other shows, sorted by rating. The graph is
**bipartite** — edges only connect shows to people, never show-to-show
or person-to-person directly. Show node size encodes rating; color encodes
primary genre.

### The Tool

Open `tv_graph.html`. Enter any TV show or actor name and click **Start**.
The tool fetches the top cast of the seed show (or top credits of the seed
actor) and draws the initial graph. Click any node to see details in the
sidebar. Click **+ Expand this node** to grow the graph from that point.

**[OBSERVE9]** Start with any TV show/Actor you have seen recently. After a few expansions, 
name two shows or actors you did not expect to be connected to your starting point.

&nbsp;

&nbsp;


**[OBSERVE10]** Look at the sidebar when a show node is selected. The rating,
network, and genre appear. Find the highest-rated show in your graph and
the lowest-rated show. Are they connected directly (sharing a cast member),
or are they in different parts of the graph?

&nbsp;

&nbsp;

**[REFLECT]** The graph only shows the top 10 cast members per show and the
top 7 show credits per person, sorted by rating. What kinds of people are
systematically excluded by this cutoff? What would the graph look like if
you used writers or directors instead of cast members as the connecting nodes?

&nbsp;

&nbsp;

---

## Part 6: Music Artist Graph

### Background

**MusicBrainz** is a community-maintained open music encyclopedia — think
Wikipedia, but exclusively for music metadata. It stores not just artist
names and albums, but *relationships* between artists: who was a member
of which band, who influenced whom, who collaborated with whom, who is
a tribute act for whom.

These relationships are typed and directional. "Influenced by" is
different from "member of band" is different from "collaboration." This
richness makes the MusicBrainz graph semantically meaningful in a way that
simple co-occurrence graphs are not — each edge tells you *how* two artists
are connected, not just *that* they are.

No API key is required. MusicBrainz is fully public. The tool includes a
150ms delay between requests to be a polite API citizen.

### The Tool

Open `music_graph.html`. Enter any artist name and click **Start**.
The initial graph shows the seed artist and all their direct
MusicBrainz relationships. Node color encodes genre (orange = rock,
pink = pop, purple = electronic, etc.). Click any node to see its full
metadata; expand to grow the graph further.

**[OBSERVE11]** Start with a band you know well. Look at the relationship
types shown in the sidebar when you click the seed node. List all the
distinct relationship types that appear. Check out some other bands. 
List a few of the relationships you notice. Which type is most common?

&nbsp;

&nbsp;


**[OBSERVE12]** Expand two or three nodes outward from your seed artist.
Do you notice any **genre clusters** forming — groups of nodes with
similar colors that are densely connected to each other but sparsely
connected to the rest of the graph? Describe one cluster or pattern you can identify.

&nbsp;

&nbsp;

**[REFLECT]** MusicBrainz is maintained by volunteers who add and edit
relationships manually. What kinds of artists or musical traditions are
likely to be underrepresented or have sparse relationship data? What does
that say about whose musical history gets preserved in structured form?

&nbsp;

&nbsp;

---

## Part 7: Wikidata Entity Graph

### Background

**Wikidata** is the structured data backbone of Wikipedia. Where Wikipedia
stores knowledge as prose, Wikidata stores it as **triples**: subject →
property → value. For example:

```
Marie Curie → educated at → University of Paris
Marie Curie → field of work → chemistry
Marie Curie → award received → Nobel Prize in Physics
Nobel Prize in Physics → instance of → Nobel Prize
```

Every entity has a **QID** (like `Q7186` for Marie Curie) and potentially
hundreds of typed property-value pairs. When a value is itself a Wikidata
entity, it can be clicked to expand the graph further. This creates an
infinitely traversable knowledge graph covering every person, place,
concept, and work that Wikipedia covers — but with explicit, labeled
relationships instead of hyperlinks.

The **Properties** dropdown lets you choose how many property types to
fetch: *Core* is fast (9 properties), *Rich* covers ~30 of the most
interesting ones.

### The Tool

Open `wikidata_graph.html`. Enter any person, place, concept, or creative
work and click **Start**. The graph appears with the seed entity at center
and its directly connected entities as nodes. Click any node to see its
full property list in the sidebar. Click any property value that is
highlighted in green to jump to that entity; click **+ Expand** to pull
all of its connections into the graph.

**[OBSERVE13]** Start with a scientist or historical figure. After the
initial graph loads, look at the sidebar properties. List three properties
or connections and their values that you find most surprising or that 
you did not already know. For each one, note what type of value it is.

&nbsp;

&nbsp;

**[OBSERVE14]** Try starting with an abstract concept rather than a person —
try `photosynthesis`, `democracy`, `jazz`, or `black hole`. How does the
graph structure differ from a person-seed graph? Are the relationships more
hierarchical (chains of `subclass of`) or more lateral (many different
property types)?

&nbsp;

&nbsp;

**[REFLECT]** Wikidata relationships are added by human editors and reflect
editorial choices about what is worth linking. A scientist's "field of work"
is linked; their religious beliefs typically are not. A film's director is
linked; its cinematographer often is not. What political or cultural
assumptions are encoded in which relationships Wikidata chooses to
represent; and which does it leave out?

&nbsp;

&nbsp;

---

*CS 108 — The Art and Practice of Computer Science | Walla Walla University*