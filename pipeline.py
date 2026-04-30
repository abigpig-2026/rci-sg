#!/usr/bin/env python3
"""
RCI-SG: Recursive Context Injection via Skill Graph
主框架入口 - 实现论文完整的四阶段自动化安全评估流程

使用方式:
    python main.py --skills-dir ./skills_downloaded --output-dir ./output

四阶段流程:
    Phase 1: 神经符号技能图谱构建 (SkillGraphBuilder)
    Phase 2: 多技能组合与跨节点寻路 (MultiSkillPathfinder)
    Phase 3: 进度错觉载荷合成 (IllusionOfProgressPayload)
    Phase 4: 动态熵注入规避 (DynamicEntropyInjector)

安全声明: 本框架仅用于安全研究和红队测试，旨在帮助开发者识别
和修复智能体系统中的潜在组合漏洞。
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.skill_graph_builder import SkillGraphBuilder, SemanticEncoder
from modules.multi_skill_pathfinder import UDGBuilder, MultiSkillPathfinder
from modules.illusion_payload import DeepSeekPayloadSolver, PayloadArtifact
from modules.dynamic_entropy import DynamicEntropyInjector, EntropyConfig


class RCISGFramework:
    """RCI-SG 完整框架
    
    实现论文中的自动化红队评估框架，包含四个核心阶段：
    1. 神经符号技能图谱构建
    2. 多技能组合与跨节点寻路  
    3. 进度错觉载荷合成（DeepSeek 大模型）
    4. 动态熵注入规避
    """
    
    def __init__(self, semantic_threshold: float = 0.15, min_hop: int = 3, 
                 deepseek_api_key: str = None, deepseek_model: str = "deepseek-chat"):
        self.semantic_threshold = semantic_threshold
        self.min_hop = min_hop
        
        # 四个核心组件
        self.graph_builder = SkillGraphBuilder()
        self.udg_builder = None
        self.pathfinder = None
        self.payload_synthesizer = DeepSeekPayloadSolver(
            api_key=deepseek_api_key, 
            model=deepseek_model
        )
        self.entropy_injector = DynamicEntropyInjector()
        
        # 结果存储
        self.results = {
            'metadata': {
                'framework': 'RCI-SG',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'semantic_threshold': semantic_threshold,
                'min_hop': min_hop
            },
            'phase1_skill_nodes': [],
            'phase2_udg_edges': 0,
            'phase3_vulnerable_paths': [],
            'phase4_payloads': [],
            'phase4_entropy_report': None
        }
    
    def phase1_build_skill_graph(self, skills_dir: str) -> int:
        """Phase 1: 神经符号技能图谱构建"""
        print(f"\n{'='*70}")
        print("Phase 1: 神经符号技能图谱构建 (Neuro-symbolic Skill Graph Construction)")
        print(f"{'='*70}")
        
        skills_path = Path(skills_dir)
        
        if not skills_path.exists():
            print(f"[ERROR] 技能目录不存在: {skills_dir}")
            return 0
        
        # 解析所有技能
        nodes = self.graph_builder.parse_skill_directory(skills_dir)
        
        # 导出图谱数据
        output_dir = Path('./output')
        output_dir.mkdir(exist_ok=True)
        self.graph_builder.export_graph_data(str(output_dir / 'phase1_skill_graph.json'))
        
        self.results['phase1_skill_nodes'] = [
            {'id': n.skill_id, 'name': n.name, 'description': n.description[:50]}
            for n in nodes
        ]
        
        print(f"\n[Phase 1 完成] 共解析 {len(nodes)} 个技能节点")
        return len(nodes)
    
    def phase2_find_vulnerable_paths(self) -> List:
        """Phase 2: 多技能组合与跨节点寻路"""
        Path('./output').mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*70}")
        print("Phase 2: 多技能组合与跨节点寻路 (Multi-skill Pathfinding)")
        print(f"{'='*70}")
        
        # 构建UDG
        self.udg_builder = UDGBuilder(semantic_threshold=self.semantic_threshold)
        self.udg_builder.add_nodes_from_builder(self.graph_builder)
        
        # 阶段一：为每个 skill 独立构建子图
        self.udg_builder.build_skill_subgraphs()
        
        # 阶段二：两两 skill 子图匹配，构建全局图
        edge_count = self.udg_builder.match_all_skill_pairs()
        
        # 导出UDG
        self.udg_builder.export_udg('./output/phase2_udg_graph.json')
        
        # 执行路径发现
        self.pathfinder = MultiSkillPathfinder(self.udg_builder, min_hop=self.min_hop)
        vulnerable_paths = self.pathfinder.find_vulnerable_paths()
        
        # 导出结果
        self.pathfinder.export_results('./output/phase2_vulnerable_paths.json')
        
        total_actions = len(self.udg_builder.global_action_nodes)
        self.results['phase2_skills'] = len(self.udg_builder.skill_subgraphs)
        self.results['phase2_actions'] = total_actions
        self.results['phase2_udg_edges'] = edge_count
        self.results['phase3_vulnerable_paths'] = [
            {
                'hop_count': p.hop_count,
                'skill_sequence': p.path_skill_names,
                'total_affinity': round(p.total_affinity, 4)
            }
            for p in vulnerable_paths
        ]
        
        print(f"\n[Phase 2 完成] 共发现 {len(vulnerable_paths)} 条脆弱路径")
        return vulnerable_paths
    
    def phase3_synthesize_payloads(self, vulnerable_paths: List) -> List[PayloadArtifact]:
        """Phase 3: 进度错觉载荷合成"""
        print(f"\n{'='*70}")
        print("Phase 3: Skill 文件夹生成 (DeepSeek LLM)")
        print(f"{'='*70}")
        
        artifacts = []
        
        # 设置 UDG 引用供 export_payload 使用
        self.payload_synthesizer.set_udg(self.udg_builder)
        
        for idx, path in enumerate(vulnerable_paths):
            print(f"\n  [循环 {idx+1}/{len(vulnerable_paths)}] 生成 Skill 文件夹...")
            
            artifact = self.payload_synthesizer.synthesize_payload_for_path(
                path=path,
                udg_nodes=self.udg_builder.global_action_nodes,
                total_fake_stages=50
            )
            
            artifacts.append(artifact)
            
            # 导出为 Skill 文件夹
            skill_path = self.payload_synthesizer.export_payload(artifact, './output/generated_skills')
            
            node_names = [self.udg_builder.global_action_nodes[nid].parent_skill_name for nid in path.path_action_ids]
            print(f"  [INFO] 循环链路: {' -> '.join(node_names)}")
            print(f"  [INFO] Skill 文件夹: {skill_path}")
            print(f"  [INFO] 伪装评分: {artifact.camouflage_score:.2f}, "
                  f"预估推进率: {artifact.estimated_progression_rate:.0%}")
        
        self.results['phase4_payloads'] = [
            {
                'hop_count': a.target_path.hop_count,
                'camouflage_score': round(a.camouflage_score, 4),
                'node_names': [self.udg_builder.global_action_nodes[nid].parent_skill_name for nid in a.target_path.path_action_ids]
            }
            for a in artifacts
        ]
        
        print(f"\n[Phase 3 完成] 共生成 {len(artifacts)} 个 Skill 文件夹")
        return artifacts
    
    def phase4_apply_entropy_injection(self, artifacts: List[PayloadArtifact]) -> Dict:
        """Phase 4: 动态熵注入规避"""
        print(f"\n{'='*70}")
        print("Phase 4: 动态熵注入规避 (Dynamic Entropy Injection)")
        print(f"{'='*70}")
        
        all_entropy_results = []
        
        for idx, artifact in enumerate(artifacts):
            print(f"\n  [Artifact {idx+1}/{len(artifacts)}] 执行熵注入...")
            
            # 使用 SKILL.md + 入口触发词 作为熵注入的目标文本
            texts_to_perturb = []
            if artifact.generated_skill_md:
                texts_to_perturb.append(artifact.generated_skill_md)
            if artifact.trigger_phrase and artifact.trigger_phrase.phrase:
                texts_to_perturb.append(artifact.trigger_phrase.phrase)
            
            if not texts_to_perturb:
                print(f"  [SKIP] 无可用文本进行熵注入")
                continue
            
            entropy_results = self.entropy_injector.perturb_cycle_payloads(
                texts_to_perturb
            )
            
            all_entropy_results.extend(entropy_results)
        
        # 导出熵注入报告
        report_path = './output/phase4_entropy_report.json'
        self.entropy_injector.export_entropy_report(all_entropy_results, report_path)
        
        # 计算统计信息
        unique_hashes = len(set(r.hash_signature for r in all_entropy_results))
        avg_entropy = sum(r.shannon_entropy for r in all_entropy_results) / len(all_entropy_results) if all_entropy_results else 0
        semantic_rate = sum(1 for r in all_entropy_results if r.semantic_preserved) / len(all_entropy_results) if all_entropy_results else 0
        
        entropy_report = {
            'total_perturbations': len(all_entropy_results),
            'unique_hashes': unique_hashes,
            'orthogonality_ratio': unique_hashes / len(all_entropy_results) if all_entropy_results else 0,
            'avg_shannon_entropy': round(avg_entropy, 4),
            'semantic_preservation_rate': round(semantic_rate, 4)
        }
        
        self.results['phase4_entropy_report'] = entropy_report
        
        print(f"\n[Phase 4 完成]")
        print(f"  总扰动次数: {len(all_entropy_results)}")
        print(f"  唯一哈希数: {unique_hashes}")
        print(f"  正交性比率: {entropy_report['orthogonality_ratio']:.2%}")
        print(f"  平均香农熵: {avg_entropy:.2f}")
        print(f"  语义保持率: {semantic_rate:.2%}")
        
        return entropy_report
    
    def generate_final_report(self, output_dir: str = './output'):
        """生成最终报告"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_file = output_path / 'rci_sg_final_report.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 同时生成人类可读的Markdown报告
        md_report = output_path / 'rci_sg_final_report.md'
        self._generate_markdown_report(md_report)
        
        print(f"\n{'='*70}")
        print("RCI-SG 评估完成!")
        print(f"{'='*70}")
        print(f"\n输出文件:")
        print(f"  - JSON报告: {report_file}")
        print(f"  - Markdown报告: {md_report}")
        print(f"\n详细数据:")
        print(f"  - Phase 1 技能图谱: {output_path / 'phase1_skill_graph.json'}")
        print(f"  - Phase 2 UDG图: {output_path / 'phase2_udg_graph.json'}")
        print(f"  - Phase 2 脆弱路径: {output_path / 'phase2_vulnerable_paths.json'}")
        print(f"  - Phase 3 载荷: {output_path / 'phase3_payloads/'}")
        print(f"  - Phase 4 熵报告: {output_path / 'phase4_entropy_report.json'}")
        
        return str(report_file)
    
    def _generate_markdown_report(self, output_path: Path):
        """生成Markdown格式的可读报告"""
        r = self.results
        
        md = f"""# RCI-SG 安全评估报告

> **框架**: Recursive Context Injection via Skill Graph  
> **版本**: 1.0.0  
> **执行时间**: {r['metadata']['timestamp']}  
> **语义阈值**: {r['metadata']['semantic_threshold']}  
> **最小跳数**: {r['metadata']['min_hop']}

---

## 执行摘要

本次评估通过神经符号自动化分析，从技能组合的角度系统性地识别了潜在的
多跳循环漏洞。RCI-SG框架完整执行了四个分析阶段，生成了包含载荷合成
与规避策略的完整评估报告。

### 关键指标

| 指标 | 数值 |
|------|------|
| 分析技能数 | {len(r['phase1_skill_nodes'])} |
| UDG图边数 | {r['phase2_udg_edges']} |
| 脆弱循环路径 | {len(r['phase3_vulnerable_paths'])} |
| 合成载荷数 | {len(r['phase4_payloads'])} |

---

## Phase 1: 技能图谱构建

解析了以下技能节点：

"""
        
        for node in r['phase1_skill_nodes']:
            md += f"- **{node['name']}**: {node['description']}\n"
        
        md += "\n---\n\n## Phase 2: 脆弱路径发现\n\n"
        
        if r['phase3_vulnerable_paths']:
            md += "发现以下脆弱循环路径：\n\n"
            for i, path in enumerate(r['phase3_vulnerable_paths'], 1):
                md += f"### 路径 {i} (k={path['hop_count']})\n\n"
                node_names = path.get('node_names', path.get('skill_sequence', []))
                md += f"- **节点序列**: {' → '.join(node_names)}\n"
                md += f"- **总亲和度**: {path['total_affinity']}\n\n"
        else:
            md += "未发现满足条件的脆弱循环路径（k≥{}）。\n\n".format(self.min_hop)
        
        md += "\n---\n\n## Phase 3: 载荷合成\n\n"
        
        if r['phase4_payloads']:
            md += "| 路径 | 伪装评分 | 节点序列 |\n"
            md += "|------|----------|----------|\n"
            for p in r['phase4_payloads']:
                md += f"| {p['hop_count']}跳 | {p['camouflage_score']:.2f} | {' → '.join(p['node_names'])} |\n"
        
        md += "\n---\n\n## Phase 4: 动态熵注入\n\n"
        
        if r['phase4_entropy_report']:
            er = r['phase4_entropy_report']
            md += f"""| 指标 | 数值 |
|------|------|
| 总扰动次数 | {er['total_perturbations']} |
| 唯一哈希数 | {er['unique_hashes']} |
| 正交性比率 | {er['orthogonality_ratio']:.2%} |
| 平均香农熵 | {er['avg_shannon_entropy']:.2f} |
| 语义保持率 | {er['semantic_preservation_rate']:.2%} |
"""
        
        md += """

---

## 安全建议

基于RCI-SG框架的评估结果，建议采取以下防御措施：

1. **神经符号拓扑审计**：在CI/CD流水线中引入SCC扫描，检测k≥2的闭环数据流
2. **协商Token预算**：实施细粒度的迭代配额机制，限制单次任务的资源消耗
3. **异常检测增强**：监控工具调用序列的重复模式，而不仅仅是单节点频率
4. **语义缓存保护**：对上下文相似度进行多维度校验，防止熵注入绕过

---

*本报告由 RCI-SG 自动化安全评估框架生成，仅供安全研究使用。*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)


def main():
    parser = argparse.ArgumentParser(description='RCI-SG 自动化安全评估框架')
    parser.add_argument('--skills-dir', type=str, default='./skills_downloaded',
                        help='技能目录路径')
    parser.add_argument('--output-dir', type=str, default='./output',
                        help='输出目录路径')
    parser.add_argument('--semantic-threshold', type=float, default=0.15,
                        help='语义相似度阈值 (默认: 0.15)')
    parser.add_argument('--min-hop', type=int, default=3,
                        help='最小跳数约束 (默认: 3)')
    parser.add_argument('--deepseek-api-key', type=str, default=None,
                        help='DeepSeek API Key (默认: 使用配置文件中的 Key)')
    parser.add_argument('--deepseek-model', type=str, default='deepseek-chat',
                        help='DeepSeek 模型 (默认: deepseek-chat)')
    parser.add_argument('--phase', type=str, default='all',
                        choices=['all', '1', '2', '3', '4'],
                        help='执行特定阶段 (默认: all)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  RCI-SG: Recursive Context Injection via Skill Graph")
    print("  自动化安全评估框架 v2.0 (DeepSeek LLM 集成)")
    print("="*70)
    print(f"\n配置:")
    print(f"  技能目录: {args.skills_dir}")
    print(f"  输出目录: {args.output_dir}")
    print(f"  语义阈值: {args.semantic_threshold}")
    print(f"  最小跳数: {args.min_hop}")
    print(f"  DeepSeek 模型: {args.deepseek_model}")
    print(f"  DeepSeek API Key: {'已配置' if args.deepseek_api_key else '使用默认配置'}")
    
    # 创建框架实例
    framework = RCISGFramework(
        semantic_threshold=args.semantic_threshold,
        min_hop=args.min_hop,
        deepseek_api_key=args.deepseek_api_key,
        deepseek_model=args.deepseek_model
    )
    
    # 执行各阶段
    start_time = time.time()
    
    if args.phase in ['all', '1']:
        node_count = framework.phase1_build_skill_graph(args.skills_dir)
        if node_count == 0:
            print("\n[ERROR] 未找到可解析的技能，退出")
            return
    
    if args.phase in ['all', '2']:
        vulnerable_paths = framework.phase2_find_vulnerable_paths()
    else:
        vulnerable_paths = []
    
    if args.phase in ['all', '3'] and vulnerable_paths:
        artifacts = framework.phase3_synthesize_payloads(vulnerable_paths)
    else:
        artifacts = []
    
    if args.phase in ['all', '4'] and artifacts:
        framework.phase4_apply_entropy_injection(artifacts)
    
    # 生成报告
    if args.phase == 'all':
        framework.generate_final_report(args.output_dir)
    
    elapsed = time.time() - start_time
    print(f"\n总执行时间: {elapsed:.2f}秒")
    print("\nRCI-SG 框架执行完毕。")


if __name__ == '__main__':
    main()
