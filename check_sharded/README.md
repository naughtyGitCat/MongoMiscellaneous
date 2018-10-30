## 设计目的
检查集群中哪些库没有启用分片 \
检查集群中启用分片库中的哪些集合没有分片

## 思路
```javascript
// 连接到mongos
// 切换到config库
use config;
// 检查集群中哪些库没有启用分片
p = db.databases.find({"partitioned" : true})
// 获取所有已经分片的集合
x = db.collections.find({"dropped" :{"$ne":true} })

// 遍历所有已经启用分片的库中所有的集合名称

```
