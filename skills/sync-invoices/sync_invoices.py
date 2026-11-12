# /// script
# requires-python = ">=3.12"
# dependencies = ["pypdf==6.9.2"]
# [tool.uv]
# exclude-newer = "2026-11-10T00:00:00Z"
# ///
"""Download the missing paid invoices of the vendors of a unit.

Usage:
    uv run --script skills/sync-invoices/sync_invoices.py <unit> [--vendor <vendor>]

The vendors and the accounts are in the Invoices table of the unit README.md.
The files go to $KORTX_FILES/<instance>/<unit>/invoices/<vendor>/<YYYY>/.
The contract is in invoice-format.md.
"""

import argparse
import hashlib
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pypdf

ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = Path(__file__).resolve().parent

UNIT_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$")
INSTANCE_LINE = re.compile(r"^- Name: `(?P<name>[a-z0-9]+(-[a-z0-9]+)*)`")
INVOICES_SECTION = "Invoices"
INVOICES_TABLE = ["| Vendor | Account |", "| --- | --- |"]
INVOICE_ROW = re.compile(r"^\| `(?P<vendor>[^`]+)` \| `(?P<account>[^`]+)` \|$")
INVOICE_VENDOR = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
INVOICE_ACCOUNT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
INVOICE_NUMBER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
FILES_ENV = "KORTX_FILES"
URL = re.compile(r"https?://\S+")
SECRET = re.compile(r"(?i)\b(bearer|token|authorization|api[-_]?key)\b[\s=:\"']+(?:bearer\s+)?\S+")
ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")
NOT_ALNUM = re.compile(r"[^A-Za-z0-9]")
MESSAGE_MAX = 300
PDF_MAGIC = b"%PDF-"
PDF_PAGES = 3
INSTALL_TIMEOUT = 600

VERCEL_CLI_ENV = "KORTX_VERCEL_CLI"
VERCEL_LIST_TIMEOUT = 120
VERCEL_DOWNLOAD_TIMEOUT = 300
VERCEL_MAX_PAGES = 100
VERCEL_FIELDS = {"id": "id", "number": "invoiceNumber", "issued": "issuedAt", "status": "status"}

NEON_CLI_ENV = "KORTX_NEON_CLI"
NEON_API_ENV = "KORTX_NEON_API"
NEON_API = "https://console.neon.tech"
NEON_CREDENTIALS = "~/.config/neonctl/credentials.json"
NEON_SESSION_TIMEOUT = 120
NEON_LIST_TIMEOUT = 30
NEON_DOWNLOAD_TIMEOUT = 60
NEON_ORG = re.compile(r"^org-[a-z0-9-]+$")
NEON_FIELDS = {"id": "pdf_url", "number": "invoice_number", "issued": "issued_at", "status": "status"}
NEON_MORE_KEYS = ("pagination", "next", "next_cursor", "cursor", "has_more")
LOCAL_HOSTS = ("127.0.0.1", "localhost")


class ConfigError(Exception):
    """The parameters are not valid. The script stops."""


class ListError(Exception):
    """The list of invoices of one account failed."""


class DownloadError(Exception):
    """The download of one invoice failed."""


@dataclass
class Invoice:
    id: str
    number: str
    issued: str
    status: str


def sanitize(text, secrets=()):
    """Remove secrets, URLs and control characters from external text, and cut it."""
    text = str(text)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "<secret>")
    text = SECRET.sub(r"\1 <secret>", URL.sub("<url>", text))
    text = CONTROL.sub(" ", ANSI.sub("", text))
    return " ".join(text.split())[:MESSAGE_MAX]


def parse_issued(value):
    """Return the UTC date of issue as YYYY-MM-DD, or None if the value is not valid."""
    if not isinstance(value, str):
        return None
    try:
        issued = datetime.fromisoformat(value)
    except ValueError:
        return None
    if issued.tzinfo is None or issued.utcoffset() is None:
        return None
    return issued.astimezone(timezone.utc).date().isoformat()


def check_pdf(data, number):
    """Return None if the PDF is correct, else a short reason."""
    if not data.startswith(PDF_MAGIC):
        return "not a PDF file"
    try:
        logging.getLogger("pypdf").setLevel(logging.CRITICAL)
        reader = pypdf.PdfReader(io.BytesIO(data))
        text = "".join(page.extract_text() or "" for page in reader.pages[:PDF_PAGES])
    except Exception as error:
        return f"PDF not valid: {type(error).__name__}"
    if NOT_ALNUM.sub("", number) not in NOT_ALNUM.sub("", text):
        return "invoice number not in the PDF text"
    return None


def sections(text):
    """Return the level-2 headings and the lines under each heading."""
    result = {}
    order = []
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            order.append(current)
            result[current] = []
        elif current is not None and line.strip():
            result[current].append(line)
    return order, result


def read_instance():
    path = ROOT / "AGENTS.md"
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            m = INSTANCE_LINE.match(line)
            if m:
                return m["name"]
    raise ConfigError("the instance name is not in AGENTS.md")


def vendor_known(vendor, unit):
    if (SKILL_DIR / "vendors" / f"{vendor}.md").is_file():
        return True
    parts = unit.split("/")
    owners = ["/".join(parts[:i]) for i in range(len(parts), 0, -1)]
    return any((ROOT / "projects" / u / "skills" / f"sync-{vendor}-invoices" / "SKILL.md").is_file() for u in owners)


def read_invoices_table(unit):
    """Return the (vendor, account) rows of the Invoices table of the unit."""
    path = ROOT / "projects" / unit / "README.md"
    if not path.is_file():
        raise ConfigError(f"projects/{unit}/README.md does not exist")
    order, content = sections(path.read_text(encoding="utf-8"))
    if INVOICES_SECTION not in order:
        raise ConfigError(f"projects/{unit}/README.md has no {INVOICES_SECTION} section")
    lines = [line.strip() for line in content[INVOICES_SECTION]]
    if lines[:2] != INVOICES_TABLE:
        raise ConfigError(f"the {INVOICES_SECTION} table must start with {INVOICES_TABLE[0]}")
    if len(lines) == 2:
        raise ConfigError(f"the {INVOICES_SECTION} table has no vendor")
    rows = []
    for line in lines[2:]:
        m = INVOICE_ROW.match(line)
        if not m:
            raise ConfigError(f"row not valid in the {INVOICES_SECTION} table: {sanitize(line)}")
        vendor, account = m["vendor"], m["account"]
        if not INVOICE_VENDOR.match(vendor):
            raise ConfigError(f"the vendor {sanitize(vendor)} is not in kebab-case")
        if not INVOICE_ACCOUNT.match(account):
            raise ConfigError(f"the account {sanitize(account)} is not valid")
        if (vendor, account) in rows:
            raise ConfigError(f"{vendor} {account} is in the table more than one time")
        if not vendor_known(vendor, unit):
            raise ConfigError(f"the vendor {vendor} is not known")
        rows.append((vendor, account))
    return rows


def inside(path, root):
    return path == root or root in path.parents


def files_base(instance, unit):
    """Return the invoices folder of the unit. It must be outside the repository."""
    value = os.environ.get(FILES_ENV, "")
    if not value:
        raise ConfigError(f"{FILES_ENV} is not set")
    files = Path(value).expanduser()
    if not files.is_absolute():
        raise ConfigError(f"{FILES_ENV} must be an absolute path")
    base = files / instance / unit / "invoices"
    existing = base
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    if inside(Path(os.path.realpath(existing)), Path(os.path.realpath(ROOT))):
        raise ConfigError(f"{FILES_ENV} must be outside the repository")
    return base


def run(args, timeout, error):
    """Run a command. Return the completed process, or raise error on a timeout or an OS error."""
    env = {**os.environ, "VERCEL_TELEMETRY_DISABLED": "1"}
    try:
        return subprocess.run(args, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        raise error(f"timeout after {timeout} s")
    except OSError as e:
        raise error(sanitize(e.strerror or type(e).__name__))


def stderr_text(result):
    return sanitize(result.stderr.decode("utf-8", errors="replace")) or f"exit code {result.returncode}"


def install_cli(name):
    """Install the locked CLI packages in the cache, if they are not there. Return the path of the CLI."""
    lock = SKILL_DIR / "package-lock.json"
    digest = hashlib.sha256(lock.read_bytes()).hexdigest()[:12]
    cache_home = os.environ.get("XDG_CACHE_HOME") or str(Path("~/.cache").expanduser())
    cache = Path(cache_home) / "kortx" / "sync-invoices" / digest
    binary = cache / "node_modules" / ".bin" / name
    if binary.exists():
        return str(binary)
    cache.mkdir(parents=True, exist_ok=True)
    for file in ("package.json", "package-lock.json"):
        shutil.copyfile(SKILL_DIR / file, cache / file)
    args = ["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund", "--prefix", str(cache)]
    result = run(args, INSTALL_TIMEOUT, ConfigError)
    if result.returncode != 0:
        raise ConfigError(f"npm ci failed: {stderr_text(result)}")
    if not binary.exists():
        raise ConfigError(f"npm ci did not install the {name} CLI")
    return str(binary)


class Vercel:
    """Adapter for the Vercel CLI."""

    def __init__(self):
        self.bin = None

    def cli(self):
        if self.bin is None:
            self.bin = os.environ.get(VERCEL_CLI_ENV) or install_cli("vercel")
        return self.bin

    def list_invoices(self, account):
        cli = self.cli()
        if run([cli, "whoami"], VERCEL_LIST_TIMEOUT, ListError).returncode != 0:
            raise ListError(f"no Vercel session. Run: ! {cli} login")
        invoices = []
        seen = set()
        cursor = None
        for _ in range(VERCEL_MAX_PAGES):
            args = [cli, "billing", "invoices", "list", "--scope", account, "--limit", "100", "--json"]
            if cursor:
                args += ["--next", cursor]
            result = run(args, VERCEL_LIST_TIMEOUT, ListError)
            if result.returncode != 0:
                raise ListError(stderr_text(result))
            page_invoices, cursor = self.parse_page(result.stdout)
            invoices += page_invoices
            if not cursor:
                return invoices
            if cursor in seen:
                raise ListError("the pagination cursor is repeated")
            seen.add(cursor)
        raise ListError(f"more than {VERCEL_MAX_PAGES} pages")

    def parse_page(self, stdout):
        """Return the invoices and the next cursor of one page of the list."""
        try:
            data = json.loads(stdout)
        except ValueError:
            raise ListError("the list output is not JSON")
        if not isinstance(data, dict) or not isinstance(data.get("invoices"), list) \
                or not isinstance(data.get("pagination"), dict):
            raise ListError("the list output has no invoices list or no pagination object")
        cursor = data["pagination"].get("next")
        if cursor is not None and not isinstance(cursor, str):
            raise ListError("pagination.next is not a string")
        invoices = []
        for item in data["invoices"]:
            if not isinstance(item, dict):
                raise ListError("an invoice is not an object")
            fields = {}
            for field, key in VERCEL_FIELDS.items():
                if not isinstance(item.get(key), str):
                    raise ListError(f"an invoice has no {key} string")
                fields[field] = item[key]
            invoices.append(Invoice(**fields))
        return invoices, cursor

    def download(self, invoice, account):
        args = [self.cli(), "billing", "invoices", "download", invoice.id, "--scope", account, "-o", "-"]
        result = run(args, VERCEL_DOWNLOAD_TIMEOUT, DownloadError)
        if result.returncode != 0:
            raise DownloadError(stderr_text(result))
        return result.stdout


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects. The opener then raises an HTTPError with the 3xx code."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class CheckedRedirect(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only if the new URL is allowed."""

    def __init__(self, allowed):
        self.allowed = allowed

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not self.allowed(newurl):
            raise DownloadError("the PDF link was redirected")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Neon:
    """Adapter for the Neon Console API. The Neon CLI only refreshes the session."""

    def __init__(self):
        self.bin = None
        self.token = None
        self.base = NEON_API
        self.local = None
        override = os.environ.get(NEON_API_ENV)
        if override:
            url = urlsplit(override)
            if url.scheme not in ("http", "https") or url.hostname not in LOCAL_HOSTS:
                raise ConfigError(f"{NEON_API_ENV} must be a local URL")
            self.base = override.rstrip("/")
            self.local = (url.scheme, url.hostname)

    def cli(self):
        if self.bin is None:
            self.bin = os.environ.get(NEON_CLI_ENV) or install_cli("neonctl")
        return self.bin

    def clean(self, text):
        return sanitize(text, [self.token] if self.token else [])

    def allowed(self, url):
        parts = urlsplit(url)
        if parts.scheme == "https" and parts.hostname:
            return True
        return self.local is not None and (parts.scheme, parts.hostname) == self.local

    def read_token(self, cli):
        try:
            data = json.loads(Path(NEON_CREDENTIALS).expanduser().read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = None
        token = data.get("access_token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token:
            raise ListError(f"no Neon token. Run: ! {cli} auth")
        return token

    def list_invoices(self, account):
        if not NEON_ORG.match(account):
            raise ListError("the account is not a Neon organization ID")
        cli = self.cli()
        if run([cli, "me", "--no-analytics"], NEON_SESSION_TIMEOUT, ListError).returncode != 0:
            raise ListError(f"no Neon session. Run: ! {cli} auth")
        self.token = self.read_token(cli)
        request = urllib.request.Request(
            f"{self.base}/api/v2/organizations/{account}/billing/invoices",
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"},
        )
        opener = urllib.request.build_opener(NoRedirect)
        try:
            with opener.open(request, timeout=NEON_LIST_TIMEOUT) as response:
                body = response.read()
        except urllib.error.HTTPError as e:
            if 300 <= e.code < 400:
                raise ListError("the list request was redirected")
            raise ListError(f"HTTP {e.code}")
        except urllib.error.URLError as e:
            raise ListError(self.clean(e.reason))
        except OSError as e:
            raise ListError(self.clean(e.strerror or type(e).__name__))
        return self.parse_list(body)

    def parse_list(self, body):
        try:
            data = json.loads(body)
        except ValueError:
            raise ListError("the list output is not JSON")
        if not isinstance(data, dict) or not isinstance(data.get("invoices"), list):
            raise ListError("the list output has no invoices list")
        if any(data.get(key) for key in NEON_MORE_KEYS):
            raise ListError("the list has more pages")
        invoices = []
        for item in data["invoices"]:
            if not isinstance(item, dict):
                raise ListError("an invoice is not an object")
            fields = {}
            for field, key in NEON_FIELDS.items():
                if not isinstance(item.get(key), str):
                    raise ListError(f"an invoice has no {key} string")
                fields[field] = item[key]
            invoices.append(Invoice(**fields))
        return invoices

    def download(self, invoice, account):
        if not self.allowed(invoice.id):
            raise DownloadError("the PDF link is not valid")
        request = urllib.request.Request(invoice.id)
        opener = urllib.request.build_opener(CheckedRedirect(self.allowed))
        try:
            with opener.open(request, timeout=NEON_DOWNLOAD_TIMEOUT) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            raise DownloadError(f"HTTP {e.code}")
        except urllib.error.URLError as e:
            raise DownloadError(self.clean(e.reason))
        except OSError as e:
            raise DownloadError(self.clean(e.strerror or type(e).__name__))


ADAPTERS = {"vercel": Vercel, "neon": Neon}


def write_new(path, data):
    """Write the data to a temporary file, then link it to path. Return False if path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.link(tmp, path)
        return True
    except FileExistsError:
        return False
    finally:
        os.unlink(tmp)


def sync_invoice(adapter, vendor, account, invoice, base, counts):
    date = parse_issued(invoice.issued)
    if date is None:
        print(f"refused: {vendor} date of issue not valid: {sanitize(invoice.issued)}")
        counts["bad"] += 1
        return
    if not INVOICE_NUMBER.match(invoice.number):
        print(f"refused: {vendor} invoice number not valid: {sanitize(invoice.number)}")
        counts["bad"] += 1
        return
    if invoice.status != "paid":
        print(f"not paid: {sanitize(invoice.status)} {invoice.number}")
        return
    counts["paid"] += 1
    path = base / vendor / date[:4] / f"{date}_{vendor}_{invoice.number}.pdf"
    if path.exists():
        try:
            reason = check_pdf(path.read_bytes(), invoice.number)
        except OSError:
            reason = "cannot read"
        if reason:
            print(f"bad: {path}")
            counts["bad"] += 1
        return
    try:
        data = adapter.download(invoice, account)
    except DownloadError as error:
        print(f"missing: {path} ({error})")
        counts["missing"] += 1
        return
    reason = check_pdf(data, invoice.number)
    if reason:
        print(f"bad: {path} ({reason})")
        counts["bad"] += 1
        return
    try:
        written = write_new(path, data)
    except OSError as error:
        print(f"missing: {path} ({sanitize(error.strerror or type(error).__name__)})")
        counts["missing"] += 1
        return
    if written:
        print(f"new: {path}")
        counts["new"] += 1
    else:
        print(f"exists: {path}")


def sync_row(adapter, vendor, account, base, counts):
    """Sync the invoices of one account. Return False if the list failed."""
    try:
        invoices = adapter.list_invoices(account)
    except ListError as error:
        print(f"error: {vendor} {account}: {error}")
        return False
    for invoice in invoices:
        sync_invoice(adapter, vendor, account, invoice, base, counts)
    return True


def main():
    parser = argparse.ArgumentParser(description="Download the missing paid invoices of a unit.")
    parser.add_argument("unit", help="The unit name, for example acme or acme/api.")
    parser.add_argument("--vendor", help="Sync this vendor only.")
    args = parser.parse_args()

    counts = {"paid": 0, "new": 0, "missing": 0, "bad": 0}
    list_failed = False
    try:
        if not UNIT_NAME.match(args.unit) or not (ROOT / "projects" / args.unit / "backlog.md").is_file():
            raise ConfigError(f"{sanitize(args.unit)} is not a unit")
        rows = read_invoices_table(args.unit)
        if args.vendor is not None:
            rows = [row for row in rows if row[0] == args.vendor]
            if not rows:
                raise ConfigError(f"the vendor {sanitize(args.vendor)} is not in the {INVOICES_SECTION} table")
        base = files_base(read_instance(), args.unit)
        adapters = {}
        for vendor, account in rows:
            if vendor not in ADAPTERS:
                print(f"skip: {vendor} has no adapter in this skill")
                continue
            adapter = adapters.setdefault(vendor, ADAPTERS[vendor]())
            if not sync_row(adapter, vendor, account, base, counts):
                list_failed = True
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(" ".join(f"{key}: {value}" for key, value in counts.items()))
    if list_failed:
        return 2
    return 1 if counts["missing"] or counts["bad"] else 0


if __name__ == "__main__":
    sys.exit(main())
