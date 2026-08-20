(
    源 as table,
    参数源 as table,
    尺码表输入 as table,
    optional 源字段 as nullable record,
    optional 尺码字段 as nullable record,
    optional 参数字段 as nullable record,
    optional 英寸输入 as nullable logical
) as table =>

let
    //==================================================
    // 1. 基础函数
    //==================================================

    取数字 = (x as any) as nullable number =>
        try Number.From(x) otherwise null,

    清洗文本 = (x as any) as nullable text =>
        let
            t =
                try Text.Trim(Text.From(x))
                otherwise ""
        in
            if t = "" then null else t,

    取最大数 = (values as list) as nullable number =>
        let
            nums = List.RemoveNulls(values)
        in
            if List.IsEmpty(nums) then
                null
            else
                List.Max(nums),


    //==================================================
    // 1.5 字段配置
    //==================================================

    源字段配置 =
        if 源字段 = null then [] else 源字段,

    尺码字段配置 =
        if 尺码字段 = null then [] else 尺码字段,

    参数字段配置 =
        if 参数字段 = null then [] else 参数字段,

    // 源表字段
    源分类字段 = Record.FieldOrDefault(源字段配置, "分类", "分类"),
    源CAB字段 = Record.FieldOrDefault(源字段配置, "CAB", "CAB"),
    源版本字段 = Record.FieldOrDefault(源字段配置, "版本", "版本"),
    源长度字段 = Record.FieldOrDefault(源字段配置, "长", "L-MM"),
    源宽度字段 = Record.FieldOrDefault(源字段配置, "宽", "W-MM"),
    源高度字段 = Record.FieldOrDefault(源字段配置, "高", "H-MM"),
    源T字段 = Record.FieldOrDefault(源字段配置, "T", "T-MM"),

    // 尺码表字段
    尺码分类字段 = Record.FieldOrDefault(尺码字段配置, "分类", "分类"),
    尺码CAB字段 = Record.FieldOrDefault(尺码字段配置, "CAB", "CAB"),
    尺码版本字段 = Record.FieldOrDefault(尺码字段配置, "版本", "版本"),
    尺码长度字段 = Record.FieldOrDefault(尺码字段配置, "长", "长上限"),
    尺码名称字段 = Record.FieldOrDefault(尺码字段配置, "尺码", "内部尺码"),
    尺码粗上限字段 = Record.FieldOrDefault(尺码字段配置, "粗上限", "粗上限"),
    尺码序号字段 = Record.FieldOrDefault(尺码字段配置, "档位序号", "档位序号"),

    // 参数表字段
    参数名称字段 = Record.FieldOrDefault(参数字段配置, "参数", "参数"),
    参数数值字段 = Record.FieldOrDefault(参数字段配置, "值", "值"),

    // 单位后缀（所有内部值均为毫米）
    单位后缀 = " mm",


    参数标准化 =
        Table.Buffer(
            Table.FromRecords(
                List.Transform(
                    Table.ToRecords(参数源),
                    (当前参数 as record) as record =>
                        [
                            参数名称 =
                                清洗文本(
                                    Record.FieldOrDefault(
                                        当前参数,
                                        参数名称字段,
                                        null
                                    )
                                ),
                            参数值 =
                                取数字(
                                    Record.FieldOrDefault(
                                        当前参数,
                                        参数数值字段,
                                        null
                                    )
                                )
                        ]
                ),
                type table [参数名称 = nullable text, 参数值 = nullable number]
            )
        ),

    参数毫米 = 参数标准化,

    读取参数 = (参数名 as text) as number =>
        let
            找到的参数 =
                Table.SelectRows(
                    参数毫米,
                    each [参数名称] = 参数名
                ),

            参数值 =
                if Table.IsEmpty(找到的参数) then
                    error Error.Record(
                        "参数错误",
                        "参数不存在，或者参数值无法转换为数字。",
                        [
                            参数 = 参数名
                        ]
                    )
                else
                    找到的参数{0}[参数值]
        in
            if 参数值 = null then
                error Error.Record(
                    "参数错误",
                    "参数不存在，或者参数值无法转换为数字。",
                    [
                        参数 = 参数名
                    ]
                )
            else
                参数值,


    //==================================================
    // 2. 读取容差参数
    //==================================================

    余量长容差 = 读取参数("余量长容差"),


    //==================================================
    // 3. 清理旧结果列和内部辅助列
    //
    // 避免函数重复执行时出现：
    // 自动尺码字段已经存在
    //==================================================

    源基础 =
        Table.RemoveColumns(
            源,
            {
                "自动尺码",
                "自动长度余量"
            },
            MissingField.Ignore
        ),


    //==================================================
    // 4. 创建安全索引键
    //
    // 使用长度前缀，防止分类和 CAB 拼接后发生冲突
    //==================================================

    编码文本 = (x as nullable text) as text =>
        if x = null then
            "N;"
        else
            "T"
                & Text.From(Text.Length(x))
                & ":"
                & x
                & ";",

    编码数字 = (x as nullable number) as text =>
        if x = null then
            "N;"
        else
            "D"
                & Number.ToText(
                    x,
                    "0.###############",
                    "en-US"
                )
                & ";",

    生成尺码池键 = (
        分类 as nullable text,
        CAB as nullable text,
        版本 as nullable text
    ) as text =>
        编码文本(分类)
            & 编码文本(CAB)
            & 编码文本(版本),

    生成匹配键 = (
        分类 as nullable text,
        CAB as nullable text,
        版本 as nullable text,
        L as nullable number,
        W as nullable number,
        H as nullable number,
        T as nullable number
    ) as text =>
        编码文本(分类)
            & 编码文本(CAB)
            & 编码文本(版本)
            & 编码数字(L)
            & 编码数字(W)
            & 编码数字(H)
            & 编码数字(T),


    //==================================================
    // 5. 尺码表仅保留实际使用字段
    //
    // 字段不存在时自动补 null，不直接报错
    //==================================================

    尺码必要列 =
        Table.SelectColumns(
            尺码表输入,
            {
                尺码分类字段,
                尺码CAB字段,
                尺码版本字段,
                尺码长度字段,
                尺码粗上限字段,
                尺码名称字段,
                尺码序号字段
            },
            MissingField.UseNull
        ),


    //==================================================
    // 6. 尺码表统一清洗 + 重命名为标准内部名
    //
    // 原函数会在每一行车型匹配时重复转换文本和数字；
    // 当前版本只转换一次
    //==================================================

    尺码转换 =
        Table.TransformColumns(
            尺码必要列,
            {
                {
                    尺码分类字段,
                    each 清洗文本(_),
                    type nullable text
                },
                {
                    尺码CAB字段,
                    each 清洗文本(_),
                    type nullable text
                },
                {
                    尺码版本字段,
                    each 清洗文本(_),
                    type nullable text
                },
                {
                    尺码长度字段,
                    each 取数字(_),
                    type nullable number
                },
                {
                    尺码粗上限字段,
                    each 取数字(_),
                    type nullable number
                },
                {
                    尺码名称字段,
                    each 清洗文本(_),
                    type nullable text
                },
                {
                    尺码序号字段,
                    each 取数字(_),
                    type nullable number
                }
            }
        ),

    尺码重命名 =
        Table.RenameColumns(
            尺码转换,
            {
                {尺码分类字段, "分类"},
                {尺码CAB字段, "CAB"},
                {尺码版本字段, "版本"},
                {尺码长度字段, "长_in"},
                {尺码粗上限字段, "粗_in"},
                {尺码名称字段, "内部尺码"},
                {尺码序号字段, "档位序号"}
            }
        ),

    尺码标准化 = 尺码重命名,

    有效分类尺码 =
        Table.SelectRows(
            尺码标准化,
            each [分类] <> null
        ),

    添加尺码池键 =
        Table.AddColumn(
            有效分类尺码,
            "__尺码池键",
            each
                生成尺码池键(
                    [分类],
                    [CAB],
                    [版本]
                ),
            type text
        ),


    //==================================================
    // 7. 按分类和 CAB 排序、分组
    //
    // GroupKind.Local 要求相同键必须连续，
    // 因此先按照尺码池键排序
    //==================================================

    尺码表按池排序 =
        Table.Buffer(
            Table.Sort(
                添加尺码池键,
                {
                    {
                        "__尺码池键",
                        Order.Ascending
                    }
                }
            )
        ),

    尺码池分组 =
        Table.Buffer(
            Table.Group(
                尺码表按池排序,
                {
                    "__尺码池键"
                },
                {
                    {
                        "__尺码池",
                        (当前池 as table) as record =>
                            let
                                完整池 =
                                    Table.Buffer(
                                        Table.RemoveColumns(
                                            当前池,
                                            {
                                                "__尺码池键"
                                            },
                                            MissingField.Ignore
                                        )
                                    ),

                                可匹配池 =
                                    Table.Buffer(
                                        Table.Sort(
                                            Table.SelectRows(
                                                完整池,
                                                each
                                                    [档位序号] <> null
                                                    and [长_in] <> null
                                                    and [粗_in] <> null
                                            ),
                                            {
                                                {
                                                    "档位序号",
                                                    Order.Ascending
                                                },
                                                {
                                                    "长_in",
                                                    Order.Ascending
                                                }
                                            }
                                        )
                                    ),

                                最大长 =
                                    取最大数(
                                        完整池[长_in]
                                    ),

                                最大粗 =
                                    取最大数(
                                        完整池[粗_in]
                                    )
                            in
                                [
                                    候选表 = 可匹配池,
                                    最大长 = 最大长,
                                    最大粗 = 最大粗
                                ],
                        type record
                    }
                },
                GroupKind.Local
            )
        ),


    //==================================================
    // 8. 将尺码池转换为 Record 索引
    //
    // 后续按键直接取池，不再每行扫描整张尺码表
    //==================================================

    尺码池索引 =
        if Table.IsEmpty(尺码池分组) then
            []
        else
            Record.FromList(
                尺码池分组[__尺码池],
                尺码池分组[__尺码池键]
            ),

    空候选表 =
        Table.FirstN(
            尺码标准化,
            0
        ),

    空尺码池 =
        [
            候选表 = 空候选表,
            最大长 = null,
            最大粗 = null
        ],

    取尺码池 = (
        分类 as nullable text,
        CAB as nullable text,
        版本 as nullable text
    ) as record =>
        Record.FieldOrDefault(
            尺码池索引,
            生成尺码池键(
                分类,
                CAB,
                版本
            ),
            空尺码池
        ),


    //==================================================
    // 9. 在一个尺码池中进行匹配
    //
    // 候选表已经按 档位序号 升序排好（同序号内按长度升序）：
    // 找到第一个基础候选，就是最优基础候选
    //==================================================

    计算单个尺码池 = (
        当前池 as record,
        L as nullable number,
        W as nullable number,
        H as nullable number,
        T as nullable number
    ) as record =>
        let
            数据完整 =
                L <> null
                and W <> null
                and H <> null,

            候选池 =
                Record.FieldOrDefault(
                    当前池,
                    "候选表",
                    空候选表
                ),

            基础候选记录 =
                if not 数据完整 then
                    null
                else
                    Table.First(
                        Table.SelectRows(
                            候选池,
                            each
                                [长_in] >= L
                                and [粗_in] >= T
                        ),
                        null
                    ),

            最近行结果 =
                if not 数据完整 or Table.IsEmpty(候选池) then
                    null
                else
                    let
                        带差值 =
                            Table.AddColumn(
                                候选池,
                                "__差值",
                                (r) =>
                                    let
                                        长缺 = L - Record.FieldOrDefault(r, "长_in", null),
                                        粗缺 = T - Record.FieldOrDefault(r, "粗_in", null),
                                        各缺 = List.Select({长缺, 粗缺}, each _ <> null and _ > 0),
                                        余量 = Record.FieldOrDefault(r, "长_in", null) - L,
                                        差值 =
                                            if List.IsEmpty(各缺) then
                                                if 余量 <> null and 余量 > 余量长容差 then Number.Round(余量, 1)
                                                else 0
                                            else
                                                Number.Round(List.Max(各缺), 1)
                                    in
                                        差值,
                                type number
                            ),
                        最小差值 = List.Min(带差值[__差值]),
                        最近行 =
                            Table.First(
                                Table.SelectRows(带差值, each [__差值] = 最小差值),
                                null
                            )
                    in
                        if 最近行 = null then null
                        else
                            let
                                长缺 = L - Record.FieldOrDefault(最近行, "长_in", null),
                                粗缺 = T - Record.FieldOrDefault(最近行, "粗_in", null),
                                余量 = Record.FieldOrDefault(最近行, "长_in", null) - L,
                                失败维度 =
                                    if 长缺 > 0 and 长缺 >= 粗缺 then "超长"
                                    else if 粗缺 > 0 then "超粗"
                                    else if 余量 <> null and 余量 > 余量长容差 then "超余量"
                                    else null
                            in
                                [
                                    行 = 最近行,
                                    差值 = 最小差值,
                                    原因 = 失败维度
                                ],

            最近候选 =
                if not 数据完整 then
                    [
                        自动尺码 = "数据不全",
                        自动长度余量 = null,
                        候选 = null,
                        原因 = null,
                        相差数值 = null,
                        有最终候选 = false
                    ]
                else if 基础候选记录 <> null then
                    let
                        基础候选长度 = Record.FieldOrDefault(基础候选记录, "长_in", null),
                        长度余量原值 =
                            if 基础候选长度 = null or L = null then null
                            else 基础候选长度 - L,
                        余量合格 =
                            长度余量原值 = null
                            or 长度余量原值 <= 余量长容差
                    in
                        if 余量合格 then
                            [
                                自动尺码 = Record.FieldOrDefault(基础候选记录, "内部尺码", null),
                                自动长度余量 =
                                    if 长度余量原值 = null then null
                                    else Number.Round(长度余量原值, 1),
                                候选 = null,
                                原因 = null,
                                相差数值 = null,
                                有最终候选 = true
                            ]
                        else if 最近行结果 <> null then
                            [
                                自动尺码 = "无可用尺码",
                                自动长度余量 = null,
                                候选 = Text.From(Record.FieldOrDefault(最近行结果[行], "内部尺码", "")),
                                原因 = 最近行结果[原因],
                                相差数值 = 最近行结果[差值],
                                有最终候选 = false
                            ]
                        else
                            [
                                自动尺码 = "无可用尺码",
                                自动长度余量 = null,
                                候选 = null,
                                原因 = null,
                                相差数值 = null,
                                有最终候选 = false
                            ]
                else if 最近行结果 <> null then
                    [
                        自动尺码 = "无可用尺码",
                        自动长度余量 = null,
                        候选 = Text.From(Record.FieldOrDefault(最近行结果[行], "内部尺码", "")),
                        原因 = 最近行结果[原因],
                        相差数值 = 最近行结果[差值],
                        有最终候选 = false
                    ]
                else
                    [
                        自动尺码 = "无可用尺码",
                        自动长度余量 = null,
                        候选 = null,
                        原因 = null,
                        相差数值 = null,
                        有最终候选 = false
                    ]

        in
            [
                自动尺码 = 最近候选[自动尺码],
                自动长度余量 = 最近候选[自动长度余量],
                候选 = 最近候选[候选],
                原因 = 最近候选[原因],
                相差数值 = 最近候选[相差数值],
                有最终候选 = 最近候选[有最终候选]
            ],


        //==================================================
    // 10. 同 CAB / 同版本池优先 + 三厢车长度超限降级
    //
    // 基础规则（版本识别分池，类似 CAB）：
    // 1. 同 CAB 且同版本存在最终候选，使用同 CAB 同版本池
    // 2. 同 CAB 无候选，回退 同版本通用 CAB 池（如 DRW 版本专属池）
    // 3. 仍无候选，回退 通用版本 通用 CAB 池
    //
    // 版本池优先的意图（流量入口 / 用户心智）：
    // DRW 车型一律归入 DRW 独占池（PK-WX / PK-WXXL），
    // 即使部分 DRW 尺寸上必要性不大（如老式 C/K DRW）
    //==================================================

    计算指定分类尺码 = (
        分类文本 as nullable text,
        CAB文本 as nullable text,
        版本文本 as nullable text,
        L as nullable number,
        W as nullable number,
        H as nullable number,
        T as nullable number
    ) as record =>
        let
            // 1. 同 CAB 同版本尺码池
            同CAB同版本结果 =
                if
                    分类文本 = null
                    or CAB文本 = null
                    or 版本文本 = null
                then
                    null
                else
                    计算单个尺码池(
                        取尺码池(
                            分类文本,
                            CAB文本,
                            版本文本
                        ),
                        L,
                        W,
                        H,
                        T
                    ),

            同CAB同版本有效 =
                if 同CAB同版本结果 = null then
                    false
                else
                    同CAB同版本结果[有最终候选],

            // 2. 同版本通用 CAB 尺码池（如版本文本 = "DRW" 的专属池）
            同版本结果 =
                if
                    分类文本 = null
                    or 版本文本 = null
                then
                    null
                else
                    计算单个尺码池(
                        取尺码池(
                            分类文本,
                            null,
                            版本文本
                        ),
                        L,
                        W,
                        H,
                        T
                    ),

            同版本有效 =
                if 同版本结果 = null then
                    false
                else
                    同版本结果[有最终候选],

            // 3. 通用版本 通用 CAB 尺码池
            通用结果 =
                计算单个尺码池(
                    取尺码池(
                        分类文本,
                        null,
                        null
                    ),
                    L,
                    W,
                    H,
                    T
                ),

            最终结果 =
                if 同CAB同版本有效 then
                    同CAB同版本结果
                else if 同版本有效 then
                    同版本结果
                else
                    通用结果
        in
            最终结果,


    // 获取指定分类可使用尺码池中的最大长度
    //
    // 同时检查：同 CAB 同版本、同版本通用 CAB、通用版本通用 CAB
    // 最终取三者中较大的最大长度
    取分类最大长 = (
        分类文本 as nullable text,
        CAB文本 as nullable text,
        版本文本 as nullable text
    ) as nullable number =>
        let
            同CAB同版本最大长 =
                if
                    分类文本 = null
                    or CAB文本 = null
                    or 版本文本 = null
                then
                    null
                else
                    Record.FieldOrDefault(
                        取尺码池(
                            分类文本,
                            CAB文本,
                            版本文本
                        ),
                        "最大长",
                        null
                    ),

            同版本最大长 =
                if
                    分类文本 = null
                    or 版本文本 = null
                then
                    null
                else
                    Record.FieldOrDefault(
                        取尺码池(
                            分类文本,
                            null,
                            版本文本
                        ),
                        "最大长",
                        null
                    ),

            通用最大长 =
                if 分类文本 = null then
                    null
                else
                    Record.FieldOrDefault(
                        取尺码池(
                            分类文本,
                            null,
                            null
                        ),
                        "最大长",
                        null
                    ),

            最大长列表 =
                List.RemoveNulls(
                    {
                        同CAB同版本最大长,
                        同版本最大长,
                        通用最大长
                    }
                ),

            分类最大长 =
                if List.IsEmpty(最大长列表) then
                    null
                else
                    List.Max(最大长列表)
        in
            分类最大长,


    计算尺码 = (
        分类文本 as nullable text,
        CAB文本 as nullable text,
        版本文本 as nullable text,
        L as nullable number,
        W as nullable number,
        H as nullable number,
        T as nullable number
    ) as record =>
        let
            // 先按原始分类正常匹配
            原分类结果 =
                计算指定分类尺码(
                    分类文本,
                    CAB文本,
                    版本文本,
                    L,
                    W,
                    H,
                    T
                ),

            // 仅三厢车需要读取分类最大长度
            三厢车最大长 =
                if 分类文本 = "三厢车" then
                    取分类最大长(
                        "三厢车",
                        CAB文本,
                        版本文本
                    )
                else
                    null,

            // 三厢车车辆长度已经超过该分类最大尺码的
            // 可覆盖范围时，才触发跑车降级
            三厢车长度超限 =
                分类文本 = "三厢车"
                and L <> null
                and 三厢车最大长 <> null
                and 三厢车最大长 < L,

            // 使用跑车分类重新进行：
            // 同 CAB 同版本 → 同版本通用 CAB → 通用池 回退
            跑车降级结果 =
                if 三厢车长度超限 then
                    计算指定分类尺码(
                        "跑车",
                        CAB文本,
                        版本文本,
                        L,
                        W,
                        H,
                        T
                    )
                else
                    null,

            最终结果 =
                if 三厢车长度超限 then
                    跑车降级结果
                else
                    原分类结果
        in
            [
                自动尺码 =
                    最终结果[自动尺码],

                自动长度余量 =
                    最终结果[自动长度余量],

                候选 =
                    最终结果[候选],

                原因 =
                    最终结果[原因],

                相差数值 =
                    最终结果[相差数值]
            ],

    //==================================================
    // 11. 标准化源表匹配字段
    //
    // 每一行只清洗一次分类、CAB、L/W/H
    //==================================================

    添加匹配输入 =
        Table.AddColumn(
            源基础,
            "__尺码输入",
            each
                let
                    分类值 =
                        清洗文本(
                            Record.FieldOrDefault(
                                _,
                                源分类字段,
                                null
                            )
                        ),

                    CAB值 =
                        清洗文本(
                            Record.FieldOrDefault(
                                _,
                                源CAB字段,
                                null
                            )
                        ),

                    版本值 =
                        let
                            原始版本 =
                                清洗文本(
                                    Record.FieldOrDefault(
                                        _,
                                        源版本字段,
                                        null
                                    )
                                )
                        in
                            // DRW 版本归一化：DRW / Classic DRW / R/V DRW 等
                            // 一律并入 "DRW" 独占池（版本识别分池）
                            if
                                原始版本 <> null
                                and Text.Contains(
                                    Text.Upper(原始版本),
                                    "DRW"
                                )
                            then
                                "DRW"
                            else
                                原始版本,

                    L值 =
                        取数字(
                            Record.FieldOrDefault(
                                _,
                                源长度字段,
                                null
                            )
                        ),

                    W值 =
                        取数字(
                            Record.FieldOrDefault(
                                _,
                                源宽度字段,
                                null
                            )
                        ),

                    H值 =
                        取数字(
                            Record.FieldOrDefault(
                                _,
                                源高度字段,
                                null
                            )
                        ),

                    T值 =
                        let
                            源T =
                                取数字(
                                    Record.FieldOrDefault(
                                        _,
                                        源T字段,
                                        null
                                    )
                                )
                        in
                            if 源T <> null then
                                源T
                            else if W值 <> null and H值 <> null then
                                W值 + 2 * H值
                            else
                                null,

                    匹配键 =
                        生成匹配键(
                            分类值,
                            CAB值,
                            版本值,
                            L值,
                            W值,
                            H值,
                            T值
                        )
                in
                    [
                        __尺码分类 = 分类值,
                        __尺码CAB = CAB值,
                        __尺码版本 = 版本值,
                        __尺码L = L值,
                        __尺码W = W值,
                        __尺码H = H值,
                        __尺码T = T值,
                        __尺码匹配键 = 匹配键
                    ],
            type record
        ),

    展开匹配输入 =
        Table.ExpandRecordColumn(
            添加匹配输入,
            "__尺码输入",
            {
                "__尺码分类",
                "__尺码CAB",
                "__尺码版本",
                "__尺码L",
                "__尺码W",
                "__尺码H",
                "__尺码T",
                "__尺码匹配键"
            },
            {
                "__尺码分类",
                "__尺码CAB",
                "__尺码版本",
                "__尺码L",
                "__尺码W",
                "__尺码H",
                "__尺码T",
                "__尺码匹配键"
            }
        ),


    //==================================================
    // 12. 相同 分类 + CAB + 版本 + L/W/H 只计算一次
    //
    // 多个年份、车型记录尺寸完全相同时，
    // 不再逐行重复运行匹配函数
    //==================================================

    唯一匹配输入 =
        Table.Buffer(
            Table.Distinct(
                Table.SelectColumns(
                    展开匹配输入,
                    {
                        "__尺码匹配键",
                        "__尺码分类",
                        "__尺码CAB",
                        "__尺码版本",
                        "__尺码L",
                        "__尺码W",
                        "__尺码H",
                        "__尺码T"
                    }
                )
            )
        ),

    添加唯一匹配结果 =
        Table.AddColumn(
            唯一匹配输入,
            "__尺码匹配结果",
            each
                计算尺码(
                    [__尺码分类],
                    [__尺码CAB],
                    [__尺码版本],
                    [__尺码L],
                    [__尺码W],
                    [__尺码H],
                    [__尺码T]
                ),
            type record
        ),

    展开唯一匹配结果 =
        Table.ExpandRecordColumn(
            添加唯一匹配结果,
            "__尺码匹配结果",
            {
                "自动尺码",
                "自动长度余量",
                "候选",
                "原因",
                "相差数值"
            },
            {
                "自动尺码",
                "自动长度余量",
                "候选",
                "原因",
                "相差数值"
            }
        ),

    唯一匹配结果表 =
        Table.Buffer(
            Table.SelectColumns(
                展开唯一匹配结果,
                {
                    "__尺码匹配键",
                    "自动尺码",
                    "自动长度余量",
                    "候选",
                    "原因",
                    "相差数值"
                }
            )
        ),


    //==================================================
    // 13. 将匹配结果合并回完整源表
    //==================================================

    合并匹配结果 =
        Table.NestedJoin(
            展开匹配输入,
            {
                "__尺码匹配键"
            },
            唯一匹配结果表,
            {
                "__尺码匹配键"
            },
            "__尺码合并结果",
            JoinKind.LeftOuter
        ),

    展开最终结果 =
        Table.ExpandTableColumn(
            合并匹配结果,
            "__尺码合并结果",
            {
                "自动尺码",
                "自动长度余量",
                "候选",
                "原因",
                "相差数值"
            },
            {
                "自动尺码",
                "自动长度余量",
                "候选",
                "原因",
                "相差数值"
            }
        ),


    //==================================================
    // 14. 删除内部辅助列
    //==================================================

    清理辅助列 =
        Table.RemoveColumns(
            展开最终结果,
            {
                "__尺码分类",
                "__尺码CAB",
                "__尺码版本",
                "__尺码L",
                "__尺码W",
                "__尺码H",
                "__尺码T",
                "__尺码匹配键"
            },
            MissingField.Ignore
        )


in
    清理辅助列