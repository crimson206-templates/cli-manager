import re


def extract_completion_function(content, cli_name):
    """모든 completion 함수를 찾고, cli_name이 포함된 첫 번째 함수 반환"""
    functions = re.findall(r"(_[a-zA-Z0-9_]*_complete)", content)

    for func in functions:
        if cli_name in func:
            return func
    return None


def clean_function_name(dirty_func_name, cli_name):
    """해시값이 붙은 함수명에서 깔끔한 함수명 추출"""
    if not dirty_func_name:
        return None

    # 단순하게: _로 split해서 cli_name 찾고 재조립
    parts = dirty_func_name.split("_")

    # cli_name이 포함된 부분 찾기
    for i, part in enumerate(parts):
        if cli_name.startswith(part) or part in cli_name:
            # cli_name 복원
            return f"_{cli_name}_complete"

    return dirty_func_name


def clean_content(content, cli_name):
    """content에서 해시값이 붙은 completion 함수명을 깔끔하게 정리"""
    # 1. 원본 함수명 추출
    original_func = extract_completion_function(content, cli_name)
    if not original_func:
        return content

    # 2. 깔끔한 함수명으로 변환
    clean_func = clean_function_name(original_func, cli_name)
    if not clean_func:
        return content

    # 3. content에서 replace
    cleaned_content = content.replace(original_func, clean_func)

    return cleaned_content
