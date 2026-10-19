import streamlit as st
import requests
import json

# 1. Page Configuration
st.set_page_config(
    page_title="Multi-API Clothing Store",
    page_icon="🛍️",
    layout="wide"
)

# 2. Define Free API Sources & Links
API_SOURCES = {
    "Fake Store API": {
        "url": "https://fakestoreapi.com",
        "link": "https://fakestoreapi.com/",
        "description": "A free online REST API for e-commerce testing. We pull curated fashion items from here."
    },
    "Platzi Fake Store API": {
        "url": "https://api.escuelajs.co/api/v1/products",
        "link": "https://fakeapi.platzi.com/",
        "description": "Real e-commerce data with high-quality fashion product images and clean JSON outputs."
    }
}

# 3. Main Header & Banner
st.title("👗 Multi-API Digital Clothing Boutique")
st.write("Welcome to the aggregate clothing hub powered concurrently by independent free data platforms.")

# 4. API Directory Layout (Directly on the Home Page)
st.markdown("### 🔗 Direct API Documentation Links")
api_cols = st.columns(2)

for idx, (name, info) in enumerate(API_SOURCES.items()):
    with api_cols[idx]:
        with st.container(border=True):
            st.markdown(f"#### **[{name}]({info['link']})**")
            st.write(info['description'])
            st.caption(f"Endpoint: `{info['url']}`")

st.markdown("---")

# 5. Native Page Filter Selection
st.markdown("### 🗂️ Explore Collections")
app_mode = st.segmented_control(
    "Choose a Store Section:", 
    options=["All Clothing", "Fake Store API Inventory", "Platzi Fashion API Inventory"],
    default="All Clothing"
)

# 6. Safe Data Fetching Functions with Fallbacks
@st.cache_data(ttl=300)
def fetch_fake_store_data():
    try:
        res = requests.get("https://fakestoreapi.com", timeout=8)
        if res.status_code == 200:
            all_items = res.json()
            clothing = [
                item for item in all_items 
                if item.get('category', '').lower() in ["men's clothing", "women's clothing"]
            ]
            return clothing if clothing else all_items[:10]
        return []
    except Exception as e:
        st.warning(f"Fake Store API is temporarily unreachable.")
        return []

@st.cache_data(ttl=300)
def fetch_platzi_data():
    try:
        res = requests.get("https://api.escuelajs.co/api/v1/products", timeout=8)
        if res.status_code == 200:
            all_items = res.json()
            # Look specifically for category names related to clothing
            clothing = [
                item for item in all_items
                if item.get('category', {}).get('name', '').lower() in ['clothes', 'shoes', 'miscellaneous']
            ]
            return clothing[:15] if clothing else all_items[:15]
        return []
    except Exception as e:
        st.warning(f"Platzi Fashion API is temporarily unreachable.")
        return []

# 7. CRITICAL: Real-Time Live URL Validator & Sanitizer
def get_validated_image_url(images_field):
    fallback_placeholder = "https://unsplash.com"
    
    if not images_field:
        return fallback_placeholder
        
    # Standardize string inputs vs lists from nested APIs
    raw_url = images_field[0] if isinstance(images_field, list) else str(images_field)
    
    # Unpack nested, stringified JSON strings like '["[\"http...\"]"]'
    for _ in range(3):
        raw_url = raw_url.strip('[]"\' ')
        if raw_url.startswith('["') or raw_url.startswith('['):
            try:
                parsed = json.loads(raw_url)
                raw_url = parsed[0] if isinstance(parsed, list) else str(parsed)
            except:
                pass

    # Basic layout string filters
    if "placeimg.com" in raw_url or not raw_url.startswith("http"):
        return fallback_placeholder

    # LIVE CHECK: Fire a quick HEAD request to verify if it returns a 200 OK image
    try:
        response = requests.head(raw_url, timeout=2, allow_redirects=True)
        # Verify it exists and is explicitly an image payload type
        if response.status_code == 200 and "image" in response.headers.get("Content-Type", "").lower():
            return raw_url
    except:
        pass # If request times out or breaks, skip to fallback below
        
    return fallback_placeholder

# 8. UI Grid Rendering Helper
def render_product_grid(products, source_type):
    if not products:
        st.info("No items available to display right now from this provider.")
        return

    cols = st.columns(3)
    for i, item in enumerate(products):
        with cols[i % 3]:
            if source_type == "fakestore":
                title = item.get('title', 'Fashion Apparel')
                price = item.get('price', 0.0)
                image_url = get_validated_image_url(item.get('image'))
                desc = item.get('description', '')[:90] + "..."
            else: # platzi
                title = item.get('title', 'Platzi Style Clothing')
                price = item.get('price', 0.0)
                image_url = get_validated_image_url(item.get('images'))
                desc = item.get('description', '')[:90] + "..."

            with st.container(border=True):
                st.image(image_url, use_container_width=True)
                st.subheader(f"{title[:35]}")
                st.markdown(f"### **\${price}**")
                st.caption(desc)
                
                if st.button("Add to Cart", key=f"btn_{source_type}_{item.get('id', i)}_{i}"):
                    st.success(f"Added item to cart!")

# 9. Rendering Content Grid
fake_store_products = fetch_fake_store_data()
platzi_products = fetch_platzi_data()

if app_mode == "All Clothing":
    st.markdown("### 🏷️ From: Fake Store API Section")
    render_product_grid(fake_store_products[:6], "fakestore")
    
    st.markdown("---")
    
    st.markdown("### 🏷️ From: Platzi Fashion API Section")
    render_product_grid(platzi_products[:6], "platzi")

elif app_mode == "Fake Store API Inventory":
    st.markdown("## 🛒 Fake Store API Exclusive Feed")
    render_product_grid(fake_store_products, "fakestore")

elif app_mode == "Platzi Fashion API Inventory":
    st.markdown("## 👟 Platzi API Exclusive Feed")
    render_product_grid(platzi_products, "platzi")
