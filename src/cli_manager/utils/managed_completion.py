from pathlib import Path
from typing import Optional, Tuple, List
import shutil

from .install_completion import generate_completion, install_completion
from .meta_parser import parse_meta_from_completion, add_meta_to_completion


def refresh_cli_completion(
    cli_name: str, backend_name: str, wrapper_name: Optional[str] = None
) -> Tuple[bool, List[str]]:
    """
    특정 CLI의 completion을 갱신하거나 제거

    Args:
        cli_name: 원본 CLI 이름 (예: "docker")
        backend_name: backend 이름 (예: "supercli_backend")
        wrapper_name: wrapper CLI 이름 (선택사항)

    Returns:
        (success, messages): 성공 여부와 상태 메시지 리스트
    """
    messages = []
    completion_dir = Path.home() / ".completions"

    # 1. CLI 존재 여부 확인
    completion_script, gen_message = generate_completion(cli_name)
    if not completion_script:
        # CLI가 없으면 기존 completion 파일 제거
        completion_file = _find_completion_file(completion_dir, cli_name)
        if completion_file:
            try:
                completion_file.unlink()
                messages.append(f"Removed completion for {cli_name} (CLI not found)")
                return True, messages
            except Exception as e:
                return False, [f"Failed to remove completion file: {e}"]
        return True, [f"No completion file found for {cli_name}"]

    # 2. Meta 정보 추가
    completion_with_meta = add_meta_to_completion(
        backend_name, cli_name, wrapper_name or cli_name, completion_script
    )

    # 3. 설치 또는 갱신
    success, install_messages = install_completion(
        cli_name, completion_with_meta, wrapper_name
    )

    messages.extend(install_messages)
    return success, messages


def refresh_all_completions(backend_name: str) -> Tuple[bool, List[str]]:
    """
    모든 관리되는 completion 파일들을 검사하고 갱신

    Args:
        backend_name: backend 이름 (예: "supercli_backend")

    Returns:
        (success, messages): 전체 성공 여부와 상태 메시지 리스트
    """
    messages = []
    completion_dir = Path.home() / ".completions"

    if not completion_dir.exists():
        return True, ["No completions directory found"]

    overall_success = True

    for completion_file in completion_dir.glob("*"):
        if not completion_file.is_file():
            continue

        try:
            content = completion_file.read_text()
            meta = parse_meta_from_completion(content)

            if not meta:  # 우리가 관리하지 않는 파일
                continue

            # Meta 정보로부터 CLI 정보 추출
            cli_name = meta.get("source_cli")
            wrapper_name = meta.get("wrapper_cli")

            if cli_name == wrapper_name:
                wrapper_name = None

            # 개별 CLI completion 갱신
            success, cli_messages = refresh_cli_completion(
                cli_name, backend_name, wrapper_name
            )

            messages.extend(cli_messages)
            if not success:
                overall_success = False

        except Exception as e:
            messages.append(f"Error processing {completion_file.name}: {e}")
            overall_success = False

    return overall_success, messages


def _find_completion_file(completion_dir: Path, cli_name: str) -> Optional[Path]:
    """
    CLI에 해당하는 completion 파일 찾기
    Meta 정보를 확인하여 일치하는 파일 반환
    """
    if not completion_dir.exists():
        return None

    for file in completion_dir.glob("*"):
        if not file.is_file():
            continue

        try:
            content = file.read_text()
            meta = parse_meta_from_completion(content)

            if meta and meta.get("source_cli") == cli_name:
                return file
        except:
            continue

    return None
