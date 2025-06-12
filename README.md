# codex_f1

This repository contains a basic Streamlit dashboard using the [FastF1](https://github.com/theOehrly/Fast-F1) API. The project is organised with utilities, assets and separate modules for each dashboard tab.

## Structure

```
app.py           # Main entry point for the dashboard
utils/           # Helper functions and data utilities
assets/          # Static files such as images or logos
tabs/            # Individual Streamlit pages (tabs)
```

## Running the app

Install the required dependencies from `requirements.txt` and start Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

FastF1 caching is enabled by default in `app.py` which stores session data in a local `cache` directory for faster subsequent loads.
