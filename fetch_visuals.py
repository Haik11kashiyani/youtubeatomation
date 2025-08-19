# fetch_visuals.py
import requests
import os

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
PIXABAY_URL = "https://pixabay.com/api/"

def fetch_image(query="astrology", save_path="image.jpg"):
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "vertical",
        "per_page": 3
    }
    r = requests.get(PIXABAY_URL, params=params).json()
    if r["hits"]:
        img_url = r["hits"][0]["largeImageURL"]
        img_data = requests.get(img_url).content
        with open(save_path, "wb") as f:
            f.write(img_data)
        print(f"Saved image to {save_path}")
    else:
        print("No images found, using default.")
        # Optionally use a placeholder image

if __name__ == "__main__":
    fetch_image("astrology")
