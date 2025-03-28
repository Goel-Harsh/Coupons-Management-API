# Coupons-Management-API
Coupons Management API for an E-commerce Website

This API provides endpoints to manage and apply coupons for an e-commerce platform. It supports creating, retrieving, updating, deleting, and applying various types of coupons.

## Implemented Cases

### 1. **Coupon Creation**
   - **Cart-wise Coupons**: Coupons that apply to the entire cart if a minimum threshold is met.
     - Example: `{ "type": "cart-wise", "details": { "threshold": 100, "discount": 10 } }`
   - **Product-wise Coupons**: Coupons that apply to specific products in the cart.
     - Example: `{ "type": "product-wise", "details": { "product_id": "123", "discount": 5 } }`
   - **Buy X Get Y (BXGY) Coupons**: Coupons that provide free products when certain quantities of other products are purchased.
     - Example: `{ "type": "bxgy", "details": { "buy_products": [{ "product_id": "123", "quantity": 2 }], "get_products": [{ "product_id": "456", "quantity": 1 }], "repetition_limit": 2 } }`

### 2. **Coupon Retrieval**
   - Retrieve all coupons.
   - Retrieve a specific coupon by its ID.

### 3. **Coupon Update**
   - Update the type and details of an existing coupon by its ID.

### 4. **Coupon Deletion**
   - Delete a specific coupon by its ID.

### 5. **Applicable Coupons**
   - Fetch all applicable coupons for a given cart and calculate the total discount.

### 6. **Apply Coupon**
   - Apply a specific coupon to a cart and return the updated cart with discounted prices.

---

## API Endpoints

### 1. **Create a Coupon**
   - **Endpoint**: `POST /coupons`
   - **Description**: Create a new coupon.
   - **Request Body**:
     ```json
     {
       "type": "cart-wise",
       "details": { "threshold": 100, "discount": 10 }
     }
     ```
   - **Response**:
     ```json
     {
       "message": "Coupon created successfully",
       "coupon": { "id": "unique-id", "type": "cart-wise", "details": { "threshold": 100, "discount": 10 } }
     }
     ```

### 2. **Retrieve All Coupons**
   - **Endpoint**: `GET /coupons`
   - **Description**: Retrieve all available coupons.
   - **Response**:
     ```json
     {
       "coupons": [ { "id": "unique-id", "type": "cart-wise", "details": { "threshold": 100, "discount": 10 } } ]
     }
     ```

### 3. **Retrieve a Coupon by ID**
   - **Endpoint**: `GET /coupons/<id>`
   - **Description**: Retrieve a specific coupon by its ID.
   - **Response**:
     ```json
     {
       "coupon": { "id": "unique-id", "type": "cart-wise", "details": { "threshold": 100, "discount": 10 } }
     }
     ```

### 4. **Update a Coupon**
   - **Endpoint**: `PUT /coupons/<id>`
   - **Description**: Update an existing coupon by its ID.
   - **Request Body**:
     ```json
     {
       "type": "product-wise",
       "details": { "product_id": "123", "discount": 5 }
     }
     ```
   - **Response**:
     ```json
     {
       "message": "Coupon updated successfully",
       "coupon": { "id": "unique-id", "type": "product-wise", "details": { "product_id": "123", "discount": 5 } }
     }
     ```

### 5. **Delete a Coupon**
   - **Endpoint**: `DELETE /coupons/<id>`
   - **Description**: Delete a specific coupon by its ID.
   - **Response**:
     ```json
     {
       "message": "Coupon deleted successfully"
     }
     ```

### 6. **Get Applicable Coupons**
   - **Endpoint**: `POST /applicable-coupons`
   - **Description**: Fetch all applicable coupons for a given cart.
   - **Request Body**:
     ```json
     {
       "cart": {
         "products": [
           { "product_id": "123", "price": 50, "quantity": 2 },
           { "product_id": "456", "price": 30, "quantity": 1 }
         ]
       }
     }
     ```
   - **Response**:
     ```json
     {
       "applicable_coupons": [
         { "coupon_id": "unique-id", "type": "cart-wise", "discount": 10 }
       ]
     }
     ```

### 7. **Apply a Coupon**
   - **Endpoint**: `POST /apply-coupon/<id>`
   - **Description**: Apply a specific coupon to a cart.
   - **Request Body**:
     ```json
     {
       "cart": {
         "products": [
           { "product_id": "123", "price": 50, "quantity": 2 },
           { "product_id": "456", "price": 30, "quantity": 1 }
         ]
       }
     }
     ```
   - **Response**:
     ```json
     {
       "updated_cart": {
         "products": [
           { "product_id": "123", "price": 50, "quantity": 2, "discounted_price": 45 },
           { "product_id": "456", "price": 30, "quantity": 1, "discounted_price": 30 }
         ]
       },
       "total_discount": 10
     }
     ```

---

## Unimplemented Cases

1. **Coupon Expiry Dates**
   - Reason: Time constraints; the current implementation does not handle time-based coupon validity.

2. **Coupon Usage Limits**
   - Reason: Not implemented due to lack of a persistent database to track usage counts.

3. **Stacking Multiple Coupons**
   - Reason: Complexity in calculating combined discounts and ensuring no conflicts between coupons.

4. **Dynamic Discount Percentages**
   - Reason: The current implementation only supports fixed discount amounts, not percentages.

---

## Limitations

1. **In-Memory Storage**: Coupons are stored in memory, so data is lost when the server restarts.
2. **No Authentication**: The API does not include user authentication or authorization.
3. **No Database Integration**: The implementation lacks a persistent database for storing coupons and cart data.
4. **Limited Validation**: The API assumes that the input data is mostly valid and does not perform exhaustive validation.
5. **Performance**: The in-memory approach may not scale well for large datasets or high traffic.

---

## Assumptions

1. **Unique Coupon Details**: Each coupon is unique based on its type and details.
2. **Valid Input Data**: The API assumes that the input JSON payloads are well-formed and contain the required fields.
3. **Single Currency**: All prices and discounts are assumed to be in the same currency.
4. **Static Product Prices**: Product prices in the cart are assumed to remain constant during coupon application.
5. **Repetition Limit for BXGY**: The repetition limit for BXGY coupons is strictly enforced and cannot exceed the specified value.

---

## How to Run

1. Install dependencies:
   ```sh
   pip install flask
2. Run the server:
    ```sh
    flask --app api run
3. Use tools like Postman or curl to interact with the API.
