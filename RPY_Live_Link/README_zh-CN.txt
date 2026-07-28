RPY Live Link for Abaqus/CAE 2021
=================================

用途
----
选择一个 .rpy 或 .py 文件后，插件会通过 Abaqus GUI 主事件循环监控它
的保存操作。每次文件保存完成并稳定后，脚本会在 Abaqus 主内核命令
路径中重新执行，模型随之更新。

安装
----
将整个 RPY_Live_Link 文件夹复制到：

    C:\Users\ASDF\abaqus_plugins\

然后重新启动 Abaqus/CAE。

使用
----
1. 打开 Abaqus/CAE。
2. 选择 Plug-ins -> RPY Live Link -> Configure / Start...
3. Browse 选择需要监控的 .rpy 或 .py 文件。
4. 点击 Open in Notepad 可用记事本打开。
5. 点击 Apply 或 OK 启动监听。
6. 在记事本修改参数并按 Ctrl+S，模型会自动更新。
7. 可通过 Plug-ins -> RPY Live Link -> Status 查看状态。
8. 可通过 Plug-ins -> RPY Live Link -> Stop 停止监听。

注意
----
* 每次重新启动 Abaqus/CAE 后，需要重新启动一次监听。
* 监听文件拥有当前 Abaqus 会话的完整脚本权限。
* 如果脚本采用“删除零件并重建”的方式，旧零件的网格、截面、载荷和
  边界条件可能丢失。复杂模型建议把完整重建流程写入脚本。
* 完整自动生成的 abaqus.rpy 可能包含界面初始化操作。为了稳定参数化，
  建议监控只包含建模命令的独立 .rpy/.py 文件。
* 执行日志与被监控文件保存在同一目录，文件名为：
  <原文件名>.rpy_live_link.log

版本
----
1.1.0：改用 GUI 定时器 + 主内核执行，修复 Abaqus/CAE 2021 中后台
线程可能阻塞、状态为 ON 但执行次数始终为 0 的问题。
