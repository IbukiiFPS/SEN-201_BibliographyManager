
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple
from ..db import BibliographyDB

class EntriesService:
    def __init__(self, db: BibliographyDB) -> None:
        self.db = db

    def add(self, data: Dict[str, Any]) -> int:
        self._validate(data)
        return self.db.add_entry(**data)

    def update(self, entry_id: int, data: Dict[str, Any]) -> None:
        self._validate(data, partial=True)
        self.db.update_entry(entry_id, **data)

    def remove(self, entry_id: int) -> None:
        self.db.delete_entry(entry_id)

    def list(self, where: Optional[str] = None, params: Sequence[Any] = ()) -> List[Tuple]:
        return self.db.list_entries(where, params)

    def get(self, entry_id: int):
        return self.db.get_entry(entry_id)

    def search_query(self, q: str) -> Tuple[str, Sequence[Any]]:
        q = q.strip()
        if not q:
            return "", ()
        if q.startswith('tag:'):
            tag = q[len('tag:'):].strip()
            return 'tags LIKE ?', (f'%{tag}%',)
        if re.match(r'^\d{4}(-\d{2}-\d{2})?$', q):
            # year or date -> search by year only
            return 'year = ?', (int(q.split('-')[0]),)
        # general search
        p = f'%{q}%'
        return '(authors LIKE ? OR title LIKE ? OR tags LIKE ? OR venue LIKE ?)', (p, p, p, p)

    def _validate(self, data: Dict[str, Any], partial: bool = False) -> None:
        # Basic validation rules matching the single-file version
        if not partial:
            if not data.get('authors', '').strip() or not data.get('title', '').strip():
                raise ValueError('Authors and Title are required')
        year = data.get('year')
        if isinstance(year, str) and year.strip() == '':
            data['year'] = None
        elif year is not None:
            if isinstance(year, str):
                if not re.match(r'^\d{4}$', year):
                    raise ValueError('Year must be a 4-digit year')
                data['year'] = int(year)
            elif isinstance(year, int):
                if year < 0 or year > 9999:
                    raise ValueError('Year must be a 4-digit year')
            else:
                raise ValueError('Year must be an integer or 4-digit string')
