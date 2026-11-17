#!/usr/bin/env python3
"""
Script utilitário para gerar relatórios e dossiês de abordagem em PDF utilizando Chromium headless.
Uso:
    python3 generate_pdf.py --input /caminho/documento.html --output /caminho/saida.pdf
"""

import sys
import os
import argparse
import subprocess

def compile_pdf(input_html: str, output_pdf: str, chromium_path: str = "chromium"):
    if not os.path.exists(input_html):
        print(f"Erro: Arquivo HTML de entrada não encontrado: {input_html}")
        sys.exit(1)

    abs_input = os.path.abspath(input_html)
    abs_output = os.path.abspath(output_pdf)
    user_data_dir = "/tmp/chromium-data-lead-approach"
    os.makedirs(user_data_dir, exist_ok=True)

    cmd = [
        chromium_path,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={user_data_dir}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={abs_output}",
        abs_input
    ]

    print(f"Compilando PDF a partir de {abs_input}...")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if os.path.exists(abs_output) and os.path.getsize(abs_output) > 0:
            print(f"Sucesso! PDF gerado em: {abs_output} ({os.path.getsize(abs_output)} bytes)")
        else:
            print(f"Aviso: O arquivo PDF não foi gerado ou está vazio.")
            print(result.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar Chromium: {e}")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compilador de relatórios PDF com Chromium headless.")
    parser.add_argument("--input", "-i", required=True, help="Caminho do arquivo HTML de entrada.")
    parser.add_argument("--output", "-o", required=True, help="Caminho do arquivo PDF de saída.")
    parser.add_argument("--chromium", default="chromium", help="Caminho do executável do Chromium.")
    args = parser.parse_args()

    compile_pdf(args.input, args.output, args.chromium)
