#!/usr/bin/env python3
"""Pruebas de scripts/validate.py: cada regla con su caso negativo y, donde aplica, su caso de aceptación.

Cada test copia el repositorio a un directorio temporal, muta el catálogo, un bloque o un manifest y
ejecuta el validador sobre esa copia. Así los fixtures nunca tocan el repositorio real.

Uso:  python3 -m unittest scripts/test_validate.py -v
"""
import copy
import os
import shutil
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


class Fixture:
    """Copia del repo sobre la que se construyen bloques implementados y manifests."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="foundation-")
        shutil.copytree(REPO, self.root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.catalog_path = os.path.join(self.root, "registry", "catalog.yaml")
        self.catalog = yaml.safe_load(open(self.catalog_path, encoding="utf-8"))

    def entry(self, block_id):
        return next(b for b in self.catalog["blocks"] if b["id"] == block_id)

    def implement(self, block_id, status="draft", version="0.1.0", descriptor=None, catalog=None,
                  integration="integration.md", tests="tests/README.md", write_artifacts=True):
        """Promueve un candidato: crea blocks/<id>/ con block.yaml coherente con el catálogo."""
        e = self.entry(block_id)
        e["status"] = status
        e["latest_version"] = version
        e["path"] = f"blocks/{block_id}"
        if catalog:
            e.update(catalog)
        shared = {k: e[k] for k in ("id", "family", "variant", "extends", "requires", "decision_mode",
                                    "default_for", "providers", "origin", "description") if k in e}
        d = {**shared, "name": e["name"], "version": version, "kind": ["docs"], "status": status}
        if integration:
            d["integration"] = integration
        if tests:
            d["tests"] = tests
        if descriptor:
            d.update({k: v for k, v in descriptor.items() if v is not None})
            for k, v in descriptor.items():
                if v is None:
                    d.pop(k, None)
        folder = os.path.join(self.root, "blocks", block_id)
        dump(os.path.join(folder, "block.yaml"), d)
        if write_artifacts:
            open(os.path.join(folder, "integration.md"), "w").write("# integración\n")
            os.makedirs(os.path.join(folder, "tests"), exist_ok=True)
            open(os.path.join(folder, "tests", "README.md"), "w").write("# tests\n")
        return d

    def save(self):
        dump(self.catalog_path, self.catalog)

    def manifest(self, blocks, name="product.foundation.manifest.yaml"):
        """Manifest de producto fuera de examples/ (por tanto sujeto a la regla de estado)."""
        data = {"manifest_version": 1, "product": "demo", "repo": "x/demo",
                "profile": {"type": "saas", "market": "ES", "locale": "es", "currency": "EUR"},
                "blocks": [{"id": b, "version": "1.0.0", "variant": v, "copied_at": "2026-09-04",
                            "source_commit": "0000000", "customized": False} for b, v in blocks]}
        path = os.path.join(self.root, name)
        dump(path, data)
        return path

    def run(self, manifests=None):
        self.save()
        return validate.run(self.root, manifests)

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)

    def assertRejects(self, errors, fragment):
        self.assertTrue(any(fragment in e for e in errors),
                        f"esperaba un error con {fragment!r}; errores: {errors}")

    def assertAccepts(self, errors):
        self.assertEqual(errors, [], f"esperaba cero errores; errores: {errors}")

    # ---------------------------------------------------------------- estado base
    def test_repo_is_green(self):
        self.assertAccepts(self.fx.run())

    def test_finesse_example_still_validates(self):
        errors = self.fx.run([os.path.join(self.fx.root, "examples", "finesse-es.foundation.manifest.yaml")])
        self.assertAccepts(errors)

    # ---------------------------------------------------------------- 1. drift catálogo ↔ block.yaml
    def test_drift_requires(self):
        self.fx.implement("auth", descriptor={"requires": {"workspace": ">=1"}})
        self.assertRejects(self.fx.run(), "drift en requires")

    def test_drift_requires_ignores_yaml_order(self):
        self.fx.implement("appointments", catalog={"requires": {"workspace": ">=1", "calendar": ">=1", "notifications": ">=1"}},
                          descriptor={"requires": {"notifications": ">=1", "calendar": ">=1", "workspace": ">=1"}})
        self.assertFalse(any("drift en requires" in e for e in self.fx.run()))

    def test_drift_variant(self):
        self.fx.implement("auth", descriptor={"variant": "region:es", "extends": "workspace",
                                              "requires": {"workspace": ">=1"}})
        self.assertRejects(self.fx.run(), "drift en variant")

    def test_drift_status_and_version(self):
        self.fx.implement("auth", descriptor={"version": "0.2.0"})
        self.assertRejects(self.fx.run(), "drift en version")

    # ---------------------------------------------------------------- 2. path ↔ id
    def test_catalog_path_pointing_to_another_block(self):
        self.fx.implement("auth")
        self.fx.implement("calendar", catalog={"requires": {"workspace": ">=1"}})
        self.fx.entry("auth")["path"] = "blocks/calendar"
        errors = self.fx.run()
        self.assertRejects(errors, "debe ser exactamente 'blocks/auth'")
        self.assertRejects(errors, "cuyo id es 'calendar'")

    # ---------------------------------------------------------------- 3. manifest variant ↔ catálogo
    def test_manifest_wrong_variant(self):
        self.fx.implement("auth")
        m = self.fx.manifest([("auth", "region:es")])
        self.assertRejects(self.fx.run([m]), "registra variant 'region:es'")

    def test_manifest_correct_variant_accepted(self):
        self.fx.implement("auth")
        self.assertAccepts(self.fx.run([self.fx.manifest([("auth", "core")])]))

    # ---------------------------------------------------------------- 4. stable exige integration y tests
    def test_stable_without_integration(self):
        self.fx.implement("auth", status="stable", version="1.0.0", integration=None)
        self.assertRejects(self.fx.run(), "'integration' is a required property")

    def test_stable_without_tests(self):
        self.fx.implement("auth", status="stable", version="1.0.0", tests=None)
        self.assertRejects(self.fx.run(), "'tests' is a required property")

    def test_stable_integration_path_missing(self):
        self.fx.implement("auth", status="stable", version="1.0.0", integration="nope.md")
        self.assertRejects(self.fx.run(), "exige integration apuntando a una ruta existente")

    def test_stable_tests_path_missing(self):
        self.fx.implement("auth", status="stable", version="1.0.0", tests="tests/nope.md")
        self.assertRejects(self.fx.run(), "exige tests apuntando a una ruta existente")

    def test_stable_with_artifacts_accepted(self):
        self.fx.implement("auth", status="stable", version="1.0.0")
        self.assertAccepts(self.fx.run())

    def test_draft_without_artifacts_accepted(self):
        self.fx.implement("auth", integration=None, tests=None, write_artifacts=False)
        self.assertAccepts(self.fx.run())

    # ---------------------------------------------------------------- 5. extends ∈ requires
    def test_extends_missing_from_requires_in_descriptor_and_catalog(self):
        self.fx.implement("appointments", catalog={"requires": {"workspace": ">=1", "calendar": ">=1", "notifications": ">=1"}})
        self.fx.implement("appointments-beauty", catalog={"requires": {}}, descriptor={"requires": {}})
        errors = self.fx.run()
        self.assertRejects(errors, "catalog: appointments-beauty: extends appointments debe aparecer también en requires")
        self.assertRejects(errors, "block blocks/appointments-beauty/block.yaml: extends appointments debe aparecer también en requires")

    # ---------------------------------------------------------------- 6. deprecated en manifests existentes
    def test_deprecated_block_valid_in_existing_manifest(self):
        self.fx.implement("ci", status="deprecated", version="1.2.0")
        self.assertAccepts(self.fx.run([self.fx.manifest([("ci", "core")])]))

    def test_candidate_still_rejected_in_manifest(self):
        self.assertRejects(self.fx.run([self.fx.manifest([("ci", "core")])]), "un candidate nunca se copia")

    # ---------------------------------------------------------------- 7. manifest malformado sin traceback
    def test_malformed_manifest_does_not_abort_others(self):
        self.fx.implement("auth")
        broken = os.path.join(self.fx.root, "broken.yaml")
        dump(broken, {"manifest_version": 1, "product": "demo", "repo": "x/demo",
                      "profile": {"type": "saas", "market": "ES", "locale": "es", "currency": "EUR"},
                      "blocks": [{"version": "1.0.0"}]})
        good_but_wrong = self.fx.manifest([("auth", "region:es")], name="second.yaml")
        errors = self.fx.run([broken, good_but_wrong])   # no debe lanzar KeyError
        self.assertRejects(errors, "'id' is a required property")
        self.assertRejects(errors, "second.yaml: auth registra variant")

    # ---------------------------------------------------------------- 8. providers con adapters
    def test_provider_block_without_providers(self):
        self.fx.implement("email-provider", catalog={"providers": None}, descriptor={"providers": None})
        self.fx.entry("email-provider").pop("providers", None)
        self.assertRejects(self.fx.run(), "'providers' is a required property")

    def test_provider_block_with_empty_list(self):
        self.fx.implement("email-provider", catalog={"providers": []}, descriptor={"providers": []})
        self.assertRejects(self.fx.run(), "[] should be non-empty")

    def test_provider_block_with_adapter_accepted(self):
        self.fx.implement("email-provider")
        self.assertAccepts(self.fx.run())

    def test_candidate_provider_without_adapters_allowed(self):
        self.fx.entry("whatsapp-provider").pop("providers", None)   # candidate: sin implementación
        self.assertAccepts(self.fx.run())

    # ---------------------------------------------------------------- 9. claves YAML duplicadas
    def test_duplicate_yaml_key_rejected(self):
        self.fx.implement("auth")
        path = os.path.join(self.fx.root, "blocks", "auth", "block.yaml")
        with open(path, "a", encoding="utf-8") as f:
            f.write("id: calendar\n")
        self.assertRejects(self.fx.run(), "clave duplicada 'id'")

    def test_duplicate_key_in_manifest_rejected(self):
        self.fx.implement("auth")
        m = self.fx.manifest([("auth", "core")])
        with open(m, "a", encoding="utf-8") as f:
            f.write("blocks: []\n")
        self.assertRejects(self.fx.run([m]), "clave duplicada 'blocks'")

    # ---------------------------------------------------------------- 10. SemVer solo dígitos ASCII
    def test_unicode_digits_rejected(self):
        for v in ("1٢.0.0", "1.0.0-1٢"):
            with self.subTest(v=v):
                fx = Fixture()
                self.addCleanup(fx.cleanup)
                fx.implement("auth", status="deprecated", version=v)
                self.assertRejects(fx.run(), "does not match")

    def test_valid_semver_accepted(self):
        for status, v in (("stable", "1.0.0"), ("draft", "0.1.0-alpha.1"), ("draft", "0.1.0+build.7")):
            with self.subTest(v=v):
                fx = Fixture()
                self.addCleanup(fx.cleanup)
                fx.implement("auth", status=status, version=v)
                self.assertAccepts(fx.run())

    # ---------------------------------------------------------------- 11. stable >= 1.0.0 real
    def test_stable_below_one_rejected(self):
        for v in ("0.9.9", "1.0.0-alpha", "1.0.0-rc.1"):
            with self.subTest(v=v):
                fx = Fixture()
                self.addCleanup(fx.cleanup)
                fx.implement("auth", status="stable", version=v)
                self.assertRejects(fx.run(), "does not match")

    def test_stable_at_or_above_one_accepted(self):
        for v in ("1.0.0", "1.0.1", "2.0.0", "2.0.0+build.4", "2.0.0-rc.1"):
            with self.subTest(v=v):
                fx = Fixture()
                self.addCleanup(fx.cleanup)
                fx.implement("auth", status="stable", version=v)
                self.assertAccepts(fx.run())

    def test_semver_precedence(self):
        k = validate.semver_key
        self.assertLess(k("1.0.0-rc.1"), k("1.0.0"))
        self.assertLess(k("1.0.0-alpha"), k("1.0.0-alpha.1"))
        self.assertLess(k("1.0.0-alpha.1"), k("1.0.0-alpha.beta"))
        self.assertLess(k("1.0.0-beta.2"), k("1.0.0-beta.11"))
        self.assertLess(k("1.0.0"), k("2.0.0-rc.1"))
        self.assertEqual(k("1.0.0+a"), k("1.0.0+b"))
        self.assertIsNone(k("1٢.0.0"))

    # ---------------------------------------------------------------- 12. candidate sin directorio
    def test_candidate_directory_rejected(self):
        os.makedirs(os.path.join(self.fx.root, "blocks", "auth"))
        open(os.path.join(self.fx.root, "blocks", "auth", "README.md"), "w").write("# auth\n")
        self.assertRejects(self.fx.run(), "auth es candidate pero existe blocks/auth/")

    def test_directory_without_catalog_entry_rejected(self):
        os.makedirs(os.path.join(self.fx.root, "blocks", "mystery"))
        self.assertRejects(self.fx.run(), "blocks/mystery/: directorio sin entrada en el catálogo")


if __name__ == "__main__":
    unittest.main()
