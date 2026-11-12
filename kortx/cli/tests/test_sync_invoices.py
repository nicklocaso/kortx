"""Tests for the sync-invoices script, with a fake Vercel CLI and hand-made PDF files.

The script is skills/sync-invoices/sync_invoices.py. It needs pypdf, which is not in the CLI environment.
Thus the tests run the script as a subprocess with `uv run --script`, in a temporary copy of an instance.
All values are synthetic.
"""

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL = REPO / "skills" / "sync-invoices"
FIXTURE_ENV = "FAKE_VERCEL_FIXTURE"
LOG_ENV = "FAKE_VERCEL_LOG"
ACCOUNT = "example-team"

FAKE_CLI = """#!{python}
import base64, json, os, sys

args = sys.argv[1:]
with open(os.environ["{log_env}"], "a", encoding="utf-8") as log:
    log.write(json.dumps(args) + "\\n")
with open(os.environ["{fixture_env}"], encoding="utf-8") as f:
    fixture = json.load(f)


def finish(step):
    if "stdout" in step:
        sys.stdout.write(step["stdout"])
    if "pdf" in step:
        sys.stdout.buffer.write(base64.b64decode(step["pdf"]))
    if "stderr" in step:
        sys.stderr.write(step["stderr"])
    sys.exit(step.get("exit", 0))


if args == ["whoami"]:
    finish(fixture.get("whoami", {{"stdout": "example-user\\n"}}))
if args[:3] == ["billing", "invoices", "list"]:
    if "list" in fixture:
        finish(fixture["list"])
    cursor = args[args.index("--next") + 1] if "--next" in args else ""
    finish({{"stdout": json.dumps(fixture["pages"][cursor])}})
if args[:3] == ["billing", "invoices", "download"]:
    finish(fixture["downloads"][args[3]])
finish({{"stderr": "unknown command\\n", "exit": 1}})
"""


def pdf(text):
    """Return a valid one-page PDF file that shows the text."""
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R"
         b" /Resources << /Font << /F1 5 0 R >> >> >>"),
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def invoice(id, number, issued="2026-10-01T10:00:00Z", status="paid"):
    return {"id": id, "invoiceNumber": number, "issuedAt": issued, "status": status}


def page(*invoices, next=None):
    return {"invoices": list(invoices), "pagination": {"next": next}}


def download(data):
    return {"pdf": base64.b64encode(data).decode()}


@unittest.skipUnless(shutil.which("uv"), "uv is not installed")
class SyncTestCase(unittest.TestCase):
    """Make a temporary instance with the unit `acme`, a files folder and a fake Vercel CLI."""

    @classmethod
    def setUpClass(cls):
        # The tests set XDG_CACHE_HOME. Keep the real uv cache, so that uv does not download pypdf again.
        result = subprocess.run(["uv", "cache", "dir"], capture_output=True, text=True, check=True)
        cls.uv_cache = result.stdout.strip()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name).resolve()
        self.root = tmp / "instance"
        self.files = tmp / "files"
        self.files.mkdir()
        self.work = tmp / "work"
        self.work.mkdir()
        self.write("AGENTS.md", "# Agent rules\n\n## Instance\n\n- Name: `example`, the test instance.\n")
        self.set_table(("vercel", ACCOUNT))
        self.write("projects/acme/backlog.md", "# Backlog\n")
        target = self.root / "skills" / "sync-invoices"
        (target / "vendors").mkdir(parents=True)
        shutil.copyfile(SKILL / "sync_invoices.py", target / "sync_invoices.py")
        shutil.copyfile(SKILL / "vendors" / "vercel.md", target / "vendors" / "vercel.md")
        self.script = target / "sync_invoices.py"
        self.cli = self.work / "vercel"
        self.cli.write_text(FAKE_CLI.format(python=sys.executable, log_env=LOG_ENV, fixture_env=FIXTURE_ENV))
        self.cli.chmod(0o755)
        self.fixture_path = self.work / "fixture.json"
        self.log_path = self.work / "calls.log"
        self.log_path.touch()
        self.fixture = {}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def set_table(self, *rows):
        text = "# acme\n\n## Invoices\n\n| Vendor | Account |\n| --- | --- |\n"
        self.write("projects/acme/README.md", text + "".join(f"| `{v}` | `{a}` |\n" for v, a in rows))

    def path(self, number, date="2026-10-01"):
        return self.files / "example" / "acme" / "invoices" / "vercel" / date[:4] / f"{date}_vercel_{number}.pdf"

    def env(self, **override):
        env = dict(os.environ)
        for name in ("KORTX_FILES", "KORTX_VERCEL_CLI", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"):
            env.pop(name, None)
        env.update({
            "KORTX_FILES": str(self.files),
            "KORTX_VERCEL_CLI": str(self.cli),
            "XDG_CACHE_HOME": str(self.work / "cache"),
            "UV_CACHE_DIR": self.uv_cache,
            FIXTURE_ENV: str(self.fixture_path),
            LOG_ENV: str(self.log_path),
        })
        for name, value in override.items():
            if value is None:
                env.pop(name, None)
            else:
                env[name] = value
        return env

    def run_script(self, *args, **env):
        """Run the script. Return the exit code and the stdout and stderr lines."""
        self.fixture_path.write_text(json.dumps(self.fixture), encoding="utf-8")
        result = subprocess.run(
            ["uv", "run", "--script", str(self.script), *args],
            cwd=self.root, env=self.env(**env), capture_output=True, text=True, timeout=300, check=False,
        )
        parts = list(self.files.rglob("*.part"))
        self.assertEqual(parts, [], f"temporary files are left: {parts}")
        return result.returncode, result.stdout.splitlines(), result.stderr

    def sync(self, *args, **env):
        return self.run_script("acme", *args, **env)

    def calls(self, command):
        lines = self.log_path.read_text(encoding="utf-8").splitlines()
        return [args for args in map(json.loads, lines) if args[2:3] == [command]]

    def all_files(self):
        return sorted(p for p in self.files.rglob("*") if p.is_file())

    def assertLine(self, line, lines):
        self.assertIn(line, lines, f"output: {lines}")

    def assertSummary(self, lines, paid=0, new=0, missing=0, bad=0):
        self.assertEqual(lines[-1], f"paid: {paid} new: {new} missing: {missing} bad: {bad}", f"output: {lines}")


class TestDownload(SyncTestCase):
    def setUp(self):
        super().setUp()
        self.data = pdf("Invoice TEST-0001")
        self.fixture = {
            "pages": {"": page(invoice("inv_1", "TEST-0001"), invoice("inv_2", "TEST-0002", status="open"))},
            "downloads": {"inv_1": download(self.data), "inv_2": download(pdf("Invoice TEST-0002"))},
        }

    def test_first_run_downloads_paid_invoice(self):
        code, lines, _ = self.sync()
        self.assertEqual(code, 0, lines)
        self.assertLine(f"new: {self.path('TEST-0001')}", lines)
        self.assertLine("not paid: open TEST-0002", lines)
        self.assertSummary(lines, paid=1, new=1)
        self.assertEqual(self.path("TEST-0001").read_bytes(), self.data)
        self.assertEqual(self.all_files(), [self.path("TEST-0001")])
        self.assertEqual([args[3] for args in self.calls("download")], ["inv_1"])

    def test_second_run_downloads_nothing(self):
        self.sync()
        self.log_path.write_text("")
        code, lines, _ = self.sync()
        self.assertEqual(code, 0, lines)
        self.assertSummary(lines, paid=1, new=0)
        self.assertEqual(self.calls("download"), [])
        self.assertEqual(self.path("TEST-0001").read_bytes(), self.data)

    def test_existing_file_is_not_overwritten(self):
        other = pdf("Invoice TEST-0001 local copy")
        self.path("TEST-0001").parent.mkdir(parents=True)
        self.path("TEST-0001").write_bytes(other)
        code, lines, _ = self.sync()
        self.assertEqual(code, 0, lines)
        self.assertSummary(lines, paid=1, new=0)
        self.assertEqual(self.path("TEST-0001").read_bytes(), other)
        self.assertEqual(self.calls("download"), [])

    def test_existing_bad_file(self):
        for name, data in (("not a PDF", b"not a PDF"), ("other number", pdf("Invoice TEST-9999"))):
            with self.subTest(name=name):
                self.path("TEST-0001").parent.mkdir(parents=True, exist_ok=True)
                self.path("TEST-0001").write_bytes(data)
                code, lines, _ = self.sync()
                self.assertEqual(code, 1, lines)
                self.assertLine(f"bad: {self.path('TEST-0001')}", lines)
                self.assertSummary(lines, paid=1, bad=1)
                self.assertEqual(self.path("TEST-0001").read_bytes(), data)


class TestList(SyncTestCase):
    def test_two_pages(self):
        self.fixture = {
            "pages": {
                "": page(invoice("inv_1", "TEST-0001"), next="cursor-1"),
                "cursor-1": page(invoice("inv_2", "TEST-0002", issued="2026-10-15T08:00:00Z")),
            },
            "downloads": {"inv_1": download(pdf("TEST-0001")), "inv_2": download(pdf("TEST-0002"))},
        }
        code, lines, _ = self.sync()
        self.assertEqual(code, 0, lines)
        self.assertLine(f"new: {self.path('TEST-0001')}", lines)
        self.assertLine(f"new: {self.path('TEST-0002', '2026-10-15')}", lines)
        self.assertSummary(lines, paid=2, new=2)
        self.assertIn("cursor-1", self.calls("list")[1])

    def test_repeated_cursor(self):
        self.fixture = {
            "pages": {
                "": page(invoice("inv_1", "TEST-0001"), next="cursor-1"),
                "cursor-1": page(invoice("inv_2", "TEST-0002"), next="cursor-1"),
            },
            "downloads": {},
        }
        code, lines, _ = self.sync()
        self.assertEqual(code, 2, lines)
        self.assertLine(f"error: vercel {ACCOUNT}: the pagination cursor is repeated", lines)
        self.assertEqual(self.calls("download"), [])
        self.assertEqual(self.all_files(), [])

    def test_list_fails(self):
        cases = {
            "exit code": ({"stderr": "server error\n", "exit": 1}, "server error"),
            "not JSON": ({"stdout": "Fetching invoices...\n"}, "the list output is not JSON"),
            "no pagination": ({"stdout": json.dumps({"invoices": []})},
                              "the list output has no invoices list or no pagination object"),
        }
        for name, (step, message) in cases.items():
            with self.subTest(name=name):
                self.fixture = {"list": step, "downloads": {}}
                code, lines, _ = self.sync()
                self.assertEqual(code, 2, lines)
                self.assertLine(f"error: vercel {ACCOUNT}: {message}", lines)
                self.assertFalse([line for line in lines if line.startswith("new:")], lines)
                self.assertSummary(lines)
                self.assertEqual(self.all_files(), [])

    def test_no_session(self):
        self.fixture = {"whoami": {"stderr": "not logged in\n", "exit": 1}, "pages": {}, "downloads": {}}
        code, lines, _ = self.sync()
        self.assertEqual(code, 2, lines)
        errors = [line for line in lines if line.startswith(f"error: vercel {ACCOUNT}:")]
        self.assertEqual(len(errors), 1, lines)
        self.assertIn("no Vercel session", errors[0])
        self.assertEqual(self.calls("list"), [])


class TestRefused(SyncTestCase):
    def test_hostile_invoice_numbers(self):
        numbers = ["../x", ".hidden", "a/b"]
        self.fixture = {
            "pages": {"": page(invoice("inv_ok", "TEST-0001"),
                               *(invoice(f"inv_{i}", n) for i, n in enumerate(numbers)))},
            "downloads": {"inv_ok": download(pdf("TEST-0001")),
                          **{f"inv_{i}": download(pdf(n)) for i, n in enumerate(numbers)}},
        }
        code, lines, _ = self.sync()
        self.assertEqual(code, 1, lines)
        for number in numbers:
            with self.subTest(number=number):
                self.assertLine(f"refused: vercel invoice number not valid: {number}", lines)
        self.assertSummary(lines, paid=1, new=1, bad=3)
        self.assertEqual(self.all_files(), [self.path("TEST-0001")])
        self.assertEqual([args[3] for args in self.calls("download")], ["inv_ok"])

    def test_time_without_zone(self):
        self.fixture = {
            "pages": {"": page(invoice("inv_1", "TEST-0001", issued="2026-10-01T00:00:00"))},
            "downloads": {"inv_1": download(pdf("TEST-0001"))},
        }
        code, lines, _ = self.sync()
        self.assertEqual(code, 1, lines)
        self.assertLine("refused: vercel date of issue not valid: 2026-10-01T00:00:00", lines)
        self.assertSummary(lines, bad=1)
        self.assertEqual(self.all_files(), [])

    def test_time_with_offset_uses_utc_date(self):
        self.fixture = {
            "pages": {"": page(invoice("inv_1", "TEST-0001", issued="2026-10-01T23:30:00-02:00"))},
            "downloads": {"inv_1": download(pdf("TEST-0001"))},
        }
        code, lines, _ = self.sync()
        self.assertEqual(code, 0, lines)
        self.assertLine(f"new: {self.path('TEST-0001', '2026-10-02')}", lines)
        self.assertEqual(self.all_files(), [self.path("TEST-0001", "2026-10-02")])


class TestBadDownload(SyncTestCase):
    def test_download_not_valid(self):
        cases = {
            "not a PDF": (b"<html>error</html>", "not a PDF file"),
            "other number": (pdf("Invoice TEST-9999"), "invoice number not in the PDF text"),
        }
        for name, (data, reason) in cases.items():
            with self.subTest(name=name):
                self.fixture = {
                    "pages": {"": page(invoice("inv_1", "TEST-0001"))},
                    "downloads": {"inv_1": download(data)},
                }
                code, lines, _ = self.sync()
                self.assertEqual(code, 1, lines)
                self.assertLine(f"bad: {self.path('TEST-0001')} ({reason})", lines)
                self.assertSummary(lines, paid=1, bad=1)
                self.assertEqual(self.all_files(), [])

    def test_download_fails_without_url_in_output(self):
        url = "https://invoices.example.test/inv_1.pdf?token=fake-token-0123456789"
        self.fixture = {
            "pages": {"": page(invoice("inv_1", "TEST-0001"))},
            "downloads": {"inv_1": {"stderr": f"\x1b[31mError:\x1b[0m cannot get {url}\n", "exit": 1}},
        }
        code, lines, stderr = self.sync()
        self.assertEqual(code, 1, lines)
        self.assertLine(f"missing: {self.path('TEST-0001')} (Error: cannot get <url>)", lines)
        self.assertSummary(lines, paid=1, missing=1)
        output = "\n".join(lines) + stderr
        for secret in (url, "invoices.example.test", "fake-token-0123456789", "\x1b"):
            self.assertNotIn(secret, output)
        self.assertEqual(self.all_files(), [])

    def test_download_fails_without_token_in_output(self):
        self.fixture = {
            "pages": {"": page(invoice("inv_1", "TEST-0001"))},
            "downloads": {"inv_1": {"stderr": "Authorization: Bearer fake-token-0123456789 refused\n", "exit": 1}},
        }
        code, lines, stderr = self.sync()
        self.assertEqual(code, 1, lines)
        self.assertLine(f"missing: {self.path('TEST-0001')} (Authorization <secret> refused)", lines)
        self.assertNotIn("fake-token-0123456789", "\n".join(lines) + stderr)


class TestParameters(SyncTestCase):
    def setUp(self):
        super().setUp()
        self.fixture = {"pages": {"": page()}, "downloads": {}}

    def assertConfigError(self, args, message, **env):
        code, lines, stderr = self.run_script(*args, **env)
        self.assertEqual(code, 2, lines)
        self.assertIn(f"error: {message}", stderr)
        self.assertEqual(lines, [])
        self.assertEqual(self.calls("list"), [])

    def test_files_folder_not_set(self):
        self.assertConfigError(["acme"], "KORTX_FILES is not set", KORTX_FILES=None)

    def test_files_folder_not_absolute(self):
        self.assertConfigError(["acme"], "KORTX_FILES must be an absolute path", KORTX_FILES="files")

    def test_files_folder_in_instance(self):
        for folder in (self.root, self.root / "files"):
            with self.subTest(folder=folder):
                self.assertConfigError(["acme"], "KORTX_FILES must be outside the repository",
                                       KORTX_FILES=str(folder))
        self.assertFalse((self.root / "files").exists())
        self.assertFalse((self.root / "example").exists())

    def test_unit_does_not_exist(self):
        for unit in ("nope", "../acme", "Acme"):
            with self.subTest(unit=unit):
                self.assertConfigError([unit], f"{unit} is not a unit")

    def test_vendor_not_in_table(self):
        self.assertConfigError(["acme", "--vendor", "other"], "the vendor other is not in the Invoices table")

    def test_vendor_not_known(self):
        self.set_table(("vercel", ACCOUNT), ("unknown-vendor", ACCOUNT))
        self.assertConfigError(["acme"], "the vendor unknown-vendor is not known")


if __name__ == "__main__":
    unittest.main()
