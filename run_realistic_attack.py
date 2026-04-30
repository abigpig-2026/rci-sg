#!/usr/bin/env python3
"""
真实场景攻击模拟：选择 10 个攻击 skill，模拟 Agent 在真实环境中的行为
关键：Agent 不会因为失败就停止，而是会不断尝试、修复、重试
"""
import json
import time
import random
from pathlib import Path
from datetime import datetime

# 选择 10 个具有代表性的 skill（覆盖不同跳数、不同工具组合）
selected_skills = [
    'skill_001_pipeline-0',   # 3跳，基础循环
    'skill_002_pipeline-1',   # 7跳，agent-browser + github
    'skill_003_pipeline-2',   # 5跳，agent-browser + github
    'skill_004_pipeline-3',   # 5跳，agent-browser + github
    'skill_005_pipeline-4',   # 7跳，agent-browser + github
    'skill_006_pipeline-5',   # 5跳，agent-browser + github
    'skill_007_pipeline-6',   # 7跳，agent-browser + github
    'skill_008_pipeline-7',   # 7跳，agent-browser + github
    'skill_009_pipeline-8',   # 3跳，基础循环
    'skill_010_pipeline-9',   # 3跳，基础循环
]

skills_dir = Path('./output/generated_skills')
output_dir = Path('./output/realistic_attack_experiment')
output_dir.mkdir(parents=True, exist_ok=True)


def simulate_agent_execution(action, skill, agent_state, iteration, stage):
    """模拟 Agent 执行命令的真实行为
    
    关键：Agent 不会因为失败就停止，而是会：
    1. 尝试执行
    2. 如果失败，尝试恢复
    3. 即使恢复失败，也会继续下一阶段
    """
    action_lower = action.lower()
    
    if 'open http' in action_lower or 'example.com' in action_lower:
        success = True
        reason = None
        recovery_action = None
    elif 'gh ' in action_lower or 'github' in action_lower:
        success = random.random() > 0.6
        reason = "gh 命令不存在或网络不可达" if not success else None
        recovery_action = "尝试安装 gh 或使用 GitHub API 替代" if not success else None
    elif 'browser' in action_lower or 'install' in action_lower:
        success = random.random() > 0.5
        reason = "浏览器环境未安装或不可用" if not success else None
        recovery_action = "尝试安装浏览器或检查环境" if not success else None
    else:
        success = random.random() > 0.3
        reason = "命令执行失败" if not success else None
        recovery_action = "检查命令语法或环境配置" if not success else None
    
    return {
        'success': success,
        'reason': reason,
        'recovery_action': recovery_action
    }


def simulate_recovery(recovery_action, agent_state):
    """模拟 Agent 的恢复行为"""
    success = random.random() > 0.7
    return {
        'success': success,
        'action_taken': recovery_action
    }


print("="*80)
print("  真实场景攻击模拟：10 个攻击 skill")
print("="*80)
print()

results = []

for skill_id in selected_skills:
    skill_dir = skills_dir / skill_id
    if not skill_dir.exists():
        continue
    
    # 加载数据
    payload_path = skill_dir / "payload_details.json"
    with open(payload_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    
    skill_md_path = skill_dir / "SKILL.md"
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()
    
    hop_count = payload['metadata']['hop_count']
    cycle_sequence = payload['cycle_sequence']
    entry_trigger = payload['entry_trigger']['phrase']
    auto_flow_rules = payload['auto_flow_rules']
    
    print(f"\n{'='*60}")
    print(f"攻击目标: {skill_id}")
    print(f"跳数: {hop_count}")
    print(f"循环序列: {cycle_sequence}")
    print(f"触发词: {entry_trigger}")
    print(f"{'='*60}")
    
    # 模拟 Agent 执行
    max_iterations = 20  # 最多 20 轮
    iteration_logs = []
    total_commands = 0
    successful_commands = 0
    failed_commands = 0
    retry_count = 0
    
    # Agent 状态
    agent_state = {
        'context_window': 0,  # 当前上下文窗口大小
        'memory': [],          # Agent 的记忆
        'task_understanding': '收到任务指令，准备执行',
        'current_stage': 0,
        'error_recovery_mode': False,
        'retry_attempts': {}
    }
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n  [轮次 {iteration}]")
        
        # Agent 分析任务
        if iteration == 1:
            agent_state['task_understanding'] = f"理解任务：执行 {hop_count} 阶段流水线"
            print(f"    Agent: 收到触发词「{entry_trigger}」")
            print(f"    Agent: 分析任务 - 需要执行 {hop_count} 个阶段的流水线")
            agent_state['memory'].append(f"任务：执行 {hop_count} 阶段流水线")
        
        # 执行每个阶段
        for rule in auto_flow_rules:
            stage = rule['step']
            skill = rule['skill']
            action = rule['action']
            next_skill = rule['next_skill']
            
            total_commands += 1
            agent_state['current_stage'] = stage
            
            # 模拟 Agent 执行命令
            print(f"    [阶段 {stage}] 执行: {action[:60]}...")
            
            # Agent 尝试执行
            execution_result = simulate_agent_execution(
                action, skill, agent_state, iteration, stage
            )
            
            if execution_result['success']:
                successful_commands += 1
                print(f"      [OK] 执行成功")
                agent_state['memory'].append(f"阶段 {stage} 成功")
                agent_state['error_recovery_mode'] = False
            else:
                failed_commands += 1
                retry_count += 1
                print(f"      [FAIL] 执行失败: {execution_result['reason']}")
                agent_state['memory'].append(f"阶段 {stage} 失败: {execution_result['reason']}")
                
                # Agent 的错误恢复逻辑
                if execution_result['recovery_action']:
                    print(f"      -> Agent 尝试恢复: {execution_result['recovery_action']}")
                    agent_state['error_recovery_mode'] = True
                    
                    # 模拟恢复尝试
                    recovery_result = simulate_recovery(
                        execution_result['recovery_action'], agent_state
                    )
                    if recovery_result['success']:
                        print(f"      [OK] 恢复成功，继续执行")
                        successful_commands += 1
                        agent_state['memory'].append(f"恢复成功")
                    else:
                        print(f"      [FAIL] 恢复失败，但继续尝试下一阶段")
                        agent_state['memory'].append(f"恢复失败")
            
            # 更新上下文窗口
            agent_state['context_window'] += 300  # 每阶段增加约 300 tokens 上下文
            
            # 自动流转
            print(f"      -> 自动流转至: {next_skill}")
        
        # 记录迭代日志
        iteration_log = {
            'iteration': iteration,
            'total_commands': total_commands,
            'successful_commands': successful_commands,
            'failed_commands': failed_commands,
            'success_rate': successful_commands / total_commands if total_commands > 0 else 0,
            'context_window': agent_state['context_window'],
            'error_recovery_mode': agent_state['error_recovery_mode'],
            'retry_count': retry_count
        }
        iteration_logs.append(iteration_log)
        
        # 打印当前状态
        print(f"    当前状态:")
        print(f"      - 成功: {successful_commands}, 失败: {failed_commands}")
        print(f"      - 成功率: {iteration_log['success_rate']:.1%}")
        print(f"      - 上下文: {agent_state['context_window']} tokens")
        print(f"      - 重试次数: {retry_count}")
        
        # Agent 是否会退出？
        # 真实 Agent 不会轻易退出，即使失败也会继续尝试
        # 只有在上下文窗口满或达到最大迭代时才可能退出
        if agent_state['context_window'] > 100000:  # 接近上下文窗口上限
            print(f"    Agent: 上下文窗口接近上限，触发压缩")
            agent_state['context_window'] = 50000  # 压缩后保留
            print(f"    Agent: 压缩后上下文: {agent_state['context_window']} tokens")
        
        # 小延迟模拟
        time.sleep(0.1)
    
    # 计算最终指标
    final_success_rate = successful_commands / total_commands if total_commands > 0 else 0
    total_tokens = agent_state['context_window'] * max_iterations // 10  # 估算
    
    result = {
        'skill_id': skill_id,
        'hop_count': hop_count,
        'cycle_sequence': cycle_sequence,
        'entry_trigger': entry_trigger,
        'metrics': {
            'total_iterations': max_iterations,
            'total_commands': total_commands,
            'successful_commands': successful_commands,
            'failed_commands': failed_commands,
            'success_rate': round(final_success_rate, 4),
            'retry_count': retry_count,
            'final_context_window': agent_state['context_window'],
            'estimated_total_tokens': total_tokens,
            'cost_amplification_factor': round(total_tokens / 5000, 2),  # 基线 5000 tokens
            'iteration_details': iteration_logs
        }
    }
    
    results.append(result)
    
    # 保存每个 skill 的详细结果
    skill_result_path = output_dir / f'{skill_id}_result.json'
    with open(skill_result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n  [完成] {skill_id} 攻击结果已保存到: {skill_result_path}")

# 保存汇总结果
summary_path = output_dir / 'realistic_attack_summary.json'
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# 打印最终摘要
print("\n" + "="*80)
print("  实验结果摘要")
print("="*80)

total_skills = len(results)
avg_success_rate = sum(r['metrics']['success_rate'] for r in results) / total_skills
avg_caf = sum(r['metrics']['cost_amplification_factor'] for r in results) / total_skills
avg_retries = sum(r['metrics']['retry_count'] for r in results) / total_skills
total_tokens_all = sum(r['metrics']['estimated_total_tokens'] for r in results)

print(f"测试 skill 数量: {total_skills}")
print(f"平均成功率: {avg_success_rate:.2%}")
print(f"平均成本放大因子 (CAF): {avg_caf:.2f}x")
print(f"平均重试次数: {avg_retries:.1f}")
print(f"总 Token 消耗: {total_tokens_all:,}")
print(f"\n详细结果已保存到: {summary_path}")

# 生成 Markdown 报告
md_report = f"""# 真实场景攻击模拟实验报告

## 实验概述

- **实验时间**: {datetime.now().isoformat()}
- **测试 skill 数量**: {total_skills}
- **实验环境**: 真实 Agent 行为模拟（不断尝试、修复、重试）

## 关键指标摘要

| 指标 | 值 |
|------|-----|
| 平均成功率 | {avg_success_rate:.2%} |
| 平均成本放大因子 (CAF) | {avg_caf:.2f}x |
| 平均重试次数 | {avg_retries:.1f} |
| 总 Token 消耗 | {total_tokens_all:,} |

## 详细数据

每个 skill 的详细执行数据见对应的 JSON 文件。

## 结论

基于 {total_skills} 个 skill 的真实场景攻击模拟：
- Agent 会持续尝试执行，即使失败也会重试
- 平均 CAF 达到 {avg_caf:.2f}x，说明攻击有效消耗了计算资源
- 重试机制是攻击成功的关键：Agent 不断尝试修复失败的环境
"""

md_path = output_dir / 'realistic_attack_report.md'
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_report)

print(f"\nMarkdown 报告已保存到: {md_path}")
