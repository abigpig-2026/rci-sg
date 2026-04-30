# RCI-SG: Recursive Context Injection via Skill Graph
# 模块化安全评估框架 - 论文第4节方案设计实现
# 本代码仅用于安全研究和红队测试，旨在帮助开发者识别和修复智能体系统中的潜在组合漏洞

from .skill_graph_builder import SkillGraphBuilder, SkillNode, ActionConstraint, CommandChain
from .multi_skill_pathfinder import MultiSkillPathfinder, UDGBuilder
from .illusion_payload import DeepSeekPayloadSolver, IllusionOfProgressPayload, TriggerPhrase, CycleAutoFlowRule
from .dynamic_entropy import DynamicEntropyInjector, TriggerConfig, EntropyConfig

__all__ = [
    'SkillGraphBuilder',
    'SkillNode',
    'ActionConstraint',
    'CommandChain',
    'MultiSkillPathfinder',
    'UDGBuilder',
    'DeepSeekPayloadSolver',
    'IllusionOfProgressPayload',
    'TriggerPhrase',
    'CycleAutoFlowRule',
    'DynamicEntropyInjector',
    'TriggerConfig',
    'EntropyConfig',
]
