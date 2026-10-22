"""Local terminology checks. Explicit names only; not a substitute for review."""
import json
import re
from pathlib import Path

POLICY_PATH=Path(__file__).resolve().parents[1]/'translations/politica.json'


def occurrences(text,term):
    # A proper name can wrap across lines; matching must survive reflow.
    text=re.sub(r'\s+',' ',text)
    term=re.sub(r'\s+',' ',term)
    # Permit normal English plural for protected professions and loanwords.
    suffix='s?' if term.lower() in ('hunter','soldier','punk','upgrade') else ''
    return len(re.findall(r'(?<!\w)'+re.escape(term)+suffix+r'(?!\w)',text,re.IGNORECASE))


def validate(source,target,policy=None):
    policy=policy or json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    issues=[]
    for term in policy['protected_terms']+policy['protected_names']:
        before=occurrences(source,term)
        if before and occurrences(target,term)<before:
            issues.append(f'Termo/nome protegido ausente: {term}')
    for term in policy['forbidden_targets']:
        if occurrences(target,term):issues.append(f'Termo não autorizado: {term}')
    for term,replacement in policy['required_translations'].items():
        if occurrences(source,term) and not occurrences(target,replacement):
            issues.append(f'Tradução obrigatória: {term} -> {replacement}')
    # Longer expressions first; nested phrases are counted only once.
    patterns=sorted(policy['preserve_expressions'],key=len,reverse=True)
    regex=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(p) for p in patterns)+r')(?!\w)')
    expressions=regex.findall(source)+re.findall(r'\*[^*\r\n\t]+\*',source)
    for expression in set(expressions):
        if target.count(expression)<expressions.count(expression):
            issues.append(f'Expressão preservada ausente: {expression}')
    return sorted(set(issues))
