#!/usr/bin/env python3
"""Validación de Forte Foundation.

Comprueba lo que JSON Schema no puede expresar además de validar contra los schemas:

  YAML       claves duplicadas en cualquier mapping se rechazan (PyYAML las sobrescribiría en silencio)
  catálogo   ids únicos · requires/extends apuntan a bloques existentes · extends también está en requires ·
             familias coherentes con el schema · path canónico blocks/<id> con block.yaml del mismo id ·
             un candidate no tiene directorio en blocks/ · stable >= 1.0.0 con precedencia SemVer real
  blocks/    todo directorio corresponde a un bloque no candidate del catálogo (salvo _template)
  block.yaml valida · sin drift respecto al catálogo (id, family, variant, extends, requires, status,
             version, decision_mode, default_for, providers) · extends también en requires ·
             stable con integration y tests que existen · stable >= 1.0.0 real
  manifests  ids únicos · bloques existen en el catálogo · variant coincide con el catálogo ·
             dependency closure (todo requires/extends de un bloque copiado tiene entrada) ·
             nunca un candidate (deprecated sí: una copia existente sigue siendo válida; omitido en examples/)
  enlaces    enlaces relativos y anclas de todos los .md resuelven

Un archivo estructuralmente inválido se reporta y se salta sus comprobaciones semánticas; nunca
aborta el proceso ni impide validar el resto. El proceso termina con exit code 1 si hay errores.

Uso:  python3 scripts/validate.py                       (todo el repositorio)
      python3 scripts/validate.py ruta.yaml [...]       (uno o más manifests concretos)
      python3 scripts/validate.py --root DIR [...]      (otro checkout, usado por los tests)
Requiere: pip install pyyaml jsonschema
"""
import glob
import json
import os
import re
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker

COPIABLE_NEW = {"draft", "stable"}            # seleccionables para una instalación nueva
VALID_IN_MANIFEST = {"draft", "stable", "deprecated"}  # válidos como copia ya existente
DRIFT_FIELDS = ("id", "family", "variant", "extends", "requires", "status",
                "decision_mode", "default_for", "providers")

# SemVer 2.0.0 con dígitos ASCII únicamente (\d en Python también acepta dígitos Unicode).
SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)
ASCII_DIGITS = re.compile(r"^[0-9]+$")


def semver_key(version):
    """Clave de precedencia SemVer 2.0.0. None si la versión no es válida.

    Una prerelease precede a la versión normal (1.0.0-rc.1 < 1.0.0); los identificadores numéricos
    preceden a los alfanuméricos; más identificadores gana si los anteriores son iguales; build se ignora.
    """
    m = SEMVER_RE.match(version or "")
    if not m:
        return None
    core = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    pre = m.group(4)
    if pre is None:
        return (core, 1, ())
    ids = tuple((0, int(p), "") if ASCII_DIGITS.match(p) else (1, 0, p) for p in pre.split("."))
    return (core, 0, ids)


STABLE_MIN = semver_key("1.0.0")


# ---------------------------------------------------------------- YAML sin claves duplicadas
class DuplicateKeyError(yaml.YAMLError):
    pass


class StrictLoader(yaml.SafeLoader):
    """SafeLoader que rechaza claves duplicadas en cualquier mapping."""

    def construct_mapping(self, node, deep=False):
        seen = {}
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise DuplicateKeyError(
                    f"clave duplicada '{key}' (líneas {seen[key]} y {key_node.start_mark.line + 1})")
            seen[key] = key_node.start_mark.line + 1
        return super().construct_mapping(node, deep=deep)


class Validator:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.errors = []
        self._schemas = {}

    # ------------------------------------------------------------ utilidades
    def err(self, msg):
        self.errors.append(msg)
        print(f"  ✗ {msg}")

    def rel(self, path):
        return os.path.relpath(path, self.root)

    def load_yaml(self, path):
        """Devuelve el documento o None tras reportar el error (sintaxis, clave duplicada, lectura)."""
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.load(f, Loader=StrictLoader)
        except (OSError, yaml.YAMLError) as e:
            self.err(f"{self.rel(path)}: YAML inválido: {str(e).strip().splitlines()[0]}")
            return None

    def schema(self, name):
        if name not in self._schemas:
            with open(os.path.join(self.root, "spec", "schemas", name), encoding="utf-8") as f:
                self._schemas[name] = json.load(f)
        return self._schemas[name]

    def validate_schema(self, schema_name, data, label):
        v = Draft202012Validator(self.schema(schema_name), format_checker=FormatChecker())
        found = sorted(v.iter_errors(data), key=lambda e: list(e.path))
        for e in found:
            where = "/".join(map(str, e.path)) or "<root>"
            self.err(f"{label} [{where}]: {e.message[:220]}")
        return not found

    def status_line(self, before, text):
        print(f"{'OK  ' if len(self.errors) == before else 'FAIL'} {text}")

    def check_stable_version(self, label, status, version):
        if status == "stable":
            key = semver_key(version)
            if key is None or key < STABLE_MIN:
                self.err(f"{label}: status stable exige version >= 1.0.0 con precedencia SemVer real "
                         f"({version} no cumple; 1.0.0-rc.1 precede a 1.0.0)")

    def check_extends_in_requires(self, label, data):
        base = data.get("extends")
        if base and base not in (data.get("requires") or {}):
            self.err(f"{label}: extends {base} debe aparecer también en requires con un rango de versión")

    # ------------------------------------------------------------ catálogo
    def check_catalog(self):
        """Devuelve {id: entrada} o None si el catálogo no puede usarse."""
        before = len(self.errors)
        path = os.path.join(self.root, "registry", "catalog.yaml")
        cat = self.load_yaml(path)
        if not isinstance(cat, dict) or not self.validate_schema("catalog.schema.json", cat, "catalog"):
            self.status_line(before, "catálogo: inválido, se omiten las comprobaciones que dependen de él")
            return None
        blocks = cat.get("blocks", [])
        ids = [b["id"] for b in blocks]
        for dup in sorted({i for i in ids if ids.count(i) > 1}):
            self.err(f"catalog: id duplicado {dup}")
        known = set(ids)
        schema_families = set(self.schema("block.schema.json")["$defs"]["family"]["enum"])
        if set(cat.get("families", {})) != schema_families:
            self.err("catalog: las familias definidas no coinciden con el enum de block.schema.json")
        for b in blocks:
            bid = b["id"]
            for r in list(b.get("requires", {})) + ([b["extends"]] if "extends" in b else []):
                if r not in known:
                    self.err(f"catalog: {bid} referencia un bloque inexistente: {r}")
            self.check_extends_in_requires(f"catalog: {bid}", b)
            block_dir = os.path.join(self.root, "blocks", bid)
            if b["status"] == "candidate":
                if os.path.isdir(block_dir):
                    self.err(f"catalog: {bid} es candidate pero existe blocks/{bid}/ "
                             "(un candidate no tiene implementación en Foundation)")
                continue
            self.check_stable_version(f"catalog: {bid}", b["status"], b.get("latest_version"))
            expected = f"blocks/{bid}"
            if b.get("path") != expected:
                self.err(f"catalog: {bid} tiene path {b.get('path')!r}; debe ser exactamente {expected!r}")
            descriptor = os.path.join(self.root, b.get("path") or expected, "block.yaml")
            if not os.path.isfile(descriptor):
                self.err(f"catalog: {bid} tiene status {b['status']} pero no existe {self.rel(descriptor)}")
            else:
                data = self.load_yaml(descriptor)
                if isinstance(data, dict) and data.get("id") != bid:
                    self.err(f"catalog: {bid} apunta a {self.rel(descriptor)} cuyo id es {data.get('id')!r}")
        self.status_line(before, f"catálogo: {len(blocks)} bloques")
        return {b["id"]: b for b in blocks}

    # ------------------------------------------------------------ bloques
    def check_blocks(self, catalog):
        before = len(self.errors)
        blocks_dir = os.path.join(self.root, "blocks")
        for name in sorted(os.listdir(blocks_dir)) if os.path.isdir(blocks_dir) else []:
            folder = os.path.join(blocks_dir, name)
            if not os.path.isdir(folder) or name == "_template":
                continue
            entry = catalog.get(name)
            if entry is None:
                self.err(f"blocks/{name}/: directorio sin entrada en el catálogo")
            elif entry["status"] == "candidate":
                self.err(f"blocks/{name}/: directorio de un bloque candidate (ya reportado en el catálogo)")
            if not os.path.isfile(os.path.join(folder, "block.yaml")):
                self.err(f"blocks/{name}/: directorio sin block.yaml")
        for path in sorted(glob.glob(os.path.join(blocks_dir, "*", "block.yaml"))):
            self.check_block(path, catalog)
        self.status_line(before, "bloques")

    def check_block(self, path, catalog):
        folder = os.path.basename(os.path.dirname(path))
        label = f"block {self.rel(path)}"
        data = self.load_yaml(path)
        if not isinstance(data, dict) or not self.validate_schema("block.schema.json", data, label):
            return
        self.check_extends_in_requires(label, data)
        self.check_stable_version(label, data.get("status"), data.get("version"))
        if data.get("status") == "stable":
            for field in ("integration", "tests"):
                target = os.path.join(os.path.dirname(path), data.get(field, ""))
                if not data.get(field) or not os.path.exists(target):
                    self.err(f"{label}: status stable exige {field} apuntando a una ruta existente "
                             f"({data.get(field)!r})")
        if folder == "_template":
            return
        if data.get("id") != folder:
            self.err(f"{label}: id {data.get('id')!r} no coincide con la carpeta {folder}")
        entry = catalog.get(folder)
        if entry is None:
            return  # ya reportado en check_blocks
        for field in DRIFT_FIELDS:
            mine, theirs = data.get(field), entry.get(field)
            if field == "requires":
                mine, theirs = dict(mine or {}), dict(theirs or {})
            if field == "providers":
                mine, theirs = sorted(mine or []), sorted(theirs or [])
            if mine != theirs:
                self.err(f"{label}: drift en {field}: block.yaml={mine!r} catálogo={theirs!r}")
        if entry.get("latest_version") != data.get("version"):
            self.err(f"{label}: drift en version: block.yaml={data.get('version')!r} "
                     f"catálogo latest_version={entry.get('latest_version')!r}")

    # ------------------------------------------------------------ manifests
    def check_manifest(self, path, catalog):
        before = len(self.errors)
        label = f"manifest {self.rel(path)}"
        data = self.load_yaml(path)
        if not isinstance(data, dict) or not self.validate_schema("manifest.schema.json", data, label):
            self.status_line(before, f"{label} (inválido: se omiten las comprobaciones semánticas)")
            return
        entries = data.get("blocks", [])
        ids = [e["id"] for e in entries]
        for dup in sorted({i for i in ids if ids.count(i) > 1}):
            self.err(f"{label}: id duplicado {dup} (una entrada por bloque copiado)")
        copied = set(ids)
        illustrative = self.rel(path).startswith("examples" + os.sep)
        for e in entries:
            entry = catalog.get(e["id"])
            if entry is None:
                self.err(f"{label}: {e['id']} no existe en el catálogo")
                continue
            if entry["status"] not in VALID_IN_MANIFEST and not illustrative:
                self.err(f"{label}: {e['id']} tiene status {entry['status']}; un candidate nunca se copia")
            if e.get("variant") != entry.get("variant"):
                self.err(f"{label}: {e['id']} registra variant {e.get('variant')!r} "
                         f"pero el catálogo lo define como {entry.get('variant')!r}")
            for dep in entry.get("requires", {}):
                if dep not in copied:
                    self.err(f"{label}: {e['id']} requiere {dep} pero no hay entrada para él (dependency closure)")
            if "extends" in entry and entry["extends"] not in copied:
                self.err(f"{label}: {e['id']} extiende {entry['extends']} pero no hay entrada para él")
        note = " (ilustrativo: se omite la comprobación de estado copiable)" if illustrative else ""
        self.status_line(before, f"{label}{note}")

    # ------------------------------------------------------------ enlaces
    def check_links(self):
        before = len(self.errors)
        total = 0
        for md in glob.glob(os.path.join(self.root, "**", "*.md"), recursive=True):
            if os.sep + ".git" + os.sep in md:
                continue
            with open(md, encoding="utf-8") as f:
                text = re.sub(r"```.*?```", "", f.read(), flags=re.S)
            for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
                link = m.group(1)
                if link.startswith(("http://", "https://", "mailto:")):
                    continue
                total += 1
                target_path, _, anchor = link.partition("#")
                target = os.path.normpath(os.path.join(os.path.dirname(md), target_path)) if target_path else md
                if not os.path.exists(target):
                    self.err(f"{self.rel(md)}: enlace roto {link}")
                    continue
                if anchor and target.endswith(".md"):
                    with open(target, encoding="utf-8") as f:
                        body = f.read()
                    heads = [re.sub(r"[^\w\s-]", "", h.lower()).strip().replace(" ", "-")
                             for h in re.findall(r"^#+\s+(.*)$", body, flags=re.M)]
                    if anchor not in heads:
                        self.err(f"{self.rel(md)}: ancla #{anchor} no existe en {self.rel(target)}")
        self.status_line(before, f"enlaces: {total} comprobados")

    # ------------------------------------------------------------ orquestación
    def run(self, manifests=None):
        catalog = self.check_catalog()
        if manifests:
            if catalog is not None:
                for p in manifests:
                    self.check_manifest(os.path.abspath(p), catalog)
        else:
            if catalog is not None:
                self.check_blocks(catalog)
                for p in sorted(glob.glob(os.path.join(self.root, "examples", "*.manifest.yaml"))):
                    self.check_manifest(p, catalog)
            self.check_links()
        return self.errors


def run(root, manifests=None):
    """API para tests: devuelve la lista de errores."""
    return Validator(root).run(manifests)


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    args = list(argv)
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i:i + 2]
    errors = run(root, args or None)
    print(f"\n{'TODO OK' if not errors else f'{len(errors)} error(es)'}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
