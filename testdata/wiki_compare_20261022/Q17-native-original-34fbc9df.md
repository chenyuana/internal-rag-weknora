## 逐项判定的结论

先列出判定结果，依据均来自 AC 20-181（2014-04-07，AHRS 适航批准补充指导）。该文件是面向 TC/ATC/STC/ASTC 申请人的指导材料<kb doc="AC_20-181.pdf" chunk_id="9174a025-ce1e-41bf-9334-78def7744df7" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />，并且明确其补充的正是“TSO-C201 中包含、但需要在**安装时**评估”的那些特征<kb doc="AC_20-181.pdf" chunk_id="999625b4-ce92-4059-bcb9-312706cf2996" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

| 开发方或供应商的主张 | 文件依据 | 判定 |
|---|---|---|
| ①“GNSS 有 TSO 授权，速度精度即已被验证” | §2.3.2：**取得 TSO 授权并不要求通过速度精度试验**<kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；须确保 GNSS 源数据满足 AHRS 安装规定的最低速度精度要求<kb doc="AC_20-181.pdf" chunk_id="f86f0674-5189-45ac-99b3-5453e3910751" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **不成立**（TSO 授权的范围被误解） |
| ② 用该 GNSS 速度数据做姿态修正是可接受的接口 | §2.3.1：外部 GNSS 须以适当精度、完整性、可用性和软硬件设计保证提供所需输入<kb doc="AC_20-181.pdf" chunk_id="40330931-98a2-461f-91aa-b2600fe31f8c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；合格标准限定为 TSO-C145d、C146d、C196b 的任何修订版<kb doc="AC_20-181.pdf" chunk_id="1da0f60e-d9d8-4cac-826b-d97686eacb09" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="8eeece07-dcfc-4339-8500-b02acdd52826" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **需另行证明**；若为 TSO-C129a 设备，则**不在本文件覆盖范围** |
| ③ GNSS 报告无效后仍输出数值，仍继续使用 | §2.3.3：某些 GNSS 件确实会在数据被标记无效后仍输出错误的位置和速度数据；**若 AHRS 检测到已告警的 GNSS 故障，AHRS 应停止使用错误的 GNSS 数据**<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **与原文冲突，不可接受** |
| ④ 只做了“数据可用”判断，未评估告警与失效影响 | §2.2.2：申请人应确定外部辅助源失效与告警如何影响 AHRS 性能，必要时进行地面或飞行试验；无法试验时以分析证明；辅助源失效导致禁用姿态输出或切换模式时，须在 §§23.1309、25.1309、27.1309、29.1309 安全分析中说明<kb doc="AC_20-181.pdf" chunk_id="88a20b46-eef5-49fa-8de2-b1e53d7dc090" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="ab0559ee-da94-4fd7-bd76-f2dc4a2f41f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="19c4fc4d-cf52-4c82-9368-1aee0ad5505b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="6497d606-18eb-4fab-b815-8c154c29e990" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **缺失环节** |
| ⑤ 失去 GNSS 辅助后的运行方式未评估 | §3：TSO-C201 允许可选降级模式，在部分失效或失去辅助源时提供基本姿态性能<kb doc="AC_20-181.pdf" chunk_id="c1185200-e52d-4f2f-803d-2893f21fdd2d" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；应在适航认证中评估其设计与运行适用性<kb doc="AC_20-181.pdf" chunk_id="0e5793bf-2ca3-4ecf-a037-f1b63585b48f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | **必须补齐** |

### 关于第①条：TSO 授权与速度精度是两件事

§2.3.2 的原文把这一点写得很直白：

> “GNSS position sources are not required to pass velocity accuracy tests to receive TSO authorization.”<kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

也就是说，**TSO 授权本身不构成对速度精度的验证**。若要使用 GNSS 位置源的速度精度，应由安装方确认其数据满足 AHRS 安装所规定的最低速度精度要求<kb doc="AC_20-181.pdf" chunk_id="f86f0674-5189-45ac-99b3-5453e3910751" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；文件给出的一种验证方法是证明该 GNSS 源通过 AC 20-138D 规定的速度精度试验，并指出这些试验通常由 GNSS 源设备制造商完成<kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="3dd19dfe-e748-4171-b54a-35ef177bf684" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。因此，正确的举证方向是“GNSS OEM 的速度精度试验报告或声明”，而不是“TSO 证书”。

### 关于第③条：无效标志之后的数值必须停用

§2.3.3 同时做了两件事：一是承认“某些 GNSS 件在数据被标记无效后仍会输出错误的位置与速度数据”这一现实<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；二是给出要求——审查 GNSS 规格以确定该情况是否可能发生，并且**AHRS 在检测到已告警的 GNSS 故障时应停止使用错误数据**，分析可作为符合性方法<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

因此，“报无效后继续拿数值做姿态修正”本身就是一个与文件相悖的设计选择。需要区分两种情形，并分别举证：

- 若 AHRS **能**检测到该已告警的故障：必须设计成“停止使用”，并以分析或试验证明；
- 若 AHRS **不能**检测到：这属于检测能力缺失，须在安全分析中处理，并触发 §2.2.2 的告警/失效影响评估<kb doc="AC_20-181.pdf" chunk_id="88a20b46-eef5-49fa-8de2-b1e53d7dc090" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="ab0559ee-da94-4fd7-bd76-f2dc4a2f41f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />，而不能以“数值看起来正常”为由继续使用。

### 关于第④⑤条：告警、降级模式与运行文件

- 告警要求：应操作相关以尽量减少机组工作负荷；清晰、无歧义、及时；仅在该状态存在时显示；位置一致地置于电子显示特定区域；需要机组立即感知时置于主视场<kb doc="AC_20-181.pdf" chunk_id="ab0559ee-da94-4fd7-bd76-f2dc4a2f41f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- 降级模式：DO-334 指出该模式可支持巡航、爬升、下降、等待和仪表进近，但**可能不适用于自动驾驶运行或某些飞行程序**<kb doc="AC_20-181.pdf" chunk_id="0af7475e-960e-47b5-b3fa-7f4a37e550b0" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；适用性须按 §§23.1301、25.1301、27.1301 或 29.1301 判断<kb doc="AC_20-181.pdf" chunk_id="6f56a24a-1b21-46ff-b5d8-9175d7f976db" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；不得以降级模式为依据减少航空器所需姿态仪表数量<kb doc="AC_20-181.pdf" chunk_id="93982b30-9ed8-48d4-bd24-aee046d4d13a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；安装手册规定的飞行包线或时间限制须纳入飞行手册<kb doc="AC_20-181.pdf" chunk_id="93982b30-9ed8-48d4-bd24-aee046d4d13a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="1a70e384-cab9-488f-be72-e92d769611e6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；降级模式属非正常状态，不应在地面（含初始起动、发动机起动后）启用<kb doc="AC_20-181.pdf" chunk_id="1a70e384-cab9-488f-be72-e92d769611e6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- 对其他应用的影响：降级模式性能是为支持主姿态、航向、转弯率和侧滑-滑移指示而定义的；对自动驾驶、HUD、SVS 等更高性能应用可能不够充分；若分析表明不够充分，应确保降级模式**不驱动**这些应用<kb doc="AC_20-181.pdf" chunk_id="7511ef79-5b06-4d5b-b082-d7c36c585384" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="91d7c971-818c-459d-ab20-b994c5631fde" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- 文件更新：A/RFMS 或操作说明须包含降级模式说明、降级模式下的告警、航空器操作指令，并指明将丢失哪些系统应用（如自动驾驶）以及可执行机动或运行类型的限制<kb doc="AC_20-181.pdf" chunk_id="3a2e542a-2c45-454d-bd86-8adc42cc1349" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="fde02d4a-20cf-4447-b868-a8bcf7017f40" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

---

## 文件对 TSO-C129a 接口说到了哪一步

**只说到“排除”这一步，没有任何实质性技术内容。**整份 AC 关于 TSO-C129a 的表述只有 §2.3.1.2 一句：

> “This AC does not address AHRS interface to TSO-C129a … since this TSO design standard may not provide sufficient availability in high interference environments.”<kb doc="AC_20-181.pdf" chunk_id="28ecf06c-03a9-47db-85fc-a9e615996bd8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

由此可以界定三件事：

1. **范围**：本 AC 不覆盖 AHRS 与 TSO-C129a 设备之间的接口；给出的理由是 C129a 这一设计标准在**高干扰环境下可能无法提供足够的可用性**<kb doc="AC_20-181.pdf" chunk_id="28ecf06c-03a9-47db-85fc-a9e615996bd8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
2. **推荐的替代路径**：§2.3.1.1 把外部 GNSS 的合格标准限定为 TSO-C145d、TSO-C146d、TSO-C196b 的任何修订版<kb doc="AC_20-181.pdf" chunk_id="1da0f60e-d9d8-4cac-826b-d97686eacb09" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="8eeece07-dcfc-4339-8500-b02acdd52826" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />，即回退到“本文件覆盖的那几类 GNSS”。
3. **文件的边界**：它既没有给出 C129a 接口的完整性、可用性判据与告警处理要求，也没有说“禁止使用 C129a”。准确含义是“**本文件不作为该接口的符合性依据**”——若坚持使用 C129a，申请人须另行建立并证明符合性（包括高干扰环境下的可用性、失效与告警处理、安全分析、安装批准），不能引用 AC 20-181 作为依据。

## 处置建议

1. 撤回“有 TSO 就已验证速度精度”的论证，改以 GNSS OEM 按 AC 20-138D 方法出具的速度精度试验证据满足安装规定值<kb doc="AC_20-181.pdf" chunk_id="2e551b84-d937-4220-a987-3043856ce2ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="3dd19dfe-e748-4171-b54a-35ef177bf684" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
2. 修改设计：当 AHRS 检测到已告警的 GNSS 故障时，就停用该 GNSS 数据（这属于设计特征，不能只写在说明里）<kb doc="AC_20-181.pdf" chunk_id="e376826f-35d5-4eb8-8ef0-4135d41c6acd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
3. 补齐 §2.2.2 的失效与告警影响评估，以及 §3 的降级模式评估与 A/RFMS 更新<kb doc="AC_20-181.pdf" chunk_id="88a20b46-eef5-49fa-8de2-b1e53d7dc090" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="0e5793bf-2ca3-4ecf-a037-f1b63585b48f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-181.pdf" chunk_id="3a2e542a-2c45-454d-bd86-8adc42cc1349" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
4. 若 GNSS 确为 TSO-C129a 件，另立接口符合性论证，并专门处理高干扰可用性问题<kb doc="AC_20-181.pdf" chunk_id="28ecf06c-03a9-47db-85fc-a9e615996bd8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；同时注意外部辅助源并非作为 TSO-C201 项目设计批准的一部分被鉴定，接口属于安装方责任<kb doc="AC_20-181.pdf" chunk_id="d2f8c2ca-12fa-424b-be4d-1a5faadbd7ed" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

相关背景可参见 [[concept/ahrs-aiding-sources|AHRS 辅助源]] 与 [[concept/degraded-mode|降级模式]]。