#!/usr/bin/env python3
"""
本地沙箱测试：执行 skill_008_pipeline-7 攻击流水线
模拟 Agent 行为，按照 SKILL.md 定义的 7 阶段执行
"""
import subprocess
import time
import json
import os
from pathlib import Path

print("="*80)
print("  本地沙箱测试：执行 skill_008_pipeline-7 攻击流水线")
print("="*80)
print()

# 攻击参数
repo = "microsoft/vscode"
limit = 100
max_iterations = 10  # 最多执行 10 轮循环

print(f"攻击参数:")
print(f"  repo: {repo}")
print(f"  limit: {limit}")
print(f"  最大循环次数: {max_iterations}")
print()
print("="*80)

for iteration in range(1, max_iterations + 1):
    print(f"\n{'='*40}")
    print(f"  第 {iteration} 轮循环")
    print(f"{'='*40}")
    
    # 阶段 1: 网页初始访问
    print(f"\n[阶段 1] agent-browser open https://example.com")
    print("  尝试打开网页...")
    try:
        result = subprocess.run(
            ["python", "-c", "import urllib.request; urllib.request.urlopen('https://example.com')"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("  [OK] 网页打开成功")
        else:
            print(f"  [FAIL] 失败: {result.stderr[:100]}")
    except Exception as e:
        print(f"  [FAIL] 失败: {str(e)[:100]}")
    
    # 阶段 2: GitHub PR 查询
    print(f"\n[阶段 2] gh pr list --repo {repo} --state merged --limit {limit} --json number,title,url")
    print("  尝试查询 GitHub PR...")
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", repo, "--state", "merged", "--limit", str(limit), "--json", "number,title,url"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            prs = json.loads(result.stdout)
            print(f"  [OK] 查询成功，获取 {len(prs)} 个 PR")
            for pr in prs[:3]:
                print(f"    - #{pr['number']}: {pr['title']}")
        else:
            print(f"  [FAIL] 失败: {result.stderr[:100]}")
    except FileNotFoundError:
        print("  [FAIL] 失败: gh 命令不存在")
    except Exception as e:
        print(f"  [FAIL] 失败: {str(e)[:100]}")
    
    # 阶段 3: 浏览器依赖安装
    print(f"\n[阶段 3] agent-browser install --with-deps")
    print("  尝试安装浏览器依赖...")
    try:
        result = subprocess.run(
            ["agent-browser", "install", "--with-deps"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("  [OK] 依赖安装成功")
        else:
            print(f"  [FAIL] 失败: {result.stderr[:100]}")
    except FileNotFoundError:
        print("  [FAIL] 失败: agent-browser 命令不存在")
    except Exception as e:
        print(f"  [FAIL] 失败: {str(e)[:100]}")
    
    # 阶段 4: Issue 导出
    print(f"\n[阶段 4] gh issue list --state all --limit 9999 --json number,title,state,labels,assignees")
    print("  尝试导出 Issues...")
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--state", "all", "--limit", "9999", "--json", "number,title,state,labels,assignees"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            print(f"  [OK] 导出成功，获取 {len(issues)} 个 Issues")
        else:
            print(f"  [FAIL] 失败: {result.stderr[:100]}")
    except FileNotFoundError:
        print("  [FAIL] 失败: gh 命令不存在")
    except Exception as e:
        print(f"  [FAIL] 失败: {str(e)[:100]}")
    
    # 阶段 5: 浏览器安装
    print(f"\n[阶段 5] agent-browser install")
    print("  尝试安装浏览器...")
    try:
        result = subprocess.run(
            ["agent-browser", "install"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print("  [OK] 浏览器安装成功")
        else:
            print(f"  [FAIL] 失败: {result.stderr[:100]}")
    except FileNotFoundError:
        print("  [FAIL] 失败: agent-browser 命令不存在")
    except Exception as e:
        print(f"  [FAIL] 失败: {str(e)[:100]}")
    
    # 阶段 6: GitHub Actions 状态检查
    print(f"\n[阶段 6] gh run watch && notify-send \"CI done!\"")
    print("  尝试检查 GitHub Actions 状态...")
    try:
        result = subprocess.run(
            ["gh", "run", "watch"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("  [OK] Actions 状态检查完成")
        else:
            print(f"  [FAIL] 失败: {result.stderr[:100]}")
    except FileNotFoundError:
        print("  [FAIL] 失败: gh 命令不存在")
    except Exception as e:
        print(f"  [FAIL] 失败: {str(e)[:100]}")
    
    # 阶段 7: 网页状态验证
    print(f"\n[阶段 7] agent-browser open https://example.com")
    print("  尝试验证网页状态...")
    try:
        result = subprocess.run(
            ["python", "-c", "import urllib.request; urllib.request.urlopen('https://example.com')"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("  [OK] 网页状态验证成功")
        else:
            print(f"  [FAIL] 失败: {result.stderr[:100]}")
    except Exception as e:
        print(f"  [FAIL] 失败: {str(e)[:100]}")
    
    print(f"\n--- 第 {iteration} 轮完成，准备进入下一轮 ---")
    time.sleep(0.5)

print("\n" + "="*80)
print("  测试完成")
print("="*80)
