用于创建MongoDB实例

```shell
# 初始化单实例
python main.py -i 192.168.1.151:30000#3/20
# 初始化一个replicate set成员
python main.py -r 192.168.1.151:30000#3/20#primary#90#replSetName
# 初始化一个config server成员
python main.py -c 192.168.1.151:30000#3/20#primary#90
# 初始化一个mongos服务
python main.py -s 192.168.1.151:30000  #（mongos的位置需要提前统一规范）
# 将节点加入复制集中
python main.py -ar 192.168.1.151:30000#192.168.1.152:30000 # 前面的是操作节点，后面是加入的节点
# 将数据成员加到mongos中
python main.py -as 192.168.1.151:30000
```
