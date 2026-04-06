import os
import sys

# Attempt to import Playwright
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[!] Playwright is not installed.")
    print("    Please run: pip install playwright")
    print("    And then:   playwright install chromium")
    sys.exit(1)

def convert_html_to_pdf(html_file_path):
    """Converts a local HTML file to a formatted PDF using headless Chromium."""
    if not os.path.exists(html_file_path):
        print(f"[!] The file '{html_file_path}' was not found.")
        return

    # Create the output PDF filename (e.g., chat_durov.html -> chat_durov.pdf)
    base_name = os.path.splitext(html_file_path)[0]
    pdf_file_path = f"{base_name}.pdf"

    print(f"[*] Starting conversion for '{html_file_path}'...")

    try:
        with sync_playwright() as p:
            # Launch an invisible Chromium browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Convert the local file path to a file:// URL format
            abs_path = os.path.abspath(html_file_path)
            file_url = f"file://{abs_path}"

            print("[*] Loading HTML and waiting for media to render...")
            # Go to the HTML file and wait until all resources (like images) are fully loaded
            page.goto(file_url, wait_until='networkidle')

            # Generate the PDF
            # print_background=True ensures our CSS background colors/bubbles show up
            page.pdf(
                path=pdf_file_path,
                format="A4",
                print_background=True,
                margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
            )

            browser.close()
            print(f"[+] Success! PDF saved as '{pdf_file_path}'")
            
    except Exception as e:
        print(f"[!] An error occurred during PDF generation: {e}")

if __name__ == "__main__":
    print("="*50)
    print("        HTML TO PDF AUTOCONVERTER")
    print("="*50)
    
    html_input = input("Enter the path to your HTML file (e.g., chat_durov.html): ").strip()
    
    if html_input:
        convert_html_to_pdf(html_input)
    else:
        print("No file specified. Exiting.")