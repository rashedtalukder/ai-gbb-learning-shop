import sys
import json
from typing import Any, Callable, Set
import logging
import config
import pypandoc


logging.basicConfig(level=logging.INFO)


async def save_to_pdf(itinerary: str, file_path: str) -> str:
    """
    Saves the provided travel itinerary as a PDF document.

    :param itinerary (str): The travel itinerary as markdown to save as a PDF document.

    :return: The path to the saved PDF file.
    :rtype: str
    """

    if not itinerary:
        logging.error("No itinerary provided.")
        return json.dumps({"error": "No itinerary provided."})

    try:
        pdf_output = pypandoc.convert_text(itinerary, 'rst', format='md')

        w = open(file_path, "w", encoding="utf-8")
        write_status = w.write(pdf_output)
        w.close()
    except Exception as e:
        logging.error(
            "Failed to save the itinerary as a PDF. Error message:\n %s", e)
        write_status = 0

    return json.dumps({"wrote_characters": write_status})


async def process_itinerary(doc_url: str) -> str:
    """
    Gets the provided itinerary document URL to the Azure Content Understanding service's document 
    analyzer to extract the content of the unstructured document into a structured format.

    :param doc_url (str): The HTTP URL to retrieve the travel itinerary from.

    :return: The processed itinerary with the extracted or generated fields as a markdown string.
    :rtype: str
    """

    if not doc_url:
        logging.error("No document URL provided.")
        return json.dumps({"error": "No document URL provided."})

    if config.CU_CLIENT is None or config.ANALYZER_ID is None:
        logging.error(
            "Content Understanding client or analyzer ID not initialized.")
        return json.dumps({"error": "Content Understanding client or analyzer ID not initialized."})

    try:
        analyze_file = config.CU_CLIENT.begin_analyze(
            analyzer_id=config.ANALYZER_ID,
            file_location=doc_url
        )
    except (ConnectionError, TimeoutError, ValueError) as e:
        logging.error("Failed to analyze the document. Error message:\n %s", e)
        config.CU_CLIENT.delete_analyzer(analyzer_id=config.ANALYZER_ID)
        sys.exit(1)
    output = config.CU_CLIENT.poll_result(analyze_file)

    logging.info("📊 Status of the analyze operation: %s", output["status"])
    logging.info("🔎 Analyze operation completed with the result:")
    logging.info(json.dumps(output, indent=2))

    itinerary = {"raw": output["result"]["contents"][0]["markdown"],
                 "start_date": output["result"]["contents"][0]["fields"]["StartDate"]["valueDate"],
                 "end_date": output["result"]["contents"][0]["fields"]["EndDate"]["valueDate"],
                 "existing_plans": output["result"]["contents"][0]["fields"]["ExistingPlans"]["valueString"]}

    logging.info(" Generated Itinerary:\n\n %s\n\n", itinerary)
    return json.dumps(itinerary)


# Example User Input for Each Function
# 1. Process Itinerary
#     User Input: "Process the travel itinerary document available at http://www.example.com/itinerary.pdf."
#     User Input: "http://www.example.com/itinerary.pdf."
#     User Input: "My travel itinerary with my flight details and hotel information is available at http://www.example.com/intinerary.pdf"
# Statically defined user functions for fast reference
travel_functions: Set[Callable[..., Any]] = {
    save_to_pdf,
    process_itinerary,
}
