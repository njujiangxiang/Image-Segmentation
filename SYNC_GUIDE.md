# 🔄 Image-Segmentation 同步指南

本指南帮助你解决本地 Git 与 GitHub 仓库同步的问题。

---

## ✅ 当前状态

**本地仓库**: `/Users/xiaoyu/.openclaw/workspace/Image-Segmentation/`  
**GitHub 仓库**: `https://github.com/njujiangxiang/Image-Segmentation`  
**当前分支**: `main`  
**同步状态**: ✅ 已同步

---

## 🚀 快速同步

### 方式一：使用同步脚本（推荐）

```bash
cd /Users/xiaoyu/.openclaw/workspace/Image-Segmentation
./sync.sh
```

脚本会自动：
1. 检查当前状态
2. 获取远程最新代码
3. 拉取远程更新
4. 检查未跟踪的文件
5. 检查暂存区的修改
6. 推送到 GitHub
7. 显示最终状态

---

### 方式二：手动命令

#### 1. 检查状态

```bash
cd /Users/xiaoyu/.openclaw/workspace/Image-Segmentation
git status
```

#### 2. 拉取远程更新

```bash
git pull origin main
```

#### 3. 添加修改的文件

```bash
# 添加所有修改
git add .

# 或添加指定文件
git add path/to/file.py
```

#### 4. 提交修改

```bash
git commit -m "描述你的修改"
```

#### 5. 推送到 GitHub

```bash
git push origin main
```

---

## ❌ 常见问题及解决方案

### 问题 1: 无法提交（nothing to commit）

**症状**:
```
nothing to commit, working tree clean
```

**原因**: 没有修改的文件或文件已被 .gitignore 忽略

**解决方案**:
```bash
# 1. 检查是否有未跟踪的文件
git status --untracked-files=all

# 2. 查看 .gitignore 规则
cat .gitignore

# 3. 如果要强制添加被忽略的文件
git add -f path/to/ignored_file.py
```

---

### 问题 2: 推送失败（远程有更新）

**症状**:
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs to ...
```

**原因**: 远程仓库有本地没有的提交

**解决方案**:
```bash
# 1. 先拉取远程更新
git pull origin main

# 2. 解决可能的冲突（如果有）

# 3. 再次推送
git push origin main
```

---

### 问题 3: 本地和远程不一致

**症状**: 本地提交和远程提交历史不同

**解决方案**:

#### 方案 A: 保留本地修改（合并）
```bash
git pull origin main
# 解决冲突后
git commit
git push origin main
```

#### 方案 B: 强制同步（覆盖远程）
⚠️ **谨慎使用**，会覆盖远程历史

```bash
# 确保本地是正确的
git log --oneline -5

# 强制推送
git push -f origin main
```

---

### 问题 4: 文件被 .gitignore 忽略

**症状**: 文件修改了但 `git status` 看不到

**解决方案**:

```bash
# 1. 查看哪些文件被忽略
git status --ignored

# 2. 查看 .gitignore 规则
cat .gitignore

# 3. 如果要跟踪被忽略的文件
git add -f path/to/file

# 4. 或修改 .gitignore 规则
```

**当前 .gitignore 忽略的文件**:
- `__pycache__/` - Python 缓存
- `*.pyc` - Python 编译文件
- `.vscode/`, `.claude/` - IDE 配置
- `.DS_Store` - macOS 系统文件
- `*.jpg`, `*.png`, `*.jpeg` - 图片文件（测试数据）
- `*.pth`, `*.pt`, `*.onnx` - 模型文件

---

### 问题 5: Git 用户配置错误

**症状**: 提交时显示错误的用户名或邮箱

**解决方案**:

```bash
# 1. 查看当前配置
git config user.name
git config user.email

# 2. 修改配置
git config user.name "小雨爸爸"
git config user.email "nju.jiangxiang@gmail.com"

# 3. 验证配置
git config --list | grep user
```

---

## 📊 常用命令速查

### 状态检查
```bash
git status                    # 查看状态
git status --short           # 简洁模式
git log --oneline -5         # 最近 5 次提交
git remote -v                # 远程仓库
git branch -a                # 所有分支
```

### 同步操作
```bash
git fetch origin             # 获取远程更新
git pull origin main         # 拉取并合并
git push origin main         # 推送到远程
```

### 添加和提交
```bash
git add .                    # 添加所有修改
git add path/to/file         # 添加指定文件
git commit -m "消息"         # 提交
git commit --amend           # 修改上次提交
```

### 查看差异
```bash
git diff                     # 工作区与暂存区差异
git diff HEAD                # 工作区与最新提交差异
git diff --cached            # 暂存区与最新提交差异
```

### 撤销操作
```bash
git reset HEAD file          # 撤销暂存
git checkout -- file         # 撤销工作区修改
git reset --hard HEAD        # 重置所有修改（危险！）
```

---

## 🔧 配置优化

### 全局 Git 配置（一次性设置）

```bash
# 用户信息
git config --global user.name "小雨爸爸"
git config --global user.email "nju.jiangxiang@gmail.com"

# 默认编辑器
git config --global core.editor "vim"

# 自动处理换行符
git config --global core.autocrlf input

# 启用彩色输出
git config --global color.ui true

# 默认推送行为
git config --global push.default simple
```

### 查看配置

```bash
# 查看所有配置
git config --list

# 查看全局配置
git config --global --list

# 查看本地配置
git config --local --list
```

---

## 📝 最佳实践

### 1. 提交前检查

```bash
# 提交前总是先检查状态
git status

# 查看修改内容
git diff

# 确保与远程同步
git pull origin main
```

### 2. 提交信息规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试相关
chore: 构建工具/依赖等
```

**示例**:
```bash
git commit -m "feat: 添加逆光检测功能"
git commit -m "fix: 修复直方图分析边界问题"
git commit -m "docs: 更新 README 使用说明"
```

### 3. 频繁同步

- **每天开始工作前**: `git pull`
- **完成一个功能后**: `git push`
- **长时间工作期间**: 每 1-2 小时 `git pull` 一次

### 4. 小步提交

- 每个提交只做一件事
- 提交信息清晰明确
- 便于回滚和审查

---

## 🆘 获取帮助

### Git 内置帮助

```bash
git help          # 总帮助
git help <command>  # 命令帮助，如：git help push
git <command> --help
```

### 检查同步状态

```bash
cd /Users/xiaoyu/.openclaw/workspace/Image-Segmentation

# 运行同步脚本
./sync.sh

# 或手动检查
git status
git log --oneline -5
git remote -v
```

---

## 📞 联系支持

如有问题，请检查：
1. 网络连接是否正常
2. GitHub 账号是否有访问权限
3. 本地 Git 配置是否正确

**仓库地址**: https://github.com/njujiangxiang/Image-Segmentation

---

**最后更新**: 2026 年 3 月 18 日
