import csv
import random
from tqdm import tqdm
from datetime import datetime, timedelta

# 初始化产品信息和定价
products = {
    'Espresso': 8, 'Americano': 10, 'Cappuccino': 12, 'Latte': 13, 'Flat White': 14,
    'Mocha': 15, 'Affogato': 14, 'Cold Brew': 16, 'Polish-Style Coffee': 15,
    'Matcha Latte': 18, 'Hot Chocolate': 14, 'Coconut Iced Coffee': 17,
    'Nutty Chocolate Cake': 12, 'Polish Cheesecake': 15, 'Mini Almond Cookie Set': 8
}

# 生成日期范围
start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2024-12-31', '%Y-%m-%d')
date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

# 生成顾客数据
customers = [{'customer_id': i, 'last_purchase': random.choice(date_range), 'total_spent': 0.0} for i in range(1, 5001)]

# 生成订单数据
orders = []
order_quantity_by_product = {product: 0 for product in products}  # 用于记录每个产品的总销售数量

for i in tqdm(range(1,100001)):
    product = random.choice(list(products.keys()))
    quantity = random.randint(1,5)
    unit_price = products[product]
    total_price = round(quantity * unit_price,2)
    customer_id = random.randint(1, 5000)  # 随机选择一个顾客
    
    # 将订单数据添加到订单列表中
    orders.append({
        'order_id': i, 'date': random.choice(date_range), 'quantity': quantity,
        'product': product, 'unit_price': unit_price, 'total_price': total_price,
        'customer_id': customer_id
    })
    
    # 更新对应顾客的 total_spent
    for customer in customers:
        if customer['customer_id'] == customer_id:
            customer['total_spent'] += total_price
    
    # 更新每个产品的销售数量
    order_quantity_by_product[product] += quantity

# 生成库存数据，确保库存量足够
inventory = []
for product in products:
    # 为了确保库存量大于销售数量，库存量至少为销售数量的1到1.5倍
    required_inventory = order_quantity_by_product[product]
    inventory_multiplier = random.uniform(1, 1.5)  # 生成一个在1到1.5之间的随机数
    inventory_quantity = int(required_inventory * inventory_multiplier)
    
    inventory.append({
        'product': product,
        'units_in_stock': inventory_quantity,  # 设置库存量
        'category': 'Beverage' if product in products else 'Dessert'
    })

# 写入 CSV 文件
def write_to_csv(filename, fieldnames, data):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# 保存数据
write_to_csv('customers.csv', ['customer_id', 'last_purchase', 'total_spent'], customers)
write_to_csv('inventory.csv', ['product', 'units_in_stock', 'category'], inventory)
write_to_csv('orders.csv', ['order_id', 'date', 'quantity', 'product', 'unit_price', 'total_price', 'customer_id'], orders)

print("Data generation complete. Files saved: customers.csv, inventory.csv, orders.csv")
