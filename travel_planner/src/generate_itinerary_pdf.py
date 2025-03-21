from fpdf import FPDF
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _clean_text(text):
    """Removes unsupported characters for PDF encoding"""
    return text.encode('latin-1', 'ignore').decode('latin-1')


def create_itinerary_pdf(itinerary_data, output_file):
    """
    Generates a PDF document for a travel itinerary.

    This function takes itinerary data as a JSON object, formats the data, and 
    generates a PDF document with the itinerary details. The PDF includes the 
    trip name, destinations, start and end dates, and a day-wise breakdown of 
    activities.

    The generated PDF is saved to the specified output file path.

    Args:
        itinerary_data (dict): The itinerary data as a JSON object.
        output_file (str): Path to the output PDF file.

    Raises:
        Exception: If there is an error in generating the PDF, an exception is 
                    logged with the error message.
    """
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", "", 12)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, _clean_text(itinerary_data.get(
            "TripName", "Travel Itinerary")), ln=True, align="C")
        pdf.ln(10)

        # Destinations
        pdf.set_font("Arial", "B", 12)
        pdf.cell(
            200, 10, f"Destinations: {_clean_text(itinerary_data.get('Destinations', 'Unknown'))}", ln=True)

        # Dates
        pdf.cell(
            200, 10, f"Start Date: {itinerary_data.get('StartDate', 'Unknown')}", ln=True)
        pdf.cell(
            200, 10, f"End Date: {itinerary_data.get('EndDate', 'Unknown')}", ln=True)
        pdf.ln(10)

        # Day-wise itinerary
        pdf.set_font("Arial", "", 11)
        for day, activities in itinerary_data.get("Days", {}).items():
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, _clean_text(day), ln=True)
            pdf.set_font("Arial", "", 11)

            for time_of_day, activity in activities.items():
                if activity:
                    pdf.cell(
                        200, 10, f"{time_of_day}: {_clean_text(activity)}", ln=True)

            pdf.ln(5)

        # Save PDF
        pdf.output(output_file)
        logging.info("✅ PDF successfully saved as %s", output_file)

    except Exception as e:
        logging.error("❌ Error saving PDF: %s", e)
