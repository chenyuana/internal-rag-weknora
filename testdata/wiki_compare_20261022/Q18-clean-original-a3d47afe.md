## 判定基线

AC 20-182A（10/1/16，[[entity/ac-20-182a|AC 20-182A]]）对这四条线是分开规定的：**告警抑制**（§6.3）只管“new aural and visual alerts”，**图标**归显示要求（§6.5）且明确“不是告警”，**反应式系统的 caution 与 warning** 由 §6.4.2 分别处置。软件把三者混成一个“清空/关闭”动作，是问题的根源。该 AC 为非强制性指导，但若采用其方法则须在所有重要方面遵循<kb doc="AC_20-182A.pdf" chunk_id="767b9d09-9f10-4d7c-aa91-d1153dbf38c6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

## 一、新告警：三个场景都应“抑制新告警”，但触发条件各不相同

| 场景 | 现状 | 应纠正为 | 依据 |
|---|---|---|---|
| 最后进近 40 ft AGL | 触发新告警 | **抑制**：从 50 ft AGL 至接地，所有**新的**听觉与视觉 caution、warning 告警均被抑制。40 ft 已在该区间内，因此不得发出新告警 | §6.3.2<kb doc="AC_20-182A.pdf" chunk_id="ce6f2e83-d74b-447e-980a-2ecf990575a6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 巡航 1300 ft AGL | 触发新告警 | **抑制**：1200 ft AGL 以上，所有新的 warning 与 caution 告警被抑制。1300 ft 在其上 | §6.3.3<kb doc="AC_20-182A.pdf" chunk_id="ce6f2e83-d74b-447e-980a-2ecf990575a6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 起飞抬轮前 | 触发新告警 | **抑制，但触发量是“规定速度”**：在抬轮前的某一规定飞机速度抑制所有新的听觉与视觉告警，**离地后重新启用**。设定须按安装手册，并与该机型特定的起飞告警抑制准则一致 | §6.3.1<kb doc="AC_20-182A.pdf" chunk_id="ce6f2e83-d74b-447e-980a-2ecf990575a6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |

三处要点：

- 抑制的宾语是“**new** aural and visual alerts”，即不新发告警；它不授权、也不要求把已有显示抹掉。
- 抬轮前抑制的判据是**速度**而非高度或“在地面”，且**离地后必须恢复**。若实现为“落地/离地状态锁存”或起飞后仍不恢复，属偏离。
- 抑制逻辑本身是审定验证项：第 9 节要求确认告警、**告警抑制**、annunciation 与控制功能均正确工作<kb doc="AC_20-182A.pdf" chunk_id="07ef1485-1cd9-4a11-b027-5460b7cebed0" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。另有 AFM/S 义务：说明告警何时提供、何时被抑制<kb doc="AC_20-182A.pdf" chunk_id="ff3483c5-e4a4-4db8-b708-b179fb3d0070" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

## 二、图标：“一并清空”没有依据，且方向相反

纠正三点：

1. **图标不是告警**。附录 A 表 1 注 1 明确：前视风切变图标是“weather hazard position indication and not an alert”<kb doc="AC_20-182A.pdf" chunk_id="eb6d3cac-8cfe-49b1-b8e3-8acbdb6a5ab4" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。因此 §6.3.1–6.3.3 这些约束“aural and visual alerts”的抑制条款，**不能**被援引作为清除图标的理由。
2. **任何高度都允许显示**。§6.5.1：“It is permissible to display the windshear icon at any altitude at which the system is armed in the windshear mode.”<kb doc="AC_20-182A.pdf" chunk_id="a822f52e-2c7a-40d4-9c93-36006fd0b463" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> 所以 40 ft AGL、1300 ft AGL、抬轮前都不是“图标必须消失”的高度；允许显示（非强制），但**清空既有图标不属于该条允许的设计选择**。
3. **“新威胁 ⇒ 清空全部”破坏了威胁的可视连续性**。既有图标对应的威胁若仍在 TSO-C63 定义的告警区域内，抹掉它等于丢失位置指示；而 caution 还可能升级为时间紧迫的 warning<kb doc="AC_20-182A.pdf" chunk_id="eb6d3cac-8cfe-49b1-b8e3-8acbdb6a5ab4" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />，清空会同时抹掉这一升级的可视依据。此外，系统本应能发出表 1 中**全部** Advisory、Caution、Warning 三个等级的提示与告警<kb doc="AC_20-182A.pdf" chunk_id="ce6f2e83-d74b-447e-980a-2ecf990575a6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-182A.pdf" chunk_id="1ec56c3b-70b6-4040-aff9-abf8eebbb910" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

应改为：图标按**单个威胁的生命周期**管理——威胁进入/移出定义区域、系统退出风切变预位模式或失去有效性时才增删；新威胁出现只影响“是否新增告警”，不影响既有图标的存留。若确有显示拥挤等原因需要移除，须以人因评估和相应显示/告警功能验证支撑<kb doc="AC_20-182A.pdf" chunk_id="07ef1485-1cd9-4a11-b027-5460b7cebed0" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />，并在 AFM/S 中写明<kb doc="AC_20-182A.pdf" chunk_id="ff3483c5-e4a4-4db8-b708-b179fb3d0070" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。

## 三、反应式 caution 与 warning：不能“永久关闭”，两者处置不同

现行为“前视系统失效时永久关闭反应式注意和警告”，须按 §6.4.2 及其注拆成三条纠正：

| 状态 | 应纠正为 | 依据 |
|---|---|---|
| 前视系统**正常** | 反应式系统的 **caution 告警应被禁用**（避免与前视告警重复/冲突） | §6.4.2<kb doc="AC_20-182A.pdf" chunk_id="a822f52e-2c7a-40d4-9c93-36006fd0b463" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 前视系统**失效** | **允许发出**反应式 caution 告警——即失效时应恢复 caution，而不是关闭 | §6.4.2<kb doc="AC_20-182A.pdf" chunk_id="a822f52e-2c7a-40d4-9c93-36006fd0b463" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| 任何状态 | 反应式系统的 **warning 告警应保持启用**，不得因前视系统失效而关闭 | §6.4.2 注<kb doc="AC_20-182A.pdf" chunk_id="a822f52e-2c7a-40d4-9c93-36006fd0b463" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |

另外两点：

- **“永久”不成立**。前视系统失效是可能恢复的状态，恢复后应回到“caution 禁用、warning 启用”的常态逻辑；把关闭做成锁存且不可恢复，会使飞机永久失去反应式告警能力。
- **失效本身要有指示**：应确保风切变探测能力失效的 annunciation 在机组正常坐姿即可见<kb doc="AC_20-182A.pdf" chunk_id="ce6f2e83-d74b-447e-980a-2ecf990575a6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。正确做法是“报出前视系统失效 + 恢复反应式 caution + 保留反应式 warning”，而不是静默地把整条反应式告警链关掉。

## 修改后应满足的行为（自检清单）

- 40 ft AGL / 1300 ft AGL / 抬轮前规定速度之后：**不新发**听觉与视觉 caution、warning；离地后（起飞场景）自动恢复告警能力<kb doc="AC_20-182A.pdf" chunk_id="ce6f2e83-d74b-447e-980a-2ecf990575a6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
- 上述任何阶段：**不清空**既有图标；图标仅随威胁离开定义区域或系统退出预位/失去有效性而移除；表 1 三等级提示与告警仍可实现<kb doc="AC_20-182A.pdf" chunk_id="1ec56c3b-70b6-4040-aff9-abf8eebbb910" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-182A.pdf" chunk_id="eb6d3cac-8cfe-49b1-b8e3-8acbdb6a5ab4" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
- 反应式系统：前视正常 → caution 禁用、warning 启用；前视失效 → caution 可发、warning 保持启用、失效指示可见<kb doc="AC_20-182A.pdf" chunk_id="ce6f2e83-d74b-447e-980a-2ecf990575a6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /><kb doc="AC_20-182A.pdf" chunk_id="a822f52e-2c7a-40d4-9c93-36006fd0b463" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。
- AFM/S 中写明告警提供与抑制的条件，以及失效时的机组动作<kb doc="AC_20-182A.pdf" chunk_id="ff3483c5-e4a4-4db8-b708-b179fb3d0070" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；相关抑制与告警功能纳入第 9 节测试验证<kb doc="AC_20-182A.pdf" chunk_id="07ef1485-1cd9-4a11-b027-5460b7cebed0" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。