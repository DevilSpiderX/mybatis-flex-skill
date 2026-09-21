# Service 与 Mapper 操作参考

> ⚠️ **重要限制**：ServiceImpl **不能**继承 IService，直接注入 Mapper 使用。

## Service 实现（不继承 IService）

直接在 ServiceImpl 中注入 Mapper 使用：

```java
@Service
@RequiredArgsConstructor
public class AccountService {
    private final AccountMapper accountMapper;
    
    // 基础 CRUD
    public List<Account> list() {
        return accountMapper.selectAll();
    }
    
    public Account getById(String id) {
        return accountMapper.selectOneById(id);
    }
    
    public void save(Account account) {
        accountMapper.insert(account);
    }
    
    public void update(Account account) {
        accountMapper.update(account);
    }
    
    public void delete(String id) {
        accountMapper.deleteById(id);
    }
    
    // 复杂查询使用 QueryChain（1.11.8 起 BaseMapper 无 queryChain()，用静态工厂）
    public List<Account> listActive() {
        return QueryChain.of(accountMapper)
            .where(ACCOUNT.STATUS.eq(1))
            .list();
    }
    
    // 分页查询（QueryChain 只有 page(Page)，没有 page(int, int)）
    public Page<Account> page(int pageNum, int pageSize) {
        return QueryChain.of(accountMapper)
            .page(new Page<>(pageNum, pageSize));
    }
    
    // 条件查询
    public List<Account> search(String name, Integer age) {
        return QueryChain.of(accountMapper)
            .where(ACCOUNT.USER_NAME.like(name, If::hasText))
            .and(ACCOUNT.AGE.ge(age, Objects::nonNull))
            .list();
    }
}
```

## BaseMapper 方法

### 新增

```java
int insert(T entity);
int insertSelective(T entity);                              // 忽略 null
int insertBatch(Collection<T> entities);                    // 按第一条构建字段
int insertBatchSelective(Collection<T> entities);           // 忽略 null，内部走 Db.executeBatch
int insertOrUpdate(T entity);                               // 主键有值则更新，否则插入
```

（源码：`mybatis-flex-core/src/main/java/com/mybatisflex/core/BaseMapper.java:87-257`。不存在
`insertOrUpdateBatch`，批量"存在则更新"需循环或自行分批次处理。）

### 查询

```java
T selectOneById(Serializable id);
List<T> selectAll();
List<T> selectListByQuery(QueryWrapper query);
<R> List<R> selectListByQueryAs(QueryWrapper query, Class<R> asType);
Page<T> paginate(Number pageNumber, Number pageSize, QueryWrapper query);

// 关联查询
T selectOneWithRelationsById(Serializable id);
List<T> selectAllWithRelations();
List<T> selectListWithRelationsByQuery(QueryWrapper query);
T selectOneWithRelationsByQuery(QueryWrapper query);
```

（源码：`BaseMapper.java:475-862`。）

**计数与存在性判断**——BaseMapper 没有无参 `selectCount()`，也没有 `exists`：

```java
long total = accountMapper.selectCountByQuery(query);   // BaseMapper.java:924
boolean exists = QueryChain.of(accountMapper)           // exists() 在链式对象上
    .where(ACCOUNT.USER_NAME.eq("zhang san"))
    .exists();
```

**链式查询入口**：1.11.8 起 `BaseMapper` 不再提供 `queryChain()` 方法（旧版有，已移除），
从 Mapper 拿链式查询用静态工厂 `QueryChain.of(mapper)`（用法见官方测试
`mybatis-flex-test/.../mapper/QueryChainTest.java:57`）。`IService` 上仍有 `queryChain()`，
但本项目 Service 不继承 IService，用不到。

### 更新

```java
int update(T entity);                                            // 通过 ID 更新，忽略 null
int updateByQuery(T entity, QueryWrapper query);                 // 条件更新，忽略 null
int updateByQuery(T entity, boolean ignoreNulls, QueryWrapper query);  // ignoreNulls=false 时更新 null
```

（源码：`BaseMapper.java:359-449`。不存在 `updateByQueryWithNulls`，需要"包含 null 更新"用
三参版传 `false`。）

### 删除

```java
int deleteById(Serializable id);
int deleteBatchByIds(Collection<? extends Serializable> idList);
int deleteByQuery(QueryWrapper query);
```

## UpdateEntity

部分字段更新：

```java
Account update = UpdateEntity.of(Account.class, "xxx");
update.setUserName("张三");
update.setAge(25);
accountMapper.update(update);
```

## Db 工具类

### 原生 SQL

```java
// 查询
List<Row> rows = Db.selectListBySql("SELECT * FROM tb_account");
Row row = Db.selectOneBySql("SELECT * FROM tb_account WHERE id = ?", "xxx");
long count = Db.selectCount("SELECT count(*) FROM tb_account");

// 更新
int rows = Db.updateBySql("UPDATE tb_account SET age = ? WHERE id = ?", 25, "xxx");
```

（源码：`mybatis-flex-core/src/main/java/com/mybatisflex/core/row/Db.java:526`（selectOneBySql）、
`:662`（selectListBySql）、`:955`（selectCount）、`:317`（updateBySql）。不存在 `selectAllBySql` /
`selectNumberBySql`，查询全部行用 `selectListBySql`，取数值用 `selectCount` 或
`Db.selectObject(sql, args)`。）

### Row 操作

```java
// 新增
Row row = new Row();
row.set("user_name", "zhang san");
row.set("age", 18);
Db.insert("tb_account", row);

// 更新（Row 必须包含主键）
Row update = new Row();
update.set("id", 100);          // 主键
update.set("age", 19);
Db.updateById("tb_account", update);

// 删除（需指定主键列名）
Db.deleteById("tb_account", "id", "xxx");

// 查询（需指定主键列名）
Row row = Db.selectOneById("tb_account", "id", "xxx");
List<Row> rows = Db.selectAll("tb_account");
Page<Row> page = Db.paginate("tb_account", 1, 10, QueryWrapper.create());
```

（源码：`Db.java:87`（insert）、`:353`（updateById）、`:219`（deleteById）、`:572`（selectOneById）、
`:810`（selectAll）、`:1094` 附近（paginate 四参重载）。Row 级接口都需要显式主键列名或带主键的 Row，
没有 `(表名, id值)` 两参重载。）

### 批量操作

```java
// 批量执行（consumer 必须用传入的 mapper 参数）
Db.executeBatch(entities, 1000, AccountMapper.class, (mapper, entity) -> {
    mapper.insert(entity);
});

// 批量更新
Db.updateEntitiesBatch(entities, 1000);

// 原生 SQL 批量：实现 BatchArgsSetter（getBatchSize + getSqlArgs(index)）
Db.updateBatch("UPDATE tb_account SET age = ? WHERE id = ?", new BatchArgsSetter() {
    @Override
    public int getBatchSize() {
        return accounts.size();
    }

    @Override
    public Object[] getSqlArgs(int index) {
        Account account = accounts.get(index);
        return new Object[]{account.getAge(), account.getId()};
    }
});
```

`Db.updateBatch` 名叫 update，实际可执行任何 SQL（insert/delete/update 均可）
（源码：`Db.java:327`，接口 `BatchArgsSetter.java:18`）。不存在
`Db.executeBatch(sql, batchSize, (preparer, entity) -> ...)` 这种 lambda 重载。

**坑点：consumer 内部的 insert/update 返回值不是影响行数。** `Db.executeBatch` 内部以
`ExecutorType.BATCH` 打开独立 SqlSession，语句先入批、由 `flushStatements()` 统一执行
（`mybatis-flex-core/src/main/java/com/mybatisflex/core/row/RowMapperInvoker.java:97-126`）；
`FlexBatchExecutor.doUpdate` 直接返回常量 `BATCH_UPDATE_RETURN_VALUE`（`Integer.MIN_VALUE + 1002`，
`mybatis-flex-core/src/main/java/com/mybatisflex/core/mybatis/executor/FlexBatchExecutor.java:82`，
常量定义见 MyBatis `BatchExecutor.java:43`）。真实影响行数在 `Db.executeBatch` 的返回值 `int[]` 中：
长度与入参集合一致、按顺序逐条对应（`RowMapperInvoker.java:111,121`）；需要总数时自行求和
（`Db.updateEntitiesBatch` 内部就是 `Arrays.stream(...).sum()`，`mybatis-flex-core/src/main/java/com/mybatisflex/core/row/Db.java:460`）。

```java
// 正确：影响行数取 Db.executeBatch 的返回值
int[] rows = Db.executeBatch(entities, 1000, AccountMapper.class, (mapper, entity) -> mapper.insert(entity));
long total = Arrays.stream(rows).sum();

// 错误：把 consumer 内部 insert 的返回值当影响行数
Db.executeBatch(entities, 1000, AccountMapper.class, (mapper, entity) -> {
    int affected = mapper.insert(entity);   // 恒为 BATCH_UPDATE_RETURN_VALUE，与行数无关
});
```

其他注意：

- consumer 必须使用参数传入的 `mapper`（来自 BATCH session，`RowMapperInvoker.java:100`）；若改用容器注入的
  Mapper Bean，语句经默认 executor 立即执行，失去批处理意义。
- 每条数据只应触发一条语句：`results` 数组按 `datas.size()` 预分配，一个 `consumer.accept` 里执行多条语句时
  updateCounts 总数越界，回填会数组越界。
- 批量执行失败抛 `BatchExecutorException`（`FlexBatchExecutor.java:120-132`），已入批的子批次随事务回滚，
  需按项目错误响应策略处理。

## 分页查询

```java
// Page 对象
Page<Account> page = new Page<>(1, 10);  // 第 1 页，每页 10 条

// Mapper 分页
Page<Account> result = accountMapper.paginate(page.getPageNumber(), 
                                              page.getPageSize(), 
                                              query);

// QueryChain 分页
Page<Account> result = QueryChain.of(accountMapper)
    .where(ACCOUNT.STATUS.eq(1))
    .page(new Page<>(1, 10));

// 关联分页（返回 Page<T>，Relation 字段已填充）
Page<Account> result2 = accountMapper.paginateWithRelations(page, query);

// 总记录数
result.getTotalRow();
// 总页数
result.getTotalPage();
// 当前页数据
result.getRecords();
```

## 条件判断

```java
// If 静态方法
.and(ACCOUNT.USER_NAME.like(name, If::hasText))
.and(ACCOUNT.AGE.ge(age, Objects::nonNull))
.and(ACCOUNT.STATUS.eq(status, s -> s > 0))

// 自定义条件
.and(ACCOUNT.DEPT_ID.in(deptIds, ids -> ids != null && !ids.isEmpty()))
```

## 排序

```java
QueryWrapper.create()
    .select().from(ACCOUNT)
    .orderBy(ACCOUNT.CREATE_TIME.desc())
    .orderBy(ACCOUNT.AGE.asc());

// 多字段排序
QueryWrapper.create()
    .select().from(ACCOUNT)
    .orderBy(ACCOUNT.DEPT_ID.asc(), ACCOUNT.AGE.desc());

// Null 排序
QueryWrapper.create()
    .select().from(ACCOUNT)
    .orderBy(ACCOUNT.NICK_NAME.asc().nullsLast());
```

## 只查询部分字段

```java
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.ID, ACCOUNT.USER_NAME)
    .from(ACCOUNT);

// 转 VO
List<AccountVO> voList = accountMapper.selectListByQueryAs(query, AccountVO.class);
```

## 字段排除

```java
QueryWrapper query = QueryWrapper.create()
    .select(ACCOUNT.ALL_COLUMNS
        .except(ACCOUNT.CREATE_TIME, ACCOUNT.UPDATE_TIME))
    .from(ACCOUNT);
```

## 字段重命名

```java
QueryWrapper query = QueryWrapper.create()
    .select(
        ACCOUNT.USER_NAME.as("name"),
        ACCOUNT.AGE.as("userAge")
    )
    .from(ACCOUNT);

// 转 VO
List<AccountVO> voList = accountMapper.selectListByQueryAs(query, AccountVO.class);
```
