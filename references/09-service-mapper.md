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
    
    // 复杂查询使用 QueryChain
    public List<Account> listActive() {
        return accountMapper.queryChain()
            .where(ACCOUNT.STATUS.eq(1))
            .list();
    }
    
    // 分页查询
    public Page<Account> page(int pageNum, int pageSize) {
        return accountMapper.queryChain()
            .page(pageNum, pageSize);
    }
    
    // 条件查询
    public List<Account> search(String name, Integer age) {
        return accountMapper.queryChain()
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
int insertBatch(Collection<T> entities);
int insertOrUpdate(T entity);
int insertOrUpdateBatch(Collection<T> entities);
```

### 查询

```java
T selectOneById(Serializable id);
List<T> selectAll();
List<T> selectListByQuery(QueryWrapper query);
<T1> List<T1> selectListByQueryAs(QueryWrapper query, Class<T1> asType);
Page<T> paginate(int pageNumber, int pageSize, QueryWrapper query);
long selectCount();
long selectCountByQuery(QueryWrapper query);
boolean exists(QueryWrapper query);

// 关联查询
T selectOneWithRelationsById(Serializable id);
List<T> selectAllWithRelations();
List<T> selectListWithRelationsByQuery(QueryWrapper query);
T selectOneWithRelationsByQuery(QueryWrapper query);

// QueryChain
QueryChain<T> queryChain();
QueryChain<T> queryChain(QueryWrapper query);
```

### 更新

```java
int update(T entity);  // 通过 ID 更新，忽略 null
int updateByQuery(T entity, QueryWrapper query);  // 条件更新
int updateByQueryWithNulls(T entity, QueryWrapper query);  // 包含 null
```

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
List<Row> rows = Db.selectAllBySql("SELECT * FROM tb_account");
Row row = Db.selectOneBySql("SELECT * FROM tb_account WHERE id = ?", "xxx");
long count = Db.selectNumberBySql("SELECT count(*) FROM tb_account", null).longValue();

// 更新
int rows = Db.updateBySql("UPDATE tb_account SET age = ? WHERE id = ?", 25, "xxx");
```

### Row 操作

```java
// 新增
Row row = new Row();
row.set("user_name", "zhang san");
row.set("age", 18);
Db.insert("tb_account", row);

// 更新
Db.updateById("tb_account", row);

// 删除
Db.deleteById("tb_account", "xxx");

// 查询
Row row = Db.selectOneById("tb_account", "xxx");
List<Row> rows = Db.selectAll("tb_account");
Page<Row> page = Db.paginate("tb_account", 1, 10, QueryWrapper.create());
```

### 批量操作

```java
// 批量执行
Db.executeBatch(entities, 1000, AccountMapper.class, (mapper, entity) -> {
    mapper.insert(entity);
});

// 批量更新
Db.updateEntitiesBatch(entities, 1000);

// 原生 SQL 批量
Db.executeBatch(sql, 1000, (preparer, entity) -> {
    preparer.setObject(1, entity.getUserName());
    preparer.setObject(2, entity.getAge());
});
```

## 分页查询

```java
// Page 对象
Page<Account> page = new Page<>(1, 10);  // 第 1 页，每页 10 条

// Mapper 分页
Page<Account> result = accountMapper.paginate(page.getPageNumber(), 
                                              page.getPageSize(), 
                                              query);

// QueryChain 分页
Page<Account> result = accountMapper.queryChain()
    .where(ACCOUNT.STATUS.eq(1))
    .page(1, 10);

// PageWithDetails
PageWithDetails<Account, Role> result = 
    (PageWithDetails) accountMapper.paginateWithRelations(page, query);

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
