"""
模块 4.1: 神经符号技能图谱构建 (Neuro-symbolic Skill Graph Construction)

本模块实现论文4.1节描述的双平面神经符号特征提取引擎。
将异构的第三方技能拆解为细粒度的参数约束与行为意图，
并在全局视角下构建出精确的"有向循环依赖图(UDG)"。

核心功能：
- 解析Skill的SKILL.md文件，提取输入输出约束
- 使用sentence-transformers对技能描述进行语义向量化
- 构建标准化的动作约束元组 T_i = <I_i, O_i, V_i>
- 为后续的多技能组合分析提供形式化基础

安全声明：本代码仅用于安全研究和红队测试，旨在帮助开发者识别
和修复智能体系统中的潜在组合漏洞。
"""

import os
import re
import ast
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    HAS_SBERT = True
except ImportError:
    HAS_SBERT = False
    print("[WARN] sentence-transformers未安装，使用替代向量表示")


@dataclass
class ActionConstraint:
    """动作约束元组中的参数约束
    
    对应论文中的 I_i (输入约束) 和 O_i (输出约束)
    通过对技能底层执行脚本进行AST静态解析得出
    """
    name: str
    param_type: str  # 'string', 'number', 'boolean', 'json', 'file', 'url', 'unknown'
    required: bool = True
    description: str = ""
    schema: Optional[Dict] = None  # JSON Schema if available
    
    def __hash__(self):
        return hash((self.name, self.param_type, self.required))


@dataclass
class CommandChain:
    """命令链 - 论文中的 C_i 字段
    
    表示技能隐式调用的底层物理执行流
    例如: gh pr checks, agent-browser snapshot, curl -s
    """
    tool: str           # 顶层工具 (gh, agent-browser, curl)
    subcommand: str     # 子命令 (pr, snapshot, open)
    action: str         # 具体动作 (checks, -i, <url>)
    flags: List[str] = field(default_factory=list)
    output_format: str = "text"
    description: str = ""


@dataclass
class SkillNode:
    """技能节点 - 对应论文中的状态转移节点
    
    每个技能 s_i 被映射为一个严谨的动作约束元组:
    T_i = <I_i, O_i, C_i, V_i>
    
    其中:
    - I_i: 强类型输入约束列表
    - O_i: 输出数据结构列表
    - C_i: 底层物理命令链列表
    - V_i: 语义表征向量 (R^d)
    """
    skill_id: str
    name: str
    description: str
    source_file: str
    
    # 动作约束元组
    inputs: List[ActionConstraint] = field(default_factory=list)   # I_i
    outputs: List[ActionConstraint] = field(default_factory=list)  # O_i
    command_chains: List[CommandChain] = field(default_factory=list)  # C_i
    semantic_vector: Optional[np.ndarray] = None  # V_i ∈ R^d
    
    # 原始内容
    raw_content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 提取的动作关键词（用于图谱构建）
    action_verbs: List[str] = field(default_factory=list)
    data_entities: List[str] = field(default_factory=list)
    
    def get_vector_dim(self) -> int:
        if self.semantic_vector is not None:
            return len(self.semantic_vector)
        return 0


class SemanticEncoder:
    """语义编码器 - 将技能的自然语言文档映射到高维空间向量
    
    使用本地 BGE-M3 模型进行向量化映射。
    如果没有安装 sentence-transformers，则使用基于关键词的简单替代方案。
    """

    def __init__(self, local_model_path: str = r'C:\Users\lenovo\Desktop\论文\Kimi_Agent_循环检测与优化\rci-sg\models\BAAI\bge-m3'):
        self.model = None
        self.model_path = local_model_path
        if HAS_SBERT:
            try:
                # 重新导入确保在HAS_SBERT为True时可用
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(local_model_path)
                print(f"[INFO] 已加载本地 BGE-M3 模型，路径: {local_model_path}")
            except Exception as e:
                import traceback
                print(f"[WARN] 无法加载模型: {type(e).__name__}: {e}")
                traceback.print_exc()
        else:
            print("[WARN] sentence-transformers未安装，使用降级向量表示")

    def encode(self, text: str) -> np.ndarray:
        """将文本编码为语义向量"""
        if self.model is not None:
            return self.model.encode(text, normalize_embeddings=True)
        else:
            # 降级方案：基于关键词的确定性哈希向量
            return self._fallback_encode(text)

    def _fallback_encode(self, text: str) -> np.ndarray:
        """降级编码方案 - 基于关键词的确定性哈希向量"""
        text_lower = text.lower()

        # 关键词类别
        action_patterns = [
            r'\b(get|fetch|retrieve|read|write|create|update|delete|search|find|parse|convert|transform|generate|analyze|process|send|receive|download|upload|list|show|display)\b',
            r'\b(data|file|json|text|image|video|audio|url|api|request|response|input|output|result|content|document|message)\b',
            r'\b(user|system|server|client|database|web|cloud|local|remote|external|internal)\b',
        ]

        dim = 1024  # BGE-M3 的输出维度为 1024
        vector = np.zeros(dim)

        for pattern in action_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                hash_val = int(hashlib.md5(match.encode()).hexdigest(), 16)
                pos = hash_val % dim
                vector[pos] += 1.0

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector


class SkillGraphBuilder:
    """神经符号技能图谱构建器

    实现论文4.1节描述的双平面神经符号特征提取引擎：
    1. 符号层面：通过AST静态解析提取输入输出约束
    2. 神经层面：通过语义编码器获取高维向量表征

    将异构的非结构化技能转化为标准化的状态转移节点。
    """

    def __init__(self, model_path: str = r'C:\Users\lenovo\Desktop\论文\Kimi_Agent_循环检测与优化\rci-sg\models\BAAI\bge-m3'):
        self.encoder = SemanticEncoder(model_path)
        self.nodes: Dict[str, SkillNode] = {}

        # 动作动词词典（用于符号分析）
        self.action_keywords = {
            'read', 'write', 'get', 'fetch', 'retrieve', 'create', 'update', 'delete',
            'search', 'find', 'query', 'parse', 'convert', 'transform', 'generate',
            'analyze', 'process', 'send', 'receive', 'download', 'upload', 'list',
            'show', 'display', 'render', 'extract', 'filter', 'sort', 'merge',
            'split', 'compress', 'decompress', 'encode', 'decode', 'format',
            'validate', 'verify', 'check', 'scan', 'monitor', 'notify', 'report',
            'summarize', 'translate', 'synthesize', 'execute', 'run', 'call',
            'invoke', 'trigger', 'schedule', 'cancel', 'retry', 'loop', 'iterate'
        }

        # 数据实体词典
        self.data_keywords = {
            'file', 'json', 'xml', 'csv', 'text', 'string', 'number', 'boolean',
            'image', 'video', 'audio', 'url', 'uri', 'path', 'api', 'request',
            'response', 'input', 'output', 'result', 'data', 'content', 'document',
            'message', 'email', 'notification', 'log', 'record', 'entry', 'item',
            'list', 'array', 'object', 'map', 'dictionary', 'set', 'stream',
            'buffer', 'cache', 'database', 'table', 'schema', 'template'
        }

    def parse_skill_file(self, skill_path: str) -> Optional[SkillNode]:
        """解析单个Skill文件，提取动作约束元组"""
        path = Path(skill_path)

        if not path.exists():
            print(f"[ERROR] Skill文件不存在: {skill_path}")
            return None

        # 读取SKILL.md
        skill_md_path = path / "SKILL.md" if path.is_dir() else path
        if not skill_md_path.exists():
            # 尝试查找任何.md文件
            md_files = list(path.glob("*.md")) if path.is_dir() else []
            if md_files:
                skill_md_path = md_files[0]
            else:
                print(f"[ERROR] 未找到SKILL.md: {skill_path}")
                return None

        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[ERROR] 读取文件失败: {e}")
            return None

        # 解析元数据
        metadata = self._extract_metadata(content)

        # 提取动作约束
        inputs, outputs = self._extract_io_constraints(content)

        # 提取命令链 (C_i) - 使用AST解析脚本文件
        command_chains = self._extract_command_chains(content, skill_dir=path if path.is_dir() else None)

        # 提取动作关键词和数据实体
        action_verbs = self._extract_action_verbs(content)
        data_entities = self._extract_data_entities(content)

        # 生成语义向量
        semantic_text = f"{metadata.get('description', '')}. "
        semantic_text += f"Actions: {', '.join(action_verbs)}. "
        semantic_text += f"Data: {', '.join(data_entities)}. "
        semantic_text += content[:500]

        semantic_vector = self.encoder.encode(semantic_text)

        # 构建节点ID
        skill_name = metadata.get('name', path.name)
        skill_id = f"skill_{skill_name}_{hashlib.md5(str(path).encode()).hexdigest()[:8]}"

        node = SkillNode(
            skill_id=skill_id,
            name=skill_name,
            description=metadata.get('description', ''),
            source_file=str(skill_md_path),
            inputs=inputs,
            outputs=outputs,
            command_chains=command_chains,
            semantic_vector=semantic_vector,
            raw_content=content[:2000],
            metadata=metadata,
            action_verbs=action_verbs,
            data_entities=data_entities
        )

        self.nodes[skill_id] = node
        print(f"[INFO] 已解析技能节点: {skill_name} (ID: {skill_id})")
        print(f"       输入约束: {len(inputs)}, 输出约束: {len(outputs)}, "
              f"命令链: {len(command_chains)}, 语义维度: {len(semantic_vector)}")

        return node

    def parse_skill_directory(self, directory: str) -> List[SkillNode]:
        """解析目录下的所有Skill"""
        dir_path = Path(directory)
        nodes = []

        if not dir_path.exists():
            print(f"[ERROR] 目录不存在: {directory}")
            return nodes

        # 查找所有包含SKILL.md的目录
        for skill_dir in dir_path.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    node = self.parse_skill_file(str(skill_dir))
                    if node:
                        nodes.append(node)

        print(f"\n[INFO] 共解析 {len(nodes)} 个技能节点")
        return nodes

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """提取YAML frontmatter元数据"""
        metadata = {}

        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            for key in ['name', 'description', 'version', 'author', 'license']:
                pattern = rf'{key}:\s*(.+?)(?:\n|$)'
                match = re.search(pattern, yaml_content, re.IGNORECASE)
                if match:
                    metadata[key] = match.group(1).strip()

        if 'description' not in metadata:
            para_match = re.search(r'\n\n([^#\n].{50,500})\n', content)
            if para_match:
                metadata['description'] = para_match.group(1).strip()

        return metadata

    def _extract_io_constraints(self, content: str) -> Tuple[List[ActionConstraint], List[ActionConstraint]]:
        """提取输入输出约束（符号层面分析）"""
        inputs = []
        outputs = []

        input_patterns = [
            r'`([^`]+)`\s*\(input\)',
            r'[Ii]nput:\s*`?([^`\n]+)`?',
            r'(?:参数|输入|argument|parameter)\s*[:：]\s*`?([^`\n]+)`?',
            r'(?:takes|accepts|requires)\s+`?([^`\n]+?)`?\s*(?:as|for)',
            r'--([a-zA-Z-]+)\s+(?:<[^>]+>|"[^"]*"|\S+)',
            r'\$([A-Z_]+)',
        ]

        output_patterns = [
            r'`([^`]+)`\s*\(output\)',
            r'[Oo]utput:\s*`?([^`\n]+)`?',
            r'(?:输出|返回|returns|outputs?|produces?)\s*[:：]\s*`?([^`\n]+)`?',
            r'(?:returns|outputs?|generates?|produces?)\s+(?:a|an|the)?\s*`?([^`\n]{5,100})`?',
        ]

        type_hints = {
            'url': 'url', 'uri': 'url', 'http': 'url', 'endpoint': 'url',
            'file': 'file', 'path': 'file', 'directory': 'file', 'folder': 'file',
            'json': 'json', 'xml': 'json', 'csv': 'json', 'yaml': 'json',
            'text': 'string', 'string': 'string', 'str': 'string',
            'number': 'number', 'int': 'number', 'integer': 'number', 'float': 'number',
            'bool': 'boolean', 'boolean': 'boolean', 'flag': 'boolean',
        }

        seen_inputs = set()
        for pattern in input_patterns:
            for match in re.finditer(pattern, content):
                param_name = match.group(1).strip()
                if param_name in seen_inputs or len(param_name) > 50:
                    continue
                seen_inputs.add(param_name)

                param_type = 'unknown'
                param_lower = param_name.lower()
                for hint, ptype in type_hints.items():
                    if hint in param_lower:
                        param_type = ptype
                        break

                inputs.append(ActionConstraint(
                    name=param_name,
                    param_type=param_type,
                    required=True,
                    description=f"Extracted input parameter: {param_name}"
                ))

        seen_outputs = set()
        for pattern in output_patterns:
            for match in re.finditer(pattern, content):
                output_name = match.group(1).strip()
                if output_name in seen_outputs or len(output_name) > 50:
                    continue
                seen_outputs.add(output_name)

                output_type = 'unknown'
                out_lower = output_name.lower()
                for hint, ptype in type_hints.items():
                    if hint in out_lower:
                        output_type = ptype
                        break

                outputs.append(ActionConstraint(
                    name=output_name,
                    param_type=output_type,
                    required=True,
                    description=f"Extracted output: {output_name}"
                ))

        if not inputs:
            inputs.append(ActionConstraint(
                name="context",
                param_type="string",
                required=True,
                description="Default input: execution context"
            ))
        if not outputs:
            outputs.append(ActionConstraint(
                name="result",
                param_type="string",
                required=True,
                description="Default output: execution result"
            ))

        return inputs, outputs

    def _extract_action_verbs(self, content: str) -> List[str]:
        """提取动作动词"""
        verbs = []
        content_lower = content.lower()

        code_blocks = re.findall(r'```\w*\n(.*?)```', content, re.DOTALL)
        for block in code_blocks:
            commands = re.findall(r'^(?:\$\s*)?([a-zA-Z][a-zA-Z0-9_-]+)', block, re.MULTILINE)
            verbs.extend(commands)

        for keyword in self.action_keywords:
            if keyword in content_lower:
                verbs.append(keyword)

        return list(set(verbs))

    def _extract_data_entities(self, content: str) -> List[str]:
        """提取数据实体"""
        entities = []
        content_lower = content.lower()

        for keyword in self.data_keywords:
            if keyword in content_lower:
                entities.append(keyword)

        urls = re.findall(r'https?://[^\s\)]+', content)
        for url in urls:
            domain_match = re.search(r'https?://([^/]+)', url)
            if domain_match:
                entities.append(domain_match.group(1))

        return list(set(entities))

    def _extract_command_chains(self, content: str, skill_dir: Optional[Path] = None) -> List[CommandChain]:
        """提取命令链 C_i - 基于AST的底层物理执行流分析（论文4.1节要求）
        
        实现论文要求的：对底层执行脚本（如 Python 或 Bash）进行深度抽象语法树（AST）解析
        
        流程：
        1. 扫描技能目录，找到所有 .py/.sh/.js 脚本文件
        2. 对 Python 脚本使用 ast 模块进行AST解析
        3. 对 Bash 脚本使用结构化解析
        4. 对 JavaScript 脚本使用正则提取
        5. 从 SKILL.md 的 markdown 代码块中提取命令（降级方案）
        """
        chains = []
        
        if skill_dir is not None and skill_dir.exists():
            python_files = list(skill_dir.rglob("*.py"))
            bash_files = list(skill_dir.rglob("*.sh"))
            js_files = list(skill_dir.rglob("*.js")) + list(skill_dir.rglob("*.mjs"))
            
            for py_file in python_files:
                chains.extend(self._parse_python_ast(py_file))
            
            for sh_file in bash_files:
                chains.extend(self._parse_bash_script(sh_file))
            
            for js_file in js_files:
                chains.extend(self._parse_javascript(js_file))
        
        if not chains:
            chains.extend(self._extract_from_markdown(content))
        
        return chains
    
    def _parse_python_ast(self, filepath: Path) -> List[CommandChain]:
        """使用Python ast模块对Python脚本进行AST静态解析
        
        提取以下AST节点：
        - FunctionDef/AsyncFunctionDef: 函数定义
        - Call: 函数调用（subprocess.run, requests.get, os.system等）
        - Import/ImportFrom: 导入的模块
        - Assign: 赋值语句（包含命令字符串）
        """
        chains = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception:
            return chains
        
        try:
            tree = ast.parse(source_code, filename=str(filepath))
        except SyntaxError:
            return chains
        
        subprocess_tools = {'subprocess', 'os', 'sys', 'shutil', 'requests', 'urllib'}
        command_execution_funcs = {
            ('subprocess', 'run'), ('subprocess', 'call'), ('subprocess', 'Popen'),
            ('subprocess', 'check_output'), ('subprocess', 'check_call'),
            ('os', 'system'), ('os', 'popen'), ('os', 'exec'),
            ('shutil', 'copy'), ('shutil', 'move'), ('shutil', 'rmtree'),
            ('requests', 'get'), ('requests', 'post'), ('requests', 'put'),
            ('requests', 'delete'), ('requests', 'patch'),
            ('urllib', 'request'), ('urllib', 'urlopen'),
        }
        
        imported_modules = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules[alias.name] = alias.asname or alias.name
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for alias in node.names:
                        imported_modules[f"{node.module}.{alias.name}"] = alias.asname or alias.name
            
            elif isinstance(node, ast.Call):
                chain = self._extract_python_call(node, source_code, imported_modules, command_execution_funcs)
                if chain:
                    chains.append(chain)
        
        return chains
    
    def _extract_python_call(self, node: ast.Call, source: str, imports: Dict, exec_funcs: Set) -> Optional[CommandChain]:
        """从Python AST Call节点提取CommandChain"""
        func_name = None
        
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func.value, ast.Attribute):
                if isinstance(node.func.value.value, ast.Name):
                    func_name = f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
        
        if not func_name:
            return None
        
        is_exec_call = False
        for module, func in exec_funcs:
            if func_name.startswith(module) and func in func_name:
                is_exec_call = True
                break
        
        if not is_exec_call:
            if any(mod in func_name for mod in {'subprocess', 'os.system', 'requests'}):
                is_exec_call = True
        
        if not is_exec_call:
            return None
        
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                args.append(arg.value)
            elif isinstance(arg, ast.List):
                for elt in arg.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        args.append(elt.value)
        
        for keyword in node.keywords:
            if keyword.arg in {'args', 'command', 'cmd', 'url', 'data'}:
                if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    args.append(keyword.value.value)
                elif isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            args.append(elt.value)
        
        if not args:
            return None
        
        cmd_line = ' '.join(str(a) for a in args[:5])
        parts = cmd_line.split()
        
        return CommandChain(
            tool=parts[0] if parts else func_name,
            subcommand=parts[1] if len(parts) > 1 else "",
            action=parts[2] if len(parts) > 2 else "",
            flags=[p for p in parts if p.startswith('-') or p.startswith('--')],
            output_format='text',
            description=f"[AST] {func_name}: {cmd_line[:80]}"
        )
    
    def _parse_bash_script(self, filepath: Path) -> List[CommandChain]:
        """解析Bash脚本，提取命令链"""
        chains = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            return chains
        
        known_tools = {'gh', 'agent-browser', 'curl', 'npx', 'npm', 'git', 'python', 'node', 
                      'wget', 'docker', 'kubectl', 'aws', 'gcloud', 'az', 'ssh', 'scp', 'rsync'}
        output_format_patterns = {
            '--json': 'json', '-json': 'json', '--format json': 'json',
            '--output-format json': 'json', '--jq': 'json',
            '-o': 'file', '--output': 'file',
            '.png': 'image', '.jpg': 'image', '.pdf': 'pdf',
            '--yaml': 'yaml', '--csv': 'csv', '--xml': 'xml',
            '--text': 'text', '--html': 'html',
        }
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            line = re.sub(r'^\$\s*', '', line)
            
            parts = line.split()
            if not parts:
                continue
            
            tool = parts[0]
            if tool in known_tools or any(tool.endswith(f"/{t}") for t in known_tools):
                subcommand = parts[1] if len(parts) > 1 else ""
                action = parts[2] if len(parts) > 2 else ""
                flags = [p for p in parts if p.startswith('-') or p.startswith('--')]
                
                output_format = 'text'
                line_lower = line.lower()
                for flag, fmt in output_format_patterns.items():
                    if flag in flags or flag in line_lower:
                        output_format = fmt
                        break
                
                chains.append(CommandChain(
                    tool=tool,
                    subcommand=subcommand,
                    action=action,
                    flags=flags,
                    output_format=output_format,
                    description=f"[Bash] {line[:80]}"
                ))
        
        return chains
    
    def _parse_javascript(self, filepath: Path) -> List[CommandChain]:
        """解析JavaScript脚本，提取命令链"""
        chains = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return chains
        
        # 1. child_process 调用
        child_process_patterns = [
            r'(?:child_process|spawn|exec|execFile|run)\s*\(\s*["\']([^"\']+)["\']',
            r'(?:execSync|execa|shelljs)\s*\(\s*["\']([^"\']+)["\']',
            r'process\.spawn\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in child_process_patterns:
            for match in re.finditer(pattern, content):
                cmd = match.group(1)
                parts = cmd.split()
                chains.append(CommandChain(
                    tool=parts[0] if parts else "node",
                    subcommand=parts[1] if len(parts) > 1 else "",
                    action=parts[2] if len(parts) > 2 else "",
                    flags=[p for p in parts if p.startswith('-') or p.startswith('--')],
                    output_format='text',
                    description=f"[JS] {cmd[:80]}"
                ))
        
        # 2. require 导入
        require_pattern = r'(?:const|let|var)\s+\w+\s*=\s*require\s*\(\s*["\']([^"\']+)["\']\s*\)'
        for match in re.finditer(require_pattern, content):
            module_name = match.group(1)
            if any(t in module_name for t in {'child_process', 'execa', 'shelljs', 'cross-spawn'}):
                chains.append(CommandChain(
                    tool="node",
                    subcommand="require",
                    action=module_name,
                    flags=[],
                    output_format='text',
                    description=f"[JS Import] {module_name}"
                ))
        
        # 3. CLI 命令结构提取（从 case/switch 或 CLI 入口解析命令）
        filename = filepath.stem
        
        # 从 switch case 语句提取 CLI 子命令
        case_pattern = r"case\s+['\"](\w+)['\"]:"
        case_commands = re.findall(case_pattern, content)
        
        if case_commands:
            for cmd in case_commands:
                if cmd not in {'default'}:
                    chains.append(CommandChain(
                        tool="node",
                        subcommand=f"{filename}.js",
                        action=cmd,
                        flags=[],
                        output_format='text',
                        description=f"[JS CLI] node {filename}.js {cmd}"
                    ))
        
        # 从 process.argv 或 console.log 中的 usage 提取命令
        usage_pattern = r"(?:node\s+)?(\w+\.js)\s+(add|remove|list|check|get|create|delete|update|search|fetch|parse|run|start|stop)\b"
        for match in re.finditer(usage_pattern, content, re.IGNORECASE):
            script_name = match.group(1)
            subcommand = match.group(2).lower()
            cmd_key = f"node {script_name} {subcommand}"
            if not any(c.action == subcommand and c.subcommand == script_name for c in chains):
                chains.append(CommandChain(
                    tool="node",
                    subcommand=script_name,
                    action=subcommand,
                    flags=[],
                    output_format='text',
                    description=f"[JS Usage] {cmd_key}"
                ))
        
        return chains
    
    def _extract_from_markdown(self, content: str) -> List[CommandChain]:
        """从 SKILL.md 的 markdown 代码块中提取命令链（降级方案）"""
        chains = []
        known_tools = {'gh', 'agent-browser', 'curl', 'npx', 'npm', 'git', 'python', 'node'}
        output_format_patterns = {
            '--json': 'json', '-json': 'json', '--format json': 'json',
            '--output-format json': 'json', '--jq': 'json',
            '-o': 'file', '--output': 'file',
            '.png': 'image', '.jpg': 'image', '.pdf': 'pdf',
            '--yaml': 'yaml', '--csv': 'csv', '--xml': 'xml',
            '--text': 'text', '--html': 'html',
        }
        
        bash_blocks = re.findall(r'```bash\n(.*?)```', content, re.DOTALL)
        for block in bash_blocks:
            for line in block.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                line = re.sub(r'^\$\s*', '', line)
                parts = line.split()
                if len(parts) < 1:
                    continue
                tool = parts[0]
                if tool not in known_tools:
                    continue
                
                subcommand = parts[1] if len(parts) > 1 else ""
                action = parts[2] if len(parts) > 2 else ""
                flags = [p for p in parts if p.startswith('-') or p.startswith('--')]
                
                output_format = 'text'
                line_lower = line.lower()
                for flag, fmt in output_format_patterns.items():
                    if flag in flags or flag in line_lower:
                        output_format = fmt
                        break
                
                chains.append(CommandChain(
                    tool=tool,
                    subcommand=subcommand,
                    action=action,
                    flags=flags,
                    output_format=output_format,
                    description=line[:100]
                ))
        
        return chains

    def get_all_nodes(self) -> Dict[str, SkillNode]:
        return self.nodes

    def get_node_vector_matrix(self) -> Tuple[List[str], np.ndarray]:
        skill_ids = list(self.nodes.keys())
        vectors = [self.nodes[sid].semantic_vector for sid in skill_ids]

        if not vectors:
            return [], np.array([])

        matrix = np.vstack(vectors)
        return skill_ids, matrix

    def compute_semantic_similarity(self, node_a: SkillNode, node_b: SkillNode) -> float:
        if node_a.semantic_vector is None or node_b.semantic_vector is None:
            return 0.0

        vec_a = node_a.semantic_vector.reshape(1, -1)
        vec_b = node_b.semantic_vector.reshape(1, -1)

        sim = cosine_similarity(vec_a, vec_b)[0][0]
        return float(sim)

    def export_graph_data(self, output_path: str):
        graph_data = {
            'nodes': [],
            'metadata': {
                'total_nodes': len(self.nodes),
                'encoder_type': 'sentence-transformers' if HAS_SBERT else 'fallback',
                'version': '1.0.0'
            }
        }

        for skill_id, node in self.nodes.items():
            node_data = {
                'skill_id': skill_id,
                'name': node.name,
                'description': node.description[:200],
                'inputs': [{'name': i.name, 'type': i.param_type} for i in node.inputs],
                'outputs': [{'name': o.name, 'type': o.param_type} for o in node.outputs],
                'command_chains': [
                    {'tool': c.tool, 'subcommand': c.subcommand, 'action': c.action, 
                     'flags': c.flags, 'format': c.output_format}
                    for c in node.command_chains
                ],
                'action_verbs': node.action_verbs,
                'data_entities': node.data_entities,
            }
            graph_data['nodes'].append(node_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)

        print(f"[INFO] 图谱数据已导出: {output_path}")





if __name__ == '__main__':
    # 单元测试
    import tempfile
    
    # 创建测试Skill
    test_skill_content = """---
name: test-skill
description: A test skill for reading files and outputting JSON data
---

# Test Skill

This skill reads files from a directory and outputs structured JSON data.

## Usage

Input: `file_path` (string) - Path to the file
Output: `json_data` (JSON) - Parsed file content

```bash
python read_file.py --input /path/to/file --format json
```

The skill processes text files and converts them to JSON format.
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / 'test-skill'
        skill_dir.mkdir()
        (skill_dir / 'SKILL.md').write_text(test_skill_content)
        
        builder = SkillGraphBuilder()
        node = builder.parse_skill_file(str(skill_dir))
        
        assert node is not None
        assert node.name == 'test-skill'
        assert len(node.inputs) > 0
        assert len(node.outputs) > 0
        assert node.semantic_vector is not None
        print("\n[PASS] SkillGraphBuilder 单元测试通过!")
