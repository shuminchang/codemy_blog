from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='highlight')
def highlight(text, search):
    highlighted = re.sub(f'({re.escape(search)})', r'<mark>\1</mark>', text, flags=re.IGNORECASE)
    return mark_safe(highlighted)

@register.filter(name='excerpt')
def excerpt(text, search, char_count=50):
    # Escape special characters in the search string
    search_escaped = re.escape(search)

    # Find the serach string in the text
    match = re.search(f'({search_escaped})', text, flags=re.IGNORECASE)
    if not match:
        return text[:char_count * 2] + '...' # Return original text if no match is found
    
    start = max(match.start() - char_count, 0)
    end = min(match.end() + char_count, len(text))

    # Extract the surrounding text
    excerpt_text = text[start:end]
    print(excerpt_text)

    # Highlight the search term within the excerpt
    highlighted_excerpt = highlight(excerpt_text, search)

    # Add ellipses if the excerpt is not the full text
    if start > 0:
        highlighted_excerpt = '...' + highlighted_excerpt
    if end < len(text):
        highlighted_excerpt = highlighted_excerpt + '...'

    return mark_safe(highlighted_excerpt)