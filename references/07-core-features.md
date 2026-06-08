# 官网核心功能用例补齐

本文件补齐官网核心功能页的常用入口。涉及权限、租户、数据源、SQL 审计、加密、动态表名时属于高风险变更，修改前先梳理调用链和影响范围。

## 逻辑删除

```java
@Table("tb_account")
public class Account {
    @Column(isLogicDelete = true)
    private Boolean deleted;
}
```

删除方法会生成逻辑删除更新语义，查询默认过滤已删除数据。不要用原生 SQL 绕过逻辑删除。

## 乐观锁

```java
@Table("tb_account")
public class Account {
    @Column(version = true)
    private Long version;
}
```

同一张表只能有一个 version 字段。更新失败时要按项目错误响应处理并提示数据已变化。

## 数据填充

数据填充有两类：

- `@Table(onInsert/onUpdate)`：Java 应用层设置值。
- `@Column(onInsertValue/onUpdateValue)`：数据库层 SQL 片段设置值。

```java
@Column(onInsertValue = "now()", onUpdateValue = "now()")
private LocalDateTime updatedTime;
```

使用数据库函数时要确认数据库方言兼容性。

## 数据脱敏

数据脱敏用于查询结果展示控制，不等同于权限控制。需要防止原始字段通过其他接口、日志、导出链路泄露。

## 数据缓存

开启缓存前确认缓存粒度、失效策略和更新一致性。写操作频繁的表不要只为减少查询代码而启用缓存。

## SQL 审计

SQL 审计适合拦截或记录危险 SQL，例如无 where 更新、删除、慢 SQL。生产启用前确认误拦截策略和日志容量。

## SQL 打印

SQL 打印适合本地和测试环境定位问题。生产环境开启会暴露参数和增加日志量，默认不要在生产 profile 打开。

## 多数据源

```yaml
mybatis-flex:
  datasource:
    ds1:
      url: jdbc:mysql://127.0.0.1:3306/db
      username: root
      password: 123456
    ds2:
      url: jdbc:mysql://127.0.0.1:3306/db2
      username: root
      password: 123456
```

需要动态切换时使用项目既有数据源 key 规范。不要在业务代码里硬编码未知数据源名。

## 读写分离

读写分离基于多数据源。写操作走 master，查询走 slave。涉及事务时要确认读己之写、一致性延迟和强制主库读取策略。

## 数据源加密

数据源加密用于配置文件中的敏感信息解密。密钥来源必须来自安全配置，不写死在业务代码或仓库文档示例里。

## 动态表名

```java
TableManager.setDynamicTableProcessor(tableName -> tableName + "_01");
```

动态表名适用于分表、多租户独立表等场景。必须确认所有增删改查路径都经过同一处理器。

## 事务管理

Spring 项目优先使用 `@Transactional`。复杂编程式事务再参考 `references/13-transaction-util.md`。

## 数据权限

数据权限应在统一方言、拦截或权限策略层处理。不要在 Controller 或前端硬编码拼接权限条件。

## 字段权限

字段权限可通过 `@Table(onSet = XxxSetListener.class)` 在实体属性 set 阶段控制返回值。

```java
public class AccountOnSetListener implements SetListener {
    @Override
    public Object onSet(Object entity, String property, Object value) {
        if ("password".equals(property) && !hasPasswordPermission()) {
            return null;
        }
        return value;
    }
}
```

## 字段加密

官网示例使用 `SetListener` 对查询返回值处理。若需求是入库加密、查询解密，需要另行确认 TypeHandler、字段监听或统一加解密链路。

## 字典回写

字典回写可在 `onSet` 监听中根据数据库字段补充展示字段，展示字段要配置 `@Column(ignore = true)`。

```java
@Column(ignore = true)
private String sexString;
```

## 枚举属性

```java
public enum TypeEnum {
    TYPE1(1, "类型1");

    @EnumValue
    private final int code;
    private final String desc;
}
```

需要保存枚举属性值而不是枚举名时使用 `@EnumValue`。

## 多租户

```java
@Column(tenantId = true)
private Long tenantId;

TenantManager.setTenantFactory(() -> new Object[]{currentTenantId()});
```

多租户是数据隔离能力。新增查询、更新、删除时必须保留租户隔离，不能用原生 SQL 绕过。
