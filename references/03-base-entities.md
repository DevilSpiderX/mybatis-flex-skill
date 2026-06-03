# 基础实体类与配置

## Entity 基础类

### BaseEntity

```java
package com.example.common.model.base.entity;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 其他Entity继承该类，可自动填写create_time、update_time字段
 *
 * @author DevilSpiderX
 */
@Data
public class BaseEntity implements Serializable {
    /**
     * 创建时间
     */
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    private LocalDateTime updateTime;
}
```

### BaseAllEntity

```java
package com.example.common.model.base.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 其他Entity继承该类，可自动填写create_time、update_time、create_user、update_user字段
 *
 * @author DevilSpiderX
 */
@EqualsAndHashCode(callSuper = true)
@Data
public class BaseAllEntity extends BaseEntity {
    /**
     * 创建人 id
     */
    private Long createUser;

    /**
     * 更新人 id
     */
    private Long updateUser;
}
```

## UUIDv7 主键生成器

### 生成器实现

```java
package com.example.mybatisflex.keygen;

import com.github.f4b6a3.uuid.UuidCreator;
import com.mybatisflex.core.keygen.IKeyGenerator;

import java.util.UUID;

/**
 * 对应数据库类型为 <code>char(32)</code>
 *
 * @author DevilSpiderX
 */
public class UUIDv7KeyGenerator implements IKeyGenerator {

    public static final String NAME = "UUIDv7";

    @Override
    public Object generate(Object entity, String keyColumn) {
        return generateUUIDv7().toString()
                .replace("-", "");
    }

    private UUID generateUUIDv7() {
        return UuidCreator.getTimeOrderedEpoch();
    }

}
```

### 注册方式

```java
KeyGeneratorFactory.register(UUIDv7KeyGenerator.NAME, new UUIDv7KeyGenerator());
```

### 使用方式

```java
@Id(keyType = KeyType.Generator, value = UUIDv7KeyGenerator.NAME)
private String id;
```

**数据库字段类型：** `char(32)`

## 自动插值配置

### 配置类

```java
package com.example.server.configuration;

import cn.dev33.satoken.context.SaHolder;
import com.mybatisflex.annotation.InsertListener;
import com.mybatisflex.annotation.UpdateListener;
import com.mybatisflex.core.keygen.KeyGeneratorFactory;
import com.mybatisflex.core.logicdelete.LogicDeleteProcessor;
import com.mybatisflex.core.logicdelete.impl.TimeStampLogicDeleteProcessor;
import com.mybatisflex.spring.boot.MyBatisFlexCustomizer;
import com.example.common.model.base.entity.BaseAllEntity;
import com.example.common.model.base.entity.BaseEntity;
import com.example.mybatisflex.keygen.UUIDv7KeyGenerator;
import com.example.server.satoken.StpKit;
import jakarta.annotation.Nullable;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 配置自动填充字段。
 * 继承了BaseEntity、BaseAllEntity的实体类，
 * 会自动填充createUser、updateUser、createTime、updateTime这几个字段
 *
 * @author DevilSpiderX
 */
@Configuration
public class MybatisFlexConfig {

    static {
        KeyGeneratorFactory.register(UUIDv7KeyGenerator.NAME, new UUIDv7KeyGenerator());
    }

    @Bean
    public MyBatisFlexCustomizer mybatisFlexCustomizer() {
        final var baseEntityListener = new BaseEntityListener();

        return (config) -> {
            config.registerInsertListener(
                    baseEntityListener,
                    BaseAllEntity.class,
                    BaseEntity.class
            );
            config.registerUpdateListener(
                    baseEntityListener,
                    BaseAllEntity.class,
                    BaseEntity.class
            );
        };
    }

    public static class BaseEntityListener implements InsertListener, UpdateListener {

        @Override
        public void onInsert(final Object entity) {
            final Long userId = getUserId();
            final var time = LocalDateTime.now();

            if (entity instanceof BaseAllEntity baseAllEntity) {
                final long _userId = Objects.requireNonNullElse(userId, -1L);
                baseAllEntity.setCreateUser(_userId);
                baseAllEntity.setUpdateUser(_userId);
                baseAllEntity.setCreateTime(time);
                baseAllEntity.setUpdateTime(time);
            } else if (entity instanceof BaseEntity baseEntity) {
                baseEntity.setCreateTime(time);
                baseEntity.setUpdateTime(time);
            }
        }

        @Override
        public void onUpdate(final Object entity) {
            final Long userId = getUserId();
            final var time = LocalDateTime.now();

            if (entity instanceof BaseAllEntity baseAllEntity) {
                final long _userId = Objects.requireNonNullElse(userId, -1L);
                baseAllEntity.setUpdateUser(_userId);
                baseAllEntity.setUpdateTime(time);
            } else if (entity instanceof BaseEntity baseEntity) {
                baseEntity.setUpdateTime(time);
            }
        }

        private @Nullable Long getUserId() {
            final var saContext = SaHolder.getContext();
            if (!saContext.isValid()) {
                return null;
            }

            final var id = StpKit.USER.getLoginIdDefaultNull();

            final Number result;
            if (id instanceof Number _id) {
                result = _id;
            } else if (id instanceof String _id) {
                result = Long.parseLong(_id);
            } else {
                return null;
            }

            return result.longValue();
        }
    }

    @Bean
    public LogicDeleteProcessor flexLogicDeleteProcessor() {
        return new TimeStampLogicDeleteProcessor();
    }

}
```

## 事务工具类

### TransactionUtil

```java
package com.example.mybatisflex.util;

import jakarta.annotation.Nonnull;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionException;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.support.TransactionCallback;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.Objects;

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

## 推荐配置

```properties
# mybatis-flex.config
processor.enable=true
processor.mapper.generateEnable=true
processor.mapper.annotation=true
```

| 配置项                            | 说明                 |
| --------------------------------- | -------------------- |
| `processor.enable`                | 启用 APT 开关        |
| `processor.mapper.generateEnable` | APT 开启 Mapper 生成 |
| `processor.mapper.annotation`     | 开启 @Mapper 注解    |
