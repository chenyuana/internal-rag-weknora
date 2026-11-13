## 结论先说

供应商的两项提议分别涉及锂电池的**四个独立的技术和批准环节**，不能合并成“检查合格即可装机”：

1. **更换电池内部的单个电芯，必须同时得到该锂电池 OEM 和 FAA 的批准**，这属于批准事项，而非维修判断；
2. **在同一电池内混用不同厂商的电芯原则上是禁止的**，唯一的例外途径是“由锂电池 OEM 提出、并经 FAA 批准的替代方法”（alternate means）；供应商自行提出并只做端电压检查，不属于这种例外；
3. **端电压合格只是健康状态判据中的一项**（OEM 规定还包括容量、内阻等），不能据此放行；
4. **长期储存的备件，其“外观正常”不足以证明适航**，必须按 OEM 储存或维护程序以及 ICA（持续适航文件）中的备件储存程序完成充电记录、功能或电荷保持检查和寿命期管理。

背景：AC 20-184（2015-10-15）本身是咨询通告，官方明确“this AC is not mandatory and does not constitute a regulation”，它给出的是表明符合适用适航要求的可接受方法<kb doc="AC_20-184.pdf" chunk_id="0288b983-df13-44b5-b33f-b98320fb9585" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。但其中被写入 ICA 或适航限制的内容，以及主管当局施加的特殊条件，会通过认证基础成为强制要求。相关条款的系统梳理见 [[concept/lithium-battery-maintenance-replacement-storage-handling|锂电池维护、更换、存储与操作]]。

---

## 一、单体（电芯）更换的批准要求：须由锂电池 OEM 和 FAA 双重批准

AC 20-184 §2.9.9 原文：

> “Replacement of individual cells within lithium batteries must be approved by the lithium battery's OEM and the FAA.”<kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

要点：

- **批准主体是“锂电池的 OEM”和 FAA**，两者都要有。电芯供应商、维修单位或运营人自己的工程评估都不是批准主体；如果供应商本身不是该锂电池的 OEM，它提出的“替换方案”在文件层面就不满足第一个条件。
- 这是与“换整块电池”不同的层级：整块电池更换时，ICA 必须按锂电池 OEM 维护手册给出更换说明（§2.9.8）<kb doc="AC_20-184.pdf" chunk_id="c4ee2801-0501-41ac-94b3-bd84867760dd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；ICA 应按制造商建议包含电池强制更换计划和定期维护（§3.2.2）<kb doc="AC_20-184.pdf" chunk_id="d4744bd7-e573-4ed6-824f-95e3f92a1e9c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；更换的锂电池应是**该特定飞机应用批准**的电池（§3.2.7）<kb doc="AC_20-184.pdf" chunk_id="eb7ae326-f1c9-49da-9ed5-d5ba1c3173ae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。整块电池更换尚且有这些约束，更不必说电芯级更换。
- 批准一旦涉及设计或构型改变，就意味着原有的电池级符合性证据（如 DO-311、DO-347 的电池级试验与热失控假设）不再自动适用于新构型；这一点属于由 §2.9.9 的批准要求引申出的工程判断，AC 未逐条展开。

## 二、混用不同厂商电芯的“例外”：有，但门槛很窄

同一 §2.9.9 第二句：

> “Mixing of cells from different manufacturers within a lithium battery is not permitted unless an alternate means proposed by the lithium batteries OEM and approved by the FAA exist.”<kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

必须分清两点：

- **原则**是“不允许”（not permitted），不是“默认允许、检查合格即可”；
- **例外**需要同时满足两个条件：**由锂电池 OEM 提出**替代方法，且**该方法经 FAA 批准**。例外针对的是“替代方法”（可接受的符合性方法），属于程序性门槛，而非放宽到“端电压合格”这种单一检查；它也不能替代第一句中的“单电芯更换须经 OEM 和 FAA 批准”，两个条件要同时满足。

因此，“另一厂商单体 + 端电压合格检查”这一组合：既不满足单电芯更换的批准条件，也不属于获 FAA 批准的替代方法，**不可按维修直接实施**。

## 三、储存备件的维护要求：外观正常不等于可用

相关要求分布在 ICA 要求与第 3 章两处：

| 环节 | 要求 | 依据 |
|---|---|---|
| ICA 中的备件储存程序 | ICA **应当**包含备件储存中锂电池的维护程序，以防装机时用到因长期储存导致电荷保持能力下降或其他损伤的电池 | §2.9.7<kb doc="AC_20-184.pdf" chunk_id="978d6e3b-92b5-4891-ad53-626a58f4109e" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 特殊条件第 9 项的 MOC | ICA 必须包含备件储存电池的维护程序，防止把**低荷电状态长期储存**导致退化的电池用于更换；**更换电池必须与 FAA 批准的制造商和件号相同** | 附录 F<kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 充电充足的定义 | “sufficiently charged”指电池保留足够的（以安时计）电荷，使电芯不被损伤；充电低于某点会造成“充电并保持满容量能力”的下降超过正常运行退化 | 附录 F 注<kb doc="AC_20-184.pdf" chunk_id="cebe871f-6663-409c-956e-cd49647884f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="1553b77b-6d8d-4835-a1e2-569f270d7ddf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 储存状态 | 按制造商建议的荷电状态和温度储存；考虑储存期内监测电路可能耗电 | §2.7<kb doc="AC_20-184.pdf" chunk_id="9f100a8f-66e4-4739-a3eb-b03a20580223" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 储存与使用间隔 | 记录充电日期；若未在制造商建议间隔内使用，按制造商建议进行维护/servicing | §3.3.2<kb doc="AC_20-184.pdf" chunk_id="e46d4c5b-7f43-41bc-b158-d6d18bd2914b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 周转库存 | 按制造商建议的检查间隔做**功能检查**；失效模式包括电荷保持能力下降、颗粒沉降、长期储存造成的其他损伤；还可能需定期维护 | §3.1.9<kb doc="AC_20-184.pdf" chunk_id="8ad63261-4aa1-48a3-89f6-79a4d96b97a9" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 使用前检查 | 使用前检查泄漏或变形；**有任何泄漏或变形证据即不得使用** | §3.3.7<kb doc="AC_20-184.pdf" chunk_id="53203e2a-5cd5-4a5c-a617-055352fc022e" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 寿命 | 搁置寿命=规定条件下保持 80% 额定安时容量的最长期限；服务寿命=搁置寿命+装机寿命之和，以“replace-by”或到期日标示 | 附录 C §C.1.12/C.1.13<kb doc="AC_20-184.pdf" chunk_id="2903846b-49b3-4f88-be9e-c5586a0bf906" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="bd396cd7-08ed-4c47-876b-4cb43bd78e7f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="cfda173c-9f1b-4f97-a07a-cb4025ddca20" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 装机与记录 | 更换电池须处于适航状态；更换时检查接口腐蚀与潮气、做绝缘电阻等壳体短路检查；维修记录反映所有更换并记录电池到期日 | §3.2.1、§3.2.4—§3.2.6<kb doc="AC_20-184.pdf" chunk_id="04e4902c-ff05-46f0-a6de-c3445e03ba1b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="2ddeaeed-8202-417d-8733-4e923b381d31" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="eb7ae326-f1c9-49da-9ed5-d5ba1c3173ae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |

关键点：**目视检查只能排除泄漏、变形、腐蚀、热损伤等外部证据，看不到电荷保持能力下降、内阻上升、颗粒沉降这类储存退化**；而 ICA 与特殊条件第 9 项恰恰是围绕“防止低荷电状态长期储存后退化的电池被装上飞机”设置的<kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="cebe871f-6663-409c-956e-cd49647884f5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

## 四、对两个场景的逐项判定

**场景 1：以另一厂商单体替换其中一个电芯，仅做端电压合格检查**

- 批准层面：不满足 §2.9.9 第一句（缺锂电池 OEM 与 FAA 批准）<kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；
- 例外层面：不满足第二句（例外须为 OEM 提出并经 FAA 批准的替代方法）<kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；
- 技术层面：端电压只是 OEM 可规定的性能测量之一，健康状态还应考虑在役时间、环境因素、**负载下低电压**这类已观察到的失效，以及容量、电压、内阻等指标（§3.1.4）<kb doc="AC_20-184.pdf" chunk_id="285efcf3-6ef5-4f17-8e65-c021aa107531" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="f217a696-e519-4df5-a61a-5f4798242cbf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；只测开路端电压无法覆盖容量衰减与内阻差异。此外，单个电芯过充即可能导致热失控（§2.7）<kb doc="AC_20-184.pdf" chunk_id="9f100a8f-66e4-4739-a3eb-b03a20580223" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />，混装电芯的一致性属于安全相关问题，不能靠一次电压检查证明。
- 结论：**不予批准**。若确需推进，应取得“锂电池 OEM + FAA”对电芯更换及混用替代方法的批准文件；否则退回到“整块更换为该飞机应用批准、且与 FAA 批准制造商/件号相同的电池”<kb doc="AC_20-184.pdf" chunk_id="eb7ae326-f1c9-49da-9ed5-d5ba1c3173ae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

**场景 2：长期储存备件外观正常，直接装机**

- 外观正常只覆盖 §3.3.7 的泄漏/变形排除<kb doc="AC_20-184.pdf" chunk_id="53203e2a-5cd5-4a5c-a617-055352fc022e" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />，不能替代 §2.9.7 的备件储存维护程序<kb doc="AC_20-184.pdf" chunk_id="978d6e3b-92b5-4891-ad53-626a58f4109e" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />、§3.3.2 的充电日期与超期维护<kb doc="AC_20-184.pdf" chunk_id="e46d4c5b-7f43-41bc-b158-d6d18bd2914b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />、§3.1.9 的周转库存功能检查<kb doc="AC_20-184.pdf" chunk_id="8ad63261-4aa1-48a3-89f6-79a4d96b97a9" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- 还必须核对：是否仍在搁置寿命/服务寿命（replace-by 日期）内<kb doc="AC_20-184.pdf" chunk_id="2903846b-49b3-4f88-be9e-c5586a0bf906" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="bd396cd7-08ed-4c47-876b-4cb43bd78e7f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；更换电池是否为该机型批准件<kb doc="AC_20-184.pdf" chunk_id="eb7ae326-f1c9-49da-9ed5-d5ba1c3173ae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 且与 FAA 批准的制造商和件号一致<kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；装机时按 §3.2.4/§3.2.5 检查接口腐蚀、潮气与绝缘电阻<kb doc="AC_20-184.pdf" chunk_id="2ddeaeed-8202-417d-8733-4e923b381d31" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；维修记录记录更换与到期日<kb doc="AC_20-184.pdf" chunk_id="eb7ae326-f1c9-49da-9ed5-d5ba1c3173ae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- 结论：**仅凭外观不能放行**；应补齐储存与充电记录、功能/电荷保持检查结果、寿命期与件号符合性证据后再装机。

## 五、三条要求的边界（便于区分）

- **批准对象不同**：电芯级更换针对“电池内部构型变更”，批准人是锂电池 OEM + FAA<kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；整电池更换针对“装机器件”，要求为该飞机应用批准件、并与 FAA 批准的制造商/件号一致<kb doc="AC_20-184.pdf" chunk_id="eb7ae326-f1c9-49da-9ed5-d5ba1c3173ae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- **例外性质不同**：混用厂商电芯的例外是“OEM 提出 + FAA 批准的替代方法”，属符合性方法层面的例外，不是维修级别的偏离<kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。
- **维护依据不同**：储存备件的要求落在 ICA 的备件储存程序与 OEM 储存/维护说明上（充电日期、功能检查、电荷保持、泄漏变形、寿命期）<kb doc="AC_20-184.pdf" chunk_id="978d6e3b-92b5-4891-ad53-626a58f4109e" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="e46d4c5b-7f43-41bc-b158-d6d18bd2914b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="8ad63261-4aa1-48a3-89f6-79a4d96b97a9" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

需要向供应商索取的最小证据清单：锂电池 OEM 对电芯更换的批准、FAA 对该替代方法的批准（或该飞机应用批准件的证明）、电芯一致性与电池级试验影响的评估结论，以及备件的储存记录、最近一次充电日期、功能/电荷保持检查报告与剩余寿命（replace-by）信息。