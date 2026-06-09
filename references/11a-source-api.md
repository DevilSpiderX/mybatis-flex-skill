# MyBatis-Flex 核心源码解析 — QueryMethods（SQL 函数方法类）

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
