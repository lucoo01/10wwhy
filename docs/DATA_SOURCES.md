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
