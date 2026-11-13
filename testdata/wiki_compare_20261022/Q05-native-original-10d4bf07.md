先把“原数据”分成两类，否则容易把两套规则混在一起：

1. **按数据保留协议代 FAA 保管的记录**：这些是 FAA 数据，不是公司可以自由处分的普通资产。<kb doc="AC_20-179.pdf" chunk_id="164414b0-36ca-4220-84f4-5083d93bcffa" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
2. **公司自有的设计、软件、商业秘密和知识产权**：按商业合同、许可或转让安排处理；AC 20-179 不处理这部分，并明确 DAH 仍保留底层设计和证实数据的知识产权。<kb doc="AC_20-179.pdf" chunk_id="623aafa9-ca83-4bab-bf68-a7c642d34330" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="7dd8e1dd-9147-4af5-b360-de6d1936ffaf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

## 三件事的判断

### 1. 整体出售 AML-STC：可以

AC 20-180 第 10 节明确：设计批准持有人可以把 AML-STC **整体**转让给第三方，例如出售或变更所有权。<kb doc="AC_20-180.pdf" chunk_id="fea2e811-ad09-4b5b-a900-85e1d3868356" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

关键词是“整体”。AML-STC 不能把某个型号拆出去，也不能拆成多个独立 STC；各型号共享的基线数据链不能断。<kb doc="AC_20-180.pdf" chunk_id="fc688be3-c4fb-41e2-80ba-4913f9d87c9e" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

### 2. 原数据保管协议自动转给买方：不可以

AC 20-179 ¶6.c 明确规定：**书面数据保留协议不可转让**。<kb doc="AC_20-179.pdf" chunk_id="7dd8e1dd-9147-4af5-b360-de6d1936ffaf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 该 AC 的“type certificate”包括 STC 和修订 STC，因此适用于本案的 AML-STC。<kb doc="AC_20-179.pdf" chunk_id="b9a43478-dcd6-4559-95fa-d4e750e0abd6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

协议是 FAA 与原持有人之间的安排，不是随 AML-STC 自动转移的合同权利。新持有人如希望继续代 FAA 保管数据，必须**自己与 FAA 谈判并签署新的数据保留协议**。<kb doc="AC_20-179.pdf" chunk_id="104203c5-beb6-485f-85f1-2a3e564e0bf5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

### 3. 买方只收购清单上的一个型号：不可以

这正是 AC 20-180 第 10 节禁止的“从 AML-STC 中拆分型号”。AC 明确：**拆分 AML-STC 中的型号，或把 AML-STC 拆成多个独立 STC，都是不允许的**。<kb doc="AC_20-180.pdf" chunk_id="fc688be3-c4fb-41e2-80ba-4913f9d87c9e" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

原因是 AML-STC 的各型号共享基线数据；一旦拆链，就要重新建立该型号的符合性数据、适航指令、服务通告、问题纸和豁免等历史，代价很大。<kb doc="AC_20-180.pdf" chunk_id="fea2e811-ad09-4b5b-a900-85e1d3868356" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

如果买方只要一个型号，通常只有两类合规路径：

- 买下**整张 AML-STC**，即使商业上只使用其中一个型号；
- 针对该型号**另行申请自己的 STC/型号设计更改批准**。

不能通过合同把其他型号从 AML-STC 中剥离，只把其中一个型号卖给买方。

## 原数据何时可以直接交新持有人

按 AC 20-179 ¶6.c，顺序是：

1. **新持有人与 FAA 签署自己的数据保留协议**；
2. **FAA 通知原持有人**：新持有人已经与 FAA 达成协议；
3. 原持有人将其设施内保留的**所有 FAA 记录转交新持有人**。<kb doc="AC_20-179.pdf" chunk_id="104203c5-beb6-485f-85f1-2a3e564e0bf5" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="714285c3-7d4d-48ae-8afc-d2f6dbf8dc2a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

如果新持有人不愿签署数据保留协议，则原持有人必须在**证书转移前**把所有 FAA 记录交回适当的 FAA 办公室，不能直接交给买方。<kb doc="AC_20-179.pdf" chunk_id="714285c3-7d4d-48ae-8afc-d2f6dbf8dc2a" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="d393f3ca-1e6e-4463-8c2d-ec094044d8a0" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

特殊情形：如果物理位置不变、记录保持完整、存储方法不变，并且新持有人与 FAA 已签署新的数据保留协议，则记录可以原地保留，不必先交回 FAA；但这仍然是“新协议”在起作用，不是原协议自动转让。<kb doc="AC_20-179.pdf" chunk_id="d393f3ca-1e6e-4463-8c2d-ec094044d8a0" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="fa7f2166-e6bf-40eb-94d2-5ee568306c38" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

## 结论

- **整体出售 AML-STC：可以**，但必须整体转让，不能拆分型号。
- **原数据保管协议自动转给买方：不可以**；新持有人必须与 FAA 另签协议。
- **买方只收购一个型号：不可以**；这属于禁止的拆分 AML-STC。
- **原数据直接交新持有人**：只在新持有人自己与 FAA 签署数据保留协议、且 FAA 通知原持有人之后；否则记录应交回 FAA，而不是交给买方。知识产权和商业秘密则另行按商业合同处理。<kb doc="AC_20-179.pdf" chunk_id="623aafa9-ca83-4bab-bf68-a7c642d34330" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="7dd8e1dd-9147-4af5-b360-de6d1936ffaf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />