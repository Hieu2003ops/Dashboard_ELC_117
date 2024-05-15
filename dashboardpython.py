import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Dashboard Python nhóm 117", layout="wide")

# Function to load data with caching to improve performance
@st.cache_data
def load_data(file_name, sheet_name):
    return pd.read_excel(file_name, sheet_name=sheet_name)
def main():
    # Load data
    data = load_data('ELC_117.xlsx', 'Data_full')

    # Create header in the center
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 60px;'>Dashboard Nhóm 117</h1>", unsafe_allow_html=True)

    # Create button-based tabs
        if 'current_tab' not in st.session_state:
            st.session_state['current_tab'] = 'Tab 1'

    # Create button-based tabs
    tabs = ["Tab 1", "Tab 2", "Tab 3", "Tab 4", "Tab 5"]
    tab_buttons = st.columns(len(tabs))
    for i, button in enumerate(tab_buttons):
        if button.button(tabs[i]):
            st.session_state['current_tab'] = tabs[i]

    # Layout and content adjustments
    if st.session_state['current_tab'] == "Tab 1":
        st.header("Tổng Quan Thị Trường")
        @st.cache_data
        def calculate_metrics(data):
            unique_customers = data['Mã khách hàng'].nunique()
            unique_orders = data['Mã đơn hàng'].nunique()
            unique_groups = data['Mã PKKH'].nunique()
            total_items = data['Mã mặt hàng'].nunique()
            return unique_customers, unique_orders, unique_groups, total_items
        def plot_data(data, group_col, agg_col, agg_func='sum', chart_type='bar', title=""):
            if agg_func == 'sum':
                agg_data = data.groupby(group_col)[agg_col].sum().reset_index()
            elif agg_func == 'mean':
                agg_data = data.groupby(group_col)[agg_col].mean().reset_index()
            elif agg_func == 'nunique':
                agg_data = data.groupby(group_col)[agg_col].nunique().reset_index()
            else:
                raise ValueError("Unsupported aggregation function")
            color_scale = px.colors.sequential.Rainbow_r
            if chart_type == 'bar':
                fig = px.bar(agg_data, x=group_col, y=agg_col, title=title,
                            color=agg_col, color_continuous_scale=color_scale)
            elif chart_type == 'line':
                fig = px.line(agg_data, x=group_col, y=agg_col, title=title,
                            markers=True, color_continuous_scale=color_scale)
            else:
                raise ValueError("Unsupported chart type")
            fig.update_layout(width=450, height=450)
            return fig
        def plot_time_series(data, x_col, group_col, value_col, agg_func, title):
            if agg_func == 'sum':
                agg_data = data.groupby([x_col, group_col])[value_col].sum().reset_index()
            elif agg_func == 'nunique':
                agg_data = data.groupby([x_col, group_col])[value_col].nunique().reset_index()

            fig = px.line(agg_data, x=x_col, y=value_col, color=group_col,
                        title=title, labels={group_col: "Kiểu PKKH", x_col: "Tháng", value_col: "Giá trị"})
            fig.update_layout(width=450, height=400)
            return fig

        unique_customers, unique_orders, unique_groups, total_items = calculate_metrics(data)

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Tổng số khách hàng", f"{unique_customers:,}")
        col_b.metric("Tổng số đơn hàng", f"{unique_orders:,}")
        col_c.metric("Tổng số phân khúc khách hàng", f"{unique_groups:,}")
        col_d.metric("Tổng số mặt hàng", f"{total_items:,}")

        # Bar chart
        chart_col1, chart_col2,chart_col3 = st.columns(3)
        with chart_col1:
            fig_orders = plot_data(data, 'Kiểu PKKH', 'Mã đơn hàng', 'nunique', 'bar', 'Tổng số đơn hàng với Kiểu PKKH')
            st.plotly_chart(fig_orders)
        with chart_col2:
            fig_revenue = plot_data(data, 'Kiểu PKKH', 'Thành tiền', 'sum', 'bar', 'Tổng doanh thu với Kiểu PKKH')
            st.plotly_chart(fig_revenue)
        with chart_col3:
            fig_orders = plot_data(data, 'Kiểu PKKH', 'Lợi Nhuận Gộp', 'sum', 'bar', 'Tổng lợi nhuận với Kiểu PKKH')
            st.plotly_chart(fig_orders)

        # Time series line charts on the same row
        time_series_charts = st.columns(3)
        with time_series_charts[0]:
            fig_order_time_series = plot_time_series(data, 'Tháng', 'Kiểu PKKH', 'Mã đơn hàng', 'nunique', 'Đơn hàng theo tháng và kiểu PKKH')
            st.plotly_chart(fig_order_time_series)
        with time_series_charts[1]:
            fig_revenue_time_series = plot_time_series(data, 'Tháng', 'Kiểu PKKH', 'Thành tiền', 'sum', 'Doanh thu theo tháng và kiểu PKKH')
            st.plotly_chart(fig_revenue_time_series)
        with time_series_charts[2]:
            fig_revenue_time_series = plot_time_series(data, 'Tháng', 'Kiểu PKKH', 'Lợi Nhuận Gộp', 'sum', 'Lợi Nhuận theo tháng và kiểu PKKH')
            st.plotly_chart(fig_revenue_time_series)


    # Content for Tab 2
    elif st.session_state['current_tab'] == "Tab 2":
        st.header("Phân Tích Khách Hàng")
        @st.cache_data
        def process_segments(data):
            unique_segments = data[['Mã PKKH', 'Mô tả Phân Khúc Khách hàng']].drop_duplicates().set_index('Mã PKKH')
            segment_counts = data.groupby('Mã PKKH')['Mã khách hàng'].nunique()
            segment_percentage = segment_counts / segment_counts.sum()
            segment_percentage = segment_percentage.reset_index(name="Tỉ lệ phần trăm")
            return unique_segments, segment_percentage

        def plot_customer_distribution(segment_percentage):
            fig = px.pie(
                segment_percentage, 
                values='Tỉ lệ phần trăm', 
                names='Mã PKKH', 
                title='Phân phối khách hàng',
                color='Mã PKKH',
                color_discrete_sequence=px.colors.diverging.Portland_r
            )
            fig.update_traces(textinfo='percent+label')
            fig.update_layout(
                title='<b>Phân phối khách hàng theo phân khúc RFM</b>',
                showlegend=True,
                autosize=True,
                width=400,  # Adjusted width for better visualization
                height=600  # Adjusted height to match the DataFrame's height
            )
            return fig
            # Process and cache unique segments and customer distribution
        unique_segments, segment_percentage = process_segments(data)
        
        # Layout for DataFrame and Pie Chart, adjust 'gap' for better spacing
        col1, col2 = st.columns([1, 1], gap="medium")        
        with col1:
            st.markdown("### Bảng phân khúc khách hàng duy nhất:")
            # Improved display using st.table for a cleaner look
            st.table(unique_segments.style.format(precision=2).set_properties(**{'background-color': 'lightblue', 'color': 'black', 'border': '1px solid black'}))   
        with col2:
            st.markdown("### Phân phối khách hàng:")
            fig = plot_customer_distribution(segment_percentage)
            st.plotly_chart(fig, use_container_width=True) 
        def plot_total_orders_by_segment(data):
            total_orders_by_segment = data.groupby('Mã PKKH')['Mã đơn hàng'].nunique()
            df_total = total_orders_by_segment.reset_index(name='Tổng số đơn hàng').sort_values(by='Tổng số đơn hàng', ascending=False)

            fig_total = px.bar(df_total, x='Mã PKKH', y='Tổng số đơn hàng',
                            title='Tổng số đơn hàng theo Mã PKKH',
                            color='Tổng số đơn hàng',
                            color_continuous_scale=px.colors.sequential.Rainbow)
            fig_total.update_layout(margin={"r":10, "t":30, "l":10, "b":10}, 
                                    width=450, height=400)  # Cập nhật kích thước và margin
            return fig_total

        def plot_quarterly_orders_by_segment(data):
            quarterly_orders = data.groupby(['Mã PKKH', 'Quý'])['Mã đơn hàng'].nunique()
            df_quarterly = quarterly_orders.reset_index(name='Tổng số đơn hàng')

            fig_quarterly = px.line(df_quarterly, x='Quý', y='Tổng số đơn hàng',
                                    title='Đơn hàng theo từng Quý',
                                    color='Mã PKKH',
                                    markers=True,
                                    color_discrete_sequence=px.colors.diverging.Geyser)
            fig_quarterly.update_layout(margin={"r":10, "t":30, "l":10, "b":10}, 
                                        width=450, height=400)
            return fig_quarterly

        def plot_monthly_orders_by_segment(data):
            monthly_orders = data.groupby(['Mã PKKH', 'Tháng'])['Mã đơn hàng'].nunique()
            df_monthly = monthly_orders.reset_index(name='Tổng số đơn hàng')

            fig_monthly = px.line(df_monthly, x='Tháng', y='Tổng số đơn hàng',
                                title='Đơn hàng theo từng Tháng',
                                color='Mã PKKH',
                                markers=True,
                                color_discrete_sequence=px.colors.diverging.Geyser)
            fig_monthly.update_layout(margin={"r":10, "t":30, "l":10, "b":10}, 
                                    width=450, height=400)
            return fig_monthly
        st.title("Phân tích đơn hàng")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(plot_total_orders_by_segment(data))
        with col2:
            st.plotly_chart(plot_quarterly_orders_by_segment(data))
        with col3:
            st.plotly_chart(plot_monthly_orders_by_segment(data))

        def plot_bar_chart(data, group_col, agg_col, title, color_scale):
            grouped_data = data.groupby(group_col)[agg_col].sum()
            df = grouped_data.reset_index(name=f'Tổng {agg_col}').sort_values(by=f'Tổng {agg_col}', ascending=True)

            fig = px.bar(df, x=group_col, y=f'Tổng {agg_col}',
                        title=title,
                        color=f'Tổng {agg_col}',
                        color_continuous_scale=color_scale)
            fig.update_layout(
                margin={"r":30, "t":60, "l":30, "b":30},  # Chỉnh sửa margin
                width=450,  # Chiều rộng của biểu đồ
                height=400,  # Chiều cao của biểu đồ
                title_font_size=16  # Cỡ chữ của tiêu đề
            )
            return fig

        def plot_line_chart(data, group_cols, agg_col, title, color_sequence):
            grouped_data = data.groupby(group_cols)[agg_col].sum()
            df = grouped_data.reset_index(name=f'Tổng {agg_col}')

            fig = px.line(df, x=group_cols[1], y=f'Tổng {agg_col}',
                        title=title,
                        color=group_cols[0],
                        markers=True,
                        color_discrete_sequence=color_sequence)
            fig.update_layout(
                margin={"r":30, "t":60, "l":30, "b":30},  # Chỉnh sửa margin
                width=450,  # Chiều rộng của biểu đồ
                height=400,  # Chiều cao của biểu đồ
                title_font_size=16  # Cỡ chữ của tiêu đề
            )
            return fig
        def display_charts(data):
            st.title("Phân tích Doanh thu và Lợi nhuận")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.plotly_chart(plot_bar_chart(data, 'Mã PKKH', 'Thành tiền', 'Tổng doanh thu theo Mã PKKH', px.colors.sequential.Rainbow))
            with col2:
                st.plotly_chart(plot_line_chart(data, ['Mã PKKH', 'Quý'], 'Thành tiền', 'Doanh thu theo từng Quý', px.colors.diverging.Geyser))
            with col3:
                st.plotly_chart(plot_line_chart(data, ['Mã PKKH', 'Tháng'], 'Thành tiền', 'Doanh thu theo từng Tháng', px.colors.diverging.Geyser))

            st.title("Phân tích Lợi nhuận")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.plotly_chart(plot_bar_chart(data, 'Mã PKKH', 'Lợi Nhuận Gộp', 'Tổng lợi nhuận theo Mã PKKH', px.colors.sequential.Rainbow))
            with col2:
                st.plotly_chart(plot_line_chart(data, ['Mã PKKH', 'Quý'], 'Lợi Nhuận Gộp', 'Lợi nhuận theo từng Quý', px.colors.diverging.Geyser))
            with col3:
                st.plotly_chart(plot_line_chart(data, ['Mã PKKH', 'Tháng'], 'Lợi Nhuận Gộp', 'Lợi nhuận theo từng Tháng', px.colors.diverging.Geyser))
        display_charts(data)       


        
    elif st.session_state['current_tab'] == "Tab 3":
        st.header("Phân Tích Doanh Thu")
        st.markdown("chưa xong")
    elif st.session_state['current_tab'] == "Tab 4":
        st.header("Phân Tích Hành Vi Mua")
    elif st.session_state['current_tab'] == "Tab 5":
        st.header("Phân Tích RFM")    
        # This decorator ensures that the data processing is cached correctly.
        def calculate_purchase_frequency(data):
            order_counts = data.groupby(['RFM_segment'])['Mã đơn hàng'].nunique()
            customer_counts = data.groupby(['RFM_segment'])['Mã khách hàng'].nunique()
            purchase_frequency = order_counts / customer_counts
            purchase_frequency_df = purchase_frequency.reset_index()
            purchase_frequency_df.columns = ['RFM_segment', 'Tần suất mua hàng']
            purchase_frequency_df['Tần suất mua hàng'] = purchase_frequency_df['Tần suất mua hàng'].map("{:.2f}".format)
            return purchase_frequency_df

        def calculate_repeat_customer_ratio(data):
            orders_per_customer = data.groupby(['RFM_segment', 'Mã khách hàng'])['Mã đơn hàng'].nunique()
            repeat_customers = orders_per_customer[orders_per_customer > 1]
            repeat_customer_counts = repeat_customers.groupby('RFM_segment').size()
            total_customers = data.groupby('RFM_segment')['Mã khách hàng'].nunique()
            repeat_customer_ratio = repeat_customer_counts / total_customers
            repeat_customer_ratio_df = repeat_customer_ratio.reset_index()
            repeat_customer_ratio_df.columns = ['RFM_segment', 'Tỷ lệ khách hàng mua lặp lại']
            repeat_customer_ratio_df['Tỷ lệ khách hàng mua lặp lại'] = repeat_customer_ratio_df['Tỷ lệ khách hàng mua lặp lại'].fillna(0).map("{:.2f}".format)
            return repeat_customer_ratio_df

        def calculate_average_order_value(data):
            revenue_per_rfm = data.groupby('RFM_segment')['Thành tiền'].sum()
            orders_per_rfm = data.groupby('RFM_segment')['Mã đơn hàng'].nunique()
            aov_per_rfm = revenue_per_rfm / orders_per_rfm
            df_aov_per_rfm = pd.DataFrame({
                'RFM_segment': aov_per_rfm.index, 
                'Total_Revenue': revenue_per_rfm, 
                'Total_Orders': orders_per_rfm,
                'AOV': aov_per_rfm
            })
            return df_aov_per_rfm

        # Choose the type of analysis
        analysis_options = ["Tần Suất Mua Hàng", "Tỷ Lệ Mua Hàng Lặp Lại", "Giá Trị Trung Bình Đơn Hàng"]
        selected_analysis_type = st.selectbox("Chọn loại phân tích:", analysis_options)

        # Display results based on the selected analysis type
        if selected_analysis_type == "Tần Suất Mua Hàng":
            result_df = calculate_purchase_frequency(data)
            st.dataframe(result_df)
        elif selected_analysis_type == "Tỷ Lệ Mua Hàng Lặp Lại":
            result_df = calculate_repeat_customer_ratio(data)
            st.dataframe(result_df)
        elif selected_analysis_type == "Giá Trị Trung Bình Đơn Hàng":
            result_df = calculate_average_order_value(data)
            st.dataframe(result_df)
        else:
            st.write("Không có dữ liệu cho loại phân tích được chọn.")

if __name__ == '__main__':
    main()

