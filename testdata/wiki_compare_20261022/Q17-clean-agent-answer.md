## 结论

开发方的三条理由都不成立：**TSO 授权本身不能证明速度精度已合格**；**报无效后仍输出数值是文件明确要求防护的失效模式，不是可用依据**；继续把该数据用于姿态修正，与 AC 20-181 第 2.3.3 节的处置要求相反。

## 一、逐项判断

| # | 开发方主张/做法 | 判断 | 文件依据 |
|---|---|---|---|
| 1 | GNSS 有 TSO 授权，因此速度数据可用于 AHRS | ✗ 不成立 | TSO 授权只能证明设备符合其 TSO 设计标准；AC 20-181 还要求外部辅助源在**精度、完整性、可用性、软硬件设计保证**上与具体 AHRS 安装相匹配的安装级评估（§2.2.1、§2.3.1）<kb doc="AC_20-181.pdf" chunk_id="7b6687b0-fc67-40e8-88b7-0355dadc811e" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 2 | “有 TSO 就已验证速度精度” | ✗ 与原文相反 | §2.3.2 明文：*“GNSS position sources are not required to pass velocity accuracy tests to receive TSO authorization.”* 要证明的是 GNSS 数据满足**AHRS 安装所规定的最低速度精度**，途径之一是 AC 20-138D 的速度精度试验，通常由 GNSS 设备制造商完成<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 3 | GNSS 报无效后仍输出数值，所以可继续用 | ✗ 误读 | §2.3.3 承认“某些 GNSS 产品在数据被标记为无效后仍输出错误的定位和速度数据”，但要求：先审查 GNSS 规范确认是否会发生该情况；**若 AHRS 检测到已告警的故障，应停止使用错误数据**；分析可作为符合性方法<kb doc="AC_20-181.pdf" chunk_id="a134ee49-160c-4678-885f-75edf0d0f266" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 4 | 明知无效仍用于姿态修正 | ✗ 不可接受 | GNSS 速度被用于计算纵向加速度以消除姿态误差<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />，错误速度会直接进入姿态解算。§2.2.2 还要求确定辅助源失效/告警如何影响 AHRS 性能，并用地面/飞行试验或分析证明告警与飞行员动作适当（例如 AHRS 禁用姿态输出或切换模式）<kb doc="AC_20-181.pdf" chunk_id="7b6687b0-fc67-40e8-88b7-0355dadc811e" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。把已识别故障当作正常输入使用，缺少任何支撑分析 |

补充要点：问题 2 与问题 4 之间存在实质性影响：这不是“精度略降”的问题，而是**错误数据被主动用于修正姿态**，且 §2.3.3 的措辞是“cease using”，没有留下“只要数值连续就可用”的空间。

## 二、文件对 TSO-C129a 接口说到哪一步

只说了一句**排除性声明**，没有给出任何接口指导：

- §2.3.1.2：*“This AC does not address AHRS interface to TSO-C129a, Airborne Supplemental Navigation Equipment Using the Global Positioning System (GPS), since this TSO design standard may not provide sufficient availability in high interference environments.”*<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />
- 也就是说：AC 20-181 **不涉及** C129a 接口，理由是 C129a 在高干扰环境下可能无法提供足够可用性；文件**没有**给出 C129a 的鉴定要求、速度精度验证方法或故障处置指导。
- 文件认可的外部 GNSS 标准只有三条：TSO-C145d、TSO-C146d、TSO-C196b（任何修订版）<kb doc="AC_20-181.pdf" chunk_id="7cf383dd-95c0-4c47-b79c-928b98e05997" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

因此，若按 AC 20-181 走批准路径，**不能把 TSO-C129a 当作满足 §2.3.1 鉴定的依据**，也不能从该文件推出 C129a 的数据可用于 AHRS 姿态修正；如确需使用，必须与审定方另行商定可接受的符合性方法。相关整理见 [[concept/ahrs-aiding-sources|AHRS辅助源]]。

## 三、需要补齐的证据

1. **速度精度**：AC 20-138D 规定的速度精度试验数据（或 GNSS 制造商数据），对照 AHRS 安装规定的最低速度精度限值。
2. **接口鉴定**：精度、完整性、可用性、软件等级与电子硬件设计保证，并含高干扰环境下的可用性论证；若坚持用 C129a，此项缺少文件支持。
3. **故障处置**：GNSS 规范审查结论、AHRS 对“已告警故障”的抑制/切换逻辑，以及地面/飞行试验或 §23.1309、§25.1309、§27.1309、§29.1309 安全分析。
4. **降级模式**：失去 GNSS 辅助后姿态性能是否满足预期运行，按 AC 20-181 第 3 节评估（参见 [[concept/ahrs-degraded-mode|AHRS降级模式]]）<kb doc="AC_20-181.pdf" chunk_id="7b6687b0-fc67-40e8-88b7-0355dadc811e" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

性质提醒：AC 20-181（4/7/14）是咨询通告而非联邦航空法规，条文中的“should/ensure”属指导性符合性表述；但作为批准基础，仍须满足，或经审定方接受等效替代方法。