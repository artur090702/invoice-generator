import json
import re
import subprocess
import tempfile
from pathlib import Path

import pick
from jinja2 import Environment, FileSystemLoader

LOCAL_DIR = Path.home() / ".local" / "share" / "geninvoice"
TEMPLATE_DIR = LOCAL_DIR / "templates"
CLIENT_DIR = LOCAL_DIR / "clients"

_LATEX_SPECIAL = {
    '\\': r'\textbackslash{}',
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
}
_LATEX_ESCAPE_RE = re.compile('|'.join(re.escape(k) for k in _LATEX_SPECIAL))


def latex_escape(text: str) -> str:
    return _LATEX_ESCAPE_RE.sub(lambda m: _LATEX_SPECIAL[m.group()], str(text))


def _sanitize_strings(data: dict):
    def esc(s):
        return latex_escape(str(s))

    def esc_multiline(s):
        return latex_escape(str(s)).replace("\n", " \\\\\n")

    for key in ('invoice_number',):
        if key in data:
            data[key] = esc(data[key])

    if 'my_info' in data:
        data['my_info'] = esc_multiline(data['my_info'])

    client = data.get('client', {})
    for key in ('name', 'btw_id'):
        if key in client:
            client[key] = esc(client[key])
    if 'info' in client:
        client['info'] = esc_multiline(client['info'])

    for item in data.get('billed_items', []):
        for key in ('name', 'subtext', 'rate', 'quantity'):
            if key in item and isinstance(item[key], str):
                item[key] = esc(item[key])


def is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def prepare_data(data: dict):
    _sanitize_strings(data)
    data['amount'] = round(sum(item['amount'] for item in data['billed_items']), 2)
    match data['invoice_type']:
        case 'btw':
            data['btw_total'] = float(data['btw']) * data['amount'] / 100
        case 'marge':
            data |= {'marge': True, 'btw': 0, 'btw_total': 0.0}
        case 'verlegd':
            data |= {'verlegd': True, 'btw': 0, 'btw_total': 0.0}


def _fmt(value) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value) if value else ''


def compile_invoice(data: dict) -> bytes:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.filters['fmt'] = _fmt
    safe_number = re.sub(r'[^a-zA-Z0-9_\-]', '_', str(data['invoice_number'])) or 'invoice'

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        for filename in ['preamble.tex', 'myinfo.tex']:
            (tmp / filename).write_text(env.get_template(filename).render(data), encoding='utf-8')

        tex_file = tmp / f"{safe_number}.tex"
        tex_file.write_text(env.get_template('template.tex').render(data), encoding='utf-8')

        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_file],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(e.stdout)
            print(e.stderr, flush=True)
            raise

        return (tmp / f"{safe_number}.pdf").read_bytes()


def generate_pdf(data: dict) -> bytes:
    prepare_data(data)
    return compile_invoice(data)
