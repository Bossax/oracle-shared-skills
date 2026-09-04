import sys
import re
from pathlib import Path

def check_density(source_path, draft_path, min_ratio=0.8, max_ratio=1.6):
    with open(source_path, 'r', encoding='utf-8') as f:
        source_text = f.read()
    with open(draft_path, 'r', encoding='utf-8') as f:
        draft_text = f.read()

    # Remove whitespaces for pure character density calculation
    src_len = len(re.sub(r'\s+', '', source_text))
    draft_len = len(re.sub(r'\s+', '', draft_text))

    if src_len == 0:
        print("SIZE HEURISTIC SKIPPED: source is empty.")
        sys.exit(0)

    ratio = draft_len / src_len

    print(f"Size heuristic: source={src_len} chars draft={draft_len} chars ratio={ratio:.2f}")

    if ratio < min_ratio:
        print(f"\nSIZE HEURISTIC FAILED: draft is {ratio*100:.1f}% of source "
              f"(minimum {min_ratio*100:.1f}%).")
        print("This is a rewrite-only lower-bound signal, not an editorial verdict.")
        sys.exit(1)
    elif ratio > max_ratio:
        print(f"\nSIZE HEURISTIC FAILED: draft is {ratio*100:.1f}% of source "
              f"(maximum {max_ratio*100:.1f}%).")
        print("A floor alone rewards padding -- a thin argument stretched with filler")
        print("still passes a minimum-ratio check. This is a rewrite-only ceiling")
        print("signal, not an editorial verdict.")
        sys.exit(1)
    else:
        print("SIZE HEURISTIC PASSED")
        print("This does not certify source fidelity or editorial quality.")
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python check_density.py <source_path> <draft_path> [min_ratio] [max_ratio]")
        sys.exit(1)

    min_ratio = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
    max_ratio = float(sys.argv[4]) if len(sys.argv) > 4 else 1.6
    check_density(sys.argv[1], sys.argv[2], min_ratio, max_ratio)
