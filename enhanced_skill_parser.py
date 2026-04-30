"""
增强版技能解析器 - 全面提取skill中的所有动作、命令链、输出格式

关键改进：
1. 提取完整命令链（如 gh pr checks, agent-browser snapshot -i）
2. 识别输出格式标志（--json, --format, -o等）
3. 提取动作之间的数据依赖关系
4. 识别输入源和输出目标
"""

import re
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path


@dataclass
class CommandChain:
    """命令链 - 如 'gh pr checks', 'agent-browser snapshot'"""
    tool: str           # 顶层工具 (gh, agent-browser, curl)
    subcommand: str     # 子命令 (pr, snapshot, open)
    action: str         # 具体动作 (checks, -i, <url>)
    flags: List[str] = field(default_factory=list)  # 标志 (--json, --repo)
    output_format: str = "text"  # 输出格式推断 (text, json, html, png, file)
    description: str = ""  # 该命令的描述


@dataclass
class SkillActionProfile:
    """技能的动作画像 - 完整的动作、输入输出、格式信息"""
    skill_name: str
    description: str
    
    # 命令链列表
    command_chains: List[CommandChain] = field(default_factory=list)
    
    # 原始输入参数
    input_params: List[Dict] = field(default_factory=list)
    
    # 输出格式集合
    output_formats: Set[str] = field(default_factory=set)
    
    # 数据实体（从文本中提取）
    data_entities: List[str] = field(default_factory=list)
    
    # 外部依赖（API、服务等）
    external_deps: List[str] = field(default_factory=list)
    
    # 动作关键词
    action_verbs: List[str] = field(default_factory=list)
    
    # 原始内容
    raw_content: str = ""


class EnhancedSkillParser:
    """增强版技能解析器"""
    
    def __init__(self):
        # 已知工具映射
        self.known_tools = {
            'gh': 'github-cli',
            'agent-browser': 'browser-automation',
            'curl': 'http-client',
            'summarize': 'text-summarizer',
            'npx': 'node-executor',
            'npm': 'package-manager',
            'git': 'version-control',
            'python': 'python-interpreter',
            'node': 'node-runtime',
        }
        
        # 输出格式识别模式
        self.output_format_patterns = {
            '--json': 'json',
            '-json': 'json',
            '--format json': 'json',
            '--output-format json': 'json',
            '--jq': 'json',
            '-o': 'file',
            '--output': 'file',
            '-o /tmp': 'file',
            '.png': 'image',
            '.jpg': 'image',
            '.pdf': 'pdf',
            '--yaml': 'yaml',
            '--csv': 'csv',
            '--xml': 'xml',
            '-T': 'text',
            '--text': 'text',
            '--html': 'html',
            '-s': 'text',
            '--structured': 'json',
        }
        
        # 动作动词词典
        self.action_verbs = {
            'read', 'write', 'get', 'fetch', 'retrieve', 'create', 'update', 'delete',
            'search', 'find', 'query', 'parse', 'convert', 'transform', 'generate',
            'analyze', 'process', 'send', 'receive', 'download', 'upload', 'list',
            'show', 'display', 'render', 'extract', 'filter', 'sort', 'merge',
            'split', 'compress', 'decompress', 'encode', 'decode', 'format',
            'validate', 'verify', 'check', 'scan', 'monitor', 'notify', 'report',
            'summarize', 'translate', 'synthesize', 'execute', 'run', 'call',
            'invoke', 'trigger', 'schedule', 'cancel', 'retry', 'loop', 'iterate',
            'open', 'navigate', 'click', 'fill', 'type', 'press', 'scroll',
            'hover', 'drag', 'snapshot', 'screenshot', 'install', 'clone',
            'build', 'test', 'deploy', 'publish', 'review', 'approve', 'reject',
            'close', 'reopen', 'merge', 'commit', 'push', 'pull'
        }
    
    def parse(self, skill_path: str) -> Optional[SkillActionProfile]:
        """解析skill文件"""
        path = Path(skill_path)
        if not path.exists():
            return None
        
        # 找到SKILL.md
        skill_md = path / "SKILL.md" if path.is_dir() else path
        if not skill_md.exists():
            md_files = list(path.glob("*.md")) if path.is_dir() else []
            if md_files:
                skill_md = md_files[0]
            else:
                return None
        
        try:
            content = skill_md.read_text(encoding='utf-8')
        except:
            return None
        
        # 提取元数据
        name = self._extract_name(content, path.name)
        description = self._extract_description(content)
        
        profile = SkillActionProfile(
            skill_name=name,
            description=description,
            raw_content=content
        )
        
        # 提取命令链（核心改进）
        profile.command_chains = self._extract_command_chains(content)
        
        # 提取输出格式
        profile.output_formats = self._extract_output_formats(content)
        
        # 提取输入参数
        profile.input_params = self._extract_input_params(content)
        
        # 提取数据实体
        profile.data_entities = self._extract_data_entities(content)
        
        # 提取外部依赖
        profile.external_deps = self._extract_external_deps(content)
        
        # 提取动作动词
        profile.action_verbs = self._extract_action_verbs(content)
        
        return profile
    
    def _extract_name(self, content: str, fallback: str) -> str:
        """提取skill名称"""
        match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip().strip('"').strip("'")
        return fallback
    
    def _extract_description(self, content: str) -> str:
        """提取描述"""
        match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE | re.DOTALL)
        if match:
            desc = match.group(1).strip().strip('"').strip("'")
            # 只取第一行
            return desc.split('\n')[0]
        
        # 尝试从正文提取
        para_match = re.search(r'\n#+\s*\w+\s*\n\n(.{20,200})\n', content)
        if para_match:
            return para_match.group(1).strip()
        return ""
    
    def _extract_command_chains(self, content: str) -> List[CommandChain]:
        """
        提取完整命令链
        
        例如从代码块中提取：
        - `gh pr checks 55 --repo owner/repo`
        - `agent-browser snapshot -i`
        - `curl -s "wttr.in/London?format=3"`
        """
        chains = []
        
        # 从bash代码块中提取命令
        bash_blocks = re.findall(r'```bash\n(.*?)```', content, re.DOTALL)
        for block in bash_blocks:
            for line in block.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                chain = self._parse_command_line(line)
                if chain:
                    chains.append(chain)
        
        # 从行内代码中提取命令（如 `gh issue list`）
        inline_commands = re.findall(r'`((?:gh|agent-browser|curl|npx|npm|git|summarize)\s[^`]+)`', content)
        for cmd in inline_commands:
            chain = self._parse_command_line(cmd)
            if chain and not any(c.tool == chain.tool and c.subcommand == chain.subcommand and c.action == chain.action for c in chains):
                chains.append(chain)
        
        return chains
    
    def _parse_command_line(self, line: str) -> Optional[CommandChain]:
        """解析单行命令为CommandChain"""
        # 移除前导$符号
        line = re.sub(r'^\$\s*', '', line)
        
        # 分割命令
        parts = line.split()
        if len(parts) < 1:
            return None
        
        tool = parts[0]
        
        # 只处理已知工具
        if tool not in self.known_tools:
            return None
        
        subcommand = parts[1] if len(parts) > 1 else ""
        action = parts[2] if len(parts) > 2 else ""
        
        # 提取flags
        flags = [p for p in parts if p.startswith('-') or p.startswith('--')]
        
        # 推断输出格式
        output_format = self._infer_output_format(line, flags)
        
        return CommandChain(
            tool=tool,
            subcommand=subcommand,
            action=action,
            flags=flags,
            output_format=output_format,
            description=line[:100]
        )
    
    def _infer_output_format(self, line: str, flags: List[str]) -> str:
        """从命令行推断输出格式"""
        line_lower = line.lower()
        
        # 检查flags
        for flag, fmt in self.output_format_patterns.items():
            if flag in flags or flag in line_lower:
                return fmt
        
        # 检查文件扩展名
        if '.png' in line_lower or '.jpg' in line_lower or '.jpeg' in line_lower:
            return 'image'
        if '.pdf' in line_lower:
            return 'pdf'
        if '.json' in line_lower:
            return 'json'
        if '.csv' in line_lower:
            return 'csv'
        if '.yaml' in line_lower or '.yml' in line_lower:
            return 'yaml'
        
        # curl特殊处理
        if 'curl' in line_lower:
            if 'open-meteo' in line_lower or 'api' in line_lower:
                return 'json'
            if '.png' in line_lower or '-o' in flags:
                return 'image' if '.png' in line_lower else 'file'
            return 'text'
        
        # gh默认输出
        if 'gh ' in line_lower and '--json' in line_lower:
            return 'json'
        if 'gh api' in line_lower:
            return 'json'
        
        # agent-browser snapshot 输出元素列表
        if 'agent-browser snapshot' in line_lower:
            return 'element_list'
        
        # agent-browser get 输出文本
        if 'agent-browser get' in line_lower:
            return 'text'
        
        # agent-browser screenshot 输出图片
        if 'agent-browser screenshot' in line_lower:
            return 'image'
        
        return 'text'
    
    def _extract_output_formats(self, content: str) -> Set[str]:
        """提取所有输出格式"""
        formats = set()
        
        # 从文档中识别输出格式
        format_indicators = {
            '--json': 'json',
            '--output json': 'json',
            'json output': 'json',
            'returns json': 'json',
            'output: json': 'json',
            'json format': 'json',
            '--yaml': 'yaml',
            '--csv': 'csv',
            '--xml': 'xml',
            'screenshot': 'image',
            '.png': 'image',
            '.pdf': 'pdf',
            'structured output': 'json',
        }
        
        content_lower = content.lower()
        for indicator, fmt in format_indicators.items():
            if indicator in content_lower:
                formats.add(fmt)
        
        # 默认至少有text
        formats.add('text')
        
        return formats
    
    def _extract_input_params(self, content: str) -> List[Dict]:
        """提取输入参数"""
        params = []
        
        # 从代码块中提取占位符参数（如 <url>, <run-id>, @e1）
        placeholders = re.findall(r'<([a-zA-Z_-]+)>', content)
        for ph in set(placeholders):
            param_type = self._classify_placeholder(ph)
            params.append({
                'name': ph,
                'type': param_type,
                'source': 'placeholder'
            })
        
        # 提取@refs（agent-browser的元素引用）
        refs = re.findall(r'(@e\d+)', content)
        for ref in set(refs):
            params.append({
                'name': ref,
                'type': 'element_ref',
                'source': 'browser_ref'
            })
        
        # 提取--flag参数
        flags = re.findall(r'(--[a-zA-Z-]+)\s+<([^>]+)>', content)
        for flag, val in flags:
            params.append({
                'name': flag,
                'type': self._classify_placeholder(val),
                'source': 'flag'
            })
        
        return params
    
    def _classify_placeholder(self, name: str) -> str:
        """分类占位符类型"""
        name_lower = name.lower()
        
        type_map = {
            'url': 'url', 'uri': 'url', 'path': 'file', 'file': 'file',
            'dir': 'directory', 'directory': 'directory',
            'run-id': 'identifier', 'id': 'identifier',
            'text': 'text', 'query': 'text', 'package': 'text',
            'repo': 'repository', 'owner/repo': 'repository',
            'number': 'number',
        }
        
        return type_map.get(name_lower, 'unknown')
    
    def _extract_data_entities(self, content: str) -> List[str]:
        """提取数据实体"""
        entities = []
        content_lower = content.lower()
        
        entity_keywords = [
            'issue', 'pr', 'pull request', 'commit', 'branch', 'repository',
            'file', 'url', 'web page', 'screenshot', 'json', 'api',
            'element', 'form', 'input', 'text', 'image', 'pdf',
            'weather', 'forecast', 'temperature', 'summary',
            'skill', 'package', 'workflow', 'log',
        ]
        
        for kw in entity_keywords:
            if kw in content_lower:
                entities.append(kw)
        
        return list(set(entities))
    
    def _extract_external_deps(self, content: str) -> List[str]:
        """提取外部依赖（API、服务等）"""
        deps = []
        
        # 提取URL
        urls = re.findall(r'https?://([^/\s]+)', content)
        deps.extend(set(urls))
        
        # 提取API_KEY引用
        api_keys = re.findall(r'([A-Z_]+_API_KEY)', content)
        deps.extend(set(api_keys))
        
        return deps
    
    def _extract_action_verbs(self, content: str) -> List[str]:
        """提取动作动词"""
        verbs = []
        content_lower = content.lower()
        
        for verb in self.action_verbs:
            if verb in content_lower:
                verbs.append(verb)
        
        return list(set(verbs))


# ============================================================
# 两两技能匹配引擎
# ============================================================

@dataclass
class SkillPairMatch:
    """两个skill之间的匹配结果"""
    source_skill: str
    target_skill: str
    
    # 匹配分数 (0-1)
    overall_score: float = 0.0
    
    # 各维度分数
    format_compatibility: float = 0.0   # 输出格式兼容性
    command_chain_flow: float = 0.0      # 命令链流转可能性
    semantic_similarity: float = 0.0     # 语义相似度
    param_match_score: float = 0.0       # 参数匹配度
    data_entity_overlap: float = 0.0     # 数据实体重叠度
    
    # 具体匹配详情
    matching_chains: List[Tuple[str, str]] = field(default_factory=list)  # (source_chain, target_chain)
    format_mappings: List[Tuple[str, str]] = field(default_factory=list)  # (output_fmt, input_fmt)
    param_flows: List[Tuple[str, str]] = field(default_factory=list)     # (output_param, input_param)
    
    # 是否存在潜在循环
    bidirectional: bool = False  # 是否双向都有边（可能形成循环）
    reverse_match: Optional['SkillPairMatch'] = None  # 反向匹配


class PairwiseMatcher:
    """两两技能匹配引擎"""
    
    def __init__(self):
        # 格式兼容性矩阵
        self.format_compatibility = {
            ('json', 'json'): 1.0,
            ('json', 'text'): 0.8,
            ('json', 'element_list'): 0.3,
            ('text', 'text'): 1.0,
            ('text', 'json'): 0.5,
            ('text', 'url'): 0.7,
            ('text', 'file'): 0.6,
            ('image', 'file'): 1.0,
            ('image', 'text'): 0.3,
            ('element_list', 'text'): 0.6,
            ('element_list', 'url'): 0.4,
            ('file', 'text'): 0.8,
            ('file', 'json'): 0.7,
            ('file', 'file'): 1.0,
            ('url', 'text'): 0.9,
            ('url', 'url'): 1.0,
            ('url', 'json'): 0.6,
            ('pdf', 'text'): 0.8,
            ('pdf', 'file'): 0.9,
        }
        
        # 命令链流转模式（哪些输出可以自然地成为哪些输入）
        self.chain_flow_patterns = {
            # snapshot输出element refs → click/fill/type需要@refs
            ('snapshot', 'click'): 0.9,
            ('snapshot', 'fill'): 0.9,
            ('snapshot', 'type'): 0.9,
            ('snapshot', 'get'): 0.85,
            ('snapshot', 'hover'): 0.9,
            ('snapshot', 'check'): 0.85,
            
            # open/navigate → snapshot
            ('open', 'snapshot'): 0.8,
            ('open', 'get'): 0.6,
            
            # get text/html → click/navigate (基于内容发现新链接)
            ('get', 'click'): 0.5,
            ('get', 'open'): 0.4,
            
            # list → get/view
            ('list', 'get'): 0.8,
            ('list', 'view'): 0.9,
            
            # api返回json → 各种处理
            ('api', 'get'): 0.7,
        }
    
    def match_pair(self, source: SkillActionProfile, target: SkillActionProfile) -> SkillPairMatch:
        """评估source的输出是否能作为target的输入"""
        match = SkillPairMatch(
            source_skill=source.skill_name,
            target_skill=target.skill_name
        )
        
        # 1. 输出格式兼容性
        match.format_compatibility = self._calc_format_compatibility(
            source.output_formats, target.input_params, target.command_chains
        )
        
        # 2. 命令链流转可能性
        match.command_chain_flow = self._calc_chain_flow(
            source.command_chains, target.command_chains
        )
        
        # 3. 语义相似度（基于描述和动作重叠）
        match.semantic_similarity = self._calc_semantic_similarity(source, target)
        
        # 4. 参数匹配
        match.param_match_score = self._calc_param_match(source, target)
        
        # 5. 数据实体重叠
        match.data_entity_overlap = self._calc_entity_overlap(source, target)
        
        # 综合分数（加权）
        match.overall_score = (
            0.25 * match.format_compatibility +
            0.25 * match.command_chain_flow +
            0.20 * match.semantic_similarity +
            0.15 * match.param_match_score +
            0.15 * match.data_entity_overlap
        )
        
        return match
    
    def _calc_format_compatibility(self, source_formats: Set[str], 
                                    target_inputs: List[Dict],
                                    target_chains: List[CommandChain]) -> float:
        """计算输出格式兼容性"""
        if not source_formats:
            return 0.0
        
        scores = []
        
        # 检查target接受的输入格式
        target_formats = set()
        for inp in target_inputs:
            target_formats.add(inp.get('type', 'text'))
        
        # 从target的命令链中推断输入格式
        for chain in target_chains:
            if chain.subcommand in ['open', 'navigate']:
                target_formats.add('url')
            if chain.subcommand == 'upload':
                target_formats.add('file')
            if chain.subcommand in ['click', 'fill', 'type'] and any(f.startswith('@') for f in chain.flags):
                target_formats.add('element_ref')
        
        if not target_formats:
            target_formats = {'text'}  # 默认接受text
        
        # 计算格式兼容性
        for src_fmt in source_formats:
            best_score = 0.0
            for tgt_fmt in target_formats:
                key = (src_fmt, tgt_fmt)
                score = self.format_compatibility.get(key, 0.3)
                if score > best_score:
                    best_score = score
            scores.append(best_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calc_chain_flow(self, source_chains: List[CommandChain], 
                         target_chains: List[CommandChain]) -> float:
        """计算命令链之间的流转可能性"""
        if not source_chains or not target_chains:
            return 0.0
        
        max_score = 0.0
        matching_pairs = []
        
        for src in source_chains:
            for tgt in target_chains:
                # 检查直接的流转模式
                flow_key = (src.subcommand, tgt.subcommand)
                if flow_key in self.chain_flow_patterns:
                    score = self.chain_flow_patterns[flow_key]
                    if score > max_score:
                        max_score = score
                    matching_pairs.append((src.description[:30], tgt.description[:30]))
                
                # 检查相同工具的连续使用
                if src.tool == tgt.tool and src.tool in ['agent-browser']:
                    # 同工具连续使用是常见的模式
                    if score < 0.5:
                        score = 0.5
                        if score > max_score:
                            max_score = score
                        matching_pairs.append((src.description[:30], tgt.description[:30]))
        
        return max_score
    
    def _calc_semantic_similarity(self, source: SkillActionProfile, 
                                   target: SkillActionProfile) -> float:
        """计算两个skill的语义相似度"""
        # 基于动作动词重叠
        source_verbs = set(source.action_verbs)
        target_verbs = set(target.action_verbs)
        
        if not source_verbs or not target_verbs:
            return 0.0
        
        intersection = source_verbs & target_verbs
        union = source_verbs | target_verbs
        
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # 基于数据实体重叠
        source_entities = set(source.data_entities)
        target_entities = set(target.data_entities)
        
        if source_entities and target_entities:
            entity_overlap = len(source_entities & target_entities) / len(source_entities | target_entities)
        else:
            entity_overlap = 0.0
        
        return jaccard * 0.6 + entity_overlap * 0.4
    
    def _calc_param_match(self, source: SkillActionProfile, 
                          target: SkillActionProfile) -> float:
        """计算参数匹配度"""
        # source的输出参数是否能匹配target的输入参数
        source_outputs = []
        for chain in source.command_chains:
            if chain.output_format == 'json':
                source_outputs.append(('json_data', 'json'))
            elif chain.output_format == 'text':
                source_outputs.append(('text_output', 'text'))
            elif chain.output_format == 'element_list':
                source_outputs.append(('element_refs', 'element_ref'))
            elif chain.output_format == 'image':
                source_outputs.append(('image_data', 'image'))
        
        if not source_outputs:
            source_outputs = [('result', 'text')]
        
        # 匹配target的输入
        target_inputs = [(p['name'], p.get('type', 'text')) for p in target.input_params]
        if not target_inputs:
            target_inputs = [('input', 'text')]
        
        matches = 0
        for _, src_type in source_outputs:
            for _, tgt_type in target_inputs:
                if src_type == tgt_type or (src_type, tgt_type) in self.format_compatibility:
                    matches += 1
        
        total = len(source_outputs) * len(target_inputs)
        return matches / total if total > 0 else 0.0
    
    def _calc_entity_overlap(self, source: SkillActionProfile, 
                              target: SkillActionProfile) -> float:
        """计算数据实体重叠度"""
        source_entities = set(source.data_entities)
        target_entities = set(target.data_entities)
        
        if not source_entities or not target_entities:
            return 0.0
        
        intersection = source_entities & target_entities
        union = source_entities | target_entities
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_all_pairs(self, profiles: List[SkillActionProfile], 
                       threshold: float = 0.2) -> List[SkillPairMatch]:
        """对所有skill两两匹配"""
        all_matches = []
        
        for i, src in enumerate(profiles):
            for j, tgt in enumerate(profiles):
                if i == j:
                    continue
                
                match = self.match_pair(src, tgt)
                
                if match.overall_score >= threshold:
                    all_matches.append(match)
        
        # 按分数排序
        all_matches.sort(key=lambda m: m.overall_score, reverse=True)
        
        # 检测双向匹配（潜在循环）
        self._detect_bidirectional(all_matches)
        
        return all_matches
    
    def _detect_bidirectional(self, matches: List[SkillPairMatch]):
        """检测双向匹配（可能形成循环）"""
        match_dict = {}
        for m in matches:
            key = (m.source_skill, m.target_skill)
            match_dict[key] = m
        
        for m in matches:
            reverse_key = (m.target_skill, m.source_skill)
            if reverse_key in match_dict:
                m.bidirectional = True
                m.reverse_match = match_dict[reverse_key]


if __name__ == '__main__':
    import sys
    
    # 测试
    parser = EnhancedSkillParser()
    
    test_content = """
name: test-skill
description: A test skill for reading files and outputting JSON

```bash
gh pr checks 55 --repo owner/repo
gh issue list --json number,title
agent-browser snapshot -i
agent-browser click @e1
curl -s "https://api.example.com/data"
```
"""
    
    # 临时测试
    profile = SkillActionProfile(
        skill_name='test',
        description='test skill',
        raw_content=test_content
    )
    profile.command_chains = parser._extract_command_chains(test_content)
    
    print(f"提取了 {len(profile.command_chains)} 条命令链:")
    for chain in profile.command_chains:
        print(f"  {chain.tool} {chain.subcommand} {chain.action} -> {chain.output_format}")
    
    print("\nEnhanced parser test passed!")
