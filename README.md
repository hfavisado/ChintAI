# Real Estate Scraper ChintAI

A web scraper for real estate properties in Tokyo's 23 wards, supporting multiple websites including SUUMO and AtHome.

## Features

- Scrapes property listings from multiple real estate websites
- Filters properties based on specific criteria:
  - Price: Up to ¥230,000/month for rent or ¥100M for purchase
  - Location: Tokyo's 23 wards
  - Distance: Within 10 minutes of nearest train station
  - Floor area: 65m² or above
  - Building material: Reinforced concrete
  - Floor: 2nd floor or higher
  - Gas type: City gas only
- Saves results in JSON format
- Modular architecture for easy expansion to support more websites

## Installation

Choose one of the following methods to install and run the scraper:

### Method 1: Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ChintAI.git
cd ChintAI
```

2. Build and run the Docker container:
```bash
docker build -t chintai .
docker run -v $(pwd)/results:/app/results chintai
```

The results will be saved in the `results` directory on your host machine.

### Method 2: Using Poetry

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/ChintAI.git
cd ChintAI
```

3. Install dependencies and run the scraper:
```bash
poetry install
poetry run scraper
```

### Method 3: Traditional Python Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ChintAI.git
cd ChintAI
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the scraper:
```bash
python src/main.py
```

## Usage

The scraper will:
1. Search for properties matching the criteria
2. Save the results to a JSON file with timestamp in the `results` directory
3. Print a summary of found properties

## Adding New Scrapers

To add support for a new website:
1. Create a new scraper class in `src/scrapers/` that inherits from `BaseScraper`
2. Implement the required methods:
   - `search_properties()`
   - `get_property_details()`
3. Add the new scraper to the main script

## Project Structure

```
ChintAI/
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py
│   │   ├── suumo_scraper.py
│   │   └── athome_scraper.py
│   ├── models/
│   │   └── property.py
│   └── main.py
├── tests/
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Notes

- The scraper uses async/await for better performance
- Results are saved in JSON format with UTF-8 encoding
- Each property listing includes detailed information and a URL to the original listing
- When using Docker, results are saved in a volume mounted at `/app/results` 