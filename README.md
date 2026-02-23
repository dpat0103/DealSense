# DealSense

DealSense is a pricing intelligence tool for used cars. It analyzes vehicle listings and estimates a fair market value, deal quality, and comparable listings using real data.

The goal is simple: help buyers quickly determine whether a car is overpriced, fairly priced, or a strong deal.

This repository contains the backend API, training pipeline, and a minimal frontend for local exploration.

What it does

Given a dataset of vehicle listings, DealSense can:

Estimate a fair market price using a trained model

Score each listing as a great deal, fair deal, or overpriced

Show how far above or below market a listing is

Provide comparable vehicles for context

Expose everything through a local API

The current version is designed for local use and experimentation.

Why this exists

Used car pricing is inconsistent and difficult to evaluate without experience. Listings vary widely based on mileage, location, trim, and seller behavior. Most marketplaces show raw listings but provide little insight.

DealSense attempts to quantify that market using historical data.

# Repository Structure
backend/
  app/           FastAPI service and model code
  scripts/       Data loading utilities
  data/          Sample dataset
  artifacts/     Model outputs (ignored in git)
  requirements.txt

frontend/
  Minimal UI for local testing

.gitignore
README.md

# Backend Setup 
cd backend
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

# Load sample data 
python -m scripts.load_csv --csv data/sample_listings.csv --reset

# Train the model
python -m app.ml.train

# Run the API
uvicorn app.main:app --reload --port 8000

# Example API request 
GET /search?make=buick&model=encore&limit=10
