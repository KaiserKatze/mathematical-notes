#!/bin/bash
# 这个脚本是在开发者本地工作站使用的

GITHUB_TOKEN="github-token.ignore"

get_ssh_agent_pid() {
	ps -ef | grep ssh-agent | grep -Po '^\w+\s+\K\d+'
}

git_push_all() {
	# 开始推送
	for remote in $(git remote); do
		echo "[INFO] Start pushing to '$(git remote get-url $remote)' ..."
		#if [[ -n $(git branch --no-color | grep dev) ]]; then
		#	# 推送（除master以外的）特别分支
		#	git push -f -u $remote dev
		#else
		#	git push $remote :dev
		#fi
		# git push -f $remote && git push -f --tags $remote ||\
		# 	echo "[ERROR] Fail git push $remote!" 1>&2
		git push -fq $remote &>/dev/null &
	done

	# case $do_upload_pdf_file in
	# 	[Yy]* )
	# 		git tag -d $RELEASE_TAG  # 删除标签
	# 		export RELEASE_TITLE="Release $RELEASE_TAG"
	# 		export RELEASE_NOTES="Daily update"
	# 		cat $GITHUB_TOKEN | awk 'match($0,/^\w+/){print $1}' | gh auth login -p ssh --with-token &&\
	# 			echo "[INFO] Login successfully" &&\
	# 			gh release create "$RELEASE_TAG" "$OUTPUT_FILE#$OUTPUT_FILE" --latest \
	# 				--title "$RELEASE_TITLE" \
	# 				--notes "$RELEASE_NOTES" \
	# 				-R "$REPO" &&\
	# 			gh auth logout ||\
	# 			echo "[ERROR] Fail to upload release $RELEASE_TAG!" 1>&2 && exit 1

	# 		for remote in $(git remote); do
	# 			echo "[INFO] Remove temporary tag from '$(git remote get-url $remote)' ..."
	# 			git push $remote ":$RELEASE_TAG"
	# 		done
	# 	;;
	# esac

	# # 向 Github 推送发行版 PDF 文件
	# export REPO="KaiserKatze/mathematical-notes"  # Github 仓库
	# export RELEASE_TAG=${RELEASE_TAG:-$(date +'%Y%m%d%H%M%S')-$(git log --format=%h -1)}  # 自动生成 git 标签
	# case $do_upload_pdf_file in
	# 	[Yy]* )
	# 		git tag $RELEASE_TAG  # 打标签
	# 	;;
	# esac
}

pid_ssh_agent=($(get_ssh_agent_pid))  # 获取 SSH Agent 进程的 PID，并保存到数组中
echo "[INFO] 正在运行的 SSH Agent 进程共计${#pid_ssh_agent[@]}个."
for ((i = 0; i < ${#pid_ssh_agent[@]}; i++)); do
    kill -9 "${pid_ssh_agent[i]}" && echo "杀死 SSH Agent 进程(pid=${pid_ssh_agent[i]})."  # 杀死已存在的 SSH Agent 进程
done
pid_ssh_agent=$(get_ssh_agent_pid)  # 重新获取 SSH Agent 进程的 PID
if [ -z "$pid_ssh_agent" ]; then  # 验证是否已经把 SSH Agent 进程清理干净
	echo "[INFO] 成功创建 SSH Agent："  # 如果一个 SSH Agent 都没有，就创建一个
	eval $(ssh-agent)
else
	echo "[ERROR] 清理已有 SSH Agent 失败！"
	exit 1  # 预料之外的错误
fi

# 准备 SSH 密匙
ssh-add
if [ $? -ne 0 ]; then
	echo "[ERROR] 没有启动 SSH Agent 后台程序，或者无法添加 SSH 密匙!" 1>&2
	exit 1
fi

# 在后台执行推送
git_push_all

# 数据统计
find . -type f \( -name '*.tex' -o -name '*.sty' \) |\
	xargs cat | wc -lc|\
	awk '{print "LaTeX 代码共计：" $1 " 行，" $2 " 字节."}'
find . -type f -name '*.tex' | wc -l |\
	awk '{print ".tex 文件共计：" $1 " 个."}'
find . -type f -name '*.sty' | wc -l |\
	awk '{print ".sty 文件共计：" $1 " 个."}'

# 在本地重命名 texlive 输出的 PDF 文件
SOURCE_FILE="math.pdf"
OUTPUT_FILE="数学笔记.pdf"
if [[ ! -f "$OUTPUT_FILE" || $(stat --printf="%s" $SOURCE_FILE) -ge $(( $(stat --printf="%s" $OUTPUT_FILE) * 8 / 10 )) ]]; then
	cp "$SOURCE_FILE" "$OUTPUT_FILE" &>/dev/null && echo "[INFO] 已生成最新版'数学笔记.pdf'文件." || echo "[ERROR] 生成最新版'数学笔记.pdf'失败！"
	# 如果没有 Github token 文件，那么不上传 PDF 文件
	if [[ ! -f "$GITHUB_TOKEN" ]]; then
		do_upload_pdf_file="n"
	else
		read -p "是否向 Github 上传 PDF 文件？(Y/n) " do_upload_pdf_file
	fi
else
	do_upload_pdf_file="n"
fi
