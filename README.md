## 功能简介
这是一个英语批量处理脚本，用来保存原先 Anki 的配置，而不是下述这个项目执行的结果

需要配合这位大佬的脚本使用（负责从不背单词批量导出单词）
https://github.com/ImQQiaoO/BubeiDanci_takeout

## 使用步骤
1. 将上文那个项目的执行结果 BBDC.csv，另存为 BBDC.txt **注意：必须是utf-8的格式 不然 Anki 导入不了** 
2. 从 Anki 导出想要保存的配置 保存为 Anki.txt
3. 根据控制台提示，将上诉两个文件的**完整路径**输入到控制台内

## 配置
    "use_default": false, # 下一次执行脚本是否使用上一次配置
    "bbdc_path": "C:\\Users\\17450\\Desktop\\BBDC.txt", # BBDC保存的文件路径
    "anki_path": "E:\\English\\Anki.txt", # Anki 导出的文件路径
    "output_path": "E:\\English\\BBDC_update\\result.txt", # 本项目执行结果所保存的路径
    "sb_do_replace": true, # 是否将 sb 转换成 somebody
    "sth_do_replace": true # 是否将 sth 转换成 something
## 测试
### 配置

    "use_default": false,
    "bbdc_path": "BBDC.txt",
    "anki_path": "Anki.txt",
    "output_path": "BBDC_updated.txt",
    "sb_do_replace": true,
    "sth_do_replace": false
### 测试文件
BBDC.txt:

    3831,argue for sth,-
    123,test,测速
    1321,admin,管理者
    1321,admin sb,管理者 sb
Anki.txt:

    argue for something	为…辩护；主张…
    test	测adw
    admin	管理者
    admin somebody	管理者 somebawdody
### 测试结果
BBDC_updated.txt

    3831,argue for sth,- //BBDC有 Anki没有 (sth 没有变为 something 所以不匹配)
    123,test,测adw // BBDC有 Anki有 Anki优先级高
    1321,admin,管理者 // BBDC 与 Anki 相同
    1321,admin somebody,管理者 somebawdody // BBDC有 Anki没有 但开始了sb转换 somebody 的开关 所以匹配上了


<hr>
小记: 

打包命令
1. pip install pyinstaller
2. pyinstaller --onefile --console update_bbdc.py

