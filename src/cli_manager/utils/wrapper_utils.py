import subprocess
from pathlib import Path
from typing import List


def get_wrapper_script_path() -> Path:
    """wrapper script 경로 반환"""
    return Path.home() / ".local" / "bin" / "superclisubs"


def generate_wrapper_script(registered_clis: List[str]) -> str:
    """wrapper script 내용 생성"""
    return f"""#!/bin/bash
# superclisubs wrapper script

registered_clis="{' '.join(registered_clis)}"

if [[ " $registered_clis " =~ " $1 " ]]; then
    "$@"
else
    echo "Unknown command: $1"
    echo "Available commands: $registered_clis"
    exit 1
fi
"""


def update_wrapper_script(registered_clis: List[str]) -> tuple[bool, str]:
    """
    wrapper script 업데이트

    Returns:
        (success, message): 성공 여부와 메시지
    """
    try:
        script_path = get_wrapper_script_path()
        script_path.parent.mkdir(parents=True, exist_ok=True)

        # 스크립트 생성
        script_content = generate_wrapper_script(registered_clis)
        script_path.write_text(script_content)

        # 실행 권한 설정
        subprocess.run(["chmod", "+x", str(script_path)], check=True)

        return True, f"Updated wrapper script at {script_path}"

    except Exception as e:
        return False, f"Failed to update wrapper script: {e}"


def get_registered_clis() -> List[str]:
    """
    현재 등록된 CLI 목록 읽기

    Note:
        wrapper script가 없으면 빈 목록 반환
    """
    try:
        script_path = get_wrapper_script_path()
        if not script_path.exists():
            return []

        content = script_path.read_text()

        # registered_clis="..." 부분 찾기
        for line in content.splitlines():
            if line.startswith('registered_clis="'):
                # 따옴표 안의 내용을 공백으로 분리
                clis = line.split('"')[1].split()
                return clis

        return []

    except:
        return []
