#!/bin/bash
# Image-Segmentation 同步脚本
# 用于本地与 GitHub 仓库的同步

set -e

echo "🔄 Image-Segmentation 同步脚本"
echo "================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 1. 检查当前状态
echo "📊 步骤 1: 检查当前状态"
echo "--------------------------------"
git status --short
if [ $? -ne 0 ]; then
    echo "❌ Git 状态检查失败"
    exit 1
fi
echo "✅ 状态检查完成"
echo ""

# 2. 获取远程最新代码
echo "📥 步骤 2: 获取远程最新代码"
echo "--------------------------------"
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" == "$REMOTE" ]; then
    echo "✅ 本地与远程已同步"
else
    echo "⚠️  本地与远程不同步"
    echo "   本地：$LOCAL"
    echo "   远程：$REMOTE"
fi
echo ""

# 3. 拉取远程更新（如果有）
echo "📥 步骤 3: 拉取远程更新"
echo "--------------------------------"
git pull origin main --no-edit
echo "✅ 拉取完成"
echo ""

# 4. 检查未跟踪的文件
echo "📁 步骤 4: 检查未跟踪的文件"
echo "--------------------------------"
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED" ]; then
    echo "发现未跟踪的文件:"
    echo "$UNTRACKED"
    echo ""
    read -p "是否添加到暂存区？(y/n): " answer
    if [ "$answer" == "y" ]; then
        git add .
        echo "✅ 文件已添加到暂存区"
    fi
else
    echo "✅ 没有未跟踪的文件"
fi
echo ""

# 5. 检查暂存区的修改
echo "📝 步骤 5: 检查暂存区的修改"
echo "--------------------------------"
STAGED=$(git diff --cached --name-only)
if [ -n "$STAGED" ]; then
    echo "暂存区有以下修改:"
    echo "$STAGED"
    echo ""
    read -p "是否提交？(y/n): " answer
    if [ "$answer" == "y" ]; then
        read -p "输入提交信息: " message
        git commit -m "$message"
        echo "✅ 提交完成"
    fi
else
    echo "✅ 暂存区没有修改"
fi
echo ""

# 6. 推送到 GitHub
echo "📤 步骤 6: 推送到 GitHub"
echo "--------------------------------"
BEHIND=$(git rev-list --count HEAD..origin/main)
AHEAD=$(git rev-list --count origin/main..HEAD)

if [ "$AHEAD" -gt 0 ]; then
    echo "📤 本地领先远程 $AHEAD 个提交，准备推送..."
    git push origin main
    echo "✅ 推送成功"
elif [ "$BEHIND" -gt 0 ]; then
    echo "⚠️  本地落后远程 $BEHIND 个提交，请先拉取"
    git pull origin main
else
    echo "✅ 本地与远程完全同步，无需推送"
fi
echo ""

# 7. 最终状态
echo "📊 步骤 7: 最终状态"
echo "--------------------------------"
git status
echo ""
echo "📝 最近提交:"
git log --oneline -5
echo ""
echo "================================"
echo "✅ 同步完成！"
echo ""
