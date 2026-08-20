let

    尺寸源 = "\\NAS8824B4\Public\PQData\all_cars_data\source\车型尺寸库.csv",
    子车系源 = "\\NAS8824B4\Public\PQData\all_cars_data\source\子车系维护表.csv",

    //==================================================
    // 1. 读取车型尺寸库 CSV
    //==================================================

    尺寸表 =
        Csv.Document(
        File.Contents(尺寸源),
        [
            Delimiter = ",",
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),

    提升的标题 =
        Table.PromoteHeaders(
            尺寸表,
            [
                PromoteAllScalars = true
            ]
        ),


    //==================================================
    // 2. 尽早只保留最终需要的源表字段
    //
    // 避免后续步骤持续携带：
    // 参考车型、备注、迭代状态以及多余空列
    //==================================================

    源保留必要列 =
        Table.SelectColumns(
            提升的标题,
            {
                "DIMENSION-ID",
                "MAKE",
                "MODEL",
                "版本",
                "代际",
                "YEAR",
                "分类",
                "结构",
                "CAB",
                "BED",
                "L-IN",
                "W-IN",
                "H-IN"
            },
            MissingField.UseNull
        ),

    更改的类型 =
        Table.TransformColumnTypes(
            源保留必要列,
            {
                {"DIMENSION-ID", type text},
                {"MAKE", type text},
                {"MODEL", type any},
                {"版本", type text},
                {"代际", type text},
                {"YEAR", type any},
                {"分类", type text},
                {"结构", type text},
                {"CAB", type any},
                {"BED", type any},
                {"L-IN", type number},
                {"W-IN", type number},
                {"H-IN", type number}
            }
        ),


    //==================================================
    // 3. 一次性生成毫米字段（1 英寸 = 25.4 毫米）
    //
    // 使用一个 Record 列，一次遍历生成三个毫米字段，
    // 不再连续进行三次 Table.AddColumn
    //==================================================

    添加毫米记录 =
        Table.AddColumn(
            更改的类型,
            "__毫米尺寸",
            each
                let
                    lmm =
                        if [#"L-IN"] = null then
                            null
                        else
                            [#"L-IN"] * 25.4,

                    wmm =
                        if [#"W-IN"] = null then
                            null
                        else
                            [#"W-IN"] * 25.4,

                    hmm =
                        if [#"H-IN"] = null then
                            null
                        else
                            [#"H-IN"] * 25.4
                in
                    [
                        #"L-MM" = lmm,
                        #"W-MM" = wmm,
                        #"H-MM" = hmm,
                        #"T-MM" =
                            if wmm = null or hmm = null then
                                null
                            else
                                wmm + 2 * hmm
                    ],
            type record
        ),

    展开毫米记录 =
        Table.ExpandRecordColumn(
            添加毫米记录,
            "__毫米尺寸",
            {
                "L-MM",
                "W-MM",
                "H-MM",
                "T-MM"
            },
            {
                "L-MM",
                "W-MM",
                "H-MM",
                "T-MM"
            }
        ),


    //==================================================
    // 4. 读取并清洗子车系维护表
    //==================================================

    子表原始 =
        Csv.Document(
            File.Contents(子车系源),
            [
                Delimiter = ",",
                Encoding = 65001,
                QuoteStyle = QuoteStyle.Csv
            ]
        ),

    子表标题 =
        Table.PromoteHeaders(
            子表原始,
            [PromoteAllScalars = true]
        ),

    子表保留列 =
        Table.SelectColumns(
            子表标题,
            {"Year", "主车型", "结构", "版本", "候选车型"},
            MissingField.UseNull
        ),

    子表清洗 =
        Table.TransformColumns(
            子表保留列,
            {
                {"Year", each try Int64.From(_) otherwise null, Int64.Type},
                {"主车型", each Text.Trim(if _ = null then "" else Text.From(_)), type text},
                {"结构", each Text.Trim(if _ = null then "" else Text.From(_)), type text},
                {"版本", each Text.Trim(if _ = null then "" else Text.From(_)), type text},
                {"候选车型", each Text.Trim(if _ = null then "" else Text.From(_)), type text}
            }
        ),

    子表有效 =
        Table.SelectRows(
            子表清洗,
            each [Year] <> null and [主车型] <> "" and [候选车型] <> ""
        ),


    //==================================================
    // 5. 拆分候选车型并聚合
    //
    // 候选车型可能含 ";" 分隔的多个值，
    // 拆分后按 Year + 主车型 + 结构 + 版本 重新聚合
    //==================================================

    子表拆分候选 =
        Table.ExpandListColumn(
            Table.TransformColumns(
                子表有效,
                {
                    {
                        "候选车型",
                        (v) => List.Transform(Text.Split(v, ";"), each Text.Trim(_)),
                        type list
                    }
                }
            ),
            "候选车型"
        ),

    子表拆分后有效 =
        Table.SelectRows(
            子表拆分候选,
            each [候选车型] <> ""
        ),

    子表去重 =
        Table.Distinct(
            子表拆分后有效,
            {"Year", "主车型", "结构", "版本", "候选车型"}
        ),

    子表聚合 =
        Table.Group(
            子表去重,
            {"Year", "主车型", "结构", "版本"},
            {
                {
                    "__候选",
                    each Text.Combine(List.Sort(List.Distinct([候选车型])), "; "),
                    type text
                }
            }
        ),

    子表缓存 =
        Table.Buffer(子表聚合),


    //==================================================
    // 6. 为主表生成辅助匹配字段并计算 SUB-MODEL
    //
    // 通过 Year ∈ [年起, 年止] + 主车型 + 结构 + 版本
    // 关联子车系维护表
    //==================================================

    添加源辅助字段 =
        Table.AddColumn(
            展开毫米记录,
            "__源辅助",
            each
                let
                    makeText = Text.Trim(if [MAKE] = null then "" else Text.From([MAKE])),
                    modelText = Text.Trim(if [MODEL] = null then "" else Text.From([MODEL])),

                    主车型 =
                        Text.Combine(
                            List.Select({makeText, modelText}, each _ <> ""),
                            " "
                        ),

                    结构 = Text.Trim(if [结构] = null then "" else Text.From([结构])),
                    版本 = Text.Trim(if [版本] = null then "" else Text.From([版本])),

                    yrText = Text.Trim(if [YEAR] = null then "" else Text.From([YEAR])),
                    yrNorm =
                        Text.Replace(
                            Text.Replace(
                                Text.Replace(
                                    Text.Replace(yrText, "/", "-"),
                                    "–", "-"
                                ),
                                "—", "-"
                            ),
                            "－", "-"
                        ),
                    yrParts =
                        List.Select(
                            List.Transform(Text.Split(yrNorm, "-"), each Text.Trim(_)),
                            each _ <> ""
                        ),
                    年起 =
                        if List.Count(yrParts) = 0 then null
                        else try Number.From(yrParts{0}) otherwise null,
                    年止 =
                        if List.Count(yrParts) = 0 then null
                        else if List.Count(yrParts) = 1 then 年起
                        else try Number.From(yrParts{List.Count(yrParts) - 1}) otherwise null
                in
                    [
                        __主车型 = 主车型,
                        __结构 = 结构,
                        __版本 = 版本,
                        __年起 = 年起,
                        __年止 = 年止
                    ],
            type record
        ),

    展开源辅助字段 =
        Table.ExpandRecordColumn(
            添加源辅助字段,
            "__源辅助",
            {"__主车型", "__结构", "__版本", "__年起", "__年止"},
            {"__主车型", "__结构", "__版本", "__年起", "__年止"}
        ),


    //==================================================
    // 7. 通过 主车型 + 结构 + 版本 关联子车系表
    //    再通过 Year ∈ [年起, 年止] 过滤年份范围
    //    将范围内的候选值汇总到单个单元格，避免展开造成主表行复制
    //==================================================

    合并子表 =
        Table.NestedJoin(
            展开源辅助字段,
            {"__主车型", "__结构", "__版本"},
            子表缓存,
            {"主车型", "结构", "版本"},
            "__子表匹配",
            JoinKind.LeftOuter
        ),

    添加SUBMODEL =
        Table.AddColumn(
            合并子表,
            "SUB-MODEL",
            each
                let
                    年起 = [__年起],
                    年止 = [__年止],
                    matched =
                        if 年起 = null or 年止 = null then
                            Table.FirstN([__子表匹配], 0)
                        else
                            Table.SelectRows(
                                [__子表匹配],
                                (r) => r[Year] >= 年起 and r[Year] <= 年止
                            ),
                    候选列表 =
                        if Table.IsEmpty(matched) then
                            {}
                        else
                            List.Combine(
                                List.Transform(
                                    matched[__候选],
                                    (v) =>
                                        List.Transform(
                                            Text.Split(if v = null then "" else v, ";"),
                                            each Text.Trim(_)
                                        )
                                )
                            ),
                    有效候选 = List.Select(候选列表, each _ <> "")
                in
                    Text.Combine(List.Sort(List.Distinct(有效候选)), "; "),
            type text
        ),


    //==================================================
    // 8. 删除辅助字段
    //==================================================

    删除辅助列 =
        Table.RemoveColumns(
            添加SUBMODEL,
            {"__主车型", "__结构", "__版本", "__年起", "__年止", "__子表匹配"},
            MissingField.Ignore
        ),


    //==================================================
    // 9. 最终列顺序
    //==================================================

    最终列 =
        Table.SelectColumns(
            删除辅助列,
            {
                "MAKE",
                "MODEL",
                "SUB-MODEL",
                "版本",
                "代际",
                "YEAR",
                "分类",
                "结构",
                "CAB",
                "BED",
                "L-MM",
                "W-MM",
                "H-MM",
                "T-MM",
                "DIMENSION-ID"
            },
            MissingField.UseNull
        )
in
    最终列
