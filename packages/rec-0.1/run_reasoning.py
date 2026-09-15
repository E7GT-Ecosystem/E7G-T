"""Command-line runner for the bounded REC-B1/0.1 evaluator."""

from importlib.machinery import SourceFileLoader
import argparse
import json


rec = SourceFileLoader("rec", "packages/rec-0.1/e7gt_rec_v0_1.py").load_module()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a REC-B1/0.1 envelope")
    parser.add_argument("envelope")
    parser.add_argument("--out")
    args = parser.parse_args()
    with open(args.envelope, encoding="utf-8") as source:
        envelope = json.load(source)
    rendered = json.dumps(rec.evaluate(envelope).witness, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as target:
            target.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
