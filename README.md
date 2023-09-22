# PyWxDump
wechat数据库decrypted--适用于Linux版本微信，python版本3.7及以上测试通过

## 解密步骤
1、安装依赖：pip install -r requirements.txt

2、添加偏移:如果version_list.json没有你的微信版本，就需要自己添加，有则忽略

3、修改自己的路径：在[get_wx_decrypted_db.py](Program%2Fget_wx_decrypted_db.py)文件的`MSG_DIR`参数

4、执行脚本:python get_wx_info.py

5、如果要将整个工程变成一个单独的执行文件，则pip安装pyinstaller后，执行`pyinstaller --paths=Program/  --onefile Program/get_wx_info.py`


## 执行结果截图
![1.jpg](/img/1.jpg)


## 解密后查看

可以搭配[chatViewTools](https://github.com/Ormicron/chatViewTool)查看

执行步骤：
1、安装java环境和JavaFx环境，JavaFx版本需大于等于Java版本
可以在[这里](https://gluonhq.com/products/javafx/)下载JavaFx的SDK压缩包后解压

2、命令行执行`java --module-path /home/user/openjfx-17.0.8_linux-x64_bin-sdk/javafx-sdk-17.0.8/lib --add-modules javafx.controls,javafx.fxml -jar chatViewTool.jar` 


3、直接点击界面的“查看数据库”按钮，选择上面解密后的文件夹即可查看


## 查看界面截图
![2.jpg](/img/2.jpg)



参考链接：

[SharpWxDump](https://github.com/AdminTest0/SharpWxDump)

[PyWxDump](https://github.com/xaoyaoo/PyWxDump/tree/python1.0)

PS：上面用到的chatViewTool和JavaFx均放在utils文件夹中，自取