from bokeh.models import ColumnDataSource, BooleanFilter, CDSView, Band, Range1d, LinearAxis, BoxAnnotation, Span
from bokeh.models import HoverTool,WheelZoomTool, PanTool, ResetTool, CrosshairTool, BoxSelectTool, BoxZoomTool, SaveTool
from bokeh.io import show, output_notebook, curdoc, export_png
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row, column, layout
from bokeh.models.formatters import PrintfTickFormatter, NumeralTickFormatter, DatetimeTickFormatter
from bokeh.palettes import Blues, Reds, Purples, Oranges, Greens, Greys, YlGn, RdPu, Category10, Category20, Category20b, Set1, Set2, Set3

from typing import List, Tuple, Union
import datetime
import numpy as np
import pandas as pd

from danbi.extlib.stock import genBaseIndicator

tools = [PanTool(), WheelZoomTool(), ResetTool(), CrosshairTool(), BoxSelectTool(), BoxZoomTool(), SaveTool()]


def setJupyterNotebookBokehEnable():
    from bokeh.resources import INLINE
    output_notebook(resources=INLINE)


def showPandas(df: pd.DataFrame, xlist: Union[str, List[str]], ylist: List[Tuple[str, str]], typeList: Union[str, List[List[str]]] = "line", width: int = 1500, height: int = 400, col_dir: bool = True, sync_axis: str = "xy", graph_widths: Union[int, List[int]] = 1, line_colors: List[str] = None, hover=True, **options):
    cds = ColumnDataSource(df)
    
    toolbar_location = options.get("toolbar_location", "above")
    legend_location = options.get("legend_location", "top_right")
    local_tools = options.get("tools", tools)
    title = options.get("title", "Learning History")
    title_size = options.get("title_size", "11pt")
    format_datetime = options.get("format_datetime", "%Y-%m-%d")
    COLOR = [Category20b[20][idx] for idx in range(1, 20, 4)] + list(Set1[9]) + list(Category10[10]) + [Category20[20][idx] for idx in range(0, 20, 2)] + list(Set2[8]) + \
        [Category20b[20][idx] for idx in range(0, 20, 4)] + [Category20[20][idx] for idx in range(1, 20, 2)] + \
        list(Set3[12]) + [Category20b[20][idx] for idx in range(2, 20, 4)] + [Category20b[20][idx] for idx in range(3, 20, 4)]
    
    len_y = len(ylist)
    if col_dir:
        width = int(width/len_y)
    else:
        height = int(height/len_y)
    
    if isinstance(xlist, str):
        xlist = [xlist for _ in range(len_y)]
    if isinstance(typeList, str):
        typeList = [typeList for _ in range(len_y)]
    
    plot_figures = []
    for idx, (xname, ynames) in enumerate(zip(xlist, ylist)):
        fig = figure(plot_width=width, plot_height=height, title=" & ".join(ynames), tools=local_tools, toolbar_location=toolbar_location)

        if isinstance(graph_widths, int):
            graph_widths = [graph_widths for _ in range(len(ynames))]
        else:
            if len(graph_widths) < len(ynames):
                for _ in range(len(graph_widths), len(ynames)):
                    graph_widths.append(graph_widths[-1])
        tooltips = [(f"{xname}", f"@{xname}")]
        types = typeList[idx]
        if isinstance(types, str):
            types = [types for _ in range(len(ynames))]
        for idx, name in enumerate(ynames):
            if types[idx] == "line":
                fig_each = fig.line(x=xname, y=name, source=cds, line_width=graph_widths[idx], color=COLOR[idx % 50], legend_label=name, alpha=0.8, muted_alpha=0.02)
            elif types[idx] == "scatter":
                fig_each = fig.scatter(x=xname, y=name, source=cds, size=graph_widths[idx], color=COLOR[idx % 50], legend_label=name, alpha=0.8, muted_alpha=0.02)
            
            if idx == 0:
                fig_base = fig_each
            tooltips.append((f"{name}", f"@{name}"))
        if hover:
            fig.add_tools(HoverTool(
                tooltips=tooltips,
                mode="vline",
                renderers=[fig_base]
            ))
        fig.title.text_font_size = title_size
        fig.grid.grid_line_alpha = 0.3
        fig.legend.border_line_alpha = 0
        fig.legend.background_fill_alpha = 0
        fig.legend.click_policy = "mute"
        fig.legend.location = legend_location
        if isinstance(cds.data[xname][0], datetime.date):
            fig.xaxis.formatter = DatetimeTickFormatter(years=[format_datetime], months=[format_datetime], days=[format_datetime])

        plot_figures.append(fig)
    
    if sync_axis is not None:
        for plot1 in plot_figures:
            for plot2 in plot_figures:
                if "x" in sync_axis:
                    plot1.x_range = plot2.x_range
                if "y" in sync_axis:
                    plot1.y_range = plot2.y_range

    chart_rows = gridplot([plot_figures] if col_dir else [[plot] for plot in plot_figures])
    curdoc().add_root(chart_rows)
    show(chart_rows)


def showTensorflowLearningHistory(history, width: int = 1500, height: int = 400, legend: str = "bottm_left"):
    ylist = []
    keys = history.history.keys()
    for key in keys:
        if not key.startswith("val_"):
            validation = "val_"+key
            if validation in keys:
                ylist.append([key, "val_"+key])
            else:
                ylist.append([key])
            
    showPandas(
        pd.DataFrame(history.history), "index", ylist, "line", 1500, 400, True, "x", [2, 1],
        {"legend_location": legend}
    )


def showAsRows(plots: List[figure], sync_axis: str = "xy"):
    for plot1 in plots:
        for plot2 in plots:
            if "x" in sync_axis:
                plot1.x_range = plot2.x_range
            if "y" in sync_axis:
                plot1.y_range = plot2.y_range
    
    chart_rows = gridplot([[plot] for plot in plots])
    curdoc().add_root(chart_rows)
    show(chart_rows)


def showAsGrid(plots: List[List[Union[figure, List[figure]]]], sync_axis: str = "xy"):
    plots_flat = sum(plots, [])
    for plot1 in plots_flat:
        for plot2 in plots_flat:
            if "x" in sync_axis:
                plot1.x_range = plot2.x_range
            if "y" in sync_axis:
                plot1.y_range = plot2.y_range
    
    grid = []
    for rows in plots:
        row = []
        for cols in rows:
            if isinstance(cols, list):
                col = column(cols)
                row.append(col)
            else:
                row.append(cols)
        grid.append(row)
    
    chart_rows = gridplot(grid)
    curdoc().add_root(chart_rows)
    show(chart_rows)


def _figLine(fig, x, y, source, line_width, color, alpha, legend_label, y_range_name=None):
    if y_range_name:
        line = fig.line(x=x, y=y, source=source, line_width=line_width, color=color, alpha=alpha, legend_label=legend_label, muted_alpha=0.05, y_range_name=y_range_name)
        fig.circle(x=x, y=y, source=source, radius=0, y_range_name=y_range_name)
    else:
        line = fig.line(x=x, y=y, source=source, line_width=line_width, color=color, alpha=alpha, legend_label=legend_label, muted_alpha=0.05)
        fig.circle(x=x, y=y, source=source, radius=0)
    
    return line


def _setStyle(fig, location="top_left"):
    fig.title.text_font_size = "12pt"
    fig.grid.grid_line_alpha = 0.3
    fig.yaxis.formatter = NumeralTickFormatter(format="0,0[.]00")
    fig.xaxis.formatter = DatetimeTickFormatter(years=["%Y-%m-%d"], months=["%Y-%m-%d"], days=["%Y-%m-%d"])

    fig.legend.border_line_alpha = 0
    fig.legend.background_fill_alpha = 0
    fig.legend.padding = -5
    fig.legend.spacing = -4
    fig.legend.click_policy = "mute"
    fig.legend.location = location
    fig.legend.label_text_font_size = "9pt"


def getBokehDataSource(df: pd.DataFrame) -> ColumnDataSource:
    return ColumnDataSource(df)


def showCandleBollingerIchimoku(df: pd.DataFrame, width: int = 1000, height: int = 300, **options):
    if "mavolu" not in df:
        df = genBaseIndicator(df)
    cds = ColumnDataSource(df)
    show(plotCandleBollingerIchimoku(cds, width, height, **options))


def plotCandleBollingerIchimoku(cds: ColumnDataSource, width: int = 1000, height: int = 300, candle: bool = True, bollinger: bool = True, ma: bool = True, vol_ma: bool = True, ichimoku: bool = True, trade: bool = True, **options):
    toolbar_location = options.get("toolbar_location", "above")
    local_tools = options.get("tools", tools)
    title = options.get("title", "Candle & Boillinger Bands & Ichimoku")
    trade_symbol_size = options.get("trade_symbol_size", 12)
    BLUE, RED, ORANGE, GREEN, GRAY, RDPU = Blues[9], Reds[9], Oranges[9], Greens[9], Greys[9], RdPu[9]
    fig = figure(plot_width=width, plot_height=height, x_axis_type="datetime", title=title, tools=local_tools, toolbar_location=toolbar_location)
    
    base_line = fig.line(x="reg_day", y="close", source=cds, line_width=0, color="green", alpha=0)
    
    # Bollenger Bands
    if bollinger:
        fig.varea(x='reg_day', y1='bbl', y2='bbu', source=cds, fill_alpha=0.3, fill_color=BLUE[6], legend_label = "bollinger bands", muted_alpha=0)
    
    # Candle Chart
    if candle:
        inc = cds.data["open"] <= cds.data["close"]
        dec = cds.data["close"] < cds.data["open"]
        view_inc = CDSView(source=cds, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=cds, filters=[BooleanFilter(dec)])
        width = 12*60*60*1500
        fig.segment(x0="reg_day", x1="reg_day", y0="low", y1="high", color=RED[1], source=cds, view=view_inc, legend_label="candle", muted_alpha=0)
        fig.segment(x0="reg_day", x1="reg_day", y0="low", y1="high", color=BLUE[1], source=cds, view=view_dec, legend_label="candle", muted_alpha=0)
        fig.vbar(x='reg_day', width=width, top='open', bottom='close', fill_color=RED[1], line_color=RED[1], source=cds, view=view_inc, legend_label="candle", muted_alpha=0)
        fig.vbar(x='reg_day', width=width, top='open', bottom='close', fill_color=BLUE[1], line_color=BLUE[1], source=cds, view=view_dec, legend_label="candle", muted_alpha=0)
    
    # Moving Average
    if ma:
        _figLine(fig, 'reg_day', 'ma5',  cds, 1.2, RED[2],   0.5, 'ma5')
        _figLine(fig, 'reg_day', 'ma20', cds, 1.6, BLUE[0],   0.5, 'ma20')
        _figLine(fig, 'reg_day', 'ma60', cds, 2, ORANGE[3], 0.8, 'ma60')
    
    # Ichimoku
    if ichimoku and "imspan2" in cds.data:
        _figLine(fig, 'reg_day', 'imspan2', cds, 1.1, GRAY[0], 0.7, 'ichimoku cloud')
        _figLine(fig, 'reg_day', 'imspan1', cds, 1, GRAY[3], 0.7, 'ichimoku cloud')
        fig.varea(x='reg_day', y1='imspan2', y2='imspan1', source=cds, fill_alpha=0.3, fill_color=GRAY[6], legend_label = "ichimoku cloud", muted_alpha=0)
        _figLine(fig, 'reg_day', 'imbase', cds, 1.8, GREEN[0], 0.7, 'ichimoku base line')
        _figLine(fig, 'reg_day', 'imtrans', cds, 1.4, GREEN[1], 0.7, 'ichimoku transition line')
        _figLine(fig, 'reg_day', 'imtail', cds, 1.4, RDPU[2], 0.7, 'ichimoku trailing line')

    # Volume Moving Average
    if vol_ma:
        fig.y_range = Range1d(min(cds.data["close"]) * 0.9, max(cds.data["close"])*1.1)
        if "mavolu" in cds.data:
            fig.extra_y_ranges = {'volume': Range1d(np.nanmin(cds.data["mavolu"])*0.9, np.nanmax(cds.data["mavolu"])*1.1)}
            fig.add_layout(LinearAxis(y_range_name='volume'), 'right')
            _ = _figLine(fig, 'reg_day', 'mavolu',  cds, 2, ORANGE[6], 0.7, "ma_volume", "volume")
    
    # Trade
    if trade and ("env_buy" in cds.data):
        fig.scatter(x="reg_day", y="env_buy", source=cds, size=trade_symbol_size, color="red", marker="triangle", legend_label="trade buy", muted_alpha=0.05)
        fig.scatter(x="reg_day", y="env_sell", source=cds, size=trade_symbol_size, color="blue", marker="inverted_triangle", legend_label="trade sell", muted_alpha=0.05)

    _setStyle(fig)
    fig.add_tools(HoverTool(
        tooltips=[
            ("date", "@reg_day{%F}"),
            ("close", "@close{,}"),
            ("high", "@high{,}"),
            ("low", "@low{,}"),
            ("open", "@open{,}"),
            ("ma5", "@ma5{,}"),
            ("ma20", "@ma20{,}"),
            ("ma60", "@ma60{,}"),
            ("ma_volume", "@mavolu{,}"),
        ],
        formatters={
            "@reg_day": "datetime"
        },
        mode="vline",
        renderers=[base_line]
    ))

    return fig


def showMovingAverage(df: pd.DataFrame, width: int = 1000, height: int = 300, **options):
    if "mavolu" not in df:
        genBaseIndicator(df)
    cds = ColumnDataSource(df)
    show(plotMovingAverage(cds, width, height, **options))


def plotMovingAverage(cds: ColumnDataSource, width: int = 1000, height: int = 300, **options):
    toolbar_location = options.get("toolbar_location", "above")
    local_tools = options.get("tools", tools)
    title = options.get("title", "Moving Average")
    COLOR = Category20[20]
    
    # Moving Average
    fig = figure(plot_width=width, plot_height=height, x_axis_type="datetime", title=title, tools=local_tools, toolbar_location=toolbar_location)
    base_line = _figLine(fig, 'reg_day', 'ma5',   cds, 1, COLOR[0],  0.6, 'ma5')
    _figLine(fig, 'reg_day', 'ma10',  cds, 1, COLOR[18], 0.6, 'ma10')
    _figLine(fig, 'reg_day', 'ma20',  cds, 1, COLOR[8],  0.9, 'ma20')
    _figLine(fig, 'reg_day', 'ma60',  cds, 2, COLOR[2],  0.7, 'ma60')
    _figLine(fig, 'reg_day', 'ma120', cds, 2, COLOR[16], 1,   'ma120')
    fig.y_range = Range1d(min(cds.data["close"]) * 0.7, max(cds.data["close"])*1.05)
    
    fig.extra_y_ranges = {'volume': Range1d(np.nanmin(cds.data["volume"]), np.nanmax(cds.data["volume"])*1.5)}
    fig.add_layout(LinearAxis(y_range_name='volume'), 'right')
    fig.vbar(x='reg_day', top='volume', source=cds, bottom=0, width=30000000, color=COLOR[11], alpha=0.5, muted_alpha=0.1, legend_label='volume', y_range_name="volume")
    
    _setStyle(fig)
    fig.add_tools(HoverTool(
        tooltips=[
            ("date", "@reg_day{%F}"),
            ("ma5", "@ma5{,}"),
            ("ma20", "@ma20{,}"),
            ("ma60", "@ma60{,}"),
            ("ma120", "@ma120{,}"),
            ("volume", "@volume{,}"),
        ],
        formatters={
            "@reg_day": "datetime"
        },
        mode="vline",
        renderers=[base_line]
    ))
    
    return fig


def showMacd(df: pd.DataFrame, width: int = 1000, height: int = 300, **options):
    if "mavolu" not in df:
        genBaseIndicator(df)
    cds = ColumnDataSource(df)
    show(plotMacd(cds, width, height, **options))


def plotMacd(cds: ColumnDataSource, width: int = 1000, height: int = 300, **options):
    toolbar_location = options.get("toolbar_location", "above")
    local_tools = options.get("tools", tools)
    title = options.get("title", "MACD")
    COLOR = Category20b[20]
    
    # Moving Average
    fig = figure(plot_width=width, plot_height=height, x_axis_type="datetime", title=title, tools=local_tools, toolbar_location=toolbar_location)
    
    inc = cds.data["macdh"] >= 0
    dec = cds.data["macdh"] < 0
    view_inc = CDSView(source=cds, filters=[BooleanFilter(inc)])
    view_dec = CDSView(source=cds, filters=[BooleanFilter(dec)])
    
    fig.vbar(x='reg_day', top='macdh', bottom=0, width=30000000, color=COLOR[14], source=cds, view=view_inc, muted_alpha=0.1, legend_label='histogram')
    fig.vbar(x='reg_day', top='macdh', bottom=0, width=30000000, color=COLOR[2], source=cds, view=view_dec, muted_alpha=0.1, legend_label='histogram')
    base_line = fig.line(x='reg_day', y='macd', line_width=2, color=COLOR[2], alpha=0.7, source=cds, legend_label='macd', muted_alpha=0)
    fig.line(x='reg_day', y='macds', line_width=2, color=COLOR[6], alpha=0.7, source=cds, legend_label='signal', muted_alpha=0)
    fig.renderers.extend([Span(location=0, dimension='width', line_color="forestgreen", line_width=0.5)])
    
    _setStyle(fig)
    fig.add_tools(HoverTool(
        tooltips=[
            ("date", "@reg_day{%F}"),
            ("macd", "@macd{,}"),
            ("signal", "@macds{,}"),
            ("histogram", "@macdh{,}"),
        ],
        formatters={
            "@reg_day": "datetime"
        },
        mode="vline",
        renderers=[base_line]
    ))
    
    return fig


def showTimeseriesLines(df: pd.DataFrame, width: int, height: int, x: str = "reg_day", ylist: list = [], **options):
    cds = ColumnDataSource(df)
    show(plotTimeseriesLines(cds, width, height, x, ylist, **options))


def plotTimeseriesLines(cds: ColumnDataSource, width: int = 1000, height: int = 300, x: str = "reg_day", ylist: list = [], trade: bool = False, **options):
    toolbar_location = options.get("toolbar_location", "above")
    local_tools = options.get("tools", tools)
    title = options.get("title", "Timeseries Lines")
    base_y = options.get("base_y", 0)
    area = options.get("area", [])
    trade_symbol_size = options.get("trade_symbol_size", 12)
    legend = options.get("legend", {})
    
    COLOR = Category20[20]
    tooltips = []
    fig = figure(plot_width=width, plot_height=height, x_axis_type="datetime", title=title, tools=local_tools, toolbar_location=toolbar_location)
    
    for idx, y in enumerate(ylist):
        legend_label = legend[y] if y in legend else y
        if idx == 0:
            base_line = _figLine(fig, x, y,  cds, 1, COLOR[idx], 0.8, y, legend_label=legend_label)
        else:
            _ = _figLine(fig, x, y,  cds, 1, COLOR[idx*2 if idx < 11 else idx*2-1], 0.6 if idx < 11 else 0.8, y, legend_label=legend_label)
        tooltips.append((y, f"@{y}" + "{,.03f}"))
    fig.renderers.extend([Span(location=base_y, dimension='width', line_color="forestgreen", line_width=0.5)])
    
    if len(area) == 2:
        fig.add_layout(BoxAnnotation(top=area[0], fill_alpha=0.05, fill_color=COLOR[6]))
        fig.add_layout(BoxAnnotation(bottom=area[1], fill_alpha=0.05, fill_color=COLOR[4]))

    # Trade
    if trade and ("mark_up" in cds.data):
        fig.scatter(x=x, y="mark_up", source=cds, size=trade_symbol_size, color="red", marker="triangle", legend_label="up", muted_alpha=0.05)
    if trade and ("mark_dn" in cds.data):
        fig.scatter(x=x, y="mark_dn", source=cds, size=trade_symbol_size, color="blue", marker="inverted_triangle", legend_label="down", muted_alpha=0.05)

    _setStyle(fig)
    fig.add_tools(HoverTool(
        tooltips=[("date", "@"+x+"{%F}")] + tooltips,
        formatters={
            f"@{x}": "datetime"
        },
        mode="vline",
        renderers=[base_line]
    ))
    
    return fig
