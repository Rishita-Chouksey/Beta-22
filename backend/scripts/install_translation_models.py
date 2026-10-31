"""Install offline translation models (Argos Translate).

Online (needs internet only for this one step):
    python -m scripts.install_translation_models

Offline / blocked network - download the .argosmodel files in a browser (or on another
network), put them in a folder, then:
    python -m scripts.install_translation_models --dir C:\\path\\to\\models
    python -m scripts.install_translation_models --file en_hi.argosmodel --file en_bn.argosmodel

Needed: en->hi, hi->en, en->bn, bn->en. hi<->bn is pivoted through English automatically.
"""
import argparse
import sys
from pathlib import Path

PAIRS = [("en", "hi"), ("hi", "en"), ("en", "bn"), ("bn", "en")]


def install_files(paths) -> int:
    import argostranslate.package as package

    failed = 0
    for p in paths:
        try:
            print(f"[install] {p}")
            package.install_from_path(str(p))
        except Exception as exc:
            failed += 1
            print(f"[failed]  {p}: {type(exc).__name__}: {exc}")
    return failed


def install_online() -> int:
    import argostranslate.package as package

    try:
        package.update_package_index()
    except Exception as exc:
        print(f"[failed] could not reach the model index: {type(exc).__name__}: {exc}")
        print("Your network/DNS is blocking the download. Try another network or DNS (e.g. 8.8.8.8),\n"
              "or download the files manually and use --dir / --file (see --help).")
        return 1

    available = package.get_available_packages()
    failed = []
    for src, tgt in PAIRS:
        pkg = next((p for p in available if p.from_code == src and p.to_code == tgt), None)
        if pkg is None:
            print(f"[missing] no model published for {src}->{tgt}")
            failed.append((src, tgt))
            continue
        print(f"[install] {src}->{tgt} ...")
        try:
            package.install_from_path(pkg.download())
        except Exception as exc:
            print(f"[failed]  {src}->{tgt}: {exc}")
            for link in getattr(pkg, "links", []) or []:
                print(f"          manual download: {link}")
            failed.append((src, tgt))
    print("Done." if not failed else f"Finished with gaps: {failed}. Re-run, or install those files manually.")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install offline translation models")
    parser.add_argument("--file", action="append", default=[], help="path to a .argosmodel file (repeatable)")
    parser.add_argument("--dir", help="folder containing .argosmodel files")
    args = parser.parse_args()

    try:
        import argostranslate.package  # noqa: F401
    except ImportError:
        print("argostranslate is not installed. Run: python -m pip install -r requirements.txt")
        return 1

    files = [Path(f) for f in args.file]
    if args.dir:
        files += sorted(Path(args.dir).glob("*.argosmodel"))
    if files:
        return 1 if install_files(files) else 0
    return install_online()


if __name__ == "__main__":
    sys.exit(main())
