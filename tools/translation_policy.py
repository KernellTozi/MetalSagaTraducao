"""Local terminology checks. Explicit names only; not a substitute for review."""
import json
import re
from pathlib import Path

POLICY_PATH=Path(__file__).resolve().parents[1]/'translations/politica.json'


def occurrences(text,term,case_sensitive=False):
    # A proper name can wrap across lines; matching must survive reflow.
    text=re.sub(r'\s+',' ',text)
    term=re.sub(r'\s+',' ',term)
    # Permit normal English plural for protected professions and loanwords.
    suffix='s?' if term.lower() in ('hunter','soldier','punk','upgrade') else ''
    return len(re.findall(r'(?<!\w)'+re.escape(term)+suffix+r'(?!\w)',text,
                          0 if case_sensitive else re.IGNORECASE))


def validate(source,target,policy=None):
    policy=policy or json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    issues=[]
    for term in policy['protected_terms']+policy['protected_names']:
        sensitive=term in policy.get('case_sensitive_names',[])
        before=occurrences(source,term,sensitive)
        if before and occurrences(target,term,sensitive)<before:
            issues.append(f'Termo/nome protegido ausente: {term}')
    for term in policy['forbidden_targets']:
        if occurrences(target,term):issues.append(f'Termo não autorizado: {term}')
    material_source=source
    for name in sorted(policy['protected_names'],key=len,reverse=True):
        pattern=r'(?<!\w)'+r'\s+'.join(map(re.escape,name.split()))+r'(?!\w)'
        flags=0 if name in policy.get('case_sensitive_names',[]) else re.IGNORECASE
        material_source=re.sub(pattern,' ',material_source,flags=flags)
    for term,replacement in policy['required_translations'].items():
        if occurrences(material_source,term) and not occurrences(target,replacement):
            issues.append(f'Tradução obrigatória: {term} -> {replacement}')
    # Longer expressions first; nested phrases are counted only once.
    patterns=sorted(policy['preserve_expressions'],key=len,reverse=True)
    regex=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(p) for p in patterns)+r')(?!\w)')
    expressions=regex.findall(source)+re.findall(r'\*[^*\r\n\t]+\*',source)
    for expression in set(expressions):
        if target.count(expression)<expressions.count(expression):
            issues.append(f'Expressão preservada ausente: {expression}')
    return sorted(set(issues))
