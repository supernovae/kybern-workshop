"""Read-only whole-root inventory. No collection, execution, or database repair.

Run only on a quiescent root with zero descendants, both before and after replay.
Every regular file is hashed; every SQLite table is read, including ALL attempt
rows (no status filters or joins). Does not prove absence of transient work:
continuous probe/process observation remains a separate requirement.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import stat


def _files(root):
    result = {}
    for path in sorted(root.rglob('*')):
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise ValueError('symlink in inventory')
        if stat.S_ISDIR(info.st_mode):
            result[path.relative_to(root).as_posix()] = {'kind': 'directory'}
        elif stat.S_ISREG(info.st_mode):
            before = (info.st_size, info.st_mtime_ns, info.st_ino)
            h = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''): h.update(block)
            info = path.stat()
            if before != (info.st_size, info.st_mtime_ns, info.st_ino):
                raise ValueError('inventory changed during read')
            result[path.relative_to(root).as_posix()] = {
                'kind': 'file', 'bytes': info.st_size, 'sha256': h.hexdigest()}
        else:
            raise ValueError('nonregular entry in inventory')
    return result


def capture(root):
    root = Path(root).absolute()
    if root.is_symlink() or any(p.is_symlink() for p in root.parents) or not root.is_dir():
        raise ValueError('inventory requires an existing nonsymlink root')
    files = _files(root)
    databases = {}
    for name, entry in files.items():
        if entry['kind'] != 'file': continue
        path = root/name
        with path.open('rb') as stream: header = stream.read(16)
        if header != b'SQLite format 3\x00': continue
        # immutable=1 guarantees no SQLite sidecar creation. It cannot read a WAL;
        # refuse uncheckpointed databases rather than silently omitting new rows.
        wal = root/(name+'-wal')
        journal = root/(name+'-journal')
        if any(p.exists() and p.stat().st_size for p in (wal, journal)):
            raise ValueError('inventory requires quiescent checkpointed SQLite; no repair performed')
        con = sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1', uri=True)
        try:
            tables = {}
            for (table,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
                quoted = '"'+table.replace('"','""')+'"'
                cursor = con.execute('SELECT * FROM '+quoted)
                columns = [item[0] for item in cursor.description]
                rows = []
                for row in cursor.fetchall():
                    rows.append([{'blob_hex': v.hex()} if isinstance(v, bytes) else v for v in row])
                rows.sort(key=lambda r: json.dumps(r, sort_keys=True, allow_nan=False))
                tables[table] = {'columns': columns, 'rows': rows}
            databases[name] = tables
        finally: con.close()
    if files != _files(root): raise ValueError('inventory changed during read')
    return {'format': 'workshop-whole-root-inventory-v1', 'root': str(root),
            'files': files, 'databases': databases,
            'retained_file_bytes': sum(v.get('bytes', 0) for v in files.values())}


def compare_replay(before, after, *, new_audit_files=()):
    """Fail closed on ANY stored-state change. Explicit new audit files only.

    No globs or directory exclusions. An audit path must start with audit/ or
    logs/replay/; it must be absent before replay. Existing file changes, raw
    database changes, extra run/pilot/receipt files and all table changes refuse.
    Operational churn may conservatively refuse; it is never silently ignored.
    """
    if before['format'] != 'workshop-whole-root-inventory-v1' or before['format'] != after['format']:
        raise ValueError('inventory format mismatch')
    if before['root'] != after['root']: raise ValueError('replay root changed')
    if before['databases'] != after['databases']: raise ValueError('database rows changed')
    allowed = set(new_audit_files)
    if len(allowed) != len(new_audit_files): raise ValueError('duplicate audit path')
    for name in allowed:
        path = Path(name)
        if (path.is_absolute() or '..' in path.parts or path.as_posix() != name or
            not (name.startswith('audit/') or name.startswith('logs/replay/')) or
            name in before['files'] or name not in after['files']):
            raise ValueError('invalid new audit path')
    a = {k: v for k, v in after['files'].items() if k not in allowed}
    if before['files'] != a: raise ValueError('replay changed full file inventory')
    return {'status': 'UNCHANGED_PERSISTED_STATE', 'scope': 'whole_root',
            'transient_work': 'requires_continuous_observation'}


def require_single_attempt(inventory, attempt_id, run_id):
    rows = []
    for tables in inventory["databases"].values():
        if "attempts" in tables:
            table = tables["attempts"]
            rows.extend(dict(zip(table["columns"], row, strict=True)) for row in table["rows"])
    if len(rows) != 1:
        raise ValueError("full inventory must contain exactly one Controller attempt")
    row = rows[0]
    if (not attempt_id or not run_id or row.get("attempt_id") != attempt_id or
        row.get("run_id") != run_id or row.get("status") != "COMPLETE" or
        row.get("ingestion_status") != "COMPLETE"):
        raise ValueError("full inventory attempt differs from selected completed ingestion")
    return {"status": "ONE_COMPLETED_ATTEMPT", "scope": "all_controller_tables"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    cap = sub.add_parser('capture'); cap.add_argument('root', type=Path)
    cmp = sub.add_parser('replay'); cmp.add_argument('before', type=Path); cmp.add_argument('after', type=Path)
    cmp.add_argument('--new-audit-path', action='append', default=[])
    single = sub.add_parser('single-attempt'); single.add_argument('inventory', type=Path)
    single.add_argument('--attempt-id', required=True); single.add_argument('--run-id', required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == 'capture': result = capture(args.root)
        elif args.action == 'single-attempt':
            result = require_single_attempt(json.loads(args.inventory.read_text()), args.attempt_id, args.run_id)
        else: result = compare_replay(json.loads(args.before.read_text()), json.loads(args.after.read_text()),
                                     new_audit_files=args.new_audit_path)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
        parser.exit(1, f'inventory refused: {error}\n')
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__': main()
