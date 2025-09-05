# pages_module/utils.py
import streamlit.components.v1 as components
from datetime import datetime

def display_carousel(items, item_type="track"):
    slides = ""
    for item in items:
        if item_type == "artist":
            img_url = item.get("images", [{}])[0].get("url", "")
            caption = f"<strong>{item.get('name', 'Unknown')}</strong><br/>Popularity: {item.get('popularity', 0)}"
        elif item_type == "track":
            album_images = item.get("album", {}).get("images", [])
            img_url = album_images[0]["url"] if album_images else ""
            duration_ms = item.get("duration_ms", 0)
            minutes = duration_ms // 60000
            seconds = (duration_ms % 60000) // 1000
            caption = f"<strong>{item.get('name', 'Unknown')}</strong><br/>{minutes}:{seconds:02d}"
            if item.get("played_at"):
                played_time = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
                caption += f"<br/>🎧 {played_time.strftime('%d/%m %H:%M')}"
        else:
            img_url, caption = "", "Item"

        slides += f"""
        <div class="swiper-slide">
            <img src="{img_url}" alt="cover">
            <div class="caption">{caption}</div>
        </div>
        """

    html_code = f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/>
    <style>
    .swiper {{
        width: 100%;
        padding: 15px 0;
    }}
    .swiper-slide {{
        background: #181818;
        border-radius: 12px;
        overflow: hidden;
        text-align: center;
        color: #fff;
        font-size: 14px;
        width: 160px !important;
    }}
    .swiper-slide img {{
        width: 100%;
        height: 160px;
        object-fit: cover;
        border-bottom: 1px solid #333;
    }}
    .caption {{
        padding: 6px;
        font-size: 13px;
    }}
    </style>
    <div class="swiper">
      <div class="swiper-wrapper">
        {slides}
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
    const swiper = new Swiper('.swiper', {{
        slidesPerView: 5,
        spaceBetween: 15,
        loop: true,
        autoplay: {{
            delay: 2500,
            disableOnInteraction: false,
        }},
    }});
    </script>
    """
    components.html(html_code, height=260)
