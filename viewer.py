import requests
from bs4 import BeautifulSoup
import time
import os
import sys
import re

# Attempt to import deep_translator for the new translation feature
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False


def clear_screen():
    """Clears the console screen for better readability."""
    os.system('cls' if os.name == 'nt' else 'clear')

def download_media(url, folder_path, filename):
    """Downloads a media file from a URL to a specified folder."""
    try:
        r = requests.get(url, stream=True, timeout=15)
        if r.status_code == 200:
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"    [!] Failed to download media: {e}")
    return False

def fetch_channel_messages(channel_name):
    """
    Fetches and parses messages from a public Telegram channel's web preview.
    """
    url = f"https://t.me/s/{channel_name}"
    # Use a standard User-Agent so Telegram doesn't block the request as a basic bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        
        # If the channel doesn't exist or isn't public, Telegram usually redirects or returns 404
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all message container divs
        message_containers = soup.find_all('div', class_='tgme_widget_message')
        
        # If no messages are found, the channel might be invalid or completely empty
        if not message_containers and "Telegram Web" not in soup.text:
             return None

        parsed_messages = []

        for msg in message_containers:
            # Extract the unique post ID (e.g., 'durov/123')
            post_id = msg.get('data-post', '')

            # Extract the message text
            text_div = msg.find('div', class_='tgme_widget_message_text')
            if text_div:
                # Use separator='\n' to keep line breaks in the message
                text = text_div.get_text(separator='\n').strip()
            else:
                text = "[Media / Non-text Content]"

            media_urls = []
            
            # Extract photo URLs
            photo_wraps = msg.find_all('a', class_='tgme_widget_message_photo_wrap')
            for wrap in photo_wraps:
                style = wrap.get('style', '')
                # Extract URL from background-image: url('...')
                match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
                if match:
                    media_urls.append(match.group(1))
                    
            # Extract video URLs
            videos = msg.find_all('video')
            for video in videos:
                src = video.get('src')
                if src:
                    media_urls.append(src)

            # Extract view count
            views_span = msg.find('span', class_='tgme_widget_message_views')
            views = views_span.text.strip() if views_span else "N/A"

            # Extract timestamp
            time_tag = msg.find('time')
            timestamp = time_tag.text if time_tag else "Unknown Time"

            parsed_messages.append({
                'id': post_id,
                'text': text,
                'media_urls': media_urls,
                'views': views,
                'timestamp': timestamp
            })

        return parsed_messages

    except requests.exceptions.RequestException as e:
        print(f"\n[!] Network error occurred: {e}")
        return []

def main():
    clear_screen()
    print("="*50)
    print("    TELEGRAM PUBLIC CHANNEL LIVE VIEWER")
    print("="*50)
    print("Type 'quit' or press Ctrl+C to exit at any time.\n")

    while True:
        channel_name = input("Enter a public Telegram channel username (e.g., 'durov', 'telegram'): ").strip()
        
        if channel_name.lower() == 'quit':
            break
            
        if not channel_name:
            continue
            
        # Clean up URL inputs if the user accidentally pastes the whole link
        if "t.me/" in channel_name:
            channel_name = channel_name.split('/')[-1]

        # Check for translation preference
        target_lang = None
        if TRANSLATION_AVAILABLE:
            trans_choice = input("Translate messages? (Enter 'en' for English, 'es' for Spanish, or leave blank to skip): ").strip().lower()
            if trans_choice in ['en', 'english']:
                target_lang = 'en'
            elif trans_choice in ['es', 'spanish']:
                target_lang = 'es'
        else:
            print("[!] 'deep_translator' library not found. Skipping translation feature.")
            print("    (To enable translation, install it via: pip install deep_translator)\n")

        save_media_choice = input("Would you like to save images and videos to a folder? (y/n): ").strip().lower()
        save_media = save_media_choice == 'y'
        
        media_folder = f"media_{channel_name}"
        if save_media:
            os.makedirs(media_folder, exist_ok=True)
            print(f"[*] Media will be saved to the '{media_folder}' folder.")

        print(f"\nConnecting to @{channel_name}...")
        
        seen_post_ids = set()
        refresh_rate = 15 # Seconds to wait between live checks
        
        # Initial Fetch
        messages = fetch_channel_messages(channel_name)
        
        if messages is None:
            print(f"[!] Could not find a public channel named '@{channel_name}'.")
            print("It might be private, non-existent, or restricted.\n")
            continue
            
        clear_screen()
        print(f"--- LIVE FEED: @{channel_name} ---")
        if target_lang:
            print(f"Translation enabled: Target Language -> {target_lang.upper()}")
        print(f"Polling for new messages every {refresh_rate} seconds. Press Ctrl+C to change channel.\n")
        
        try:
            while True:
                messages = fetch_channel_messages(channel_name)
                
                if messages:
                    new_messages = []
                    # Identify only the new messages we haven't seen yet
                    for msg in messages:
                        if msg['id'] not in seen_post_ids:
                            new_messages.append(msg)
                            seen_post_ids.add(msg['id'])
                    
                    # Print new messages
                    for msg in new_messages:
                        print(f"[{msg['timestamp']}] 👁 {msg['views']} views")
                        print("-" * 40)
                        
                        display_text = msg['text']
                        
                        # Apply translation if requested and the text is not just a media placeholder
                        if target_lang and display_text and display_text != "[Media / Non-text Content]":
                            try:
                                translated = GoogleTranslator(source='auto', target=target_lang).translate(display_text)
                                display_text = f"{translated}\n\n[Original]:\n{display_text}"
                            except Exception as e:
                                display_text = f"[Translation Error: {e}]\n{display_text}"
                                
                        print(f"{display_text}")
                        
                        if msg['media_urls']:
                            print(f"\n[!] Contains {len(msg['media_urls'])} media file(s).")
                            if save_media:
                                # Sanitize the post ID so it's safe to use as a file name
                                sanitized_id = msg['id'].replace('/', '_')
                                for idx, url in enumerate(msg['media_urls']):
                                    # Very simple extension guess based on the URL text
                                    ext = ".mp4" if ".mp4" in url.lower() else ".jpg"
                                    filename = f"{sanitized_id}_{idx}{ext}"
                                    print(f"    -> Downloading {filename}...")
                                    download_media(url, media_folder, filename)

                        print("-" * 40 + "\n")
                
                # Wait before polling again
                time.sleep(refresh_rate)
                
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully to return to the main menu
            clear_screen()
            print("\nStopped live feed.")
            print("="*50)
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting program. Goodbye!")
        sys.exit(0)