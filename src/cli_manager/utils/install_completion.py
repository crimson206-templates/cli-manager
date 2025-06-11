import subprocess
from pathlib import Path
from typing import Optional, Tuple
from cli_manager.utils.hash_cleaner import clean_content


def generate_completion(cli_name: str) -> Tuple[Optional[str], str]:
    """
    지정된 CLI의 completion 생성

    Returns:
        (completion_script, message): completion script와 상태 메시지
    """
    try:
        result = subprocess.run(
            [cli_name, "completions", "bash"],
            capture_output=True,
            text=True,
            check=True,
        )

        script = clean_content(result.stdout, cli_name)
        return script, f"Generated completion for {cli_name}"
    except subprocess.CalledProcessError as e:
        return None, f"Failed to generate completion for {cli_name}: {e}"
    except FileNotFoundError:
        return None, f"{cli_name} not found in PATH"


def add_wrapper_completion(
    completion_script: str, wrapper_name: str, cli_name: str
) -> str:
    """wrapper script용 completion 추가"""

    wrapper_completion = f"""
# {wrapper_name} completion (wrapper for {cli_name})
__{wrapper_name}_complete() {{
    local cur prev words cword
    _init_completion || return
    
    # {cli_name} completion 함수 찾아서 호출
    local backend_func=$(declare -F | grep _{cli_name}.*_complete | head -1 | cut -d' ' -f3)
    if [ -n "$backend_func" ]; then
        $backend_func "$@"
    fi
}}

complete -F __{wrapper_name}_complete {wrapper_name}
"""

    return completion_script + wrapper_completion


def install_completion(
    cli_name: str, completion_script: str, wrapper_name: Optional[str] = None
) -> Tuple[bool, list[str]]:
    """
    completion 설치

    Returns:
        (success, messages): 성공 여부와 메시지 리스트
    """
    messages = []

    try:
        # ~/.completions 폴더 설정
        completion_dir = Path.home() / ".completions"
        completion_dir.mkdir(exist_ok=True)

        # completion 파일 설치
        completion_file = completion_dir / cli_name
        completion_file.write_text(completion_script)

        # .bashrc에 로더 추가 (한 번만)
        bashrc_message = add_bashrc_loader()
        if bashrc_message:
            messages.append(bashrc_message)

        messages.append(f"✅ Completion installed: {completion_file}")

        if wrapper_name:
            messages.append(f"✅ Wrapper completion added for: {wrapper_name}")

        messages.append("Restart terminal to activate")

        return True, messages

    except Exception as e:
        return False, [f"Failed to install completion: {e}"]


def add_bashrc_loader() -> Optional[str]:
    """
    필요시 .bashrc에 completion 로더 추가

    Returns:
        메시지 (추가했을 경우만)
    """
    bashrc = Path.home() / ".bashrc"

    if bashrc.exists() and "~/.completions" in bashrc.read_text():
        return None  # 이미 있음

    loader = """
# Auto-load custom completions
for completion in ~/.completions/*; do
    [ -r "$completion" ] && source "$completion"
done
"""

    try:
        with open(bashrc, "a") as f:
            f.write(loader)
        return "Added completion loader to ~/.bashrc"
    except Exception as e:
        return f"Failed to add loader to .bashrc: {e}"
