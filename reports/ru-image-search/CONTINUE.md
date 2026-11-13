# 俄罗斯云端制图接续

用户授权：使用更新后的云环境，从当前断点继续俄罗斯 CSV 范围的找图、原件验证、实际制图和验收。全部 1309 项验收完成后暂停并报告。老车与范围外俄罗斯始终暂停。用户已授权公网全部域名访问；必须核验当前新环境实际已应用，不能冒称设置生效。

## 仓库和断点

- 结果仓库 https://github.com/licwan62/all_cars_data ，分支 `ru-image-search-20261113-batch01`。本轮从 `65a16c3b233adb6e46cb07a67e9f3699e4200050` 续作，接续时先 fetch，核对最新远端，保留并发任务变化。
- 入口 `reports/ru-image-search/work/checkpoint.json`。网络恢复、原件和来源目视复核见 2026-11-13_08；以 checkpoint 的 progress/candidate/readiness 指针为准。历史批次不改写。
- 正式输入 `reports/ru-image-search/artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json`，SHA256 `55cab41b8358f6054ec57ba471a07aedc4056a2e85896fa2804c955dd2b87c65`，来源提交 `e31aebfcf2a3fdc29b1cb0169e51393110419a8d`。
- 同批 `input/俄罗斯原始列表.csv` SHA256 `eb97d5becf5229324e935575c90a475f10cd790f686a253174fc157cab8c7eef`。500 行、1309 项任务、2394 条尺寸记录。按 scope_rows 与 requirements 配置核对，不把代表年当照片精确车型年或拍摄年证据。
- 第08批已将前10项的11张候选全部完整下载、解码、查看，并备份至原私有OSS，11张完整GET读回SHA一致。来源许可和逐张观察见该批 original-source-evidence / source-visual-reviews；下载量不计成品验收。生成/成品验收仍为0，所有1309项、2394条尺寸记录、500行未完成。搜索进行中，以新批进度为准。

## OSS 已配置过，不要再次索要密钥

- 现行制作仓库 https://github.com/licwan62/main_picture_producer ，先检查最新 main/master。此前读取 main `bfd99908f93635e4aba1e3d6f95297dde114dc25`；默认 master 是 `356f210e063274d8d03fe88b49d7bc8af5b62452`。main 较新。读取当前 AGENTS.md。
- `config/asset_storage.local.json` 被 Git 忽略，新克隆没有它不表示用户未配置 OSS。可按下列非秘密元数据恢复，已有文件先检查，禁止覆盖不同配置。
- bucket `vehicle-gallary`；region `cn-hangzhou`；endpoint `https://oss-cn-hangzhou.aliyuncs.com`；prefix `main_picture_producer/v1/objects`；cache_limit_bytes `8388608`。
- 按 asset_store.backend_id 的算法计算，此配置标识必须为 `e376451857dee2ecc82b9bedc08d1bbf99687df07e0a55b1dd97f005553cb4dc`，与原成功完整读回凭证完全一致。
- 云环境已有变量 `accessKeyId`、`accessKeySecret`；只在执行进程中映射到现行 SDK 要求的 `OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`。配置 credentials 字段保持空值。不要在日志、提示词、Git 或报告打印/保存密钥值。
- 安装仓库锁定的 requirements-storage.txt（alibabacloud-oss-v2==1.4.1），依赖放项目外，使用现行 asset_store 接口。
- 本轮已重新安装SDK至 `/workspace/scratch/ru-oss-sdk`，在 `/workspace/ru_picture_producer` 独立工作树恢复空credentials配置并核对backend。现行asset_store签名GET成功恢复一张既有Silverado图，SHA与解码通过并已查看，尚未核准RU适配和当前批准。
- 当前环境实测 `observations_current=true`、network policy `unrestricted/enforced`。沙箱内代理端口不可达，已获准的外层执行器使用继承代理和TLS信任可访问GitHub、Google、Commons；OSS未签名403是私有服务响应，签名GET成功，不能继续套用旧网络阻塞结论。Commons API使用明确项目User-Agent，默认requests标识会被要求遵守robots策略。
- 原件路径/SHA/size/对象key见第08批JSON；原图不入Git。新环境本地路径不保证存在，按对象key完整GET并校验后恢复；不得把缓存缺失当作需要重新生图。网络设置不等于OSS Bucket公开，不修改Bucket私有权限。

## 规则与资产复用

- 用户本轮要求“pull一下看看”，已再次fetch制作仓库全部远端分支，仅main/master且仍为上述提交；仍未发现data/俄罗斯、俄罗斯专用制作规则/台账/合格样例。已请用户给出具体仓库/分支/路径或推送本机现行资料；等待期间可继续来源检索核验，不能将皮卡画布、视角、阴影规则无证据地套用全部俄罗斯车型。原始CSV已保存，不必再次索取。
- 使用 asset_store 公共接口读压缩资产索引，前次共 38076 条。没有俄罗斯路径，但 31 项皮卡类俄罗斯任务具有 314 条同名称当前成品/参考资产候选。详见批次06 `output/asset-reuse-audit-20261113_06.json`，含逻辑路径、已登记 SHA、对象 key；当时本地均无图档。
- 名称匹配不证明代际/cab/货斗/车身/版本/市场符合。先恢复、校验、看图及核对当前批准凭证，合格者复用；不得因为缓存缺失重新生成，不重发结果未知的请求。
- 通过现有 imagegen 工作流实际制作、保存原图与成品、记录图档路径/SHA、配置和适用记录、逐项技术与目视验收。不得猜车型生成、冒称已看图，或把远程图片/缩略图当本地原件。
- 分批使用 lib/artifact_batch.py 创建不可变 reports/ru-image-search 批次，更新持久工作队列及 checkpoint，分批提交推送自己的结果分支；合并前检查并发远端。
- 完成后报告任务数、覆盖记录数、图档位置、报告、远端提交以及暂停状态。实际无法恢复的阻塞须保存精确剩余数量和证据，不假称完成，不自动领取其他范围任务。
