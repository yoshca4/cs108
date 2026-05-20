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