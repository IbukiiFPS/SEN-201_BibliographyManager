
import re
from typing import Dict, Optional

def escape_bibtex(s: str) -> str:
    if s is None:
        return ""
    # Minimal escaping for braces, percent, and backslashes
    return s.replace('\\', '\\\\').replace('{', r'\{').replace('}', r'\}').replace('%', r'\%')

def entry_to_bibtex(entry: Dict, bibkey: Optional[str] = None) -> str:
    # Heuristic key: authorLastNameYearTitleword
    if bibkey is None:
        author = entry.get('authors', '') or ''
        year = entry.get('year') or 'n.d.'
        m = re.search(r"([A-Za-z'-]+)(?:\s|$)", author)
        last = m.group(1) if m else 'anon'
        titleword = re.sub(r"[^A-Za-z]", '', (entry.get('title') or 'untitled'))[:6]
        bibkey = f"{last}{year}{titleword}".lower()

    bibtype = 'article' if entry.get('venue') else 'misc'
    fields = {
        'author': entry.get('authors'),
        'title': entry.get('title'),
        'journal': entry.get('venue'),
        'year': entry.get('year'),
        'volume': entry.get('volume'),
        'number': entry.get('number'),
        'pages': entry.get('pages'),
        'doi': entry.get('doi'),
        'url': entry.get('url'),
    }
    lines = [f"@{bibtype}{{{bibkey},"]
    # Only include non-empty fields
    non_empty = [(k, v) for k, v in fields.items() if v is not None and str(v).strip() != '']
    for i, (k, v) in enumerate(non_empty):
        val = escape_bibtex(str(v))
        comma = ',' if i < len(non_empty) - 1 else ''
        lines.append(f"  {k} = {{{val}}}{comma}")
    lines.append('}')
    return "\n".join(lines)
