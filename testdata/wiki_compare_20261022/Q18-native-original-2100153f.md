## 判定基线

依据 AC 20-182A（2016-10-01）第 6.3、6.4、6.5 节及附录 A：**§6.3 抑制的只是“new aural and visual alerts”；图标归 §6.5 管，并且明确规定“不是告警”；反应式系统的 caution 与 warning 在 §6.4.2 里分别处置**。软件把这三层当成一个开关，是全部问题的来源。<kb doc="AC_20-182A.pdf" chunk_id="2fddfdd4-3d86-4123-9677-c296308ec916" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="585c4f48-39c7-4d7d-8a20-dd149d845bdf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="b6ab038f-48c8-4b5d-b900-8b20f9d630fd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

## 一、新告警：三个阶段都应“抑制新告警”，但门槛量各不相同

| 场景 | 文件要求 | 纠正 |
|---|---|---|
| 最后进近 40 ft AGL | §6.3.2：从 **50 ft AGL 至接地**，所有新的系统听觉与视觉 caution、warning 告警均被抑制<kb doc="AC_20-182A.pdf" chunk_id="2fddfdd4-3d86-4123-9677-c296308ec916" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 40 ft 已落在区间内，因此**不发出**新的听觉/视觉告警，只保留位置指示类显示 |
| 巡航 1300 ft AGL | §6.3.3：**1200 ft AGL 以上**，所有新的听觉与视觉 warning 与 caution 告警被抑制<kb doc="AC_20-182A.pdf" chunk_id="2fddfdd4-3d86-4123-9677-c296308ec916" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 1300 ft 在其上，因此**不发出**新告警 |
| 起飞抬轮前 | §6.3.1：在**抬轮前某一指定飞机速度**抑制所有新的听觉与视觉告警，**离地后重新启用**告警能力；起飞告警设定按安装手册，且抑制条件须与该机型特定的起飞告警抑制准则一致<kb doc="AC_20-182A.pdf" chunk_id="db314ed3-2885-4e0a-9350-51c7af101b89" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 判据是**速度**，不是高度或“在地面”；并且离地后必须自动恢复 |

需要纠正的三处理解偏差：

- **三种门槛是三种不同性质的量**（AGL 高度 / AGL 高度 / 指定空速）。用统一的“地面/空中”逻辑或固定高度门限去覆盖起飞场景，不符合 §6.3.1。
- **抑制只约束“新”告警**，不约束探测、不约束既有显示；“检测到新威胁”并不触发抑制，触发抑制的是**当时所处飞行阶段**。
- **抑制不得做成锁存**：起飞场景要求在离地后重新启用<kb doc="AC_20-182A.pdf" chunk_id="db314ed3-2885-4e0a-9350-51c7af101b89" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。若抑制状态在抬轮后仍保持，即偏离。
- 并列条款的优先关系需在审定文件中写清：§6.2.3 以 must 要求在威胁超阈值或位于 TSO-C63 定义区域内时发出视觉文本警告<kb doc="AC_20-182A.pdf" chunk_id="f557cc9a-89a2-43d7-854f-04c5a13f69b0" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />，而 §6.3.2/6.3.3 又要求在这些阶段抑制新告警；文件未明示二者如何衔接，建议在 AFM/S 与符合性记录中明确“抑制优先”，避免实现与验证口径不一。

## 二、图标：“一并清空”没有依据，纠正为按威胁个体管理

1. **图标不是告警**。附录 A 表 1 注 1：“The forward-looking windshear icon is provided as a weather hazard position indication and not an alert.”<kb doc="AC_20-182A.pdf" chunk_id="fad8947b-a20c-4b25-88ac-66004a0cbf95" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 因而 §6.3 那些只针对“aural and visual alerts”的抑制条款，**不能**被用来清理图标。
2. **任何高度都允许显示**。§6.5.1：“It is permissible to display the windshear icon at any altitude at which the system is armed in the windshear mode.”<kb doc="AC_20-182A.pdf" chunk_id="b6ab038f-48c8-4b5d-b900-8b20f9d630fd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 40 ft AGL、1300 ft AGL、抬轮前都不是“必须清除图标”的高度。
3. **清空会抹掉危害位置信息与升级线索**。图标承载的是威胁方位，而 caution 还可能依危害位置升级为时间紧迫的 warning<kb doc="AC_20-182A.pdf" chunk_id="fad8947b-a20c-4b25-88ac-66004a0cbf95" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />——清空全部图标等于把这一升级的可视依据一起抹掉。
4. **还要保证能力完整**。§6.2.2 以 must 要求集成系统能发出表 1 所载**全部** Advisory、Caution、Warning 通告与告警（图标按 §6.5 给出）<kb doc="AC_20-182A.pdf" chunk_id="909cc67e-e161-4efa-ac1b-ec4ed14c9046" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />；“全部图标一并清空”的批量逻辑容易使某等级失去应有呈现。

应改为：图标以**单个威胁的生命周期**增删——威胁进入时新增其图标（允许，无需因处于抑制区而拒绝显示），威胁离开 TSO-C63 所定义区域、系统退出风切变预位模式或探测能力失效时才移除；**新威胁的出现只影响“是否新增告警”，不影响既有图标存留**。若出于显示管理确需减载，须有人因评估支撑，并在 AFM/S 中说明告警提供与抑制的条件<kb doc="AC_20-182A.pdf" chunk_id="893cf31e-cf58-4c82-846a-815043a89d5c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。

## 三、反应式注意与警告：不能“永久关闭”，两者处置完全不同

§6.4.2 正文与注：“you should ensure the reactive windshear system's caution alert is disabled. It is acceptable to issue reactive windshear caution alerts if the forward-looking windshear system is inoperative.” 注：“**The reactive windshear system warning alert should remain enabled.**”<kb doc="AC_20-182A.pdf" chunk_id="585c4f48-39c7-4d7d-8a20-dd149d845bdf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="3b41850f-1a35-407b-a0d1-ea662004ebe6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

逐项纠正：

| 状态 | 应有行为 | 现状问题 |
|---|---|---|
| 前视系统正常工作 | 反应式 **caution 告警应被禁用**<kb doc="AC_20-182A.pdf" chunk_id="585c4f48-39c7-4d7d-8a20-dd149d845bdf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | —— |
| 前视系统失效 | **允许（并应恢复）发出反应式 caution 告警**<kb doc="AC_20-182A.pdf" chunk_id="585c4f48-39c7-4d7d-8a20-dd149d845bdf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 关闭 caution → 丢失本可用的告警能力 |
| 任何状态 | 反应式 **warning 告警保持启用**<kb doc="AC_20-182A.pdf" chunk_id="3b41850f-1a35-407b-a0d1-ea662004ebe6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 关闭 warning → 直接违反注释要求 |
| 前视系统恢复 | 回到“caution 禁用、warning 启用”的常态逻辑 | “永久”锁存 → 不可恢复，属状态机缺陷 |

另外两条必须同时纠正：

- **失效本身要有可见通告**：§6.2.4 要求风切变探测能力失效的通告在机组正常坐姿下易于看到<kb doc="AC_20-182A.pdf" chunk_id="e15e69e4-8c99-41bf-8eb0-6d8195930143" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />。正确表现是“报告前视失效 + 恢复反应式 caution + 保留反应式 warning”，而不是静默关闭。
- **风险叠加**：若前视系统失效后既无可见通告、又永久关闭了反应式 caution 与 warning，则该阶段机上实际不存在任何风切变告警能力——这是本案最严重的后果，应在设计更改中单独评估。

## 汇总：改后的行为

| 层级 | 40 ft AGL 进近 | 1300 ft AGL 巡航 | 抬轮前（规定速度起） |
|---|---|---|---|
| 新告警 | 抑制<kb doc="AC_20-182A.pdf" chunk_id="2fddfdd4-3d86-4123-9677-c296308ec916" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 抑制<kb doc="AC_20-182A.pdf" chunk_id="2fddfdd4-3d86-4123-9677-c296308ec916" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 抑制，离地后恢复<kb doc="AC_20-182A.pdf" chunk_id="db314ed3-2885-4e0a-9350-51c7af101b89" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 图标 | 可显示、不清空<kb doc="AC_20-182A.pdf" chunk_id="b6ab038f-48c8-4b5d-b900-8b20f9d630fd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="fad8947b-a20c-4b25-88ac-66004a0cbf95" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 可显示、不清空<kb doc="AC_20-182A.pdf" chunk_id="b6ab038f-48c8-4b5d-b900-8b20f9d630fd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 可显示、不清空<kb doc="AC_20-182A.pdf" chunk_id="b6ab038f-48c8-4b5d-b900-8b20f9d630fd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 反应式 caution | 前视正常：禁用；前视失效：可发<kb doc="AC_20-182A.pdf" chunk_id="585c4f48-39c7-4d7d-8a20-dd149d845bdf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 同左 | 同左 |
| 反应式 warning | 始终启用<kb doc="AC_20-182A.pdf" chunk_id="3b41850f-1a35-407b-a0d1-ea662004ebe6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 始终启用<kb doc="AC_20-182A.pdf" chunk_id="3b41850f-1a35-407b-a0d1-ea662004ebe6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 始终启用<kb doc="AC_20-182A.pdf" chunk_id="3b41850f-1a35-407b-a0d1-ea662004ebe6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 失效通告 | 需可见<kb doc="AC_20-182A.pdf" chunk_id="e15e69e4-8c99-41bf-8eb0-6d8195930143" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 需可见<kb doc="AC_20-182A.pdf" chunk_id="e15e69e4-8c99-41bf-8eb0-6d8195930143" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> | 需可见<kb doc="AC_20-182A.pdf" chunk_id="e15e69e4-8c99-41bf-8eb0-6d8195930143" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |

相关条目：[[concept/qian-shi-feng-qie-bian-tan-ce|前视风切变探测]]、[[entity/fan-ying-shi-feng-qie-bian-xi-tong|反应式风切变系统]]、[[concept/lei-da-gao-jing-yu-xian-shi-yao-qiu|雷达告警与显示要求]]。需要说明，该 AC 属咨询通告、非强制性，是可接受的符合性方法之一；若采用其方法，则须在所有重要方面一致。