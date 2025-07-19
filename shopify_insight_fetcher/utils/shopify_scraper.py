import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def clean_text(soup):
    for tag in soup(["script", "style", "noscript", "svg", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"loading\.{0,3}", "", text, flags=re.I)
    return text[:2000]

def clean_store_name(url):
    domain = urlparse(url).netloc
    return domain.replace("www.", "")

def scrape_shopify_store(url):
    try:
        session = requests.Session()

        result = {
            "store_name": clean_store_name(url),
            "products": [],
            "hero_products": [],
            "privacy_policy": "",
            "refund_policy": "",
            "faqs": [],
            "about_brand": "",
            "contact_info": {"emails": [], "phones": []},
            "social_links": {},
            "important_links": {}
        }

        # 1. Products from /products.json
        products_url = urljoin(url, "/products.json")
        products_resp = session.get(products_url, timeout=10)
        if products_resp.status_code == 200:
            data = products_resp.json()
            for prod in data.get("products", []):
                try:
                    price = float(prod["variants"][0].get("price", 0)) if prod.get("variants") else None
                    result["products"].append({
                        "title": prod.get("title", ""),
                        "price": price,
                        "url": urljoin(url, f"/products/{prod.get('handle', '')}"),
                        "is_hero": False
                    })
                except Exception as e:
                    print("[Product Error]", str(e))
                    continue

        # 2. Scrape homepage
        home_resp = session.get(url, timeout=10)
        soup = BeautifulSoup(home_resp.text, "html.parser")

        # 3. Hero products
        seen_urls = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/products/" in href:
                full_url = urljoin(url, href)
                if full_url not in seen_urls:
                    result["hero_products"].append({
                        "title": a.get_text(strip=True),
                        "price": None,
                        "url": full_url,
                        "is_hero": True
                    })
                    seen_urls.add(full_url)

        # 4. Extract contact info
        email_match = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", home_resp.text)
        phone_match = re.findall(r"\+?\d[\d\s\-]{7,}\d", home_resp.text)
        result["contact_info"] = {
            "emails": list(set(email_match)),
            "phones": list(set(phone_match))
        }

        # 5. Extract social links
        socials = {}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(x in href for x in ["instagram", "facebook", "twitter", "tiktok", "linkedin", "youtube"]):
                match = re.search(r"(instagram|facebook|twitter|tiktok|linkedin|youtube)", href)
                if match:
                    platform = match.group(1).lower()
                    socials[platform] = href
        result["social_links"] = socials

        # 6. About, FAQ, Policy links
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(strip=True).lower()
            full_href = urljoin(url, href)

            # About Page
            if ("about" in href or "about" in text) and not result["about_brand"]:
                try:
                    about_resp = session.get(full_href)
                    if about_resp.status_code == 200:
                        about_soup = BeautifulSoup(about_resp.text, "html.parser")
                        result["about_brand"] = clean_text(about_soup)
                except:
                    pass

            # FAQ Page
            elif ("faq" in href or "frequently asked" in text) and not result["faqs"]:
                try:
                    faq_resp = session.get(full_href)
                    if faq_resp.status_code == 200:
                        faq_soup = BeautifulSoup(faq_resp.text, "html.parser")
                        qas = re.findall(r"Q[:\)]\s*(.*?)\nA[:\)]\s*(.*?)\n", faq_soup.get_text(), re.DOTALL)
                        if qas:
                            result["faqs"] = [{"question": q.strip(), "answer": a.strip()} for q, a in qas][:10]
                        else:
                            for tag in faq_soup.find_all(["h3", "strong"]):
                                q = tag.get_text(strip=True)
                                a_tag = tag.find_next_sibling()
                                if a_tag:
                                    a = a_tag.get_text(strip=True)
                                    result["faqs"].append({"question": q, "answer": a})
                except:
                    pass

            # Privacy or Refund Policy
            elif "policy" in href or "privacy" in href or "refund" in href:
                try:
                    policy_resp = session.get(full_href)
                    if policy_resp.status_code == 200:
                        policy_soup = BeautifulSoup(policy_resp.text, "html.parser")
                        policy_text = clean_text(policy_soup)
                        if "refund" in href:
                            result["refund_policy"] = policy_text
                        elif "privacy" in href:
                            result["privacy_policy"] = policy_text
                except:
                    pass

            # Footer Important Links
            if any(word in text for word in ["blog", "track", "order", "help", "contact"]):
                result["important_links"][a.get_text(strip=True)] = full_href

        # 7. Merge hero and normal products
        existing_urls = set(p["url"] for p in result["products"])
        for hero in result["hero_products"]:
            if hero["url"] not in existing_urls:
                result["products"].append(hero)

        return result

    except Exception as e:
        print("[Scraper Error]", str(e))
        return None
