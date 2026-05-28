import json, subprocess
from datetime import datetime
from pathlib import Path

ROADMAP_DIR = Path("C:/resfi/roadmap")
DATA_FILE   = ROADMAP_DIR / "data" / "resfi_data.json"

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    data['meta']['updated']    = datetime.now().strftime('%Y-%m-%d %H:%M')
    data['meta']['updated_by'] = 'Claude Code'
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_worklog(block_id: str, summary: str, changes: list):
    data = load_data()
    entry = {
        "id":      len(data['worklog']) + 1,
        "date":    datetime.now().strftime('%Y-%m-%d'),
        "time":    datetime.now().strftime('%H:%M'),
        "block":   block_id,
        "summary": summary,
        "changes": changes
    }
    data['worklog'].append(entry)
    save_data(data)
    return entry

def update_block_field(block_id: str, field_path: str, value):
    """특정 블럭의 특정 필드 값 변경
    예: update_block_field('L2', 'badge', 'done')
    """
    data = load_data()
    if block_id in data['blocks']:
        keys = field_path.split('.')
        obj = data['blocks'][block_id]
        for key in keys[:-1]:
            obj = obj[key]
        obj[keys[-1]] = value
        save_data(data)

def git_push(commit_msg: str) -> bool:
    try:
        subprocess.run(['git', '-C', str(ROADMAP_DIR), 'add', '.'],
                       check=True, capture_output=True)
        result = subprocess.run(
            ['git', '-C', str(ROADMAP_DIR), 'commit', '-m', commit_msg],
            capture_output=True, text=True
        )
        if result.returncode not in (0, 1):  # 1 = nothing to commit
            return False
        push = subprocess.run(
            ['git', '-C', str(ROADMAP_DIR), 'push'],
            capture_output=True, text=True
        )
        return push.returncode == 0
    except Exception as e:
        print(f'❌ git push 실패: {e}')
        return False

def update_roadmap(block_id: str, summary: str, changes: list):
    """
    메인 함수 — 마스터가 "로드맵 업데이트" 명령 시 Claude Code가 호출

    예시:
    update_roadmap(
        block_id='L2',
        summary='Phase 1 현황 업데이트',
        changes=['PASS: 204 → 250개', 'FAIL: 141 → 100개']
    )
    """
    print(f"\n🔄 로드맵 업데이트: [{block_id}] {summary}")

    entry = add_worklog(block_id, summary, changes)
    print(f"  ✅ 작업일지 #{entry['id']} 추가")

    commit_msg = f"update({block_id}): {summary}"
    if git_push(commit_msg):
        print(f"  ✅ GitHub push 완료")
        print(f"  🌐 https://today2bobi-lab.github.io/resfi-roadmap/")
        print(f"  ⏳ 1~2분 후 자동 반영")
    else:
        print(f"  ⚠️  push 실패 — JSON은 로컬에 저장됨. 수동 push 필요.")

if __name__ == "__main__":
    update_roadmap(
        block_id='L-INFRA',
        summary='GitHub Pages 연동 완료',
        changes=[
            'Pages URL: https://today2bobi-lab.github.io/resfi-roadmap/',
            'JSON 분리 완료',
            '"로드맵 업데이트" 커맨드 활성화'
        ]
    )
