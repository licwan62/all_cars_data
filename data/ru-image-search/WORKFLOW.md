# 俄罗斯车型图：独立消费队列

2026-11-14 生效。主协调以吞吐为职责，禁止介入车型、改款、市场、车身、许可、参数等资料复核；这些判定完全由 identity 承担。主协调不得自己签 identity 或 final_visual 凭证，也不得推翻 identity 的 hold。实际逐图验收仍须进行，由独立 identity_visual 完成，不能把自动 SHA 校验当作视觉通过。

## 角色和交接

| 角色 | 唯一责任 | 交出后立即做什么 |
|---|---|---|
| source | 按车型包收集原件、许可和身份依据，保留原始文件与 SHA | 入 identity_pending 后继续下一车型，不等待生产 |
| identity_source / identity_a | 独立核实来源、同代际、同改款、同市场、同车身结构和配置适用性 | 写 SHA 绑定 identity 凭证；疑难独立 hold，不要求主代理查证 |
| P1 / P2 | 领取 ready、按已审核来源构造提示、生成并保留真实原始返回 | submit-render 后立即领取下一项，不等 OSS、视觉审核或入账 |
| V1 / V2 | 独立处理输出、上传私有 OSS、完整 GET、实际字节 SHA 和解码 | submit-verification 后立即领取下一校验任务，不等视觉审核 |
| identity_visual / identity_final | 实际查看来源和成品，核对前方 1/2 或 1/3、身份、车徽、顶杆、轮胎和画面 | 签 final_visual 或出具定向返修/hold；直接通知对应工位 |
| root | 机器校验凭证、冻结范围、重复项和计数，安装台账，Git 提交 | 只处理入账事件，不再打开资料或逐图二次审查 |
| site_assets | 从正式台账异步导出网站 | 每 15 分钟合并同步，不阻塞生产或入账 |

来源审核和成品视觉审核应由不同的在岗消费者处理，避免难资料堵塞视觉队列。逻辑角色不强制增加常驻代理：恢复时可把既有闲置代理分配给 V 或 identity_visual；须在派发时明确签名角色及授权名单。不得声称已更换模型或档位而没有启动参数证据。

```text
source → identity_pending → identity_source → ready → P1/P2
  → verification_pending → V1/V2 → final_visual_pending
  → identity_visual → in_review → root 机器登记 → done
```

这是显式队列/租约协议，不是后台守护进程。每个在岗消费者交付后应自行领取下一项；无工作时发一次等待通知，由上游交付事件重新唤醒。主代理不能把“等待整包完成”设为派发条件，不能只结束子代理却宣称后台持续运行。

## 在制品与异常

- `identity_pending + ready` 合计达到 12 暂停常规 source 入库，降到 6 或以下恢复；疑难补缺只能关联原 hold，不另囤库存。
- P1/P2 每人最多一个 producing 租约；生成同时在途上限 3。生产提交保留原始返回后释放生产租约。
- V 每人最多一个 verifying 租约；完成包保留原 verification_claim_id，状态改为 final_visual_pending 后释放 V 工位。追加视觉签名不能改完工包的 source/candidate、OSS、completion 或租约。
- 一张失败只阻塞该配置；实际返回后的连续两次返修仍失败，转 identity 疑难或换源，其余继续。不得用换源绕开 unknown。
- 未知/中断请求先恢复结果再决定；保留 P1-034、P1-060 的正式 registry 约束，不重发、不推断成功、不抹除历史。
- identity 不通过时出具可执行原因及 source/output SHA，直接回给对应 source/P；root 仅机械登记 hold/requeue，不复核理由。
- 每完成 6 张或最老完整审核包等待 5 分钟触发入账。单批 root 机器处理预算 60 秒；超时拆批并保留错误，不开展资料研究。此为运行目标，尚未用恢复后的真实产线验证。
- 分配、素材就绪、生产开始、验收完成、生成次数、实际账单成本沿用原始证据统计；未知成本保持 null。不能从接受张数推算调用量。

## 命令协议

在仓库根目录运行。所有 worker 先核对 queue/正式 checkpoint 与既有未完成请求。只有 root 可安装正式 checkpoint 和提交 Git。

1. root 用 `configure-workflow --actor root --policy-file data/ru-image-search/workflow-policy.json` 配置队列；配置会保存 SHA 绑定快照。`paused=true` 保持停产，不能创建新生产/校验租约或提交新 render。
2. source 用 `enqueue --file SOURCE_PACKET` 入库。新模式进入 identity_pending；旧 ready 缺实际身份凭证也须迁移回 identity_pending。既有 active/unknown 不重置。
3. identity 用 `submit-identity --worker identity_a --evidence IDENTITY_JSON` 审核来源。通过后进入 ready。实际审核要求及凭证格式见 `scripts/ru_pilot_delegated_review.md`。
4. P 用 `claim --worker P1` 原子领单；保留已返回原始字节和身份凭证，用 `submit-render --worker P1 --claim CLAIM --result RENDER_JSON` 交出；立即再次 claim。禁止在这一环上传/等待 root 审核。
5. V 用 `claim-verification --worker V1` 领取独立 verification_claim_id。完成真实 OSS 全量回读后，用 `submit-verification --worker V1 --claim CLAIM --verification-claim VCLAIM --result VERIFIED_JSON` 交包；立即再次 claim-verification。
6. identity_visual 实际验图并写 SHA 绑定 final_visual 凭证。V 角色自动转发带签名完成包，用 `submit-review --worker V1 --claim CLAIM --verification-claim VCLAIM --result FINAL_REVIEW_JSON` 进入 in_review；该旧 lease 不占其新 verifying 工位。
7. root 用 `ru_pilot_delegated_review.py assemble` 组装自动登记条目，再用 `ru_pilot_publish.py --policy-file POLICY --actor root --file ACCEPTANCE ...` 机器检查/创建不可变批次。只存 JSON 审核依据，车辆及 OSS 回取图像保留私有 OSS。新模式保持前视门禁，不接受纯侧面、后方或缺凭证结果。
8. `ru_pilot_install.py --publication-result RESULT_JSON --actor root` 默认只读验证；明确 `--install` 才以旧 checkpoint SHA 防并发原子安装。成功后 root 对对应 claim 用已发布凭证 resolve done，再提交推送该完整批次。默认不会为 worker 接受结果，也不会自行运行 imagegen。

旧 `pilot20/root_signoff.py`、`install_checked_batch.py` 和网站私有脚本中硬编码 reviewer=root 的流程在新模式退役，不作为恢复入口。历史 root 审核和旧图保持原样，新审核字段不得谎称 root 实际看过图片。Sites 只消费正式 index 的 current_front_view_passed / SHA 和 progress 的 current_front_view_*，不能按 reviewer=root 筛掉委托通过图，也不能重新把历史审批当作当前前视通过。

## 当前切换与恢复

此次修复只运行隔离工程测试，生产仍暂停，未新增验收。正式图像结果仍是第 82 批：295/2394 当前前视配置，92/1309 完整任务，4/500 完整映射行，34 张待前视返修。队列切换只保存角色策略和缺凭证待审状态，不回写历史批次，不清除 active/unknown。

恢复生产时必须把暂停策略显式改为 false，保存新的 SHA 绑定策略快照并更新 checkpoint 策略指针，再 configure-workflow；不能只修改 JSON 文件让已有审核凭证静默换依据。优先由 identity/V 接管已返回积压，P 恢复原有零生成 claim 后按新协议消费。恢复后的第一组实际吞吐再验证队列等待时间和每小时验收数量；本次测试不能证明速度已提高。
