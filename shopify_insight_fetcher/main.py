############################# FASTAPI ##########################################

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.shopify_scraper import scrape_shopify_store
from database.db import init_db
from database.crud import save_brand_data
from database.schema import create_tables  # ensure this exists

app = FastAPI(
    title="Shopify Insights Fetcher API",
    description="Fetches product, FAQ, policy, contact, and social data from Shopify stores",
    version="1.0.0"
)

# Enable CORS (optional: restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema using Pydantic
class ShopifyRequest(BaseModel):
    website_url: str

# Startup hook: initialize DB and create tables
@app.on_event("startup")
def startup():
    init_db()
    create_tables()

# Health check route
@app.get("/")
def root():
    return {"message": "Shopify Insights Fetcher API is running start scrapping"}

# Main scraping + storing route
@app.post("/fetch_insights/")
def fetch_insights(request: ShopifyRequest):
    try:
        print("started")
        brand_data = scrape_shopify_store(request.website_url)
        print(brand_data)

        if not brand_data:
            raise HTTPException(status_code=400, detail="Failed to scrape the provided URL.")

        save_brand_data(brand_data)

        return {
            "success": True,
            "message": "Data fetched and stored successfully",
            "data": brand_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



############################  FLASK ##########################################


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from utils.shopify_scraper import scrape_shopify_store
# from database.db import init_db
# from database.crud import save_brand_data
# from database.schema import create_tables

# app = Flask(__name__)
# CORS(app)

# # Initialize DB on startup
# @app.before_request
# def startup():
#     init_db()
#     create_tables()

# # Health check route
# @app.route("/", methods=["GET"])
# def root():
#     return jsonify({"message": "Shopify Insights Fetcher API is running start scraping"})

# # Main route for scraping and saving insights
# @app.route("/fetch_insights/", methods=["POST"])
# def fetch_insights():
#     try:
#         data = request.get_json()
#         website_url = data.get("website_url")

#         if not website_url:
#             return jsonify({"success": False, "message": "website_url is required"}), 400

#         print("Scraping started...")
#         brand_data = scrape_shopify_store(website_url)
#         print("Scraped data:", brand_data)

#         if not brand_data:
#             return jsonify({"success": False, "message": "Failed to scrape the provided URL."}), 400

#         save_brand_data(brand_data)

#         return jsonify({
#             "success": True,
#             "message": "Data fetched and stored successfully",
#             "data": brand_data
#         })

#     except Exception as e:
#         return jsonify({"success": False, "message": "Internal Server Error", "error": str(e)}), 500

# # Run Flask app
# if __name__ == "__main__":
#     app.run(debug=True)