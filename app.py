import io
import re

from flask import Flask, jsonify, request, send_file

import invoice

app = Flask(__name__, static_folder='demo')
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

REQUIRED_FIELDS = ['invoice_number', 'invoice_type', 'billed_items', 'client', 'my_info']
VALID_INVOICE_TYPES = ('btw', 'marge', 'verlegd')

URL_PREFIX="/invoice_generator"

@app.route(f'{URL_PREFIX}/')
def serve_home():
    return app.send_static_file('index.html')


@app.post(f'{URL_PREFIX}/generate')
def generate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    if data['invoice_type'] not in VALID_INVOICE_TYPES:
        return jsonify({'error': 'Invalid invoice_type'}), 400

    safe_filename = re.sub(r'[^\w.\-]', '_', str(data['invoice_number'])) or 'invoice'

    try:
        pdf_bytes = invoice.generate_pdf(data)
    except Exception:
        app.logger.exception("PDF generation failed")
        return jsonify({'error': 'Failed to generate invoice'}), 500

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{safe_filename}.pdf",
    )


def start(host='0.0.0.0', port=8080, debug=False):
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start()
