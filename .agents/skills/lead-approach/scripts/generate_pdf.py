#!/usr/bin/env python3
"""
Compilador de relatórios e dossiês de abordagem em PDF utilizando Chromium/Chrome headless.
Compatível com Antigravity, Claude Code e OpenAI Codex no Linux e macOS.

Uso:
    python3 generate_pdf.py --input /caminho/documento.html --output /caminho/saida.pdf
"""

import sys
import os
import shutil
import argparse
import subprocess

CANDIDATE_BROWSERS = [
    "chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium-browser",
    "brave",
    "brave-browser",
    "microsoft-edge",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/snap/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
]

def find_browser(preferred: str = None) -> str:
    if preferred and shutil.which(preferred):
        return preferred
    if preferred and os.path.isfile(preferred) and os.access(preferred, os.X_OK):
        return preferred

    for b in CANDIDATE_BROWSERS:
        found = shutil.which(b)
        if found:
            return found
        if os.path.isfile(b) and os.access(b, os.X_OK):
            return b

    return None

def compile_pdf(input_html: str, output_pdf: str, chromium_path: str = None):
    if not os.path.exists(input_html):
        print(f"Erro: Arquivo HTML de entrada não encontrado: {input_html}")
        sys.exit(1)

    browser = find_browser(chromium_path)
    if not browser:
        print("Erro: Nenhum executável do Chromium ou Google Chrome encontrado no sistema.")
        print("Por favor, instale o Chromium ou forneça o caminho com a flag --chromium.")
        sys.exit(1)

    abs_input = os.path.abspath(input_html)
    abs_output = os.path.abspath(output_pdf)
    user_data_dir = "/tmp/chromium-data-lead-approach"
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(os.path.dirname(abs_output) or ".", exist_ok=True)

    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--user-data-dir={user_data_dir}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={abs_output}",
        abs_input
    ]

    print(f"Compilando PDF usando {browser}...")
    print(f"Origem: {abs_input}")
    print(f"Destino: {abs_output}")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if os.path.exists(abs_output) and os.path.getsize(abs_output) > 0:
            print(f"✅ Sucesso! PDF gerado em: {abs_output} ({os.path.getsize(abs_output)} bytes)")
        else:
            print(f"⚠️ Aviso: O arquivo PDF não foi gerado ou está vazio.")
            print(result.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar navegador: {e}")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compilador de relatórios PDF com Chromium headless.")
    parser.add_argument("--input", "-i", required=True, help="Caminho do arquivo HTML de entrada.")
    parser.add_argument("--output", "-o", required=True, help="Caminho do arquivo PDF de saída.")
    parser.add_argument("--chromium", default=None, help="Caminho específico do executável Chromium/Chrome.")
    args = parser.parse_args()

    compile_pdf(args.input, args.output, args.chromium)
