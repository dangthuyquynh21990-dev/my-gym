import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Phân tích hội viên MyGym",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_csv("day3_segmented_data.csv")
    for col in ["join_date", "last_visit_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

df = load_data()

# Từ điển Việt hóa
vi_labels = {
    "membership_type": "Loại hội viên",
    "subscription_model": "Gói đăng ký",
    "monthly_equiv": "Doanh thu quy đổi theo tháng",
    "ltv_proxy": "Giá trị khách hàng (LTV)",
    "weekly_minutes": "Số phút tập mỗi tuần",
    "visit_per_week": "Số buổi tập mỗi tuần",
    "tenure_months": "Thời gian gắn bó (tháng)",
    "churn_risk": "Nguy cơ rời bỏ",
    "home_gym_location": "Chi nhánh",
    "access_hours": "Khung giờ truy cập",
    "value_segment": "Phân khúc khách hàng",
    "addon_count": "Số dịch vụ đi kèm",
    "members": "Số hội viên",
    "share": "Tỷ trọng",
    "avg_ltv_proxy": "LTV trung bình",
    "avg_monthly_equiv": "Doanh thu tháng trung bình",
    "avg_weekly_minutes": "Số phút tập/tuần trung bình",
    "avg_tenure": "Thời gian gắn bó trung bình",
    "likely_churn_rate": "Tỷ lệ có nguy cơ rời bỏ cao"
}

# Sidebar
st.sidebar.title("Bộ lọc")

membership_options = sorted(df["membership_type"].dropna().unique()) if "membership_type" in df.columns else []
branch_options = sorted(df["home_gym_location"].dropna().unique()) if "home_gym_location" in df.columns else []
subscription_options = sorted(df["subscription_model"].dropna().unique()) if "subscription_model" in df.columns else []
segment_options = sorted(df["value_segment"].dropna().unique()) if "value_segment" in df.columns else []

selected_membership = st.sidebar.multiselect(
    "Loại hội viên",
    membership_options,
    default=membership_options
)

selected_branch = st.sidebar.multiselect(
    "Chi nhánh",
    branch_options,
    default=branch_options
)

selected_subscription = st.sidebar.multiselect(
    "Gói đăng ký",
    subscription_options,
    default=subscription_options
)

selected_segment = st.sidebar.multiselect(
    "Phân khúc khách hàng",
    segment_options,
    default=segment_options
)

filtered_df = df.copy()

if "membership_type" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["membership_type"].isin(selected_membership)]

if "home_gym_location" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["home_gym_location"].isin(selected_branch)]

if "subscription_model" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["subscription_model"].isin(selected_subscription)]

if "value_segment" in filtered_df.columns and len(segment_options) > 0:
    filtered_df = filtered_df[filtered_df["value_segment"].isin(selected_segment)]

# Header
st.title("🏋️ Dashboard Phân Tích Hội Viên MyGym")
st.markdown(
    """
    Dashboard này hỗ trợ phân tích:
    - giá trị khách hàng
    - nguy cơ rời bỏ
    - mức độ gắn kết
    - hiệu suất chi nhánh
    - cơ hội tối ưu doanh thu và giữ chân hội viên
    """
)

st.info(
    "Điểm nổi bật: Nhóm hội viên cao cấp và gói dài hạn thường tạo giá trị cao hơn, trong khi gói theo tháng có xu hướng rời bỏ cao hơn."
)

# KPI
st.subheader("Tổng quan KPI")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tổng số hội viên", f"{len(filtered_df):,}")
col2.metric("Doanh thu quy đổi theo tháng", f"{filtered_df['monthly_equiv'].mean():.2f}")
col3.metric("Giá trị khách hàng trung bình", f"{filtered_df['ltv_proxy'].mean():.2f}")
col4.metric("Tỷ lệ có nguy cơ rời bỏ cao", f"{(filtered_df['churn_risk'] == 'Likely Churn').mean():.1%}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Tổng quan",
    "Giá trị khách hàng",
    "Giữ chân hội viên",
    "Dịch vụ & Gắn kết",
    "Chi nhánh & Phân khúc"
])

# TAB 1
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Phân bố nguy cơ rời bỏ")
        churn_dist = filtered_df["churn_risk"].value_counts(normalize=True).reset_index()
        churn_dist.columns = ["churn_risk", "share"]
        fig = px.pie(
            churn_dist,
            names="churn_risk",
            values="share",
            title="Tỷ trọng nguy cơ rời bỏ",
            labels={
                "churn_risk": "Nguy cơ rời bỏ",
                "share": "Tỷ trọng"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Cơ cấu loại hội viên")
        membership_mix = filtered_df["membership_type"].value_counts().reset_index()
        membership_mix.columns = ["membership_type", "members"]
        fig = px.bar(
            membership_mix,
            x="membership_type",
            y="members",
            title="Số lượng hội viên theo loại thẻ",
            labels={
                "membership_type": "Loại hội viên",
                "members": "Số hội viên"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Xem nhanh dữ liệu")
    st.dataframe(filtered_df.head(20), use_container_width=True)

# TAB 2
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Giá trị theo loại hội viên")
        membership_summary = (
            filtered_df.groupby("membership_type")
            .agg(
                members=("ltv_proxy", "size"),
                avg_ltv_proxy=("ltv_proxy", "mean"),
                avg_monthly_equiv=("monthly_equiv", "mean"),
                avg_weekly_minutes=("weekly_minutes", "mean")
            )
            .reset_index()
            .sort_values("avg_ltv_proxy", ascending=False)
        )

        fig = px.bar(
            membership_summary,
            x="membership_type",
            y="avg_ltv_proxy",
            color="avg_monthly_equiv",
            title="Giá trị khách hàng trung bình theo loại hội viên",
            labels={
                "membership_type": "Loại hội viên",
                "avg_ltv_proxy": "LTV trung bình",
                "avg_monthly_equiv": "Doanh thu tháng trung bình"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Giá trị khách hàng và mức độ gắn kết")
        fig = px.scatter(
            filtered_df,
            x="weekly_minutes",
            y="ltv_proxy",
            color="churn_risk",
            hover_data=["membership_type", "subscription_model"],
            title="Mối quan hệ giữa mức độ tập luyện và giá trị khách hàng",
            labels={
                "weekly_minutes": "Số phút tập mỗi tuần",
                "ltv_proxy": "Giá trị khách hàng (LTV)",
                "churn_risk": "Nguy cơ rời bỏ"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 3
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Nguy cơ rời bỏ theo gói đăng ký")
        churn_sub = (
            filtered_df.groupby("subscription_model")
            .agg(likely_churn_rate=("churn_risk", lambda x: (x == "Likely Churn").mean()))
            .reset_index()
        )

        fig = px.bar(
            churn_sub,
            x="subscription_model",
            y="likely_churn_rate",
            title="Tỷ lệ rời bỏ cao theo gói đăng ký",
            labels={
                "subscription_model": "Gói đăng ký",
                "likely_churn_rate": "Tỷ lệ có nguy cơ rời bỏ cao"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Thời gian gắn bó theo gói đăng ký")
        tenure_sub = (
            filtered_df.groupby("subscription_model")
            .agg(avg_tenure=("tenure_months", "mean"))
            .reset_index()
        )

        fig = px.bar(
            tenure_sub,
            x="subscription_model",
            y="avg_tenure",
            title="Thời gian gắn bó trung bình theo gói đăng ký",
            labels={
                "subscription_model": "Gói đăng ký",
                "avg_tenure": "Thời gian gắn bó trung bình (tháng)"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 4
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Mức độ gắn kết theo khung giờ truy cập")
        access_summary = (
            filtered_df.groupby("access_hours")
            .agg(
                avg_weekly_minutes=("weekly_minutes", "mean"),
                avg_monthly_equiv=("monthly_equiv", "mean")
            )
            .reset_index()
        )

        fig = px.bar(
            access_summary,
            x="access_hours",
            y="avg_weekly_minutes",
            color="avg_monthly_equiv",
            title="Mức độ gắn kết theo khung giờ truy cập",
            labels={
                "access_hours": "Khung giờ truy cập",
                "avg_weekly_minutes": "Số phút tập/tuần trung bình",
                "avg_monthly_equiv": "Doanh thu tháng trung bình"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Số dịch vụ đi kèm và giá trị khách hàng")
        if "addon_count" in filtered_df.columns:
            fig = px.box(
                filtered_df,
                x="addon_count",
                y="ltv_proxy",
                title="Giá trị khách hàng theo số dịch vụ đi kèm",
                labels={
                    "addon_count": "Số dịch vụ đi kèm",
                    "ltv_proxy": "Giá trị khách hàng (LTV)"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

# TAB 5
with tab5:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Hiệu suất chi nhánh")
        branch_summary = (
            filtered_df.groupby("home_gym_location")
            .agg(
                members=("ltv_proxy", "size"),
                avg_ltv_proxy=("ltv_proxy", "mean"),
                avg_monthly_equiv=("monthly_equiv", "mean"),
                likely_churn_rate=("churn_risk", lambda x: (x == "Likely Churn").mean())
            )
            .reset_index()
        )

        fig = px.scatter(
            branch_summary,
            x="avg_monthly_equiv",
            y="likely_churn_rate",
            size="members",
            hover_name="home_gym_location",
            title="Doanh thu và nguy cơ rời bỏ theo chi nhánh",
            labels={
                "avg_monthly_equiv": "Doanh thu tháng trung bình",
                "likely_churn_rate": "Tỷ lệ có nguy cơ rời bỏ cao"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Phân khúc khách hàng")
        if "value_segment" in filtered_df.columns:
            segment_summary = (
                filtered_df.groupby("value_segment")
                .agg(
                    members=("ltv_proxy", "size"),
                    avg_ltv_proxy=("ltv_proxy", "mean")
                )
                .reset_index()
            )

            fig = px.bar(
                segment_summary,
                x="value_segment",
                y="members",
                color="avg_ltv_proxy",
                title="Tổng quan phân khúc khách hàng",
                labels={
                    "value_segment": "Phân khúc khách hàng",
                    "members": "Số hội viên",
                    "avg_ltv_proxy": "LTV trung bình"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Đề xuất hành động")
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        st.success("Giữ chân hội viên\n\nƯu tiên chuyển đổi nhóm hội viên theo tháng đang hoạt động tốt sang gói quý hoặc năm.")

    with action_col2:
        st.success("Tăng doanh thu\n\nKết hợp PT và lớp nhóm thành gói dịch vụ thay vì giảm giá đại trà.")

    with action_col3:
        st.success("Tối ưu vận hành\n\nXem xét các chi nhánh có tỷ lệ rời bỏ cao để cải thiện trải nghiệm tại điểm tập.")