# hard_pagefree 参考答案（页码无关版）

共 20 题；标 `revision: page-free-20261110` 的为题面改写项。

## ZT2H-001 · 按表 19.6 的情景 2（两架 300 座合计生产 1000 架、600 座只生产 500 架），600 座方案的采购成本与 DOC/ASM 相对两架 300 座各差多少？请用表中数值验算这两个百分比，并说明为什么开发成本相同、采购成本却变贵。

**题型**　计算　**可答**　是

**参考答案要点**

- 采购成本 195.01 对 178.84（百万美元，1994 年），600 座高 9.0%（约 9.04%）。
- DOC 5.39 对 5.16，600 座低 4.3%（约 4.27%）。
- 两情景开发成本均为 5.94 对 3.35（十亿美元，1994 年），产量从 1000 减到 500 使单机分摊的开发成本翻倍。

**原文证据**

- **4052X_19.pdf** · 切片序号 18 · 切片 ID `02ff1e53-0e5c-41fb-91d2-b516bd666cc7`

  > Production run; Two 300-seat=1000; One 600-seat=500 Development B1994; Two 300-seat=3.35; One 600-seat=5.94 PurchasecostM 1994; Two 300-seat=178.84; One 600-seat=195.01 Direct operating cost; Two 300-seat=5.39; One 600-seat=5.16

- **4052X_19.pdf** · 切片序号 14 · 切片 ID `64ca4ea3-3c2e-4045-9c42-ad525d8e5350`

  > different production volumes and rates, the 600-seat aircraft is seen to be 9.0% more expensive than two 300-seat designs and the DOC/ASM advantage is reduced 4.3%.


## ZT2H-002 · 4052X_07 的初始起飞重量算例取商载 17 100 kg、使用空重分数 51%、燃油分数 21.4%，得 M_TO≈61 957 kg。若把使用空重分数改为 52%、其余不变，按同一质量方程 M_TO 约为多少？比原结果高多少？

**题型**　计算　**可答**　是

**参考答案要点**

- 用 M_TO = M_UL / (1 − M_E/M_TO − M_F/M_TO) 计算。
- 17 100/(1−0.52−0.214) ≈ 64 300 kg（64 286 kg）。
- 比 61 957 kg 高约 2 300 kg（约 +3.7%）。

**原文证据**

- **4052X_07.pdf** · 切片序号 19 · 切片 ID `7d0d5602-6adc-4741-8386-e020e12ccefc`

  > M_TO = 17100/(1 - 0.51 - 0.214) = 61957 kg (approx. 62000). The estimation of M_TO is very sensitive to the prediction of empty and fuel mass ratios.


## ZT2H-003 · 70 座基准若改为 6 并列 84 座、起飞质量不变，航程会降到多少？若仍要求 1250 nm，84 座与 96 座的 MTOM 和 DOC/ASM 相对 70 座如何变化？机翼面积是否改变？

**题型**　计算　**可答**　是

**参考答案要点**

- 起飞质量不变时燃油减少，航程降到 578 nm。
- MTOM 分别约增加 2 t 与 4 t；机翼面积不变，翼载升高、巡航升阻比提高。
- DOC/ASM 分别比基准低 15% 与 24.6%。

**原文证据**

- **4052X_16.pdf** · 切片序号 53 · 切片 ID `4d33543c-c5f1-4ac0-a56f-947355145bf4`

  > If take-off mass remains unchanged the fuel mass is reduced and the range decreases substantially to 578 nm.

- **4052X_16.pdf** · 切片序号 58 · 切片 ID `f6929b9b-c26a-49b5-96c6-930ae5ceb6a5`

  > Maximum take-off mass increases by approximately two and four tonnes respectively compared with the 70-seat model. Wing area remains unchanged thus increasing wing loading and hence cruise lift/drag ratio. With 84 passengers, the DOC per ASM is 15% below the baseline aircraft. For 96 passengers, DOC per ASM is 24.6% below the baseline aircraft.


## ZT2H-004 · 按表 9.4，涵道比从 3.0 增到 13.0 时推重比和短舱直径各怎样变化？四种发动机中短舱最长的是哪一个？

**题型**　表格　**可答**　是

**参考答案要点**

- 推重比 5.12→4.03→3.83→3.17，随涵道比增大单调下降（约 38%）。
- 短舱直径 3.81→4.11→4.74 m（涵道比 3.0 未给）。
- 短舱最长的是涵道比 8.0（9.14 m，全长短舱），不是涵道比最大的 13.0（5.63 m）。

**原文证据**

- **4052X_09.pdf** · 切片序号 49 · 切片 ID `d93417bd-eea0-45fd-a672-a84405ac3d6e`

  > Bypass ratio 3.0 6.5 8.0 13.0; Thrust/engine weight 5.12 4.03 3.83 3.17; Nacelle length (m) 2.405 5.94 9.14* 5.63; Nacelle diameter (m) - 3.81 4.11 4.74. \* Full length nacelle.


## ZT2H-005 · 按表 17.1，EH101 与 UH-60A 的满载质量各是多少？用满载质量除以全长，谁的单位长度质量更高？

**题型**　计算　**可答**　是

**参考答案要点**

- EH101 14 288 kg、UH-60A 9 979 kg。
- EH101 约 756 kg/m（14 288/18.90），UH-60A 约 792 kg/m（9 979/12.60）。
- UH-60A 的单位长度质量更高。

**原文证据**

- **4052X_17.pdf** · 切片序号 7 · 切片 ID `aef7f100-bb57-4d28-aa93-f885a08476cd`

  > EH Industries EH101 18.90 4.52 5.22 9000/14288; Sikorsky UH-60A Black Hawk 12.60 3.56 3.76 5216/9979 (Overall length m; Width m; Height m; Mass unloaded/loaded kg).


## ZT2H-006 · 为什么民机客舱直径一旦确定就难以更改，而机身长度却能在后续型别中加长？长径比过低与过高各有什么代价？

**题型**　多跳　**可答**　是

**参考答案要点**

- 直径固定后实际上无法更改；长度可通过插入 plug 段加长，属机型自然发展计划的一部分。
- 长径比过低：有机身阻力代价，但为日后加长留有余地。
- 长径比过高：细长管状结构，可能出现动力结构不稳定，并限制后续加长。

**原文证据**

- **4052X_05.pdf** · 切片序号 7 · 切片 ID `b96e13ae-c2bb-40c6-a638-0fade75efd2a`

  > Two geometrical parameters specify the passenger cabin (diameter and length). Of these the cabin diameter is the most critical because once fixed it is impractical to change. On the other hand, part of the natural development programme of the aircraft will be to stretch the fuselage by adding extra length ('plugs') to increase capacity.

- **4052X_05.pdf** · 切片序号 76 · 切片 ID `dd442c55-6611-48ce-9c61-5170486e2337`

  > A low ratio (leading to a stubby fuselage shape) will result in a drag penalty but will offer potential for future stretch. A high fineness ratio gives a long thin tubular structure which may suffer from dynamic structural instability and will restrict future developments (stretch).


## ZT2H-007 · 参数研究为什么一次只改变一两个变量？两变量时“九点研究”怎样组织、结果怎样读出？基准设计点为什么常取中心点？

**题型**　多跳　**可答**　是

**参考答案要点**

- 为使多变量设计问题可控，每次只考虑一两个变量。
- 两变量取 3×3=9 个点，每点完成整机设计再画 carpet plot（例：x=wing loading、y=thrust loading、目标为最大起飞重量）。
- 基准点常取中心以同时显示正负变化；可再加第三变量（如载客数）形成一组 carpet。

**原文证据**

- **4052X_13.pdf** · 切片序号 3 · 切片 ID `51928f96-772f-4164-8628-f947f44de130`

  > it is preferable to consider only one or two variables in any specific study ... For a parametric investigation involving two variables the classical nine-point study can be used. In a particular aircraft design study, variable x could be 'wing loading', variable y the 'thrust loading' and the objective function could be 'aircraft maximum take-off weight'.

- **4052X_13.pdf** · 切片序号 4 · 切片 ID `bff6e0d0-cb26-4646-86ab-8f5b119c70f9`

  > The 'baseline design point' is often chosen as the centre point in the nine-point study to show positive and negative changes. In association with the x and y variables a third parameter could be varied ... Such three-variable studies produce a series of carpet plots.


## ZT2H-008 · 发动机的四种推力额定各是什么？哪两个由合格审定型号试验确定？起飞额定每次飞行允许多久，何时可延长？最大连续为什么不在正常飞行中使用？

**题型**　事实　**可答**　是

**参考答案要点**

- 起飞、最大连续、最大爬升、最大巡航四种额定。
- 起飞与最大连续由发动机合格审定型号试验确定。
- 起飞额定通常每次飞行 5 分钟，特殊情况可延至 10 分钟。
- 最大连续仅用于严重应急，正常使用会不可接受地缩短发动机寿命。

**原文证据**

- **4052X_09.pdf** · 切片序号 23 · 切片 ID `53eff86f-defc-4ca2-bc4b-e5bb94e092f8`

  > Take-off rating ... normally cleared for only five minutes per flight but this can be increased to ten minutes to meet special cases. Maximum continuous ... only used in the event of a serious emergency condition. Although it could be used for normal operations the engine service life would be unacceptably reduced. Take-off and maximum continuous ratings are determined by the engine certification type test.


## ZT2H-009 · 制造商按“现金基础”报出的 DOC 与总额法差在哪？他们为什么这样做？引用厂商或媒体公布的 DOC 时要注意什么？

**题型**　推理　**可答**　是

**参考答案要点**

- 现金基础不含飞机固定费用（standing charge）。
- 理由：使 DOC 数字显著降低；且航空公司按年租赁日益普遍，该项进入公司资产负债表的另一部分。
- 引用外部 DOC 时必须确认是总额法还是现金法，否则方案比较会失真。

**原文证据**

- **4052X_12.pdf** · 切片序号 33 · 切片 ID `06bfb577-3b9b-4cdc-b96b-59b9ac36524c`

  > Some manufacturers quote all the above cost parameters on a cash basis, by which they mean that the aircraft standing charge is not included in the total cost ... Be careful when using quoted DOC figures from manufacturers or the aeronautical press to understand if the total or cash method of calculating the values has been used.


## ZT2H-010 · 查书末索引：trim drag、carpet plots、type record 的 overview 分别指向哪一页？

**题型**　索引　**可答**　是

**参考答案要点**

- trim drag 指向 176 页。
- carpet plots 指向 327 页。
- type record 的 overview 指向 336 页。

**原文证据**

- **4052X_indx.pdf** · 切片序号 8 · 切片 ID `662d50ee-739f-4c44-a9a6-86bdb7c84db9`

  > trim drag 176 ... type record ... overview 336

- **4052X_indx.pdf** · 切片序号 6 · 切片 ID `7ba79393-9b80-4d66-b341-ad038c2934df`

  > carpet plots 327


## ZT2H-011 · 按目录，第 13 章 Parametric Studies 的前一章和后一章各是什么？本章自身包含哪两个小节？

**题型**　目录　**可答**　是

**参考答案要点**

- 前一章为第 12 章 Aircraft Cost Estimations，后一章为第 14 章 Aircraft Type Specification。
- 本章两节：13.1 Introduction、13.2 Example。

**原文证据**

- **4052X_toc.pdf** · 切片序号 2 · 切片 ID `48c3fa26-d148-45cf-95ea-24a5f46bf38d`

  > 12. Aircraft Cost Estimations 302 ... 13. Parametric Studies 326 13.1 Introduction 327 13.2 Example 329 14. Aircraft Type Specification 335


## ZT2H-012 · 按目录，第 9 章的 9.10、9.11、9.12 分别是什么小节？三者的主题分别关于什么？

**题型**　目录　**可答**　是

**参考答案要点**

- 9.10 Rules for Scaling an Engine（发动机缩放规则）。
- 9.11 Engine Price（发动机价格）。
- 9.12 Maintenance Costs（维护成本）。

**原文证据**

- **4052X_toc.pdf** · 切片序号 1 · 切片 ID `2df9edcf-4d22-44ee-953a-afdd3a895968`

  > 9.9 Derivation of Pod Geometry 197 9.10 Rules for Scaling an Engine 201 9.11 Engine Price 201 9.12 Maintenance Costs 202 9.13 Engine Data 202


## ZT2H-013 · According to the Chinese helicopter design handbook (Vol. 19), which engine characteristics must be given as the main powerplant general parameters, and which other powerplant items are listed alongside the engine?

**题型**　跨语言　**可答**　是

**参考答案要点**

- 发动机：功率、耗油率、加（减）速特性、尺寸和重量。
- 并列项还包括：传动系统（传输功率限制、尺寸、重量）、进气道/排气管、燃油系统、主减速器滑油冷却、灭火系统、起动供电与发动机状态监控。

**原文证据**

- **公开+第19册(直升机设计).pdf** · 切片序号 62 · 切片 ID `e2523aa7-bdf1-4e60-ad75-6d41bac1105b`

  > 2.6.1.1 动力装置主要总体参数 a. 发动机：功率、耗油率、加(减)速特性、尺寸和重量；b. 传动系统：传输的功率限制，尺寸和重量；c. 发动机的进气道、排气管装置：尺寸和重量；d. 燃油系统……g. 起动供电系统及发动机工作状况的信息传输与监控系统


## ZT2H-014 · What numerical limits does the same handbook give for minimum engine specific fuel consumption, engine power-to-weight ratio, and transmission power-to-weight ratio?

**题型**　跨语言　**可答**　是

**参考答案要点**

- 最低耗油率不大于 0.27 kg/(h·kW)。
- 发动机功率重量比不小于 7.5 kW/kg。
- 传动系统功率重量比不小于 4 kW/kg。

**原文证据**

- **公开+第19册(直升机设计).pdf** · 切片序号 63 · 切片 ID `77b70c5d-2202-4fd8-8ccc-cac2cde7a14b`

  > a. 要求发动机耗油率低，最低耗油率一般不大于 0.27,kg/(h·kW)。b. 要求重量轻，体积小，功率重量比一般不小于 7.5kW/kg。c. ……传输的功率与重量之比不小于 4kW/kg。


## ZT2H-015 · In the New Large Aircraft study, how are seats arranged on the main and upper decks of the single-fuselage twin-deck layout, and why must the layout be multi-deck?

**题型**　跨语言　**可答**　是

**参考答案要点**

- 主层 14 座，3–4–4–3；上层 12 座，2–4–4–2。
- 单机身要把机身长度控制在可接受范围需 24–28 座并排，这必然导致多甲板布局。

**原文证据**

- **4052X_18.pdf** · 切片序号 3 · 切片 ID `fee7ea4f-32e5-4b0c-af24-e2743a845d66`

  > The single-fuselage design proved the most difficult since this requires 24–28 seats abreast to maintain acceptable fuselage length ... Figure 18.1 shows that the main deck has 14 seats arranged 3–4–4–3, whilst the upper deck has 12 seats in 2–4–4–2 configuration.


## ZT2H-016 · 按书中的折旧公式，若残值为初始价格的 15%、折旧期为 12 年，年折旧率是多少？请写出计算式。

**题型**　计算　**可答**　是

**参考答案要点**

- 计算式 [(P − 0.15P)/P]/(12/100)。
- 结果 7.08%（0.85/0.12）。

**原文证据**

- **4052X_12.pdf** · 切片序号 16 · 切片 ID `3506f0b0-857a-4a8c-b270-b6f08c9674e4`

  > [(initial price - residual value)/initial price]/(depreciation period/100) ... [(P - 0.15P)/P]/[12/100] = 7.08%


## ZT2H-017 · 能否用 Fig. 12.3 的“价格—空机重量”图线估算 70–100 座支线客机的价格？书中对这类图线和价格数据有哪些限制？

**题型**　边界　**可答**　是

**参考答案要点**

- 不宜直接用于具体机型：该图覆盖 100–500 座，范围过宽，应在目标吨位附近另做分析。
- 价格数据须按通胀与汇率归一化；也可考虑用最大起飞重量、速度、载客数等替代空机重量作参数。
- 价格还受市场、竞争、政治、补偿贸易等非工程因素影响，不能仅由重量推出。

**原文证据**

- **4052X_12.pdf** · 切片序号 19 · 切片 ID `d4494f3e-dd49-4677-a815-64fca6decd59`

  > Such a crude plot should not be used for particular aircraft analysis as the range of aircraft size covered is too extensive (100–500 passengers) ... Care must be taken when using price data to normalise the values to account for inflation and the devaluation of currencies.

- **4052X_12.pdf** · 切片序号 16 · 切片 ID `3506f0b0-857a-4a8c-b270-b6f08c9674e4`

  > The estimation of aircraft price is complicated by many non-engineering factors (e.g. market conditions, competition, politics, off-set trade agreements, international collaboration on manufacture, etc.).


## ZT2H-018 · 该书把适航性分成哪几个标题？环境方面主要监管哪两项，它们主要与什么有关？

**题型**　事实　**可答**　是

**参考答案要点**

- 结构完整性、系统完整性、运行完整性、坠撞安全性四类，且总体构型上相互依赖。
- 环境监管主要是噪声与排放。
- 两者主要与发动机设计和飞行剖面有关。

**原文证据**

- **4052X_04.pdf** · 切片序号 1 · 切片 ID `27e58652-e196-45e4-8ae5-48493052bcf0`

  > Although airworthiness is described under the separate headings of structural integrity, system integrity, operation integrity and crashworthiness there is considerable interdependence ... noise and emissions are the main regulatory issues which affect the design of the aircraft. Both are largely associated with engine design aspects and aircraft flight


## ZT2H-019 · 《Civil Jet Aircraft Design》表 1.1 中 2010 年的定期航班客运量（passenger-km）是多少？

**题型**　信息不足　**可答**　否

**参考答案要点**

- 无法确定：表 1.1 只到 2000 年（1970、1980、1990、2000 四列）。
- 需补充 2010 年的 ICAO 或其他统计资料。

**原文证据**

- **4052X_01.pdf** · 切片序号 13 · 切片 ID `bef1aacd-c475-4f6d-ae7e-4a75cee25ef0`

  > Table 1.1 Historical traffic data (source ICAO) Column 2=1970; Column 3=1980; Column 4=1990; Column 5=2000 ... Passenger-km (billions) 382 929 1654 2830


## ZT2H-020 · 总体2 里那架 70 座先进支线客机的首飞日期、首架交付客户和启动用户分别是什么？

**题型**　信息不足　**可答**　否

**参考答案要点**

- 无法确定：该案例是设计研究（规格→估算→优化→增长型），不含首飞、交付与客户记录。
- 需补充该项目的试飞报告、交付记录或启动用户公告。

**原文证据**

- **4052X_16.pdf** · 切片序号 58 · 切片 ID `f6929b9b-c26a-49b5-96c6-930ae5ceb6a5`

  > This chapter described the design of an advanced regional airliner from the development of a specification, through to prediction of initial estimates and computation of the baseline design.

