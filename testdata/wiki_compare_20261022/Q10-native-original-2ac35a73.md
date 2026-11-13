## 结论

经理的判定依据用错了。是否需要重新评估，取决于**变更的实质与影响**，而不是是否新增机型。

AC 20-180 第 9.b 段专门处理这种情形：**STC 持有人不向 AML 增加新型号，而是对 AML 上现有硬件或部件做升级（例如软件修订）**。文件要求：仔细考虑，确保新修订不对先前批准产生非预期后果；并直接举例称，**软件修订可能在音响或视觉显示上带来新功能，需要新的飞行机组培训以识别警告和系统失效**，这可能影响飞机的运行特性或限制，**可能需要进一步评估飞行员工作负荷、人为因素以及修订软件带来的其他后果**。<kb doc="AC_20-180.pdf" chunk_id="dd8c381a-d9b8-4b71-aa70-a404d8238ddf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="bdaee47e-ca24-466f-afa7-b0c129084d88" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="99c539af-a227-423c-ad78-b15e54e9bbae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

因此，“不是新增机型”只意味着不必追加 AML 型号条目，**不意味着可以免于重新评估**。

## 一、变更定性与批准路径

- 对 AML-STC 的**重大更改**（如增加型号、修订现有型号）需 FAA 或授权 ODA 批准；**轻微更改**通常通过证书管理协议处理，或按 FAA 接受的持有人内部流程处理。<kb doc="AC_20-180.pdf" chunk_id="78850fe3-ad36-47b5-9279-c75f02cf8c5f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 软件升级若改变告警内容、告警等级或激光指向限位，就不应被归入“轻微”处理。
- AML-STC **不是“一揽子批准”**：每个新增或修订型号都需按 14 CFR 21.20 表明符合并提交型号设计、证实数据与飞行手册补充（FMS）；与已批准型号存在差异时需补充证实；**受改装影响区域的认证基础与修正案水平按每个型号单独确定**；FMS 须对每个型号适用。<kb doc="AC_20-180.pdf" chunk_id="0b7835d6-504d-4665-816e-3b15cb3fb84d" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="54cefa7a-b21f-45f0-897e-6cb10848502a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="d11310b2-0451-4004-b8f0-ac873322592f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**审查问题**：本次软件升级被归为重大更改还是轻微更改？依据是什么？批准路径（STC 修订 / 证书管理协议）是否已确定？

## 二、多型号适用性（不能用一个型号的结论覆盖全清单）

基线数据在整个型号清单中持续适用于每个型号，但**差异必须逐型号补充证实**；AML-STC 不能用来免除证实义务。<kb doc="AC_20-180.pdf" chunk_id="0b7835d6-504d-4665-816e-3b15cb3fb84d" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="54cefa7a-b21f-45f0-897e-6cb10848502a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**审查问题**：新软件在各型号上的显示分辨率、告警音频通路、显示优先级逻辑、AFMS 修订水平是否逐一核对？哪些型号存在接口差异、因而需要单独证实？

## 三、新声光提示本身的告警合规性

- 告警与通告必须遵循该机驾驶舱告警理念，并符合 14 CFR §25.1322、AC 25.1322-1、AC 23.1311-1。<kb doc="AC_20-182A.pdf" chunk_id="7ae0b4b6-ea92-4c87-bb39-f979118f1472" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="cd9b67b6-d2cb-468e-9298-ac0bef2ab628" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- 集成系统须能发出**附录 A 表 1 所描述的全部** Advisory、Caution、Warning 通告与告警。<kb doc="AC_20-182A.pdf" chunk_id="909cc67e-e161-4efa-ac1b-ec4ed14c9046" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- 显示须**清晰无歧义**，包括格式、颜色、标签、数据格式，以及**与其他显示参数的交互**；颜色递进语义须遵循 AC 25-11 附录 G、AC 25.1302-1、AC 25.1322-1、AC 23.1311-1。<kb doc="AC_20-182A.pdf" chunk_id="ea04151a-fb24-4d9f-93d5-586478efc120" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="b1dad6f1-6cff-4c71-9afa-0217cf0d90da" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**审查问题**：新提示属于哪一级告警？文本、颜色、图标、听觉是否符合上述判据？是否与既有告警在同一区域相互遮挡？

## 四、告警优先级与多源同屏互不干扰

**所有**飞机告警都应经过优先级排序；若告警可能**同时发出或由不同系统发出**，须确保互不干扰且**两者都可理解**（TSO-C151c 附录 1 表 4-2 为可接受示例；25 部另见 AC 25.1322-1 第 8.b 节多听觉告警）。<kb doc="AC_20-182A.pdf" chunk_id="df93f732-5b72-4ef5-9937-ba345245a1a5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="a084e20d-70e2-40c1-88da-350b97a48952" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**审查问题**：新旧告警的优先级矩阵是否重做？同一秒内两路听觉告警的仲裁规则、谁抑制谁，是否有试验证据？

## 五、激光指向限位：这是软件实现的安全功能，必须重新验证

- 系统安全评估须考虑**机械、软件或 AEH 止动装置**，用以防止激光被转向可能导致乘员眼暴露于直接或反射辐射的方向；**若转向止动由软件或 AEH 实现，其保证等级应与该止动装置相关的功能失效状态相称**。<kb doc="AC_20-183.pdf" chunk_id="ee697ad7-f6e1-44a7-9fad-f9a857b99707" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="2fda42a9-555d-4f19-b449-1c2bd44c7e15" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="bb1c6e20-c40a-4ddc-a151-f98ff15a975f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- 该失效状态的定性很高：激光故障导致机组或乘客眼/皮肤暴露超过 MPE，**至少为“危害性”功能失效**；若因飞行员眼/皮肤损伤严重而无法继续安全飞行，**可能为灾难性**。<kb doc="AC_20-183.pdf" chunk_id="b6edd349-62c3-4e18-9330-5e4587da9e79" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="b5a1731f-6376-498d-bbaf-ffc45b92cd01" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- 软件若可能促成上述失效，须按 AC 20-115C 开发，**软件等级与失效状态分类相称**。<kb doc="AC_20-183.pdf" chunk_id="3ebd9390-a1ab-46d8-8f14-70562e6f3775" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**审查问题**：升级后的软件是否重新判定软件等级（原等级是否仍成立）？指向限位的实现与验证是否独立于被升级的显示功能（避免共用代码或共用资源导致共因失效）？“限位失效→越界指向→超 MPE”的路径是否重新做过 FMEA/FTA？

## 六、构型控制、重新认证与 FDA 差异

- AC 20-183 §7.3.6：**不应**对激光设备或安装做未经批准的更改，因为可能影响适航性（如电磁兼容、环境兼容性或引入新的失效模式），并使激光设备认证与 FDA 差异**失效**；申请人须提供全寿命周期构型保持计划；**若安装导致对制造商已认证的激光设备进行修改，须按 §1040.10(i) 重新认证**。<kb doc="AC_20-183.pdf" chunk_id="bf4b9eb5-3af4-48cf-a84a-e8630ce3d125" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="6e652ed4-c5c6-4aa7-baa7-a8a355f50a56" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- 安装型号设计须包含适用的 21 CFR 1040 要求（钥匙控制、发射指示器、标签、远程联锁连接器）与 FDA 差异中的技术控制（如飞机接口安全联锁）。<kb doc="AC_20-183.pdf" chunk_id="2d2cecf3-dc32-48c8-a5a7-07dfbe52980c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- 非 Class I 激光须完成并记录 NOHD/MPE 计算报告。<kb doc="AC_20-183.pdf" chunk_id="68455996-fd78-4cb2-8e9e-93da6214e438" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**审查问题**：软件改动是否构成“对已认证激光设备的修改”（→ 重新认证）？FDA 差异是否需要修订？EMC/环境鉴定是否需要重做或出具影响分析？NOHD 是否因指向限位逻辑改变而变化？

## 七、文件化与培训

- AML 构型控制表须记录 TCDS、MDL/安装图、件号、型号专用注记、初始批准与修订日期，以保持可追溯性。<kb doc="AC_20-180.pdf" chunk_id="54cefa7a-b21f-45f0-897e-6cb10848502a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />（构型控制条款）
- AC 20-180 §9.b 明确：新音响/视觉功能**可能需要新的飞行机组培训**以识别警告和系统失效；可能影响运行特性或限制。<kb doc="AC_20-180.pdf" chunk_id="bdaee47e-ca24-466f-afa7-b0c129084d88" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="99c539af-a227-423c-ad78-b15e54e9bbae" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**审查问题**：AML 表中软件件号/版本是否更新？FMS/AFMS 修订水平是否重批？培训大纲与模拟机科目是否覆盖新告警？

## 审查清单（可直接用于评审会）

| # | 审查方面 | 关键问题 | 主要依据 |
|---|---|---|---|
| 1 | 变更定性 | 重大还是轻微？批准路径？ | AC 20-180 §9 <kb doc="AC_20-180.pdf" chunk_id="78850fe3-ad36-47b5-9279-c75f02cf8c5f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 2 | 多型号适用性 | 逐型号差异是否补充证实？ | AC 20-180 基线数据要求 <kb doc="AC_20-180.pdf" chunk_id="0b7835d6-504d-4665-816e-3b15cb3fb84d" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="54cefa7a-b21f-45f0-897e-6cb10848502a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 3 | 告警合规 | 三级告警齐备、清晰无歧义、颜色语义 | AC 20-182A 5.1/5.2/6.2 <kb doc="AC_20-182A.pdf" chunk_id="7ae0b4b6-ea92-4c87-bb39-f979118f1472" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="909cc67e-e161-4efa-ac1b-ec4ed14c9046" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="ea04151a-fb24-4d9f-93d5-586478efc120" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 4 | 优先级 | 同时/异源告警互不干扰且可理解 | AC 20-182A 5.5 <kb doc="AC_20-182A.pdf" chunk_id="df93f732-5b72-4ef5-9937-ba345245a1a5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="a084e20d-70e2-40c1-88da-350b97a48952" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 5 | 激光限位软件 | 软件等级与失效分类相称、重新验证 | AC 20-183 7.3.1.2/7.3.4 <kb doc="AC_20-183.pdf" chunk_id="bb1c6e20-c40a-4ddc-a151-f98ff15a975f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="3ebd9390-a1ab-46d8-8f14-70562e6f3775" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 6 | 失效后果 | 超 MPE 至少“危害性”，可能灾难性 | AC 20-183 7.3.1.1 <kb doc="AC_20-183.pdf" chunk_id="b6edd349-62c3-4e18-9330-5e4587da9e79" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 7 | 重新认证/差异 | 是否修改已认证设备、FDA 差异是否失效 | AC 20-183 7.3.6 <kb doc="AC_20-183.pdf" chunk_id="bf4b9eb5-3af4-48cf-a84a-e8630ce3d125" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="6e652ed4-c5c6-4aa7-baa7-a8a355f50a56" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 8 | 构型与培训 | 件号/版本、FMS 修订、机组培训 | AC 20-180 §9 <kb doc="AC_20-180.pdf" chunk_id="bdaee47e-ca24-466f-afa7-b0c129084d88" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |

**一句话：** “不新增机型”只改变 AML 清单是否需要增加条目，不改变“软件修订可能对先前批准产生非预期后果”这一判断；<kb doc="AC_20-180.pdf" chunk_id="dd8c381a-d9b8-4b71-aa70-a404d8238ddf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="bdaee47e-ca24-466f-afa7-b0c129084d88" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 尤其当激光指向限位由软件实现时，软件升级等同于改动一项安全功能的实现方式，必须重做系统安全分析、软件等级判定与构型控制。<kb doc="AC_20-183.pdf" chunk_id="bb1c6e20-c40a-4ddc-a151-f98ff15a975f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="3ebd9390-a1ab-46d8-8f14-70562e6f3775" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="bf4b9eb5-3af4-48cf-a84a-e8630ce3d125" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

> 上述三份文件均为咨询通告、非强制法规；但若按其方法取证，须在重要方面完整遵循。延伸阅读：[[concept/aml-stc-configuration-control-and-type-design-change|AML-STC构型控制与型号设计更改管理]]、[[concept/jiguang-shebei-ruanjian-baozheng|激光设备软件保证]]、[[concept/xitong-anquan-fenxi|系统安全分析]]、[[concept/gouwang-kongzhi|构型控制]]。