#!/usr/bin/env python3
"""
RCI-SG 消融实验脚本

实验变体:
- V-Full: 完整 RCI-SG 框架（进度错觉 + 动态熵注入）
- V-w/o-Illusion: 移除进度错觉机制
- V-w/o-Entropy: 移除动态熵注入

使用方法:
    python experiment_ablation.py
"""

import os
import sys
import time
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.skill_graph_builder import SkillGraphBuilder
from modules.multi_skill_pathfinder import UDGBuilder, MultiSkillPathfinder


SKILLHUB_DIR = Path(__file__).parent / "output" / "generated_skills"


def find_all_skill_directories(skills_dir: Path) -> list:
    """查找所有包含 SKILL.md 的目录"""
    skill_dirs = []
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / 'SKILL.md').exists():
            skill_dirs.append(item)
    return sorted(skill_dirs)


def run_cycle_detection(variant: str) -> dict:
    """执行循环检测实验
    
    Args:
        variant: 实验变体 ('full', 'w/o_illusion', 'w/o_entropy')
    """
    if not SKILLHUB_DIR.exists():
        print(f"[ERROR] 技能目录不存在: {SKILLHUB_DIR}")
        return {
            'variant': variant,
            'skill_count': 0,
            'cycle_count': 0,
            'avg_hop_count': 0.0,
            'total_affinity': 0.0,
        }
    
    # Phase 1: 解析所有技能
    builder = SkillGraphBuilder()
    skill_dirs = find_all_skill_directories(SKILLHUB_DIR)
    
    print(f"[INFO] 找到 {len(skill_dirs)} 个技能目录")
    
    nodes = []
    for skill_dir in skill_dirs:
        node = builder.parse_skill_file(str(skill_dir))
        if node:
            nodes.append(node)
    
    print(f"[INFO] 成功解析 {len(nodes)} 个技能节点")
    
    if not nodes:
        return {
            'variant': variant,
            'skill_count': 0,
            'cycle_count': 0,
            'avg_hop_count': 0.0,
            'total_affinity': 0.0,
        }
    
    # Phase 2: 构建 UDG
    udg_builder = UDGBuilder(semantic_threshold=0.15)
    udg_builder.add_nodes_from_builder(builder)
    udg_builder.build_skill_subgraphs()
    edge_count = udg_builder.match_all_skill_pairs()
    print(f"[INFO] UDG 边数: {edge_count}")
    
    # Phase 3: 循环检测 (根据变体配置不同参数)
    if variant == 'full':
        enable_illusion = True
        enable_entropy = True
    elif variant == 'w/o_illusion':
        enable_illusion = False
        enable_entropy = True
    elif variant == 'w/o_entropy':
        enable_illusion = True
        enable_entropy = False
    else:
        enable_illusion = True
        enable_entropy = True
    
    pathfinder = MultiSkillPathfinder(
        udg_builder, 
        min_hop=3,
        enable_illusion=enable_illusion,
        enable_entropy=enable_entropy
    )
    cycles = pathfinder.find_vulnerable_paths()
    
    avg_hops = sum(c.hop_count for c in cycles) / len(cycles) if cycles else 0.0
    total_affinity = sum(c.total_affinity for c in cycles) if cycles else 0.0
    
    return {
        'variant': variant,
        'skill_count': len(nodes),
        'cycle_count': len(cycles),
        'avg_hop_count': avg_hops,
        'total_affinity': total_affinity,
    }


def run_ablation_experiment() -> list:
    """执行所有消融实验变体"""
    print(f"\n{'='*80}")
    print(f"[消融实验] 使用生成的技能集: {SKILLHUB_DIR}")
    print(f"{'='*80}")
    
    results = []
    variants = [
        ('V-Full', 'full'),
        ('V-w/o-Illusion', 'w/o_illusion'),
        ('V-w/o-Entropy', 'w/o_entropy'),
    ]
    
    for variant_name, variant_key in variants:
        print(f"\n{'='*80}")
        print(f"[{variant_name}] 开始实验...")
        print(f"{'='*80}")
        t0 = time.time()
        result = run_cycle_detection(variant_key)
        elapsed = time.time() - t0
        result['time'] = elapsed
        result['variant_name'] = variant_name
        
        print(f"\n[{variant_name}] 实验完成:")
        print(f"  循环数: {result['cycle_count']}")
        print(f"  平均跳数: {result['avg_hop_count']:.2f}")
        print(f"  总亲和度: {result['total_affinity']:.2f}")
        print(f"  耗时: {elapsed:.2f}s")
        
        results.append(result)
    
    return results


def print_summary_table(all_results: list):
    """打印消融实验结果汇总表"""
    print(f"\n\n{'='*90}")
    print("RCI-SG 消融实验结果汇总")
    print(f"{'='*90}")
    
    print(f"\n{'实验变体':<25} {'技能数':>8} {'循环图个数':>12} {'平均跳数':>10} {'总亲和度':>12} {'运行时间(s)':>12}")
    print(f"{'-'*90}")
    
    for r in all_results:
        print(f"{r['variant_name']:<25} {r['skill_count']:>8} {r['cycle_count']:>12} "
              f"{r['avg_hop_count']:>10.2f} {r['total_affinity']:>12.2f} {r['time']:>12.2f}")
    
    print(f"{'='*90}")


def main():
    print("="*90)
    print("RCI-SG 消融实验")
    print(f"技能目录: {SKILLHUB_DIR}")
    print(f"实验变体: V-Full, V-w/o-Illusion, V-w/o-Entropy")
    print(f"{'='*90}")
    
    start_time = time.time()
    all_results = run_ablation_experiment()
    total_elapsed = time.time() - start_time
    
    # 打印汇总表格
    print_summary_table(all_results)
    
    print(f"\n总耗时: {total_elapsed:.2f}s")
    print(f"\n实验完成!")


if __name__ == '__main__':
    main()
