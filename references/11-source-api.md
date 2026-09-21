# MyBatis-Flex 核心源码解析

本文件为索引页，详细内容拆分至以下子文件：

| 文件 | 主题 | 关键类 |
|------|------|--------|
| [11a-source-api.md](11a-source-api.md) | SQL 函数方法类 | `QueryMethods` |
| [11b-source-api.md](11b-source-api.md) | 查询包装器、链式查询 | `QueryWrapper`、`QueryWrapperAdapter`、`ChainQuery`、`MapperQueryChain`、`QueryChain` |
| [11c-source-api.md](11c-source-api.md) | 属性设置、更新包装器、链式更新/删除 | `PropertySetter`、`UpdateWrapper`、`UpdateChain` |
| [11d-source-api.md](11d-source-api.md) | 条件判断工具类 | `If` |

---

## 类继承关系

> 均已按源码核实（版本基线 1.11.8）：
> `PropertySetter` 为接口（update/PropertySetter.java:32）；
> `UpdateWrapper<T> extends PropertySetter<UpdateWrapper<T>>, Serializable`（update/UpdateWrapper.java:35）；
> `ChainQuery<T>` 为接口（query/ChainQuery.java:38），`MapperQueryChain<T> extends ChainQuery<T>`（query/MapperQueryChain.java:44）；
> `BaseQueryWrapper<T extends BaseQueryWrapper<T>>`（query/BaseQueryWrapper.java:26），`QueryWrapper extends BaseQueryWrapper<QueryWrapper>`（query/QueryWrapper.java:34）；
> `QueryWrapperAdapter<R extends QueryWrapperAdapter<R>> extends QueryWrapper`（query/QueryWrapperAdapter.java:36）；
> `QueryChain<T> extends QueryWrapperAdapter<QueryChain<T>> implements MapperQueryChain<T>`（query/QueryChain.java:30）；
> `UpdateChain<T> extends QueryWrapperAdapter<UpdateChain<T>> implements PropertySetter<UpdateChain<T>>`（update/UpdateChain.java:40）。

```
PropertySetter<R>                   # 属性设置接口（set / setRaw）

UpdateWrapper<T>                    # 更新包装器接口（实现 PropertySetter）
                                    #   通过代理维护 Map<String,Object> 存储待更新字段

ChainQuery<T>                       # 链式查询接口
    └── MapperQueryChain<T>         # Mapper 链式查询接口

BaseQueryWrapper<T>                 # 基础查询包装器
    └── QueryWrapper                # 查询包装器
        └── QueryWrapperAdapter<R>  # 泛型适配器（WHERE / JOIN / GROUP BY / ORDER BY 等）
            ├── QueryChain<T>       # 链式查询（同时实现 MapperQueryChain）
            └── UpdateChain<T>      # 链式更新/删除（同时实现 PropertySetter）
```

---

## 参考来源

- 包路径：`com.mybatisflex.core.query`、`com.mybatisflex.core.update`
- 源码版本：MyBatis-Flex 1.11.8（根 pom.xml:73 `<revision>`）
