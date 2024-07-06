current_status = {
    'status': 'idle',
    'pages_extracted': 0,
    'total_pages': 0,
    'current_url': None,
    'depth': 0
}

def update_status(status=None, pages_extracted=None, total_pages=None, current_url=None, depth=None):
    global current_status
    if status is not None:
        current_status['status'] = status
    if pages_extracted is not None:
        current_status['pages_extracted'] = pages_extracted
    if total_pages is not None:
        current_status['total_pages'] = total_pages
    if current_url is not None:
        current_status['current_url'] = current_url
    if depth is not None:
        current_status['depth'] = depth
        