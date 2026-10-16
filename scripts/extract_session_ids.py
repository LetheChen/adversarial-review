#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adversarial-review 辅助脚本：提取 session/thread id + 核对当次真实模型 + 记账。

仅用于 **CLI 子进程执行层**（codex exec / claude -p）。原生 subagent 执行层没有外部会话，
本脚本不适用——那条路径的记账靠 REVIEW 文档里的账本（见 SKILL.md §5）。

用法：
    python extract_session_ids.py <R1-codex.jsonl> [R1-claude.json ...]
    python extract_session_ids.py --help

对每个产物文件自动识别 codex / claude 流：
  - codex  (--json 事件流)       -> thread_id  (resume: codex exec resume <id>)
  - claude (json / stream-json)  -> session_id (resume: claude -p --resume <id>) + 记账
最后读取两家 CLI 当前默认配置 (~/.codex/config.toml、~/.claude/settings.json)，
与流内实际出现的模型交叉校验，双审核方同源或不一致时给出警告（必须写进 REVIEW 元信息）。

同源判定按 **厂商/基座族**（见 model_family），不是字符串精确相等——
MiniMax-M3 与 MiniMax-M3.1-Flash-Preview 字面不等但同源，字面相等会漏检。

解析只处理 '{' 开头的行——天然免疫 stderr 警告混入
（坑清单：[claude-code:unrecognized_model] 行会破坏整体 json.load）。

⚠️ 本脚本的输出会进入 REVIEW 元信息表（SKILL.md §4.4 第 1 项）。
   凡打印 "校验未完成" 的项目，REVIEW 元信息里**不得**声称已核对。
"""
import json
import os
import re
import sys


# --- 厂商/基座族判定：字面相等 != 语义同源 ---------------------------------------
# 顺序有意义：先匹配更具体的族名，避免 'o1' 之类短前缀误伤。
FAMILY_PATTERNS = [
    ('minimax',  ('minimax', 'abab')),
    ('anthropic', ('claude', 'anthropic', 'sonnet', 'opus', 'haiku')),
    ('openai',   ('gpt-', 'gpt3', 'gpt4', 'gpt5', 'openai', 'text-davinci')),
    ('google',   ('gemini', 'gemma', 'bison', 'google/')),
    ('zhipu',    ('glm', 'zhipu', 'chatglm')),
    ('moonshot', ('kimi', 'moonshot')),
    ('alibaba',  ('qwen', 'tongyi', 'dashscope')),
    ('deepseek', ('deepseek',)),
    ('mistral',  ('mistral', 'mixtral')),
    ('meta',     ('llama',)),
]


def model_family(name):
    """返回模型名的厂商/基座族；识别不出返回 None。"""
    if not name:
        return None
    n = str(name).lower()
    for fam, pats in FAMILY_PATTERNS:
        for p in pats:
            if p in n:
                return fam
    return None


def reconfigure_stdout():
    """中文 Windows 控制台默认 GBK，打印 '⚠️' 会抛 UnicodeEncodeError。
    入口先重配一次，errors='replace' 保证任何字符都不会中断脚本。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


def parse_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        raw = f.read()
    objs = []
    try:
        objs.append(json.loads(raw))  # claude --output-format json（整文件）
    except Exception:
        for ln in raw.splitlines():  # stream-json / 混入了 stderr 行
            ln = ln.strip()
            if ln.startswith('{'):
                try:
                    objs.append(json.loads(ln))
                except Exception:
                    pass
    info = {'kind': None, 'id': None, 'model': None, 'cost': 0.0, 'is_error': None}
    for o in objs:
        if not isinstance(o, dict):
            continue
        if o.get('thread_id'):  # codex: thread.started 等事件
            info['kind'] = 'codex'
            info['id'] = info['id'] or o['thread_id']
        t = o.get('type')
        if t in ('system', 'result') and o.get('session_id'):
            info['kind'] = info['kind'] or 'claude'
            info['id'] = info['id'] or o['session_id']
        if t == 'result':
            info['is_error'] = o.get('is_error')
            for v in (o.get('modelUsage') or {}).values():
                info['cost'] += v.get('costUSD') or 0.0
            if not info['model']:  # modelUsage 键可能是 CLI 别名，仅兜底
                for k in (o.get('modelUsage') or {}):
                    info['model'] = k
                    break
        msg = o.get('message')
        if t == 'assistant' and isinstance(msg, dict) and msg.get('model'):
            info['model'] = msg['model']  # stream-json: 网关真实回应，优先级最高
    return info


def codex_default():
    p = os.path.expanduser('~/.codex/config.toml')
    try:
        with open(p, encoding='utf-8', errors='replace') as fh:
            for ln in fh:
                m = re.match(r'\s*model\s*=\s*"([^"]+)"', ln)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return None


def claude_default():
    p = os.path.expanduser('~/.claude/settings.json')
    try:
        with open(p, encoding='utf-8', errors='replace') as fh:
            env = json.load(fh).get('env', {})
        return env.get('ANTHROPIC_DEFAULT_SONNET_MODEL_NAME'), env.get('ANTHROPIC_BASE_URL')
    except Exception:
        return None, None


def main(argv):
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0 if len(argv) > 1 else 1)
    stream_models = {'codex': set(), 'claude': set()}
    for path in argv[1:]:
        print('== %s ==' % path)
        if not os.path.exists(path):
            print('  (文件不存在，跳过)')
            continue
        try:
            i = parse_file(path)
        except Exception as e:
            print('  (解析失败：%s)' % e)
            continue
        if i['kind'] == 'codex':
            print('  thread_id : %s' % i['id'])
            print('  resume    : codex exec resume %s --skip-git-repo-check ...' % i['id'])
        elif i['kind'] == 'claude':
            print('  session_id: %s' % i['id'])
            print('  resume    : claude -p --resume %s ...' % i['id'])
            print('  is_error  : %s   记账: $%.2f（虚拟账单，见 references/pitfalls.md）'
                  % (i['is_error'], i['cost']))
        else:
            print('  (未识别出 session/thread id——确认这是 codex --json 或 claude json/stream-json 产物)')
            continue
        if i['model']:
            stream_models[i['kind']].add(i['model'])
            print('  流内 model: %s' % i['model'])

    cm = codex_default()
    am, base = claude_default()
    print('== 两家 CLI 当前默认配置（开跑前核对） ==')
    print('  codex  : %s' % cm)
    print('  claude : %s @ %s' % (am, base))

    for key, default, cfgpath in (('codex', cm, 'config.toml'), ('claude', am, 'settings.json')):
        if not stream_models[key]:
            print('  [!] %s 流内未取到模型 —— **流内/配置交叉校验未完成**，'
                  'REVIEW 元信息不得声称已核对 %s 实际模型。' % (key, key))
        elif default and default not in stream_models[key]:
            print('  ⚠️ %s 流内实际模型 %s 与 %s 默认 %s 不一致——以流内为准'
                  % (key, sorted(stream_models[key]), cfgpath, default))

    cf, af = model_family(cm), model_family(am)
    if not cm or not am:
        print('  [!] 两家默认配置未全部读到 —— 同源判定未完成，请人工核对。')
    elif cf and af and cf == af:
        print('  ⚠️ 双审核方同源（厂商族 %s）：codex=%s / claude=%s —— '
              'REVIEW 元信息必须声明"双审核方同族，多样性仅来自 harness/提示差异"' % (cf, cm, am))
    elif cm == am:
        print('  ⚠️ 双审核方同源（模型名全同）：%s —— REVIEW 元信息必须声明' % cm)
    elif cf and af:
        print('  ok：厂商族不同（%s vs %s），未见同源。' % (cf, af))
    else:
        print('  [!] 至少一家模型名无法识别厂商族（codex=%s -> %r，claude=%s -> %r）—— '
              '同源判定未完成，请人工核对，REVIEW 元信息不得写"已确认不同源"。'
              % (cm, cf, am, af))


if __name__ == '__main__':
    reconfigure_stdout()
    main(sys.argv)
