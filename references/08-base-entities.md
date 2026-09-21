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
     * 无登录上下文时的默认审计人，按项目实际取值（如系统账号的 UUIDv7）
     */
    public static final String DEFAULT_USER_ID = "system";

    /**
     * 创建人，UUIDv7 字符串，对应数据库类型为 <code>char(32)</code>
     */
    private String createUser;

    /**
     * 更新人，UUIDv7 字符串，对应数据库类型为 <code>char(32)</code>
     */
    private String updateUser;
}
```

## UUIDv7 主键生成器

**依赖**（Maven；Gradle 用 `implementation "com.github.f4b6a3:uuid-creator:6.1.1"`）：

```xml
<dependency>
    <groupId>com.github.f4b6a3</groupId>
    <artifactId>uuid-creator</artifactId>
    <version>6.1.1</version>
</dependency>
```

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

### 抽象监听基类

`AbstractInsertUpdateListener` 实现 `InsertListener`/`UpdateListener`，构造期通过反射取子类泛型参数得到
`supportType`，`onInsert`/`onUpdate` 中按 `isInstance` 过滤，只把支持的实体类型转交 `doInsert`/`doUpdate`
模板方法：

```java
package com.example.mybatisflex.listener;

import com.mybatisflex.annotation.InsertListener;
import com.mybatisflex.annotation.UpdateListener;
import org.jspecify.annotations.NonNull;

import java.lang.reflect.ParameterizedType;

/**
 * 类型支持 insert 和 update 监听器。
 *
 * @author DevilSpiderX
 * @param <T> T 泛型类型
 */
public abstract class AbstractInsertUpdateListener<T> implements InsertListener, UpdateListener {

    /**
     * 支持的类型
     */
    private final Class<T> supportType;

    @SuppressWarnings("unchecked")
    public AbstractInsertUpdateListener() {
        final var clazz = this.getClass();
        final var params = ((ParameterizedType) clazz.getGenericSuperclass()).getActualTypeArguments();
        if (params.length == 0) {
            throw new IllegalArgumentException(clazz.getSimpleName() + "继承AbstractInsertUpdateListener请指定泛型");
        }
        supportType = (Class<T>) params[0];
    }

    public abstract void doInsert(@NonNull T entity);

    public abstract void doUpdate(@NonNull T entity);

    @SuppressWarnings("unchecked")
    @Override
    public void onInsert(final Object entity) {
        if (supportType.isInstance(entity)) {
            final var object = (T) entity;
            doInsert(object);
        }
    }

    @SuppressWarnings("unchecked")
    @Override
    public void onUpdate(final Object entity) {
        if (supportType.isInstance(entity)) {
            final var object = (T) entity;
            doUpdate(object);
        }
    }

}
```

注意：

- 直接子类必须显式携带泛型参数（如 `extends AbstractInsertUpdateListener<BaseEntity>`），未指定时构造期抛
  `IllegalArgumentException`。
- `supportType` 来自 `getClass().getGenericSuperclass()`，若中间层子类未携带泛型参数（多级继承），强转
  `ParameterizedType` 会 `ClassCastException`。
- 框架侧注册的实体类与 `supportType` 取交集：`registerInsertListener(listener, BaseAllEntity.class, BaseEntity.class)`
  中的实体只要是通过 `supportType.isInstance` 的类型就会触发；由于 `BaseAllEntity extends BaseEntity`，
  `supportType` 为 `BaseEntity` 时两个注册都命中。

### 配置类

```java
package com.example.server.configuration;

import com.mybatisflex.core.keygen.KeyGeneratorFactory;
import com.mybatisflex.core.logicdelete.LogicDeleteProcessor;
import com.mybatisflex.core.logicdelete.impl.TimeStampLogicDeleteProcessor;
import com.mybatisflex.spring.boot.MyBatisFlexCustomizer;
import com.example.common.model.base.entity.BaseAllEntity;
import com.example.common.model.base.entity.BaseEntity;
import com.example.common.time.PlatformTime;
import com.example.mybatisflex.keygen.UUIDv7KeyGenerator;
import com.example.mybatisflex.listener.AbstractInsertUpdateListener;
import org.jspecify.annotations.NonNull;
import org.jspecify.annotations.Nullable;
import org.springframework.beans.factory.ObjectProvider;
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

    private final UserIdSupplier userIdSupplier;

    public MybatisFlexConfig(final ObjectProvider<UserIdSupplier> userIdSupplierProvider) {
        this.userIdSupplier = userIdSupplierProvider.getIfAvailable(() -> () -> null);
    }

    @Bean
    public MyBatisFlexCustomizer mybatisFlexCustomizer() {
        final var baseEntityListener = new BaseEntityListener(userIdSupplier);

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

    public static class BaseEntityListener extends AbstractInsertUpdateListener<BaseEntity> {

        private final UserIdSupplier userIdSupplier;

        public BaseEntityListener(final UserIdSupplier userIdSupplier) {
            this.userIdSupplier = userIdSupplier;
        }

        @Override
        public void doInsert(final @NonNull BaseEntity entity) {
            final var time = LocalDateTime.now(PlatformTime.ZONE_ID);
            entity.setCreateTime(time);
            entity.setUpdateTime(time);
            if (entity instanceof BaseAllEntity baseAllEntity) {
                final var userId = getUserId();
                // 创建人和更新人优先拿已经存在entity中的值
                // 如果为null，再从当前登录用户中拿
                final var createUser = Objects.requireNonNullElse(baseAllEntity.getCreateUser(), userId);
                final var updateUser = Objects.requireNonNullElse(baseAllEntity.getUpdateUser(), createUser);
                baseAllEntity.setCreateUser(createUser);
                baseAllEntity.setUpdateUser(updateUser);
            }
        }

        @Override
        public void doUpdate(final @NonNull BaseEntity entity) {
            final var time = LocalDateTime.now(PlatformTime.ZONE_ID);
            entity.setUpdateTime(time);
            if (entity instanceof BaseAllEntity baseAllEntity) {
                final var userId = getUserId();
                baseAllEntity.setUpdateUser(userId);
            }
        }

        private String getUserId() {
            final var id = userIdSupplier.get();
            return switch (id) {
                case Number _id -> _id.toString();
                case String _id when !_id.isBlank() -> _id;
                case null -> BaseAllEntity.DEFAULT_USER_ID;
                default -> throw new IllegalArgumentException("userId must be non-blank number or string");
            };
        }

    }

    @Bean
    public LogicDeleteProcessor flexLogicDeleteProcessor() {
        return new TimeStampLogicDeleteProcessor();
    }

    @FunctionalInterface
    public interface UserIdSupplier {
        @Nullable
        Object get();
    }

}
```

### 设计要点

- `UserIdSupplier` 通过 `ObjectProvider` 注入并降级为 `() -> null`：配置类不直接依赖 Sa-Token，
  测试和非 Web 环境无 Bean 也能启动；接入登录上下文时，在其他配置类提供一个 `UserIdSupplier` Bean 即可。
- `getUserId()` 把登录 ID 统一收敛为 `String`：`Number` 转字符串、非空白 `String` 原样返回、
  无登录上下文回落 `BaseAllEntity.DEFAULT_USER_ID`，其他类型直接抛 `IllegalArgumentException`，避免脏值入库。
- insert 时优先保留实体上已有的 `createUser`/`updateUser`（上游显式指定场景），为 null 才取当前登录用户；
  `updateUser` 再回落 `createUser`，保证两个字段不会一个为空一个有值。
- 时间统一走 `LocalDateTime.now(PlatformTime.ZONE_ID)`，避免多环境时区不一致。
- 监听器在 SQL 构建期同步执行，`getUserId()` 抛异常会中断整个 SQL 构建（见 `07-core-features.md` 数据填充章节）。

## 事务工具类

### TransactionUtil

适用于需要编程式事务控制的场景。需要 `spring-tx` 的 `PlatformTransactionManager`。

**源码位置**：见 `13-transaction-util.md`

**使用示例**：见 `13-transaction-util.md`
