## 结论

三方面的理由各自对应不同义务，需分别判断；三项都不能支持“只留最新版、删旧图旧报告”：

| 问题 | 公司做法的性质 | 主要依据 |
|---|---|---|
| 追溯 | 破坏 AML 逐型号可追溯性与历史链 | AC 20-180 §11、附录 A |
| FAA 数据保管 | 销毁 TC 的永久记录，违反代保管义务 | AC 20-179 ¶4.b、¶6.a |
| 商业秘密 | 商业秘密只要求“标识＋保护”，不构成销毁理由 | AC 20-179 ¶5、¶6.a(2)、¶6.b |

## 一、追溯：删掉旧安装图与旧试验报告，等于切断“历史链”

**要求是逐型号保持可追溯性和共性。** AC 20-180 第 11 段：构型控制是跟踪对 AML 所做全部更改的方法，更改可能是增加型号或修订现有型号；**无论哪种，要求都是为每个型号维护相关数据，使型号之间的可追溯性和共性能够被验证**。<kb doc="AC_20-180.pdf" chunk_id="e8a224f1-58b5-475a-b9dd-11b024302e6c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**被删的正是构型控制的登记字段。** 附录 A 表格要求逐型号填写：MDL／安装图**及其修订号**（一般以安装图或 MDL 之一做构型控制，替换文件必须能达可追溯性目的）；<kb doc="AC_20-180.pdf" chunk_id="6d2558b1-93de-41cd-982c-54981e3462ab" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> FMS 的修订级别与**批准日期**（同一 AFM 可能对每个型号有多个补充章节）；<kb doc="AC_20-180.pdf" chunk_id="f3cf3ed9-23bc-4013-9595-0aff4cfb5b40" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> ICA 的文件号、修订级别与日期；<kb doc="AC_20-180.pdf" chunk_id="7db59726-1004-40bb-b5c2-df861c615f5b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 以及受改装影响区域所适用的**认证基础与修正案水平**。<kb doc="AC_20-180.pdf" chunk_id="e031137b-50c9-4eec-bb6c-60e03281a5bf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**只留最新总说明书会丢失两样东西**：一是各型号在不同时间、依据不同修订状态获批的事实；二是旧试验报告所承载的符合性证据链——AC 20-179 明确把“**试验计划**”“**试验与分析报告，含公司与 FAA 的符合性检查记录**”（对应 14 CFR 21.21、21.33、21.35）列入可代 FAA 保留的数据。<kb doc="AC_20-179.pdf" chunk_id="552d7069-bb42-49bf-9375-d1dadb4dc476" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**一旦链条断了，重建代价很高。** AC 20-180：各型号共享基线数据，基线数据在整个型号清单中持续适用于每个型号；**一旦通过拆分型号打破这一链条，就需要大量工作重新建立该特定型号的历史（如符合性数据、适航指令、服务通告、问题纸和豁免）**。<kb doc="AC_20-180.pdf" chunk_id="fea2e811-ad09-4b5b-a900-85e1d3868356" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

**Wiki 不能替代记录。** 保留范围明确要求“**经批准飞行手册的原件及所有修订**”（21.5）以及“**所有被接受手册（如 ICA）的原件**”（21.50）。<kb doc="AC_20-179.pdf" chunk_id="552d7069-bb42-49bf-9375-d1dadb4dc476" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="60df998a-9a99-489e-a190-cd9e20949993" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> Wiki 是由源文件生成的派生摘要，没有修订号、批准日期与符合性检查记录，只能作为索引，不能作为保留对象或符合性证据。

## 二、FAA 数据保管：这是“TC 的永久记录，不得销毁”

- **适用范围包含 STC**：AC 20-179 的“TC”涵盖原始 TC、修订 TC、**STC 或修订 STC**，也适用于 PMA 申请人/持有人（不适用于 ODA 持有人，此类持有人须确保其 ODA 程序手册的数据保留章节与要求一致）。<kb doc="AC_20-179.pdf" chunk_id="b9a43478-dcd6-4559-95fa-d4e750e0abd6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="4aca6d6f-8cf8-436d-9505-050765f229fe" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **永久记录属性**：数据保留协议项下的数据是产品的**TC 永久记录，不得销毁**，须按现行 FAA 记录管理时间表保留。<kb doc="AC_20-179.pdf" chunk_id="e5985e4f-2a04-4d64-a44a-b6362bf9bd67" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **数据归属**：若你签订保留协议，代 FAA 保留的数据**是 FAA 的数据，不是公司自己的数据**，须在 FAA 要求时提供；FAA 可将其用于生产检查、设计代表技术监督、设计审查、持续运行安全监督等任何官方目的。<kb doc="AC_20-179.pdf" chunk_id="164414b0-36ca-4220-84f4-5083d93bcffa" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="92319a31-6f5f-4789-a324-06be14257848" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **随时可查**：协议须含一项声明——所有记录可在 FAA 或 NTSB 要求时随时提供检查（见 14 CFR 21.49），并规定请求后数据可供审查的时间间隔。<kb doc="AC_20-179.pdf" chunk_id="9002a367-7502-49f5-b0b9-9af8f855e1ca" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="7cdc0a2e-8b2a-4b1c-ae08-7ec254331df6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **电子化可以，但必须可检索、可读**：公司须控制存储、维护与备份能力以保证可访问性，并以 FAA 可读取的格式提供数据；**历史数据须能检索，或转移到可检索的其它介质**；转移后须确保 FAA 能访问此前提交的全部数据与新数据。<kb doc="AC_20-179.pdf" chunk_id="b7154b31-ebe8-4d16-b61c-82e4237ea126" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="fc97ed20-f8a7-4049-96a4-e9649cf505cc" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **终止也须返还**：协议终止时所有记录须返还 FAA；在转移完成前 FAA 的访问权不终止。<kb doc="AC_20-179.pdf" chunk_id="7feda680-ceef-4a2d-a9c8-a73154e5e4ed" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="623aafa9-ca83-4bab-bf68-a7c642d34330" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

所以问题不在“数据仓库迁移”，而在**迁移后不可检索、不可读、只剩一个最新文件**。若要减少本地实体保管，可行路径是依协议移交/返还 FAA，或按 AC 21-48 的电子方式保留并保证可访问。

## 三、商业秘密：只支持“标识与保护”，不支持“删除”

- **协议要求的是标识**：最低条款第 2 项即“标明记录中你认为属于专有的部分”。<kb doc="AC_20-179.pdf" chunk_id="9002a367-7502-49f5-b0b9-9af8f855e1ca" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **FAA 有法定保护义务**：FAA 雇员有义务保护专有数据免遭未经授权发布，联邦雇员未经授权发布某些信息违反 18 U.S.C. §1905。<kb doc="AC_20-179.pdf" chunk_id="e97624f9-b713-4f85-8f05-104114f22e08" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **只有四种情形可对外发布**：所有权人书面同意；请求者持有所有权人签署的书面发布许可；有管辖权法院的命令或传票；请求者能援引法规、双边协议或上级书面命令。<kb doc="AC_20-179.pdf" chunk_id="b64a04f9-484e-48c1-8295-ff1f93f75272" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="42c955c6-51ea-44e3-ad8b-83e410cf3784" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="9fa7241a-8f19-4ca4-a81f-c595e6140680" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
- **证书终止后 IP 仍归公司**：TC 交还、撤销或终止后，DAH 仍保留其对基础设计与证实数据的知识产权；第 5.a、5.b 段要求向公众发布数据须取得 DAH 书面同意。<kb doc="AC_20-179.pdf" chunk_id="623aafa9-ca83-4bab-bf68-a7c642d34330" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="7dd8e1dd-9147-4af5-b360-de6d1936ffaf" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

商业秘密在法律上对应的是**受控访问、专有标识、发布前书面同意**三项机制，而不是“可以不留”。反过来，删除记录会让公司在 21.49 检查、持续适航问题与产品责任诉讼中无法自证符合性——对商业秘密是净损失。

## 四、建议的补救动作

1. **立即停止删除，从备份恢复**旧版安装图、旧试验报告及图 1 所列其它数据类型（图样与规范及其清单、使用限制、试验计划、报告、AFM 原件及所有修订、ICA 原件、服务通告）。<kb doc="AC_20-179.pdf" chunk_id="552d7069-bb42-49bf-9375-d1dadb4dc476" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="60df998a-9a99-489e-a190-cd9e20949993" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
2. **核查是否签有数据保留协议**（PSP 或 MoA）。若有，删除即违约；若无，仍须满足 21.49 的可供检查要求。<kb doc="AC_20-179.pdf" chunk_id="9002a367-7502-49f5-b0b9-9af8f855e1ca" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="7cdc0a2e-8b2a-4b1c-ae08-7ec254331df6" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
3. **以 AML 表为索引重建清单**：逐型号登记 MDL/安装图修订号、FMS 修订级别与批准日期、ICA 文件号/修订/日期、P/N、型号专用注记、初始与修订批准日期。<kb doc="AC_20-180.pdf" chunk_id="6d2558b1-93de-41cd-982c-54981e3462ab" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="f3cf3ed9-23bc-4013-9595-0aff4cfb5b40" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-180.pdf" chunk_id="7db59726-1004-40bb-b5c2-df861c615f5b" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
4. **迁移验证**：确认历史数据可检索、格式 FAA 可读，新旧数据均可访问。<kb doc="AC_20-179.pdf" chunk_id="b7154b31-ebe8-4d16-b61c-82e4237ea126" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="fc97ed20-f8a7-4049-96a4-e9649cf505cc" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
5. **标注专有部分并做访问控制**，对外发布前取得书面同意。<kb doc="AC_20-179.pdf" chunk_id="9002a367-7502-49f5-b0b9-9af8f855e1ca" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="b64a04f9-484e-48c1-8295-ff1f93f75272" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />
6. **把 Wiki 定位为索引**，引用时回指原始文件，不作为保留或符合性证据。

**一句话：** “Wiki 已总结”解决检索效率，不解决记录义务；“商业秘密”解决访问控制，不解决保存期限。对多型号批准而言，删旧安装图与旧试验报告会同时切断逐型号追溯链、违反 TC 永久记录的保管义务，并使专有数据失去受保护的法律基础。<kb doc="AC_20-180.pdf" chunk_id="e8a224f1-58b5-475a-b9dd-11b024302e6c" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="e5985e4f-2a04-4d64-a44a-b6362bf9bd67" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /><kb doc="AC_20-179.pdf" chunk_id="e97624f9-b713-4f85-8f05-104114f22e08" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" />

> AC 20-179／20-180 均为咨询通告、非强制法规；<kb doc="AC_20-179.pdf" chunk_id="76f1ba98-f21e-4072-8d5e-219a2ea30523" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 但其列明的记录类型分别对应 14 CFR 21.5、21.21、21.31、21.33、21.41、21.49、21.50 等强制条款，<kb doc="AC_20-179.pdf" chunk_id="552d7069-bb42-49bf-9375-d1dadb4dc476" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 且一旦声明按其方法取证，须完整遵循。<kb doc="AC_20-179.pdf" chunk_id="76f1ba98-f21e-4072-8d5e-219a2ea30523" kb_id="ec1ebcc3-6d50-46d6-8a64-5444dce0962e" /> 延伸阅读：[[concept/certification-data-retention-agreement|认证数据保留协议]]、[[concept/type-design-and-substantiation-data-retention-scope|型号设计与证实数据保留范围]]、[[concept/proprietary-data-protection-and-intellectual-property|专有数据保护与知识产权]]、[[concept/aml-stc-configuration-control-and-type-design-change|AML-STC构型控制与型号设计更改管理]]。