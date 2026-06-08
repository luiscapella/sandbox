"""
Call Center Performance Analysis System — CLI entry point.

Usage:
  python main.py generate    # generate sample data
  python main.py analyze     # run all analysis
  python main.py compare     # top vs bottom agent comparison
  python main.py playbook    # generate coaching playbook
  python main.py all         # run everything end to end
"""

import sys
import os

# Allow imports from analysis/ and insights/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "analysis"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "insights"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))


def cmd_generate():
    import generate_sample_data
    generate_sample_data.main()


def cmd_analyze():
    import agent_analysis
    import pattern_extraction
    print("\n--- Agent Performance Segmentation ---")
    agent_analysis.run()
    print("\n--- Extracting Conversation Patterns ---")
    pattern_extraction.extract_all()


def cmd_compare():
    import agent_comparison
    agent_comparison.compare()


def cmd_playbook():
    import generate_playbooks
    generate_playbooks.generate()


COMMANDS = {
    "generate": cmd_generate,
    "analyze":  cmd_analyze,
    "compare":  cmd_compare,
    "playbook": cmd_playbook,
}


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"

    if arg == "all":
        print("\n=== Running Full Pipeline ===")
        cmd_generate()
        cmd_analyze()
        cmd_compare()
        cmd_playbook()
    elif arg in COMMANDS:
        COMMANDS[arg]()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
