"""Roda no GitHub (tarefa "Publicar site"): monta o site em _site/ e destranca os vídeos
agendados cuja hora já passou. Feito por ferramentas/atualizar_site.py (canal CaveirIA).

Saída para o GitHub: publicar=true/false (na tarefa de 15 em 15 min, só publica se algo novo foi liberado).
"""
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "_site"
MARCA = "<!--AGENDADOS-->"
SITE_NO_AR = "https://caveiria.github.io/liberados.txt"

agora = dt.datetime.now(dt.timezone.utc)
if os.environ.get("AGORA_TESTE"):  # só para teste no PC
    agora = dt.datetime.fromisoformat(os.environ["AGORA_TESTE"])

shutil.rmtree(SAIDA, ignore_errors=True)
shutil.copytree(RAIZ, SAIDA, ignore=shutil.ignore_patterns(
    ".git", ".github", "agendado", "_site", ".gitignore", ".gitattributes", ".gerado"))

agenda_arq = RAIZ / "agendado" / "agenda.json"
agenda = json.loads(agenda_arq.read_text(encoding="utf-8")) if agenda_arq.exists() else []
chave = os.environ.get("SITE_CHAVE")
liberados, cartoes = [], []

prontos = [e for e in agenda if dt.datetime.fromisoformat(e["sai"]) <= agora]
if prontos and not chave:
    print("::warning::Tem vídeo para liberar, mas falta o segredo SITE_CHAVE no GitHub.")
    prontos = []

for e in sorted(prontos, key=lambda e: e["sai"], reverse=True):
    r = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "200000",
                        "-pass", "env:SITE_CHAVE", "-in", str(RAIZ / "agendado" / e["arquivo"])],
                       capture_output=True)
    if r.returncode != 0:
        print(f"::error::Não consegui destrancar {e['arquivo']} (senha diferente?)")
        continue
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(r.stdout)) as t:
            t.extractall(tmp, filter="data")
        tmp = Path(tmp)
        slug = (tmp / "slug.txt").read_text(encoding="utf-8").strip()
        shutil.copytree(tmp / slug, SAIDA / slug, dirs_exist_ok=True)
        cartoes.append((tmp / "card.html").read_text(encoding="utf-8"))
    liberados.append(e["arquivo"])
    print(f"Liberado: /{slug}/ (hora: {e['sai']})")

indice = SAIDA / "index.html"
html = indice.read_text(encoding="utf-8")
indice.write_text(html.replace(MARCA, MARCA + "".join(cartoes), 1), encoding="utf-8")
estado = "\n".join(sorted(liberados)) + "\n"
(SAIDA / "liberados.txt").write_text(estado, encoding="utf-8")

# na tarefa de 15 em 15 min, só publica se mudou algo em relação ao site no ar
publicar = True
if os.environ.get("GITHUB_EVENT_NAME") == "schedule":
    try:
        no_ar = urllib.request.urlopen(SITE_NO_AR, timeout=20).read().decode("utf-8")
        publicar = no_ar != estado
    except Exception as erro:  # sem conseguir ler o site no ar: publica por garantia
        print("Não li o site no ar:", erro)
print(f"{len(liberados)} liberados, {len(agenda) - len(liberados)} ainda trancados. Publicar: {publicar}")
saida_gh = os.environ.get("GITHUB_OUTPUT")
if saida_gh:
    with open(saida_gh, "a", encoding="utf-8") as f:
        f.write(f"publicar={'true' if publicar else 'false'}\n")
