# 数据来源说明

## docs/百科问答/ 目录

本目录下的 100 个分片文件（`百科问答-001.md` ~ `百科问答-100.md`）共收录 **100,000 条**中文"为什么 / 如何"类开放问答问题，**仅含问题，不含答案**。

### 数据来源

- **数据集**：[I_Wonder_Why-Chinese](https://huggingface.co/datasets/Mxode/I_Wonder_Why-Chinese)（"十万个为什么 - 中文百科开放问答数据集"）
- **作者**：Max Zhang（GitHub: [Mxoder](https://github.com/Mxoder) · Hugging Face: [Mxode](https://huggingface.co/Mxode)）
- **索引仓库**：[Maxs-Awesome-Datasets](https://github.com/Mxoder/Maxs-Awesome-Datasets)
- **许可证**：[CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)（署名-相同方式共享 4.0 国际）

### 数据处理

从原数据集 `general` 子集（1,224,139 条）中：

1. 抽取 `prompt` 字段（问题），丢弃 `response`（答案）；
2. 精确去重 + 质量过滤（长度 5–120 字、含疑问标记）；
3. 随机抽样 100,000 条。

处理脚本见 `_pipeline/extract.py`。

### 许可证约束（重要）

本目录的问题内容派生自 CC-BY-SA-4.0 协议数据集，使用时须：

- **署名**：注明作者 Max Zhang 及数据集来源；
- **相同方式共享**：对本部分内容的演绎作品，须以 CC-BY-SA-4.0 或兼容协议开源。

如需闭源或商用，请另行评估或寻求其他数据来源。

### 引用

```bibtex
@misc{zhang2025maxawesomedatasets,
  title={Max's Awesome Datasets},
  author={Max Zhang},
  year={2025},
  howpublished={\url{https://github.com/Mxoder/Maxs-Awesome-Datasets}},
}
```

## 领域分类标签

为便于按主题检索，百科问答已对每条问题附加一个**中等粒度领域标签**，以 `[类目]` 形式置于 md 文件中每行问题编号之后，例如：

```
1. [生命科学] 蚕蛹为什么要在化蛹前会不吃不动？
2. [化学] 为什么某些古老的书籍和字画材料能够长时间保存而不褪色？
```

### 类目清单（12 类）

| 代号 | 类目 | 覆盖范围 |
|---|---|---|
| astro | 天文宇宙 | 恒星、行星、黑洞、宇宙学、日食月食 |
| physics | 物理学 | 力、光、电、磁、热、声、量子 |
| chem | 化学 | 物质性质、反应、溶解、元素 |
| bio | 生命科学 | 动物、植物、微生物、进化、生态行为 |
| human | 人体与健康 | 生理、疾病、感官、遗传 |
| earth | 地球与环境 | 地理、地质、气象、海洋、气候 |
| tech | 技术与工程 | 机械、电子、计算机、建筑、交通 |
| math | 数学与信息 | 数、逻辑、编码、统计 |
| hist | 历史与人文 | 历史、考古、语言、文化、艺术 |
| psycho | 心理与社会 | 心理、行为、社会现象 |
| daily | 日常生活 | 食物、家居、生活常识 |
| other | 其他 | 跨领域或难以归入上述类目 |

### 说明

- 标签由 LLM 自动生成（处理脚本 `_pipeline/classify.py`），**可能存在少量误分**；如需精确归类，建议人工复核关键应用场景。
- 标签数据存放于 `_pipeline/prompts_100k_classified.jsonl`（每行 `{"i": 行号, "prompt": ..., "category": 代号}`），通过 `_pipeline/import.py` 渲染进 md。
