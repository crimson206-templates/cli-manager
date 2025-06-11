import json
import re
from typing import Dict, Optional


META_PREFIX = "# META: "


def add_meta_to_completion(
    backend_name: str, source_cli: str, wrapper_cli: str, completion_content: str
) -> str:
    """
    completion 파일에 메타 정보를 추가

    Args:
        backend_name: supercli backend 이름 (예: "supercli_backend")
        source_cli: 원본 CLI 이름 (예: "docker")
        wrapper_cli: wrapper CLI 이름 (예: "my_docker")
        completion_content: 기존 completion script 내용

    Returns:
        메타 정보가 추가된 completion script
    """
    meta_data = {
        "backend": backend_name,
        "source_cli": source_cli,
        "wrapper_cli": wrapper_cli,
    }

    meta_line = META_PREFIX + json.dumps(meta_data, separators=(",", ":"))

    # 메타 정보를 맨 위에 추가
    return f"{meta_line}\n{completion_content}"


def parse_meta_from_completion(completion_content: str) -> Optional[Dict[str, str]]:
    """
    completion 파일에서 메타 정보를 추출

    Args:
        completion_content: completion script 내용

    Returns:
        메타 정보 dictionary 또는 None (메타 정보가 없는 경우)
    """
    lines = completion_content.split("\n")

    # 첫 번째 줄에서 메타 정보 찾기
    for line in lines:
        if line.startswith(META_PREFIX):
            try:
                meta_json = line[len(META_PREFIX) :]
                return json.loads(meta_json)
            except json.JSONDecodeError:
                # 메타 정보 파싱 실패
                return None

    return None
