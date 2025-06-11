import pytest
from cli_manager.utils.meta_parser import (
    add_meta_to_completion,
    parse_meta_from_completion,
    META_PREFIX
)


class TestAddMetaToCompletion:
    def test_add_meta_basic(self):
        """기본적인 메타 정보 추가 테스트"""
        backend = "supercli_backend"
        source = "docker"
        wrapper = "my_docker"
        content = "# Docker completion script\ncomplete -F _docker docker"
        
        result = add_meta_to_completion(backend, source, wrapper, content)
        
        lines = result.split('\n')
        assert lines[0].startswith('# META: ')
        assert '"backend":"supercli_backend"' in lines[0]
        assert '"source_cli":"docker"' in lines[0]
        assert '"wrapper_cli":"my_docker"' in lines[0]
        assert lines[1] == "# Docker completion script"
        
    def test_add_meta_empty_content(self):
        """빈 content에 메타 정보 추가"""
        result = add_meta_to_completion("backend", "cli", "wrapper", "")
        
        lines = result.split('\n')
        assert lines[0].startswith('# META: ')
        assert lines[1] == ""
        
    def test_add_meta_special_characters(self):
        """특수 문자가 포함된 이름들"""
        result = add_meta_to_completion("my-backend", "cli_tool", "my.wrapper", "content")
        
        meta = parse_meta_from_completion(result)
        assert meta["backend"] == "my-backend"
        assert meta["source_cli"] == "cli_tool"
        assert meta["wrapper_cli"] == "my.wrapper"


class TestParseMetaFromCompletion:
    def test_parse_meta_valid(self):
        """정상적인 메타 정보 파싱"""
        content = '# META: {"backend":"test_backend","source_cli":"test_cli","wrapper_cli":"test_wrapper"}\n# completion script'
        
        meta = parse_meta_from_completion(content)
        
        assert meta is not None
        assert meta["backend"] == "test_backend"
        assert meta["source_cli"] == "test_cli"
        assert meta["wrapper_cli"] == "test_wrapper"
        
    def test_parse_meta_no_meta(self):
        """메타 정보가 없는 경우"""
        content = "# Just a normal completion script\ncomplete -F _test test"
        
        meta = parse_meta_from_completion(content)
        
        assert meta is None
        
    def test_parse_meta_invalid_json(self):
        """잘못된 JSON 형식"""
        content = "# META: {invalid json}\n# completion script"
        
        meta = parse_meta_from_completion(content)
        
        assert meta is None
        
    def test_parse_meta_middle_of_file(self):
        """메타 정보가 파일 어디에 있어도 찾을 수 있음"""
        content = """# Normal comment
# META: {"backend":"test","source_cli":"test","wrapper_cli":"test"}
# completion script"""
        
        meta = parse_meta_from_completion(content)
        
        assert meta is not None


class TestIntegration:
    def test_full_workflow(self):
        """전체 워크플로우 테스트: add -> parse -> remove"""
        backend = "my_backend"
        source = "kubectl"
        wrapper = "my_kubectl"
        original_content = "# Kubectl completion\ncomplete -F _kubectl kubectl"
        
        # 1. 메타 정보 추가
        with_meta = add_meta_to_completion(backend, source, wrapper, original_content)
        
        # 2. 메타 정보 파싱
        parsed_meta = parse_meta_from_completion(with_meta)
        assert parsed_meta["backend"] == backend
        assert parsed_meta["source_cli"] == source
        assert parsed_meta["wrapper_cli"] == wrapper

        
    def test_complex_completion_script(self):
        """복잡한 completion script 테스트"""
        backend = "super_backend"
        source = "helm"
        wrapper = "my_helm"
        
        complex_content = """# Helm completion script
_helm_complete() {
    local cur prev words cword
    _init_completion || return
    
    case "${words[1]}" in
        install|upgrade)
            COMPREPLY=($(compgen -W "chart1 chart2" -- "$cur"))
            ;;
        *)
            COMPREPLY=($(compgen -W "install upgrade list" -- "$cur"))
            ;;
    esac
}

complete -F _helm_complete helm"""
        
        # 전체 플로우 테스트
        with_meta = add_meta_to_completion(backend, source, wrapper, complex_content)
        parsed_meta = parse_meta_from_completion(with_meta)
        
        assert parsed_meta["backend"] == backend
        assert parsed_meta["source_cli"] == source  
        assert parsed_meta["wrapper_cli"] == wrapper
        
        # 메타 정보가 첫 줄에만 있는지 확인
        lines = with_meta.split('\n')
        meta_count = sum(1 for line in lines if line.startswith('# META:'))
        assert meta_count == 1

def test_add_meta_to_completion():
    # Test with empty completion content
    result = add_meta_to_completion("backend", "source", "wrapper", "")
    assert result.startswith(META_PREFIX)
    assert '"backend":"backend"' in result
    assert '"source_cli":"source"' in result
    assert '"wrapper_cli":"wrapper"' in result

    # Test with non-empty completion content
    completion_content = "echo 'test'"
    result = add_meta_to_completion("backend", "source", "wrapper", completion_content)
    assert result.startswith(META_PREFIX)
    assert '"backend":"backend"' in result
    assert '"source_cli":"source"' in result
    assert '"wrapper_cli":"wrapper"' in result
    assert completion_content in result
    assert result.endswith(completion_content)

    # Test with completion content that already has meta
    completion_with_meta = f'{META_PREFIX}{{"old":"meta"}}\necho "test"'
    result = add_meta_to_completion("backend", "source", "wrapper", completion_with_meta)
    assert result.startswith(META_PREFIX)
    assert '"backend":"backend"' in result
    assert '"source_cli":"source"' in result
    assert '"wrapper_cli":"wrapper"' in result
    assert 'echo "test"' in result

def test_parse_meta_from_completion():
    # Test with valid meta
    content = f'{META_PREFIX}{{"backend":"test","source_cli":"src","wrapper_cli":"wrap"}}\necho "test"'
    result = parse_meta_from_completion(content)
    assert result is not None
    assert result["backend"] == "test"
    assert result["source_cli"] == "src"
    assert result["wrapper_cli"] == "wrap"

    # Test with invalid JSON meta
    content = f'{META_PREFIX}invalid json\necho "test"'
    result = parse_meta_from_completion(content)
    assert result is None

    # Test with no meta
    content = 'echo "test"'
    result = parse_meta_from_completion(content)
    assert result is None

    # Test with empty content
    result = parse_meta_from_completion("")
    assert result is None

    # Test with only meta prefix
    result = parse_meta_from_completion(META_PREFIX)
    assert result is None