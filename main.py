import argparse
import json
import logging
import sys

from crew import ResumeTailorCrew

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate ATS-optimized tailored resume")
    parser.add_argument("--resume", required=True, help="Path to input resume (.pdf or .docx)")
    parser.add_argument("--role", required=True, help="Target role title")
    parser.add_argument("--tech-stack", required=True, help="Comma-separated target tech stack")
    parser.add_argument(
        "--output",
        default="tailored_resume.docx",
        help="Path to output DOCX (default: tailored_resume.docx)",
    )
    parser.add_argument(
        "--dump-raw",
        action="store_true",
        help="Print raw task outputs as JSON",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        result = ResumeTailorCrew(
            resume_path=args.resume,
            target_role=args.role,
            tech_stack=args.tech_stack,
            output_path=args.output,
        ).run()
    except Exception as exc:  # pragma: no cover
        logger.exception("Resume tailoring failed: %s", exc)
        return 1

    print(f"Generated: {result.output_docx}")
    if result.score is not None:
        print(f"ATS Match Score: {result.score}")
    if result.missing_keywords:
        print("Missing Keywords:")
        for kw in result.missing_keywords:
            print(f"- {kw}")
    if result.suggestions:
        print("Suggestions:")
        for suggestion in result.suggestions:
            print(f"- {suggestion}")

    if args.dump_raw:
        print(json.dumps(result.raw_outputs, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
