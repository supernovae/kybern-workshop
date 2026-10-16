"""Bounded copy of prepared inputs; no acquisition, preparation or computation."""
import json
import os
from pathlib import Path
import stat
import sys
from workshop import read, safe, require


def stage(source, state):
    source, state = safe(source), safe(state)
    limits = read(state / "session.json")["limits"]
    maximum = limits["storage"]["root_bytes"]["A"]
    count, total, files = 0, 0, []
    for root, dirs, names in os.walk(source, followlinks=False):
        for name in dirs + names:
            p = Path(root) / name
            mode = p.lstat().st_mode
            require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), "regular input files/directories only")
            count += 1
            require(count <= limits["scan_entries"], "input entry budget")
            if stat.S_ISREG(mode):
                total += p.stat().st_size
                require(total <= maximum, "input byte budget")
                files.append(p)
    target = state / "inputs"
    target.mkdir()  # Exclusive: never reuse partial staging.
    copied = 0
    for p in files:
        out = target / p.relative_to(source)
        out.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as src, out.open("xb") as dst:
            require(stat.S_ISREG(os.fstat(src.fileno()).st_mode), "nonregular input")
            while block := src.read(1024 * 1024):
                copied += len(block)
                require(copied <= maximum, "input grew beyond byte budget")
                dst.write(block)
            dst.flush()
            os.fsync(dst.fileno())
    return {"files": len(files), "bytes": copied, "output": str(target)}


if __name__ == "__main__":
    require(sys.argv[1:] == ["stage"], "usage: handoff.py stage")
    print(json.dumps(stage(Path("/inputs"), Path(os.environ["SPARSELAB_WORK_DIR"]))))
