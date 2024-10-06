class MangaRelease:
    """Represents a manga release"""

    def __init__(self, title: str, link: str, release_date: str, publisher: str):
        self.title = title
        self.link = link
        self.release_date = release_date
        self.publisher = publisher

    def __repr__(self):
        return (
            f"MangaRelease(\n"
            f" title: {self.title},\n"
            f" link: {self.link},\n"
            f" release_date: {self.release_date},\n"
            f" publisher: {self.publisher}\n"
            f")"
        )
