import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

def update_notebook(notebook_path):
    # 노트북 파일 읽기
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # 가상환경 설정 섹션 추가 (시스템 요구사항 섹션 다음에)
    venv_cell = new_markdown_cell(
        "## 가상환경 설정\n\n"
        "터미널에서 다음 명령어를 실행하여 가상환경을 설정합니다:\n"
        "```bash\n"
        "python -m venv venv\n"
        "source venv/bin/activate  # macOS/Linux\n"
        "pip install -r requirements.txt\n"
        "```\n"
    )
    
    # 패키지 체크 함수 업데이트
    updated_check_packages = new_code_cell(
        'def check_packages():\n'
        '    """필요한 Python 패키지 확인"""\n'
        '    required_packages = [\n'
        '        "langchain",\n'
        '        "chromadb",\n'
        '        "requests",\n'
        '        "sentence_transformers",\n'
        '        "torch",\n'
        '        "langchain_community",\n'
        '        "langchain_core"\n'
        '    ]\n'
        '    \n'
        '    for package in required_packages:\n'
        '        try:\n'
        '            __import__(package)\n'
        '            print(f"✅ {package} 패키지가 설치되어 있습니다.")\n'
        '        except ImportError:\n'
        '            print(f"❌ {package} 패키지를 찾을 수 없습니다. \'pip install {package}\'를 실행하세요.")\n'
        '\n'
        '# 패키지 확인\n'
        'check_packages()'
    )
    
    # 시스템 요구사항 섹션 찾기
    for i, cell in enumerate(nb.cells):
        if "## 시스템 요구사항" in cell.source:
            # 가상환경 설정 섹션 추가
            nb.cells.insert(i + 1, venv_cell)
            break
    
    # 패키지 체크 함수가 있는 셀 찾아서 업데이트
    for i, cell in enumerate(nb.cells):
        if "def check_packages()" in cell.source:
            nb.cells[i] = updated_check_packages
            break
    
    # 수정된 노트북 저장
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

if __name__ == "__main__":
    notebook_path = "00_setup_and_run.ipynb"
    update_notebook(notebook_path)
