let

    销量源 = "\\NAS8824B4\Public\PQData\all_cars_data\source\atom_sales.csv",
    尺寸源 = "\\NAS8824B4\Public\PQData\all_cars_data\source\车型尺寸库.csv",


    //==================================================
    // 1. 读取销量表 → 提取 DIMENSION-ID → 按 DIMENSION-ID 汇总
    //==================================================

    销量表原始 =
        Csv.Document(
            File.Contents(销量源),
            [
                Delimiter = ",",
                Encoding = 65001,
                QuoteStyle = QuoteStyle.Csv
            ]
        ),

    销量表 = ref_atom_sales

    // atom_record_id 去掉 "|ATOM_YEAR=..." 后缀 = DIMENSION-ID
    添加DIMID =
        Table.AddColumn(
            销量表,
            "DIMENSION-ID",
            each
                let
                    id = if [atom_record_id] = null then "" else Text.From([atom_record_id])
                in
                    Text.Split(id, "|ATOM_YEAR="){0},
            type text
        ),

    销量类型 =
        Table.TransformColumnTypes(
            添加DIMID,
            {
                {"预估销量", type number},
                {"DIMENSION-ID", type text}
            }
        ),

    // 同一个 DIMENSION-ID 对应多个 ATOM_YEAR 行，求和
    按DIMID汇总 =
        Table.Group(
            销量类型,
            {"DIMENSION-ID"},
            {
                {"销量合计", each List.Sum([预估销量]), type nullable number}
            }
        ),


    //==================================================
    // 2. 读取车型尺寸库（仅取 DIMENSION-ID）
    //==================================================

    尺寸表原始 =
        Csv.Document(
            File.Contents(尺寸源),
            [
                Delimiter = ",",
                Encoding = 65001,
                QuoteStyle = QuoteStyle.Csv
            ]
        ),

    尺寸表 =
        Table.PromoteHeaders(
            尺寸表原始,
            [PromoteAllScalars = true]
        ),

    尺寸仅DIMID =
        Table.SelectColumns(
            尺寸表,
            {"DIMENSION-ID"},
            MissingField.UseNull
        ),


    //==================================================
    // 3. 左连接：车型尺寸库 ← 销量汇总
    //==================================================

    合并销量 =
        Table.NestedJoin(
            尺寸仅DIMID,
            {"DIMENSION-ID"},
            按DIMID汇总,
            {"DIMENSION-ID"},
            "__销量",
            JoinKind.LeftOuter
        ),

    展开销量 =
        Table.ExpandTableColumn(
            合并销量,
            "__销量",
            {"销量合计"},
            {"销量合计"}
        ),

    填充空销量 =
        Table.ReplaceValue(
            展开销量,
            null, 0,
            Replacer.ReplaceValue,
            {"销量合计"}
        )

in
    填充空销量
