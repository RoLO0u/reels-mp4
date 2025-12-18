from instaloader import Post

from src.const import L

def download(shortcode: str) -> Post:
  return Post.from_shortcode(L.context, shortcode)
