# 行业研究 Skill

[English](README.md) | 简体中文

一个面向通用 AI 智能体的行业研究 skill。它支持行业全览、公司与产品定位、行业地图、生命周期判断、盈利能力与估值分析、竞争分析，以及结构化 Markdown 研究报告。

## 安装

使用开放智能体 skills CLI 从仓库安装该 skill：

```bash
npx skills add <github-owner>/industry-research-skill --skill industry-research
```

请将 `<github-owner>` 替换为托管本仓库的 GitHub 账户名或组织名。

## 仓库结构

```text
skills/industry-research/  可安装的 skill 及其支持文件
reports/                   仅限非商业使用的示例研究报告
```

## 许可证

### Skill

`skills/industry-research/` 下的文件采用 [Apache License 2.0](LICENSE) 授权。[中文译文](LICENSE.zh-CN.md)仅供理解和审阅。允许将该 skill 用于商业用途，包括使用该 skill 生成用于商业目的的报告。

skill 目录内也包含一份 Apache 许可证副本，以确保单独安装 skill 时许可证能够随之提供。

### 示例报告

`reports/` 下现有的报告单独采用 [知识共享署名-非商业性使用 4.0 国际许可协议](reports/LICENSE) 授权。[中文许可说明](reports/LICENSE.zh-CN.md)仅供理解和审阅。未经版权所有者另行许可，不得将这些报告用于商业用途。

### 生成的输出

通过正常使用该 skill 独立生成的报告，不会自动受到适用于 `reports/` 的 CC BY-NC 4.0 许可协议约束。在遵守适用法律、第三方权利、模型提供商条款，以及使用者自身专业或监管义务的前提下，使用者可以将独立生成的报告商业化。

复制 `reports/` 中现有报告，或者实质性派生自现有报告的输出，仍然受到该报告许可证的约束。

## 免责声明

本项目不提供投资建议或其他专业建议。使用者有责任核验生成内容，并对基于生成内容作出的所有决定、分发行为和商业化行为负责。完整免责声明请参阅 [DISCLAIMER.zh-CN.md](DISCLAIMER.zh-CN.md)。
