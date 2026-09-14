#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adversarial-review-panel 辅助脚本：提取 session/thread id + 核对当次真实模型 + 记账。

用法：
    python extract_session_ids.py <R1-codex.jsonl> [R1-claude.json ...]

对每个产物文件自动识别 codex / claude 流：
  - codex  (--json 事件流)       -> thread_id  (resume: codex exec resume <id>)
  - claude (json / stream-json)  -> session_id (resume: claude -p --resume <id>) + 记账
最后读取两家 CLI 当前默认配置 (~/.codex/config.toml、~/.claude/settings.json)，
与流内实际出现的模型交叉校验，双审核方同源或不一致时给出警告（必须写进 REVIEW 元信息）。

解析只处理 '{' 开头的行——天然免疫 stderr 警告混入
（坑清单：[claude-code:unrecognized_model] 行会破坏整体 json.load）。
"""
import json
import os
import re
import sys


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


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    stream_models = {'codex': set(), 'claude': set()}
    for path in sys.argv[1:]:
        print('== %s ==' % path)
        if not os.path.exists(path):
            print('  (文件不存在，跳过)')
            continue
        try:
            i = parse_file(path)
        except Exception as e:
            print('  (解析失败，跳过: %s)' % e)
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
    if cm and stream_models['codex'] and cm not in stream_models['codex']:
        print('  ⚠️ codex 流内实际模型 %s 与 config.toml 默认 %s 不一致——以流内为准'
              % (sorted(stream_models['codex']), cm))
    if am and stream_models['claude'] and am not in stream_models['claude']:
        print('  ⚠️ claude 流内实际模型 %s 与 settings.json 默认 %s 不一致——以流内为准'
              % (sorted(stream_models['claude']), am))
    if cm and am and cm == am:
        print('  ⚠️ 双审核方同源：%s —— REVIEW 元信息必须声明'
              '"双审核方同源，多样性仅来自 harness/提示差异"' % cm)


if __name__ == '__main__':
    main()
