import glob
import re

sections = [
    'abstract_keywords.tex',
    'introduction.tex',
    'literature_review.tex',
    'dataset_preprocessing.tex',
    'methodology.tex',
    'experimental_setup.tex',
    'results_discussion.tex',
    'alert_system.tex',
    'conclusion_future_work.tex'
]

clean_parts = []
prose_only_parts = []

for sec in sections:
    with open('sections/' + sec, 'r', encoding='utf-8') as fp:
        text = fp.read()
    
    if sec == 'abstract_keywords.tex':
        abs_match = re.search(r'\\begin\{abstract\}([\s\S]*?)\\end\{abstract\}', text)
        key_match = re.search(r'\\begin\{IEEEkeywords\}([\s\S]*?)\\end\{IEEEkeywords\}', text)
        
        abs_text = abs_match.group(1).strip() if abs_match else ""
        key_text = key_match.group(1).strip() if key_match else ""
        
        clean_parts.append(f"Abstract: {abs_text}\n\nIndex Terms: {key_text}")
        continue

    # Strip figure environments, table environments, equations environments cleanly
    text_clean = re.sub(r'\\begin\{figure\}[\s\S]*?\\end\{figure\}', '', text)
    text_clean = re.sub(r'\\begin\{table\}[\s\S]*?\\end\{table\}', '', text_clean)
    text_clean = re.sub(r'\\begin\{equation\}[\s\S]*?\\end\{equation\}', '', text_clean)
    
    text_clean = re.sub(r'\\section\*?\{([^}]+)\}', r'\1\n', text_clean)
    text_clean = re.sub(r'\\subsection\*?\{([^}]+)\}', r'\1\n', text_clean)
    text_clean = re.sub(r'\\subsubsection\*?\{([^}]+)\}', r'\1\n', text_clean)
    text_clean = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text_clean)
    text_clean = re.sub(r'\\textit\{([^}]+)\}', r'\1', text_clean)
    text_clean = re.sub(r'\\cite\{[^}]+\}', '', text_clean)
    text_clean = re.sub(r'\\ref\{[^}]+\}', '', text_clean)
    text_clean = re.sub(r'\\begin\{[^}]+\}', '', text_clean)
    text_clean = re.sub(r'\\end\{[^}]+\}', '', text_clean)
    text_clean = re.sub(r'\\item\s*', '- ', text_clean)
    text_clean = re.sub(r'\\[a-zA-Z]+', '', text_clean)
    text_clean = text_clean.replace('{', '').replace('}', '').replace('``', '"').replace("''", '"')
    text_clean = re.sub(r'\[[^\]]+\]', '', text_clean)
    
    lines = [l.strip() for l in text_clean.splitlines() if l.strip() and not l.strip().startswith('label:') and not l.strip().startswith('fig:') and not l.strip().startswith('tab:')]
    clean_parts.append('\n\n'.join(lines))

full_clean_text = '\n\n'.join(clean_parts)
with open('smartgrid_sentinel_clean_text.txt', 'w', encoding='utf-8') as fp:
    fp.write(full_clean_text)

print('Clean text successfully generated!')

