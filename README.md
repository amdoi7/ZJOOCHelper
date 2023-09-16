#在浙学 zjooc.cn 刷课全自动脚本
脱机实现 在浙学(www.zjooc.cn) 秒过章节内容和作业、测验、考试等。



使用方法：

新建一个python文件 安装以下操作 

```python
from zjooc import ZJOOC

if __name__ == '__main__':
	# 输入在浙学的账号密码
    user = ZJOOC(username='', pwd='')

    while True:
        commands = input("Enter your commands.\n")
        if commands == "exit":
            break
        elif commands == "help":
            print(
                """
                msg:
                0-测验 1-考试 2-作业
                3-info 4-course 5-score
                6-video 7-ans
                ex: 
                    msg 0
                    msg 6 course_id
                    msg 7 paperId course_id
                do:
                0-测验、考试、作业 1-video 2-all[not suggest!!!]
                ex：
                    do 0 paper_id course_id class_id
                    do 1 course_id
                    do 2 #FIX 谨慎使用！！！
                """.strip()
            )
        else:
            user.paser(commands)
```

