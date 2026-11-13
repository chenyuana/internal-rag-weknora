## 先说明：为什么一句“按制造商手册维护”不成立

1. **ICA 不是设备手册的合集，而是与安装构型绑定的批准文件。** AML-STC 要求按 14 CFR 21.50 并提供满足相应部（23/25/27/29/31/33/35）ICA 规则的 ICA；<kb doc="AC_20-180.pdf" chunk_id="cf20a9b5-9a09-41ee-a0e2-ced150cd43ac" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 在 AML 表中，每个型号都要登记 ICA 的**文件号、修订水平和日期**。<kb doc="AC_20-180.pdf" chunk_id="7db59726-1004-40bb-b5c2-df861c615f5b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
2. **AML 多型号项目本身就有“逐型号差异”。** 安装说明须详细到使后续安装可重复，并在正确执行时**对每个型号形成一致且合规的安装**，可采用“通用章＋型号附录”的格式；<kb doc="AC_20-180.pdf" chunk_id="f1957fc4-b9af-41b8-887a-9a3ce7c288e1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="66579eb2-b378-478d-87a0-705a17d13cd1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> AFM 可能对每个型号分别增加补充章节；<kb doc="AC_20-180.pdf" chunk_id="f3cf3ed9-23bc-4013-9595-0aff4cfb5b40" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 部件 P/N 列还要求保证**所有型号使用同一部件**。<kb doc="AC_20-180.pdf" chunk_id="3d5a200c-1577-4919-ad80-47c59ef6fddb" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
3. **三个子系统都有“手册里没有、只有安装才产生”的维护项**：雷达罩修理后的性能下限、电池容量测量间隔与通气、激光的联锁与可达发射限值相关程序（见下）。

---

## 一、多型号安装层（框架性核对）

- **逐型号索引**：ICA 修订号与批准日期必须与 AML 表中该型号的条目一致；型号专用注记栏须记录针对**部件本身**（而非整机）的 AD/SB 及任何附加限制或条件。<kb doc="AC_20-180.pdf" chunk_id="7db59726-1004-40bb-b5c2-df861c615f5b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="39e96ce5-226b-43b0-ba20-7f73dcc3b18b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **构型控制锚点**：每个型号的 ICA 应指向该型号的 MDL/安装图**修订号**（构型控制文件），替换文件须能实现可追溯与构型控制目的。<kb doc="AC_20-180.pdf" chunk_id="6d2558b1-93de-41cd-982c-54981e3462ab" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **安装差异须在 ICA 中显性化**：结构连接（金属蒙皮/加强片材料与厚度差异）、闪电防护集成、复合材料开孔等，凡影响检查可达性或复装一致性的，都要写成型号附录条目。<kb doc="AC_20-180.pdf" chunk_id="f1957fc4-b9af-41b8-887a-9a3ce7c288e1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="66579eb2-b378-478d-87a0-705a17d13cd1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **与 AFMS 的分工**：运行限制与操作程序在 AFMS，维修与检查在 ICA；两者对同一项目（如雷达地面危害区、激光 NOHD、电池低电量告警）的数值必须一致，不能各写一套。

## 二、气象雷达与雷达罩（AC 20-182A 第 11 节，属“应”包含）

| 必须写进 ICA 的内容 | 具体要求/判据 |
|---|---|
| 雷达系统与**雷达罩**的维护说明 | 分系统级，不能只引用雷达厂家手册 <kb doc="AC_20-182A.pdf" chunk_id="968d7512-56b4-4fd1-b714-f99d099ca238" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 雷达与飞机的接口说明 | 需覆盖供电、显示/告警、与姿态航向等数据源的接口，维修后按此做功能验证 <kb doc="AC_20-182A.pdf" chunk_id="0c102c4a-65fe-4aa1-a447-42f3ccfa3880" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| **校准说明** | 目标是使雷达罩与天线性能维持**等于或优于基本系统取证时所示的水平**——这是可量化下限，不是“按手册” <kb doc="AC_20-182A.pdf" chunk_id="cb4ef52a-091c-45fb-bd05-992cabe9e65c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| **检查间隔** | 须分别给出雷达系统与雷达罩的检查间隔 <kb doc="AC_20-182A.pdf" chunk_id="cb4ef52a-091c-45fb-bd05-992cabe9e65c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| **危害区域** | 列出雷达运行的危害区域，并与 AFMS 中“地面运行危害区域”一致 <kb doc="AC_20-182A.pdf" chunk_id="cb4ef52a-091c-45fb-bd05-992cabe9e65c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="893cf31e-cf58-4c82-846a-815043a89d5c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 雷达罩修理/更换准则 | 高性能雷达罩的物理特性微小变化即会不利影响性能；**任何修理，不论多小**，都应使雷达罩恢复到飞机气象雷达运行所需的**最低性能**；修理或更换时参照 AC 43-14 与 RTCA/DO-213A 最新修订 <kb doc="AC_20-182A.pdf" chunk_id="3ee7f730-6ea4-447c-9361-50e281f5eb34" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="e4b5d481-34f2-488e-968d-30cb2bf62141" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |

> 提示：本节用“should”，属可接受方法；若按该 AC 取证，仍应按其全部条款执行。

## 三、可充电锂电池（AC 20-184 §2.9 与第 3 章，“必须”项较多）

**编制基础**：ICA 须按 21.50(b)、23/25/27/29.1529、25.1709/25.1729、23 部附录 G、25 部附录 H、27/29 部附录 A 及 FAA Order 8110.54 编制，并**与飞机其他维修说明兼容**。<kb doc="AC_20-184.pdf" chunk_id="bb862427-f113-45e2-8b14-8c045b09e4d1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="ff861126-d79b-4cb1-a249-5829608f61d8" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="dec51ffa-6379-47b7-ad3a-e98d7eb9dddf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 必要时须含 **FAA 批准的“适航限制”部分**，规定 43.16 与 91.403 项下的维修。<kb doc="AC_20-184.pdf" chunk_id="784b1600-6daf-4f01-af17-957d75ca937f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**必须包含的五类内容**：

1. 安装维护手册中的操作说明与**设备限制**；<kb doc="AC_20-184.pdf" chunk_id="86429ba6-e1eb-4849-a2db-ab4cc3756780" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
2. 安装程序与限制，足以保证电芯/电池按程序安装后仍满足飞机适航要求，且**限制须标明该安装的任何独特方面**；<kb doc="AC_20-184.pdf" chunk_id="4d811c87-5e8b-46f6-b2b9-e2aa201af99f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
3. **按适当间隔测量电池容量**的维护要求；<kb doc="AC_20-184.pdf" chunk_id="9d41524d-f3f2-4f91-bd91-24cb103da037" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
4. 按制造商建议**更换电池的计划勤务信息**；<kb doc="AC_20-184.pdf" chunk_id="06b29856-3a54-44fc-a74a-73b7fb0892f3" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
5. **目视检查电池和/或充电器退化**的维护与检查要求。<kb doc="AC_20-184.pdf" chunk_id="06b29856-3a54-44fc-a74a-73b7fb0892f3" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**必须核对的具体条目（易被“按手册”漏掉）**：

- **更换**：须含按锂电池 OEM 维护手册更换电池的说明；<kb doc="AC_20-184.pdf" chunk_id="c4ee2801-0501-41ac-94b3-bd84867760dd" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 更换电池须为 FAA 批准的同一制造商与件号；<kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> **单个电芯更换须经 OEM 与 FAA 批准**，且非经批准替代方法不得在同一电池内混用不同制造商电芯。<kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **备件储存**：须含备件库存电池的维护程序，防止把因长期低荷电储存而容量衰减或受损的电池装回飞机。<kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="466b4563-a59f-4622-afc7-39a7acad42eb" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **误操作防护**：须含防止跌落、短路等造成人身伤害或财产损失的注意事项。<kb doc="AC_20-184.pdf" chunk_id="b317e82f-24e7-4850-a956-df4b5f92f9d3" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **机械完整性与通气**：电池须正确安装连接、无物理损伤；通气系统须按维护手册**定期检查连接牢固与方向正确**，并兼顾飞机与电池制造商的具体安装要求。<kb doc="AC_20-184.pdf" chunk_id="22449144-3ff6-45c3-94cc-ea49344292ea" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="815bcdf9-8750-4093-ad5c-61200641e667" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **寿命与年龄**：记录制造/安装日期，维修记录或车间记录中登记电池年龄，不得超过制造商建议的使用期限。<kb doc="AC_20-184.pdf" chunk_id="f6344d07-e516-4fd5-95b7-df9d68bcb7e2" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **荷电状态**：须有保障措施确保飞机不在电池电量不足以完成预定功能时起飞。<kb doc="AC_20-184.pdf" chunk_id="a92137ac-6502-4e14-98b2-7acfdab45ac3" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **健康状态指标**：在役时间、环境因素、观察到的故障（如负载下低电压）以及制造商规定的容量/电压/内阻等测量值。<kb doc="AC_20-184.pdf" chunk_id="285efcf3-6ef5-4f17-8e65-c021aa107531" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="f217a696-e519-4df5-a61a-5f4798242cbf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **目视检查项目**：端子与其他连接处的腐蚀、点蚀、电弧、烧伤并清洁；安装不当（端子螺钉、连接片、连接器松动）；电池安装座；包括热损伤/变色在内的物理损伤证据。<kb doc="AC_20-184.pdf" chunk_id="a9169c55-2ce0-461c-a84e-ecb2bd9fe23a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="73fd6c62-cbb1-43f8-9ba4-b2b0c223c23a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

## 四、不可见激光（AC 20-183 §7.3.9，“应”包含的七项激光服务信息）

1. 带适当警告与注意事项的**维修程序**，避免暴露于超过可达发射限值（AEL）的激光与附带辐射；<kb doc="AC_20-183.pdf" chunk_id="7f45d937-8fa8-44ac-aafa-9949d129e56b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
2. 使产品**保持符合性**的维护计划；<kb doc="AC_20-183.pdf" chunk_id="7f45d937-8fa8-44ac-aafa-9949d129e56b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
3. **可能提高可达辐射水平**的控制装置与程序清单；<kb doc="AC_20-183.pdf" chunk_id="91f212f8-df9f-4b87-9755-b510f02e0ff1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
4. 可拆卸防护罩部位的识别——这些部位会让人体接触超过 AEL 的激光或附带辐射；<kb doc="AC_20-183.pdf" chunk_id="91f212f8-df9f-4b87-9755-b510f02e0ff1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
5. 针对**每一项维修程序或其序列**，避免暴露于已知危害水平的激光与附带辐射的程序；<kb doc="AC_20-183.pdf" chunk_id="f1341532-83d6-42e7-92f0-e75244076c94" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
6. 所需标签（颜色可选）与警告的**复制件**；<kb doc="AC_20-183.pdf" chunk_id="f1341532-83d6-42e7-92f0-e75244076c94" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
7. 所需标签与警告在设备上的**位置**。<kb doc="AC_20-183.pdf" chunk_id="e0d3a95b-0d5d-4551-94cf-4ca899bd7fa1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**与运行限制联动、必须逐条核对的内容**：

- **钥匙控制**：地面及滑行、起飞、着陆期间须处于关断位（FDA IIIb/IV、IEC 3B/4）——ICA 中要有对应的功能检查与复装后验证步骤。<kb doc="AC_20-183.pdf" chunk_id="3d70a359-13fa-44bb-a3f1-664c66c8d7c1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **飞机接口安全联锁**：任何需要与飞机系统接口的联锁不可用时不得使用激光；ICA 须列出联锁清单与功能测试方法（如与雷达高度表联动、低于规定离地高度禁用）。<kb doc="AC_20-183.pdf" chunk_id="f6cb5b79-d6bd-4be0-8797-3560ce9ce20a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **NOHD 数值**：AFMS 或标牌上规定的 NOHD 须与 ICA 中的校准/检查方法配套；多 LIDAR 构型可用驾驶舱标牌标识新型号与 NOHD 代替修订 AFMS。<kb doc="AC_20-183.pdf" chunk_id="3d70a359-13fa-44bb-a3f1-664c66c8d7c1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="f811cd0e-3155-41ea-a6ea-c1167942dc4a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **构型控制**：任何未经批准的更改（含软件、硬件、光学件）都可能使激光设备认证与 FDA 差异失效，ICA 须与服务中的构型控制记录挂钩。<kb doc="AC_20-180.pdf" chunk_id="6d2558b1-93de-41cd-982c-54981e3462ab" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **建议项**：按 ANSI Z136.1 第 1.3 段建立激光安全计划。<kb doc="AC_20-183.pdf" chunk_id="d5baa8a2-e571-4a7c-ae9f-5de563206694" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

## 五、建议的 ICA 结构

```
第 1 章  通用：适用范围、AML 型号索引、构型控制、记录要求
第 2 章  安装说明（可重复性、型号差异、闪电/EMC 集成）
第 3 章  气象雷达与雷达罩（维护、接口、校准、间隔、危害区、修理准则）
第 4 章  可充电锂电池（AWR、容量测量间隔、更换、储存、通气、检查）
第 5 章  不可见激光（七项服务信息、联锁/钥匙控制测试、NOHD）
附录 A～N  每个型号的专用条目（结构连接、接近方式、P/N、AD/SB）
```

## 交付前自检表

| 检查点 | 通过判据 | 依据 |
|---|---|---|
| 型号完整性 | AML 每个型号都有 ICA 文件号/修订/日期 | <kb doc="AC_20-180.pdf" chunk_id="7db59726-1004-40bb-b5c2-df861c615f5b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 安装可重复 | 每个型号按说明可复现一致且合规的安装 | <kb doc="AC_20-180.pdf" chunk_id="f1957fc4-b9af-41b8-887a-9a3ce7c288e1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 雷达罩性能 | 校准后性能 ≥ 基本系统取证水平；任何修理恢复到最低性能 | <kb doc="AC_20-182A.pdf" chunk_id="cb4ef52a-091c-45fb-bd05-992cabe9e65c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="3ee7f730-6ea4-447c-9361-50e281f5eb34" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 雷达危害区 | ICA 与 AFMS 数值一致 | <kb doc="AC_20-182A.pdf" chunk_id="cb4ef52a-091c-45fb-bd05-992cabe9e65c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-182A.pdf" chunk_id="893cf31e-cf58-4c82-846a-815043a89d5c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 电池容量 | 有明确测量间隔与判据 | <kb doc="AC_20-184.pdf" chunk_id="9d41524d-f3f2-4f91-bd91-24cb103da037" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 电池更换 | 同制造商同件号；电芯更换经批准 | <kb doc="AC_20-184.pdf" chunk_id="71242e42-f355-4cec-a2d8-8ccd7d2d2b8f" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="e512be5c-f95c-4de7-8694-898001bcea65" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 激光服务信息 | 七项齐全，含每项程序的防照射步骤 | <kb doc="AC_20-183.pdf" chunk_id="7f45d937-8fa8-44ac-aafa-9949d129e56b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="f1341532-83d6-42e7-92f0-e75244076c94" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="e0d3a95b-0d5d-4551-94cf-4ca899bd7fa1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |
| 激光联锁 | 钥匙控制与飞机接口联锁有测试步骤 | <kb doc="AC_20-183.pdf" chunk_id="3d70a359-13fa-44bb-a3f1-664c66c8d7c1" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="f6cb5b79-d6bd-4be0-8797-3560ce9ce20a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> |

**一句话：** “所有设备按制造商手册维护”缺的不是文件名称，而是**与安装构型绑定的判据**——雷达罩的性能下限与校准、雷达的地面危害区、电池的容量测量间隔与更换/储存规则、激光的七项服务信息与联锁测试。这些都必须以数值、间隔、验收标准和型号附录的形式写进 ICA，而不是交给设备手册。<kb doc="AC_20-182A.pdf" chunk_id="cb4ef52a-091c-45fb-bd05-992cabe9e65c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-184.pdf" chunk_id="9d41524d-f3f2-4f91-bd91-24cb103da037" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-183.pdf" chunk_id="7f45d937-8fa8-44ac-aafa-9949d129e56b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

> 三份 AC 均为咨询通告、非强制法规；但按 21.50 与各部 ICA 规则的强制要求仍然成立。<kb doc="AC_20-180.pdf" chunk_id="cf20a9b5-9a09-41ee-a0e2-ced150cd43ac" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 延伸阅读：[[concept/lei-da-tian-xian-zhao-wei-hu|雷达天线罩维护]]、[[concept/instructions-for-continued-airworthiness-lithium-battery|锂电池持续适航文件]]、[[concept/chixu-shihang-shuoming|激光持续适航说明]]、[[concept/installation-instructions-and-ica|安装说明与 ICA]]。