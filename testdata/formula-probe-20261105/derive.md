以下按 **4.2.1.2「桨叶在挥舞面内的弯曲振动」** 作答。原文在该节把式(4-2)明确称为“旋转桨叶的弯曲自由振动方程”；4.2.1.3 的摆振面内弯曲振动另列式(4-6)～(4-9)，本答复不将两组方程混用。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />

## 一、方程

挥舞面内桨叶的弯曲振动方程为：

\[
\left(EI_{YY}z^{\prime\prime}\right)^{\prime\prime}
-\left(Nz^{\prime}\right)^{\prime}
+m\ddot z=Tz
\tag{4-1}
\]

![式(4-1) 原文图像](http://localhost:8080/api/v1/ingestion/jobs/ee2a43e49c7d4aa49707a0d4f58cde18/assets/634f95daad6b70e1d608)

原文随后写道：“如果桨叶气动载荷 \(T_z=0\)，得到旋转桨叶的弯曲自由振动方程”：<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />

\[
\left(EI_{YY}z^{\prime\prime}\right)^{\prime\prime}
-\left(Nz^{\prime}\right)^{\prime}
+m\ddot z=0
\tag{4-2}
\]

![式(4-2) 原文图像](http://localhost:8080/api/v1/ingestion/jobs/ee2a43e49c7d4aa49707a0d4f58cde18/assets/fba81101932b230da894)

这里的“自由振动”是指**气动载荷项置零**，并不表示旋翼不旋转；离心力项 \(N\) 仍保留，因此式(4-2)是旋转桨叶的自由振动方程。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />

主要符号中，原文明确给出的有：

- \(N\)：\(r\) 剖面承受的离心力，
  \[
  N=\int_r^R \Omega^2 r m\,\mathrm{d}r
  \]
  \(R\) 为展向积分上限。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />
- \(m\)：单位长度质量。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />
- \(\Omega\)：旋翼转速；本节摘录未重复说明，本册后文式(4-80)的符号表注明“\(\Omega\)——旋翼转速”。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="92d619ef-caae-432d-aaac-73f13b221552" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />

需要说明的符号：

- \(EI_{YY}\)：原文在本节只以乘积组合 \(EI_{YY}\) 出现，检索内容未逐项解释 \(E\) 与 \(I_{YY}\) 的文字定义；这里保留原组合，不擅自把它展开为某一具体截面轴的惯性矩。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />
- 式(4-1)右端在原图中排作 \(Tz\)，但紧接正文写“桨叶气动载荷 \(T_z=0\)”。因此文字说明按正文记作 \(T_z\)；原图下标显示不够清楚，特此说明。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />
- 式(4-4)使用带上划线的 \(\overline{\omega}_\beta\)。检索文本的符号说明中出现“\(\omega_\beta^2=\omega_\beta^2\Omega^2\)”的重复，疑为上划线丢失或 OCR 误差；按式(4-4)与式(4-5)的对应关系，应理解为
  \[
  \omega_\beta^2=\overline{\omega}_\beta^2\Omega^2.
  \]
  其中 \(\omega_\beta\) 为挥舞圆频率，\(\overline{\omega}_\beta\) 为式(4-4)中的相应频率参数。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />

## 二、用分离变量法得到模态方程和频率方程

原文写道：“用分离变量法求解自由振动方程。令解为”<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />

\[
z=z(r)q(t)
\tag{4-3}
\]

![式(4-3) 原文图像](http://localhost:8080/api/v1/ingestion/jobs/ee2a43e49c7d4aa49707a0d4f58cde18/assets/ac46e27ee76cf051fbdc)

将式(4-3)代入式(4-2)。把原文“代入式(4-2)，得模态方程”这一步的代数过程展开写，就是：

\[
\left[\left(EI_{YY}z^{\prime\prime}(r)\right)^{\prime\prime}
-\left(Nz^{\prime}(r)\right)^{\prime}\right]q(t)
+mz(r)\ddot q(t)=0.
\]

移项并除以 \(mz(r)q(t)\)，得

\[
\frac{
\left(EI_{YY}z^{\prime\prime}(r)\right)^{\prime\prime}
-\left(Nz^{\prime}(r)\right)^{\prime}
}{
mz(r)
}
=
-\frac{\ddot q(t)}{q(t)}.
\]

左端只含 \(r\)，右端只含 \(t\)，故两端只能等于同一分离常数。取该常数为 \(\omega_\beta^2\)，则分别得到原文的模态方程：

\[
\left(EI_{YY}z^{\prime\prime}(r)\right)^{\prime\prime}
-\left(Nz^{\prime}(r)\right)^{\prime}
-\overline{\omega}_\beta^2\Omega^2 m z(r)=0
\tag{4-4}
\]

![式(4-4) 原文图像](http://localhost:8080/api/v1/ingestion/jobs/ee2a43e49c7d4aa49707a0d4f58cde18/assets/a12a56f9fc3518a4c2a9)

和频率方程：

\[
\ddot q(t)+\omega_\beta^2 q(t)=0
\tag{4-5}
\]

式(4-4)、(4-5)均见原文。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />

## 三、两个方程各起什么作用

- **式(4-4)是模态方程**：它是关于振型函数 \(z(r)\) 的常微分方程，含有待定的频率参数 \(\overline{\omega}_\beta\)。求解时必须同时使用原文给出的边界条件：铰接式桨叶在水平铰处的挠度、弯矩为零；无铰桨叶在根部挠度、转角为零，桨尖弯矩、切力为零。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" /><kb doc="公开+第19册(直升机设计).pdf" chunk_id="b4219fa3-6c82-4c21-8a77-99ad2062b2d8" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />
- **式(4-5)是原文所称的“频率方程”**：它是关于时间函数 \(q(t)\) 的方程，其解为以 \(\omega_\beta\) 为圆频率的简谐振动：
  \[
  q(t)=A\cos\omega_\beta t+B\sin\omega_\beta t.
  \]
  因而式(4-5)给出的是时间振动形式；具体的固有频率值仍需由式(4-4)与边界条件联立确定。<kb doc="公开+第19册(直升机设计).pdf" chunk_id="38dd598b-ad68-4201-a5c2-03b8e163f303" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />
- 原文还指出：“由模态方程可以证明，桨叶挥舞弯曲模态，满足正交条件。”<kb doc="公开+第19册(直升机设计).pdf" chunk_id="b4219fa3-6c82-4c21-8a77-99ad2062b2d8" kb_id="4f216fce-1f63-4392-8e90-85ac1b6c7e8a" />