"""One-time download of offline translation models (needs internet only for this step).

    cd backend && python -m scripts.install_translation_models

Installs en<->hi and en<->bn Argos Translate models. After this, translation runs
fully offline; hi<->bn is pivoted through English automatically.
"""
import sys

PAIRS = [("en", "hi"), ("hi", "en"), ("en", "bn"), ("bn", "en")]


def main() -> int:
    try:
        import argostranslate.package as package
    except ImportError:
        print("argostranslate is not installed. Run: pip install -r requirements.txt")
        return 1

    package.update_package_index()
    available = package.get_available_packages()
    failed = []
    for src, tgt in PAIRS:
        pkg = next((p for p in available if p.from_code == src and p.to_code == tgt), None)
        if pkg is None:
            print(f"[missing] no model published for {src}->{tgt}")
            failed.append((src, tgt))
            continue
        print(f"[install] {src}->{tgt} ...")
        package.install_from_path(pkg.download())
    print("Done." if not failed else f"Done with gaps: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
