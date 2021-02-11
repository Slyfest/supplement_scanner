# Ingredient Scanner

Telegram bot that scans food products for potentially harmful supplements.

**Note**: Currently supports product labels written in Russian.

<p float="left">
  <img src="assets/image_to_scan.jpg" width="300" />
  <img src="assets/scan_results.png" width="370" /> 
</p>

## How to use

1. Clone the repository.
2. Install [Poetry](https://github.com/python-poetry/poetry) (if you still haven't) and run poetry install.
3. Run python app/scrape_supplements.py to update csv file with supplements.
4. Store token of your Telegram bot in .env file at the project root.
5. Run python app/bot.py

## TODO

* Improve OpenCV preprocessing pipeline
* Add full support for English product labels