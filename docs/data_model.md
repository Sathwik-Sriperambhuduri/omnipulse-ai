# Phase 2 Data Model

The Phase 2 model combines **transactional data** (customers buying products)
with **behavioral data** (visitors browsing the store) and supporting business
data such as inventory and marketing campaigns.

## Keys in plain language

A **primary key** is a column whose value uniquely identifies a row. For
example, no two rows in `orders.csv` share an `order_id`.

A **foreign key** stores the primary key of a related row. For example, an
order's `customer_id` points to the customer who placed it. The generator never
creates a foreign key that points to a missing parent row. In clickstream data,
a foreign key may be blank when the visitor is anonymous or the event does not
concern a particular product.

## Relationship diagram

The `1` side is the parent; the `many` side can contain several related rows.

```text
customers (1) --------< orders (many)
    |                      |
    |                      +--------< payments (many*)
    |                      |
    |                      +--------< order_items (many) >-------- (1) products
    |                      |                                      /       |
    +----------------------|----< reviews (many) <---------------+        |
    |                                                              inventory (many)
    |
    +--------< clickstream_events (many) >---------------------- (1) products

marketing_campaigns  (standalone campaign summaries)

* Phase 2 currently generates one payment row per order, while the model can
  naturally support multiple attempts in a future phase.
```

## One-to-many relationships

- One customer can place many orders; each order belongs to one customer.
- One order contains one or more order items; each item belongs to one order.
- One product can occur in many order items; each item refers to one product.
- One order currently has one payment record.
- One customer, order, or product can be connected to many reviews over time.
- One product can have inventory records in several warehouses.
- One known customer can produce many clickstream events.
- One product can be referenced by many product-specific clickstream events.

Reviews have three foreign keys because all three facts matter: who wrote the
review, which order proves the purchase, and which product was reviewed. The
generator additionally checks that the reviewed product was an item in that
specific order.

## Why `order_items` is separate from `orders`

An order can contain several products, each with its own quantity, price, and
discount. Putting product columns directly on the order would require awkward
fields such as `product_1`, `product_2`, and `product_3`, and would impose an
arbitrary limit. Keeping item rows separately allows any number of products
without repeating order-level details such as the shipping address.

The totals still reconcile:

```text
line_total  = quantity × unit_price − line discount
order_total = sum(line_total) + shipping_cost + tax_amount
```

The order's `discount_amount` is the sum of its item-level discounts.

## Transactional data versus clickstream data

Transactional rows represent durable business facts: a registered customer
placed an order, paid an amount, or reviewed a purchase. They are structured,
relatively low-volume, and usually require complete identifiers.

Clickstream rows are a chronological event log. A single visit can create many
events, most visits never become orders, and anonymous visitors are normal. The
event sequence helps explain a browsing funnel—for example, `page_view`, then
`product_view`, then `add_to_cart`—without claiming that every sequence ends in
a purchase. This is why clickstream customer and product keys are nullable and
why clickstream belongs in its own dataset.
