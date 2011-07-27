def effective_page_range_for(page, paginator, delta=3):
    return [p for p in range(page.number - delta, page.number + delta + 1) 
                if (p > 0 and p <= paginator.num_pages)]
