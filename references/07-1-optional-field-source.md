# OptionalField 源码实现

本文档包含 `OptionalField` 三态值类型的核心实现代码。

## OptionalField 类

```java
package com.example.json.lang;

import jakarta.annotation.Nonnull;
import jakarta.annotation.Nullable;

import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Stream;

/**
 * 三态值类型：MISSING（不存在）、NULL（存在但为null）、VALUE（有值）
 * 
 * @author DevilSpiderX
 */
public class OptionalField<T> {

    private static final OptionalField<?> MISSING = new OptionalField<>(State.MISSING, null);
    private static final OptionalField<?> NULL = new OptionalField<>(State.NULL, null);

    public enum State {
        MISSING, NULL, VALUE
    }

    private final State state;
    private final T value;

    private OptionalField(final @Nonnull State state, final @Nullable T value) {
        this.state = state;
        this.value = value;
    }

    /**
     * 创建 MISSING 状态（字段不存在）
     */
    @Nonnull
    public static <T> OptionalField<T> missing() {
        return (OptionalField<T>) MISSING;
    }

    /**
     * 创建 NULL 状态（字段存在但为 null）
     */
    @Nonnull
    public static <T> OptionalField<T> _null() {
        return (OptionalField<T>) NULL;
    }

    /**
     * 创建 VALUE 状态（字段有值）
     * 如果 value 为 null，则返回 NULL 状态
     */
    @Nonnull
    public static <T> OptionalField<T> of(final @Nullable T value) {
        if (value == null) {
            return _null();
        } else {
            return new OptionalField<>(State.VALUE, value);
        }
    }

    /**
     * 从可能为 null 的 OptionalField 创建
     * 如果 field 为 null，则返回 MISSING 状态
     */
    @Nonnull
    public static <T> OptionalField<T> of(final @Nullable OptionalField<T> field) {
        if (field == null) {
            return missing();
        }
        return field;
    }

    /**
     * 获取当前状态
     */
    public State getState() {
        return state;
    }

    /**
     * 获取值（仅 VALUE 状态有效）
     */
    public T getValue() {
        return value;
    }

    /**
     * 是否有值（VALUE 状态）
     */
    public boolean isPresent() {
        return state == State.VALUE;
    }

    /**
     * 是否为 NULL 状态
     */
    public boolean isNull() {
        return state == State.NULL;
    }

    /**
     * 是否为 MISSING 状态
     */
    public boolean isMissing() {
        return state == State.MISSING;
    }

    @Override
    public String toString() {
        return switch (state) {
            case MISSING -> "OptionalField.MISSING";
            case NULL -> "OptionalField.NULL";
            case VALUE -> "OptionalField[" + value + "]";
        };
    }

    @Override
    public boolean equals(final Object o) {
        if (!(o instanceof final OptionalField<?> that)) return false;
        return state == that.state && Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(state, value);
    }

    /**
     * 转换为 Stream（VALUE 状态返回包含值的 Stream，否则返回空 Stream）
     */
    @Nonnull
    public Stream<T> stream() {
        if (isPresent()) {
            return Stream.of(value);
        } else {
            return Stream.empty();
        }
    }

    /**
     * 获取值，如果是 MISSING 或 NULL 则返回默认值
     */
    public T orElse(final T other) {
        if (isPresent()) {
            return value;
        } else {
            return other;
        }
    }

    /**
     * 获取值，根据状态返回不同的默认值
     */
    public T orElse(final T otherInNull, final T otherInMissing) {
        return switch (state) {
            case VALUE -> value;
            case NULL -> otherInNull;
            case MISSING -> otherInMissing;
        };
    }

    /**
     * 获取值，如果是 MISSING 或 NULL 则通过 Supplier 获取默认值
     */
    public T orElseGet(final @Nonnull Supplier<? extends T> supplier) {
        if (isPresent()) {
            return value;
        } else {
            return supplier.get();
        }
    }

    /**
     * 获取值，根据状态通过不同的 Supplier 获取默认值
     */
    public T orElseGet(
            final @Nonnull Supplier<? extends T> supplierInNull,
            final @Nonnull Supplier<? extends T> supplierInMissing
    ) {
        return switch (state) {
            case VALUE -> value;
            case NULL -> supplierInNull.get();
            case MISSING -> supplierInMissing.get();
        };
    }

    /**
     * 匹配状态并执行相应操作（只处理 VALUE 和 NULL）
     */
    public void match(
            final @Nonnull Consumer<? super T> present,
            final @Nonnull Runnable nullValue
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        switch (state) {
            case NULL -> nullValue.run();
            case VALUE -> present.accept(value);
        }
    }

    /**
     * 匹配状态并执行相应操作（处理所有三种状态）
     */
    public void match(
            final @Nonnull Consumer<? super T> present,
            final @Nonnull Runnable nullValue,
            final @Nonnull Runnable missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        switch (state) {
            case MISSING -> missing.run();
            case NULL -> nullValue.run();
            case VALUE -> present.accept(value);
        }
    }

    /**
     * 匹配状态并返回结果（处理所有三种状态）
     */
    public <R> R match(
            final @Nonnull Function<? super T, ? extends R> present,
            final @Nonnull Supplier<? extends R> nullValue,
            final @Nonnull Supplier<? extends R> missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        return switch (state) {
            case MISSING -> missing.get();
            case NULL -> nullValue.get();
            case VALUE -> present.apply(value);
        };
    }

    /**
     * 映射值（仅 VALUE 状态会转换）
     */
    @Nonnull
    public <U> OptionalField<U> map(final @Nonnull Function<? super T, ? extends U> mapper) {
        Objects.requireNonNull(mapper);
        if (isPresent()) {
            return OptionalField.of(mapper.apply(value));
        } else {
            if (isNull()) {
                return OptionalField._null();
            } else {
                return OptionalField.missing();
            }
        }
    }

    /**
     * 扁平映射（仅 VALUE 状态会转换）
     */
    @Nonnull
    public <U> OptionalField<U> flatMap(final @Nonnull Function<? super T, ? extends OptionalField<? extends U>> mapper) {
        Objects.requireNonNull(mapper);
        if (isPresent()) {
            final OptionalField<U> r = (OptionalField<U>) mapper.apply(value);
            return Objects.requireNonNull(r);
        } else {
            if (isNull()) {
                return OptionalField._null();
            } else {
                return OptionalField.missing();
            }
        }
    }
}
```

## OptionalDtoUtil 工具类

用于将包含 `OptionalField` 字段的 DTO 转换为 `UpdateEntity`。

```java
package com.example.mybatisflex.util;

import com.mybatisflex.core.util.UpdateEntity;
import com.example.json.lang.OptionalField;
import lombok.extern.slf4j.Slf4j;

import java.beans.IntrospectionException;
import java.beans.Introspector;
import java.lang.reflect.InvocationTargetException;
import java.util.Objects;

/**
 * OptionalField DTO 转换工具
 * 
 * @author DevilSpiderX
 */
@Slf4j
public class OptionalDtoUtil {

    private OptionalDtoUtil() {
    }

    /**
     * 将 DTO 转换为 UpdateEntity（无 ID）
     * 
     * @param dto   源 DTO 对象
     * @param clazz 目标实体类
     * @return UpdateEntity 实例
     */
    public static <R> R toUpdateEntity(final Object dto, final Class<R> clazz) {
        return toUpdateEntity(dto, clazz, null);
    }

    /**
     * 将 DTO 转换为 UpdateEntity（带 ID）
     * 
     * @param dto   源 DTO 对象
     * @param clazz 目标实体类
     * @param id    主键 ID
     * @return UpdateEntity 实例
     */
    public static <R> R toUpdateEntity(final Object dto, final Class<R> clazz, final Object id) {
        if (dto == null) {
            return null;
        }

        final R entity;
        if (id == null) {
            entity = UpdateEntity.of(clazz);
        } else {
            entity = UpdateEntity.of(clazz, id);
        }

        final var dtoClass = dto.getClass();
        try {
            final var targetPds = Introspector.getBeanInfo(clazz, Object.class)
                    .getPropertyDescriptors();

            if (dtoClass.isRecord()) {
                // Record 类型处理
                convertRecordToEntity(dto, entity, targetPds, clazz);
            } else {
                // 普通类处理
                convertClassToEntity(dto, entity, targetPds, clazz);
            }
        } catch (IntrospectionException e) {
            log.warn("无法获取BeanInfo: {}", clazz.getName());
        }

        return entity;
    }

    /**
     * Record 类型 DTO 转换
     */
    private static <R> void convertRecordToEntity(
            final Object dto,
            final R entity,
            final java.beans.PropertyDescriptor[] targetPds,
            final Class<R> clazz
    ) throws IntrospectionException {
        final var dtoClass = dto.getClass();
        final var components = dtoClass.getRecordComponents();

        for (final var targetPd : targetPds) {
            final var propertyName = targetPd.getName();
            final var writeMethod = targetPd.getWriteMethod();
            if (writeMethod == null) {
                continue;
            }

            // 找 record 组件匹配的属性名
            for (final var component : components) {
                if (Objects.equals(component.getName(), propertyName)) {
                    final var accessor = component.getAccessor();
                    try {
                        final var value = accessor.invoke(dto);
                        handleFieldValue(entity, writeMethod, value, propertyName);
                    } catch (InvocationTargetException | IllegalAccessException e) {
                        log.debug("属性 {} 转换失败: {}", propertyName, e.getMessage(), e);
                    }
                    break;
                }
            }
        }
    }

    /**
     * 普通类 DTO 转换
     */
    private static <R> void convertClassToEntity(
            final Object dto,
            final R entity,
            final java.beans.PropertyDescriptor[] targetPds,
            final Class<R> clazz
    ) throws IntrospectionException {
        final var dtoClass = dto.getClass();
        final var dtoPds = Introspector.getBeanInfo(dtoClass, Object.class)
                .getPropertyDescriptors();

        for (final var targetPd : targetPds) {
            final var propertyName = targetPd.getName();
            final var writeMethod = targetPd.getWriteMethod();
            if (writeMethod == null) {
                continue;
            }

            // 在 dto 字段中找匹配
            for (final var dtoPd : dtoPds) {
                if (Objects.equals(dtoPd.getName(), propertyName)) {
                    final var accessor = dtoPd.getReadMethod();
                    try {
                        final var value = accessor.invoke(dto);
                        handleFieldValue(entity, writeMethod, value, propertyName);
                    } catch (InvocationTargetException | IllegalAccessException e) {
                        log.debug("属性 {} 转换失败: {}", propertyName, e.getMessage(), e);
                    }
                    break;
                }
            }
        }
    }

    /**
     * 处理字段值
     */
    private static <R> void handleFieldValue(
            final R entity,
            final java.lang.reflect.Method writeMethod,
            final Object value,
            final String propertyName
    ) throws InvocationTargetException, IllegalAccessException {
        if (value instanceof OptionalField<?> optionalFieldValue) {
            // OptionalField 类型处理
            if (optionalFieldValue.isPresent()) {
                // 有值：设置实际值
                writeMethod.invoke(entity, optionalFieldValue.getValue());
            } else if (optionalFieldValue.isNull()) {
                // NULL：设置为 null
                writeMethod.invoke(entity, (Object) null);
            }
            // MISSING：忽略，不设置
        } else if (value != null) {
            // 靳非 OptionalField 类型，直接设置
            writeMethod.invoke(entity, value);
        }
    }
}
```

## 相关文档

- [07-optional-field.md](07-optional-field.md) - OptionalField 使用指南
