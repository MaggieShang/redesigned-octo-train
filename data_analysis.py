import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.backends.backend_pdf import PdfPages
from textwrap import fill

fig_size = (11.69,8.27)
pdf_path = './analysis_report.pdf'
with PdfPages(pdf_path) as pdf:

    #ABC analysis 计算总额，分类，分类标准：前40%A， 中间40%B，20%C
    def ABC_analysis():
        # 步骤1: 加载订单数据
        file_path = './orders.csv'
        df = pd.read_csv(file_path)

        # 步骤2: 计算每个产品的总销售额
        product_sales = df.groupby('product')['total_price'].sum().reset_index()
        
        # 步骤3: 按总销售额降序排列产品
        product_sales = product_sales.sort_values(by='total_price', ascending=False)

        # 步骤4: 计算每个产品的销售额占总销售额的百分比sales proportion
        total_sales = product_sales['total_price'].sum()  # 计算总销售额
        product_sales['percentage'] = round((product_sales['total_price'] / total_sales) * 100, 2)  # 保留两位小数

        # 步骤5: 计算累计销售额百分比
        product_sales['cumulative_sales'] = product_sales['total_price'].cumsum()
        product_sales['cumulative_percentage'] = round((product_sales['cumulative_sales'] / total_sales) * 100, 2)  # 保留两位小数

        # 步骤6: 根据累计销售百分比进行分类
        def categorize_product(percentage):
            if percentage <= 40:
                return 'A'  # 前40%销售额
            elif percentage <= 80:
                return 'B'  # 接下来的40%销售额
            else:
                return 'C'  # 剩余的20%销售额

        product_sales['category'] = product_sales['cumulative_percentage'].apply(categorize_product)

        # 步骤7: 输出结果
        #print(product_sales)

        # 保存结果到新的CSV文件
        product_sales.to_csv('./abc_analysis_results.csv', index=False)

    #ABC_analysis()

    def ABC_analysis_visualization():
        # 加载ABC分析结果
        file_path = './abc_analysis_results.csv'
        abc_data = pd.read_csv(file_path)

        # 可视化1：ABC 类别的产品数量分布bar chart
        plt.figure(figsize=fig_size)
        ax = sns.countplot(data=abc_data, x='category', palette='pastel', order=['A', 'B', 'C'])
        for container in ax.containers:
            ax.bar_label(container, fmt='%d', label_type='edge', fontsize=10, color='black')
        plt.title('Number of Products by ABC Category', fontsize=14)
        plt.xlabel('ABC Category', fontsize=12)
        plt.ylabel('Number of Products', fontsize=12)
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        # 保存图像
        #plt.show()

        # 可视化2：销售额sales proportion占比的饼图
        plt.figure(figsize=fig_size)
        sales_by_category = abc_data.groupby('category')['total_price'].sum()
        sales_by_category.plot.pie(
            autopct='%1.1f%%', labels=['A', 'B', 'C'], colors=['#ff9999', '#66b3ff', '#99ff99'],
            startangle=90, explode=(0.1, 0, 0)
        )
        plt.title('Sales Contribution by ABC Category', fontsize=14)
        plt.ylabel('')  # 隐藏默认的 y 轴标签
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        #plt.show()

        
        # 可视化3：展示所有产品的表格table
        # 创建一个图形和一个坐标轴
        fig,ax = plt.subplots(figsize=fig_size)  # 更大的表格显示区域
        ax.axis('tight')
        ax.axis('off')
        
        # 创建表格，显示所有ABC分析的内容
        table_data = abc_data[['product', 'total_price', 'category', 'percentage', 'cumulative_percentage']]
        table = ax.table(cellText=table_data.values, colLabels=table_data.columns, loc='center', cellLoc='center', colColours=['#f0f0f0']*5)
        
        # 设置表格字体
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        
        # 设置表格单元格颜色
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_fontsize(12)
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#d3d3d3')  # 设置表头颜色
            else:
                cell.set_facecolor('#ffffff')  # 设置数据单元格的背景色

        plt.title('Product Details by ABC Category', fontsize=14)
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
       
        # 结论部分 summerize the conclusion of ABC Analysis
        text_tit = f"ABC Analysis Summary:"
        text_A = f"Category A products contribute the most to revenue, accounting for {abc_data[abc_data['category'] == 'A']['percentage'].sum():.2f}% of total sales. Focus \n on maintaining their availability and improving sales efficiency."
        text_B = f"Category B products contribute moderately, accounting for {abc_data[abc_data['category'] == 'B']['percentage'].sum():.2f}%. Consider exploring growth \n opportunities for these products."
        text_C = f"Category C products contribute the least but are the most numerous. They only contribute {abc_data[abc_data['category'] == 'C']['percentage'].sum():.2f}% \n of total sales. Review these products for potential removal or repositioning."
        plt.subplots(figsize=fig_size)
        plt.text(-0.1,1.0, text_tit, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.9, text_A, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.7, text_B, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.5, text_C, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.axis('off')
        pdf.savefig()  # 保存到 PDF
        plt.close()
        

    #FRM analysis ， 计算\FRM
    def FRM_analysis():
        # 加载顾客数据
        customers_df = pd.read_csv('./customers.csv')

        # 获取当前日期
        current_date = datetime.now()

        # 计算频率（Frequency） - 每个顾客的订单数量
        orders_df = pd.read_csv('./orders.csv')
        frequency = orders_df.groupby('customer_id')['order_id'].count().reset_index(name='frequency')

        # 计算最近性（Recency） - 距离最后一次购买的天数
        customers_df['last_purchase'] = pd.to_datetime(customers_df['last_purchase'])
        customers_df['recency'] = (current_date - customers_df['last_purchase']).dt.days

        # 计算货币（Monetary） - 使用 customers.csv 中的 total_spent
        monetary = customers_df[['customer_id', 'total_spent']]

        # 合并所有数据
        fr_data = frequency.merge(monetary, on='customer_id').merge(customers_df[['customer_id', 'recency']], on='customer_id')

        # 定义frm with low midiem high，先取mean value，再取最小值到mean 到half（分为 3 个区间）
        frequency_bins = [
            fr_data['frequency'].min(),
            (fr_data['frequency'].min() + fr_data['frequency'].mean()) / 2,
            fr_data['frequency'].mean(),
            fr_data['frequency'].max()
        ]
        recency_bins = [
            fr_data['recency'].min(),
            (fr_data['recency'].min() + fr_data['recency'].mean()) / 2,
            fr_data['recency'].mean(),
            fr_data['recency'].max()
        ]
        monetary_bins = [
            fr_data['total_spent'].min(),
            (fr_data['total_spent'].min() + fr_data['total_spent'].mean()) / 2,
            fr_data['total_spent'].mean(),
            fr_data['total_spent'].max()
        ]

        # 使用 pd.cut 分类
        fr_data['Frequency_Category'] = pd.cut(
            fr_data['frequency'],
            bins=frequency_bins,
            labels=['Low', 'Medium', 'High'],
            include_lowest=True
        )
        fr_data['Recency_Category'] = pd.cut(
            fr_data['recency'],
            bins=recency_bins,
            labels=['High', 'Medium', 'Low'],
            include_lowest=True
        )
        fr_data['Monetary_Category'] = pd.cut(
            fr_data['total_spent'],
            bins=monetary_bins,
            labels=['Low', 'Medium', 'High'],
            include_lowest=True
        )

        # 打印输出检查
        #print(fr_data)

        # 保存结果到新的 CSV 文件
        fr_data.to_csv('./frm_analysis_results.csv', index=False)
    #FRM_analysis()


    #FRM Visualization
    def FRM_Visualization():
        # 加载 frm_analysis_results.csv 数据
        file_path = './frm_analysis_results.csv'
        fr_data = pd.read_csv(file_path)

        # 确保 'Frequency_Category', 'Recency_Category', 'Monetary_Category' 是有序的类别
        category_order = ['Low', 'Medium', 'High']  # 设定分类的顺序

        # 将这些列转换为有序的类别数据
        fr_data['Frequency_Category'] = pd.Categorical(fr_data['Frequency_Category'], categories=category_order, ordered=True)
        fr_data['Recency_Category'] = pd.Categorical(fr_data['Recency_Category'], categories=category_order, ordered=True)
        fr_data['Monetary_Category'] = pd.Categorical(fr_data['Monetary_Category'], categories=category_order, ordered=True)

        # Frequency 分类的分布 bar chart
        plt.figure(figsize=fig_size)
        sns.countplot(data=fr_data, x='Frequency_Category', palette='coolwarm', order=category_order)
        plt.title('Frequency Category Distribution')
        plt.xlabel('Frequency Category')
        plt.ylabel('Number of Customers')
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        #plt.show()

        # Recency 分类的分布 bar chart
        plt.figure(figsize=fig_size)
        sns.countplot(data=fr_data, x='Recency_Category', palette='coolwarm', order=category_order)
        plt.title('Recency Category Distribution')
        plt.xlabel('Recency Category')
        plt.ylabel('Number of Customers')
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        #plt.show()

        # Monetary 分类的分布 bar chart
        plt.figure(figsize=fig_size)
        sns.countplot(data=fr_data, x='Monetary_Category', palette='coolwarm', order=category_order)
        plt.title('Monetary Category Distribution')
        plt.xlabel('Monetary Category')
        plt.ylabel('Number of Customers')
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        #plt.show()
        
        # conclusion of FRM,FRM analysis summary
        text_tit = f'FRM analysis summary'
        #low,medium,high = fr_data['Frequency_Category']
        low = len(fr_data[fr_data['Frequency_Category'] == 'Low'])
        medium = len(fr_data[fr_data['Frequency_Category'] == 'Medium'])
        high = len(fr_data[fr_data['Frequency_Category'] == 'High'])
        low,medium,high = low/(low+medium+high),medium/(low+medium+high),high/(low+medium+high)
        low,medium,high = round(low*10000)/100,round(medium*10000)/100,round(high*10000)/100
        text_A = f'Accoring to the Frequency Category Distribution, Low-Frequency customers takes {low}%, Medium \n -Frequency customers takes {medium}%, and High-Frequency customers takes {medium}%.'
        low = len(fr_data[fr_data['Recency_Category'] == 'Low'])
        medium = len(fr_data[fr_data['Recency_Category'] == 'Medium'])
        high = len(fr_data[fr_data['Recency_Category'] == 'High'])
        low,medium,high = low/(low+medium+high),medium/(low+medium+high),high/(low+medium+high)
        low,medium,high = round(low*10000)/100,round(medium*10000)/100,round(high*10000)/100
        text_B = f'Accoring to the Recency Category Distribution, Low-Recency customers takes {low}%, Medium \n -Recency customers takes {medium}%, and High-Recency customers takes {medium}%.'
        low = len(fr_data[fr_data['Monetary_Category'] == 'Low'])
        medium = len(fr_data[fr_data['Monetary_Category'] == 'Medium'])
        high = len(fr_data[fr_data['Monetary_Category'] == 'High'])
        low,medium,high = low/(low+medium+high),medium/(low+medium+high),high/(low+medium+high)
        low,medium,high = round(low*10000)/100,round(medium*10000)/100,round(high*10000)/100
        text_C = f'Accoring to the Monetary Category Distribution, Low-Monetary customers takes {low}%, Medium \n -Monetary customers takes {medium}%, and High-Monetary customers takes {medium}%.'
        plt.subplots(figsize=fig_size)
        plt.text(-0.1,1.0, text_tit, fontsize=20, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.9, text_A, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.7, text_B, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.5, text_C, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.axis('off')
        pdf.savefig()  # 保存到 PDF
        plt.close()

    #FRM_Visualization()


    #classify_customer to different types and visualization
    def class_customer():
        # 加载 frm_analysis_results.csv 数据
        file_path = 'frm_analysis_results.csv'
        fr_data = pd.read_csv(file_path)

        # 定义顾客分类规则
        def classify_customer(row):
            if row['Frequency_Category'] == 'High' and row['Recency_Category'] == 'High' and row['Monetary_Category'] == 'High':
                return 'Loyal & High-Value Customers'  # 高频次、最近且高消费的顾客
            elif row['Frequency_Category'] == 'High' and row['Recency_Category'] == 'Low' and row['Monetary_Category'] == 'High':
                return 'At-Risk High-Value Customers'  # 高频次、低近期且高消费的顾客
            elif row['Frequency_Category'] == 'Low' and row['Recency_Category'] == 'High' and row['Monetary_Category'] == 'High':
                return 'Potential High-Value Customers'  # 低频次、高近期且高消费的顾客
            elif row['Frequency_Category'] == 'High' and row['Recency_Category'] == 'High' and row['Monetary_Category'] == 'Low':
                return 'Frequent but Low-Value Customers'  # 高频次、近期且低消费的顾客
            elif row['Frequency_Category'] == 'Low' and row['Recency_Category'] == 'Low' and row['Monetary_Category'] == 'Low':
                return 'Inactive & Low-Value Customers'  # 低频次、低近期且低消费的顾客
            else:
                return 'Other Customers'  # 其他类型顾客

        # 添加分类列
        fr_data['Customer_Segment'] = fr_data.apply(classify_customer,axis=1)

        # 保存分类结果到新的 CSV 文件
        output_path = 'customer_segmentation_results.csv'
        fr_data.to_csv(output_path, index=False)
        #print(f"分类结果已保存到 {output_path}")

    #class_customer()


    #class customer visualization
    def class_customer_visualization():
        # 加载分类结果数据
        file_path = 'customer_segmentation_results.csv'
        fr_data = pd.read_csv(file_path)

        # 顾客分类分布 bar chart
        plt.figure(figsize=fig_size)
        ax = sns.countplot(
            data=fr_data,
            y='Customer_Segment',
            palette='Set2',
            order=['Loyal & High-Value Customers', 'At-Risk High-Value Customers', 'Potential High-Value Customers','Frequent but Low-Value Customers', 'Inactive & Low-Value Customers', 'Other Customers']  # 更新类别顺序
        )

        # 添加数据标签
        for container in ax.containers:
            ax.bar_label(container, fmt='%d', label_type='edge', fontsize=10, color='black')

        # 设置标题和轴标签
        plt.subplots_adjust(left=0.25, right=0.9)
        plt.title('Customer Segmentation Distribution', fontsize=14)
        plt.xlabel('Number of Customers', fontsize=12)
        plt.ylabel('Customer Segment', fontsize=12)
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        # 展示图像
        #plt.show()
        
        #结论根据顾客分类制定不同政策。
        C1 = fr_data[fr_data['Customer_Segment'] == 'Loyal & High-Value Customers'].shape[0]
        C2 = fr_data[fr_data['Customer_Segment'] == 'At-Risk High-Value Customers'].shape[0]
        C3 = fr_data[fr_data['Customer_Segment'] == 'Potential High-Value Customers'].shape[0]
        C4 = fr_data[fr_data['Customer_Segment'] == 'Frequent but Low-Value Customers'].shape[0]
        C5 = fr_data[fr_data['Customer_Segment'] == 'Inactive & Low-Value Customers'].shape[0]
        C6 = fr_data[fr_data['Customer_Segment'] == 'Other Customers'].shape[0]
        text_tit = f'Formulate consumer policies'
        text_content = f'Accoring to the Customer Segmentation Distribution. \n \n For Loyal & High-Value Customers (total number is {C1}) we should, \n a.special offers, special discounts, and VIP memberships. b.offer new products tasting coupons. \n \n For At-Risk High-Value Customers (total number is {C2}) we should, \n a.offer time-sensitive offers. b.solve concerns through feedback. \n \n For Potential High-Value Customers (total number is {C3}) we should, \n a.offer special coupons. b.Granting special membership privileges. \n \n For Frequent but Low-Value Customers (total number is {C4}) we should,\n offer bundled offers and high-value coupons. \n \n For Inactive & Low-Value Customers (total number is {C5}) we should, \n a.offer discounts or “We miss you!” emails. b.automation to reduce engagement costs. \n \n For Other Customers (total number is {C6}) we should, \n a.oreduce marketing efforts. b.analyze behavior to identify potential. \n c. offer general promotions'
        plt.subplots(figsize=fig_size)
        plt.text(-0.1,1.0, text_tit, fontsize=20, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.9, text_content, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.axis('off')
        pdf.savefig()  # 保存到 PDF
        plt.close()
        
    #class_customer_visualization()


    #根据月份统计月销售额，并分类淡旺季peak_season，off_season
    def sales_trend_analysis():
        file_path = './orders.csv'
        
        # 加载文件
        df = pd.read_csv(file_path)

        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])  # 确保日期列是 datetime 类型
        df['month'] = df['date'].dt.to_period('M')  # 提取月份
        
        # 按月统计销售额
        monthly_sales = df.groupby('month')['total_price'].sum().reset_index()

        # 可视化：按月销售额趋势 line chart
        plt.figure(figsize=fig_size)
        plt.plot(monthly_sales['month'].astype(str), monthly_sales['total_price'], marker='o')
        plt.title('Monthly Sales Trend', fontsize=14)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Total Sales', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid()
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        
        #设置淡旺季规则，月销售额小于四分之一的是淡季，四分之三以上是旺季
        total_sales = monthly_sales['total_price'].tolist()
        sales_cut_low = min(total_sales)+(max(total_sales)-min(total_sales))/4
        sales_cut_high = min(total_sales)+(max(total_sales)-min(total_sales))/4*3
        peak_season = [] ; off_season = []
        for i in [1,2,3,4,5,6,7,8,9,10,11,12]:
            if total_sales[i-1] >= sales_cut_high: peak_season.append(i)
            if total_sales[i-1] <= sales_cut_low: off_season.append(i)
        peak_season = ", ".join(map(str,peak_season))
        off_season = ", ".join(map(str,off_season))
        
        #结论Summary of sales months，并根据去年的淡旺季制定政策
        text_tit = f'Summary of sales months'
        text_A = f'According to the Monthly Sales Trend, the peak sales month(s) is(are): {peak_season}, and the \n off sales month(s) is(are): {off_season}.'
        text_B = f'Policy recommendations: Based on the monthly sales of this year, we recommend referring to \n this analysis and adjusting the monthly purchase volume for the next year.'
        plt.subplots(figsize=fig_size)
        plt.text(-0.1,1.0, text_tit, fontsize=20, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.9, text_A, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.text(-0.1,0.7, text_B, fontsize=15, ha='left', va='top', linespacing=1.5)
        plt.axis('off')
        pdf.savefig()  # 保存到 PDF
        plt.close()
        plt.show()

    #计算相同购买次数的顾客数量，并生成柱状图
    def visualize_repeat_purchases():
        # 加载订单数据
        file_path = './orders.csv'
        df = pd.read_csv(file_path)

        # 计算每位顾客的购买次数
        purchase_counts = df.groupby('customer_id')['order_id'].count().reset_index(name='purchase_count')

        # 计算平均购买次数（红线是平均购买次数）
        avg_purchase_count = purchase_counts['purchase_count'].mean()

        # 可视化：购买次数的分布
        plt.figure(figsize=fig_size)
        sns.histplot(purchase_counts['purchase_count'], bins=20, kde=False, color='skyblue')

        # 添加平均购买次数的直线
        plt.axvline(avg_purchase_count, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_purchase_count:.2f}')

        # 图表标题和标签
        plt.title('Distribution of Customer Purchase Counts', fontsize=14)
        plt.xlabel('Number of Purchases', fontsize=12)
        plt.ylabel('Number of Customers', fontsize=12)
        plt.legend()  # 显示图例
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        pdf.savefig()  # 保存当前图到PDF
        plt.close()
        # 展示图表
        #plt.show()
        

    #ABC_analysis()
    #ABC_analysis_visualization()
    #FRM_analysis()
    #FRM_Visualization()
    #class_customer()
    #class_customer_visualization()

    #sales_trend_analysis()
    #visualize_repeat_purchases()
    
    # 创建标题页函数
    def add_title_page():
        plt.figure(figsize=(11.69, 8.27))  # 设置纸张大小为 A4
        plt.text(
            0.5, 0.5,  # 坐标：居中显示
            "Coffee Point Data Analysis Report",  # 标题内容
            fontsize=37,  # 字体大小
            ha='center',  # 水平居中
            va='center'   # 垂直居中
        )
        plt.axis('off')  # 关闭轴线
        pdf.savefig()  # 保存到 PDF
        plt.close()


    def save_report_to_pdf():
        add_title_page()
        ABC_analysis()
        ABC_analysis_visualization()
        FRM_analysis()
        FRM_Visualization()
        class_customer()
        
        sales_trend_analysis()
        visualize_repeat_purchases()
        class_customer_visualization()
        
        print(f"report save in {pdf_path}")

    save_report_to_pdf()







