import requests
from bs4 import BeautifulSoup

def scrape_gce():
    urls = [
        "https://gcebodi.ac.in/",
        "https://gcebodi.ac.in/content/hods",
        "https://gcebodi.ac.in/22/department-computer-science-engineering-faculty",
        "https://gcebodi.ac.in/content/about-institute-0",
        "https://gcebodi.ac.in/content/college-fee-structure-0",
        "https://gcebodi.ac.in/content/courses-offered-0",
        "https://gcebodi.ac.in/content/placements"
    ]
    
    knowledge_base = ""
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            # Extract main text
            text = soup.get_text(separator=' ', strip=True)
            knowledge_base += f"\nSOURCE: {url}\n{text}\n"
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    with open("gce_bodi_data.txt", "w", encoding="utf-8") as f:
        f.write(knowledge_base)
    print("✅ Website data saved to gce_bodi_data.txt")

if __name__ == "__main__":
    scrape_gce()