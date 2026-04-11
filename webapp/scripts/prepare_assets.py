import argparse
import shutil
from pathlib import Path


def copy_required_assets(source_dir: Path, target_dir: Path, files: list[str]) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    copied = 0

    for name in files:
        src = source_dir / name
        dst = target_dir / name
        if not src.is_file():
            raise FileNotFoundError(f"Required asset not found: {src}")
        shutil.copy2(src, dst)
        copied += 1
        print(f"[prepare_assets] copied: {src} -> {dst}")

    print(f"[prepare_assets] done, total copied: {copied}")
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy required webapp assets before packaging")
    parser.add_argument("--source", required=True, help="Source directory")
    parser.add_argument("--target", required=True, help="Target directory")
    parser.add_argument("--files", nargs="+", required=True, help="Required asset file names")
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    target_dir = Path(args.target).resolve()

    copy_required_assets(source_dir, target_dir, args.files)


if __name__ == "__main__":
    main()

