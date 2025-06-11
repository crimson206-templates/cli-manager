import subprocess
import sys
from pathlib import Path
from cleo.commands.command import Command
from cleo.helpers import argument, option


class CompletionInitCommand(Command):
    name = "completion-init"
    description = "Install bash completion for any CLI to ~/.completions/"
    
    arguments = [
        argument("cli_name", "Name of the CLI to install completion for", optional=True)
    ]
    
    options = [
        option("wrapper", "w", "Also setup completion for a wrapper script", flag=False)
    ]
    
    def handle(self) -> int:
        # CLI 이름 결정
        cli_name = self.argument("cli_name") or "supercli_backend"
        wrapper_name = self.option("wrapper")
        
        # completion 생성
        completion_script = self.generate_completion(cli_name)
        if not completion_script:
            return 1
        
        # wrapper completion도 필요하면 추가
        if wrapper_name:
            completion_script = self.add_wrapper_completion(completion_script, wrapper_name, cli_name)
        
        # 설치
        return self.install_completion(cli_name, completion_script)
    
    def generate_completion(self, cli_name: str) -> str | None:
        """지정된 CLI의 completion 생성"""
        try:
            result = subprocess.run(
                [cli_name, "completions", "bash"],
                capture_output=True, text=True, check=True
            )
            self.line(f"<comment>Generated completion for {cli_name}</comment>")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.line(f"<error>Failed to generate completion for {cli_name}: {e}</error>")
            return None
        except FileNotFoundError:
            self.line(f"<error>{cli_name} not found in PATH</error>")
            return None
    
    def add_wrapper_completion(self, completion_script: str, wrapper_name: str, cli_name: str) -> str:
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
    
    def install_completion(self, cli_name: str, completion_script: str) -> int:
        """completion 설치"""
        
        # ~/.completions 폴더 설정
        completion_dir = Path.home() / ".completions"
        completion_dir.mkdir(exist_ok=True)
        
        # completion 파일 설치
        completion_file = completion_dir / cli_name
        completion_file.write_text(completion_script)
        
        # .bashrc에 로더 추가 (한 번만)
        self.add_bashrc_loader()
        
        self.line(f"<info>✅ Completion installed: {completion_file}</info>")
        
        wrapper_name = self.option("wrapper")
        if wrapper_name:
            self.line(f"<info>✅ Wrapper completion added for: {wrapper_name}</info>")
        
        self.line("<comment>Restart terminal to activate</comment>")
        return 0

    def add_bashrc_loader(self):
        """필요시 .bashrc에 completion 로더 추가"""
        bashrc = Path.home() / ".bashrc"
        
        if bashrc.exists() and "~/.completions" in bashrc.read_text():
            return  # 이미 있음
        
        loader = '''
# Auto-load custom completions
for completion in ~/.completions/*; do
    [ -r "$completion" ] && source "$completion"
done
'''

        with open(bashrc, "a") as f:
            f.write(loader)
        
        self.line("<info>Added completion loader to ~/.bashrc</info>")