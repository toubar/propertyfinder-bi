import pandas as pd
import re
from io import StringIO

# Paste your raw CSV data here as a string
csv_data = """
property-card-module_property-card__link__L6AKb href,styles_desktop_gallery-image__n81d5 src,property-card-module_property-card__image-count__HZqam,styles-module_content__property-type__QuVl4,styles-module_content__price__SgQ5p,styles-module_content__title__eOEkd,styles-module_content__listing-level__OTHNr,styles_empty__Qq2XI src,styles-module_content__location__bNgNM,styles-module_content__details-item__mlu9B,styles-module_content__details-item__mlu9B (2),styles-module_content__details-item__mlu9B (3),styles-module_footer__publish-info__UVabq,link-module_link__TaDrq href (2),link-module_link__TaDrq,button-module_button__06uQ8,link-module_link__TaDrq href (3),link-module_link__TaDrq (2),tag-module_tag__jFU3w,email-alert-card_card__bg__dvRas src,email-alert-card_card__bell__mhxgh src,email-alert-card_card__title__tqkgk,email-alert-card_card__description__nqSzE,email-alert-card_card__locations__1_bkN
https://www.propertyfinder.eg/en/plp/buy/townhouse-for-sale-north-coast-ras-al-hekma-june-7537139.html,https://www.propertyfinder.eg/property/fbf05588859cc70675418e3e1cb2d95c/416/272/MODE/51fd6b/7537139-36b95o.webp?ctr=eg,13,Townhouse,"22,000,000 EGP",June Townhouse ready to deliver with lowest price,PREMIUM,https://www.propertyfinder.eg/broker/2/178/98/MODE/bc86cd/1750-logo.jpg?ctr=eg,"June, Ras Al Hekma, North Coast",3,3,202 sqm,Listed 1 hour ago,tel:+201207550900,Call,Email,https://api.whatsapp.com/send?phone=+20221257340&text=Hello...,WhatsApp,,,,,,
"""

# Load data
df = pd.read_csv('propertyfinder-2025-07-08.csv')

# Rename columns to something more usable
df.columns = [
    "Listing_URL", "Image_URL", "Image_Count", "Property_Type", "Price_EGP",
    "Title", "Listing_Level", "Broker_Logo_URL", "Location",
    "Bedrooms", "Bathrooms", "Area_sqm", "Listed_Time",
    "Phone_Link", "Call_Text", "Email_Text", "WhatsApp_Link",
    "WhatsApp_Text", "Down_Payment", "Bell_Icon",
    "Title_Extra", "Description_Extra", "Locations_Extra", "Unused"
]

# Clean numeric fields
def extract_number(text):
    if pd.isnull(text):
        return None
    numbers = re.findall(r'\d+', str(text).replace(',', ''))
    return int(''.join(numbers)) if numbers else None

df["Price_EGP_Clean"] = df["Price_EGP"].apply(extract_number)
df["Down_Payment_Clean"] = df["Down_Payment"].apply(extract_number)
df["Area_sqm_Clean"] = df["Area_sqm"].apply(extract_number)
df["Bedrooms"] = pd.to_numeric(df["Bedrooms"], errors='coerce').fillna(0).astype(int)
df["Bathrooms"] = pd.to_numeric(df["Bathrooms"], errors='coerce').fillna(0).astype(int)

# Preview cleaned data
print(df.head())

df.to_csv("cleaned_real_estate_listings.csv", index=False)

print("✅ Cleaned data saved to 'cleaned_real_estate_listings.csv'")