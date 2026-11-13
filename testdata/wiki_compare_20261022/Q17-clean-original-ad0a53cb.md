## 结论

这套论证的两个支撑点都不成立：文件在**“TSO 授权是否覆盖速度精度”**这一条上给出了明确否定；在**“数据被标记无效”**这一条上，文件要求 AHRS 检测到该故障后**停止使用**，而不是继续使用。<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />

来源为 AC 20-181（4/7/14），属咨询通告，用 should/ensure 指导性措辞，但它是 FAA 在该主题上给出的可接受符合性方法（[[concept/ahrs-aiding-sources|AHRS辅助源]]）。

## 逐项判断

| # | 待判断的说法/主张 | 文件原文依据 | 判断 |
|---|---|---|---|
| 1 | GNSS 速度数据可用于 AHRS 姿态修正 | §2.3：“GNSS velocity data can be used to compute longitudinal accelerations to help eliminate errors.”<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **成立（有前提）**，前提是第 2–4 项的鉴定与精度要求 |
| 2 | “有 TSO 授权就已验证速度精度” | §2.3.2：“GNSS position sources are not required to pass velocity accuracy tests to receive TSO authorization.”<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **不成立**——这正是 TSO 授权范围之外的项目 |
| 3 | 精度要求由谁定、怎么取证 | §2.3.2：应确保 GNSS 源数据满足“the minimum velocity accuracy requirement prescribed by the AHRS installation”；验证途径之一是使 GNSS 源通过 AC 20-138D 规定的速度精度试验，通常由 GNSS 设备制造商完成<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **须补做**：最低速度精度指标由 AHRS 安装方自行规定并独立取证 |
| 4 | 除 TSO 之外是否还有别的条件 | §2.3.1：应确保外部 GNSS 以适当的精度、完整性、可用性以及软硬件设计保证提供所需输入<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **成立**：TSO 是入门条件，不是接口数据可用的完整证明 |
| 5 | “GNSS 报无效后仍输出数值”这一现象 | §2.3.3：“It is possible for some GNSS articles to output erroneous position and velocity data after the data is flagged invalid.”<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **现象被文件承认**，并触发“审查 GNSS 规范以确定是否可能发生该情况”的义务<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 6 | 因此可继续把该数值用于姿态修正 | §2.3.3：“if the AHRS detects the annunciated GNSS fault, the AHRS should cease using erroneous GNSS data.”<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **不成立，处置方向相反**：应停用并转降级/禁用相应输出 |
| 7 | 用“分析”支持继续使用 | §2.3.3 末句“Analysis may be used as a means of compliance.”；§2.2.2 的分析是用于确保“the appropriate action occurs with degradation or failure of the external aiding source”，示例即 AHRS 禁用姿态输出或切换模式<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-181.pdf" chunk_id="7b6687b0-fc67-40e8-88b7-0355dadc811e" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **误用**：分析是证明“会正确停用/降级”的符合性方法，不是“允许继续使用”的许可 |
| 8 | 故障检测链路是否具备 | §2.3.3 的义务以“AHRS 检测到已告警的 GNSS 故障”为条件<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；§2.2.2 要求申请人确定外部辅助源失效与告警如何影响 AHRS 性能，必要时做地面/飞行试验<kb doc="AC_20-181.pdf" chunk_id="7b6687b0-fc67-40e8-88b7-0355dadc811e" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> | **需补证**：若接口不接收该告警，此条不触发，问题回到 §2.2.2 的失效影响评估与 §2.3.1 的完整性论证，不能用“有 TSO”搪塞 |

补充一个容易被忽略的点：§2.2.2 要求告警“清晰、明确且及时，且仅在相应状态存在时显示”<kb doc="AC_20-181.pdf" chunk_id="7b6687b0-fc67-40e8-88b7-0355dadc811e" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。因此，如果在数据已被标记为无效之后，既不撤下这些数据、也不给出相应指示，就与告警逻辑不符；仅以“数值仍然可用”为由继续让这些数据参与修正，也与该条相悖。

## 文件对 TSO-C129a 接口说到了哪一步

只有一句**范围排除**，条目为 §2.3.1.2：

> “This AC does not address AHRS interface to TSO-C129a, Airborne Supplemental Navigation Equipment Using the Global Positioning System (GPS), since this TSO design standard may not provide sufficient availability in high interference environments.”<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />

逐层看它的“深度”：

- **说了什么**：本 AC 不涉及 AHRS 与 TSO-C129a 的接口；给出的唯一理由是，该 TSO 设计标准在**高干扰环境**下可能无法提供足够**可用性**<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
- **没说什么**：没有针对 C129a 的任何评估方法、接受准则、补偿措施或替代符合性路径；也没有出现“禁止安装/不得使用”的措辞。“does not address”是划出适用范围，既不是合格判定，也不是禁令。
- **可推出的边界**：§2.3.1.1 的合格清单只列 TSO-C145d、TSO-C146d、TSO-C196b 的**任一修订版**<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。C129a 设备不在这份清单内，因此不能作为本 AC 下的符合性依据；若确需该接口，属于本 AC 覆盖范围之外，须与 FAA 另行商定审定基础。
- **与本案的关系**：C129a 是“可用性/范围”问题，与“速度精度”不是一个问题。即便把 GNSS 换成 C145d/C146d/C196b，§2.3.2 的最低速度精度要求仍单独适用<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />——所以不能靠“换一个 TSO 号”来回答本案的质疑。

## 要让该设计站得住，需要三项证据

1. **规范审查记录**：依据 GNSS 规范说明“标记无效后是否仍输出位置/速度”，若可能，说明 AHRS 如何检测该告警<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
2. **停用与降级行为**：检测到已告警故障即置该速度数据不可用，按设计禁用姿态输出或切换模式，并用试验或分析证明其动作与告警指示一致<kb doc="AC_20-181.pdf" chunk_id="7b6687b0-fc67-40e8-88b7-0355dadc811e" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
3. **独立的速度精度证据**：由安装方定义最低速度精度要求，按 AC 20-138D 的速度精度试验取得数据，不能以 TSO 授权替代<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。