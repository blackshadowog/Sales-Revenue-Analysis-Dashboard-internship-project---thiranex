"""
Sales & Revenue Analysis Dashboard
===================================
A professional interactive dashboard for sales data analysis.
Uses: Tkinter, Matplotlib, Pandas, NumPy, Seaborn
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────── THEME ───────────────────────────
DARK_BG      = "#0D1117"
PANEL_BG     = "#161B22"
CARD_BG      = "#1C2128"
ACCENT1      = "#00D4FF"   # cyan
ACCENT2      = "#7C3AED"   # purple
ACCENT3      = "#10B981"   # green
ACCENT4      = "#F59E0B"   # amber
ACCENT5      = "#EF4444"   # red
TEXT_PRI     = "#E6EDF3"
TEXT_SEC     = "#8B949E"
BORDER       = "#30363D"
CHART_COLORS = ["#00D4FF", "#7C3AED", "#10B981", "#F59E0B", "#EF4444",
                "#06B6D4", "#8B5CF6", "#34D399", "#FCD34D", "#F87171"]

plt.rcParams.update({
    "figure.facecolor":  PANEL_BG,
    "axes.facecolor":    CARD_BG,
    "axes.edgecolor":    BORDER,
    "axes.labelcolor":   TEXT_SEC,
    "text.color":        TEXT_PRI,
    "xtick.color":       TEXT_SEC,
    "ytick.color":       TEXT_SEC,
    "grid.color":        BORDER,
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "legend.facecolor":  CARD_BG,
    "legend.edgecolor":  BORDER,
    "font.family":       "sans-serif",
})

# ─────────────────────────── SAMPLE DATA GENERATOR ───────────────────────────
def generate_sample_data():
    np.random.seed(42)
    products   = ["Laptop Pro", "Smart Watch", "Wireless Earbuds", "Tablet Ultra",
                  "Gaming Mouse", "Mechanical Keyboard", "4K Monitor", "USB-C Hub",
                  "Webcam HD", "SSD Drive"]
    categories = ["Electronics", "Wearables", "Audio", "Electronics", "Peripherals",
                  "Peripherals", "Displays", "Accessories", "Peripherals", "Storage"]
    regions    = ["North", "South", "East", "West", "Central"]
    salespersons = ["Alice Johnson", "Bob Smith", "Carol White", "David Brown",
                    "Emma Davis", "Frank Miller", "Grace Wilson", "Henry Moore"]

    dates = pd.date_range(start="2023-01-01", end="2024-12-31", freq="D")
    n = 2500

    data = {
        "Date":         np.random.choice(dates, n),
        "Product":      np.random.choice(products, n, p=[.15,.12,.13,.11,.09,.10,.08,.08,.07,.07]),
        "Category":     None,
        "Region":       np.random.choice(regions, n, p=[.25,.20,.20,.20,.15]),
        "SalesPerson":  np.random.choice(salespersons, n),
        "Units":        np.random.randint(1, 25, n),
    }
    df = pd.DataFrame(data)

    price_map = {"Laptop Pro":1299,"Smart Watch":349,"Wireless Earbuds":179,
                 "Tablet Ultra":899,"Gaming Mouse":79,"Mechanical Keyboard":149,
                 "4K Monitor":499,"USB-C Hub":59,"Webcam HD":99,"SSD Drive":129}
    cat_map   = dict(zip(products, categories))

    df["Category"]    = df["Product"].map(cat_map)
    df["UnitPrice"]   = df["Product"].map(price_map)
    df["Discount"]    = np.random.choice([0, 0.05, 0.10, 0.15, 0.20], n,
                                         p=[.50, .20, .15, .10, .05])
    df["Revenue"]     = (df["Units"] * df["UnitPrice"] * (1 - df["Discount"])).round(2)
    df["COGS"]        = (df["Revenue"] * np.random.uniform(0.45, 0.65, n)).round(2)
    df["Profit"]      = (df["Revenue"] - df["COGS"]).round(2)
    df["ProfitMargin"]= ((df["Profit"] / df["Revenue"]) * 100).round(1)
    df["Date"]        = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df

# ─────────────────────────── KPI CARD ───────────────────────────
class KPICard(tk.Frame):
    def __init__(self, parent, title, value, subtitle, accent, icon, **kwargs):
        super().__init__(parent, bg=CARD_BG, relief="flat", **kwargs)
        self.configure(highlightbackground=accent, highlightthickness=1)

        # Top bar
        top = tk.Frame(self, bg=accent, height=3)
        top.pack(fill="x", side="top")

        body = tk.Frame(self, bg=CARD_BG, padx=16, pady=12)
        body.pack(fill="both", expand=True)

        # Icon + title row
        header = tk.Frame(body, bg=CARD_BG)
        header.pack(fill="x")
        tk.Label(header, text=icon, font=("Segoe UI Emoji", 18),
                 bg=CARD_BG, fg=accent).pack(side="left")
        tk.Label(header, text=title, font=("Segoe UI", 10, "bold"),
                 bg=CARD_BG, fg=TEXT_SEC).pack(side="left", padx=(8,0))

        # Value
        self.val_label = tk.Label(body, text=value, font=("Segoe UI", 22, "bold"),
                                   bg=CARD_BG, fg=TEXT_PRI)
        self.val_label.pack(anchor="w", pady=(6,2))

        # Subtitle
        self.sub_label = tk.Label(body, text=subtitle, font=("Segoe UI", 9),
                                   bg=CARD_BG, fg=TEXT_SEC)
        self.sub_label.pack(anchor="w")

    def update_value(self, value, subtitle=""):
        self.val_label.config(text=value)
        if subtitle:
            self.sub_label.config(text=subtitle)

# ─────────────────────────── MAIN APP ───────────────────────────
class SalesDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📊 Sales & Revenue Analysis Dashboard")
        self.geometry("1600x950")
        self.minsize(1200, 700)
        self.configure(bg=DARK_BG)

        self.df_raw  = generate_sample_data()
        self.df      = self.df_raw.copy()

        # State
        self.year_var    = tk.StringVar(value="All")
        self.region_var  = tk.StringVar(value="All")
        self.category_var= tk.StringVar(value="All")
        self.person_var  = tk.StringVar(value="All")
        self.active_chart= tk.StringVar(value="Revenue Trend")

        self._build_ui()
        self._apply_filters()

    # ── BUILD UI ──
    def _build_ui(self):
        # ── Top Header ──
        self._build_header()
        # ── Main container ──
        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=10, pady=(0,10))
        # ── Left Sidebar (filters) ──
        self._build_sidebar(main)
        # ── Right content ──
        content = tk.Frame(main, bg=DARK_BG)
        content.pack(side="left", fill="both", expand=True)
        # ── KPI Row ──
        self._build_kpi_row(content)
        # ── Charts ──
        self._build_chart_area(content)

    def _build_header(self):
        header = tk.Frame(self, bg=PANEL_BG, height=62)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Left logo/title
        left = tk.Frame(header, bg=PANEL_BG)
        left.pack(side="left", padx=20, pady=10)
        tk.Label(left, text="📊", font=("Segoe UI Emoji", 22),
                 bg=PANEL_BG, fg=ACCENT1).pack(side="left")
        title_f = tk.Frame(left, bg=PANEL_BG)
        title_f.pack(side="left", padx=8)
        tk.Label(title_f, text="Sales & Revenue Dashboard",
                 font=("Segoe UI", 15, "bold"), bg=PANEL_BG, fg=TEXT_PRI).pack(anchor="w")
        tk.Label(title_f, text="Real-time interactive analytics",
                 font=("Segoe UI", 9), bg=PANEL_BG, fg=TEXT_SEC).pack(anchor="w")

        # Right action buttons
        right = tk.Frame(header, bg=PANEL_BG)
        right.pack(side="right", padx=20)
        self._icon_btn(right, "📂 Import Data", self._import_data, ACCENT2).pack(side="left", padx=4)
        self._icon_btn(right, "💾 Export CSV",  self._export_csv,  ACCENT3).pack(side="left", padx=4)
        self._icon_btn(right, "🖨  Export PDF",  self._export_pdf,  ACCENT4).pack(side="left", padx=4)
        self._icon_btn(right, "🔄 Sample Data", self._reload_sample,ACCENT1).pack(side="left", padx=4)

        # Separator
        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x")

    def _icon_btn(self, parent, text, cmd, color):
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=CARD_BG, fg=color, activebackground=BORDER,
                        activeforeground=color, relief="flat",
                        font=("Segoe UI", 9, "bold"),
                        padx=12, pady=6, cursor="hand2",
                        highlightbackground=color, highlightthickness=1)
        return btn

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=PANEL_BG, width=220)
        sidebar.pack(side="left", fill="y", padx=(0,8), pady=8)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🎛  FILTERS & SLICERS",
                 font=("Segoe UI", 9, "bold"), bg=PANEL_BG,
                 fg=ACCENT1, pady=14).pack(fill="x", padx=12)

        sep = tk.Frame(sidebar, bg=BORDER, height=1)
        sep.pack(fill="x", padx=12)

        # Filter sections
        years    = ["All"] + sorted(self.df_raw["Date"].dt.year.unique().astype(str).tolist())
        regions  = ["All"] + sorted(self.df_raw["Region"].unique().tolist())
        cats     = ["All"] + sorted(self.df_raw["Category"].unique().tolist())
        persons  = ["All"] + sorted(self.df_raw["SalesPerson"].unique().tolist())

        self._filter_block(sidebar, "📅 Year",        self.year_var,    years)
        self._filter_block(sidebar, "🗺  Region",      self.region_var,  regions)
        self._filter_block(sidebar, "📦 Category",    self.category_var, cats)
        self._filter_block(sidebar, "👤 Sales Person", self.person_var,  persons)

        # Apply button
        tk.Frame(sidebar, bg=PANEL_BG, height=12).pack()
        btn = tk.Button(sidebar, text="✅  APPLY FILTERS",
                        command=self._apply_filters,
                        bg=ACCENT1, fg=DARK_BG, font=("Segoe UI", 10, "bold"),
                        relief="flat", padx=10, pady=8, cursor="hand2")
        btn.pack(fill="x", padx=14, pady=4)

        reset_btn = tk.Button(sidebar, text="↩  Reset Filters",
                              command=self._reset_filters,
                              bg=CARD_BG, fg=TEXT_SEC, font=("Segoe UI", 9),
                              relief="flat", padx=10, pady=6, cursor="hand2",
                              highlightbackground=BORDER, highlightthickness=1)
        reset_btn.pack(fill="x", padx=14, pady=2)

        # Stats summary
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=12, pady=12)
        self.stats_frame = tk.Frame(sidebar, bg=PANEL_BG)
        self.stats_frame.pack(fill="x", padx=12)
        tk.Label(self.stats_frame, text="📋 DATASET SUMMARY",
                 font=("Segoe UI", 8, "bold"), bg=PANEL_BG,
                 fg=TEXT_SEC).pack(anchor="w", pady=(0,6))
        self.stats_labels = {}
        for key in ["Records", "Date Range", "Products", "Avg Margin"]:
            row = tk.Frame(self.stats_frame, bg=PANEL_BG)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=key+":", font=("Segoe UI", 8),
                     bg=PANEL_BG, fg=TEXT_SEC, width=11, anchor="w").pack(side="left")
            lbl = tk.Label(row, text="—", font=("Segoe UI", 8, "bold"),
                           bg=PANEL_BG, fg=TEXT_PRI, anchor="w")
            lbl.pack(side="left")
            self.stats_labels[key] = lbl

        # Chart selector
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=12, pady=10)
        tk.Label(sidebar, text="📈 CHART TYPE", font=("Segoe UI", 9, "bold"),
                 bg=PANEL_BG, fg=TEXT_SEC, padx=12).pack(anchor="w")
        charts = ["Revenue Trend", "Product Performance", "Regional Map",
                  "Category Breakdown", "Profit Analysis", "Heatmap"]
        for ch in charts:
            rb = tk.Radiobutton(sidebar, text=ch, variable=self.active_chart,
                                value=ch, command=self._draw_main_chart,
                                bg=PANEL_BG, fg=TEXT_PRI, selectcolor=PANEL_BG,
                                activebackground=PANEL_BG, activeforeground=ACCENT1,
                                font=("Segoe UI", 9), padx=16, pady=3,
                                indicatoron=True)
            rb.pack(anchor="w")

    def _filter_block(self, parent, label, var, options):
        tk.Frame(parent, bg=PANEL_BG, height=6).pack()
        tk.Label(parent, text=label, font=("Segoe UI", 9, "bold"),
                 bg=PANEL_BG, fg=TEXT_PRI, padx=14).pack(anchor="w")
        combo = ttk.Combobox(parent, textvariable=var, values=options,
                             state="readonly", width=22)
        combo.pack(padx=14, pady=(2,0), fill="x")
        combo.bind("<<ComboboxSelected>>", lambda e: None)
        self._style_combobox(combo)

    def _style_combobox(self, combo):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=CARD_BG, background=CARD_BG,
                         foreground=TEXT_PRI, selectbackground=ACCENT2,
                         selectforeground=TEXT_PRI, bordercolor=BORDER,
                         arrowcolor=ACCENT1, insertcolor=TEXT_PRI)
        style.map("TCombobox", fieldbackground=[("readonly", CARD_BG)],
                  foreground=[("readonly", TEXT_PRI)])

    def _build_kpi_row(self, parent):
        kpi_frame = tk.Frame(parent, bg=DARK_BG)
        kpi_frame.pack(fill="x", pady=(8,6))

        cards_data = [
            ("Total Revenue",  "💰", ACCENT1),
            ("Total Profit",   "📈", ACCENT3),
            ("Total Units",    "📦", ACCENT2),
            ("Avg Margin",     "🎯", ACCENT4),
            ("Transactions",   "🔢", ACCENT5),
        ]
        self.kpi_cards = {}
        for i, (title, icon, color) in enumerate(cards_data):
            card = KPICard(kpi_frame, title=title, value="—", subtitle="Loading...",
                           accent=color, icon=icon)
            card.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)
            self.kpi_cards[title] = card

    def _build_chart_area(self, parent):
        charts_container = tk.Frame(parent, bg=DARK_BG)
        charts_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Main chart (left-big)
        self.main_chart_frame = tk.Frame(charts_container, bg=CARD_BG,
                                          highlightbackground=BORDER,
                                          highlightthickness=1)
        self.main_chart_frame.pack(side="left", fill="both", expand=True,
                                    padx=(0,6), pady=6)

        # Side charts (right column)
        right_col = tk.Frame(charts_container, bg=DARK_BG, width=380)
        right_col.pack(side="left", fill="y", pady=6)
        right_col.pack_propagate(False)

        self.top_prod_frame = tk.Frame(right_col, bg=CARD_BG,
                                        highlightbackground=BORDER,
                                        highlightthickness=1)
        self.top_prod_frame.pack(fill="both", expand=True, pady=(0,6))

        self.donut_frame = tk.Frame(right_col, bg=CARD_BG,
                                     highlightbackground=BORDER,
                                     highlightthickness=1)
        self.donut_frame.pack(fill="both", expand=True)

    # ── FILTER LOGIC ──
    def _apply_filters(self):
        df = self.df_raw.copy()
        if self.year_var.get() != "All":
            df = df[df["Date"].dt.year == int(self.year_var.get())]
        if self.region_var.get() != "All":
            df = df[df["Region"] == self.region_var.get()]
        if self.category_var.get() != "All":
            df = df[df["Category"] == self.category_var.get()]
        if self.person_var.get() != "All":
            df = df[df["SalesPerson"] == self.person_var.get()]
        self.df = df
        self._update_kpis()
        self._update_stats()
        self._draw_main_chart()
        self._draw_top_products()
        self._draw_donut()

    def _reset_filters(self):
        self.year_var.set("All")
        self.region_var.set("All")
        self.category_var.set("All")
        self.person_var.set("All")
        self._apply_filters()

    # ── KPI UPDATE ──
    def _update_kpis(self):
        df = self.df
        if df.empty:
            return
        total_rev   = df["Revenue"].sum()
        total_prof  = df["Profit"].sum()
        total_units = df["Units"].sum()
        avg_margin  = df["ProfitMargin"].mean()
        transactions= len(df)

        prev = self.df_raw[self.df_raw["Date"] < df["Date"].min()] if not df.empty else pd.DataFrame()

        self.kpi_cards["Total Revenue"].update_value(
            f"${total_rev:,.0f}", f"Avg/day: ${total_rev/max(1,(df['Date'].max()-df['Date'].min()).days):,.0f}")
        self.kpi_cards["Total Profit"].update_value(
            f"${total_prof:,.0f}", f"Margin: {avg_margin:.1f}%")
        self.kpi_cards["Total Units"].update_value(
            f"{total_units:,}", f"Avg order: {total_units/max(1,transactions):.1f} units")
        self.kpi_cards["Avg Margin"].update_value(
            f"{avg_margin:.1f}%", f"COGS: ${df['COGS'].sum():,.0f}")
        self.kpi_cards["Transactions"].update_value(
            f"{transactions:,}", f"Products: {df['Product'].nunique()}")

    def _update_stats(self):
        df = self.df
        if df.empty:
            return
        self.stats_labels["Records"].config(text=f"{len(df):,}")
        dr = f"{df['Date'].min().strftime('%b %Y')} – {df['Date'].max().strftime('%b %Y')}"
        self.stats_labels["Date Range"].config(text=dr)
        self.stats_labels["Products"].config(text=str(df["Product"].nunique()))
        self.stats_labels["Avg Margin"].config(text=f"{df['ProfitMargin'].mean():.1f}%")

    # ── CHART: MAIN ──
    def _draw_main_chart(self):
        for w in self.main_chart_frame.winfo_children():
            w.destroy()

        chart = self.active_chart.get()
        title_map = {
            "Revenue Trend":      "📈 Revenue & Profit Trend Over Time",
            "Product Performance":"🏆 Product Performance Analysis",
            "Regional Map":       "🗺  Sales by Region",
            "Category Breakdown": "📊 Category Revenue Breakdown",
            "Profit Analysis":    "💹 Profit Margin Analysis",
            "Heatmap":            "🔥 Sales Heatmap (Month × Weekday)",
        }
        lbl_frame = tk.Frame(self.main_chart_frame, bg=CARD_BG)
        lbl_frame.pack(fill="x", padx=16, pady=(10,4))
        tk.Label(lbl_frame, text=title_map.get(chart,"Chart"),
                 font=("Segoe UI", 12, "bold"), bg=CARD_BG, fg=TEXT_PRI).pack(side="left")

        fig = Figure(figsize=(9,4.6), dpi=96)
        fig.patch.set_facecolor(CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(DARK_BG)

        df = self.df
        if df.empty:
            ax.text(0.5,0.5,"No data for selected filters",
                    ha="center", va="center", color=TEXT_SEC, fontsize=14,
                    transform=ax.transAxes)
        elif chart == "Revenue Trend":
            self._chart_revenue_trend(ax, fig, df)
        elif chart == "Product Performance":
            self._chart_product_perf(ax, df)
        elif chart == "Regional Map":
            self._chart_regional(ax, df)
        elif chart == "Category Breakdown":
            self._chart_category(ax, df)
        elif chart == "Profit Analysis":
            self._chart_profit(ax, df)
        elif chart == "Heatmap":
            self._chart_heatmap(ax, fig, df)

        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, self.main_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=(0,6))

        toolbar_frame = tk.Frame(self.main_chart_frame, bg=PANEL_BG)
        toolbar_frame.pack(fill="x")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.config(bg=PANEL_BG)
        toolbar.update()

    def _chart_revenue_trend(self, ax, fig, df):
        monthly = df.resample("ME", on="Date").agg(
            Revenue=("Revenue","sum"), Profit=("Profit","sum")).reset_index()
        x = np.arange(len(monthly))

        ax.fill_between(monthly["Date"], monthly["Revenue"], alpha=0.15, color=ACCENT1)
        ax.fill_between(monthly["Date"], monthly["Profit"],  alpha=0.15, color=ACCENT3)
        ax.plot(monthly["Date"], monthly["Revenue"], color=ACCENT1, lw=2.5,
                marker="o", markersize=4, label="Revenue")
        ax.plot(monthly["Date"], monthly["Profit"],  color=ACCENT3, lw=2.5,
                marker="s", markersize=4, label="Profit", linestyle="--")

        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1000:.0f}k"))
        ax.set_xlabel("Month", fontsize=9)
        ax.set_ylabel("Amount (USD)", fontsize=9)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.spines[["top","right"]].set_visible(False)

        # Trend line
        if len(monthly) > 2:
            z = np.polyfit(x, monthly["Revenue"], 1)
            p = np.poly1d(z)
            ax.plot(monthly["Date"], p(x), "--", color=ACCENT4, lw=1.5,
                    alpha=0.7, label="Trend")
            ax.legend(fontsize=9)

    def _chart_product_perf(self, ax, df):
        prod = df.groupby("Product").agg(
            Revenue=("Revenue","sum"), Units=("Units","sum"),
            Margin=("ProfitMargin","mean")).nlargest(10,"Revenue").reset_index()

        bars = ax.barh(prod["Product"], prod["Revenue"],
                       color=CHART_COLORS[:len(prod)], edgecolor="none", height=0.6)
        for bar, rev in zip(bars, prod["Revenue"]):
            ax.text(bar.get_width() + prod["Revenue"].max()*0.01, bar.get_y()+bar.get_height()/2,
                    f"${rev/1000:.1f}k", va="center", color=TEXT_SEC, fontsize=8)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1000:.0f}k"))
        ax.set_xlabel("Total Revenue", fontsize=9)
        ax.invert_yaxis()
        ax.spines[["top","right","left"]].set_visible(False)
        ax.grid(axis="x", alpha=0.3)

    def _chart_regional(self, ax, df):
        reg = df.groupby("Region").agg(
            Revenue=("Revenue","sum"), Profit=("Profit","sum"),
            Units=("Units","sum")).reset_index().sort_values("Revenue", ascending=False)

        x = np.arange(len(reg))
        w = 0.3
        b1 = ax.bar(x-w, reg["Revenue"], w, label="Revenue", color=ACCENT1, alpha=0.85)
        b2 = ax.bar(x,   reg["Profit"],  w, label="Profit",  color=ACCENT3, alpha=0.85)
        b3 = ax.bar(x+w, reg["Units"],   w, label="Units",   color=ACCENT2, alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(reg["Region"], fontsize=9)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1000:.0f}k" if x >= 1000 else str(int(x))))
        ax.legend(fontsize=9)
        ax.spines[["top","right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3)

    def _chart_category(self, ax, df):
        cat = df.groupby("Category")["Revenue"].sum().reset_index()
        cat = cat.sort_values("Revenue", ascending=False)
        colors = CHART_COLORS[:len(cat)]

        wedges, texts, autotexts = ax.pie(
            cat["Revenue"], labels=cat["Category"], colors=colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops=dict(edgecolor=DARK_BG, linewidth=2),
            pctdistance=0.82)
        for t in texts:      t.set_color(TEXT_PRI); t.set_fontsize(9)
        for t in autotexts:  t.set_color(DARK_BG);  t.set_fontsize(8); t.set_fontweight("bold")

        # Donut
        centre = plt.Circle((0,0), 0.6, fc=DARK_BG)
        ax.add_patch(centre)
        total = cat["Revenue"].sum()
        ax.text(0, 0, f"${total/1e6:.1f}M\nTotal", ha="center", va="center",
                color=TEXT_PRI, fontsize=11, fontweight="bold",
                transform=ax.transData)

    def _chart_profit(self, ax, df):
        prod = df.groupby("Product").agg(
            Revenue=("Revenue","sum"), Profit=("Profit","sum"),
            Margin=("ProfitMargin","mean"), Units=("Units","sum")).reset_index()

        sc = ax.scatter(prod["Revenue"], prod["Margin"],
                        s=prod["Units"]/prod["Units"].max()*800+100,
                        c=prod["Profit"], cmap="RdYlGn", alpha=0.85,
                        edgecolors=DARK_BG, linewidths=1.5)

        for _, row in prod.iterrows():
            ax.annotate(row["Product"].split()[0], (row["Revenue"], row["Margin"]),
                        textcoords="offset points", xytext=(6,4),
                        fontsize=7.5, color=TEXT_SEC)

        plt.colorbar(sc, ax=ax, label="Profit ($)", pad=0.01)
        ax.set_xlabel("Revenue ($)", fontsize=9)
        ax.set_ylabel("Profit Margin (%)", fontsize=9)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1000:.0f}k"))
        ax.axhline(df["ProfitMargin"].mean(), color=ACCENT4, lw=1.5, ls="--", alpha=0.7,
                   label=f"Avg Margin: {df['ProfitMargin'].mean():.1f}%")
        ax.legend(fontsize=9)
        ax.spines[["top","right"]].set_visible(False)
        ax.grid(alpha=0.3)

    def _chart_heatmap(self, ax, fig, df):
        df2 = df.copy()
        df2["Month"]   = df2["Date"].dt.strftime("%b")
        df2["Weekday"] = df2["Date"].dt.day_name()
        month_order   = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

        pivot = df2.pivot_table(values="Revenue", index="Weekday", columns="Month",
                                aggfunc="sum", fill_value=0)
        pivot = pivot.reindex(index=[w for w in weekday_order if w in pivot.index],
                              columns=[m for m in month_order if m in pivot.columns])

        cmap = sns.color_palette("mako", as_cmap=True)
        im = ax.imshow(pivot.values, aspect="auto", cmap=cmap)

        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, fontsize=8, color=TEXT_SEC)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=8, color=TEXT_SEC)

        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i,j]
                ax.text(j, i, f"${val/1000:.0f}k", ha="center", va="center",
                        fontsize=6.5, color="white" if val > pivot.values.max()*0.4 else TEXT_SEC)

        fig.colorbar(im, ax=ax, label="Revenue ($)", pad=0.01)

    # ── SIDE CHART: TOP PRODUCTS ──
    def _draw_top_products(self):
        for w in self.top_prod_frame.winfo_children():
            w.destroy()

        header = tk.Frame(self.top_prod_frame, bg=CARD_BG)
        header.pack(fill="x", padx=12, pady=(8,4))
        tk.Label(header, text="🏅 Top Products by Revenue",
                 font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEXT_PRI).pack(side="left")

        fig = Figure(figsize=(4, 3.6), dpi=90)
        fig.patch.set_facecolor(CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(DARK_BG)

        df = self.df
        if not df.empty:
            top = df.groupby("Product")["Revenue"].sum().nlargest(6)
            colors = [ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5, "#06B6D4"]

            bars = ax.bar(range(len(top)), top.values, color=colors[:len(top)],
                          edgecolor="none", width=0.65)
            ax.set_xticks(range(len(top)))
            ax.set_xticklabels([p.split()[0] for p in top.index], fontsize=7.5, rotation=25)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1000:.0f}k"))
            ax.spines[["top","right"]].set_visible(False)
            ax.grid(axis="y", alpha=0.3)

            for bar, val in zip(bars, top.values):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+top.values.max()*0.01,
                        f"${val/1000:.1f}k", ha="center", va="bottom", fontsize=7, color=TEXT_SEC)

        fig.tight_layout(pad=1.2)
        canvas = FigureCanvasTkAgg(fig, self.top_prod_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=(0,6))

    # ── SIDE CHART: DONUT ──
    def _draw_donut(self):
        for w in self.donut_frame.winfo_children():
            w.destroy()

        header = tk.Frame(self.donut_frame, bg=CARD_BG)
        header.pack(fill="x", padx=12, pady=(8,4))
        tk.Label(header, text="🍩 Revenue by Region",
                 font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEXT_PRI).pack(side="left")

        fig = Figure(figsize=(4, 3.6), dpi=90)
        fig.patch.set_facecolor(CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)

        df = self.df
        if not df.empty:
            reg = df.groupby("Region")["Revenue"].sum()
            colors = CHART_COLORS[:len(reg)]

            wedges, texts, autotexts = ax.pie(
                reg.values, labels=reg.index, colors=colors,
                autopct="%1.0f%%", startangle=90, pctdistance=0.78,
                wedgeprops=dict(edgecolor=CARD_BG, linewidth=2, width=0.55))
            for t in texts:     t.set_color(TEXT_SEC); t.set_fontsize(8)
            for t in autotexts: t.set_color("white");  t.set_fontsize(7.5)

            total = reg.sum()
            ax.text(0, 0, f"${total/1000:.0f}k", ha="center", va="center",
                    color=TEXT_PRI, fontsize=11, fontweight="bold")

        fig.tight_layout(pad=0.8)
        canvas = FigureCanvasTkAgg(fig, self.donut_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=(0,6))

    # ── ACTIONS ──
    def _import_data(self):
        path = filedialog.askopenfilename(
            title="Import Sales Data",
            filetypes=[("CSV files","*.csv"), ("Excel files","*.xlsx *.xls"),
                       ("All files","*.*")])
        if not path:
            return
        try:
            if path.endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)

            required = {"Date","Revenue","Profit"}
            missing  = required - set(df.columns)
            if missing:
                messagebox.showwarning("Column Warning",
                    f"Missing columns: {missing}\nDashboard may have limited functionality.")

            # Auto-parse date
            for col in df.columns:
                if "date" in col.lower():
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                    df = df.rename(columns={col:"Date"})
                    break

            # Fill missing numeric columns
            for col in ["Revenue","Profit","Units","ProfitMargin","COGS"]:
                if col not in df.columns:
                    df[col] = 0

            for col in ["Product","Category","Region","SalesPerson"]:
                if col not in df.columns:
                    df[col] = "Unknown"

            self.df_raw = df
            self._apply_filters()
            messagebox.showinfo("Import Success",
                f"✅ Loaded {len(df):,} records from:\n{path}")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files","*.csv")],
            initialfile=f"sales_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
        if path:
            self.df.to_csv(path, index=False)
            messagebox.showinfo("Export", f"✅ Exported {len(self.df):,} rows to:\n{path}")

    def _export_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files","*.pdf")],
            initialfile=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
        if not path:
            return
        try:
            from matplotlib.backends.backend_pdf import PdfPages
            df = self.df
            with PdfPages(path) as pdf:
                # Page 1: Revenue Trend
                fig, axes = plt.subplots(2, 2, figsize=(16,10), facecolor=DARK_BG)
                fig.suptitle("Sales & Revenue Analysis Report", color=TEXT_PRI,
                             fontsize=18, fontweight="bold", y=0.98)

                for ax in axes.flat:
                    ax.set_facecolor(CARD_BG)

                if not df.empty:
                    # Revenue trend
                    monthly = df.resample("ME", on="Date").agg(
                        Revenue=("Revenue","sum"), Profit=("Profit","sum")).reset_index()
                    axes[0,0].plot(monthly["Date"], monthly["Revenue"], color=ACCENT1, lw=2)
                    axes[0,0].plot(monthly["Date"], monthly["Profit"],  color=ACCENT3, lw=2, ls="--")
                    axes[0,0].set_title("Revenue & Profit Trend", color=TEXT_PRI)

                    # Top products
                    top = df.groupby("Product")["Revenue"].sum().nlargest(8)
                    axes[0,1].barh(top.index, top.values, color=CHART_COLORS[:len(top)])
                    axes[0,1].set_title("Top Products", color=TEXT_PRI)
                    axes[0,1].invert_yaxis()

                    # Region
                    reg = df.groupby("Region")["Revenue"].sum()
                    axes[1,0].bar(reg.index, reg.values, color=CHART_COLORS[:len(reg)])
                    axes[1,0].set_title("Revenue by Region", color=TEXT_PRI)

                    # Category
                    cat = df.groupby("Category")["Revenue"].sum()
                    axes[1,1].pie(cat.values, labels=cat.index,
                                  colors=CHART_COLORS[:len(cat)], autopct="%1.1f%%",
                                  wedgeprops=dict(edgecolor=DARK_BG))
                    axes[1,1].set_title("Category Breakdown", color=TEXT_PRI)

                plt.tight_layout()
                pdf.savefig(fig, facecolor=DARK_BG)
                plt.close(fig)

            messagebox.showinfo("PDF Export", f"✅ Report saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("PDF Error", str(e))

    def _reload_sample(self):
        self.df_raw = generate_sample_data()
        self._reset_filters()
        messagebox.showinfo("Sample Data", "✅ Fresh sample data loaded!")


# ─────────────────────────── ENTRY POINT ───────────────────────────
if __name__ == "__main__":
    app = SalesDashboard()
    app.mainloop()
