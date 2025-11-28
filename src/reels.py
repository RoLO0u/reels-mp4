import instaloader
from instaloader import Post

def download(shortcode: str) -> Post:
  L = instaloader.Instaloader()
  return Post.from_shortcode(L.context, shortcode)  