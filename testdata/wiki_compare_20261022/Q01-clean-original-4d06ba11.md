## 结论

| 判断项 | 结论 |
|---|---|
| 用同一份多型号改装批准（AML-STC）同时覆盖 Part 23 固定翼与 Part 27 旋翼机 | **不可行**。AC 20-180 明确规定 AML-STC 只签发给“同一类别”取证的航空器，并直接举例：按 Part 23 签发的 AML-STC **不能包含**按 Part 25、27 或 29 取证的航空器<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| “指导文件覆盖四类航空器”使前视风切变指导也覆盖 Part 27 | **不成立**。AC 20-182A 第 1.1 段在“适用于 Part 23、25、27、29 部航空器”之后紧接着限定：对于前视风切变和/或湍流探测能力，**本 AC 的指导仅适用于 Part 25 与 Part 23 固定翼飞机安装**<kb doc="AC_20-182A.pdf" chunk_id="767b9d09-9f10-4d7c-aa91-d1153dbf38c6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |

即：**设备层面可以共用**（同一 TSO-C63e 型号、同一穿透数据），**批准层面与安装指导层面都不能跨类别共用**。

---

## 一、批准清单的组织方式

### 1. 类别限制是硬性条件，与雷达型号是否相同无关

“An AML-STC is issued for aircraft that are type-certificated in the same category (e.g., an AML-STC for an aircraft certificated under 14 CFR part 23 cannot include aircraft certificated under parts 25, 27, or 29)”<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。该条不含“除非基线数据相同”之类的例外，因此“雷达型号和基线数据相同”无法绕过它。

### 2. 清单必须逐型号组织，且不能当成一揽子批准

- 必须清楚确立基线数据对**每一个**型号的适用性<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；
- 每个型号都须表明符合 §21.20 并具备相应数据（型号设计、证实性数据、飞行手册补充），“The AML-STC is not meant to be a blanket approval by allowing additional models without further substantiation.”<kb doc="AC_20-180.pdf" chunk_id="3705aad7-9fcf-4093-9520-acd528861605" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；
- 受影响区域的**认证基础与修正案水平须逐型号确定**，FMS 按 §21.5 逐个型号适用<kb doc="AC_20-180.pdf" chunk_id="3705aad7-9fcf-4093-9520-acd528861605" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；
- 若型号间安装差异导致相似性与基线数据无法建立，“AML-STC is not the proper method of approval”<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />；固定翼与旋翼机的天线罩、结构、系统集成差异正属于需要重新评估的情形。

### 3. 在 Part 23 内部还应考虑再细分

AC 20-180 建议 Part 23 内的 normal、utility、acrobatic、commuter 各类**分别**签发 AML-STC（因认证要求可能不同），并视改装类型（结构、动力装置、系统、航空电子等）与负责 ACO 协调确定<kb doc="AC_20-180.pdf" chunk_id="9259d265-e30d-414a-ad08-7f80edd1da54" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />。若连同类内的子类别都要按此谨慎拆分，跨 Part 23/27 合并更无从谈起。

### 4. 清单表格应呈现的结构（据附录 A 模板的列项）

Make、Model/Series、Certification basis/Amendment、TCDS 号、MDL/安装图、FMS、ICA、部件件号、型号特定注记、初始批准日与修订日——每一行对应一个型号及其自身认证基础，见 [[concept/aml-stc|AML-STC]] 与 [[entity/sa01157la|SA01157LA 示例]]。

> 注：本次检索范围内未见针对“多型号批准清单跨类别合并”的其他许可性条款；上述结论限于所采用的 AC 20-180 方法。

---

## 二、前视风切变指导的适用范围

### 1. 文件自身把“四类”与“前视风切变”分开表述

原文：“The guidance is applicable to … parts 23, 25, 27, and 29 aircraft. **For forward-looking windshear and/or turbulence detection capability, the guidance in this AC applies to parts 25 and 23 fixed-wing airplane installations.**”<kb doc="AC_20-182A.pdf" chunk_id="767b9d09-9f10-4d7c-aa91-d1153dbf38c6" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" />

即“四类”是全 AC 的一般适用范围（如 §5.2 显示颜色、§8.3 大气威胁感知告警、§9.1 气象/地面测绘飞行试验），而前视风切变被单独收窄为 **Part 23、Part 25 固定翼**。

### 2. 条款内部相互印证

| 条款 | 引用范围 |
|---|---|
| §9.1 气象与地面测绘雷达飞行试验 | 明确“parts 23, 25, 27, and 29”，并逐部分列出 AC 23-8、AC 25-7、AC 27-1、AC 29-2<kb doc="AC_20-182A.pdf" chunk_id="07ef1485-1cd9-4a11-b027-5460b7cebed0" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| §9.2 前视风切变 | 只引用 §9.1.1（AC 23-8）与 §9.1.2（AC 25-7），**未引用** §9.1.3（AC 27-1）与 §9.1.4（AC 29-2）<kb doc="AC_20-182A.pdf" chunk_id="4eab2d62-9985-4443-869e-c73da51c145d" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| §6.2.1 前视风切变告警与提示 | 「for **parts 23 and 25** aircraft」，引 §25.1322、AC 25.1322-1、AC 23.1311-1<kb doc="AC_20-182A.pdf" chunk_id="f0cdd104-5906-4bf2-905e-be003c5df91b" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |
| §5.2 显示颜色 | 「parts 23, 25, 27, and 29」，含 AC 27-1、AC 29-2<kb doc="AC_20-182A.pdf" chunk_id="e6347557-1760-4758-90d0-7a32fb315cda" kb_id="17a4fb08-2f1e-4107-b1e6-c203657a3e08" /> |

可见“覆盖四类”的表述集中在**通用**条款；一旦进入前视风切变专门章节（§6.2.1、§9.2），适用类别即收窄为 Part 23/25。

### 3. 设备层面统一，不等于安装