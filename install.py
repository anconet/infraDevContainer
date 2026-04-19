#!/usr/bin/env python3
"""Install or uninstall dev container support files for a project."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

InstallMethod = Literal["copy", "symlink"]
Operation = Literal["install", "uninstall"]
SOURCE_FILE_NAMES: tuple[str, str, str] = (
    "Dockerfile",
    "devcontainer.json",
    "post-create.sh",
)


@dataclass(frozen=True)
class InstallConfig:
    """Configuration values for the installer script."""

    operation: Operation
    method: InstallMethod
    projectRoot: Path
    scriptRoot: Path
    force: bool

    @staticmethod
    def validateInstallConfig(config: "InstallConfig") -> None:
        """Validate configuration values before changing files on disk."""
        if config.operation not in ("install", "uninstall"):
            raise ValueError(f"Unsupported operation: {config.operation}")

        if config.method not in ("copy", "symlink"):
            raise ValueError(f"Unsupported installation method: {config.method}")

        if not config.projectRoot.exists():
            raise ValueError(f"Project root does not exist: {config.projectRoot}")

        if not config.projectRoot.is_dir():
            raise ValueError(f"Project root is not a directory: {config.projectRoot}")

        if not config.scriptRoot.exists():
            raise ValueError(f"Installer directory does not exist: {config.scriptRoot}")


def buildArgumentParser() -> argparse.ArgumentParser:
    """Create the command-line parser for the installer."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=(
            "Install or uninstall VS Code dev container files by copying or "
            "creating symbolic links in a .devcontainer directory."
        )
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    installParser = subparsers.add_parser(
        "install",
        help="Create a .devcontainer directory and add the dev container files.",
    )
    installParser.add_argument(
        "--method",
        choices=("copy", "symlink", "softlink"),
        default="symlink",
        help="How to connect the files into .devcontainer. Defaults to symlink.",
    )
    installParser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root where the .devcontainer directory will be created.",
    )

    uninstallParser = subparsers.add_parser(
        "uninstall",
        help="Remove the installed .devcontainer files and directory.",
    )
    uninstallParser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root that contains the .devcontainer directory.",
    )
    uninstallParser.add_argument(
        "--yes",
        action="store_true",
        dest="force",
        help="Skip the uninstall confirmation prompt.",
    )

    return parser


def parseArguments(argv: Sequence[str] | None = None) -> InstallConfig:
    """Parse command-line arguments into a validated configuration object."""
    parser: argparse.ArgumentParser = buildArgumentParser()
    args = parser.parse_args(argv)

    requestedMethod: str = getattr(args, "method", "copy")
    normalizedMethod: InstallMethod = "symlink" if requestedMethod == "softlink" else requestedMethod  # type: ignore[assignment]
    operation: Operation = args.operation
    projectRoot: Path = Path(args.project_root).resolve()
    scriptRoot: Path = Path(__file__).resolve().parent
    force: bool = bool(getattr(args, "force", False))

    config = InstallConfig(
        operation=operation,
        method=normalizedMethod,
        projectRoot=projectRoot,
        scriptRoot=scriptRoot,
        force=force,
    )
    InstallConfig.validateInstallConfig(config)
    return config


def collectSourcePaths(scriptRoot: Path) -> list[Path]:
    """Return the source file paths that must be installed."""
    sourcePaths: list[Path] = []

    for fileName in SOURCE_FILE_NAMES:
        sourcePath: Path = scriptRoot.joinpath(fileName)
        if not sourcePath.exists():
            raise ValueError(f"Required source file is missing: {sourcePath}")
        sourcePaths.append(sourcePath)

    return sourcePaths


def createTargetDirectory(projectRoot: Path) -> Path:
    """Create the .devcontainer directory in the selected project root."""
    targetDirectory: Path = projectRoot.joinpath(".devcontainer")

    if targetDirectory.exists():
        raise ValueError(
            f"The target directory already exists: {targetDirectory}. "
            "Remove it first or run uninstall."
        )

    targetDirectory.mkdir(parents=False, exist_ok=False)
    return targetDirectory


def installByCopy(sourcePath: Path, targetPath: Path) -> None:
    """Copy a source file into the .devcontainer directory."""
    shutil.copy2(sourcePath, targetPath)



def installBySymlink(sourcePath: Path, targetPath: Path) -> None:
    """Create a relative symbolic link in the .devcontainer directory."""
    relativeSourcePath: Path = Path(os.path.relpath(sourcePath, start=targetPath.parent))
    targetPath.symlink_to(relativeSourcePath)



def performInstall(config: InstallConfig) -> None:
    """Install the dev container files using the requested method."""
    sourcePaths: list[Path] = collectSourcePaths(config.scriptRoot)
    targetDirectory: Path = createTargetDirectory(config.projectRoot)

    try:
        for sourcePath in sourcePaths:
            targetPath: Path = targetDirectory.joinpath(sourcePath.name)
            if config.method == "copy":
                installByCopy(sourcePath, targetPath)
            else:
                installBySymlink(sourcePath, targetPath)
    except Exception:
        for createdPath in targetDirectory.iterdir():
            createdPath.unlink()
        targetDirectory.rmdir()
        raise

    print(
        f"Installed {len(sourcePaths)} files into {targetDirectory} using "
        f"the {config.method} method."
    )



def confirmUninstall(config: InstallConfig) -> bool:
    """Ask the user to confirm uninstall unless force is enabled."""
    if config.force:
        return True

    prompt: str = (
        f"This will remove {config.projectRoot.joinpath('.devcontainer')}. "
        "Are you sure? [y/N]: "
    )
    response: str = input(prompt).strip().lower()
    return response in {"y", "yes"}



def performUninstall(config: InstallConfig) -> None:
    """Remove the installed dev container files and .devcontainer directory."""
    targetDirectory: Path = config.projectRoot.joinpath(".devcontainer")

    if not targetDirectory.exists():
        raise ValueError(f"No .devcontainer directory was found in {config.projectRoot}")

    if not targetDirectory.is_dir():
        raise ValueError(f"Expected a directory but found: {targetDirectory}")

    if not confirmUninstall(config):
        print("Uninstall cancelled.")
        return

    removedCount: int = 0

    for fileName in SOURCE_FILE_NAMES:
        targetPath: Path = targetDirectory.joinpath(fileName)
        if targetPath.is_symlink() or targetPath.exists():
            if targetPath.is_dir():
                raise ValueError(f"Unexpected directory found during uninstall: {targetPath}")
            targetPath.unlink()
            removedCount += 1

    remainingEntries: list[Path] = []
    for entry in targetDirectory.iterdir():
        remainingEntries.append(entry)

    if remainingEntries:
        raise ValueError(
            f"The directory {targetDirectory} still contains extra files. "
            "Remove them manually before deleting the directory."
        )

    targetDirectory.rmdir()
    print(f"Removed {removedCount} files and deleted {targetDirectory}.")



def runOperation(config: InstallConfig) -> None:
    """Dispatch to the selected install or uninstall action."""
    if config.operation == "install":
        performInstall(config)
        return

    performUninstall(config)



def main(argv: Sequence[str] | None = None) -> int:
    """Run the installer command-line interface."""
    try:
        config: InstallConfig = parseArguments(argv)
        runOperation(config)
        return 0
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Filesystem error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
