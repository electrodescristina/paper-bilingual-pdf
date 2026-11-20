# 计算机视觉术语与易错语义

这是核对用的起点，不是对所有论文强制套用的词典。以当前论文定义及用户认可的译法为准；专业语境变化时重新判断。

| 英文 | 常用译法 | 需要区分的含义 |
|---|---|---|
| keypoint / interest point | 关键点 / 兴趣点 | 作者可能区分候选点与最终关键点 |
| feature detector / descriptor | 特征检测器 / 特征描述子 | 找到哪里与如何表示该处，不互换 |
| distinctive / discriminative | 具有区分能力的 / 判别性强的 | distinctive 不宜机械译作“与众不同” |
| invariance / robustness | 不变性 / 稳健性（或鲁棒性） | 数学或构造上的不变性不等于经验抗扰能力 |
| repeatability / accuracy | 可重复性（重复检测率）/ 准确率 | 根据分母和评价协议确定，不统称准确率 |
| scale space / scale selection | 尺度空间 / 尺度选择 | scale 在这里不是量表或比例尺 |
| octave | 倍频程；尺度空间的一组 | SIFT 中为 σ 加倍的区间；首现解释定义，再统一简称 |
| Difference of Gaussians, DoG | 高斯差分 | 两个高斯尺度的差，不是一般高斯微分 |
| Laplacian of Gaussian, LoG | 高斯拉普拉斯 | 区分 ∇²G 与尺度归一化 σ²∇²G |
| extremum / maximum / minimum | 极值 / 极大值 / 极小值 | 局部极大值不应译成全局最大值 |
| localization / orientation assignment | 定位 / 方向分配 | 区分二维梯度方向与三维相机朝向 |
| viewpoint / pose | 视点 / 位姿 | 位姿通常包含位置和朝向，不只“姿态” |
| affine / similarity / projective transform | 仿射 / 相似 / 射影变换 | 自由度、保留性质不同，不互换 |
| gradient magnitude / orientation | 梯度幅值 / 梯度方向 | 不是梯度大小的两个同义说法 |
| principal curvature / Hessian | 主曲率 / Hessian（海森）矩阵 | 曲率比与空间二阶导数矩阵的关系需结合公式 |
| bin / histogram / vote | 分箱（区间）/ 直方图 / 投票 | 直方图区间与哈希桶按语境区分 |
| nearest / second-nearest neighbor | 最近邻 / 次近邻 | second-nearest 不是第二个算法找到的任意点 |
| inlier / outlier | 内点 / 离群点 | 不自动等同真实物体点 / 背景点 |
| clutter / occlusion | 杂乱背景或杂乱场景 / 遮挡 | clutter 不能在视觉场景中直接译成“杂波”而不看语境 |
| correspondence / matching | 对应关系 / 匹配 | 对应关系是结果或几何关联，匹配通常指过程 |
| epipolar geometry / fundamental matrix | 极线几何 / 基础矩阵 | 基础矩阵与本质矩阵不同 |
| aliasing / downsampling | 混叠 / 降采样 | 平滑、插值、重采样不是可互换步骤 |
| receptive field / complex cell | 感受野 / 复杂细胞 | 复杂细胞是视觉神经科学术语，不是“复杂的单元” |

## 需要结合公式的表达

- “within a factor of √2 of the correct scale”：正尺度之间通常指比值在 1/√2 到 √2 内，不能只写“小于 √2 倍”而丢失下界。
- “within 80% of the highest peak”在 SIFT 次峰选择中的意思需要结合算法：峰值达到最高峰的 80%，不是与最高峰相差 80%。
- “increase by a factor of four”通常表示变为四倍；遇到歧义结合实验量或公式核实，不自动写“增加四倍”。
- 原文将 variance 与角度单位混用时，不静默将它改称标准差；核实作者意图，必要时说明原文的用词与单位。
- 历史论文对处理速度或当时算法局限的陈述要保留其年代语境，不擅自改为今天的结论。
- PDF 中的 PDF 也可能是 probability density function（概率密度函数），不是文件格式；BBF 是 Best-Bin-First，不要凭缩写猜译。
