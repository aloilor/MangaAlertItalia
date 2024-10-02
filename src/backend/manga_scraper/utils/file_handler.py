import os
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file saving functionality for scraped data"""

    def __init__(self, path_to_save_html):
        self.path_to_save_html = path_to_save_html

    def save_response_to_file(self, manga: str, publisher: str, response: str):
        filename = f"{manga.replace(' ', '_')}_{publisher}.txt"
        full_path = os.path.join(self.path_to_save_html, filename)

        os.makedirs(self.path_to_save_html, exist_ok=True)
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(response)
            logger.info(f"Saved response to {full_path}")
        except Exception as e:
            logger.error(f"Error saving file {full_path}: {e}")
