"""Opt-in tank weapon category naming; never translate MAIN/SUB/SE."""
import re

POLICY='preserve-main-sub-se-v001'


def validate(source,target):
    source=re.sub(r'\s+',' ',source.replace('|',' '))
    target=target.replace('|',' ')
    rules={'MAIN':r'(?i:\bmain (?:gun|cannon)\b)|\bMAIN\b',
           'SUB':r'(?i:\bsub gun\b)|\bSUB\b','SE':r'\bSEs?\b'}
    issues=[]
    for term,pattern in rules.items():
        needed=len(re.findall(pattern,source))
        if source.strip() in ('Main','Sub') and source.strip().upper()==term:needed=1
        if not needed and term in ('MAIN','SUB') and re.search(r'\bmain vs\.? sub\b',source,re.IGNORECASE):needed=1
        if not needed and term in ('MAIN','SUB') and re.search(r'\b'+term+r'\s+%d',source,re.IGNORECASE):needed=1
        actual=len(re.findall(r'(?<!\w)'+term+r'(?:s)?(?!\w)',target))
        if actual<needed:issues.append(f'Categoria de armamento deve permanecer {term} ({actual}/{needed})')
    return issues
