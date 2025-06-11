import subprocess
import shutil
import os
from pathlib import Path

def install_supercli():

    local_bin = Path.home() / ".local" / "bin"
    target_file = local_bin / "supercli"
    
    local_bin.mkdir(parents=True, exist_ok=True)

    script_content = '''#!/bin/bash
# supercli wrapper script

registered_clis="pip npm git docker kubectl"

if [[ " $registered_clis " =~ " $1 " ]]; then
    "$@"
else
    supercli_backend "$@"
fi
'''
    target_file.write_text(script_content)
    
    subprocess.run(["chmod", "+x", str(target_file)], check=True)
    
    print(f"✅ supercli installed to {target_file}")
    print("✅ Execute permission set - available globally!")
