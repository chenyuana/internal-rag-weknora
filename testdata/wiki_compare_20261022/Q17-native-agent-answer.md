## 结论

开发方的三点推理均不成立：AC 20-181 一方面允许用 GNSS 速度辅助姿态，另一方面**明确否定了“取得 TSO 授权就等于速度精度已经验证”**，并且要求 AHRS 在检测到已告警的 GNSS 故障后停止使用错误数据。如果该 GNSS 是 TSO-C129a 设备，该接口根本不在本咨询通告的指导范围内。

## 逐项判断

| 判断项 | 结论 | 文件依据 |
|---|---|---|
| ① AHRS 用 GNSS 速度数据修正姿态 | **原则允许，但有条件** | §2.3：GNSS 速度数据可用于计算纵向加速度，“以帮助消除误差”，但须满足 §2.3.1 的鉴定要求与 §2.3.2 的速度精度要求 <kb doc="AC_20-181.pdf" chunk_id="157e5534-95c6-4ce9-a22a-93273a959d27" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| ② “有 TSO 授权就已验证速度精度” | **不成立（核心错误）** | §2.3.2 原文：GNSS 位置源**不要求通过速度精度试验即可取得 TSO 授权** <kb doc="AC_20-181.pdf" chunk_id="f86f0674-5189-45ac-99b3-5453e3910751" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| ③ 报无效后仍输出数值，继续用于姿态修正 | **不符合** | §2.3.3：某些 GNSS 设备在数据被标记为无效后仍会输出错误的位置与速度数据；若 AHRS 检测到已告警的 GNSS 故障，**应停止使用错误的 GNSS 数据** <kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| ④ 以“分析”作为继续使用的理由 | **误用条款** | §2.3.3 的“分析可作为符合性方法”，是用于证明“该情形不会发生”或“已停止使用”，而不是用于论证可以继续使用已告警的数据 <kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| ⑤ 若该 GNSS 是 TSO-C129a 设备 | **本 AC 不予覆盖** | §2.3.1.2 明确不涉及该接口；§2.3.1.1 的可接受标准清单只有 TSO-C145d、C146d、C196b <kb doc="AC_20-181.pdf" chunk_id="28ecf06c-03a9-47db-85fc-a9e615996bd8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="1da0f60e-d9d8-4cac-826b-d97686eacb09" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="8eeece07-dcfc-4339-8500-b02acdd52826" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| ⑥ 告警与机组/手册影响 | **须另行评估并记录** | §2.2.2 要求确定辅助源失效及告警如何影响 AHRS 性能，并试验告警与飞行员动作；若失去辅助源触发降级模式，还适用 §3.3、§3.4 <kb doc="AC_20-181.pdf" chunk_id="88a20b46-eef5-49fa-8de2-b1e53d7dc090" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="ab0559ee-da94-4fd7-bd76-f2dc4a2f41f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="19c4fc4d-cf52-4c82-9368-1aee0ad5505b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |

### ② 为什么“TSO 授权”不能证明速度精度

§2.3.2 的完整规定是：若使用 GNSS 位置源的速度精度，应确保 GNSS 源数据满足**AHRS 安装所规定的最低速度精度要求**；而“GNSS 位置源取得 TSO 授权并不要求通过速度精度试验”。验证该性能的一种方法是确认 GNSS 源通过了 AC 20-138D 规定的速度精度试验，这类试验通常由 GNSS 设备制造商完成 <kb doc="AC_20-181.pdf" chunk_id="f86f0674-5189-45ac-99b3-5453e3910751" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="3dd19dfe-e748-4171-b54a-35ef177bf684" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。也就是说，TSO 授权解答的是“设备是否获准安装使用”，并不回答“速度精度是多少”。此外，TSO-C201 本身对速度等“其他数据”不规定性能要求，须由申请人自行确认其适用于预期应用 <kb doc="AC_20-181.pdf" chunk_id="bad319e4-ec15-4638-b0ec-c733a6354575" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

### ③ 为什么“报无效后继续用”不能接受

§2.3.3 的设计前提正是开发方遇到的情形：数据被标记无效后仍可能继续输出错误数值。因此 AC 给出的动作是两条：先**审查 GNSS 规范**确认是否可能发生该情况；一旦 AHRS 检测到已告警的故障，就**停止使用**这些数据 <kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。这与 §2.3.1 要求外部 GNSS 提供“适当的精度、完整性、可用性”一脉相承 <kb doc="AC_20-181.pdf" chunk_id="40330931-98a2-461f-91aa-b2600fe31f8c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

需要精确区分的是：条款的触发条件写的是“AHRS 检测到已告警的 GNSS 故障”。如果该安装根本没有把无效标志传给 AHRS，或者 AHRS 不响应，这本身就是接口完整性与告警设计缺陷，应按 §2.2.1（辅助源性能）和 §2.2.2（失效与告警影响、地面/飞行试验、告警须清晰及时且仅在故障存在时显示）处理 <kb doc="AC_20-181.pdf" chunk_id="d2f8c2ca-12fa-424b-be4d-1a5faadbd7ed" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="88a20b46-eef5-49fa-8de2-b1e53d7dc090" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="ab0559ee-da94-4fd7-bd76-f2dc4a2f41f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。换言之，“分析”只能用来证明“该 GNSS 不会在无效后输出错误数据”或“AHRS 确实停止使用”，不能用来把“已知无效仍继续使用”合理化。

## 文件对 TSO-C129a 接口说到了哪一步

只说到**“范围排除与关切提示”**这一步，仅 §2.3.1.2 一句：

> This AC does not address AHRS interface to TSO-C129a … since this TSO design standard may not provide sufficient availability in high interference environments. <kb doc="AC_20-181.pdf" chunk_id="28ecf06c-03a9-47db-85fc-a9e615996bd8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

具体边界是：

- **它做了什么**：明确把“AHRS 与 TSO-C129a 的接口”排除在本 AC 指导范围之外，并给出理由——该 TSO 设计标准在高干扰环境下可能无法提供足够的**可用性**。
- **它没做什么**：没有给出该接口的数据内容、格式、性能指标或符合性方法；没有判定该接口“可接受”或“不可接受”（“不涉及”不等于“禁止”）；也没有对 TSO-C129a 的速度精度作任何评价——排除理由是**可用性**，不是速度精度。
- **与可接受清单的关系**：§2.3.1.1 列出的合格 GNSS 标准为 TSO-C145d、TSO-C146d、TSO-C196b 任一修订版 <kb doc="AC_20-181.pdf" chunk_id="1da0f60e-d9d8-4cac-826b-d97686eacb09" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="8eeece07-dcfc-4339-8500-b02acdd52826" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />，TSO-C129a 不在其中。因此若本项目的 GNSS 确为 TSO-C129a 设备，既不能引用本 AC 作为该接口的批准依据，也不能把它的 TSO 授权当作速度精度的证明。

## 若要维持该设计，需要补齐的工作

1. **速度精度**：按 AHRS 安装规定的最低速度精度要求取证，采用 AC 20-138D 的速度精度试验或等效分析 <kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
2. **无效标志处理**：修改接口或逻辑，使 AHRS 在检测到已告警故障时停止使用 GNSS 速度，并以分析或试验证明 <kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
3. **告警与机组动作**：完成 §2.2.2 要求的地面/飞行试验或分析，确认告警清晰、及时、仅在故障存在时显示 <kb doc="AC_20-181.pdf" chunk_id="88a20b46-eef5-49fa-8de2-b1e53d7dc090" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="ab0559ee-da94-4fd7-bd76-f2dc4a2f41f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
4. **降级模式与手册**：若失去 GNSS 辅助会进入降级模式，按 §3.1–§3.4 评估其适用性、试验方式与其他系统接口，并在 A/RFMS 中写明性能、限制、告警及将丢失的应用 <kb doc="AC_20-181.pdf" chunk_id="19c4fc4d-cf52-4c82-9368-1aee0ad5505b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；相关概念见 [[concept/degraded-mode|降级模式]] 与 [[concept/ahrs-aiding-sources|AHRS辅助源]]。
5. **审定基础**：AC 20-181 属咨询通告，条文用“should”；偏离时应以 14 CFR 23/25/27/29.1301、1309 等条款为最终符合性目标，提供等效安全水平说明。

如需，我可以把上述判断整理成一份“条款—现状—差距—符合性方法”的逐条核对表。