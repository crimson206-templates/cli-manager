import subprocess
import shutil
import os
from pathlib import Path
from typing import List

from cli_manager.utils.install_completion import (
    install_completion,
    generate_completion,
    add_wrapper_completion,
)
from cli_manager.utils.meta_parser import add_meta_to_completion


# 모든 registered CLI 목록 (completion과 공유)
REGISTERED_CLIS = ["subcli1", "subcli2"]


def install_supercli():
    """superclisubs wrapper 스크립트 설치 및 completion 설정"""
    # wrapper 스크립트 설치
    local_bin = Path.home() / ".local" / "bin"
    target_file = local_bin / "superclisubs"

    local_bin.mkdir(parents=True, exist_ok=True)

    script_content = f"""#!/bin/bash
# superclisubs wrapper script

registered_clis="{' '.join(REGISTERED_CLIS)}"

if [[ " $registered_clis " =~ " $1 " ]]; then
    "$@"
else
    echo "Unknown command: $1"
    echo "Available commands: $registered_clis"
    exit 1
fi
"""
    target_file.write_text(script_content)
    subprocess.run(["chmod", "+x", str(target_file)], check=True)

    print(f"✅ superclisubs installed to {target_file}")
    print("✅ Execute permission set - available globally!")

    # registered CLI들의 completion 설치
    for cli in REGISTERED_CLIS:
        completion_script, message = generate_completion(cli)
        if completion_script:
            print(f"Installing completion for {cli}...")
            success, messages = install_completion(cli, completion_script)
            for msg in messages:
                print(msg)

    # superclisubs completion 설치
    print("Installing completion for superclisubs...")
    wrapper_script = add_wrapper_completion("superclisubs", "supercli", REGISTERED_CLIS)
    wrapper_script = add_meta_to_completion(
        "supercli", "supercli", "superclisubs", wrapper_script
    )
    success, messages = install_completion("superclisubs", wrapper_script)
    for msg in messages:
        print(msg)


if __name__ == "__main__":
    install_supercli()
