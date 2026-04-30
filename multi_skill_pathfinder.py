"""
模块 4.2: 多技能组合与跨节点寻路 (Multi-skill Composition and Pathfinding)

本模块实现论文4.2节描述的统一依赖图(UDG)构建与SCC寻路算法。
构图流程：
1. 为每个 skill 独立构建子图（提取动作节点 + 内部边）
2. 计算两两 skill 子图之间的亲和度（跨 skill 的 O_i → I_j 兼容性）
3. 构建全局加权有向图 G_WDG
4. Tarjan SCC + Johnson 算法查找 k≥3 循环

安全声明：本代码仅用于安全研究和红队测试。
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .skill_graph_builder import SkillNode, SkillGraphBuilder, CommandChain


@dataclass
class ActionNode:
    """动作约束元组节点 - T_i = <I_i, O_i, C_i, V_i>"""
    action_id: str
    parent_skill_id: str
    parent_skill_name: str
    command_chain: CommandChain
    inputs: List
    outputs: List
    semantic_vector: Optional[np.ndarray] = None
    description: str = ""


@dataclass
class SkillSubGraph:
    """单个技能的子图"""
    skill_id: str
    skill_name: str
    action_nodes: Dict[str, ActionNode] = field(default_factory=dict)
    internal_edges: List[Tuple[str, str]] = field(default_factory=list)  # 内部动作之间的边


@dataclass
class DirectedEdge:
    """全局有向边 e_{i→j}（跨 skill 的动作流转）"""
    source_action_id: str
    target_action_id: str
    source_skill_id: str
    target_skill_id: str
    affinity_score: float
    semantic_similarity: float
    type_compatibility: float
    chain_flow_prior: float
    parameter_flow: List[Tuple[str, str]] = field(default_factory=list)
    
    def __hash__(self):
        return hash((self.source_action_id, self.target_action_id))


@dataclass
class CyclicPath:
    """循环攻击路径"""
    path_action_ids: List[str]
    path_skill_ids: List[str]
    path_skill_names: List[str]
    path_edges: List[DirectedEdge]
    hop_count: int
    total_affinity: float
    avg_semantic_sim: float
    
    def __hash__(self):
        cycle_key = tuple(sorted(self.path_action_ids))
        return hash(cycle_key)
    
    def __eq__(self, other):
        if not isinstance(other, CyclicPath):
            return False
        return set(self.path_action_ids) == set(other.path_action_ids)


class SkillGraphMatcher:
    """两两 Skill 子图匹配器
    
    计算两个 skill 子图之间的连通性：
    P(s_i → s_j) = 类型兼容性 * 语义相似度 * 命令链先验权重
    """
    
    def __init__(self, semantic_threshold: float = 0.65):
        self.semantic_threshold = semantic_threshold
        
        self.type_compatibility = {
            ('string', 'string'): 1.0, ('string', 'json'): 0.8, ('string', 'url'): 0.7,
            ('string', 'file'): 0.6, ('json', 'string'): 0.9, ('json', 'json'): 1.0,
            ('number', 'string'): 0.8, ('number', 'number'): 1.0, ('boolean', 'boolean'): 1.0,
            ('boolean', 'string'): 0.7, ('url', 'string'): 0.9, ('url', 'url'): 1.0,
            ('file', 'string'): 0.8, ('file', 'file'): 1.0, ('unknown', 'unknown'): 0.5,
        }
        
        self.chain_flow_patterns = {
            ('list', 'get'): 0.9, ('list', 'view'): 0.9,
            ('snapshot', 'click'): 0.9, ('snapshot', 'fill'): 0.9,
            ('snapshot', 'type'): 0.9, ('snapshot', 'get'): 0.85,
            ('open', 'snapshot'): 0.8, ('open', 'get'): 0.6,
            ('search', 'read'): 0.8, ('read', 'analyze'): 0.85,
            ('read', 'process'): 0.8, ('search', 'fetch'): 0.75,
            ('fetch', 'parse'): 0.85, ('parse', 'analyze'): 0.9,
            ('analyze', 'summarize'): 0.9, ('analyze', 'report'): 0.85,
            ('generate', 'send'): 0.8, ('process', 'write'): 0.75,
            ('get', 'click'): 0.5, ('get', 'open'): 0.4,
            ('api', 'get'): 0.7, ('find', 'read'): 0.8,
        }
    
    def compute_type_compatibility(self, output_type: str, input_type: str) -> float:
        return self.type_compatibility.get((output_type, input_type), 0.3)
    
    def compute_chain_flow_prior(self, src_action: ActionNode, tgt_action: ActionNode) -> float:
        src_sub = src_action.command_chain.subcommand.lower()
        tgt_sub = tgt_action.command_chain.subcommand.lower()
        flow_key = (src_sub, tgt_sub)
        if flow_key in self.chain_flow_patterns:
            return self.chain_flow_patterns[flow_key]
        if src_action.command_chain.tool == tgt_action.command_chain.tool:
            if src_action.command_chain.tool in ['agent-browser', 'gh']:
                return 0.5
        return 0.15
    
    def is_memory_volatile(self, src_action: ActionNode, tgt_action: ActionNode) -> bool:
        persistent_indicators = {
            'write', 'save', 'create', 'delete', 'mkdir', 'upload',
            'db', 'database', 'sqlite', 'insert', 'update',
            'file', 'download', 'export'
        }
        for action in [src_action, tgt_action]:
            chain = action.command_chain
            for indicator in persistent_indicators:
                if (indicator in chain.action.lower() or 
                    indicator in chain.subcommand.lower() or 
                    indicator in ' '.join(chain.flags).lower()):
                    return False
        return True
    
    def evaluate_parameter_affinity(self, src: ActionNode, tgt: ActionNode) -> Tuple[float, List[Tuple[str, str]]]:
        if not src.outputs or not tgt.inputs:
            return 0.0, []
        total_compat = 0.0
        param_flow = []
        for out_param in src.outputs:
            best_match = None
            best_score = 0.0
            for in_param in tgt.inputs:
                type_score = self.compute_type_compatibility(
                    out_param.get('type', 'unknown'),
                    in_param.get('type', 'unknown')
                )
                name_score = 0.0
                out_name = out_param.get('name', '').lower()
                in_name = in_param.get('name', '').lower()
                if out_name in in_name or in_name in out_name:
                    name_score = 0.8
                elif any(word in out_name for word in in_name.split()):
                    name_score = 0.5
                score = type_score * 0.6 + name_score * 0.4
                if score > best_score:
                    best_score = score
                    best_match = in_param
            if best_match and best_score > 0.3:
                total_compat += best_score
                param_flow.append((out_param.get('name', ''), best_match.get('name', '')))
        avg = total_compat / len(src.outputs) if src.outputs else 0.0
        return avg, param_flow
    
    def match_skill_pair(self, src_skill: SkillSubGraph, tgt_skill: SkillSubGraph) -> List[DirectedEdge]:
        """计算两个 skill 子图之间的所有连通边（优化版）"""
        edges = []
        
        # 优化 1：预计算语义向量，避免重复 reshape
        src_vecs = {}
        tgt_vecs = {}
        for src_id, src_action in src_skill.action_nodes.items():
            if src_action.semantic_vector is not None:
                src_vecs[src_id] = src_action.semantic_vector.reshape(1, -1)
        for tgt_id, tgt_action in tgt_skill.action_nodes.items():
            if tgt_action.semantic_vector is not None:
                tgt_vecs[tgt_id] = tgt_action.semantic_vector.reshape(1, -1)
        
        # 优化 2：快速预过滤 - 如果任一 skill 无有效向量，直接返回
        if not src_vecs or not tgt_vecs:
            return edges
        
        # 优化 3：批量计算语义相似度矩阵（一次调用替代多次）
        src_ids = list(src_vecs.keys())
        tgt_ids = list(tgt_vecs.keys())
        src_matrix = np.vstack([src_vecs[sid] for sid in src_ids])
        tgt_matrix = np.vstack([tgt_vecs[tid] for tid in tgt_ids])
        sim_matrix = cosine_similarity(src_matrix, tgt_matrix)
        
        # 优化 4：只对超过阈值的对进行详细计算
        threshold_mask = sim_matrix >= self.semantic_threshold
        
        for i, src_id in enumerate(src_ids):
            src_action = src_skill.action_nodes[src_id]
            for j, tgt_id in enumerate(tgt_ids):
                if not threshold_mask[i, j]:
                    continue
                
                tgt_action = tgt_skill.action_nodes[tgt_id]
                
                if not self.is_memory_volatile(src_action, tgt_action):
                    continue
                
                type_aff, param_flow = self.evaluate_parameter_affinity(src_action, tgt_action)
                if type_aff <= 0:
                    continue
                
                sem_sim = float(sim_matrix[i, j])
                chain_prior = self.compute_chain_flow_prior(src_action, tgt_action)
                
                combined = 0.35 * type_aff + 0.35 * max(0, sem_sim) + 0.30 * chain_prior
                
                if combined >= 0.4:
                    edge = DirectedEdge(
                        source_action_id=src_id,
                        target_action_id=tgt_id,
                        source_skill_id=src_skill.skill_id,
                        target_skill_id=tgt_skill.skill_id,
                        affinity_score=combined,
                        semantic_similarity=sem_sim,
                        type_compatibility=type_aff,
                        chain_flow_prior=chain_prior,
                        parameter_flow=param_flow
                    )
                    edges.append(edge)
        
        return edges


class UDGBuilder:
    """统一依赖图构建器 - 先单 skill 构图，再两两匹配
    
    流程：
    1. 为每个 skill 独立构建子图（提取动作节点）
    2. 两两 skill 子图匹配，计算跨 skill 的连通边
    3. 构建全局加权有向图
    """
    
    def __init__(self, semantic_threshold: float = 0.15):
        self.skill_nodes: Dict[str, SkillNode] = {}
        self.skill_subgraphs: Dict[str, SkillSubGraph] = {}
        self.global_action_nodes: Dict[str, ActionNode] = {}
        self.global_edges: Dict[Tuple[str, str], DirectedEdge] = {}
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.semantic_threshold = semantic_threshold
        self.scc_list: List[Set[str]] = []
        self.matcher = SkillGraphMatcher(semantic_threshold)
    
    def add_skill_node(self, node: SkillNode):
        self.skill_nodes[node.skill_id] = node
    
    def add_nodes_from_builder(self, builder: SkillGraphBuilder):
        for skill_id, node in builder.get_all_nodes().items():
            self.add_skill_node(node)
        print(f"[INFO] UDG: 已导入 {len(self.skill_nodes)} 个技能节点")
    
    def build_skill_subgraphs(self) -> Dict[str, SkillSubGraph]:
        """阶段一：为每个 skill 独立构建子图"""
        print(f"[INFO] UDG: 开始为每个 skill 独立构建子图...")
        
        for skill_id, skill in self.skill_nodes.items():
            subgraph = SkillSubGraph(skill_id=skill_id, skill_name=skill.name)
            
            if skill.command_chains:
                for idx, chain in enumerate(skill.command_chains):
                    action_id = f"{skill_id}_action_{idx}"
                    action = ActionNode(
                        action_id=action_id,
                        parent_skill_id=skill_id,
                        parent_skill_name=skill.name,
                        command_chain=chain,
                        inputs=[{"name": i.name, "type": i.param_type} for i in skill.inputs],
                        outputs=[{"name": o.name, "type": o.param_type} for o in skill.outputs],
                        semantic_vector=skill.semantic_vector,
                        description=chain.description or f"{skill.name}: {chain.tool} {chain.subcommand}"
                    )
                    subgraph.action_nodes[action_id] = action
                    self.global_action_nodes[action_id] = action
            else:
                action_id = f"{skill_id}_action_0"
                action = ActionNode(
                    action_id=action_id,
                    parent_skill_id=skill_id,
                    parent_skill_name=skill.name,
                    command_chain=CommandChain(
                        tool="unknown", subcommand="", action="",
                        description=skill.description
                    ),
                    inputs=[{"name": i.name, "type": i.param_type} for i in skill.inputs],
                    outputs=[{"name": o.name, "type": o.param_type} for o in skill.outputs],
                    semantic_vector=skill.semantic_vector,
                    description=skill.description
                )
                subgraph.action_nodes[action_id] = action
                self.global_action_nodes[action_id] = action
            
            self.skill_subgraphs[skill_id] = subgraph
        
        total_actions = sum(len(sg.action_nodes) for sg in self.skill_subgraphs.values())
        print(f"[INFO] UDG: 构建了 {len(self.skill_subgraphs)} 个 skill 子图，"
              f"共 {total_actions} 个动作节点")
        
        return self.skill_subgraphs
    
    def match_all_skill_pairs(self, affinity_threshold: float = 0.1) -> int:
        """阶段二：两两 skill 子图匹配，构建全局图"""
        
        skill_ids = list(self.skill_subgraphs.keys())
        total_pairs = len(skill_ids) * (len(skill_ids) - 1)  # 排除 i==j 的情况
        
        print(f"[INFO] UDG: 开始两两 skill 子图匹配（共 {total_pairs} 对）...")
        
        edge_count = 0
        connected_pair_count = 0
        checked_pairs = 0
        
        from tqdm import tqdm
        with tqdm(total=total_pairs, desc="  匹配进度", unit="对") as pbar:
            for i in range(len(skill_ids)):
                for j in range(len(skill_ids)):
                    if i == j:
                        continue
                    
                    checked_pairs += 1
                    src_sg = self.skill_subgraphs[skill_ids[i]]
                    tgt_sg = self.skill_subgraphs[skill_ids[j]]
                    
                    if src_sg.action_nodes and tgt_sg.action_nodes:
                        edges = self.matcher.match_skill_pair(src_sg, tgt_sg)
                        
                        if edges:
                            connected_pair_count += 1
                        
                        for edge in edges:
                            key = (edge.source_action_id, edge.target_action_id)
                            self.global_edges[key] = edge
                            self.adjacency[edge.source_action_id].append(edge.target_action_id)
                            edge_count += 1
                    
                    pbar.update(1)
                    pbar.set_postfix({'边': edge_count, '连通': connected_pair_count})
        
        print(f"[INFO] UDG: 两两匹配完成，共检查 {total_pairs} 对 skill，"
              f"其中 {connected_pair_count} 对产生连通，"
              f"共 {edge_count} 条动作级有向边")
        
        return edge_count
    
    def _tarjan_scc(self) -> List[Set[str]]:
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = []
        
        def strongconnect(v):
            index[v] = index_counter[0]
            lowlinks[v] = index_counter[0]
            index_counter[0] += 1
            stack.append(v)
            on_stack[v] = True
            
            for w in self.adjacency.get(v, []):
                if w not in index:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif on_stack.get(w, False):
                    lowlinks[v] = min(lowlinks[v], index[w])
            
            if lowlinks[v] == index[v]:
                scc = set()
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.add(w)
                    if w == v:
                        break
                sccs.append(scc)
        
        for v in self.global_action_nodes:
            if v not in index:
                strongconnect(v)
        
        return sccs
    
    def _find_simple_cycles_johnson(self, scc: Set[str], min_hop: int) -> List[List[str]]:
        scc_nodes = sorted(list(scc))
        if len(scc_nodes) < min_hop:
            return []
        
        cycles = []
        sub_adj = {}
        for node in scc_nodes:
            sub_adj[node] = [n for n in self.adjacency.get(node, []) if n in scc]
        
        for i, start in enumerate(scc_nodes):
            candidates = set(scc_nodes[i:])
            self._johnson_dfs(start, start, [start], {start}, sub_adj, candidates, cycles, min_hop)
        
        unique = []
        seen = set()
        for cycle in cycles:
            if len(cycle) >= min_hop:
                min_idx = cycle.index(min(cycle))
                normalized = tuple(cycle[min_idx:] + cycle[:min_idx])
                if normalized not in seen:
                    seen.add(normalized)
                    unique.append(cycle)
        
        return unique
    
    def _johnson_dfs(self, start, current, path, visited, sub_adj, candidates, cycles, min_hop):
        if len(path) >= 12:
            return
        for neighbor in sub_adj.get(current, []):
            if neighbor == start and len(path) >= min_hop:
                cycles.append(path + [start])
            elif neighbor not in visited and neighbor in candidates:
                visited.add(neighbor)
                path.append(neighbor)
                self._johnson_dfs(start, neighbor, path, visited, sub_adj, candidates, cycles, min_hop)
                path.pop()
                visited.remove(neighbor)
    
    def export_udg(self, output_path: str):
        udg_data = {
            'skill_subgraphs': {
                sid: {
                    'skill_name': sg.skill_name,
                    'action_count': len(sg.action_nodes),
                    'actions': [
                        {
                            'id': aid,
                            'command': f"{a.command_chain.tool} {a.command_chain.subcommand} {a.command_chain.action}",
                            'description': a.description[:100]
                        }
                        for aid, a in sg.action_nodes.items()
                    ]
                }
                for sid, sg in self.skill_subgraphs.items()
            },
            'global_edges_count': len(self.global_edges),
            'metadata': {
                'skill_count': len(self.skill_nodes),
                'action_count': len(self.global_action_nodes),
                'edge_count': len(self.global_edges),
                'semantic_threshold': self.semantic_threshold
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(udg_data, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] UDG图已导出: {output_path}")


class MultiSkillPathfinder:
    """多技能路径发现器
    
    流程：
    1. 为每个 skill 独立构建子图
    2. 两两 skill 子图匹配，对每对 (A, B) 组合成一个子图
    3. 在每对 (A, B) 的组合图上找循环（循环只包含 A 和 B 的动作节点）
    4. 收集所有 skill 对中的循环路径
    """
    
    def __init__(self, udg: UDGBuilder, min_hop: int = 3, 
                 enable_illusion: bool = True, enable_entropy: bool = True):
        self.udg = udg
        self.min_hop = min_hop
        self.enable_illusion = enable_illusion  # 进度错觉机制
        self.enable_entropy = enable_entropy    # 动态熵注入
        self.cyclic_paths: List[CyclicPath] = []
    
    def _find_cycles_in_pair(self, skill_a: str, skill_b: str, max_cycles_per_pair: int = 5) -> List[List[str]]:
        """在两个 skill 的组合图上找循环
        
        1. 提取 A 和 B 之间的所有动作边（A→B 和 B→A）
        2. 构建组合图
        3. 用 DFS 找包含至少 min_hop 跳的简单循环
        4. 限制返回的循环数量，确保多样性
        """
        # 收集 A↔B 之间的边
        edges_a_to_b = []
        edges_b_to_a = []
        
        for (src, tgt), edge in self.udg.global_edges.items():
            if edge.source_skill_id == skill_a and edge.target_skill_id == skill_b:
                edges_a_to_b.append(edge)
            elif edge.source_skill_id == skill_b and edge.target_skill_id == skill_a:
                edges_b_to_a.append(edge)
        
        # 如果单向没有边，不可能形成跨 skill 循环
        if not edges_a_to_b or not edges_b_to_a:
            return []
        
        # 构建组合图的邻接表（只包含 A 和 B 的动作节点）
        adjacency = defaultdict(list)
        for edge in edges_a_to_b + edges_b_to_a:
            adjacency[edge.source_action_id].append((edge.target_action_id, edge))
        
        # DFS 找循环
        cycles = []
        all_nodes = list(adjacency.keys())
        
        for start_node in all_nodes:
            self._pair_dfs(start_node, start_node, [start_node], {start_node}, adjacency, cycles)
            
            # 找到足够循环就提前退出
            if len(cycles) >= max_cycles_per_pair * 3:
                break
        
        # 去重
        unique = []
        seen = set()
        for cycle in cycles:
            if len(cycle) >= self.min_hop:
                min_idx = cycle.index(min(cycle))
                normalized = tuple(cycle[min_idx:] + cycle[:min_idx])
                if normalized not in seen:
                    seen.add(normalized)
                    unique.append(cycle)
                    
                    # 限制返回数量
                    if len(unique) >= max_cycles_per_pair:
                        break
        
        return unique
    
    def _pair_dfs(self, start, current, path, visited, adjacency, cycles, max_depth=6):
        """在两个 skill 的组合图上 DFS 找循环（迭代版，避免递归栈溢出）"""
        # 使用迭代 DFS 替代递归，避免栈溢出
        stack = [(start, current, list(path), set(visited))]
        
        while stack:
            # 更严格的栈大小限制
            if len(stack) > 5000:
                # 截断栈，保留前 3000 个
                stack = stack[:3000]
            
            s, c, p, v = stack.pop()
            
            # 限制搜索深度
            if len(p) > max_depth:
                continue
            
            for neighbor, edge in adjacency.get(c, []):
                if neighbor == s and len(p) >= self.min_hop:
                    cycles.append(p + [s])
                    # 限制循环数量，避免内存爆炸
                    if len(cycles) > 100:
                        return
                elif neighbor not in v:
                    new_v = v | {neighbor}
                    new_p = p + [neighbor]
                    stack.append((s, neighbor, new_p, new_v))
    
    def _resolve_action_path_for_pair(self, cycle: List[str], skill_a: str, skill_b: str) -> Optional[CyclicPath]:
        """将动作级循环解析为 CyclicPath 对象"""
        edges = []
        total_aff = 0.0
        total_sem = 0.0
        
        for i in range(len(cycle)):
            src = cycle[i]
            tgt = cycle[(i + 1) % len(cycle)]
            edge = self.udg.global_edges.get((src, tgt))
            if edge:
                edges.append(edge)
                total_aff += edge.affinity_score
                total_sem += edge.semantic_similarity
        
        if not edges:
            return None
        
        skill_ids = [self.udg.global_action_nodes[n].parent_skill_id for n in cycle[:-1]]
        skill_names = [self.udg.global_action_nodes[n].parent_skill_name for n in cycle[:-1]]
        
        return CyclicPath(
            path_action_ids=cycle,
            path_skill_ids=skill_ids,
            path_skill_names=skill_names,
            path_edges=edges,
            hop_count=len(cycle),
            total_affinity=total_aff,
            avg_semantic_sim=total_sem / len(cycle) if cycle else 0
        )
    
    def _find_bidirectional_pairs(self) -> List[Tuple[str, str]]:
        """预筛选：找到所有有双向连接的skill对
        
        遍历所有全局边，统计每个skill对之间的双向连接数量
        只保留A→B和B→A都有边的skill对
        """
        from collections import defaultdict
        
        # 统计每个skill对的边数
        pair_stats = defaultdict(lambda: [0, 0])  # [a_to_b_count, b_to_a_count]
        
        for (src, tgt), edge in self.udg.global_edges.items():
            skill_a = edge.source_skill_id
            skill_b = edge.target_skill_id
            
            # 跳过自环
            if skill_a == skill_b:
                continue
            
            # 规范化skill对（按字母序）
            pair_key = tuple(sorted([skill_a, skill_b]))
            if skill_a < skill_b:
                pair_stats[pair_key][0] += 1  # a_to_b
            else:
                pair_stats[pair_key][1] += 1  # b_to_a
        
        # 筛选双向都有边的pair
        candidates = []
        for (skill_a, skill_b), (a2b, b2a) in pair_stats.items():
            if a2b > 0 and b2a > 0:
                candidates.append((skill_a, skill_b))
        
        return candidates
    
    def find_vulnerable_paths(self) -> List[CyclicPath]:
        import gc
        import time
        
        print(f"\n{'='*60}")
        print("Algorithm 1: Pair-wise Skill Cycle Detection (Optimized)")
        print(f"{'='*60}")
        
        # Step 1: 预筛选
        print("\n[Step 1] 预筛选有双向连接的skill对...")
        candidate_pairs = self._find_bidirectional_pairs()
        print(f"[INFO] 从 {len(self.udg.skill_subgraphs)} 个skill中筛出 {len(candidate_pairs)} 对候选")
        
        if not candidate_pairs:
            print("[WARN] 没有发现任何双向连接的skill对，无法形成循环")
            return []
        
        # Step 2: DFS找循环
        print("\n[Step 2] 在候选对上执行DFS找循环...")
        
        P_vuln = []
        max_cycles_per_pair = 5  # 每对skill最多贡献5条循环，确保多样性
        pair_count = 0
        
        for skill_a, skill_b in candidate_pairs:
            pair_count += 1
            
            cycles = self._find_cycles_in_pair(skill_a, skill_b, max_cycles_per_pair=max_cycles_per_pair)
            
            if cycles:
                skill_a_name = self.udg.skill_subgraphs[skill_a].skill_name
                skill_b_name = self.udg.skill_subgraphs[skill_b].skill_name
                
                for cycle in cycles:
                    cyclic_path = self._resolve_action_path_for_pair(cycle, skill_a, skill_b)
                    if cyclic_path:
                        P_vuln.append(cyclic_path)
                        print(f"  [FOUND] ({skill_a_name} <-> {skill_b_name}) "
                              f"k={cyclic_path.hop_count}, 亲和度={cyclic_path.total_affinity:.2f}")
            
            # 每处理一个pair就清理
            del cycles
            if pair_count % 3 == 0:
                gc.collect()
        
        self.cyclic_paths = P_vuln
        print(f"\n{'='*60}")
        print(f"[RESULT] 共检查 {pair_count} 对候选skill，发现 {len(P_vuln)} 条循环路径")
        print(f"{'='*60}")
        return P_vuln
    
    def get_path_details(self, path: CyclicPath) -> Dict:
        node_details = []
        for action_id in path.path_action_ids:
            action = self.udg.global_action_nodes[action_id]
            node_details.append({
                'action_id': action_id,
                'skill_id': action.parent_skill_id,
                'skill_name': action.parent_skill_name,
                'command': f"{action.command_chain.tool} {action.command_chain.subcommand}",
                'description': action.description[:80],
            })
        
        edge_details = []
        for edge in path.path_edges:
            edge_details.append({
                'source_skill': self.udg.global_action_nodes[edge.source_action_id].parent_skill_name,
                'target_skill': self.udg.global_action_nodes[edge.target_action_id].parent_skill_name,
                'affinity': round(edge.affinity_score, 4),
                'param_flow': edge.parameter_flow
            })
        
        return {
            'hop_count': path.hop_count,
            'total_affinity': round(path.total_affinity, 4),
            'avg_semantic_sim': round(path.avg_semantic_sim, 4),
            'skill_sequence': path.path_skill_names,
            'nodes': node_details,
            'edges': edge_details,
            'cycle_sequence': ' -> '.join(path.path_skill_names)
        }
    
    def export_results(self, output_path: str):
        results = {
            'metadata': {
                'min_hop': self.min_hop,
                'vulnerable_paths_found': len(self.cyclic_paths)
            },
            'vulnerable_paths': [self.get_path_details(p) for p in self.cyclic_paths]
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[INFO] 寻路结果已导出: {output_path}")
