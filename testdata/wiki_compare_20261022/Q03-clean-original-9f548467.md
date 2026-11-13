## 结论

**这个推论不成立，两处推论都过于乐观。**

1. **“能维持基本姿态显示”只是退化模式的设计目标，并不构成对更高性能应用的许可。** 若要让自动驾驶、HUD、SVS 继续工作，必须**逐项证明**退化模式满足这些应用的性能与适航要求；证明不了，就必须在设计中让退化模式**不驱动**这些应用。
2. **多型号批准（AML-STC）的本质是“共享基线数据 + 逐型号证实”，并非免除逐型号验证。** 对涉及控制输入的系统（自动驾驶就是原文所举的例子），原文明确要求**不论是否共享基线数据**，都要逐型号设计与试验<kb doc="AC_20-180.pdf" chunk_id="2441846f-0493-4683-b94c-52cfa4f7b2b2" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

## 一、退化模式能否承载 AP / HUD / SVS

第3.3节是核心条款：“Evaluate the suitability of the degraded mode performance for other applications, as it **may not be sufficient for higher performance applications, such as an autopilot, head-up display (HUD), or a synthetic vision system (SVS) display**. If the analysis shows the degraded mode is not sufficient for other aircraft applications, **ensure the degraded mode does not drive those particular aircraft applications**.”<kb doc="AC_20-181.pdf" chunk_id="fac2ef92-4b92-4c9c-a33d-75819a062b48" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />

第3节本身也提示：RTCA DO-334 认为退化模式可支持巡航、爬升、下降、等待与仪表进近，但“**may not be acceptable for autopilot operation or certain flight procedures**”，并要求在适航审定期间评估其设计与运行适用性<kb doc="AC_20-181.pdf" chunk_id="4fed905d-5e4c-4dd1-95de-8dec7d9116b3" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

| 应用 | 能否在退化模式下继续工作 | 依据 |
|---|---|---|
| 主姿态、航向、转弯率、侧滑显示 | 可以（这就是定义目的） | <kb doc="AC_20-181.pdf" chunk_id="fac2ef92-4b92-4c9c-a33d-75819a062b48" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 自动驾驶 | 默认不可以；除非另有演示，且涉及控制输入的系统须逐型号试验 | <kb doc="AC_20-181.pdf" chunk_id="4fed905d-5e4c-4dd1-95de-8dec7d9116b3" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-180.pdf" chunk_id="2441846f-0493-4683-b94c-52cfa4f7b2b2" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| HUD | A1–A5 均能驱动基本姿态仪，但“HUD 与自动驾驶集成”可能需要更高精度类别 | <kb doc="AC_20-181.pdf" chunk_id="9421756e-5bfb-4eee-ba7e-5e4db3f98447" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| SVS | 属第3.3节列举的“更高性能应用”，须证明足够，否则不得驱动 | <kb doc="AC_20-181.pdf" chunk_id="fac2ef92-4b92-4c9c-a33d-75819a062b48" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| EFVS / FMS 集成 | 可能需要更高航向精度类别；H10/H11 仅限存在磁异常时的短期使用 | <kb doc="AC_20-181.pdf" chunk_id="0ff67505-a594-4b87-b2ea-81af9ee021b8" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |

还需同时满足以下限制：退化模式须按 §§23.1301、25.1301、27.1301 或 29.1301 判定其对**预期航空器与运行模式**是否可接受；它面向 Part 23 与“non-appendix B”Part 27 这类较小、较低性能的航空器，**不得**作为减少所需姿态仪表数量的依据；手册规定的包线或时间限制须写入飞行手册；地面（初始起动或发动机起动后）不得启用<kb doc="AC_20-181.pdf" chunk_id="ece7b269-0d76-49be-be89-7f89b29679a9" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。操作说明还须写明“哪些系统应用会丢失（例如自动驾驶）”以及退化模式下可做的机动限制<kb doc="AC_20-181.pdf" chunk_id="fac2ef92-4b92-4c9c-a33d-75819a062b48" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

试验层面：可在飞行中禁用（如拔断路器）的触发须做飞行试验；不可在飞行中评估者可用分析或仿真，但须覆盖机组工作负荷、正常 IFR 机动（爬升、下降、标准速率转弯、仪表进近）及对机组控制能力的影响；后续安装须针对独特飞行包线或运行条件演示，A/RFMS 必须载明性能特征与限制<kb doc="AC_20-181.pdf" chunk_id="770bf72f-942a-4298-acfe-264546d3acf9" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

## 二、多型号批准并未消除逐型号验证

**1. 定义层面。** AML-STC 是“multi-model approval method”，其价值在于把一组符合性数据定为 baseline data 适用于多个机型<kb doc="AC_20-180.pdf" chunk_id="65457139-ce66-49c4-81d2-573b40d7400c" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；但它“is intended for installations that are identical or similar and that share baseline data”，一旦型号间安装差异导致相似性与基线数据无法建立，“AML-STC is not the proper method of approval”<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

**2. 明确规定不是一揽子批准。** 每个型号都须表明符合 §21.20 并提供相应数据（型号设计、证实性数据、飞行手册补充）；“Whether this data is generated from testing … or re-submitted from a previous approval, **substantiation for each additional aircraft model is required**”；与既有批准机型有差异时还须补充证实；“**The AML-STC is not meant to be a blanket approval by allowing additional models without further substantiation.**”<kb doc="AC_20-180.pdf" chunk_id="3705aad7-9fcf-4093-9520-acd528861605" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />

**3. 必须逐型号确定的项目。** 受影响区域的认证基础与修正案水平逐型号确定；飞行手册补充按 §21.5 逐型号适用<kb doc="AC_20-180.pdf" chunk_id="3705aad7-9fcf-4093-9520-acd528861605" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；检查单要求对清单上**每个取证类别**都表明符合、机型间差异须恰当注明、FMS 与 ICA 对每个型号适用，并评估对运行、型号等级与限制以及机组工作负荷/人因的影响<kb doc="AC_20-180.pdf" chunk_id="e781ce0c-f549-4dcc-b1ca-00627bb61609" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-180.pdf" chunk_id="3278b1f1-b244-4834-aa9b-54f0d1e60141" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。示例清单模板也按型号逐行列出认证基础/修正案、TCDS、安装图、FMS、ICA、件号与型号特定注记<kb doc="AC_20-180.pdf" chunk_id="866db38b-db94-40a8-8f58-2dd139398349" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

![Appendix A. FAA-Approved Model List (AML) SA01157LA Installation of Generator XXX](http://localhost:8080/api/v1/ingestion/jobs/5111c9d3e8e748809ef6515f091b17de/assets/a8b51898ecf2d05294cf)

**4. 对“自动驾驶类系统”的专门限制。** §5.g：“The AML-STC **may not be suitable for systems that can directly control the aircraft**. For example, autopilot installations or similar systems that involve control inputs may require careful design installation, and testing on each proposed model **regardless of baseline data shared between them**”，并可能存在需逐案评估的**序列号特定要求**<kb doc="AC_20-180.pdf" chunk_id="2441846f-0493-4683-b94c-52cfa4f7b2b2" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。这直接否定了“通过多型号批准直接推广”的思路。

**5. 环境与安全分析可能因机型而异。** EMC、雷电与 HIRF 评估在集成航电与复合材料结构上更重要；“为某一机型做的标准化试验与类别（如 RTCA DO-160）**may not be appropriate** without further evaluation of the specific HIRF and lightning qualification levels for another aircraft model”；针对某系统的 FHA/SSA 假设也可能需补充证实，且属机型相关事项<kb doc="AC_20-180.pdf" chunk_id="4068e2ac-6485-4ca3-b5a0-c6d3e4a782ad" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

**6. 其他约束。** 涉及独特复杂安装问题的型号，宜考虑以既有基线数据加补充要求申请新的非 AML 的 STC<kb doc="AC_20-180.pdf" chunk_id="62d1c2dc-c25e-443d-a05e-5c0993328432" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；新增型号可能需要新的安装符合性检查并逐案评估<kb doc="AC_20-180.pdf" chunk_id="3278b1f1-b244-4834-aa9b-54f0d1e60141" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；仅升级既有硬件/软件（如软件修订）也可能需要重新评估机组工作负荷与人因<kb doc="AC_20-180.pdf" chunk_id="08ba4489-f7ba-4c76-9e08-0222603e5284" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；AML-STC 只覆盖同一类别取证的航空器（Part 23 的清单不能含 Part 25/27/29）<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

## 三、若要继续推进，可接受的路径

1. 先按 §3.3 对 AP、HUD、SVS 分别做**适用性分析**；结论为不足时，改为“退化模式下自动断开/抑制”的设计，并在 A/RFMS 与操作说明中声明丢失的功能与机动限制<kb doc="AC_20-181.pdf" chunk_id="fac2ef92-4b92-4c9c-a33d-75819a062b48" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
2. 若主张可继续工作：证明退化模式满足各接口系统的姿态/航向性能与适航要求（含类别串核对）<kb doc="AC_20-181.pdf" chunk_id="9421756e-5bfb-4eee-ba7e-5e4db3f98447" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-181.pdf" chunk_id="0ff67505-a594-4b87-b2ea-81af9ee021b8" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />，并按 §3.2 完成相应试验或分析<kb doc="AC_20-181.pdf" chunk_id="770bf72f-942a-4298-acfe-264546d3acf9" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；自动驾驶部分按 §5.g 逐型号设计、安装与试验<kb doc="AC_20-180.pdf" chunk_id="2441846f-0493-4683-b94c-52cfa4f7b2b2" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
3. 多型号路径上：明确各型号共享的基线数据、逐型号确立其适用性、逐型号提供 FMS/ICA 与符合性声明，并在清单中注明差异<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-180.pdf" chunk_id="3705aad7-9fcf-4093-9520-acd528861605" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-180.pdf" chunk_id="e781ce0c-f549-4dcc-b1ca-00627bb61609" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

## 四、资料界限

AC 20-181 未给出 HUD、SVS、自动驾驶的具体最低性能判据，只要求参照接口系统的性能与适航要求<kb doc="AC_20-181.pdf" chunk_id="9421756e-5bfb-4eee-ba7e-5e4db3f98447" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-181.pdf" chunk_id="0ff67505-a594-4b87-b2ea-81af9ee021b8" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />，这些判据须查相应 TSO/接口规范。检索内容中不存在“多型号批准可免除逐型号验证”的条款；相反，AC 20-180 明确其不是一揽子批准<kb doc="AC_20-180.pdf" chunk_id="3705aad7-9fcf-4093-9520-acd528861605" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。另外，AC 20-180 自述为非强制性、描述可接受方法之一，但若采用该 AC 取得批准，则须遵守其全部条款<kb doc="AC_20-180.pdf" chunk_id="9e067c2b-c702-40b9-bead-e8c54e84e445" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。可延伸阅读：[[concept/ahrs-degraded-mode|AHRS降级模式]]、[[concept/tso-c201-category-coding|TSO-C201类别编码与分类]]、[[concept/aml-stc|AML-STC]]。