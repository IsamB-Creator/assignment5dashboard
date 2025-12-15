import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Page config ----------
st.set_page_config(page_title="Juice & Smoothie Sales Dashboard", layout="wide")

st.title("Juice & Smoothie Sales Dashboard")

st.write(
    """
This app uses the Excel file **ejb.xlsx** in the same folder as this script and generates:
1. A bar chart comparing total sales for **Juices vs Smoothies**.  
2. A **time-series line chart** of daily sales.  
3. A **distribution chart** of service satisfaction ratings.  
"""
)

# ---------- Load ejb.xlsx directly ----------
try:
    df = pd.read_excel("ejb.xlsx")
except FileNotFoundError:
    st.error(
        "Could not find `ejb.xlsx` in the same folder as `app.py`. "
        "Make sure the file is there and the name is exactly `ejb.xlsx`."
    )
    st.stop()

st.subheader("Preview of ejb.xlsx")
st.dataframe(df.head())

# ---------- Column mapping in sidebar ----------
st.sidebar.header("Column Mapping")

all_cols = list(df.columns)


def default_index(col_name, cols):
    return cols.index(col_name) if col_name in cols else 0


category_col = st.sidebar.selectbox(
    "Category column (e.g., 'Category')",
    options=all_cols,
    index=default_index("Category", all_cols)
)

sales_col = st.sidebar.selectbox(
    "Sales column (total $ sales, e.g., 'Sales' or '$ Sales')",
    options=all_cols,
    index=default_index("Sales", all_cols)
)

date_col = st.sidebar.selectbox(
    "Date Ordered column (e.g., 'Date Ordered')",
    options=all_cols,
    index=default_index("Date Ordered", all_cols)
)

satisfaction_col = st.sidebar.selectbox(
    "Service Satisfaction Rating column (e.g., 'Service Satisfaction Rating')",
    options=all_cols,
    index=default_index("Service Satisfaction Rating", all_cols)
)

st.sidebar.markdown("---")
st.sidebar.write("Make sure each mapping matches the correct column in ejb.xlsx.")

# ---------- Basic cleaning / type conversions ----------
# Ensure sales is numeric
df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")

# Convert date
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# Drop rows where key columns are missing
df_clean = df.dropna(subset=[category_col, sales_col, date_col])

# ---------- Tabs for the dashboard (Question 4) ----------
tab1, tab2, tab3 = st.tabs(["Category Sales", "Sales Over Time", "Satisfaction Ratings"])

# ================== Tab 1: Category Sales Comparison (Q1) ==================
with tab1:
    st.header("Category Sales Comparison: Juices vs Smoothies (and others)")

    category_sales = (
        df_clean.groupby(category_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
    )

    st.write("Total sales by category:")
    cat_df = category_sales.reset_index()
    cat_df.columns = [category_col, "Total Sales"]
    st.dataframe(cat_df)

    fig1, ax1 = plt.subplots()
    ax1.bar(category_sales.index, category_sales.values)
    ax1.set_xlabel("Category")
    ax1.set_ylabel("Total Sales ($)")
    ax1.set_title("Total Sales by Category")
    plt.xticks(rotation=45)

    st.pyplot(fig1)

    if not category_sales.empty:
        top_category = category_sales.idxmax()
        top_sales = category_sales.max()
        st.markdown(
            f"""
**Interpretation:**  
The chart shows total sales for each product category.  
In this dataset, **{top_category}** generates the highest revenue, with approximately **${top_sales:,.2f}** in total sales.  
Compare the bar heights to explain whether **Juices or Smoothies** bring in more revenue overall.
"""
        )
    else:
        st.warning("No valid category/sales data available after cleaning.")

# ================== Tab 2: Sales Over Time (Q2) ==================
with tab2:
    st.header("Sales Over Time (Daily)")

    time_df = df_clean.dropna(subset=[date_col, sales_col]).copy()

    if time_df.empty:
        st.warning("No valid date/sales data available to plot time series.")
    else:
        daily_sales = (
            time_df.groupby(time_df[date_col].dt.date)[sales_col]
            .sum()
            .sort_index()
        )

        st.write("Daily total sales:")
        daily_df = daily_sales.reset_index()
        daily_df.columns = ["Date", "Total Sales"]
        st.dataframe(daily_df)

        fig2, ax2 = plt.subplots()
        ax2.plot(daily_sales.index, daily_sales.values)
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Total Sales ($)")
        ax2.set_title("Daily Sales Over Time")
        plt.xticks(rotation=45)

        st.pyplot(fig2)

        if len(daily_sales) > 1:
            first_date, last_date = daily_sales.index[0], daily_sales.index[-1]
            first_val, last_val = daily_sales.iloc[0], daily_sales.iloc[-1]
            if last_val > first_val:
                trend = "increased"
            elif last_val < first_val:
                trend = "decreased"
            else:
                trend = "stayed about the same"

            st.markdown(
                f"""
**Interpretation:**  
This line chart shows how total sales change from **{first_date}** to **{last_date}**.  
Overall, daily sales have **{trend}** over the period.  
You can call out visible peaks as high-demand days and dips as slower days.
"""
            )
        else:
            st.markdown(
                """
**Interpretation:**  
There is only one date in the dataset, so the line is just a single point.  
With more dates, you would see a clearer trend over time.
"""
            )

# ================== Tab 3: Satisfaction Ratings (Q3) ==================
with tab3:
    st.header("Service Satisfaction Rating Distribution")

    sat_series = df[satisfaction_col].dropna()

    if sat_series.empty:
        st.warning("No satisfaction rating data available.")
    else:
        sat_series = pd.to_numeric(sat_series, errors="coerce").dropna()
        rating_counts = sat_series.value_counts().sort_index()

        st.write("Count of customers by satisfaction rating:")
        rating_df = rating_counts.reset_index()
        rating_df.columns = ["Rating", "Count"]
        st.dataframe(rating_df)

        fig3, ax3 = plt.subplots()
        ax3.bar(rating_counts.index.astype(str), rating_counts.values)
        ax3.set_xlabel("Service Satisfaction Rating")
        ax3.set_ylabel("Number of Customers")
        ax3.set_title("Distribution of Service Satisfaction Ratings")

        st.pyplot(fig3)

        most_common_rating = rating_counts.idxmax()
        count_most_common = rating_counts.max()

        st.markdown(
            f"""
**Interpretation:**  
This chart shows how customers rated the service (e.g., on a 1–5 scale).  
The most common rating is **{most_common_rating}**, with **{count_most_common}** customers giving that score.  
Higher bars indicate ratings that customers chose more often, which tells you how satisfied they usually are.
"""
        )
