## 结论先说

把“有 TSO 授权”当作“速度精度已验证”，并据此在 GNSS 报无效后继续把数值用于姿态修正，这两点都与文件相悖。文件恰恰在 GNSS 速度精度这一条上做了**否定式说明**，并且在故障条款里要求 AHRS **停止**使用错误数据。<kb doc="AC_20-181.pdf" chunk_id="f86f0674-5189-45ac-99b3-5453e3910751" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

## 逐项判断

| # | 待判断的说法 | 文件依据（AC 20-181，2014-04-07） | 判断 |
|---|---|---|---|
| 1 | GNSS 速度数据可用于 AHRS 姿态修正 | §2.3：GNSS 速度数据可用于计算纵向加速度，以帮助消除误差<kb doc="AC_20-181.pdf" chunk_id="157e5534-95c6-4ce9-a22a-93273a959d27" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />——用途本身是被认可的 | **成立（有前提）**：前提是 §2.3.1 的鉴定要求，即精度、完整性、可用性、软硬件设计保证<kb doc="AC_20-181.pdf" chunk_id="40330931-98a2-461f-91aa-b2600fe31f8c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 2 | “GNSS 位置源有 TSO 授权，就说明速度精度已验证” | §2.3.2：“GNSS position sources are not required to pass velocity accuracy tests to receive TSO authorization”（取得 TSO 授权并不要求通过速度精度测试）<kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **不成立**：这是整段的核心否定。TSO 授权的审查范围不覆盖速度精度 |
| 3 | 应确保速度数据满足安装要求 | §2.3.2：应确保 GNSS 源数据满足 **AHRS 安装所规定的最低速度精度要求**；验证途径之一是使 GNSS 源通过 AC 20-138D 规定的速度精度测试，通常由 GNSS 设备制造商完成<kb doc="AC_20-181.pdf" chunk_id="f86f0674-5189-45ac-99b3-5453e3910751" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **必须做的动作**：精度要求由 AHRS 安装方自己定义并取证，不能靠“TSO 已验”替代 |
| 4 | “GNSS 报无效后仍输出数值”这一现象 | §2.3.3：“It is possible for some GNSS articles to output erroneous position and velocity data after the data is flagged invalid.”（某些 GNSS 设备确实可能在数据被标记无效后仍输出错误的位置与速度数据）<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **现象成立**，且文件要求**审查 GNSS 规范**以确定该情况是否可能发生<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 5 | 因此可以继续把该数值用于姿态修正 | §2.3.3：“if the AHRS detects the annunciated GNSS fault, the AHRS should cease using erroneous GNSS data”（若 AHRS 检测到已告警的 GNSS 故障，应停止使用错误的 GNSS 数据）<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **不成立，处置方向相反**：报无效即应停用，并转入告警或降级状态 |
| 6 | 用“分析”支持继续使用 | §2.3.3 末句“Analysis may be used as a means of compliance”<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；§2.2.2 的分析是用于证明辅助源退化或失效时**发生适当动作**<kb doc="AC_20-181.pdf" chunk_id="19c4fc4d-cf52-4c82-9368-1aee0ad5505b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **误用**：分析是证明“会正确停用或降级”的符合性方法，不是“可以继续使用”的许可 |
| 7 | AHRS 侧是否具备该处置能力 | §2.2.2：申请人应确定外部辅助源失效与告警如何影响 AHRS 性能，必要时做地面与飞行试验；告警应清晰、无歧义、及时，且仅在状态存在期间显示<kb doc="AC_20-181.pdf" chunk_id="88a20b46-eef5-49fa-8de2-b1e53d7dc090" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="ab0559ee-da94-4fd7-bd76-f2dc4a2f41f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **需补证**：注意 §2.3.3 的条件是“AHRS 检测到已告警的故障”。若接口根本不接收故障标志，该条不成立，问题回到完整性设计与失效影响评估 |
| 8 | 失去辅助源后的运行状态 | §3：TSO-C201 允许可选降级模式；降级模式不得驱动自动驾驶、HUD、SVS 等更高性能应用，相关告警与限制应写入 A/RFMS<kb doc="AC_20-181.pdf" chunk_id="fde02d4a-20cf-4447-b868-a8bcf7017f40" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />（[[concept/degraded-mode|降级模式]]页） | **应纳入设计说明与飞行手册**，而不是让错误数据继续参与姿态解 |

## 外部 GNSS 的鉴定口径（第 1 项的前提）

- §2.3.1.1 要求外部 GNSS 鉴定到以下任一标准的**任一修订版**：TSO-C145d、TSO-C146d、TSO-C196b<kb doc="AC_20-181.pdf" chunk_id="1da0f60e-d9d8-4cac-826b-d97686eacb09" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="8eeece07-dcfc-4339-8500-b02acdd52826" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- 除 TSO 之外，还必须满足精度、完整性、可用性以及软件和电子硬件设计保证<kb doc="AC_20-181.pdf" chunk_id="40330931-98a2-461f-91aa-b2600fe31f8c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。也就是说，TSO 是**入门条件**，不构成“接口数据可用”的完整证明——这正与第 2 项的判断一致。

## 文件对 TSO-C129a 接口说到了哪一步

只说了一句**范围排除**，没有往下走：

> §2.3.1.2 “This AC does not address AHRS interface to TSO-C129a … since this TSO design standard may not provide sufficient availability in high interference environments.”<kb doc="AC_20-181.pdf" chunk_id="28ecf06c-03a9-47db-85fc-a9e615996bd8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

具体到“哪一步”：

- **说了的**：本 AC 不涉及 AHRS 与 TSO-C129a 的接口；理由是该 TSO 设计标准在高干扰环境下可能无法提供足够可用性<kb doc="AC_20-181.pdf" chunk_id="28ecf06c-03a9-47db-85fc-a9e615996bd8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- **没说的**：没有给出 C129a 接口的任何评估方法、接受准则或补偿措施，也没有出现“禁止安装”的措辞。“does not address”是划出适用范围，不是合格性判决。
- **因此**：C129a 既不能作为本 AC 下的符合性依据，也不能反过来引用本文件论证其不可用；如确需该接口，属于本 AC 覆盖范围之外，须与 FAA 另行确定审定基础。同时注意，它与第 1–3 项的“速度精度”问题**不是同一个问题**：即使换成 C145d/C146d/C196b，速度精度仍须单独验证<kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

## 该案要站得住，需要补齐的三件事

1. **规范审查记录**：出具 GNSS 规范审查证据，确认“置无效后仍输出数据”是否可能；若可能，说明 AHRS 如何检测该告警<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
2. **停用逻辑与降级行为**：检测到已告警故障即置该速度数据不可用，转入降级模式或禁用姿态输出，并给出告警与机组动作的试验或分析证据<kb doc="AC_20-181.pdf" chunk_id="19c4fc4d-cf52-4c82-9368-1aee0ad5505b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />（[[concept/ahrs-aiding-sources|AHRS辅助源]]、[[concept/degraded-mode|降级模式]]）。
3. **速度精度独立证据**：由 AHRS 安装方定义最低速度精度要求，按 AC 20-138D 的速度精度测试取得证据，不能以 TSO 授权替代<kb doc="AC_20-181.pdf" chunk_id="f86f0674-5189-45ac-99b3-5453e3910751" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。