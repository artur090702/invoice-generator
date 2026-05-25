# invoice-generator

Interactive CLI tool for generating PDF invoices from a LaTeX template.
Supports standard BTW, marge, and BTW-verlegd.

## Requirements

- Python 3.10+
- pdflatex (TeX Live)

**Arch Linux:**
```
sudo pacman -S texlive-basic texlive-latexrecommended
```

**Debian/Ubuntu:**
```
sudo apt install texlive-latex-recommended
```

## Installation

```bash
./install.sh
```

After installing, edit your business info:
```
~/.local/share/geninvoice/templates/myinfo.tex
```

## Usage

```bash
invoice-generator
```

The tool walks you through the following prompts:

| Prompt | Description |
|--------|-------------|
| Factuur nummer | Invoice number (e.g. `2024-001`) |
| Klant | Pick an existing client or add a new one |
| Factuurtype | `btw` / `marge` / `verlegd` |
| BTW percentage | If type is `btw` |
| Line items | Repeat until done: rate, quantity, service name, subtext |

The generated PDF is written to the current directory as `<invoice_number>.pdf`.

## Client data

Client records are stored as pickle files under `~/.local/share/geninvoice/clients/`.
Each record contains the client's name, BTW-id, and address block.
New clients can be added interactively when running the tool.
