#!/usr/bin/env python3
"""
Pylint检查脚本
用于对项目中的Python代码进行静态分析
"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 需要检查的目录
CHECK_DIRS = ["src", "tests"]

# pylint配置文件
PYLINTRC = PROJECT_ROOT / ".pylintrc"


def run_pylint_on_directory(directory):
    """对指定目录运行pylint检查"""
    dir_path = PROJECT_ROOT / directory

    if not dir_path.exists():
        print(f"目录 {directory} 不存在，跳过...")
        return 0

    print(f"\n{'='*60}")
    print(f"正在检查 {directory} 目录...")
    print(f"{'='*60}")

    # 查找所有Python文件
    python_files = list(dir_path.rglob("*.py"))

    if not python_files:
        print(f"在 {directory} 中没有找到Python文件")
        return 0

    # 构建pylint命令
    cmd = [sys.executable, "-m", "pylint", "--rcfile", str(PYLINTRC), "--output-format=colorized"]

    # 添加Python文件
    cmd.extend([str(f) for f in python_files])

    try:
        # 运行pylint
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

        # 输出结果
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("错误信息:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)

        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"运行pylint时出错: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("错误: 未找到pylint，请先安装: pip install -r requirements.txt", file=sys.stderr)
        return 1


def run_pylint_on_file(file_path):
    """对单个文件运行pylint检查"""
    file_path = PROJECT_ROOT / file_path

    if not file_path.exists():
        print(f"文件 {file_path} 不存在")
        return 1

    print(f"\n正在检查文件: {file_path}")

    cmd = [sys.executable, "-m", "pylint", "--rcfile", str(PYLINTRC), "--output-format=colorized", str(file_path)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("错误信息:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)

        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"运行pylint时出错: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("错误: 未找到pylint，请先安装: pip install -r requirements.txt", file=sys.stderr)
        return 1


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 检查特定文件或目录
        target = sys.argv[1]

        if target.endswith(".py"):
            # 检查单个文件
            return run_pylint_on_file(target)
        # 检查指定目录
        return run_pylint_on_directory(target)

    # 检查所有配置的目录
    print("开始检查项目代码质量...")

    total_errors = 0

    for directory in CHECK_DIRS:
        errors = run_pylint_on_directory(directory)
        if errors is not None:
            total_errors += errors

    print(f"\n{'='*60}")
    print("检查完成！")

    if total_errors == 0:
        print("✅ 所有代码都通过了pylint检查")
    else:
        print(f"⚠️  发现 {total_errors} 个问题，请查看上面的详细信息")

    return total_errors


if __name__ == "__main__":
    sys.exit(main())
