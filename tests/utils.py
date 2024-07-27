def calculate_pages(total: int, size: int) -> int:
    """рассчитать pages.

    Получаем Pages по total, size параметрам.
    """
    if total > size:
        return total // size + (1 if total % size else 0)
    else:
        return 1
