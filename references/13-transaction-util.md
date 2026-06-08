# TransactionUtil 事务工具类

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
