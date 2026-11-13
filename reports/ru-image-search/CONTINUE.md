# 俄罗斯云端制图接续

用户授权：使用更新后的云环境，从当前断点继续俄罗斯 CSV 范围的找图、原件验证、实际制图和验收。全部 1309 项验收完成后暂停并报告。老车与范围外俄罗斯始终暂停。用户已授权公网全部域名访问；必须核验当前新环境实际已应用，不能冒称设置生效。

## 仓库和断点

- 结果仓库 https://github.com/licwan62/all_cars_data ，分支 `ru-image-search-20261113-batch01`。本轮从 `65a16c3b233adb6e46cb07a67e9f3699e4200050` 续作，接续时先 fetch，核对最新远端，保留并发任务变化。
- 入口 `reports/ru-image-search/work/checkpoint.json`。当前自主续作及成品验收见 2026-11-13_10，全范围初步查询、既有资产读取及前两次方法样张见 2026-11-13_09；11张原件与来源目视证据见 2026-11-13_08。以 checkpoint 当前 progress、working_policy、acceptance 及各来源指针为准；旧readiness中的样式待核不再构成全局人工门槛，历史批次不改写。
- 正式输入 `reports/ru-image-search/artifacts/2026-11-13_03_ru-csv-priority/output/俄罗斯优先找图队列-20261113_03.json`，SHA256 `55cab41b8358f6054ec57ba471a07aedc4056a2e85896fa2804c955dd2b87c65`，来源提交 `e31aebfcf2a3fdc29b1cb0169e51393110419a8d`。
- 同批 `input/俄罗斯原始列表.csv` SHA256 `eb97d5becf5229324e935575c90a475f10cd790f686a253174fc157cab8c7eef`。500 行、1309 项任务、2394 条尺寸记录。按 scope_rows 与 requirements 配置核对，不把代表年当照片精确车型年或拍摄年证据。
- 第08批已将前10项的11张候选全部完整下载、解码、查看，并备份至原私有OSS，11张完整GET读回SHA一致。来源许可和逐张观察见该批 original-source-evidence / source-visual-reviews；下载量不计成品验收。
- 第09批对其余1299项按配置执行2355次实际Commons初步查询，1278次有命中、1077次本次查询无命中；保存3036个去重来源页，全部为未核搜索线索，不能算原件、身份核准或尺寸覆盖。任务级1309项都已开展初步搜索；首10项中未搜细分配置仍须补齐，无命中查询不代表已穷尽来源。
- 实际生成2张Granta普通Liftback方法样张，两个请求均返回，无未知在途请求。首张天线触顶退回；第二张完整性、灰底/深底草稿质量已实际查看，最终视觉样式仍待确认。原件及3张检查底图共5个对象已OSS完整读回。成品验收仍0项，所有1309项、2394条尺寸记录、500行未完成。
- 上条为第09批历史状态。第10批取消不必要的人工样式等待，采用透明无影/来源机位作为代理工作默认，不伪造用户样式批准。新增真实Sedan生成1张，灰底/深底检查后，连同既有Liftback第二稿完成当前默认下的Codex验收，2张成品独立保存并OSS完整读回。累计生成3张、当前采用2张、覆盖2条尺寸记录；完整任务仍0/1309、整行仍0/500，剩余2392条尺寸记录。Sport不由普通版替代。

## OSS 已配置过，不要再次索要密钥

- 现行制作仓库 https://github.com/licwan62/main_picture_producer ，最新已读main `2c8779da1669d31ec0468e1f96106d24a4d90b11`、master `b1764c4912b43e0691f86fce61d5823486ef1566`。本环境制作工作树 `/workspace/ru_picture_producer` 已更新到该main，原 `/workspace/main_picture_producer` checkout 保留。先fetch最新，读取根和 `data/俄罗斯/AGENTS.md`。
- `config/asset_storage.local.json` 被 Git 忽略，新克隆没有它不表示用户未配置 OSS。可按下列非秘密元数据恢复，已有文件先检查，禁止覆盖不同配置。
- bucket `vehicle-gallary`；region `cn-hangzhou`；endpoint `https://oss-cn-hangzhou.aliyuncs.com`；prefix `main_picture_producer/v1/objects`；cache_limit_bytes `8388608`。
- 按 asset_store.backend_id 的算法计算，此配置标识必须为 `e376451857dee2ecc82b9bedc08d1bbf99687df07e0a55b1dd97f005553cb4dc`，与原成功完整读回凭证完全一致。
- 云环境已有变量 `accessKeyId`、`accessKeySecret`；只在执行进程中映射到现行 SDK 要求的 `OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`。配置 credentials 字段保持空值。不要在日志、提示词、Git 或报告打印/保存密钥值。
- 安装仓库锁定的 requirements-storage.txt（alibabacloud-oss-v2==1.4.1），依赖放项目外，使用现行 asset_store 接口。
- 本轮已重新安装SDK至 `/workspace/scratch/ru-oss-sdk`，在 `/workspace/ru_picture_producer` 独立工作树恢复空credentials配置并核对backend。现行asset_store签名GET成功恢复一张既有Silverado图，SHA与解码通过并已查看，尚未核准RU适配和当前批准。
- 当前环境实测 `observations_current=true`、network policy `unrestricted/enforced`。沙箱内代理端口不可达，已获准的外层执行器使用继承代理和TLS信任可访问GitHub、Google、Commons；OSS未签名403是私有服务响应，签名GET成功，不能继续套用旧网络阻塞结论。Commons API使用明确项目User-Agent，默认requests标识会被要求遵守robots策略。
- 原件路径/SHA/size/对象key见第08批JSON；原图不入Git。新环境本地路径不保证存在，按对象key完整GET并校验后恢复；不得把缓存缺失当作需要重新生图。网络设置不等于OSS Bucket公开，不修改Bucket私有权限。

## 规则与资产复用

- 用户本轮要求“pull一下看看”。较早fetch后远端又并发新增迁入提交；已合并结果说明 `4c30469e`，更新制作工作树到 `2c8779da`，读取并逐文件SHA核验俄罗斯规则、CSV、队列、来源清单和接续文档。旧“未迁入data/俄罗斯”阻塞已撤销，不再索取已复制资料。新规则仍明确专用视觉样例未独立核实，不能擅自将皮卡画布、视角、阴影规则扩展到全部俄罗斯车型。
- 使用 asset_store 公共接口读压缩资产索引，前次共 38076 条。没有俄罗斯路径，但 31 项皮卡类俄罗斯任务具有 314 条同名称当前成品/参考资产候选。详见批次06 `output/asset-reuse-audit-20261113_06.json`，含逻辑路径、已登记 SHA、对象 key；当时本地均无图档。
- 名称匹配不证明代际/cab/货斗/车身/版本/市场符合。先恢复、校验、看图及核对当前批准凭证，合格者复用；不得因为缓存缺失重新生成，不重发结果未知的请求。
- 第09批已通过现行有界OSS缓存对314条同名资产逐项完整读取/SHA/解码，314条均成功，对应307个不同SHA；除较早实际查看的Silverado探针外，其余只有技术读取结论，尚未逐项认车或核对当前批准，RU成品复用仍0。进度中旧 `restored_managed_asset_images=1` 指早先单张物理恢复探针，批量缓存读取以 `restored_managed_asset_entries=314`、`restored_managed_asset_unique_shas=307` 及逐项清单为准。
- 通过现有 imagegen 工作流实际制作、保存原图与成品、记录图档路径/SHA、配置和适用记录、逐项技术与目视验收。不得猜车型生成、冒称已看图，或把远程图片/缩略图当本地原件。
- 分批使用 lib/artifact_batch.py 创建不可变 reports/ru-image-search 批次，更新持久工作队列及 checkpoint，分批提交推送自己的结果分支；合并前检查并发远端。
- 完成后报告任务数、覆盖记录数、图档位置、报告、远端提交以及暂停状态。实际无法恢复的阻塞须保存精确剩余数量和证据，不假称完成，不自动领取其他范围任务。

## 2026-11-13 俄罗斯资料已同步到制图仓库

按用户要求，已将本聊天明确的任务规则、CSV原字节、1309项队列、候选、资产复用核对及非秘密OSS连接信息同步到 main_picture_producer：main `2c8779da1669d31ec0468e1f96106d24a4d90b11`，master `b1764c4`。两分支资料字节相同；读取 `data/俄罗斯/AGENTS.md`、`data/俄罗斯/规则/任务规则.md`、`data/俄罗斯/来源清单.json` 与 `文档/俄罗斯/云端与本地接续.md`。上文“没有data/俄罗斯”是迁入前事实，不能再据此索取已复制的材料。仍未独立核实的专用视觉样例按规则记待核，不冒称已恢复。

云端已完成落盘和远端推送。Windows本地 D:\Home\Repo\main_picture_producer 未由本聊天直接写入：没有可用的本机文件执行接口。已提供 `脚本/同步俄罗斯资料.ps1`，SHA预检、同内容跳过、不同内容保留原件并报告冲突；运行时不切换分支、不改本机私密配置或原队列状态。当前Linux环境无PowerShell，未宣称Windows实跑通过。生产断点仍由本仓库维护，制图仓库中的接续材料为有来源的只读快照。

## 当前下一步

用户问“需要人工介入？”。不需要人工逐张审批，原找图、制图、验收授权继续有效；上一轮将可选视觉偏好作为全局暂停条件不必要。第10批 `working-default` 明确代理采用透明无影/来源机位的工作默认，并未把UI默认选项当作用户答复，也未冒称恢复了未见过的专用视觉标准。用户将来给出明确样式时新建SHA绑定修订，不反改历史。

普通Liftback与Sedan的采用图、来源/输入/输出SHA、独立车型资料、实际观察和当前成品对象key均在第10批 `granta-accepted-variants`。该验收证明指定车身的代表性外观，不证明精确车型年、照片拍摄国家或每个配置年份；独立社区资料支持俄罗斯市场、2014五门车身及2018改款边界。

优先继续首项Sport独立素材；追加一次查询所得Drive Active、发动机、特技/改装及投产/博物馆线索未被采用。单项身份/配置缺口独立保留，不阻塞其他可核实配置。累计3次生成均已返回，不重发旧请求；11张原件和307个既有内容可按对象key/SHA恢复，3036来源页仅作检索线索。全部1309项实际验收后暂停；当前无全局人工样式等待，也没有宣称聊天结束后存在自动生图后台。
