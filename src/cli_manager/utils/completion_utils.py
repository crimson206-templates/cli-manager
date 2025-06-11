from pathlib import Path
from typing import List, Tuple, Optional

# from .generate_completion import generate_completion, add_wrapper_completion
from .install_completion import (
    install_completion,
    generate_completion,
    add_wrapper_completion,
)
from .meta_parser import add_meta_to_completion


def update_cli_completion(cli_name: str) -> Tuple[bool, List[str]]:
    """
    특정 CLI의 completion 설치/업데이트

    Returns:
        (success, messages): 성공 여부와 메시지 리스트
    """
    completion_script, message = generate_completion(cli_name)
    if not completion_script:
        return False, [message]

    success, messages = install_completion(cli_name, completion_script)
    return success, messages


def update_wrapper_completion(registered_clis: List[str]) -> Tuple[bool, List[str]]:
    """
    superclisubs의 completion 업데이트

    Returns:
        (success, messages): 성공 여부와 메시지 리스트
    """
    # wrapper completion 생성
    wrapper_script = add_wrapper_completion("superclisubs", "supercli", registered_clis)

    # meta 정보 추가
    wrapper_script = add_meta_to_completion(
        "supercli", "supercli", "superclisubs", wrapper_script
    )

    # 설치
    success, messages = install_completion("superclisubs", wrapper_script)
    return success, messages


def get_completion_dir() -> Path:
    """completion 스크립트 디렉토리 경로 반환"""
    return Path.home() / ".completions"


def remove_cli_completion(cli_name: str) -> Tuple[bool, str]:
    """
    CLI의 completion 파일 제거

    Returns:
        (success, message): 성공 여부와 메시지
    """
    try:
        completion_file = get_completion_dir() / cli_name
        if completion_file.exists():
            completion_file.unlink()
            return True, f"Removed completion for {cli_name}"
        return True, f"No completion file found for {cli_name}"
    except Exception as e:
        return False, f"Failed to remove completion for {cli_name}: {e}"
