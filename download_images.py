import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

# ==========================================
# PASTE YOUR TARGET WEBSITE LINK HERE:
TARGET_URL = "https://www.oatlas.com/en/events/place-of-reception-marrakech/"
# ==========================================


def download_images(url):
  # Set up headers to mimic a real web browser (prevents 403 Forbidden errors)
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  print(f"[*] Connecting to: {url}")
  try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(f"[!] Error fetching the URL: {e}")
    return

  # Parse the HTML content of the page
  soup = BeautifulSoup(response.text, "html.parser")
  img_tags = soup.find_all("img")

  if not img_tags:
    print("[!] No images found on this page.")
    return

  print(f"[*] Found {len(img_tags)} image tags. Starting download...")

  # Get script directory and create an 'images' subfolder
  script_dir = os.path.dirname(os.path.abspath(__file__))
  images_dir = os.path.join(script_dir, "images")
  os.makedirs(images_dir, exist_ok=True)

  downloaded_count = 0
  for idx, img in enumerate(img_tags):
    # Extract the image source link (handles standard src and lazy-loaded data-src)
    img_url = img.get("src") or img.get("data-src")

    if not img_url:
      continue

    # Convert relative URLs into absolute URLs
    img_url = urljoin(url, img_url)

    # Skip inline base64 images
    if img_url.startswith("data:image"):
      continue

    try:
      # Extract the filename from the URL
      parsed_url = urlparse(img_url)
      img_name = os.path.basename(parsed_url.path).split("?")[0]

      # If the URL doesn't have a valid filename, generate one
      if not img_name or "." not in img_name:
        img_name = f"image_{idx + 1}.jpg"

      save_path = os.path.join(images_dir, img_name)

      # Prevent overwriting if two images have the same filename
      base, ext = os.path.splitext(img_name)
      counter = 1
      while os.path.exists(save_path):
        img_name = f"{base}_{counter}{ext}"
        save_path = os.path.join(images_dir, img_name)
        counter += 1

      # Download the image content
      img_response = requests.get(img_url, headers=headers, timeout=10)
      if img_response.status_code == 200:
        with open(save_path, "wb") as f:
          f.write(img_response.content)
        print(f"[+] Downloaded: {img_name}")
        downloaded_count += 1
      else:
        print(
            f"[-] Failed to download {img_url} (Status:"
            f" {img_response.status_code})"
        )
    except Exception as e:
      print(f"[-] Error downloading {img_url}: {e}")

  print(
      f"\n[✨] Done! Successfully downloaded {downloaded_count} images to the"
      " 'images' folder."
  )


if __name__ == "__main__":
  download_images(TARGET_URL)