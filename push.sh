#!/bin/bash
# 这个脚本是在开发者本地工作站使用的

pid_ssh_agent=$(ps -ef | grep ssh-agent | grep -Po '^\w+\s+\K\d+')
if [ -n "$pid_ssh_agent" ]; then
	kill -9 "$pid_ssh_agent"
fi

ps -ef | grep ssh-agent | grep -Po '^\w+\s+\K\d+' | awk '{if(NR>1)print $0}' | while read line
do
	kill -9 "$line" && echo "Kill ssh agent(pid=$line)."  # 杀死已存在的 SSH Agent 进程
done
if [ -z "$(ps -ef | grep ssh-agent | grep -Po '^\w+\s+\K\d+')" ]; then
	eval $(ssh-agent) > /dev/null  # 如果一个 SSH Agent 都没有，就创建一个
fi

# 准备 SSH 密匙
ssh-add
if [ $? -ne 0 ]; then
	echo "[ERROR] Fail to start ssh agent deamon or add ssh key!" 1>&2
	exit 1
fi

# 在本地重命名 texlive 输出的 PDF 文件
SOURCE_FILE="math.pdf"
OUTPUT_FILE="数学笔记.pdf"
if [[ $(stat --printf="%s" $SOURCE_FILE) -ge $(stat --printf="%s" $OUTPUT_FILE) ]]; then
	cp "$SOURCE_FILE" "$OUTPUT_FILE" &>/dev/null && echo "[INFO] 已生成最新版'数学笔记.pdf'文件." || echo "[ERROR] 生成最新版'数学笔记.pdf'失败！"
fi

read -p "是否向 Github 上传 PDF 文件？(Y/n) " do_upload_pdf_file

# 向 Github 推送发行版 PDF 文件
export REPO="KaiserKatze/mathematical-notes"  # Github 仓库
export RELEASE_TAG=${RELEASE_TAG:-$(date +'%Y%m%d%H%M%S')-$(git log --format=%h -1)}  # 自动生成 git 标签
case $do_upload_pdf_file in
	[Yy]* )
		git tag $RELEASE_TAG  # 打标签
	;;
esac

# 开始推送
for remote in $(git remote); do
	echo "[INFO] Start pushing to '$(git remote get-url $remote)' ..."
	git push -f $remote && git push -f --tags $remote ||\
		echo "[ERROR] Fail git push $remote!" 1>&2
done

case $do_upload_pdf_file in
	[Yy]* )
		git tag -d $RELEASE_TAG  # 删除标签
		export RELEASE_TITLE="Release $RELEASE_TAG"
		export RELEASE_NOTES="Daily update"
		cat github-token.ignore | awk 'match($0,/^\w+/){print $1}' | gh auth login -p ssh --with-token &&\
			echo "[INFO] Login successfully" &&\
			gh release create "$RELEASE_TAG" "$OUTPUT_FILE#$OUTPUT_FILE" --latest \
				--title "$RELEASE_TITLE" \
				--notes "$RELEASE_NOTES" \
				-R "$REPO" &&\
			gh auth logout ||\
			echo "[ERROR] Fail to upload release $RELEASE_TAG!" 1>&2 && exit 1
	;;
esac
