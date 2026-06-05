# OptionalField 源码实现

本文档包含 `OptionalField` 三态值类型的核心实现代码。

## OptionalField 类

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
 *     <td>{@link State#VALUE}</td>
 *     <td>字段存在且有有效值</td>
 *     <td>{@code {"age": 25}}</td>
 *   </tr>
 *   <tr>
 *     <td>{@link State#NULL}</td>
 *     <td>字段存在但值为 {@code null}</td>
 *     <td>{@code {"age": null}}</td>
 *   </tr>
 *   <tr>
 *     <td>{@link State#MISSING}</td>
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
 * @since 1.0
 * @see State
 * @see java.util.Optional
 */
public class OptionalField<T> {

    /** MISSING 状态的单例，表示字段不存在。 */
    private static final OptionalField<?> MISSING = new OptionalField<>(State.MISSING, null);
    /** NULL 状态的单例，表示字段存在但值为 {@code null}。 */
    private static final OptionalField<?> NULL = new OptionalField<>(State.NULL, null);

    /**
     * 表示 JSON 字段的存在状态。
     *
     * @see #MISSING 字段不存在
     * @see #NULL    字段存在但值为 null
     * @see #VALUE   字段存在且有有效值
     */
    public enum State {
        /** 字段在 JSON 中不存在。 */
        MISSING,
        /** 字段在 JSON 中存在但值为 {@code null}。 */
        NULL,
        /** 字段在 JSON 中存在且有有效值。 */
        VALUE
    }

    private final State state;
    private final T value;

    /**
     * 构造 {@link OptionalField} 实例。
     *
     * @param state 字段状态，不能为 {@code null}
     * @param value 字段值，当状态为 {@link State#VALUE} 时不应为 {@code null}
     */
    private OptionalField(final @Nonnull State state, final @Nullable T value) {
        this.state = state;
        this.value = value;
    }

    /**
     * 创建一个表示字段不存在（MISSING 状态）的 {@link OptionalField} 实例。
     * <p>
     * MISSING 状态表示 JSON 中该字段完全不存在，区别于字段存在但值为 null（{@link #_null()}）。
     * </p>
     *
     * @param <T> 值的类型
     * @return MISSING 状态的 {@link OptionalField} 实例
     */
    @Nonnull
    public static <T> OptionalField<T> missing() {
        // noinspection unchecked
        return (OptionalField<T>) MISSING;
    }

    /**
     * 创建一个表示字段值为 {@code null}（NULL 状态）的 {@link OptionalField} 实例。
     * <p>
     * NULL 状态表示 JSON 中该字段存在但显式设置为 {@code null}，区别于字段不存在（{@link #missing()}）。
     * </p>
     *
     * @param <T> 值的类型
     * @return NULL 状态的 {@link OptionalField} 实例
     */
    @Nonnull
    public static <T> OptionalField<T> _null() {
        // noinspection unchecked
        return (OptionalField<T>) NULL;
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
            return new OptionalField<>(State.VALUE, value);
        }
    }

    /**
     * 根据给定的 {@link OptionalField} 创建实例。
     * <ul>
     *   <li>如果 {@code field} 为 {@code null}，返回 {@link #missing()}（MISSING 状态）</li>
     *   <li>如果 {@code field} 非 {@code null}，直接返回该字段</li>
     * </ul>
     * <p>
     * 此方法通常用于将可能为 {@code null} 的 {@link OptionalField} 转换为安全的非 null 实例。
     * </p>
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

    /**
     * 获取当前字段的状态。
     *
     * @return 字段的状态，不会为 {@code null}
     * @see State
     */
    public State getState() {
        return state;
    }

    /**
     * 获取字段的值。
     * <p>
     * 注意：如果状态为 {@link State#MISSING} 或 {@link State#NULL}，返回 {@code null}。
     * 建议使用 {@link #orElse(Object)} 或 {@link #orElseThrow()} 等方法安全地获取值。
     * </p>
     *
     * @return 字段的值，可能为 {@code null}
     */
    public T getValue() {
        return value;
    }

    /**
     * 判断字段是否存在有效值（VALUE 状态）。
     *
     * @return 如果字段状态为 {@link State#VALUE}，返回 {@code true}；否则返回 {@code false}
     */
    public boolean isPresent() {
        return state == State.VALUE;
    }

    /**
     * 判断字段的值是否为 {@code null}（NULL 状态）。
     * <p>
     * NULL 状态表示 JSON 中该字段存在但显式设置为 {@code null}。
     * </p>
     *
     * @return 如果字段状态为 {@link State#NULL}，返回 {@code true}；否则返回 {@code false}
     */
    public boolean isNull() {
        return state == State.NULL;
    }

    /**
     * 判断字段是否不存在（MISSING 状态）。
     * <p>
     * MISSING 状态表示 JSON 中该字段完全不存在。
     * </p>
     *
     * @return 如果字段状态为 {@link State#MISSING}，返回 {@code true}；否则返回 {@code false}
     */
    public boolean isMissing() {
        return state == State.MISSING;
    }

    /**
     * 判断当前字段是否为空（即不存在或显式为 null）。
     * <p>
     * 语义上等价于 {@code !isPresent()}，但提供了更具可读性的表达方式。
     * </p>
     *
     * @return 如果字段状态为 {@link State#MISSING} 或 {@link State#NULL}，返回 {@code true}；
     * 否则返回 {@code false}
     */
    public boolean isEmpty() {
        return !isPresent();
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
     * 将字段的值转换为 {@link Stream}。
     * <p>
     * 如果字段状态为 {@link State#VALUE} 且值不为 {@code null}，返回包含该值的单元素流；否则返回空流。
     * </p>
     *
     * @return 包含字段值的 {@link Stream}，不会为 {@code null}
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
     * 获取字段的值，如果值不存在则返回指定的默认值。
     * <p>
     * 无论字段状态为 {@link State#MISSING} 还是 {@link State#NULL}，都返回 {@code other}。
     * </p>
     *
     * @param other 值不存在时的默认值，可以为 {@code null}
     * @return 字段的值（如果存在）；否则返回 {@code other}
     */
    public T orElse(final @Nullable T other) {
        return orElse(other, other);
    }

    /**
     * 获取字段的值，根据不同的无值状态分别返回不同的默认值。
     * <p>
     * 与 {@link #orElse(Object)} 不同的是，此方法允许区分 NULL 和 MISSING 两种状态，分别提供不同的默认值。
     * </p>
     *
     * @param otherInNull    字段值为 {@code null}（NULL 状态）时的默认值
     * @param otherInMissing 字段不存在（MISSING 状态）时的默认值
     * @return 根据字段状态返回对应的值
     */
    public T orElse(final T otherInNull, final T otherInMissing) {
        return switch (state) {
            case VALUE -> value;
            case NULL -> otherInNull;
            case MISSING -> otherInMissing;
        };
    }

    /**
     * 如果字段存在有效值，则返回该值；否则抛出 {@link NoSuchElementException}。
     * <p>
     * 与 {@link java.util.Optional#get()} 语义一致，适用于确定值存在的场景。
     * </p>
     *
     * @return 有效值
     * @throws NoSuchElementException 如果字段不存在有效值
     */
    @Nonnull
    public T orElseThrow() {
        if (isPresent()) {
            assert value != null;
            return value;
        }
        throw new NoSuchElementException("No value present");
    }

    /**
     * 如果字段存在有效值，则返回该值；否则抛出异常。
     * <p>
     * 适用于业务上确定值必须存在的场景，避免手动编写 if-throw 模式。
     * </p>
     * <p>
     * 典型使用场景：
     * <pre>{@code
     * // 业务上确定 name 字段一定存在
     * String name = record.getOptionalName()
     *         .orElseThrow(() -> new IllegalStateException("name 字段缺失"));
     * }</pre>
     * </p>
     *
     * @return 有效值
     * @throws X 如果字段不存在有效值
     */
    @Nonnull
    public <X extends Throwable> T orElseThrow(final @Nonnull Supplier<? extends X> exceptionSupplier) throws X {
        if (isPresent()) {
            assert value != null;
            return value;
        }
        throw exceptionSupplier.get();
    }

    /**
     * 获取字段的值，如果值不存在则通过 {@link Supplier} 延迟计算默认值。
     * <p>
     * 与 {@link #orElse(Object)} 类似，但默认值是延迟计算的，适用于默认值创建成本较高的场景。
     * </p>
     *
     * @param supplier 值不存在时用于生成默认值的供应者，不能为 {@code null}
     * @return 字段的值（如果存在）；否则返回 {@code supplier} 提供的值
     * @throws NullPointerException 如果 {@code supplier} 为 {@code null}
     */
    public T orElseGet(final @Nonnull Supplier<? extends T> supplier) {
        return orElseGet(supplier, supplier);
    }

    /**
     * 获取字段的值，根据不同的无值状态分别通过 {@link Supplier} 延迟计算默认值。
     *
     * @param supplierInNull    字段值为 {@code null}（NULL 状态）时的默认值供应者
     * @param supplierInMissing 字段不存在（MISSING 状态）时的默认值供应者
     * @return 根据字段状态返回对应的值
     * @throws NullPointerException 如果任一供应者为 {@code null}
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
     * 如果字段存在有效值，则执行给定的操作。
     * <p>
     * 与 {@code if (field.isPresent()) consumer.accept(field.get())} 等价，
     * 但更简洁且表达意图更清晰。
     * </p>
     * <p>
     * 典型使用场景：
     * <pre>{@code
     * record.getOptionalName().ifPresent(name -> log.info("Name: {}", name));
     * }</pre>
     * </p>
     *
     * @param action 要执行的操作，不能为 {@code null}
     * @throws NullPointerException 如果 {@code action} 为 {@code null}
     */
    public void ifPresent(final @Nonnull Consumer<? super T> action) {
        Objects.requireNonNull(action);
        if (isPresent()) {
            action.accept(value);
        }
    }

    /**
     * 如果字段值为 {@code null}（NULL 状态），则执行给定的操作。
     * <p>
     * 典型使用场景：
     * <pre>{@code
     * record.getOptionalName()
     *         .ifNull(() -> log.warn("Name is explicitly null"));
     * }</pre>
     * </p>
     *
     * @param action 值为 null 时要执行的操作，不能为 {@code null}
     * @throws NullPointerException 如果 {@code action} 为 {@code null}
     * @since 1.0
     */
    public void ifNull(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        if (isNull()) {
            action.run();
        }
    }

    /**
     * 如果字段不存在（MISSING 状态），则执行给定的操作。
     * <p>
     * 典型使用场景：
     * <pre>{@code
     * record.getOptionalName()
     *         .ifMissing(() -> log.warn("Name field not present in JSON"));
     * }</pre>
     * </p>
     *
     * @param action 字段不存在时要执行的操作，不能为 {@code null}
     * @throws NullPointerException 如果 {@code action} 为 {@code null}
     * @since 1.0
     */
    public void ifMissing(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        if (isMissing()) {
            action.run();
        }
    }

    /**
     * 如果字段"为空"（NULL 或 MISSING 状态），则执行给定的操作。
     * <p>
     * 此方法将 NULL 和 MISSING 视为统一的"空"状态，适用于需要统一处理无值场景的情况。
     * </p>
     * <p>
     * 典型使用场景：
     * <pre>{@code
     * record.getOptionalName()
     *         .ifEmpty(() -> log.warn("Name is not available (null or missing)"));
     * }</pre>
     * </p>
     *
     * @param action 字段为空时要执行的操作，不能为 {@code null}
     * @throws NullPointerException 如果 {@code action} 为 {@code null}
     * @since 1.0
     */
    public void ifEmpty(final @Nonnull Runnable action) {
        Objects.requireNonNull(action);
        if (isEmpty()) {
            action.run();
        }
    }

    /**
     * 根据字段状态执行对应的分支操作（双分支，忽略 MISSING 状态）。
     * <p>
     * 如果字段处于 VALUE 状态，执行 {@code present}；如果处于 NULL 状态，执行 {@code nullValue}。
     * MISSING 状态不执行任何操作。
     * </p>
     *
     * @param present   字段有值时的操作
     * @param nullValue 字段值为 null 时的操作
     * @throws NullPointerException 如果任一参数为 {@code null}
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
     * 根据字段状态执行对应的分支操作（三分支）。
     *
     * @param present   字段有值时的操作
     * @param nullValue 字段值为 null 时的操作
     * @param missing   字段不存在时的操作
     * @throws NullPointerException 如果任一参数为 {@code null}
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
     * 根据字段状态执行对应的映射函数并返回结果（三分支，带返回值）。
     *
     * @param <R>       返回值类型
     * @param present   字段有值时的映射函数
     * @param nullValue 字段值为 null 时的值供应者
     * @param missing   字段不存在时的值供应者
     * @return 根据字段状态返回对应的映射结果
     * @throws NullPointerException 如果任一参数为 {@code null}
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
     * 如果字段存在有效值，则对其应用映射函数并返回新的 {@link OptionalField}。
     * <p>
     * 如果字段处于 NULL 或 MISSING 状态，直接返回当前实例（类型转换）。
     * </p>
     *
     * @param <U>    映射后的值类型
     * @param mapper 映射函数，不能为 {@code null}
     * @return 映射后的新 {@link OptionalField} 实例
     * @throws NullPointerException 如果 {@code mapper} 为 {@code null}
     */
    @Nonnull
    public <U> OptionalField<U> map(final @Nonnull Function<? super T, ? extends U> mapper) {
        Objects.requireNonNull(mapper);
        if (isPresent()) {
            return OptionalField.of(mapper.apply(value));
        }
        // noinspection unchecked
        return (OptionalField<U>) this;
    }

    /**
     * 如果字段存在有效值，则对其应用返回 {@link OptionalField} 的映射函数（展平嵌套）。
     * <p>
     * 与 {@link #map(Function)} 不同的是，此方法的映射函数本身返回 {@link OptionalField}，
     * 避免产生 {@code OptionalField<OptionalField<T>>} 的嵌套结构。
     * </p>
     *
     * @param <U>    映射后的值类型
     * @param mapper 映射函数，返回 {@link OptionalField}，不能为 {@code null}
     * @return 映射后的 {@link OptionalField} 实例
     * @throws NullPointerException 如果 {@code mapper} 或其返回值为 {@code null}
     */
    @Nonnull
    public <U> OptionalField<U> flatMap(final @Nonnull Function<? super T, ? extends OptionalField<? extends U>> mapper) {
        Objects.requireNonNull(mapper);
        if (isPresent()) {
            // noinspection unchecked
            final OptionalField<U> r = (OptionalField<U>) mapper.apply(value);
            return Objects.requireNonNull(r);
        }
        // noinspection unchecked
        return (OptionalField<U>) this;
    }

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
     * <p>
     * 典型使用场景：
     * <pre>{@code
     * // 获取有效邮箱，过滤掉无效格式
     * OptionalField<String> validEmail = record.getOptionalEmail()
     *         .filter(email -> email.contains("@"));
     * // 如果 email 存在但格式不对，validEmail 状态为 NULL（而非 MISSING）
     * // 如果 email 字段本身不存在，validEmail 状态仍为 MISSING
     * }</pre>
     * </p>
     *
     * @param predicate 谓词条件，不能为 {@code null}
     * @return 值存在且满足谓词返回当前字段；值存在但不满足返回 {@link #_null()}；值不存在返回 {@link #missing()}
     * @throws NullPointerException 如果 {@code predicate} 为 {@code null}
     */
    @Nonnull
    public OptionalField<T> filter(final @Nonnull Predicate<? super T> predicate) {
        Objects.requireNonNull(predicate);
        if (isPresent()) {
            return predicate.test(value) ? this : _null();
        }
        return this; // MISSING 状态保持不变
    }

}
```

## OptionalDtoUtil 工具类

```java
package com.example.json.lang;

import com.mybatisflex.core.update.UpdateChain;
import com.mybatisflex.core.update.UpdateEntity;

import java.lang.reflect.Field;
import java.util.Objects;

/**
 * OptionalField DTO 转换工具类
 *
 * @author DevilSpiderX
 */
public class OptionalDtoUtil {

    private OptionalDtoUtil() {
    }

    /**
     * 将包含 OptionalField 字段的 DTO 转换为 UpdateEntity
     *
     * @param dto     DTO 对象
     * @param clazz   实体类
     * @param id      实体 ID
     * @param <T>     实体类型
     * @return UpdateEntity 实例
     */
    public static <T> T toUpdateEntity(Object dto, Class<T> clazz, Object id) {
        T entity = UpdateEntity.of(clazz, id);
        Field[] fields = dto.getClass().getDeclaredFields();

        for (Field field : fields) {
            field.setAccessible(true);
            try {
                Object value = field.get(dto);
                if (value instanceof OptionalField<?> optionalField) {
                    String fieldName = field.getName();
                    Field entityField = findField(clazz, fieldName);

                    if (entityField != null) {
                        entityField.setAccessible(true);
                        optionalField.match(
                            v -> {
                                try {
                                    entityField.set(entity, v);
                                } catch (IllegalAccessException e) {
                                    throw new RuntimeException(e);
                                }
                            },
                            () -> {
                                try {
                                    entityField.set(entity, null);
                                } catch (IllegalAccessException e) {
                                    throw new RuntimeException(e);
                                }
                            },
                            () -> {} // MISSING: 不设置
                        );
                    }
                }
            } catch (IllegalAccessException e) {
                throw new RuntimeException(e);
            }
        }

        return entity;
    }

    /**
     * 将包含 OptionalField 字段的 DTO 应用到 UpdateChain
     *
     * @param dto   DTO 对象
     * @param chain UpdateChain 实例
     */
    public static void applyToChain(Object dto, UpdateChain<?> chain) {
        Field[] fields = dto.getClass().getDeclaredFields();

        for (Field field : fields) {
            field.setAccessible(true);
            try {
                Object value = field.get(dto);
                if (value instanceof OptionalField<?> optionalField) {
                    String fieldName = field.getName();
                    optionalField.match(
                        v -> chain.set(fieldName, v),
                        () -> chain.set(fieldName, null),
                        () -> {} // MISSING: 不设置
                    );
                }
            } catch (IllegalAccessException e) {
                throw new RuntimeException(e);
            }
        }
    }

    private static Field findField(Class<?> clazz, String fieldName) {
        Class<?> current = clazz;
        while (current != null && current != Object.class) {
            try {
                return current.getDeclaredField(fieldName);
            } catch (NoSuchFieldException e) {
                current = current.getSuperclass();
            }
        }
        return null;
    }
}
```
