# 坑清单与实测真相（按需参考）

> 本文件是 adversarial-review-panel 的参考层：命令报错、结果异常、首次在新机器跑、或需要成本/模型/会话细节时才读。SKILL.md 只保留了决策规则。
> 注：下文示例含内部代号/文件名/函数名（教学案例保留）；**IP 与凭据已脱敏**，端点仅保留公开地址（来源：codex 红队建议）。

## 1. 会话定位与续接（本机实测）

| 问题                                  | 答案                                                    |
| ----------------------------------- | ----------------------------------------------------- |
| claude code / codex 是不是**一次性**审核任务？ | **不是**。两者都有会话持久化 + 原生 resume                          |
| 能不能**回复到原 session**？                | **能续接，但没有推送通道**——必须由主持人显式发起下一轮，把 brief 作为新 prompt 投进去 |
| 给审核方发全文还是路径？                        | **只给路径 + 要点**。文件路径是唯一真源，避免版本漂移；同时省 token              |

| <br />         | codex                                                                                                  | claude                                                                    |
| -------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| 会话落盘位置         | `~/.codex/sessions/YYYY/MM/DD/rollout-<时间>-<UUID>.jsonl`                                               | `~/.claude/projects/<cwd编码，如 E--GitHub-myproject>/<session_id>.jsonl`     |
| session id 从哪取 | 流里的 `{"type":"thread.started","thread_id":"<UUID>"}`；或从 rollout 文件名里取 UUID                             | 流里 `system/init` 的 `session_id`；或 `--output-format json` 的顶层 `session_id` |
| 续接命令           | `codex exec resume <UUID> [PROMPT]`（`--last` 取最近）                                                      | `claude -p --resume <session_id> [PROMPT]`（`-c` 取当前目录最近）                  |
| 续接时的约束         | ⚠️ **resume 没有 `-C`，也没有 `-s`** → 必须先 `cd` 到项目根；沙箱策略**继承原 session**（原来 read-only 就还是 read-only） | 参数与首次一致即可                                                                 |
| 上下文成本          | 命中缓存后极便宜（实测一次 resume：12.95M input，其中 12.59M 是 cached）                                                  | ⚠️ **本机无提示缓存**（`cache_read_input_tokens` 恒 0）→ 每轮重发全部上下文，turn 越多越贵        |

（提取 id / 查模型 / 记账一键化：`python scripts/extract_session_ids.py <产物文件...>`）

## 2. 审核方身份与"成本"真相（务必先查）

**别信 CLI 的模型标签，去流里看** **`message.model`。** 本机实测：

```jsonc
// ~/.claude/settings.json（示例结构：第三方 Anthropic 兼容端点；真实值以你本机为准）
"env": {
  "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",   // ← 第三方兼容端点示例（公开地址、非机密；也可能换成内网网关），不是 api.anthropic.com
  "ANTHROPIC_AUTH_TOKEN": "<你的凭据——绝不写入任何文档/报告>",
  "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "MiniMax-M3"           // ← 所有别名都落到这个模型
}
```

⚠️ **示例值是历史快照，不是常量**：`settings.json` 会被用户主动切换——实测同一天内，早上还是内网 vLLM 网关的 `qwen3.8-flash`，下午已切到 `https://api.minimaxi.com/anthropic` 的 `MiniMax-M3`（与 codex 同模型）。**每次开跑前重查** env 指向 + 流里 `message.model`，拿当次事实说话。

后果（三条都很关键）：

1. **"claude code" 实际跑的可能不是 Anthropic Claude**，而是网关上的某个模型（流里 `"model":"..."` 是网关真实回应；`modelUsage.claude-sonnet-5` 只是 CLI 的本地别名）。**写 REVIEW 文档时必须如实标注真实模型**，否则"三方独立"是假的。
2. **`total_cost_usd`** **是客户端按价目表估的虚拟账单，不是真实扣费**（内网网关/第三方端点不按 Anthropic 价目计费）。但它会**真的触发中断**：实测 `--max-budget-usd 5` 在 7 分 22 秒 / 32 轮时以 `terminal_reason:"budget_exhausted"` 掐断任务，取证做了一半。
3. **网关通常不实现** **`cache_control`** → 提示缓存恒不命中 → 每轮重发全量上下文。32 轮烧掉 1.52M input tokens 就是这么来的。

**因此**：

- `--max-budget-usd` 在本机应视为"防跑飞的轮次闸门"，不是精确预算。要么给宽（如 40），要么省略；**给 5 这种照真实计价设的值一定会拦腰截断**。
- 中断后**不要从头重跑**：会话上下文都在，用 `--resume <session_id>` + 模板 D 收口指令把已有进度转成报告，成本远低于重跑。
- 独立性检查：若审核方模型**与被审系统自用模型同源**，必须在报告里注明"该审核方与被审系统共用模型来源，独立性打折"。**同理：两个审核方互相同源也要声明**——用户切换 provider 后 claude 通道与 codex 通道可同落 `MiniMax-M3`，此时"两方审查"的模型多样性不存在，分歧只剩 harness/提示词差异，REVIEW 元信息必须写"双审核方同源（模型 X）"。
- **防泄漏规矩**：REVIEW 元信息只记"真实模型名 + 端点类型（官方 / 第三方 / 内网）"三选一，**绝不记内网地址、base URL 里的凭据、token 明文**——REVIEW 文档可能被分享或入库。

## 3. 成本实测基线

claude 侧 32 轮 / 7 分 22 秒 → 1.52M input tokens、CLI 记账 $5.28（虚拟值）。**换算约每分钟 $0.72**。所以一次完整的 30 分钟级审查，在不调闸门的情况下会被 CLI 记到 $20 量级 —— 这是**记账数字，不是真实扣费**，但足以让你误判预算。另有**成本底噪**：claude 每次调用约 **$0.14 / 23k input tokens**（系统提示 + 项目 CLAUDE.md），与任务大小无关。

## 4. 中途诊断"真干活 vs 空转"

看工具调用是否持续换文件/换 SQL。codex 看 `item.completed` 的 `command_execution`；claude 看 `assistant` 消息里的 `tool_use`（`"type":"assistant"` 的 `message.content[]`）。
⚠️ **不要用 TaskOutput 看内容**：stdout 已重定向到文件，TaskOutput 只会显示 `(no output)` —— 去读那个文件。

## 5. 完整坑清单（实测）

| 坑                                                         | 现象                                                                                                                                                | 对策                                                                                                         |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **claude 的 shell 工具叫** **`PowerShell`** **不是** **`Bash`** | 白名单只写 `Bash` → 所有命令被拒（`permission_denials: [{'tool_name':'PowerShell'}]`），它会回答"权限被拒绝"并**凭记忆猜答案**                                                  | 白名单必须含 `PowerShell`（保留 `Bash` 兼容）                                                                          |
| **Bash 工具守卫拦字面量** **`PowerShell`**                        | 命令直接报 `Command blocked for security: Invoking PowerShell from Bash...`                                                                            | 用变量拼接：`PS_TOOL=$(printf 'Power%s' 'Shell')`                                                                |
| 长中文 prompt 走命令行参数                                         | 截断/乱码                                                                                                                                             | 两家都写文件 + stdin（`cat f \| claude -p` / `- < f`）                                                             |
| codex `exec resume` **没有** **`-C`** **/** **`-s`**        | 以为能像首次一样指定工作根/沙箱                                                                                                                                  | 先 `cd` 到项目根；沙箱继承原 session（read-only 会被继承）                                                                  |
| claude 没有沙箱级只读                                            | 以为能像 codex `-s read-only` 那样硬隔离                                                                                                                   | 只能靠 `--allowedTools` 白名单 + `--disallowedTools "Edit,Write"` + **跑完** **`git status --short`** **验证仓库未被动过** |
| claude 非交互下工具默认被拒                                         | 不加白名单 → 它拿不到证据却照样给结论                                                                                                                              | 必给 `--allowedTools`；`--permission-mode dontAsk` 表示"不询问，未授权即拒绝"                                             |
| 非交互挂住等审批                                                  | 卡在 approval                                                                                                                                       | codex 非交互默认 `never`；显式传就写 `-a never`                                                                       |
| 误以为 read-only 不能跑命令                                       | 以为审查只能静态读                                                                                                                                         | 实测可执行；codex 会自建 `C:\Windows\Temp\<name>\` 放脚本                                                              |
| **成本底噪**                                                  | claude 每次调用约 **$0.14 / 23k input tokens**（系统提示 + 项目 CLAUDE.md），与任务大小无关                                                                           | 用 `--max-budget-usd` 兜底；开跑前算清"轮次 × 2 家"的总量                                                                 |
| 红队有"找错"偏差                                                 | 把审查结论照单全收                                                                                                                                         | **必做二次复核**，出采纳/部分采纳/驳回三分类                                                                                  |
| **以为** **`claude`** **CLI 就是 Anthropic Claude**           | 报告里写"claude-sonnet-5 审查"，实际是网关上的其他模型                                                                                                              | 查 `~/.claude/settings.json` 的 `ANTHROPIC_BASE_URL` / `*_MODEL_NAME`，并在流里抽查 `message.model`；如实写进 REVIEW 元信息 |
| **按真实计价设** **`--max-budget-usd`**                         | 实测设 $5 → 7分22秒 / 32 轮被 `budget_exhausted` 掐断，取证做一半                                                                                               | 本机该数字是虚拟账单；当"防跑飞闸门"用，给宽（如 40）或省略                                                                           |
| 以为有提示缓存                                                   | `cache_read_input_tokens` 恒 0（网关不实现 `cache_control`）→ 每轮全量重发，轮次越多越贵                                                                               | 控制轮次；中断用 resume 收口而非重跑                                                                                     |
| 中断后从头重跑                                                   | 白烧掉已完成的取证                                                                                                                                         | `--resume <session_id>` + 模板 D 收口                                                                          |
| **相信"编辑成功"回执**                                            | 本机实测：16 项处置只真落地 6 项；同一批编辑甚至出现"回执成功但内容没进文件"                                                                                                        | 改完**必须回读 + grep 关键词**逐条验证；审核清单里加"落地核验"项（模板 A 的 E）                                                          |
| **同一文件并行 Edit**                                           | 同一条消息里对同一文件发两个 Edit：第二个以**陈旧内容**为基写入，把第一个静默覆盖（本机实测：MEMORY.md 两处修改只落地一处，回读才发现）                                                                     | 同一文件的多次修改**串行**发，或一次一个 Python 脚本写完；改完必回读                                                                   |
| **在 N 轮讨论中途改被审文档**                                        | 审核方按旧版本取证，回来引用对不上，产生假分歧                                                                                                                           | 讨论期间**冻结**被审文档，全部轮次结束后统一修订                                                                                 |
| 只让审核方"证伪"不问"有没有漏"                                         | 会漏掉文档没列的第 5 条链路/新机制                                                                                                                               | prompt 里保留一栏"**两份文档都没提到的问题**"，并明确要求回答"是否穷尽"                                                                |
| 不核审方与被审系统的**模型同源**                                        | 若网关承载的模型与被审系统自用模型同源，"独立第三方"名不副实                                                                                                                   | 在 REVIEW 元信息表里写"独立性声明"，同源则标注打折                                                                             |
| **把 stderr 并进 JSON 产物**（`> f.json 2>&1`）                  | CLI 警告行（如 `[claude-code:unrecognized_model] {"model":"MiniMax-M3",...}`）混进 JSON 文件，整体 `json.load` 必炸；实测后台子任务通知报 failed，CLI 其实 `is_error:false` 成功 | 分开重定向 `> f.json 2> f.err`；或按行解析只取 `{` 开头的行（§6 脚本已免疫）。顺带：这行警告正是**网关真实模型的免费情报**                              |
| **双审核方模型同源**                                              | 用户切换 provider 后 claude 通道与 codex 通道同跑 MiniMax-M3，"团队审核"看似两方、实为同一模型视角，盲区高度相关                                                                       | 每跑前查两家真实模型（§2）；同源时 REVIEW 元信息写"双审核方同源，多样性仅来自 harness/提示差异"；要真模型多样性，把其中一家指到不同模型家族                           |
| 把 N 轮做成"重审 N 次"                                           | 只给审核方自己的旧结论，不给对方异议                                                                                                                                | brief 必须含「对方异议 + 我的裁决」两块                                                                                   |
| 忘了清理                                                      | 仓库根留下 `_codex_*` / `_claude_*`                                                                                                                    | 跑完即删；顺带清 `C:\Windows\Temp\<name>\`                                                                         |

