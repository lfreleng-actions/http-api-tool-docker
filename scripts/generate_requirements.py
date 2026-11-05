#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""
Generate requirements file with complete dependency tree and correct hashes.

This script generates a complete requirements file with:
- All transitive dependencies for given packages
- SHA256 hashes for specified platform
- Protection against supply chain attacks
- Reproducible builds

Usage:
    python3 scripts/generate_requirements_with_hashes.py [OPTIONS] PACKAGE1 PACKAGE2 ...

Examples:
    python3 scripts/generate_requirements_with_hashes.py safety==3.6.0 bandit==1.8.3
    python3 scripts/generate_requirements_with_hashes.py --platform linux_x86_64 --python-version 311 safety==3.6.0
    python3 scripts/generate_requirements_with_hashes.py --output /tmp/security-requirements.txt safety==3.6.0 bandit==1.8.3 pip-audit==2.7.3
"""

import argparse
import hashlib
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List


def get_all_dependencies(packages: List[str]) -> List[str]:
    """Get all dependencies including transitive ones using pip install --dry-run --report."""
    deps_report = "/tmp/deps-report.json"

    print(f"Getting complete dependency tree for: {', '.join(packages)}")

    # Get complete dependency tree
    result = subprocess.run(
        ["pip", "install", "--dry-run", "--report", deps_report] + packages,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error getting dependencies: {result.stderr}", file=sys.stderr)
        return []

    # Parse JSON report to get all packages
    with open(deps_report) as f:
        report = json.load(f)

    dependencies = []
    for item in report["install"]:
        name = item["metadata"]["name"]
        version = item["metadata"]["version"]
        dependencies.append(f"{name}=={version}")

    # Clean up
    Path(deps_report).unlink(missing_ok=True)

    return sorted(set(dependencies))


def download_and_hash(
    packages: List[str], platform: str, python_version: str
) -> Dict[str, str]:
    """Download packages and get their SHA256 hashes."""
    wheels_dir = Path("/tmp/wheels-download")
    if wheels_dir.exists():
        subprocess.run(["rm", "-rf", str(wheels_dir)])
    wheels_dir.mkdir()

    print(f"Downloading packages for platform {platform}, Python {python_version}...")

    # First try with platform specification and binary-only
    cmd = [
        "pip",
        "download",
        "--platform",
        platform,
        "--python-version",
        python_version,
        "--only-binary=:all:",
        "--no-deps",
        "-d",
        str(wheels_dir),
    ] + packages

    result = subprocess.run(cmd, capture_output=True, text=True)

    # If that fails, try without platform constraints (will get current platform)
    if result.returncode != 0:
        print(
            "Platform-specific download failed, trying without platform constraints..."
        )
        print(f"Error was: {result.stderr}")

        # Clean up and try again without platform constraints
        subprocess.run(["rm", "-rf", str(wheels_dir)])
        wheels_dir.mkdir()

        cmd = [
            "pip",
            "download",
            "--only-binary=:all:",
            "--no-deps",
            "-d",
            str(wheels_dir),
        ] + packages

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error downloading packages: {result.stderr}", file=sys.stderr)
            return {}

    # Generate hashes
    hashes = {}
    for wheel_file in wheels_dir.glob("*.whl"):
        # Extract package name and version from filename
        parts = wheel_file.name.split("-")
        package_name = parts[0].replace("_", "-").lower()
        version = parts[1]

        # Get SHA256 hash using hashlib for portability
        with open(wheel_file, "rb") as f:
            file_contents = f.read()
            hash_value = hashlib.sha256(file_contents).hexdigest()
        hashes[f"{package_name}=={version}"] = hash_value

    # Clean up
    subprocess.run(["rm", "-rf", str(wheels_dir)])

    return hashes


def generate_requirements_content(
    packages_with_hashes: Dict[str, str], comment: str | None = None
) -> str:
    """Generate the requirements file content."""
    content = []

    # Load SPDX header from external file to avoid REUSE parser confusion
    header_file = Path(__file__).parent / "requirements_header.txt"
    if header_file.exists():
        with open(header_file, "r") as f:
            header_lines = f.read().strip().split("\n")
            content.extend(header_lines)
    else:
        # Fallback header if file doesn't exist
        content.append("# Generated requirements file")
        content.append("# SPDX-FileCopyrightText: 2025 The Linux Foundation")

    content.append("")

    if comment:
        content.append(f"# {comment}")
        content.append("")

    content.append("# Complete dependency tree with SHA256 hash verification")
    content.append(
        "# This ensures reproducible builds and protection against supply chain attacks"
    )
    content.append("")

    for package in sorted(packages_with_hashes.keys()):
        hash_value = packages_with_hashes[package]
        content.append(f"{package} \\")
        content.append(f"    --hash=sha256:{hash_value}")

    return "\n".join(content)


def main() -> int:
    """Main function to generate requirements file."""
    parser = argparse.ArgumentParser(
        description="Generate requirements file with complete dependency tree and hashes"
    )
    parser.add_argument(
        "packages",
        nargs="+",
        help="Packages to install with version pins (e.g., safety==3.6.0)",
    )
    parser.add_argument(
        "--platform",
        default="linux_x86_64",
        help="Platform to download packages for (default: linux_x86_64)",
    )
    parser.add_argument(
        "--python-version",
        default="311",
        help="Python version to target (default: 311)",
    )
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument(
        "--comment", help="Additional comment to include in the requirements file"
    )

    args = parser.parse_args()

    # Validate package format
    for package in args.packages:
        if "==" not in package:
            print(
                f"Error: Package '{package}' must include exact version with == (e.g., safety==3.6.0)",
                file=sys.stderr,
            )
            return 1

    # Get all dependencies
    dependencies = get_all_dependencies(args.packages)
    if not dependencies:
        print("Error: Could not resolve dependencies", file=sys.stderr)
        return 1

    print(f"Found {len(dependencies)} total dependencies: {dependencies}")

    # Download and hash all packages
    hashes = download_and_hash(dependencies, args.platform, args.python_version)
    if not hashes:
        print("Error: Could not download and hash packages", file=sys.stderr)
        return 1

    print(f"Generated hashes for {len(hashes)} packages")

    # Generate requirements content
    requirements_content = generate_requirements_content(hashes, args.comment)

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            f.write(requirements_content)
        print(f"Generated requirements file: {args.output}")
    else:
        print(requirements_content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
