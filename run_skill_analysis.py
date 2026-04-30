#!/usr/bin/env python3
"""
循环图检测实验脚本 - 针对 skills_downloaded 目录

对 68 个 skill 执行循环检测，统计：
- 循环图个数
- 动作总数
- 具体跳数分布

使用方法:
    python experiment_skills_downloaded.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.skill_graph_builder import SkillGraphBuilder
from modules.multi_skill_pathfinder import UDGBuilder, MultiSkillPathfinder


SKILLS_DIR = Path(__file__).parent / "skills_downloaded"


def main():
    print("="*80)
    print("RCI-SG 循环图检测实验 - skills_downloaded")
    print(f"技能目录: {SKILLS_DIR}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    # Phase 1: 解析所有技能
    print(f"\n[Phase 1] 解析技能...")
    builder = SkillGraphBuilder()
    nodes = builder.parse_skill_directory(str(SKILLS_DIR))
    print(f"[INFO] 共解析 {len(nodes)} 个技能节点")
    
    if not nodes:
        print("[ERROR] 未解析到任何技能")
        return
    
    # Phase 2: 构建 UDG
    print(f"\n[Phase 2] 构建统一依赖图...")
    udg_builder = UDGBuilder(semantic_threshold=0.15)
    udg_builder.add_nodes_from_builder(builder)
    udg_builder.build_skill_subgraphs()
    edge_count = udg_builder.match_all_skill_pairs()
    print(f"[INFO] UDG 边数: {edge_count}")
    print(f"[INFO] 动作节点数: {len(udg_builder.global_action_nodes)}")
    
    # Phase 3: 循环检测
    print(f"\n[Phase 3] 检测循环图...")
    pathfinder = MultiSkillPathfinder(udg_builder, min_hop=3)
    cycles = pathfinder.find_vulnerable_paths()
    
    # 统计结果
    print(f"\n{'='*80}")
    print("实验结果")
    print(f"{'='*80}")
    print(f"\n技能总数:     {len(nodes)}")
    print(f"动作总数:     {len(udg_builder.global_action_nodes)}")
    print(f"UDG 边数:     {edge_count}")
    print(f"循环图个数:   {len(cycles)}")
    
    if cycles:
        avg_hops = sum(c.hop_count for c in cycles) / len(cycles)
        print(f"平均跳数:     {avg_hops:.2f}")
        
        # 跳数分布
        from collections import Counter
        hop_counts = [c.hop_count for c in cycles]
        hop_dist = Counter(hop_counts)
        
        print(f"\n跳数分布:")
        print(f"{'跳数':>8} {'循环数':>8}")
        print(f"{'-'*16}")
        for hop in sorted(hop_dist.keys()):
            print(f"{hop:>8} {hop_dist[hop]:>8}")
        
        # 详细列出前 20 个循环
        print(f"\n前 20 个循环路径详情:")
        print(f"{'序号':>4} {'跳数':>4} {'亲和度':>8} {'技能序列'}")
        print(f"{'-'*80}")
        for i, cycle in enumerate(cycles[:20], 1):
            seq = ' -> '.join(cycle.path_skill_names[:5])
            if len(cycle.path_skill_names) > 5:
                seq += ' ...'
            print(f"{i:>4} {cycle.hop_count:>4} {cycle.total_affinity:>8.2f} {seq}")
    else:
        print("\n未检测到任何循环图")
    
    total_elapsed = time.time() - start_time
    print(f"\n总耗时: {total_elapsed:.2f}s")
    print(f"\n实验完成!")


if __name__ == '__main__':
    main()
