#!/usr/bin/env python3
"""Validación de Forte Foundation.

Comprueba lo que JSON Schema no puede expresar además de validar contra los schemas:

  catálogo   ids únicos · requires/extends apuntan a bloques existentes · variantes con extends ·
             familias coherentes con el schema · bloques no candidate tienen carpeta en blocks/
  block.yaml todo blocks/<id>/block.yaml valida y su id coincide con la carpeta y con el catálogo
  manifests  ids únicos · bloques existen en el catálogo · dependency closure (todo requires de un
             bloque copiado tiene entrada) · solo se copian bloques draft/stable (omitido en examples/)
  enlaces    enlaces relativos y anclas de todos los .md resuelven

Uso:  python3 scripts/validate.py            (todo el repositorio)
      python3 scripts/validate.py ruta.yaml  (uno o más manifests concretos)
Requiere: pip install pyyaml jsonschema
"""
import glob
import json
import os
import re
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIABLE = {"draft", "stable"}
errors = []


def err(msg):
    errors.append(msg)
    print(f"  ✗ {msg}")


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schema(name):
    with open(os.path.join(ROOT, "spec", "schemas", name), encoding="utf-8") as f:
        return json.load(f)


def validate_schema(schema, data, label):
    v = Draft202012Validator(schema, format_checker=FormatChecker())
    found = sorted(v.iter_errors(data), key=lambda e: list(e.path))
    for e in found:
        where = "/".join(map(str, e.path)) or "<root>"
        err(f"{label} [{where}]: {e.message[:220]}")
    return not found


def rel(path):
    return os.path.relpath(path, ROOT)


# ---------------------------------------------------------------- catálogo
def check_catalog():
    path = os.path.join(ROOT, "registry", "catalog.yaml")
    cat = load_yaml(path)
    ok = validate_schema(load_schema("catalog.schema.json"), cat, "catalog")
    blocks = cat.get("blocks", [])
    ids = [b["id"] for b in blocks]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        err(f"catalog: id duplicado {dup}")
    known = set(ids)
    schema_families = set(load_schema("block.schema.json")["$defs"]["family"]["enum"])
    if set(cat.get("families", {})) != schema_families:
        err("catalog: las familias definidas no coinciden con el enum de block.schema.json")
    for b in blocks:
        refs = list(b.get("requires", {})) + ([b["extends"]] if "extends" in b else [])
        for r in refs:
            if r not in known:
                err(f"catalog: {b['id']} referencia un bloque inexistente: {r}")
        if b["status"] != "candidate":
            bdir = os.path.join(ROOT, b.get("path", ""))
            if not b.get("path") or not os.path.isfile(os.path.join(bdir, "block.yaml")):
                err(f"catalog: {b['id']} tiene status {b['status']} pero no existe {b.get('path')}/block.yaml")
    print(f"{'OK  ' if ok and not errors else 'FAIL'} catálogo: {len(blocks)} bloques")
    return {b["id"]: b for b in blocks}


# ---------------------------------------------------------------- bloques
def check_blocks(catalog):
    schema = load_schema("block.schema.json")
    before = len(errors)
    for path in sorted(glob.glob(os.path.join(ROOT, "blocks", "*", "block.yaml"))):
        folder = os.path.basename(os.path.dirname(path))
        data = load_yaml(path)
        label = f"block {rel(path)}"
        validate_schema(schema, data, label)
        if folder == "_template":
            continue
        if data.get("id") != folder:
            err(f"{label}: id {data.get('id')} no coincide con la carpeta {folder}")
        entry = catalog.get(data.get("id"))
        if entry is None:
            err(f"{label}: no está en el catálogo")
        else:
            if entry["status"] != data.get("status"):
                err(f"{label}: status {data.get('status')} difiere del catálogo ({entry['status']})")
            if entry.get("latest_version") != data.get("version"):
                err(f"{label}: version {data.get('version')} difiere de latest_version del catálogo")
    print(f"{'OK  ' if len(errors) == before else 'FAIL'} bloques")


# ---------------------------------------------------------------- manifests
def check_manifest(path, catalog):
    data = load_yaml(path)
    label = f"manifest {rel(path)}"
    before = len(errors)
    validate_schema(load_schema("manifest.schema.json"), data, label)
    entries = data.get("blocks", [])
    ids = [e["id"] for e in entries]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        err(f"{label}: id duplicado {dup} (una entrada por bloque copiado)")
    copied = set(ids)
    illustrative = rel(path).startswith("examples" + os.sep)
    for e in entries:
        entry = catalog.get(e["id"])
        if entry is None:
            err(f"{label}: {e['id']} no existe en el catálogo")
            continue
        if not illustrative and entry["status"] not in COPIABLE:
            err(f"{label}: {e['id']} tiene status {entry['status']} y no es copiable")
        for dep in entry.get("requires", {}):
            if dep not in copied:
                err(f"{label}: {e['id']} requiere {dep} pero no hay entrada para él (dependency closure)")
        if "extends" in entry and entry["extends"] not in copied:
            err(f"{label}: {e['id']} extiende {entry['extends']} pero no hay entrada para él")
    note = " (ilustrativo: se omite la comprobación de estado copiable)" if illustrative else ""
    print(f"{'OK  ' if len(errors) == before else 'FAIL'} {label}{note}")


# ---------------------------------------------------------------- enlaces
def check_links():
    before = len(errors)
    total = 0
    for md in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
        if os.sep + ".git" + os.sep in md:
            continue
        text = re.sub(r"```.*?```", "", open(md, encoding="utf-8").read(), flags=re.S)
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
            link = m.group(1)
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            total += 1
            target_path, _, anchor = link.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(md), target_path)) if target_path else md
            if not os.path.exists(target):
                err(f"{rel(md)}: enlace roto {link}")
                continue
            if anchor and target.endswith(".md"):
                body = open(target, encoding="utf-8").read()
                heads = [re.sub(r"[^\w\s-]", "", h.lower()).strip().replace(" ", "-")
                         for h in re.findall(r"^#+\s+(.*)$", body, flags=re.M)]
                if anchor not in heads:
                    err(f"{rel(md)}: ancla #{anchor} no existe en {rel(target)}")
    print(f"{'OK  ' if len(errors) == before else 'FAIL'} enlaces: {total} comprobados")


def main(argv):
    catalog = check_catalog()
    if argv:
        for p in argv:
            check_manifest(os.path.abspath(p), catalog)
    else:
        check_blocks(catalog)
        for p in sorted(glob.glob(os.path.join(ROOT, "examples", "*.manifest.yaml"))):
            check_manifest(p, catalog)
        check_links()
    print(f"\n{'TODO OK' if not errors else f'{len(errors)} error(es)'}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
