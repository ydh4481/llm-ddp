import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_script(script_path: Path):
    print(f"\n🚀 실행 중: {script_path}")
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {script_path}")
        print(e.stderr)


def main():
    print("📦 모든 테스트 데이터 생성 스크립트 실행 시작!\n")

    for domain_dir in sorted(ROOT.iterdir()):
        if domain_dir.is_dir():
            script_path = domain_dir / "generate_data.py"
            if script_path.exists():
                run_script(script_path)
            else:
                print(f"⚠️ generate_data.py 없음: {domain_dir}")

    print("\n✅ 전체 완료!")


if __name__ == "__main__":
    main()
