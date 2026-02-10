# GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL 详细用法

下面给你一个从「给定坐标 -> 64 维 embedding」的完整流程。

## 1) 数据集是什么

- 数据集：`GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`
- 结果类型：`ee.ImageCollection`
- 每个年度影像通常有 `64` 个波段（即 64 维向量）
- 你的代码：

```python
jan_2023_climate = (
    ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL')
    .filterDate('2023-01', '2023-02')
    .first()
)
```

得到 `Image ... (64 bands)` 是正确的。因为这个产品是年度产品，按 1 月筛选后拿到该年度影像。

## 2) 推荐的筛选方式（按年度）

比起按 `2023-01` 到 `2023-02`，更建议直接按全年范围：

```python
image_2023 = (
    ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL')
    .filterDate('2023-01-01', '2024-01-01')
    .first()
)
```

## 3) 给定坐标提取 64 维 embedding

```python
import ee

ee.Initialize()

image = (
    ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL')
    .filterDate('2023-01-01', '2024-01-01')
    .first()
)

point = ee.Geometry.Point([116.39, 39.90])

feature = image.sample(
    region=point,
    scale=10,
    numPixels=1,
    geometries=False
).first()

band_names = image.bandNames().getInfo()      # 64 个波段名
properties = feature.toDictionary().getInfo() # 采样结果
embedding = [properties[b] for b in band_names]

print('维度:', len(embedding))
print('前 8 维:', embedding[:8])
```

## 4) 仓库内可直接运行的测试脚本

已新增：`examples/satellite_embedding_test.py`

运行方式：

```bash
python examples/satellite_embedding_test.py --lon 116.39 --lat 39.90 --year 2023
```

如果你有特定 GCP 项目：

```bash
python examples/satellite_embedding_test.py --lon 116.39 --lat 39.90 --year 2023 --project your-project-id
```

## 5) 常见问题

1. **`ee.Initialize()` 失败**
   - 先执行：`earthengine authenticate`
2. **返回空采样 (`No sample returned`)**
   - 检查坐标是否落在有效覆盖区域
   - 增大 `scale`（例如 30 或 100）
3. **维度不是 64？**
   - 先打印 `image.bandNames().size().getInfo()` 核实当前影像波段数量

## 6) 进阶：用于下游任务

拿到 64 维向量后，可用于：
- 聚类（KMeans/DBSCAN）
- 相似性检索（余弦相似度）
- 监督学习特征输入（分类/回归）

建议先做标准化（如 `StandardScaler`）再进入 ML 模型。
