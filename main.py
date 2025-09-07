import requests
from PIL import Image
from io import BytesIO

# Wikimedia Commons API endpoint
API_URL = "https://commons.wikimedia.org/w/api.php"

# Step 1: Search for 10 image titles
search_params = {
    "action": "query",
    "format": "json",
    "list": "search",
    "srsearch": "landscape",  # You can change this keyword
    "srlimit": 10,
    "srnamespace": 6  # Namespace 6 = File (images)
}


headers = {"User-Agent": "WikiCommonsDownloader/1.0 (pradipta.de@gmail.com)"}
response = requests.get(API_URL, params=search_params, headers=headers)
print(f"Status code: {response.status_code}")
print(f"Response text: {response.text[:500]}")  # Print only first 500 chars
if response.status_code != 200:
    raise Exception(f"Request failed with status code {response.status_code}")
try:
    search_results = response.json()["query"]["search"]
except Exception as e:
    print("Error parsing JSON response:", e)
    search_results = []

# Step 2: Get image info including license
titles = [result["title"] for result in search_results]
image_info_params = {
    "action": "query",
    "format": "json",
    "prop": "imageinfo",
    "titles": "|".join(titles),
    "iiprop": "url|extmetadata"
}

info_response = requests.get(API_URL, params=image_info_params, headers=headers)
pages = info_response.json()["query"]["pages"]

# Step 3: Download and display license info
output_lines = []
for page_id, page in pages.items():
    imageinfo = page.get("imageinfo", [{}])[0]
    url = imageinfo.get("url")
    metadata = imageinfo.get("extmetadata", {})
    license_name = metadata.get("LicenseShortName", {}).get("value", "Unknown")

    line1 = f"\n📷 Title: {page['title']}"
    line2 = f"🔗 URL: {url}"
    line3 = f"📜 License: {license_name}"
    print(line1)
    print(line2)
    print(line3)
    output_lines.extend([line1, line2, line3])

    # Download and display image
    if url:
        img_response = requests.get(url, headers=headers)
        if img_response.status_code == 200 and 'image' in img_response.headers.get('Content-Type', ''):
            try:
                img = Image.open(BytesIO(img_response.content))
                img.show()
            except Exception as e:
                err = f"Error opening image: {e}"
                print(err)
                output_lines.append(err)
        else:
            err = f"Failed to download image or content is not an image. Status: {img_response.status_code}, Content-Type: {img_response.headers.get('Content-Type')}"
            print(err)
            output_lines.append(err)

# Write output to a text file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))
