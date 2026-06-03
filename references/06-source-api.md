# MyBatis-Flex 核心源码解析

## QueryMethods - SQL 函数方法类

### 数学函数

| 方法 | 说明 | 示例 |
|------|------|------|
| `abs(x)` | 绝对值 | `abs(ACCOUNT.SCORE)` |
| `ceil(x)` / `ceiling(x)` | 向上取整 | `ceil(ACCOUNT.PRICE)` |
| `floor(x)` | 向下取整 | `floor(ACCOUNT.PRICE)` |
| `round(x)` / `round(x, y)` | 四舍五入 | `round(ACCOUNT.PRICE, 2)` |
| `truncate(x, y)` | 截断到小数点后 y 位 | `truncate(ACCOUNT.PRICE, 2)` |
| `pow(x, y)` / `power(x, y)` | x 的 y 次方 | `pow(ACCOUNT.BASE, 2)` |
| `sqrt(x)` | 平方根 | `sqrt(ACCOUNT.AREA)` |
| `exp(x)` | e 的 x 次方 | `exp(ACCOUNT.RATE)` |
| `mod(x, y)` | 取余 | `mod(ACCOUNT.NUM, 10)` |
| `log(x)` / `log10(x)` | 对数 | `log(ACCOUNT.VALUE)` |
| `rand()` / `rand(x)` | 随机数 (0~1) | `rand()` |
| `sign(x)` | 符号 (-1, 0, 1) | `sign(ACCOUNT.BALANCE)` |
| `pi()` | 圆周率 | `pi()` |
| `sin(x)`, `cos(x)`, `tan(x)` | 三角函数 | `sin(ACCOUNT.ANGLE)` |
| `asin(x)`, `acos(x)`, `atan(x)` | 反三角函数 | `asin(ACCOUNT.RATIO)` |
| `radians(x)` | 角度转弧度 | `radians(ACCOUNT.DEGREE)` |
| `degrees(x)` | 弧度转角度 | `degrees(ACCOUNT.RADIAN)` |

### 字符串函数

| 方法 | 说明 | 示例 |
|------|------|------|
| `length(s)` | 字符串长度 | `length(ACCOUNT.NAME)` |
| `charLength(s)` | 字符数 | `charLength(ACCOUNT.NAME)` |
| `concat(s1, s2, ...)` | 拼接字符串 | `concat(ACCOUNT.FIRST, " ", ACCOUNT.LAST)` |
| `concatWs(x, s1, s2, ...)` | 带分隔符拼接 | `concatWs("-", ACCOUNT.YEAR, ACCOUNT.MONTH)` |
| `upper(s)` | 转大写 | `upper(ACCOUNT.CODE)` |
| `lower(s)` | 转小写 | `lower(ACCOUNT.EMAIL)` |
| `left(s, n)` | 前 n 个字符 | `left(ACCOUNT.CODE, 3)` |
| `right(s, n)` | 后 n 个字符 | `right(ACCOUNT.CODE, 4)` |
| `substring(s, pos)` | 截取子串 | `substring(ACCOUNT.CODE, 2)` |
| `substring(s, pos, len)` | 截取指定长度子串 | `substring(ACCOUNT.CODE, 2, 5)` |
| `lpad(s, len, pad)` | 左填充 | `lpad(ACCOUNT.NUM, 10, "0")` |
| `rpad(s, len, pad)` | 右填充 | `rpad(ACCOUNT.NAME, 20, " ")` |
| `trim(s)` / `ltrim(s)` / `rtrim(s)` | 去空格 | `trim(ACCOUNT.NAME)` |
| `replace(s, old, new)` | 替换字符串 | `replace(ACCOUNT.PHONE, "-", "")` |
| `reverse(s)` | 反转字符串 | `reverse(ACCOUNT.CODE)` |
| `repeat(s, n)` | 重复 n 次 | `repeat("*", 5)` |
| `space(n)` | n 个空格 | `space(3)` |
| `instr(s, sub)` | 查找子串位置 | `instr(ACCOUNT.EMAIL, "@")` |
| `strcmp(s1, s2)` | 比较字符串 | `strcmp(ACCOUNT.P1, ACCOUNT.P2)` |
| `findInSet(s, set)` | 在 SET 中查找 | `findInSet("1", ACCOUNT.TAGS)` |

### 日期时间函数

| 方法 | 说明 | 示例 |
|------|------|------|
| `now()` | 当前日期时间 | `now()` |
| `curDate()` / `currentDate()` | 当前日期 | `curDate()` |
| `curTime()` / `currentTime()` | 当前时间 | `curTime()` |
| `sysDate()` | 系统日期 | `sysDate()` |
| `year(d)` | 年份 | `year(ACCOUNT.BIRTHDAY)` |
| `month(d)` | 月份 | `month(ACCOUNT.BIRTHDAY)` |
| `day(d)` / `dayOfMonth(d)` | 日 | `day(ACCOUNT.BIRTHDAY)` |
| `hour(t)` | 小时 | `hour(ACCOUNT.CREATED)` |
| `minute(t)` | 分钟 | `minute(ACCOUNT.CREATED)` |
| `second(t)` | 秒 | `second(ACCOUNT.CREATED)` |
| `quarter(d)` | 季度 (1-4) | `quarter(ACCOUNT.CREATED)` |
| `week(d)` | 第几周 | `week(ACCOUNT.CREATED)` |
| `dayOfWeek(d)` | 星期几 (1=周日) | `dayOfWeek(ACCOUNT.CREATED)` |
| `dayOfYear(d)` | 年中第几天 | `dayOfYear(ACCOUNT.CREATED)` |
| `dateFormat(d, format)` | 格式化日期 | `dateFormat(ACCOUNT.CREATED, "%Y-%m-%d")` |
| `dateDiff(d1, d2)` | 日期差（天） | `dateDiff(ACCOUNT.END, ACCOUNT.START)` |
| `addDate(d, n)` | 加 n 天 | `addDate(ACCOUNT.CREATED, 30)` |
| `subDate(d, n)` | 减 n 天 | `subDate(ACCOUNT.CREATED, 7)` |
| `addTime(t, n)` | 加 n 秒 | `addTime(ACCOUNT.CREATED, 3600)` |
| `subTime(t, n)` | 减 n 秒 | `subTime(ACCOUNT.CREATED, 1800)` |
| `unixTimestamp()` | UNIX 时间戳 | `unixTimestamp()` |
| `fromUnixTime(d)` | 时间戳转日期 | `fromUnixTime(ACCOUNT.TIMESTAMP)` |
| `toDays(d)` | 转换为天数 | `toDays(ACCOUNT.CREATED)` |
| `fromDays(n)` | 天数转日期 | `fromDays(737425)` |

### 聚合函数

| 方法 | 说明 | 示例 |
|------|------|------|
| `count()` | 总行数 | `count()` |
| `count(col)` | 指定列行数 | `count(ACCOUNT.ID)` |
| `sum(col)` | 求和 | `sum(ACCOUNT.AMOUNT)` |
| `avg(col)` | 平均值 | `avg(ACCOUNT.SCORE)` |
| `max(col)` | 最大值 | `max(ACCOUNT.PRICE)` |
| `min(col)` | 最小值 | `min(ACCOUNT.PRICE)` |
| `groupConcat(col)` | 分组拼接 | `groupConcat(ACCOUNT.NAME)` |
| `stringAgg(col, sep)` | 字符串聚合 (PG) | `stringAgg(ACCOUNT.NAME, ",")` |

### 条件/流程函数

| 方法 | 说明 | 示例 |
|------|------|------|
| `if_(cond, trueVal, falseVal)` | IF 函数 | `if_(ACCOUNT.AGE.ge(18), "成年", "未成年")` |
| `ifNull(nullCol, elseCol)` | IFNULL | `ifNull(ACCOUNT.NICK, ACCOUNT.NAME)` |
| `coalesce(col, ...)` | COALESCE | `coalesce(ACCOUNT.NICK, ACCOUNT.NAME, "未知")` |
| `case_()` | 搜索 CASE | 见下方 Case When |
| `case_(col)` | 简单 CASE | 见下方 Case When |

### CASE WHEN

```java
// 简单 Case
case_(ACCOUNT.STATUS)
    .when(1).then("启用")
    .when(0).then("禁用")
    .else_("未知")
    .end()
    .as("statusName")

// 搜索 Case
case_()
    .when(ACCOUNT.AGE.ge(60)).then("老年")
    .when(ACCOUNT.AGE.ge(40)).then("中年")
    .when(ACCOUNT.AGE.ge(18)).then("青年")
    .else_("未成年")
    .end()
    .as("ageGroup")
```

### DISTINCT

```java
distinct(ACCOUNT.NAME)                    // 单列去重
distinct(ACCOUNT.NAME, ACCOUNT.AGE)       // 多列去重
```

### 其他函数

| 方法 | 说明 | 示例 |
|------|------|------|
| `format(x, n)` | 格式化数字 | `format(ACCOUNT.PRICE, 2)` |
| `ascii(s)` | ASCII 码 | `ascii(ACCOUNT.CODE)` |
| `bin(x)` | 二进制编码 | `bin(ACCOUNT.NUM)` |
| `hex(x)` | 十六进制编码 | `hex(ACCOUNT.NUM)` |
| `oct(x)` | 八进制编码 | `oct(ACCOUNT.NUM)` |
| `conv(x, from, to)` | 进制转换 | `conv(ACCOUNT.NUM, 10, 2)` |
| `md5(s)` | MD5 加密 | `md5(ACCOUNT.PASSWORD)` |
| `cast(col, type)` | 类型转换 | `cast(ACCOUNT.NUM, "CHAR")` |
| `version()` | 数据库版本 | `version()` |
| `database()` | 当前数据库名 | `database()` |
| `user()` | 当前用户 | `user()` |
| `lastInsertId()` | 最后自增 ID | `lastInsertId()` |

### 构建常量/列

| 方法 | 说明 | 示例 |
|------|------|------|
| `number(n)` | 数字常量 | `number(100)` |
| `string(s)` | 字符串常量 | `string("hello")` |
| `null_()` | NULL 常量 | `null_()` |
| `true_()` | TRUE 常量 | `true_()` |
| `false_()` | FALSE 常量 | `false_()` |
| `column(name)` | 自定义列 | `column("custom_sql")` |
| `allColumns()` | 所有列 `*` | `allColumns()` |

### 查询条件

| 方法 | 说明 | 示例 |
|------|------|------|
| `exists(wrapper)` | EXISTS 子查询 | `exists(subQuery)` |
| `notExists(wrapper)` | NOT EXISTS | `notExists(subQuery)` |
| `not(condition)` | NOT 条件 | `not(STATUS.eq(0))` |
| `noCondition()` | 空条件 | `noCondition()` |
| `bracket(condition)` | 括号条件 | `bracket(cond1.and(cond2))` |
| `raw(sql)` | 原生 SQL | `raw("YEAR(created) = 2024")` |

---

## QueryWrapper - 核心查询方法

### 创建方式

```java
// 空 QueryWrapper
QueryWrapper.create()

// 根据实体类自动构建条件
QueryWrapper.create(entity)

// 根据 Map 构建条件
QueryWrapper.create(map)
```

### WHERE 条件方法

源码中 `QueryWrapper` 提供了以下 MyBatis-Plus 兼容方法：

| 方法 | SQL | 说明 |
|------|-----|------|
| `eq(col, val)` | `col = val` | 等于 |
| `ne(col, val)` | `col != val` | 不等于 |
| `gt(col, val)` | `col > val` | 大于 |
| `ge(col, val)` | `col >= val` | 大于等于 |
| `lt(col, val)` | `col < val` | 小于 |
| `le(col, val)` | `col <= val` | 小于等于 |
| `in(col, values)` | `col IN (...)` | IN 查询 |
| `notIn(col, values)` | `col NOT IN (...)` | NOT IN |
| `between(col, start, end)` | `col BETWEEN x AND y` | 范围查询 |
| `notBetween(col, start, end)` | `col NOT BETWEEN x AND y` | 范围排除 |
| `like(col, val)` | `col LIKE %val%` | 模糊匹配 |
| `likeLeft(col, val)` | `col LIKE val%` | 左模糊 |
| `likeRight(col, val)` | `col LIKE %val` | 右模糊 |
| `notLike(col, val)` | `col NOT LIKE %val%` | 模糊排除 |
| `isNull(col)` | `col IS NULL` | 空值判断 |
| `isNotNull(col)` | `col IS NOT NULL` | 非空判断 |

每个方法都有带 `isEffective` 参数的重载，用于动态条件控制。

### JOIN 方法

| 方法 | 说明 |
|------|------|
| `leftJoin(table)` | LEFT JOIN |
| `rightJoin(table)` | RIGHT JOIN |
| `innerJoin(table)` | INNER JOIN |
| `fullJoin(table)` | FULL JOIN |
| `crossJoin(table)` | CROSS JOIN |
| `join(table)` | JOIN |

### 其他方法

| 方法 | 说明 |
|------|------|
| `groupBy(col)` | 分组 |
| `having(condition)` | HAVING 条件 |
| `orderBy(col, asc)` | 排序（支持动态 Boolean） |
| `limit(rows)` | 限制行数 |
| `offset(offset)` | 偏移量 |
| `union(wrapper)` | UNION |
| `unionAll(wrapper)` | UNION ALL |
| `forUpdate()` | FOR UPDATE 锁 |
| `datasource(key)` | 指定数据源 |
| `hint(sql)` | SQL 提示 |
| `toSQL()` | 调试：查看生成的 SQL |

---

## ChainQuery - 链式查询接口

`ChainQuery<T>` 是链式查询的基础接口，定义了通用查询方法：

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `one()` | `T` | 查询单条 |
| `oneOpt()` | `Optional<T>` | 查询单条（Optional） |
| `oneAs(type)` | `<R>` | 查询单条并转换类型 |
| `oneAsOpt(type)` | `Optional<R>` | 查询单条并转换（Optional） |
| `list()` | `List<T>` | 查询列表 |
| `listAs(type)` | `List<R>` | 查询列表并转换 |
| `page(page)` | `Page<T>` | 分页查询 |
| `pageAs(page, type)` | `Page<R>` | 分页查询并转换 |

---

## MapperQueryChain - Mapper 链式查询

`MapperQueryChain<T>` 继承 `ChainQuery`，扩展了更多方法：

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `baseMapper()` | `BaseMapper<T>` | 获取 Mapper |
| `toQueryWrapper()` | `QueryWrapper` | 转换为 QueryWrapper |
| `count()` | `long` | 查询数量 |
| `exists()` | `boolean` | 判断是否存在 |
| `obj()` | `Object` | 获取第一列第一条数据 |
| `objAs(type)` | `<R>` | 获取第一列并转换 |
| `objOpt()` | `Optional<Object>` | 获取第一列（Optional） |
| `objList()` | `List<Object>` | 获取第一列所有数据 |
| `objListAs(type)` | `List<R>` | 获取第一列并转换 |
| `withFields()` | `FieldsBuilder<T>` | Fields 关联查询 |
| `withRelations()` | `RelationsBuilder<T>` | Relations 关联查询 |

---

## QueryChain - QueryWrapper 链式调用

`QueryChain<T>` 继承 `QueryWrapperAdapter`，实现 `MapperQueryChain`，是完整的链式查询实现。

### 创建方式

```java
// 通过实体类
QueryChain.of(Account.class)

// 通过 Mapper
QueryChain.of(accountMapper)
```

### 完整示例

```java
// 基础查询
Account account = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .one();

// DTO 转换
AccountVO vo = QueryChain.of(accountMapper)
    .select(ACCOUNT.ID, ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .oneAs(AccountVO.class);

// 分页查询
Page<Account> page = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .page(Page.of(1, 10));

// 查询单值
String name = (String) QueryChain.of(accountMapper)
    .select(ACCOUNT.USER_NAME)
    .from(ACCOUNT)
    .where(ACCOUNT.ID.eq(1))
    .obj();

// 关联查询
List<AccountVO> list = QueryChain.of(accountMapper)
    .select()
    .from(ACCOUNT)
    .where(ACCOUNT.AGE.ge(18))
    .listWithRelationsAs(AccountVO.class);
```

---

## 类继承关系

```
ChainQuery<T>                    # 链式查询接口
    └── MapperQueryChain<T>      # Mapper 链式查询接口

BaseQueryWrapper<T>              # 基础查询包装器
    └── QueryWrapper             # 查询包装器
        └── QueryWrapperAdapter<R>  # 泛型适配器
            └── QueryChain<T>    # 链式查询实现（同时实现 MapperQueryChain）
```

---

## 参考来源

- 知识库文件：MyBatis-Flex部分接口源码.md
- 包路径：`com.mybatisflex.core.query`
