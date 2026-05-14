def merge_sort(books, key=lambda x: x.title):
    """Sort books using merge sort algorithm based on a specified key."""
    if len(books) <= 1:
        return books

    # Split the list into halves
    mid = len(books) // 2
    left_half = merge_sort(books[:mid], key)  # Recursively sort the left half
    right_half = merge_sort(books[mid:], key) # Recursively sort the right half

    return merge(left_half, right_half, key)

def merge(left, right, key):
    """Merge two sorted lists based on a specified key."""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if key(left[i]).lower() <= key(right[j]).lower():
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result

def binary_search(books, target, key=lambda b: b.title):
    """
    Recursively search a SORTED list of books for target string.
    Returns the Book if found, None if not found.
    key — same interface as sort functions.
    """
    # Base case 1 — list is empty, not found
    if not books:
        return None

    mid      = len(books) // 2
    mid_val  = key(books[mid]).lower()
    target   = target.lower()

    # Base case 2 — found it
    if mid_val == target:
        return books[mid]

    # Recursive case — search the correct half
    if target < mid_val:
        return binary_search(books[:mid], target, key)      # search left
    else:
        return binary_search(books[mid + 1:], target, key)  # search right
    
    
def quick_sort(books, key=lambda b: b.title):
    """
    Sort a list of Book objects using quick sort.
    Same key interface as merge_sort for consistency.
    """
    # Base case — 0 or 1 items already sorted
    if len(books) <= 1:
        return books

    pivot = books[len(books) // 2]   # Pick middle item as pivot

    left   = [b for b in books if key(b).lower() <  key(pivot).lower()]
    middle = [b for b in books if key(b).lower() == key(pivot).lower()]
    right  = [b for b in books if key(b).lower() >  key(pivot).lower()]

    # Recursively sort each partition
    return quick_sort(left, key) + middle + quick_sort(right, key)

# services/algorithms.py

def recursive_count_overdue(books, index=0, count=0):
    """
    Recursively count overdue books.
    
    books — full list of Book objects
    index — which book we're currently checking (starts at 0)
    count — running total of overdue books found so far
    """

    # ── Base case ──────────────────────────────────────────────
    # We've checked every book — return the final count
    if index == len(books):
        return count

    # ── Check current book ─────────────────────────────────────
    # Does this book add 1 to the count or 0?
    current_book     = books[index]
    is_this_overdue  = 1 if current_book.is_overdue() else 0

    # ── Recursive case ─────────────────────────────────────────
    # Move to the NEXT book (index + 1)
    # Pass the UPDATED count forward
    return recursive_count_overdue(
        books,
        index + 1,              # next book
        count + is_this_overdue # updated count
    )
    
    
def sort_members_by_fines(members):
    """
    Sort a list of Member objects by outstanding fines.
    Highest fines appear first (descending order).
    Uses merge sort.
    """

    # Base case — 0 or 1 members already sorted
    if len(members) <= 1:
        return members

    # Split down the middle
    mid   = len(members) // 2
    left  = sort_members_by_fines(members[:mid])   # recursive call
    right = sort_members_by_fines(members[mid:])   # recursive call

    return _merge_members(left, right)


def _merge_members(left, right):
    """
    Merge two sorted member lists — highest fines first.
    Same logic as _merge() but:
      - compares get_total_fines() instead of titles
      - uses >= instead of <= for descending order
    """
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        left_fines  = left[i].get_total_fines()
        right_fines = right[j].get_total_fines()

        # >= puts the HIGHER fine first (descending)
        if left_fines >= right_fines:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result