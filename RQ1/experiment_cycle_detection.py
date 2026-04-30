#!/usr/bin/env python3
"""
循环图检测批量实验脚本

针对 skillhub_skills 中的 7 个类别分别执行循环检测，
统计每个类别的循环图个数和平均跳数。

使用方法:
    python experiment_cycle_detection.py
"""

import os
import sys
import time
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.skill_graph_builder import SkillGraphBuilder
from modules.multi_skill_pathfinder import UDGBuilder, MultiSkillPathfinder


SKILLHUB_DIR = Path(__file__).parent / "skillhub_skills"


CATEGORIES = [
    "ai_enhanced",
    "browser_automation",
    "dev_tools",
    "info_processing",
    "knowledge_management",
    "office_collaboration",
    "tools",
]


def find_skill_directories(category_dir: Path) -> list:
    """递归查找所有包含 SKILL.md 的目录
    
    skillhub_skills 的目录结构是三层嵌套：
    category/skill-name/skill-name/SKILL.md
    
    需要找到所有直接包含 SKILL.md 的目录
    """
    skill_dirs = []
    for root, dirs, files in category_dir.rglob('*'):
        # 检查是否直接包含 SKILL.md
        if (Path(root) / 'SKILL.md').exists():
            skill_dirs.append(Path(root))
    return skill_dirs


def detect_cycles_for_category(category: str) -> dict:
    """针对单个类别执行循环检测"""
    cat_dir = SKILLHUB_DIR / category
    
    if not cat_dir.exists():
        print(f"[SKIP] 类别目录不存在: {cat_dir}")
        return {
            'category': category,
            'skill_count': 0,
            'action_count': 0,
            'cycle_count': 0,
            'avg_hop_count': 0.0,
            'total_affinity': 0.0,
        }
    
    print(f"\n{'='*70}")
    print(f"[实验] 类别: {category}")
    print(f"{'='*70}")
    
    # Phase 1: 解析技能
    print(f"\n[Phase 1] 解析 {category} 类别的技能...")
    builder = SkillGraphBuilder()
    
    # 手动扫描所有技能目录（支持嵌套结构）
    skill_dirs = []
    for item in cat_dir.iterdir():
        if item.is_dir():
            # 递归查找 SKILL.md
            for root, dirs, files in os.walk(str(item)):
                if 'SKILL.md' in files:
                    skill_dirs.append(Path(root))
                    break  # 找到第一个就停止，避免重复
    
    nodes = []
    for skill_dir in skill_dirs:
        node = builder.parse_skill_file(str(skill_dir))
        if node:
            nodes.append(node)
    
    print(f"[INFO] 解析到 {len(nodes)} 个技能节点")
    
    if not nodes:
        print(f"[WARN] {category} 无可用技能")
        return {
            'category': category,
            'skill_count': 0,
            'action_count': 0,
            'cycle_count': 0,
            'avg_hop_count': 0.0,
            'total_affinity': 0.0,
        }
    
    # Phase 2: 构建 UDG 并检测循环
    print(f"\n[Phase 2] 构建统一依赖图并检测循环...")
    udg_builder = UDGBuilder(semantic_threshold=0.15)
    udg_builder.add_nodes_from_builder(builder)
    udg_builder.build_skill_subgraphs()
    edge_count = udg_builder.match_all_skill_pairs()
    print(f"[INFO] UDG 边数: {edge_count}")
    
    # 执行循环检测
    pathfinder = MultiSkillPathfinder(udg_builder, min_hop=3)
    cycles = pathfinder.find_vulnerable_paths()
    
    print(f"\n[RESULT] {category}: 发现 {len(cycles)} 条循环路径")
    
    if cycles:
        avg_hops = sum(c.hop_count for c in cycles) / len(cycles)
        total_affinity = sum(c.total_affinity for c in cycles)
        print(f"[RESULT] 平均跳数: {avg_hops:.2f}")
        print(f"[RESULT] 总亲和度: {total_affinity:.2f}")
    else:
        avg_hops = 0.0
        total_affinity = 0.0
    
    return {
        'category': category,
        'skill_count': len(nodes),
        'action_count': len(udg_builder.global_action_nodes),
        'cycle_count': len(cycles),
        'avg_hop_count': avg_hops,
        'total_affinity': total_affinity,
    }


def print_summary_table(results: list[dict]):
    """打印实验结果表格"""
    print(f"\n\n{'='*80}")
    print("实验结果汇总")
    print(f"{'='*80}")
    print(f"\n{'类别':<25} {'技能数':>8} {'动作数':>8} {'循环图个数':>12} {'平均跳数':>10}")
    print(f"{'-'*80}")
    
    total_cycles = 0
    total_skills = 0
    for r in results:
        print(f"{r['category']:<25} {r['skill_count']:>8} {r['action_count']:>8} "
              f"{r['cycle_count']:>12} {r['avg_hop_count']:>10.2f}")
        total_cycles += r['cycle_count']
        total_skills += r['skill_count']
    
    print(f"{'-'*80}")
    print(f"{'总计':<25} {total_skills:>8} {'':>8} {total_cycles:>12}")
    print(f"{'='*80}")


def main():
    print("="*80)
    print("RCI-SG 循环图检测批量实验")
    print(f"技能目录: {SKILLHUB_DIR}")
    print(f"{'='*80}")
    
    start_time = time.time()
    all_results = []
    
    for category in CATEGORIES:
        t0 = time.time()
        result = detect_cycles_for_category(category)
        elapsed = time.time() - t0
        print(f"\n[时间] {category} 耗时: {elapsed:.2f}s")
        all_results.append(result)
    
    total_elapsed = time.time() - start_time
    
    # 打印汇总表格
    print_summary_table(all_results)
    
    print(f"\n总耗时: {total_elapsed:.2f}s")
    print(f"\n实验完成!")


if __name__ == '__main__':
    main()
