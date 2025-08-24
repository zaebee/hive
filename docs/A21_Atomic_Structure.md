# Субатомная Структура Молекулы A21_Order_Fulfillment

Этот документ раскрывает внутреннюю структуру "атомов" (компонентов), визуализированных в `A21_Order_Fulfillment_Corrected.svg`. Каждый атом — это не монолит, а композиция из фундаментальных примитивов Hive (`A`ggregates, `T`ransforms, `C`onnectors, `G`enesis Events).

---

## Кластер 1: Order Domain

### Атом: `Cart` (Ядро-Агрегат)

Это ядро, отвечающее за управление корзиной покупателя. Его внутренняя структура реализует священный кодон `C→A→G`.

*   **Примитив `A` (Aggregate):** `CartAggregate`
    *   **Состояние:** `{ items: List<Item>, total_price: float, customer_id: string }`
    *   **Инварианты:** Нельзя добавить товар, которого нет в наличии. Общая стоимость всегда должна быть суммой цен товаров.
*   **Примитив `C` (Connector):** `CartAPI_Handler`
    *   **Назначение:** Принимает HTTP-запросы (например, `POST /cart/add_item`).
    *   **Трансформация:** Преобразует HTTP-запрос в `AddItemCommand`.
*   **Примитив `G` (Genesis Event):**
    *   **События:** `ItemAddedToCartEvent`, `CartCheckedOutEvent`. Эти события генерируются `CartAggregate` после успешной обработки команды.

### Атом: `Payment` (Ядро-Агрегат)

Отвечает за обработку платежей.

*   **Примитив `A` (Aggregate):** `PaymentAggregate`
    *   **Состояние:** `{ amount: float, status: 'pending' | 'success' | 'failed', transaction_id: string }`
    *   **Инварианты:** Нельзя обработать платеж на нулевую сумму.
*   **Связь:** Получает `CartCheckedOutEvent` от атома `Cart`, который триггерит `ProcessPaymentCommand`.

### Атом: `Inventory` (Ядро-Агрегат)

Отвечает за проверку и резервирование товара на складе.

*   **Примитив `A` (Aggregate):** `InventoryAggregate`
    *   **Состояние:** `{ sku: string, stock_level: int, reservations: Map<order_id, int> }`
    *   **Инварианты:** `stock_level` не может быть отрицательным.
*   **Связь:** Реагирует на `AddItemCommand` (полученный от `Cart`), чтобы проверить наличие товара.

### Атом: `PaymentGW` (Адаптер)

Это адаптер к внешнему платежному шлюзу. Его структура реализует кодон `C→T→C`.

*   **Примитив `C` (Connector):** `ExternalGatewayConnector`
    *   **Назначение:** Отправляет HTTP-запросы к API внешнего шлюза (например, Stripe).
*   **Примитив `T` (Transform):** `PaymentDataTransformer`
    *   **Назначение:** Преобразует внутреннюю структуру данных о платеже в формат, требуемый внешним API, и наоборот.
