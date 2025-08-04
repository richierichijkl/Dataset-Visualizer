import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import seaborn as sns

# ========== About Data ==========
def about_df(df):
    df_sample = df.sample(min(10, len(df)))
    size = df.shape[0]
    buffer = io.StringIO()
    df.info(buf=buffer)
    info = buffer.getvalue()
    columns = df.dtypes
    missing_values = df.isnull().sum()
    stats = df.describe(include='all')

    return df_sample, size, info, columns, missing_values, stats

# ========== Generic Statistics ==========
def basic_statistics(df):
    stats = {}
    numeric_cols = df.select_dtypes(include='number').columns

    for col in numeric_cols:
        stats[col] = {
            'Mean': df[col].mean(),
            'Median': df[col].median(),
            'Standard Deviation': df[col].std(),
            'Missing Values': df[col].isnull().sum()
        }
    return stats

# ========== Generic Graphs ==========

def plot_histogram(df, column):
    fig, ax = plt.subplots()
    df[column].dropna().plot(kind='hist', bins=10, color='skyblue', edgecolor='black', ax=ax)
    ax.set_title(f'Histogram of {column}')
    ax.set_xlabel(column)
    ax.set_ylabel('Frequency')
    return fig

def plot_pie_chart(df, column):
    fig, ax = plt.subplots()
    df[column].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_title(f'Distribution of {column}')
    ax.set_ylabel('')
    return fig

def plot_bar_chart(df, group_col, value_col):
    fig, ax = plt.subplots()
    df.groupby(group_col)[value_col].mean().plot(kind='bar', color='lightgreen', ax=ax)
    ax.set_title(f'Average {value_col} by {group_col}')
    ax.set_xlabel(group_col)
    ax.set_ylabel(f'Average {value_col}')
    return fig

def correlation_heatmap(df):
    numeric_df = df.select_dtypes(include='number')
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
    ax.set_title("Correlation Heatmap")
    return fig


def box_plot(df, numeric_col, group_col=None):
    fig, ax = plt.subplots()
    if group_col:
        sns.boxplot(x=group_col, y=numeric_col, data=df, ax=ax)
        ax.set_title(f'Boxplot of {numeric_col} by {group_col}')
    else:
        sns.boxplot(y=df[numeric_col], ax=ax)
        ax.set_title(f'Boxplot of {numeric_col}')
    return fig

def scatter_plot(df, x_col, y_col):
    fig, ax = plt.subplots()
    ax.scatter(df[x_col], df[y_col], alpha=0.6)
    ax.set_title(f'{y_col} vs {x_col}')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    return fig

def top_categories_bar(df, column, top_n=10):
    fig, ax = plt.subplots()
    df[column].value_counts().nlargest(top_n).plot(kind='bar', color='purple', ax=ax)
    ax.set_title(f'Top {top_n} Frequent Categories in {column}')
    ax.set_xlabel(column)
    ax.set_ylabel('Count')
    return fig


# ========== MAIN APP ==========
if __name__ == "__main__":
    st.title("📊 Smart Data Explorer Dashboard")
    st.subheader("Upload any CSV file to get insights and visualizations")

    st.sidebar.title("🔍 Options")
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type='csv')
    df = pd.DataFrame()

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # About Dataset
        if st.sidebar.button("About Dataset"):
            st.subheader("📄 About Dataset")
            df_sample, size, info, columns, missing_values, stats = about_df(df)
            st.write("**Sample Data:**", df_sample)
            st.write("**Dataset Size:**", size)
            st.text("**Structure Info:**\n" + info)
            st.write("**Column Types:**", columns)
            st.write("**Missing Values:**", missing_values)
            st.write("**Descriptive Statistics:**", stats)

        # Statistics
        if st.sidebar.button("Basic Statistics"):
            st.subheader("📈 Basic Statistics")
            stats = basic_statistics(df)
            for col, metrics in stats.items():
                st.write(f"**{col}**")
                st.json(metrics)

        # Graphs
        if st.sidebar.button("Dashboard"):
            st.subheader("📊 Data Visualizations")

            # Histogram
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) > 0:
                selected_num = st.selectbox("📉 Select column for Histogram", numeric_cols)
                st.pyplot(plot_histogram(df, selected_num))

            # Pie Chart
            categorical_cols = df.select_dtypes(exclude='number').columns
            if len(categorical_cols) > 0:
                selected_cat = st.selectbox("🥧 Select column for Pie Chart", categorical_cols)
                st.pyplot(plot_pie_chart(df, selected_cat))

            # Grouped Bar Chart
            if len(numeric_cols) > 0 and len(categorical_cols) > 0:
                group_col = st.selectbox("🧮 Group by (categorical)", categorical_cols)
                value_col = st.selectbox("📦 Value column (numerical)", numeric_cols)
                st.pyplot(plot_bar_chart(df, group_col, value_col))

            # Correlation Heatmap
            if len(numeric_cols) >= 2:
                st.subheader("📌 Correlation Heatmap")
                fig = correlation_heatmap(df)
                st.pyplot(fig)

            # Box Plot
            st.subheader("📦 Box Plot")
            selected_box_col = st.selectbox("Select numeric column for Box Plot", numeric_cols, key='box1')
            group_option = st.selectbox("Group by (optional)", ['None'] + list(df.columns), key='box2')
            group_col = group_option if group_option != 'None' else None
            st.pyplot(box_plot(df, selected_box_col, group_col))

            # Scatter Plot
            if len(numeric_cols) >= 2:
                st.subheader("🎯 Scatter Plot")
                x_col = st.selectbox("X-axis column", numeric_cols, key='scatter_x')
                y_col = st.selectbox("Y-axis column", numeric_cols, key='scatter_y')
                st.pyplot(scatter_plot(df, x_col, y_col))

            # Top Categories Bar Plot
            if len(categorical_cols) > 0:
                st.subheader("🧱 Top Categories")
                cat_col = st.selectbox("Select column for Top Category Bar Plot", categorical_cols, key='top_cat')
                st.pyplot(top_categories_bar(df, cat_col))


    else:
        st.info("Please upload a CSV file from the sidebar to begin.")
