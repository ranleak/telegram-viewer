import json
import os
import sys
import html

def escape_text(text):
    """Escapes HTML characters and converts newlines to <br> tags."""
    if not text:
        return ""
    return html.escape(text).replace('\n', '<br>')

def generate_chat_html(json_file):
    if not os.path.exists(json_file):
        print(f"[!] File not found: {json_file}")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        try:
            messages = json.load(f)
        except json.JSONDecodeError:
            print("[!] Invalid JSON file.")
            return

    # Extract channel name from the JSON filename to use as title
    channel_name = os.path.basename(json_file).replace('messages_', '').replace('.json', '')
    output_html = f"chat_{channel_name}.html"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chat Log: {channel_name}</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #f0f2f5;
        margin: 0;
        padding: 40px 20px;
        color: #1c1e21;
    }}
    .chat-container {{
        max-width: 600px;
        margin: 0 auto;
        background: #ffffff;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    .header {{
        text-align: center;
        border-bottom: 1px solid #e4e6eb;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }}
    .header h2 {{ margin: 0; font-size: 20px; }}
    .message {{
        margin-bottom: 24px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }}
    .bubble {{
        max-width: 85%;
        padding: 12px 16px;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        background-color: #e4e6eb;
        font-size: 15px;
        line-height: 1.5;
        word-wrap: break-word;
    }}
    .translated {{
        font-style: italic;
        color: #0056b3;
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }}
    .media-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }}
    .media-item {{
        border-radius: 12px;
        overflow: hidden;
        max-width: 100%;
    }}
    .media-item img, .media-item video {{
        max-width: 100%;
        max-height: 400px;
        display: block;
        object-fit: cover;
    }}
    .meta {{
        font-size: 12px;
        color: #65676b;
        margin-top: 6px;
        margin-left: 8px;
    }}
</style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h2>@{channel_name}</h2>
            <span style="color: #65676b; font-size: 14px;">Message Log</span>
        </div>
"""

    for msg in messages:
        original_text = escape_text(msg.get('text', ''))
        translated_text = escape_text(msg.get('translated_text'))
        timestamp = escape_text(msg.get('timestamp', 'Unknown'))
        views = escape_text(msg.get('views', 'N/A'))
        local_media = msg.get('local_media', [])

        html_content += '        <div class="message">\n'
        html_content += '            <div class="bubble">\n'

        if translated_text:
            html_content += f'                <div class="translated"><b>Translated:</b><br>{translated_text}</div>\n'
            html_content += f'                <div class="original">{original_text}</div>\n'
        else:
            html_content += f'                <div class="original">{original_text}</div>\n'

        if local_media:
            html_content += '                <div class="media-grid">\n'
            for media_path in local_media:
                # Need to replace backslashes for web paths if running on Windows
                web_path = media_path.replace('\\', '/')
                html_content += '                    <div class="media-item">\n'
                if web_path.endswith('.mp4'):
                    html_content += f'                        <video controls src="{web_path}"></video>\n'
                else:
                    html_content += f'                        <img src="{web_path}" alt="media attached">\n'
                html_content += '                    </div>\n'
            html_content += '                </div>\n'

        html_content += '            </div>\n'
        html_content += f'            <div class="meta">{timestamp} • 👁 {views}</div>\n'
        html_content += '        </div>\n'

    html_content += """
    </div>
</body>
</html>
"""

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n[+] Successfully generated {output_html}")
    print(f"    Open '{output_html}' in your web browser, then press Ctrl+P (or Cmd+P) to Save as PDF.")

if __name__ == "__main__":
    print("="*50)
    print("   TELEGRAM JSON to HTML/PDF CHAT FORMATTER")
    print("="*50)
    
    json_path = input("Enter the path to your JSON file (e.g., messages_durov.json): ").strip()
    
    if json_path:
        generate_chat_html(json_path)
    else:
        print("No file specified. Exiting.")