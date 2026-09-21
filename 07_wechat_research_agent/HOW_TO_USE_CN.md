# Personal AI Research Agents 微信公众号科研线索 Agent 使用说明

作者：Steven Yuandong Yue  
Title：AI Research Tool Builder

## 1. 这个 Agent 是什么

这是一个独立于 `06_web_literature_agent` 的新 Agent。

它专门处理微信公众号文章，不直接做 Crossref / arXiv 那种学术数据库全网检索。

目标是：

```text
公众号文章搜索入口
        ↓
找到公众号文章
        ↓
粘贴文章链接或正文
        ↓
提取 DOI / 论文标题线索
        ↓
用 Crossref 验证正式论文
        ↓
导出 Excel
```

## 2. 为什么要单独做

公众号文章经常是科研线索来源，比如会介绍最新论文、综述、材料方向、催化剂方向。

但公众号不是正式论文数据库，也没有稳定公开 API。

所以这个 Agent 和 Literature Agent 分开：

- Literature Agent：正式论文数据库搜索
- WeChat Research Agent：公众号文章线索发现

## 3. 如何启动

运行：

```powershell
D:\Projects_New Energy\Personal_AI_Research_Agents\07_wechat_research_agent\start_wechat_research_agent.bat
```

然后打开：

```text
http://localhost:8502
```

## 4. 怎么用

### 第一步：输入搜索关键词

例如：

```text
PEM catalyst HEO
高熵氧化物 催化剂
氢能源 催化剂
HER OER catalyst
```

系统会生成三个外部搜索入口：

- 搜狗微信文章搜索
- Bing 限定微信公众号文章搜索
- Google 限定微信公众号文章搜索

点击 `Open Search` 打开搜索结果。

### 第二步：找到公众号文章

打开搜索结果后，找到相关公众号文章。

复制文章链接，例如：

```text
https://mp.weixin.qq.com/s/xxxx
```

### 第三步：粘贴链接或正文

回到 Agent：

- 如果有链接，粘贴到 `公众号文章链接`
- 如果链接读取失败，把正文复制到 `公众号文章正文`

正文方式更稳定。

### 第四步：提取论文线索

点击：

```text
提取论文线索 / Extract Paper Clues
```

系统会尝试识别：

- DOI candidate
- Title candidate
- Crossref verified paper
- 年份
- DOI
- 期刊
- 论文 URL
- 原公众号链接

### 第五步：导出 Excel

结果可以下载为 Excel，方便放入项目资料或发给团队筛选。

## 5. 当前限制

- 不直接批量爬微信公众号。
- 不读取个人微信聊天记录。
- 不破解微信本地数据库。
- 微信链接可能无法自动读取。
- 公众号文章只是线索，不是正式论文来源。
- Crossref 验证结果需要人工复核。
- 还没有和正式 Literature Agent 自动合并。

## 6. 和 ChatGPT-on-WeChat 文章的关系

你提供的文章讲的是另一个方向：

```text
把微信公众号后台接入 ChatGPT-on-WeChat / AI bot
```

那属于公众号服务端对接，需要：

- 公众号管理员权限
- AppID / AppSecret
- Token
- EncodingAESKey
- 服务器和域名
- HTTPS
- API key 安全配置

这可以作为未来版本，但不是当前第一版。

当前第一版先做安全、轻量的：

```text
公众号搜索入口 + 链接/正文解析 + 论文线索提取
```

## 7. 下一版建议

- 和 `06_web_literature_agent` 合并数据导出格式
- 把公众号提取出来的论文一键加入 Literature Agent 搜索
- 增加 Qwen Plus 总结公众号文章
- 保存公众号文章历史
- 增加人工反馈标签
- 如果公司确实有公众号管理员权限，再研究 ChatGPT-on-WeChat 服务端对接


