import questionary
from loguru import logger


class BaseCli:
    CUSTOM_STYLE = questionary.Style([
        ('question', 'bold'),
        ('answer', 'fg:#ff9900 bold'),
        ('pointer', 'fg:#ff9900 bold'),
        ('text', 'fg:#4d4d4d'),
        ('disabled', 'fg:#858585 italic')
    ])
    
    BOOL_OPTIONS = [
        (True, 'Да'),
        (False, 'Нет')
    ]

    @classmethod
    def _paginate_selection(cls, items: list[str], item_name: str, items_per_page: int=10) -> list[str]:
        total_pages = (len(items) + items_per_page - 1) // items_per_page
        current_page = 0
        selected_items: list[str] = []

        while current_page < total_pages:
            start = current_page * items_per_page
            end = min(start + items_per_page, len(items))
            page_items = items[start:end]

            selected_items_on_page = questionary.checkbox(
                f"Выбери {item_name} (страница {current_page + 1} из {total_pages})",
                choices=page_items,
                style=cls.CUSTOM_STYLE,
            ).ask()

            selected_items.extend(selected_items_on_page)

            current_page += 1

        return selected_items
