import os
import json
import logging
from datetime import datetime, timedelta

# Logging setup
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

# File paths
EXTRACTED_FILE = "./output/extracted_itinerary.json"
OUTPUT_FILE = "./output/finalized_itinerary.json"


def generate_daywise_schedule(start_date, end_date, recommendations):
    """Organizes recommendations into a structured itinerary with morning, day, and night activities."""
    itinerary = {}

    try:
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        logging.error("Invalid date format: %s", e)
        return {}

    while current_date <= end_date:
        formatted_date = current_date.strftime("%B %d, %Y")
        itinerary[formatted_date] = {
            "Morning": None, "Day": None, "Night": None}
        current_date += timedelta(days=1)

    # Assign recommendations to time slots
    time_slots = ["Morning", "Day", "Night"]
    slot_index = 0

    if recommendations:
        for recommendation in recommendations:
            content = recommendation.get("content", "").split("\n")

            for line in content:
                if not line.strip():
                    continue  # Skip empty lines

                for _, slots in itinerary.items():
                    if slots[time_slots[slot_index]] is None:
                        slots[time_slots[slot_index]] = line.strip()
                        # Cycle through Morning, Day, Night
                        slot_index = (slot_index + 1) % 3
                        break

    return itinerary


def save_day_by_day_itinerary(extracted_data, output_file=OUTPUT_FILE):
    """Processes extracted itinerary data and structures the trip day by day."""
    try:
        trip_name = extracted_data.get("TripName", "Unknown Trip")
        destinations = extracted_data.get(
            "Destinations", "Unknown Destinations")
        start_date = extracted_data.get("StartDate")
        end_date = extracted_data.get("EndDate")

        # Extract AI-generated recommendations
        recommendations = extracted_data.get(
            "Here are your AI agentic recommendations:", [])

        if not start_date or not end_date:
            logging.error(
                "❌ Start date or end date missing in extracted data.")
            return

        logging.info("Trip Name: %s", trip_name)
        logging.info("Destinations: %s", destinations)
        logging.info("Start Date: %s", start_date)
        logging.info("End Date: %s", end_date)
        logging.info(
            "Processing %d AI-enhanced recommendations...", len(recommendations))

        # Debug recommendations content
        if recommendations:
            logging.debug(
                "AI-enhanced recommendations: %s", json.dumps(recommendations, indent=2))
        else:
            logging.warning("⚠️ No AI recommendations found!")

        # Generate structured itinerary using AI-enhanced recommendations
        structured_itinerary = generate_daywise_schedule(
            start_date, end_date, recommendations)

        # Debug itinerary structure
        logging.debug(
            "Generated structured itinerary: %s", json.dumps(structured_itinerary, indent=2))

        # Finalized itinerary structure
        finalized_itinerary = {
            "TripName": trip_name,
            "Destinations": destinations,
            "StartDate": start_date,
            "EndDate": end_date,
            "Days": structured_itinerary,
            "Status": "Finalized with AI-enhanced recommendations"
        }

        # Debug before writing file
        logging.debug("Saving finalized itinerary to %s...", output_file)

        # Save to JSON
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(finalized_itinerary, outfile,
                      indent=2, ensure_ascii=False)

        logging.info(
            "✅ Finalized itinerary successfully saved to %s", output_file)

        # Verify if file was saved correctly
        if os.path.exists(output_file):
            logging.info("✅ Verified: %s exists!", output_file)
            with open(output_file, "r", encoding="utf-8") as file:
                content = file.read()
                logging.debug("Finalized itinerary content:\n%s", content)
        else:
            logging.error("❌ Error: %s was not created!", output_file)

    except Exception as e:
        logging.error("❌ Error saving finalized itinerary: %s", e)
