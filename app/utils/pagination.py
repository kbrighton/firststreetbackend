class SimplePagination:
    """
    A simple pagination class that mimics Flask-SQLAlchemy's Pagination object.
    This can be used when manual pagination is needed outside of SQLAlchemy queries.
    """
    
    def __init__(self, items, page, per_page, total):
        """
        Initialize a pagination object.
        
        Args:
            items: The items for the current page
            page: The current page number (1-indexed)
            per_page: The number of items per page
            total: The total number of items
        """
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """
        Iterate over the page numbers in the pagination.
        
        Args:
            left_edge: Number of pages to show at the beginning
            left_current: Number of pages to show before current page
            right_current: Number of pages to show after current page
            right_edge: Number of pages to show at the end
            
        Returns:
            Generator yielding page numbers or None for gaps
        """
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num