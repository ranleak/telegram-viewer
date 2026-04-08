# telegram-viewer
View a live feed of a public Telegram channel, and optionally download its media - all from your CLI.

## Requirements
This script uses requests and BeautifulSoup4. Install them before use. The script now uses opencv-python (for video interpretation) and deep_translator (for translating messages/posts). It also uses [my custom Python 7zip library](https://github.com/ranleak/py7zip) to bundle media files after the live feed is exited. Make sure to install them if you want those features, otherwise the script will run without them and display a warning message. For HTML to PDF rendering, it uses Playwright. Make sure to install it like shown below:
```bash
pip install playwright
playwright install-deps
playwright install chromium
```
Then you should be good to go!

## Usage
All scripts are interactive and easy to use. Press CTRL+C once to exit the live feed (once you are in one), and press it again to exit the program. Enjoy!
