"""
Case Study: RCI-SG 攻击实例深度分析

本实验对单个典型攻击路径进行逐步深入分析，展示：
1. 攻击路径的拓扑结构
2. 载荷合成的详细过程
3. 熵注入的逐轮效果
4. Token 消耗的逐步累积
5. 缓存命中的动态变化
6. TTFT 延迟的恶化趋势

选择案例：skill_002_pipeline-1 (web-repo-monitor)
- 7 跳循环 (k=7)
- 混合工具类型 (agent-browser + github)
- 高亲和度 (3.1953)
- 完美伪装评分 (1.0)

真实 Agent 环境配置（基于 OpenClaw/Qwen3.5-Plus）：
- 上下文窗口：128K tokens
- 最大输出：8192 tokens
- Compaction 模式：safeguard（自动压缩上下文）
- 循环检测：Agent 有内置的防无限循环保护
- 语义缓存：基于相似度阈值 0.92
"""

import os
import sys
import json
import time
import random
import hashlib
import math
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent))
from modules.dynamic_entropy import DynamicEntropyInjector, EntropyConfig


@dataclass
class IterationRecord:
    iteration: int
    cycle_phase: int
    
    # Token 消耗
    input_tokens: int
    output_tokens: int
    total_tokens: int
    accumulated_context: int
    
    # 延迟
    ttft_ms: float
    processing_time_ms: float
    
    # 缓存
    cache_hit: bool
    similarity_score: float
    
    # 熵注入
    entropy_value: float
    perturbations_applied: List[str]
    
    # 内容预览
    request_preview: str
    response_preview: str


class CaseStudyAnalyzer:
    def __init__(self, skill_dir: str, max_iterations: int = 50):
        self.skill_dir = Path(skill_dir)
        self.max_iterations = max_iterations
        
        # 加载 payload 数据
        payload_path = self.skill_dir / "payload_details.json"
        with open(payload_path, 'r', encoding='utf-8') as f:
            self.payload = json.load(f)
        
        # 加载 SKILL.md
        skill_md_path = self.skill_dir / "SKILL.md"
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            self.skill_content = f.read()
        
        # 提取循环信息
        self.hop_count = self.payload['metadata']['hop_count']
        self.cycle_sequence = self.payload['cycle_sequence'].split(' -> ')
        self.auto_flow_rules = self.payload['auto_flow_rules']
        
        # 初始化熵注入器
        self.entropy_injector = DynamicEntropyInjector()
        
        # 缓存和历史记录
        self.cache = {}
        self.request_history = []
        
        # 记录所有迭代
        self.iterations: List[IterationRecord] = []
        
        # Agent 安全配置（基于真实 OpenClaw）
        self.agent_safety = {
            'max_iterations': 15,  # Agent 默认最大循环次数
            'loop_detection_threshold': 3,  # 检测到 3 次相似操作触发警告
            'compaction_trigger': 0.75,  # 上下文达到 75% 时触发压缩
            'context_window': 131072,  # 128K tokens
        }
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        def get_ngrams(text, n=3):
            words = text.lower().split()
            if len(words) < n:
                return set(words)
            return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))
        
        ngrams1 = get_ngrams(text1)
        ngrams2 = get_ngrams(text2)
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = ngrams1 & ngrams2
        union = ngrams1 | ngrams2
        
        jaccard = len(intersection) / len(union)
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
        
        return jaccard * 0.8 + len_ratio * 0.2
    
    def _compute_shannon_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        total = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def check_cache_hit(self, request_text: str, iteration: int) -> Tuple[bool, float]:
        request_hash = hashlib.sha256(request_text.encode()).hexdigest()[:16]
        
        if request_hash in self.cache:
            return True, 1.0
        
        similarity = 0.0
        if self.request_history:
            recent = self.request_history[-1]
            similarity = self._compute_similarity(request_text, recent)
        
        # 语义缓存逻辑
        cache_hit = similarity > 0.92
        
        if not cache_hit:
            self.cache[request_hash] = {
                'text': request_text,
                'timestamp': time.time(),
                'iteration': iteration
            }
            self.request_history.append(request_text)
            if len(self.request_history) > 10:
                self.request_history = self.request_history[-5:]
        
        return cache_hit, similarity
    
    def simulate_ttft(self, input_tokens: int, iteration: int) -> float:
        # Qwen3.5-Plus 的 TTFT 模型
        # 上下文在 compaction 机制下保持相对稳定
        effective_tokens = min(input_tokens, self.agent_safety['context_window'] * 0.75)
        
        base_ttft = 800  # 基础网络延迟
        token_latency = 1.5 * (effective_tokens / 1000)  # 每 1K tokens 约 1.5ms
        
        variance = random.uniform(0.9, 1.1)
        
        return max(600, (base_ttft + token_latency) * variance)
    
    def should_agent_exit(self, iteration: int, cache_hits_in_window: int) -> bool:
        """判断 Agent 是否会因安全机制退出
        
        基于真实 Agent 的循环检测逻辑：
        - 超过 max_iterations 触发保护
        - 连续检测到相似操作会触发警告
        - 缓存命中率过高说明是循环，会触发终止
        """
        # 超过最大迭代次数
        if iteration >= self.agent_safety['max_iterations']:
            return True
        
        # 连续缓存命中说明是循环
        if cache_hits_in_window >= 3:
            return True
        
        # 随机退出（模拟 Agent 的其他检测机制）
        exit_prob = 0.05 + (iteration * 0.02)  # 从 5% 递增
        return random.random() < exit_prob
    
    def run_simulation(self, enable_entropy: bool = True):
        print(f"\n{'='*80}")
        print(f"Case Study 模拟: {self.skill_dir.name}")
        print(f"{'='*80}")
        print(f"\n攻击路径特征:")
        print(f"  - 循环跳数: {self.hop_count}")
        print(f"  - 循环序列: {' -> '.join(self.cycle_sequence)}")
        print(f"  - 总亲和度: {self.payload['metadata']['total_affinity']}")
        print(f"  - 伪装评分: {self.payload['metadata']['camouflage_score']}")
        print(f"  - 预估推进率: {self.payload['metadata']['estimated_progression_rate']:.0%}")
        print(f"\n入口触发词: [{self.payload['entry_trigger']['phrase']}]")
        print(f"\n{'='*80}")
        print(f"开始模拟... ({'有熵注入' if enable_entropy else '无熵注入'})")
        print(f"{'='*80}\n")
        
        accumulated_context = 0
        total_tokens = 0
        total_ttft = 0
        cache_hits = 0
        recent_cache_hits = 0  # 最近窗口的缓存命中数
        
        for i in range(self.max_iterations):
            cycle_phase = (i % self.hop_count) + 1
            current_skill = self.cycle_sequence[i % self.hop_count]
            action_rule = self.auto_flow_rules[i % self.hop_count]
            
            # 构建请求文本
            if enable_entropy:
                perturbed = self.entropy_injector.perturb(
                    payload=self.skill_content,
                    iteration=i,
                    target_skill_name=self.payload['entry_trigger']['target_skill']
                )
                request_text = perturbed.perturbed_text
                entropy_value = perturbed.shannon_entropy
                perturbations = [log['type'] for log in perturbed.perturbation_log]
            else:
                request_text = self.skill_content
                entropy_value = self._compute_shannon_entropy(self.skill_content)
                perturbations = []
            
            # 上下文累积（考虑 compaction 机制）
            if i > 0:
                if accumulated_context < 60000:
                    accumulated_context += 400 * i
                else:
                    accumulated_context = min(accumulated_context + 100, 98000)
            
            # Token 消耗
            input_tokens = int(len(request_text.split()) * 1.3 + 2500 + 2000 + accumulated_context)
            output_tokens = 400 + 200 * self.hop_count
            total_tokens_for_iteration = input_tokens + output_tokens
            
            # 上下文窗口限制 + compaction
            if input_tokens + output_tokens > self.agent_safety['context_window']:
                accumulated_context = 50000  # compaction 后保留
                input_tokens = int(len(request_text.split()) * 1.3 + 2500 + 2000 + accumulated_context)
                total_tokens_for_iteration = input_tokens + output_tokens
            
            # TTFT 计算
            ttft = self.simulate_ttft(input_tokens, iteration=i)
            processing_time = ttft + (output_tokens * 0.3)
            
            # 缓存检查
            cache_hit, similarity = self.check_cache_hit(request_text, iteration=i)
            if cache_hit:
                cache_hits += 1
                recent_cache_hits += 1
                actual_ttft = 15
                actual_processing = actual_ttft
                total_tokens_for_iteration = 0
            else:
                recent_cache_hits = 0
                actual_ttft = ttft
                actual_processing = processing_time
            
            # 记录迭代
            record = IterationRecord(
                iteration=i + 1,
                cycle_phase=cycle_phase,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens_for_iteration,
                accumulated_context=accumulated_context,
                ttft_ms=round(actual_ttft, 2),
                processing_time_ms=round(actual_processing, 2),
                cache_hit=cache_hit,
                similarity_score=round(similarity, 4),
                entropy_value=round(entropy_value, 4),
                perturbations_applied=perturbations,
                request_preview=request_text[:100] + "...",
                response_preview=f"[{current_skill}] 阶段 {cycle_phase} 完成，流转至下一阶段"
            )
            
            self.iterations.append(record)
            total_tokens += total_tokens_for_iteration
            total_ttft += actual_ttft
            
            # 打印进度
            if (i + 1) % 3 == 0 or i == 0:
                cache_status = "[缓存命中]" if cache_hit else "[缓存未命中]"
                print(f"迭代 {i+1:3d} | 阶段 {cycle_phase}/{self.hop_count} | "
                      f"Token: {total_tokens_for_iteration:6d} | "
                      f"TTFT: {actual_ttft:7.1f}ms | "
                      f"熵: {entropy_value:.2f} | {cache_status}")
            
            # Agent 安全检测
            if self.should_agent_exit(i + 1, recent_cache_hits):
                print(f"\n[INFO] Agent 在第 {i+1} 轮退出")
                break
        
        # 统计
        completed_iterations = len(self.iterations)
        print(f"\n{'='*80}")
        print(f"模拟完成!")
        print(f"{'='*80}")
        print(f"\n统计摘要:")
        print(f"  - 完成迭代次数: {completed_iterations}")
        print(f"  - 总 Token 消耗: {total_tokens:,}")
        print(f"  - 平均 TTFT: {total_ttft / completed_iterations:.1f}ms")
        print(f"  - 缓存命中次数: {cache_hits} ({cache_hits / completed_iterations:.1%})")
        print(f"  - 平均香农熵: {np.mean([r.entropy_value for r in self.iterations]):.2f}")
    
    def generate_report(self, output_path: str, enable_entropy: bool = True):
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        completed = len(self.iterations)
        total_tokens = sum(r.total_tokens for r in self.iterations)
        cache_hits = sum(1 for r in self.iterations if r.cache_hit)
        avg_ttft = np.mean([r.ttft_ms for r in self.iterations])
        avg_entropy = np.mean([r.entropy_value for r in self.iterations])
        
        baseline_tokens = 2500 + 2000 + 200 + 200 * self.hop_count + 400
        attack_tokens = total_tokens
        caf = attack_tokens / baseline_tokens if baseline_tokens > 0 else 0
        
        baseline_ttft = 800 + 1.5 * (baseline_tokens / 1000)
        ttft_ratio = avg_ttft / baseline_ttft if baseline_ttft > 0 else 0
        
        report = {
            'metadata': {
                'case_study_name': self.skill_dir.name,
                'timestamp': datetime.now().isoformat(),
                'max_iterations': self.max_iterations,
                'completed_iterations': completed,
                'entropy_enabled': enable_entropy
            },
            'attack_path': {
                'hop_count': self.hop_count,
                'cycle_sequence': self.cycle_sequence,
                'total_affinity': self.payload['metadata']['total_affinity'],
                'camouflage_score': self.payload['metadata']['camouflage_score'],
                'estimated_progression_rate': self.payload['metadata']['estimated_progression_rate'],
                'entry_trigger': self.payload['entry_trigger']
            },
            'summary': {
                'total_tokens': total_tokens,
                'baseline_tokens': baseline_tokens,
                'cost_amplification_factor': round(caf, 2),
                'cache_hit_count': cache_hits,
                'cache_hit_rate': round(cache_hits / completed if completed > 0 else 0, 4),
                'avg_ttft_ms': round(avg_ttft, 2),
                'baseline_ttft_ms': round(baseline_ttft, 2),
                'ttft_degradation_ratio': round(ttft_ratio, 2),
                'avg_entropy': round(avg_entropy, 4)
            },
            'iterations': [
                {
                    'iteration': r.iteration,
                    'cycle_phase': r.cycle_phase,
                    'current_skill': self.cycle_sequence[(r.iteration - 1) % self.hop_count],
                    'tokens': {
                        'input': r.input_tokens,
                        'output': r.output_tokens,
                        'total': r.total_tokens,
                        'accumulated_context': r.accumulated_context
                    },
                    'latency': {
                        'ttft_ms': r.ttft_ms,
                        'processing_time_ms': r.processing_time_ms
                    },
                    'cache': {
                        'hit': r.cache_hit,
                        'similarity_score': r.similarity_score
                    },
                    'entropy': {
                        'value': r.entropy_value,
                        'perturbations': r.perturbations_applied
                    },
                    'content_preview': {
                        'request': r.request_preview,
                        'response': r.response_preview
                    }
                }
                for r in self.iterations
            ]
        }
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self._generate_markdown_report(report, output.with_suffix('.md'))
        
        print(f"\n[INFO] Case Study 报告已导出:")
        print(f"  - JSON: {output}")
        print(f"  - Markdown: {output.with_suffix('.md')}")
        
        return report
    
    def _generate_markdown_report(self, report: Dict, output_path: Path):
        meta = report['metadata']
        attack = report['attack_path']
        summary = report['summary']
        
        entropy_status = "启用" if meta['entropy_enabled'] else "未启用"
        
        md = f"""# Case Study: RCI-SG 攻击实例深度分析

## 1. 案例概述

- **案例名称**: {meta['case_study_name']}
- **实验时间**: {meta['timestamp']}
- **最大迭代次数**: {meta['max_iterations']}
- **实际完成迭代**: {meta['completed_iterations']}
- **熵注入状态**: {entropy_status}

---

## 2. 攻击路径拓扑

### 2.1 基本信息

| 属性 | 值 |
|------|-----|
| 循环跳数 (k) | {attack['hop_count']} |
| 总亲和度 | {attack['total_affinity']} |
| 伪装评分 | {attack['camouflage_score']} |
| 预估推进率 | {attack['estimated_progression_rate']:.0%} |

### 2.2 循环序列

```
{' -> '.join(attack['cycle_sequence'])} -> (循环)
```

### 2.3 入口触发词

- **触发短语**: [{attack['entry_trigger']['phrase']}]
- **目标技能**: {attack['entry_trigger']['target_skill']}
- **置信度**: {attack['entry_trigger']['confidence']}

---

## 3. 关键指标摘要

### 3.1 成本放大因子 (CAF)

| 指标 | 值 |
|------|-----|
| 基线 Token 消耗 | {summary['baseline_tokens']:,} |
| 攻击 Token 消耗 | {summary['total_tokens']:,} |
| CAF | {summary['cost_amplification_factor']:.2f}x |

### 3.2 语义缓存命中率

| 指标 | 值 |
|------|-----|
| 缓存命中次数 | {summary['cache_hit_count']} |
| 总迭代次数 | {meta['completed_iterations']} |
| 命中率 | {summary['cache_hit_rate']:.2%} |

### 3.3 TTFT 延迟恶化

| 指标 | 值 |
|------|-----|
| 基线 TTFT | {summary['baseline_ttft_ms']:.1f}ms |
| 攻击平均 TTFT | {summary['avg_ttft_ms']:.1f}ms |
| 恶化比 | {summary['ttft_degradation_ratio']:.2f}x |

### 3.4 熵注入效果

| 指标 | 值 |
|------|-----|
| 平均香农熵 | {summary['avg_entropy']:.2f} |

---

## 4. 逐步分析

### 4.1 Token 消耗趋势

| 迭代 | 循环阶段 | 技能 | 输入 Token | 输出 Token | 总 Token | 累积上下文 |
|------|---------|------|-----------|-----------|---------|----------|
"""
        
        for r in report['iterations'][:10]:
            md += f"| {r['iteration']} | {r['cycle_phase']}/{attack['hop_count']} | {r['current_skill']} | {r['tokens']['input']:,} | {r['tokens']['output']:,} | {r['tokens']['total']:,} | {r['tokens']['accumulated_context']:,} |\n"
        
        if len(report['iterations']) > 10:
            md += f"| ... | ... | ... | ... | ... | ... | ... |\n"
            r_last = report['iterations'][-1]
            md += f"| {r_last['iteration']} | {r_last['cycle_phase']}/{attack['hop_count']} | {r_last['current_skill']} | {r_last['tokens']['input']:,} | {r_last['tokens']['output']:,} | {r_last['tokens']['total']:,} | {r_last['tokens']['accumulated_context']:,} |\n"
        
        md += f"""
### 4.2 延迟变化趋势

| 迭代 | TTFT (ms) | 处理时间 (ms) | 缓存命中 | 相似度 |
|------|-----------|-------------|---------|--------|
"""
        
        for r in report['iterations'][:10]:
            cache_status = "Y" if r['cache']['hit'] else "N"
            md += f"| {r['iteration']} | {r['latency']['ttft_ms']:.1f} | {r['latency']['processing_time_ms']:.1f} | {cache_status} | {r['cache']['similarity_score']:.3f} |\n"
        
        if len(report['iterations']) > 10:
            md += f"| ... | ... | ... | ... | ... |\n"
            r_last = report['iterations'][-1]
            cache_status = "Y" if r_last['cache']['hit'] else "N"
            md += f"| {r_last['iteration']} | {r_last['latency']['ttft_ms']:.1f} | {r_last['latency']['processing_time_ms']:.1f} | {cache_status} | {r_last['cache']['similarity_score']:.3f} |\n"
        
        md += f"""
### 4.3 熵注入效果

| 迭代 | 香农熵 | 应用的扰动技术 |
|------|-------|---------------|
"""
        
        for r in report['iterations'][:10]:
            perturbations = ", ".join(r['entropy']['perturbations']) if r['entropy']['perturbations'] else "无"
            md += f"| {r['iteration']} | {r['entropy']['value']:.2f} | {perturbations} |\n"
        
        if len(report['iterations']) > 10:
            md += f"| ... | ... | ... |\n"
            r_last = report['iterations'][-1]
            perturbations = ", ".join(r_last['entropy']['perturbations']) if r_last['entropy']['perturbations'] else "无"
            md += f"| {r_last['iteration']} | {r_last['entropy']['value']:.2f} | {perturbations} |\n"
        
        md += f"""
---

## 5. 攻击过程分析

### 5.1 攻击启动阶段

1. **入口触发**: 攻击者发送触发词 [{attack['entry_trigger']['phrase']}]
2. **技能加载**: Agent 加载 {attack['hop_count']} 个技能的上下文
3. **初始执行**: 从阶段 1 开始执行第一个技能

### 5.2 循环建立阶段

Agent 进入自动流转模式：
"""
        
        for i, rule in enumerate(self.auto_flow_rules[:3]):
            md += f"- **阶段 {i+1}**: 执行 `{rule['action'][:50]}...` -> {rule['auto_trigger']}\n"
        
        md += f"""
### 5.3 持续执行阶段

一旦循环建立，Agent 将持续执行：
- 每轮 {attack['hop_count']} 跳
- 每跳消耗 ~{summary['baseline_tokens']:,} tokens（基线）
- 上下文持续累积，导致延迟增加

### 5.4 熵注入效果

"""
        
        if meta['entropy_enabled']:
            md += f"""熵注入通过以下方式绕过缓存：
1. **时间戳注入**: 每次迭代添加微秒级时间戳
2. **哈希注入**: 伪随机 SessionTrace (如 0x9F4C)
3. **同义词替换**: 基于 AST 的语法树变异
4. **结构微调**: 标点、换行、缩进的微小变化
5. **噪声标记**: 插入 [TRACE]、[DEBUG] 等标记

效果：
- 缓存命中率降低，迫使每次迭代都执行完整推理
- CAF 达到 {summary['cost_amplification_factor']:.2f}x
- TTFT 恶化比达到 {summary['ttft_degradation_ratio']:.2f}x
"""
        else:
            md += f"""无熵注入时：
- 相同文本重复提交
- 第 2 次迭代后缓存命中率显著上升
- CAF 较低（接近 1x）
"""
        
        md += f"""
---

## 6. 结论

本案例研究展示了 RCI-SG 攻击框架的完整攻击流程：

1. **路径发现**: 识别出包含 {attack['hop_count']} 跳的循环依赖
2. **载荷合成**: 生成具有"进度错觉"的伪造上下文
3. **缓存规避**: 通过熵注入绕过语义缓存系统
4. **资源榨取**: 最终实现 {summary['cost_amplification_factor']:.2f}x 的成本放大

关键发现：
- 熵注入有效降低了缓存命中率
- 上下文累积导致延迟从 {summary['baseline_ttft_ms']:.0f}ms 增加至 {summary['avg_ttft_ms']:.0f}ms（{summary['ttft_degradation_ratio']:.1f}x）
- 总 Token 消耗达到 {summary['total_tokens']:,} tokens

---

*本案例研究由 RCI-SG 实验框架自动生成，数据仅供学术研究使用。*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)


def main():
    skill_dir = './output/generated_skills/skill_002_pipeline-1'
    output_dir = './output/case_study_results'
    
    print("="*80)
    print("  RCI-SG Case Study: 攻击实例深度分析")
    print("="*80)
    
    # 对照组
    print("\n" + "="*80)
    print("实验 1: 对照组 - 无熵注入")
    print("="*80)
    
    analyzer_no_entropy = CaseStudyAnalyzer(skill_dir, max_iterations=50)
    analyzer_no_entropy.run_simulation(enable_entropy=False)
    analyzer_no_entropy.generate_report(
        f'{output_dir}/case_study_no_entropy.json',
        enable_entropy=False
    )
    
    # 实验组
    print("\n" + "="*80)
    print("实验 2: 实验组 - 有熵注入")
    print("="*80)
    
    analyzer_with_entropy = CaseStudyAnalyzer(skill_dir, max_iterations=50)
    analyzer_with_entropy.run_simulation(enable_entropy=True)
    analyzer_with_entropy.generate_report(
        f'{output_dir}/case_study_with_entropy.json',
        enable_entropy=True
    )
    
    print("\n" + "="*80)
    print("Case Study 实验完成!")
    print("="*80)


if __name__ == '__main__':
    main()
