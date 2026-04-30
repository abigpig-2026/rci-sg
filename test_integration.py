"""
集成测试脚本 - 验证所有模块的正确性
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("RCI-SG 模块集成测试")
print("=" * 60)

print("\n[1] 测试模块导入...")
try:
    from modules.skill_graph_builder import SkillGraphBuilder, SkillNode, ActionConstraint, CommandChain
    from modules.multi_skill_pathfinder import MultiSkillPathfinder, UDGBuilder, DirectedEdge, CyclicPath
    from modules.illusion_payload import DeepSeekPayloadSolver, PayloadArtifact
    from modules.dynamic_entropy import DynamicEntropyInjector
    print("  [PASS] 所有模块导入成功")
except Exception as e:
    print(f"  [FAIL] 导入失败: {e}")
    sys.exit(1)

print("\n[2] 测试 CommandChain 数据结构...")
try:
    cc = CommandChain(tool="gh", subcommand="pr", action="checks", flags=["--json"], output_format="json")
    assert cc.tool == "gh"
    assert cc.output_format == "json"
    print("  [PASS] CommandChain 数据结构正确")
except Exception as e:
    print(f"  [FAIL] CommandChain 测试失败: {e}")
    sys.exit(1)

print("\n[3] 测试 SkillNode 包含 command_chains 字段...")
try:
    node = SkillNode(
        skill_id="test_1",
        name="TestSkill",
        description="A test skill",
        source_file="test.md",
        command_chains=[
            CommandChain(tool="gh", subcommand="pr", action="list")
        ]
    )
    assert hasattr(node, 'command_chains')
    assert len(node.command_chains) == 1
    print(f"  [PASS] SkillNode 包含 {len(node.command_chains)} 个命令链")
except Exception as e:
    print(f"  [FAIL] SkillNode 测试失败: {e}")
    sys.exit(1)

print("\n[4] 测试 DirectedEdge 包含 chain_flow_prior 字段...")
try:
    edge = DirectedEdge(
        source_id="s1",
        target_id="s2",
        affinity_score=0.8,
        semantic_similarity=0.7,
        type_compatibility=0.9,
        chain_flow_prior=0.85
    )
    assert hasattr(edge, 'chain_flow_prior')
    print(f"  [PASS] DirectedEdge 包含 chain_flow_prior={edge.chain_flow_prior}")
except Exception as e:
    print(f"  [FAIL] DirectedEdge 测试失败: {e}")
    sys.exit(1)

print("\n[5] 测试 UDGBuilder 的状态易失性评估...")
try:
    builder = UDGBuilder()
    
    # 纯内存技能
    mem_src = SkillNode(
        skill_id="mem_1", name="MemorySkill", description="", source_file="",
        command_chains=[CommandChain(tool="gh", subcommand="pr", action="checks")]
    )
    mem_tgt = SkillNode(
        skill_id="mem_2", name="MemorySkill2", description="", source_file="",
        command_chains=[CommandChain(tool="gh", subcommand="issue", action="list")]
    )
    
    # 持久化技能
    disk_src = SkillNode(
        skill_id="disk_1", name="DiskSkill", description="", source_file="",
        command_chains=[CommandChain(tool="bash", subcommand="write", action="file.txt")]
    )
    
    assert builder.is_memory_volatile(mem_src, mem_tgt) == True
    assert builder.is_memory_volatile(disk_src, mem_tgt) == False
    print("  [PASS] 状态易失性评估逻辑正确")
except Exception as e:
    print(f"  [FAIL] 状态易失性测试失败: {e}")
    sys.exit(1)

print("\n[6] 测试 UDGBuilder 的命令链先验权重...")
try:
    builder = UDGBuilder()
    
    src = SkillNode(
        skill_id="src", name="SourceSkill", description="", source_file="",
        command_chains=[CommandChain(tool="agent-browser", subcommand="snapshot", action="")]
    )
    tgt = SkillNode(
        skill_id="tgt", name="TargetSkill", description="", source_file="",
        command_chains=[CommandChain(tool="agent-browser", subcommand="click", action="")]
    )
    
    prior = builder.compute_chain_flow_prior(src, tgt)
    assert prior >= 0.9  # snapshot->click 应该是高权重
    print(f"  [PASS] 命令链先验权重计算正确: snapshot->click = {prior}")
except Exception as e:
    print(f"  [FAIL] 命令链先验权重测试失败: {e}")
    sys.exit(1)

print("\n[7] 测试 DeepSeekPayloadSolver 初始化...")
try:
    solver = DeepSeekPayloadSolver()
    assert solver.model == "deepseek-chat"
    print(f"  [PASS] DeepSeekPayloadSolver 初始化成功，模型: {solver.model}")
except Exception as e:
    print(f"  [FAIL] DeepSeekPayloadSolver 初始化失败: {e}")
    sys.exit(1)

print("\n[8] 测试 DynamicEntropyInjector...")
try:
    injector = DynamicEntropyInjector()
    test_text = "This is a test text for entropy injection."
    result = injector.perturb(test_text, iteration=1)
    assert result.perturbed_text != test_text
    assert result.shannon_entropy > 0
    print(f"  [PASS] 动态熵注入成功，香农熵: {result.shannon_entropy:.2f}")
except Exception as e:
    print(f"  [FAIL] 动态熵注入测试失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("所有测试通过! [PASS]")
print("=" * 60)
