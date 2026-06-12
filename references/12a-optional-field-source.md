# OptionalField 源码实现

本文档包含 `OptionalField` 三态值类型的核心实现代码。

> **架构说明**：`OptionalField` 采用 **sealed class 层次结构**，将三态行为分布到三个 final 子类中，
> 避免运行时 switch/enum 分支判断，每个子类直接实现对应状态的语义。

## OptionalField 类（基类）

```java
package com.example.json.lang;

import jakarta.annotation.Nonnull;
import jakarta.annotation.Nullable;

import java.util.NoSuchElementException;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.stream.Stream;

/**
 * 用于表示 JSON 字段的三态值容器，区分字段"不存在"与"值为 null"两种语义。
 *
 * <p>在标准 JSON 处理中，{@code null} 值和字段缺失往往具有不同的业务含义。
 * 例如，{@code {"name": null}} 表示"用户有意将姓名置空"，而 {@code {}}（无 name 字段）
 * 表示"用户未填写姓名"。{@link java.util.Optional} 的二元设计（{@code present/absent}）
 * 无法区分这两种场景，因此需要此三态容器。</p>
 *
 * <h2>三态定义</h2>
 * <table>
 *   <tr><th>状态</th><th>含义</th><th>典型场景</th></tr>
 *   <tr>
 *     <td>{@link ValueField}</td>
 *     <td>字段存在且有有效值</td>
 *     <td>{@code {"age": 25}}</td>
 *   </tr>
 *   <tr>
 *     <td>{@link NullField}</td>
 *     <td>字段存在但值为 {@code null}</td>
 *     <td>{@code {"age": null}}</td>
 *   </tr>
 *   <tr>
 *     <td>{@link MissingField}</td>
 *     <td>字段不存在</td>
 *     <td>{@code {}}（无 age 字段）</td>
 *   </tr>
 * </table>
 *
 * <h2>与 {@link java.util.Optional} 的区别</h2>
 * <ul>
 *   <li>{@link java.util.Optional} 是二元的（{@code present} / {@code absent}），无法区分 NULL 和 MISSING</li>
 *   <li>{@code OptionalField} 提供了 {@link #isNull()}、{@link #isMissing()} 等精细状态查询</li>
 *   <li>{@code OptionalField} 的 {@link #match} 方法支持三分支模式匹配</li>
 *   <li>{@code OptionalField} 的 {@link #orElse(Object, Object)} 支持按 NULL/MISSING 状态返回不同默认值</li>
 * </ul>
 *
 * <h2>使用示例</h2>
 * <pre>{@code
 * // 假设从 JSON 反序列化得到 OptionalField<String>
 * OptionalField<String> nickname = user.getOptionalNickname();
 *
 * // 安全获取值
 * String name = nickname.orElse("匿名用户");
 *
 * // 区分 NULL 和 MISSING 给出不同默认值
 * String name = nickname.orElse("未设置", "匿名用户");
 *
 * // 三分支匹配
 * nickname.match(
 *     name -> log.info("昵称: {}", name),
 *     ()   -> log.warn("昵称字段为 null"),
 *     ()   -> log.warn("昵称字段缺失")
 * );
 *
 * // 链式转换
 * String upper = nickname
 *         .map(String::toUpperCase)
 *         .orElse("N/A");
 * }</pre>
 *
 * @param <T> 字段值的类型
 * @author DevilSpiderX
 * @see MissingField
 * @see NullField
 * @see ValueField
 * @see java.util.Optional
 * @since 1.0
 */
public sealed abstract class OptionalField<T> permits MissingField, NullField, ValueField {

    // region 静态工厂方法

    /**
     * 创建一个表示字段不存在（MISSING 状态）的 {@link OptionalField} 实例。
     *
     * @param <T> 值的类型
     * @return MISSING 状态的 {@link OptionalField} 实例
     */
    @Nonnull
    @SuppressWarnings("unchecked")
    public static <T> OptionalField<T> missing() {
        return (OptionalField<T>) MissingField.INSTANCE;
    }

    /**
     * 创建一个表示字段值为 {@code null}（NULL 状态）的 {@link OptionalField} 实例。
     *
     * @param <T> 值的类型
     * @return NULL 状态的 {@link OptionalField} 实例
     */
    @Nonnull
    @SuppressWarnings("unchecked")
    public static <T> OptionalField<T> _null() {
        return (OptionalField<T>) NullField.INSTANCE;
    }

    /**
     * 根据给定的值创建 {@link OptionalField} 实例。
     * <ul>
     *   <li>如果 {@code value} 为 {@code null}，返回 {@link #_null()}（NULL 状态）</li>
     *   <li>如果 {@code value} 非 {@code null}，返回包含该值的 VALUE 状态实例</li>
     * </ul>
     *
     * @param <T>   值的类型
     * @param value 要包装的值，可以为 {@code null}
     * @return 包含给定值的 {@link OptionalField} 实例
     */
    @Nonnull
    public static <T> OptionalField<T> of(final @Nullable T value) {
        if (value == null) {
            return _null();
        } else {
            return new ValueField<>(value);
        }
    }

    /**
     * 根据给定的 {@link OptionalField} 创建实例。
     * <ul>
     *   <li>如果 {@code field} 为 {@code null}，返回 {@link #missing()}（MISSING 状态）</li>
     *   <li>如果 {@code field} 非 {@code null}，直接返回该字段</li>
     * </ul>
     *
     * @param <T>   值的类型
     * @param field 要包装的 {@link OptionalField}，可以为 {@code null}
     * @return 非 {@code null} 的 {@link OptionalField} 实例
     */
    @Nonnull
    public static <T> OptionalField<T> of(final @Nullable OptionalField<T> field) {
        if (field == null) {
            return missing();
        }
        return field;
    }

    // endregion

    // region 状态查询

    /**
     * 判断字段是否存在有效值（VALUE 状态）。
     *
     * @return 如果字段状态为 VALUE，返回 {@code true}；否则返回 {@code false}
     */
    public abstract boolean isPresent();

    /**
     * 判断字段的值是否为 {@code null}（NULL 状态）。
     *
     * @return 如果字段状态为 NULL，返回 {@code true}；否则返回 {@code false}
     */
    public abstract boolean isNull();

    /**
     * 判断字段是否不存在（MISSING 状态）。
     *
     * @return 如果字段状态为 MISSING，返回 {@code true}；否则返回 {@code false}
     */
    public abstract boolean isMissing();

    /**
     * 判断当前字段是否为空（即不存在或显式为 null）。
     *
     * @return 如果字段状态为 NULL 或 MISSING，返回 {@code true}；
     * 否则返回 {@code false}
     */
    public boolean isEmpty() {
        return isNull() || isMissing();
    }

    // endregion

    // region 获取值

    /**
     * 获取字段的值。
     * <p>
     * 注意：如果状态为 NULL 或 MISSING，返回 {@code null}。
     * 建议使用 {@link #orElse(Object)} 或 {@link #orElseThrow()} 等方法安全地获取值。
     * </p>
     *
     * @return 字段的值，可能为 {@code null}
     */
    public abstract T getValue();

    /**
     * 将字段的值转换为 {@link Stream}。
     *
     * @return 包含字段值的 {@link Stream}，不会为 {@code null}
     */
    @Nonnull
    public abstract Stream<T> stream();

    /**
     * 获取字段的值，如果值不存在则返回指定的默认值。
     *
     * @param other 值不存在时的默认值，可以为 {@code null}
     * @return 字段的值（如果存在）；否则返回 {@code other}
     */
    public abstract T orElse(final @Nullable T other);

    /**
     * 获取字段的值，根据不同的无值状态分别返回不同的默认值。
     *
     * @param otherInNull    字段值为 {@code null}（NULL 状态）时的默认值
     * @param otherInMissing 字段不存在（MISSING 状态）时的默认值
     * @return 根据字段状态返回对应的值
     */
    public abstract T orElse(final @Nullable T otherInNull, final @Nullable T otherInMissing);

    /**
     * 如果字段存在有效值，则返回该值；否则抛出 {@link NoSuchElementException}。
     *
     * @return 有效值
     * @throws NoSuchElementException 如果字段不存在有效值
     */
    @Nonnull
    public abstract T orElseThrow();

    /**
     * 如果字段存在有效值，则返回该值；否则抛出异常。
     *
     * @return 有效值
     * @throws X 如果字段不存在有效值
     */
    @Nonnull
    public abstract <X extends Throwable> T orElseThrow(final @Nonnull Supplier<? extends X> exceptionSupplier) throws X;

    /**
     * 获取字段的值，如果值不存在则通过 {@link Supplier} 延迟计算默认值。
     *
     * @param supplier 值不存在时用于生成默认值的供应者
     * @return 字段的值（如果存在）；否则返回 {@code supplier} 提供的值
     */
    public abstract T orElseGet(final @Nonnull Supplier<? extends T> supplier);

    /**
     * 获取字段的值，根据不同的无值状态分别通过 {@link Supplier} 延迟计算默认值。
     *
     * @param supplierInNull    字段值为 {@code null}（NULL 状态）时的默认值供应者
     * @param supplierInMissing 字段不存在（MISSING 状态）时的默认值供应者
     * @return 根据字段状态返回对应的值
     */
    public abstract T orElseGet(
            final @Nonnull Supplier<? extends T> supplierInNull,
            final @Nonnull Supplier<? extends T> supplierInMissing
    );

    // endregion

    // region 条件执行

    /**
     * 如果字段存在有效值，则执行给定的操作。
     *
     * @param action 要执行的操作
     */
    public abstract void ifPresent(final @Nonnull Consumer<? super T> action);

    /**
     * 如果字段值为 {@code null}（NULL 状态），则执行给定的操作。
     *
     * @param action 值为 null 时要执行的操作
     */
    public abstract void ifNull(final @Nonnull Runnable action);

    /**
     * 如果字段不存在（MISSING 状态），则执行给定的操作。
     *
     * @param action 字段不存在时要执行的操作
     */
    public abstract void ifMissing(final @Nonnull Runnable action);

    /**
     * 如果字段"为空"（NULL 或 MISSING 状态），则执行给定的操作。
     *
     * @param action 字段为空时要执行的操作
     */
    public abstract void ifEmpty(final @Nonnull Runnable action);

    // endregion

    // region 模式匹配

    /**
     * 根据字段状态执行对应的分支操作（双分支，忽略 MISSING 状态）。
     *
     * @param present   字段有值时的操作
     * @param nullValue 字段值为 null 时的操作
     */
    public abstract void match(
            final @Nonnull Consumer<? super T> present,
            final @Nonnull Runnable nullValue
    );

    /**
     * 根据字段状态执行对应的分支操作（三分支）。
     *
     * @param present   字段有值时的操作
     * @param nullValue 字段值为 null 时的操作
     * @param missing   字段不存在时的操作
     */
    public abstract void match(
            final @Nonnull Consumer<? super T> present,
            final @Nonnull Runnable nullValue,
            final @Nonnull Runnable missing
    );

    /**
     * 根据字段状态执行对应的映射函数并返回结果（三分支，带返回值）。
     *
     * @param <R>       返回值类型
     * @param present   字段有值时的映射函数
     * @param nullValue 字段值为 null 时的值供应者
     * @param missing   字段不存在时的值供应者
     * @return 根据字段状态返回对应的映射结果
     */
    public abstract <R> R match(
            final @Nonnull Function<? super T, ? extends R> present,
            final @Nonnull Supplier<? extends R> nullValue,
            final @Nonnull Supplier<? extends R> missing
    );

    // endregion

    // region 链式转换

    /**
     * 如果字段存在有效值，则对其应用映射函数并返回新的 {@link OptionalField}。
     * <p>
     * 如果字段处于 NULL 或 MISSING 状态，直接返回当前实例（类型转换）。
     * </p>
     *
     * @param <U>    映射后的值类型
     * @param mapper 映射函数
     * @return 映射后的新 {@link OptionalField} 实例
     */
    @Nonnull
    public abstract <U> OptionalField<U> map(final @Nonnull Function<? super T, ? extends U> mapper);

    /**
     * 如果字段存在有效值，则对其应用返回 {@link OptionalField} 的映射函数（展平嵌套）。
     *
     * @param <U>    映射后的值类型
     * @param mapper 映射函数，返回 {@link OptionalField}
     * @return 映射后的 {@link OptionalField} 实例
     */
    @Nonnull
    public abstract <U> OptionalField<U> flatMap(final @Nonnull Function<? super T, ? extends OptionalField<? extends U>> mapper);

    /**
     * 如果字段存在有效值且满足给定谓词，则返回当前字段；否则返回 {@link #_null()}。
     * <p>
     * 此方法保留了 MISSING 状态的语义（字段本身不存在）：
     * <ul>
     *   <li>值存在且通过谓词 → 返回 {@code this}（保持 VALUE 状态）</li>
     *   <li>值存在但不通过谓词 → 返回 {@link #_null()}（表示值存在但无效）</li>
     *   <li>字段不存在 → 返回 {@code this}（保持 MISSING 状态）</li>
     * </ul>
     * </p>
     *
     * @param predicate 谓词条件
     * @return 值存在且满足谓词返回当前字段；值存在但不满足返回 {@link #_null()}；值不存在返回 {@link #missing()}
     */
    @Nonnull
    public abstract OptionalField<T> filter(final @Nonnull Predicate<? super T> predicate);

    // endregion

}
```

## ValueField 类（VALUE 状态）

```java
package com.example.json.lang;

import jakarta.annotation.Nonnull;
import jakarta.annotation.Nullable;

import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.stream.Stream;

/**
 * 表示 JSON 字段存在且有有效值（VALUE 状态）的 {@link OptionalField} 子类。
 *
 * <p>VALUE 状态表示 JSON 中该字段存在且包含一个非 {@code null} 的值。</p>
 *
 * @param <T> 字段值的类型
 * @author DevilSpiderX
 * @see MissingField
 * @see NullField
 * @since 1.0
 */
public final class ValueField<T> extends OptionalField<T> {

    /**
     * 字段的值，保证非 {@code null}。
     */
    private final T value;

    /**
     * 构造包含指定值的 {@link ValueField} 实例。
     *
     * @param value 字段的值，不能为 {@code null}
     * @throws NullPointerException 如果 {@code value} 为 {@code null}
     */
    ValueField(final @Nonnull T value) {
        super();
        this.value = Objects.requireNonNull(value, "value must not be null");
    }

    // region 状态查询

    @Override
    public boolean isPresent() {
        return true;
    }

    @Override
    public boolean isNull() {
        return false;
    }

    @Override
    public boolean isMissing() {
        return false;
    }

    // endregion

    // region 获取值

    @Override
    @Nonnull
    public T getValue() {
        return value;
    }

    @Override
    @Nonnull
    public Stream<T> stream() {
        return Stream.of(value);
    }

    @Override
    public T orElse(final T other) {
        return value;
    }

    @Override
    public T orElse(final @Nullable T otherInNull, final @Nullable T otherInMissing) {
        return value;
    }

    @Override
    @Nonnull
    public T orElseThrow() {
        return value;
    }

    @Override
    @Nonnull
    public <X extends Throwable> T orElseThrow(final @Nonnull Supplier<? extends X> exceptionSupplier) {
        return value;
    }

    @Override
    public T orElseGet(final @Nonnull Supplier<? extends T> supplier) {
        return value;
    }

    @Override
    public T orElseGet(
            final @Nonnull Supplier<? extends T> supplierInNull,
            final @Nonnull Supplier<? extends T> supplierInMissing
    ) {
        return value;
    }

    // endregion

    // region 条件执行

    @Override
    public void ifPresent(final @Nonnull Consumer<? super T> action) {
        Objects.requireNonNull(action);
        action.accept(value);
    }

    @Override
    public void ifNull(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        // no-op: 不是 NULL 状态
    }

    @Override
    public void ifMissing(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        // no-op: 不是 MISSING 状态
    }

    @Override
    public void ifEmpty(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        // no-op: VALUE 状态不是"空"
    }

    // endregion

    // region 模式匹配

    @Override
    public void match(
            final @Nonnull Consumer<? super T> present,
            final @Nonnull Runnable nullValue
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        present.accept(value);
    }

    @Override
    public void match(
            final @Nonnull Consumer<? super T> present,
            final @Nonnull Runnable nullValue,
            final @Nonnull Runnable missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        present.accept(value);
    }

    @Override
    public <R> R match(
            final @Nonnull Function<? super T, ? extends R> present,
            final @Nonnull Supplier<? extends R> nullValue,
            final @Nonnull Supplier<? extends R> missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        return present.apply(value);
    }

    // endregion

    // region 链式转换

    @Override
    @Nonnull
    public <U> OptionalField<U> map(final @Nonnull Function<? super T, ? extends U> mapper) {
        Objects.requireNonNull(mapper);
        return OptionalField.of(mapper.apply(value));
    }

    @Override
    @Nonnull
    @SuppressWarnings("unchecked")
    public <U> OptionalField<U> flatMap(final @Nonnull Function<? super T, ? extends OptionalField<? extends U>> mapper) {
        Objects.requireNonNull(mapper);
        final OptionalField<U> result = (OptionalField<U>) mapper.apply(value);
        return Objects.requireNonNull(result);
    }

    @Override
    @Nonnull
    public OptionalField<T> filter(final @Nonnull Predicate<? super T> predicate) {
        Objects.requireNonNull(predicate);
        return predicate.test(value) ? this : OptionalField._null();
    }

    // endregion

    // region Object 方法

    @Override
    @Nonnull
    public String toString() {
        return "OptionalField[" + value + "]";
    }

    @Override
    public boolean equals(final Object o) {
        if (o instanceof ValueField<?> that) {
            return Objects.equals(value, that.value);
        }
        return false;
    }

    @Override
    public int hashCode() {
        return Objects.hash("OptionalField.VALUE", value);
    }

    // endregion

}
```

## NullField 类（NULL 状态）

```java
package com.example.json.lang;

import jakarta.annotation.Nonnull;
import jakarta.annotation.Nullable;

import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.stream.Stream;

/**
 * 表示 JSON 字段存在但值为 {@code null}（NULL 状态）的 {@link OptionalField} 子类。
 *
 * <p>NULL 状态表示 JSON 中该字段存在但显式设置为 {@code null}，区别于字段不存在（{@link MissingField}）。</p>
 *
 * @author DevilSpiderX
 * @see MissingField
 * @see ValueField
 * @since 1.0
 */
public final class NullField extends OptionalField<Object> {

    static final NullField INSTANCE = new NullField();

    private NullField() {
        super();
    }

    // region 状态查询

    @Override
    public boolean isPresent() {
        return false;
    }

    @Override
    public boolean isNull() {
        return true;
    }

    @Override
    public boolean isMissing() {
        return false;
    }

    // endregion

    // region 获取值

    @Override
    @Nullable
    public Object getValue() {
        return null;
    }

    @Override
    @Nonnull
    public Stream<Object> stream() {
        return Stream.empty();
    }

    @Override
    public Object orElse(final @Nullable Object other) {
        return other;
    }

    @Override
    public Object orElse(final @Nullable Object otherInNull, final @Nullable Object otherInMissing) {
        return otherInNull;
    }

    @Override
    @Nonnull
    public Object orElseThrow() {
        throw new NoSuchElementException("No value present");
    }

    @Override
    @Nonnull
    public <X extends Throwable> Object orElseThrow(final @Nonnull Supplier<? extends X> exceptionSupplier) throws X {
        throw exceptionSupplier.get();
    }

    @Override
    public Object orElseGet(final @Nonnull Supplier<?> supplier) {
        return supplier.get();
    }

    @Override
    public Object orElseGet(
            final @Nonnull Supplier<?> supplierInNull,
            final @Nonnull Supplier<?> supplierInMissing
    ) {
        return supplierInNull.get();
    }

    // endregion

    // region 条件执行

    @Override
    public void ifPresent(final @Nonnull Consumer<? super Object> action) {
        Objects.requireNonNull(action);
        // no-op: 值不存在
    }

    @Override
    public void ifNull(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        action.run();
    }

    @Override
    public void ifMissing(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
    }

    @Override
    public void ifEmpty(final @Nonnull Runnable action) {
        ifNull(action);
    }

    // endregion

    // region 模式匹配

    @Override
    public void match(
            final @Nonnull Consumer<? super Object> present,
            final @Nonnull Runnable nullValue
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        nullValue.run();
    }

    @Override
    public void match(
            final @Nonnull Consumer<? super Object> present,
            final @Nonnull Runnable nullValue,
            final @Nonnull Runnable missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        nullValue.run();
    }

    @Override
    public <R> R match(
            final @Nonnull Function<? super Object, ? extends R> present,
            final @Nonnull Supplier<? extends R> nullValue,
            final @Nonnull Supplier<? extends R> missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        return nullValue.get();
    }

    // endregion

    // region 链式转换

    @Override
    @Nonnull
    @SuppressWarnings("unchecked")
    public <U> OptionalField<U> map(final @Nonnull Function<? super Object, ? extends U> mapper) {
        Objects.requireNonNull(mapper);
        return (OptionalField<U>) this;
    }

    @Override
    @Nonnull
    @SuppressWarnings("unchecked")
    public <U> OptionalField<U> flatMap(final @Nonnull Function<? super Object, ? extends OptionalField<? extends U>> mapper) {
        Objects.requireNonNull(mapper);
        return (OptionalField<U>) this;
    }

    @Override
    @Nonnull
    public OptionalField<Object> filter(final @Nonnull Predicate<? super Object> predicate) {
        Objects.requireNonNull(predicate);
        return this;
    }

    // endregion

    // region Object 方法

    @Override
    @Nonnull
    public String toString() {
        return "OptionalField.NULL";
    }

    @Override
    public boolean equals(final Object o) {
        return o instanceof NullField;
    }

    @Override
    public int hashCode() {
        return Objects.hash("OptionalField.NULL");
    }

    // endregion

}
```

## MissingField 类（MISSING 状态）

```java
package com.example.json.lang;

import jakarta.annotation.Nonnull;
import jakarta.annotation.Nullable;

import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.stream.Stream;

/**
 * 表示 JSON 字段不存在（MISSING 状态）的 {@link OptionalField} 子类。
 *
 * <p>MISSING 状态表示 JSON 中该字段完全不存在，区别于字段存在但值为 null（{@link NullField}）。</p>
 *
 * @author DevilSpiderX
 * @see NullField
 * @see ValueField
 * @since 1.0
 */
public final class MissingField extends OptionalField<Object> {

    static final MissingField INSTANCE = new MissingField();

    private MissingField() {
        super();
    }

    // region 状态查询

    @Override
    public boolean isPresent() {
        return false;
    }

    @Override
    public boolean isNull() {
        return false;
    }

    @Override
    public boolean isMissing() {
        return true;
    }

    // endregion

    // region 获取值

    @Override
    @Nullable
    public Object getValue() {
        return null;
    }

    @Override
    @Nonnull
    public Stream<Object> stream() {
        return Stream.empty();
    }

    @Override
    public Object orElse(final @Nullable Object other) {
        return other;
    }

    @Override
    public Object orElse(final @Nullable Object otherInNull, final @Nullable Object otherInMissing) {
        return otherInMissing;
    }

    @Override
    @Nonnull
    public Object orElseThrow() {
        throw new NoSuchElementException("No value present");
    }

    @Override
    @Nonnull
    public <X extends Throwable> Object orElseThrow(final @Nonnull Supplier<? extends X> exceptionSupplier) throws X {
        throw exceptionSupplier.get();
    }

    @Override
    public Object orElseGet(final @Nonnull Supplier<?> supplier) {
        return supplier.get();
    }

    @Override
    public Object orElseGet(
            final @Nonnull Supplier<?> supplierInNull,
            final @Nonnull Supplier<?> supplierInMissing
    ) {
        return supplierInMissing.get();
    }

    // endregion

    // region 条件执行

    @Override
    public void ifPresent(final @Nonnull Consumer<? super Object> action) {
        Objects.requireNonNull(action);
        // no-op: 字段不存在
    }

    @Override
    public void ifNull(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
    }

    @Override
    public void ifMissing(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        action.run();
    }

    @Override
    public void ifEmpty(final @Nonnull Runnable action) {
        ifMissing(action);
    }

    // endregion

    // region 模式匹配

    @Override
    public void match(
            final @Nonnull Consumer<? super Object> present,
            final @Nonnull Runnable nullValue
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        // no-op: MISSING 状态在双分支匹配中被忽略
    }

    @Override
    public void match(
            final @Nonnull Consumer<? super Object> present,
            final @Nonnull Runnable nullValue,
            final @Nonnull Runnable missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        missing.run();
    }

    @Override
    public <R> R match(
            final @Nonnull Function<? super Object, ? extends R> present,
            final @Nonnull Supplier<? extends R> nullValue,
            final @Nonnull Supplier<? extends R> missing
    ) {
        Objects.requireNonNull(present);
        Objects.requireNonNull(nullValue);
        Objects.requireNonNull(missing);
        return missing.get();
    }

    // endregion

    // region 链式转换

    @Override
    @Nonnull
    @SuppressWarnings("unchecked")
    public <U> OptionalField<U> map(final @Nonnull Function<? super Object, ? extends U> mapper) {
        Objects.requireNonNull(mapper);
        return (OptionalField<U>) this;
    }

    @Override
    @Nonnull
    @SuppressWarnings("unchecked")
    public <U> OptionalField<U> flatMap(final @Nonnull Function<? super Object, ? extends OptionalField<? extends U>> mapper) {
        Objects.requireNonNull(mapper);
        return (OptionalField<U>) this;
    }

    @Override
    @Nonnull
    public OptionalField<Object> filter(final @Nonnull Predicate<? super Object> predicate) {
        Objects.requireNonNull(predicate);
        return this;
    }

    // endregion

    // region Object 方法

    @Override
    @Nonnull
    public String toString() {
        return "OptionalField.MISSING";
    }

    @Override
    public boolean equals(final Object o) {
        return o instanceof MissingField;
    }

    @Override
    public int hashCode() {
        return Objects.hash("OptionalField.MISSING");
    }

    // endregion

}
```

## OptionalDtoUtil 工具类

```java
package com.example.mybatisflex.util;

import com.mybatisflex.core.util.UpdateEntity;
import com.example.json.lang.OptionalField;
import jakarta.annotation.Nonnull;
import jakarta.annotation.Nullable;
import lombok.extern.slf4j.Slf4j;

import java.beans.IntrospectionException;
import java.beans.Introspector;
import java.beans.PropertyDescriptor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.RecordComponent;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * DTO 转换为 MyBatis-Flex UpdateEntity 的工具类
 * <p>
 * 支持 OptionalField 类型，用于区分「字段未传」和「字段传了 null」
 *
 * @author DevilSpiderX
 */
@Slf4j
public class OptionalDtoUtil {

    /**
     * PropertyDescriptor 缓存：避免重复反射获取
     */
    private static final ConcurrentHashMap<Class<?>, Map<String, PropertyDescriptor>> PROPERTY_DESCRIPTOR_CACHE = new ConcurrentHashMap<>();

    /**
     * Source getter 缓存：避免重复反射获取
     */
    private static final ConcurrentHashMap<Class<?>, Map<String, Method>> SOURCE_GETTER_CACHE = new ConcurrentHashMap<>();

    private OptionalDtoUtil() {
    }

    /**
     * 将 DTO 转换为 UpdateEntity（无 ID）
     *
     * @param dto   源 DTO 对象，支持普通类和 Record
     * @param clazz 目标实体类型
     * @param <R>   目标实体类型
     * @return 转换后的 UpdateEntity，dto 为 null 时返回 null
     */
    public static <R> R toUpdateEntity(final @Nullable Object dto, final @Nonnull Class<R> clazz) {
        return toUpdateEntity(dto, clazz, null);
    }

    /**
     * 将 DTO 转换为 UpdateEntity（带 ID）
     *
     * @param dto   源 DTO 对象，支持普通类和 Record
     * @param clazz 目标实体类型
     * @param id    记录 ID，为 null 时不设置 ID
     * @param <R>   目标实体类型
     * @return 转换后的 UpdateEntity，dto 为 null 时返回 null
     */
    public static <R> R toUpdateEntity(
            final @Nullable Object dto,
            final @Nonnull Class<R> clazz,
            final @Nullable Object id
    ) {
        Objects.requireNonNull(clazz, "目标实体类型 clazz 不能为 null");

        if (dto == null) {
            return null;
        }

        log.debug("开始转换: {} -> {}, id={}", dto.getClass().getSimpleName(), clazz.getSimpleName(), id);

        final R entity = (id == null) ? UpdateEntity.of(clazz) : UpdateEntity.of(clazz, id);

        try {
            final var targetPds = getPropertyDescriptorMap(clazz);
            final var sourceGetterMap = buildSourceGetterMap(dto);

            int convertedCount = 0;
            int skippedCount = 0;

            for (final var entry : targetPds.entrySet()) {
                final var propertyName = entry.getKey();
                final var targetPd = entry.getValue();
                final var writeMethod = targetPd.getWriteMethod();

                if (writeMethod == null) {
                    continue;
                }

                final var readMethod = sourceGetterMap.get(propertyName);
                if (readMethod == null) {
                    skippedCount++;
                    continue;
                }

                try {
                    final var value = readMethod.invoke(dto);
                    applyPropertyValue(
                            entity,
                            writeMethod,
                            value,
                            targetPd.getPropertyType(),
                            readMethod.getReturnType()
                    );
                    convertedCount++;
                } catch (InvocationTargetException | IllegalAccessException e) {
                    throw new IllegalArgumentException(
                            "属性 %s 转换失败: %s".formatted(propertyName, e.getMessage()),
                            e
                    );
                }
            }

            log.debug("转换完成: {} -> {}, 已转换={}, 已跳过={}", dto.getClass().getSimpleName(), clazz.getSimpleName(), convertedCount, skippedCount);

        } catch (IntrospectionException e) {
            throw new IllegalArgumentException(
                    "无法获取 %s 的 BeanInfo: %s".formatted(
                            dto.getClass().getName(),
                            e.getMessage()
                    ), e
            );
        }

        return entity;
    }

    /**
     * 获取目标类的属性描述符 Map（带缓存）
     */
    @Nonnull
    private static Map<String, PropertyDescriptor> getPropertyDescriptorMap(final @Nonnull Class<?> clazz) throws IntrospectionException {
        return PROPERTY_DESCRIPTOR_CACHE.computeIfAbsent(clazz, k -> {
            try {
                return Arrays.stream(Introspector.getBeanInfo(k, Object.class).getPropertyDescriptors())
                        .collect(Collectors.toMap(PropertyDescriptor::getName, Function.identity()));
            } catch (IntrospectionException e) {
                throw new RuntimeException("无法获取 %s 的 BeanInfo".formatted(k.getName()), e);
            }
        });
    }

    /**
     * 构建源对象的 getter 方法 Map（带缓存）
     * <p>
     * 支持普通类（通过 PropertyDescriptor）和 Record（通过 getRecordComponents）
     */
    @Nonnull
    private static Map<String, Method> buildSourceGetterMap(final @Nonnull Object dto) throws IntrospectionException {
        final var dtoClass = dto.getClass();

        return SOURCE_GETTER_CACHE.computeIfAbsent(dtoClass, k -> {
            if (k.isRecord()) {
                return Arrays.stream(k.getRecordComponents())
                        .collect(Collectors.toMap(RecordComponent::getName, RecordComponent::getAccessor));
            }

            try {
                return Arrays.stream(Introspector.getBeanInfo(k, Object.class).getPropertyDescriptors())
                        .filter(pd -> pd.getReadMethod() != null)
                        .collect(Collectors.toMap(PropertyDescriptor::getName, PropertyDescriptor::getReadMethod));
            } catch (IntrospectionException e) {
                throw new RuntimeException("无法获取 %s 的 BeanInfo".formatted(k.getName()), e);
            }
        });
    }

    /**
     * 应用属性值到目标对象
     */
    private static void applyPropertyValue(
            final @Nonnull Object target,
            final @Nonnull Method writeMethod,
            final @Nullable Object value,
            final @Nonnull Class<?> targetPropertyType,
            final @Nonnull Class<?> sourceValueType
    ) throws InvocationTargetException, IllegalAccessException {
        if (value instanceof OptionalField<?> optionalFieldValue) {
            if (optionalFieldValue.isPresent()) {
                writeMethod.invoke(target, optionalFieldValue.getValue());
            } else if (optionalFieldValue.isNull()) {
                writeMethod.invoke(target, (Object) null);
            }
            // OptionalField 为空（既不是 present 也不是 null）时跳过，不更新
        } else if (value != null) {
            // 判断是否需要嵌套转换：目标类型不是简单类型，且源值不是简单类型
            if (!isSimpleType(targetPropertyType) && !isSimpleType(sourceValueType)) {
                try {
                    // 递归转换嵌套对象
                    final var nestedEntity = toUpdateEntity(value, targetPropertyType);
                    writeMethod.invoke(target, nestedEntity);
                } catch (IllegalArgumentException e) {
                    // 嵌套转换失败时，记录警告并跳过该属性
                    log.warn("嵌套对象转换失败，跳过属性 [{}]: {}", writeMethod.getName(), e.getMessage());
                }
            } else if (targetPropertyType.isAssignableFrom(sourceValueType)) {
                // 简单类型或兼容类型，直接赋值
                writeMethod.invoke(target, value);
            }
        }
    }

    /**
     * 判断是否为简单类型
     * <p>
     * 简单类型包括：基本类型、包装类型、String、枚举、java.util.Date、java.time.* 等
     */
    private static boolean isSimpleType(final @Nonnull Class<?> clazz) {
        return clazz.isPrimitive()
                || clazz.getName().startsWith("java.lang.")
                || clazz.getName().startsWith("java.time.")
                || clazz.getName().startsWith("java.util.")
                || clazz.isEnum();
    }

}
```
