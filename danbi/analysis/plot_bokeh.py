from bokeh.models import ColumnDataSource, BooleanFilter, CDSView, Band, Range1d, LinearAxis, BoxAnnotation, Span
from bokeh.models import HoverTool,WheelZoomTool, PanTool, ResetTool, CrosshairTool, BoxSelectTool, BoxZoomTool, SaveTool
from bokeh.io import show, output_notebook, curdoc
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row, column, layout
from bokeh.palettes import Category20, Category20b, Blues, Reds, Purples, Oranges, YlGn
from bokeh.models.formatters import PrintfTickFormatter, NumeralTickFormatter, DatetimeTickFormatter

import numpy as np
import pandas as pd

from .stock import genBaseIndicator

tools = [PanTool(), WheelZoomTool(), ResetTool(), CrosshairTool(), BoxSelectTool(), BoxZoomTool(), SaveTool()]


def setJupyterNotebookBokehEnable():
    from bokeh.resources import INLINE
    output_notebook(resources=INLINE)


def showAsRows(*args):
    chart_rows = gridplot([[chart] for chart in args])
    curdoc().add_root(chart_rows)
    show(chart_rows)


def _figLine(fig, x, y, source, line_width, color, alpha, legend_label, y_range_name=None):
    if y_range_name:
        line = fig.line(x=x, y=y, source=source, line_width=line_width, color=color, alpha=alpha, legend_label=legend_label, muted_alpha=0.1, y_range_name=y_range_name)
        fig.circle(x=x, y=y, source=source, radius=0, y_range_name=y_range_name)
    else:
        line = fig.line(x=x, y=y, source=source, line_width=line_width, color=color, alpha=alpha, legend_label=legend_label, muted_alpha=0.1)
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


def showCandleBollinger(width: int, height: int, df: pd.DataFrame, **options):
    if "mavolu" not in df:
        genBaseIndicator(df)
    cds = ColumnDataSource(df)
    show(plotCandleBollinger(width, height, cds, **options))


def plotCandleBollinger(width: int, height: int, cds: ColumnDataSource, **options):
    toolbar_location = options.get("toolbar_location", "above")
    local_tools = options.get("tools", tools)
    title = options.get("title", "Candle & Boillinger Bands")
    BLUE, RED, ORANGE = Blues[9], Reds[9], Oranges[9]

    # Candle Chart
    fig = figure(plot_width=width, plot_height=height, x_axis_type="datetime", title=title, tools=local_tools, toolbar_location=toolbar_location)
    inc = cds.data["open"] <= cds.data["close"]
    dec = cds.data["close"] < cds.data["open"]
    view_inc = CDSView(source=cds, filters=[BooleanFilter(inc)])
    view_dec = CDSView(source=cds, filters=[BooleanFilter(dec)])
    width = 12*60*60*1500
    fig.segment(x0="reg_day", x1="reg_day", y0="low", y1="high", color=RED[1], source=cds, view=view_inc)
    fig.segment(x0="reg_day", x1="reg_day", y0="low", y1="high", color=BLUE[1], source=cds, view=view_dec)
    fig.vbar(x='reg_day', width=width, top='open', bottom='close', fill_color=RED[1], line_color=RED[1], source=cds, view=view_inc)
    fig.vbar(x='reg_day', width=width, top='open', bottom='close', fill_color=BLUE[1], line_color=BLUE[1], source=cds, view=view_dec)
    
    band = Band(base='reg_day', lower='bbl', upper='bbu', source=cds, level='underlay', fill_alpha=0.3, line_width=1, line_color=BLUE[3], fill_color=BLUE[6])
    fig.add_layout(band)
    
    base_line = _figLine(fig, 'reg_day', 'ma5',  cds, 1, BLUE[0],   0.5, 'ma5')
    _figLine(fig, 'reg_day', 'ma20', cds, 1, BLUE[0],   0.8, 'ma20')
    _figLine(fig, 'reg_day', 'ma60', cds, 2, ORANGE[3], 0.8, 'ma60')
    fig.y_range = Range1d(min(cds.data["close"]) * 0.9, max(cds.data["close"])*1.1)

    if "mavolu" in cds.data:
        fig.extra_y_ranges = {'volume': Range1d(np.nanmin(cds.data["mavolu"])*0.9, np.nanmax(cds.data["mavolu"])*1.1)}
        fig.add_layout(LinearAxis(y_range_name='volume'), 'right')
        _ = _figLine(fig, 'reg_day', 'mavolu',  cds, 2, ORANGE[6], 0.7, "ma_volume", "volume")

    _setStyle(fig)
    fig.add_tools(HoverTool(
        tooltips=[
            ("date", "@reg_day{%F}"),
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


def showMovingAverage(width: int, height: int, df: pd.DataFrame, **options):
    if "mavolu" not in df:
        genBaseIndicator(df)
    cds = ColumnDataSource(df)
    show(plotMovingAverage(width, height, cds, **options))


def plotMovingAverage(width: int, height: int, cds: ColumnDataSource, **options):
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
    _figLine(fig, 'reg_day', 'ma240', cds, 2, COLOR[14], 1,   'ma240')
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


def showMacd(width: int, height: int, df: pd.DataFrame, **options):
    if "mavolu" not in df:
        genBaseIndicator(df)
    cds = ColumnDataSource(df)
    show(plotMacd(width, height, cds, **options))


def plotMacd(width: int, height: int, cds: ColumnDataSource, **options):
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


def showTimeseriesLines(width: int, height: int, df: pd.DataFrame, x: str = "reg_day", ylist: list = [], **options):
    cds = ColumnDataSource(df)
    show(plotTimeseriesLines(width, height, cds, x, ylist, **options))


def plotTimeseriesLines(width: int, height: int, cds: ColumnDataSource, x: str = "reg_day", ylist: list = [], **options):
    toolbar_location = options.get("toolbar_location", "above")
    local_tools = options.get("tools", tools)
    title = options.get("title", "Timeseries Lines")
    base_y = options.get("base_y", 0)
    area = options.get("area", [])
    
    COLOR = Category20[20]
    tooltips = []
    fig = figure(plot_width=width, plot_height=height, x_axis_type="datetime", title=title, tools=local_tools, toolbar_location=toolbar_location)
    
    for idx, y in enumerate(ylist):
        if idx == 0:
            base_line = _figLine(fig, x, y,  cds, 1, COLOR[idx], 0.8, y)
        else:
            _ = _figLine(fig, x, y,  cds, 1, COLOR[idx*2 if idx < 11 else idx*2-1], 0.6 if idx < 11 else 0.8, y)
        tooltips.append((y, f"@{y}" + "{,.03f}"))
    fig.renderers.extend([Span(location=base_y, dimension='width', line_color="forestgreen", line_width=0.5)])
    
    if len(area) == 2:
        fig.add_layout(BoxAnnotation(top=area[0], fill_alpha=0.05, fill_color=COLOR[6]))
        fig.add_layout(BoxAnnotation(bottom=area[1], fill_alpha=0.05, fill_color=COLOR[4]))

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
