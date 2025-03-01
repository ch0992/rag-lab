import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

def modify_notebook(notebook_path):
    # 노트북 파일 읽기
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # 새로운 마크다운 셀 추가
    new_cell = new_markdown_cell(
        "## 환경 설정 확인\n\n"
        "이 섹션에서는 시스템 환경이 올바르게 설정되어 있는지 확인합니다."
    )
    
    # 셀 추가
    nb.cells.insert(1, new_cell)
    
    # 수정된 노트북 저장
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

if __name__ == "__main__":
    notebook_path = "00_setup_and_run.ipynb"
    modify_notebook(notebook_path)
