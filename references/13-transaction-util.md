# TransactionUtil 事务工具类

> 🚫 **非框架 API（项目侧能力）**：`TransactionUtil`（`com.example.mybatisflex.util`）是**项目侧**基于 Spring
> `TransactionTemplate` 的封装，MyBatis-Flex 1.11.8 源码中不存在该类（检索无结果）。
> 还需注意区分两套 `Propagation`：本文示例用的是 **Spring** 的
> `org.springframework.transaction.annotation.Propagation`；MyBatis-Flex 框架自带的传播特性枚举是
> `com.mybatisflex.core.transaction.Propagation`（`mybatis-flex-core/src/main/java/com/mybatisflex/core/transaction/Propagation.java:21`）。
>
> **框架原生编程式事务**（无需引入本工具，Spring 场景同样可用）：
> - `Db.tx(Supplier<Boolean>)` / `Db.tx(Supplier<Boolean>, Propagation)` —— `mybatis-flex-core/src/main/java/com/mybatisflex/core/row/Db.java:1155`、`Db.java:1162`；返回 `null`/`false` 或抛异常即回滚
> - `Db.txWithResult(Supplier<T>)` / `Db.txWithResult(Supplier<T>, Propagation)` —— `Db.java:1170`、`Db.java:1177`；仅抛异常才回滚
> - `Db.txWithDecider(Supplier<T>, RollbackDecider<T>)` —— `Db.java:1184`
> - 底层实现 `TransactionalManager.exec(Supplier, Propagation, RollbackDecider)` —— `mybatis-flex-core/src/main/java/com/mybatisflex/core/transaction/TransactionalManager.java:60`
> - 框架 `Propagation` 枚举值：`REQUIRED`/`SUPPORTS`/`MANDATORY`/`REQUIRES_NEW`/`NOT_SUPPORTED`/`NEVER`/`NESTED`；其中 `NESTED` 运行时暂不支持（抛 `TransactionException`，见 `TransactionalManager.java:111`）
> - Spring 场景也可直接使用 `@Transactional` 或 Spring `TransactionTemplate`（官方文档 `docs/zh/core/tx.md`）
>
> ```java
> // 框架原生编程式事务示例
> Db.tx(() -> {
>     orderMapper.insert(order);
>     return true; // 返回 false/null 或抛异常均回滚
> });
> ```

## 依赖

需要 `spring-tx` 的 `PlatformTransactionManager`。

## 包路径

`com.example.mybatisflex.util.TransactionUtil`

## 源码

```java
package com.example.mybatisflex.util;

import jakarta.annotation.Nonnull;
import jakarta.annotation.Nullable;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionException;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.support.TransactionCallback;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.Objects;
import java.util.function.Consumer;

/**
 * @author DevilSpiderX
 */
public class TransactionUtil {
    private TransactionUtil() {
    }

    /**
     * 获取事务模板
     *
     * @param transactionManager 事务管理器
     * @param propagation        事务传播特性
     * @param readOnly           事务只读
     * @return 事务模板
     */
    public static TransactionTemplate getTemplate(
            final @Nonnull PlatformTransactionManager transactionManager,
            final @Nonnull Propagation propagation,
            final boolean readOnly
    ) {
        Objects.requireNonNull(transactionManager);
        final var template = new TransactionTemplate(transactionManager);
        template.setPropagationBehavior(propagation.value());
        template.setReadOnly(readOnly);
        return template;
    }

    /**
     * 获取事务模板
     *
     * @param transactionManager 事务管理器
     * @param propagation        事务传播特性
     * @return 事务模板
     */
    public static TransactionTemplate getTemplate(
            final @Nonnull PlatformTransactionManager transactionManager,
            final @Nonnull Propagation propagation
    ) {
        return getTemplate(transactionManager, propagation, false);
    }

    /**
     * 获取事务模板
     *
     * @param transactionManager 事务管理器
     * @param readOnly           事务只读
     * @return 事务模板
     */
    public static TransactionTemplate getTemplate(
            final @Nonnull PlatformTransactionManager transactionManager,
            final boolean readOnly
    ) {
        return getTemplate(transactionManager, Propagation.REQUIRED, readOnly);
    }

    /**
     * 获取事务模板。事务传播特性为默认的{@link Propagation#REQUIRED}
     *
     * @param transactionManager 事务管理器
     * @return 事务模板
     */
    public static TransactionTemplate getTemplate(
            final @Nonnull PlatformTransactionManager transactionManager
    ) {
        return getTemplate(transactionManager, Propagation.REQUIRED, false);
    }

    /**
     * 事务执行
     *
     * @param transactionManager 事务管理器
     * @param action             数据库操作
     * @param configurator       事务配置
     */
    public static <T> T execute(
            final @Nonnull PlatformTransactionManager transactionManager,
            final @Nonnull TransactionCallback<T> action,
            final @Nullable Consumer<TransactionTemplate> configurator
    ) throws TransactionException {
        final var template = getTemplate(transactionManager);
        if (Objects.nonNull(configurator)) {
            configurator.accept(template);
        }
        return template.execute(action);
    }

    /**
     * 事务执行
     *
     * @param transactionManager 事务管理器
     * @param action             数据库操作
     * @param propagation        事务传播特性
     * @param readOnly           事务只读
     */
    public static <T> T execute(
            final @Nonnull PlatformTransactionManager transactionManager,
            final @Nonnull TransactionCallback<T> action,
            final @Nonnull Propagation propagation,
            final boolean readOnly
    ) throws TransactionException {
        return getTemplate(transactionManager, propagation, readOnly)
                .execute(action);
    }

    /**
     * 事务执行
     *
     * @param transactionManager 事务管理器
     * @param action             数据库操作
     * @param propagation        事务传播特性
     */
    public static <T> T execute(
            final @Nonnull PlatformTransactionManager transactionManager,
            final @Nonnull TransactionCallback<T> action,
            final @Nonnull Propagation propagation
    ) throws TransactionException {
        return getTemplate(transactionManager, propagation)
                .execute(action);
    }

    /**
     * 事务执行
     *
     * @param transactionManager 事务管理器
     * @param action             数据库操作
     * @param readOnly           事务只读
     */
    public static <T> T execute(
            final @Nonnull PlatformTransactionManager transactionManager,
            final @Nonnull TransactionCallback<T> action,
            final boolean readOnly
    ) throws TransactionException {
        return getTemplate(transactionManager, readOnly)
                .execute(action);
    }

    /**
     * 事务执行。事务传播特性为默认的{@link Propagation#REQUIRED}
     *
     * @param transactionManager 事务管理器
     * @param action             数据库操作
     */
    public static <T> T execute(
            final @Nonnull PlatformTransactionManager transactionManager,
            final @Nonnull TransactionCallback<T> action
    ) throws TransactionException {
        return getTemplate(transactionManager)
                .execute(action);
    }

}
```

## API 说明

### getTemplate 方法

获取 `TransactionTemplate` 事务模板对象。

| 方法签名 | 说明 |
|---------|------|
| `getTemplate(transactionManager, propagation, readOnly)` | 完整参数版本 |
| `getTemplate(transactionManager, propagation)` | 默认 readOnly = false |
| `getTemplate(transactionManager, readOnly)` | 默认 propagation = REQUIRED |
| `getTemplate(transactionManager)` | 默认 propagation = REQUIRED, readOnly = false |

### execute 方法

执行事务操作。

| 方法签名 | 说明 |
|---------|------|
| `execute(transactionManager, action, configurator)` | 使用配置器自定义事务模板 |
| `execute(transactionManager, action, propagation, readOnly)` | 指定传播特性和只读 |
| `execute(transactionManager, action, propagation)` | 指定传播特性 |
| `execute(transactionManager, action, readOnly)` | 指定只读 |
| `execute(transactionManager, action)` | 默认配置 |

## 使用示例

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderMapper orderMapper;
    private final PlatformTransactionManager transactionManager;
    
    public void createOrder(Order order) {
        // 基本使用（默认 REQUIRED 传播特性）
        TransactionUtil.execute(transactionManager, status -> {
            orderMapper.insert(order);
            return null;
        });
        
        // 指定传播特性
        TransactionUtil.execute(transactionManager, status -> {
            orderMapper.insert(order);
            return null;
        }, Propagation.REQUIRES_NEW);
        
        // 只读事务
        TransactionUtil.execute(transactionManager, status -> {
            return orderMapper.selectOneById(order.getId());
        }, true);
        
        // 使用配置器自定义事务模板
        TransactionUtil.execute(transactionManager, status -> {
            orderMapper.insert(order);
            return null;
        }, template -> {
            template.setTimeout(30);
            template.setName("createOrderTx");
        });
    }
}
```
