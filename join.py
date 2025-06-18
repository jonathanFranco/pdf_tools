import os
from shutil import which
import sys
import re
from datetime import datetime
import subprocess

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    qpdf_path = os.path.join(base_dir, 'qpdf/qpdf.exe')
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qpdf_path = which('qpdf') or which('qpdf/qpdf.exe')

if not os.path.exists(qpdf_path):
    print("❌ O qpdf.exe não foi encontrado.")
    sys.exit(1)

print(f"📂 Pasta base: {base_dir}")

output = os.path.join(base_dir, 'output')
os.makedirs(output, exist_ok=True)


pdfs_peer_people = {}

for root, dirs, files in os.walk(base_dir):
    if 'output' in root.lower():
        continue
    for file in files:
        if file.lower().endswith('.pdf'):
            path = os.path.join(root, file)
            base_name = file.split('-')[0].strip().lower()

            if base_name not in pdfs_peer_people:
                pdfs_peer_people[base_name] = []
            pdfs_peer_people[base_name].append(path)
            print(f"📄 Coletado para '{base_name}': {path}")

def extract_folder_order(path):
    folder = os.path.basename(os.path.dirname(path))
    match = re.match(r'^(\d+)', folder)
    return int(match.group(1)) if match else 9999

for person, files in pdfs_peer_people.items():
    print(f"\n🔗 Juntando arquivos para '{person}':")
    files_sorted = sorted(files, key=extract_folder_order)
    valid_files = []
    for pdf in files_sorted:
        pdf_base_name = os.path.basename(pdf).split('-')[0].strip().lower()
        if pdf_base_name == person:
            valid_files.append(pdf)
        else:
            print(f"⚠️  Arquivo ignorado por nome diferente: {pdf}")
    if not valid_files:
        print(f"❌ Nenhum arquivo válido para '{person}', pulando...")
        continue
    for pdf in valid_files:
        print(f"  👉 {pdf}")

    safe_name = person.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_path = os.path.join(output, f"{safe_name}_{timestamp}.pdf")

    cmd = [qpdf_path, '--empty', '--pages'] + valid_files + ['--', output_path]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ PDF final salvo: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao juntar PDFs para '{person}': {e}")

input("\n✅ Tudo finalizado! Pressione ENTER para sair…")
