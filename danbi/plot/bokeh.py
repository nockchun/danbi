from typing import Union, List, Any, Tuple
import pandas as pd
import numpy as np
import datetime

from bokeh.models import ColumnDataSource, BooleanFilter, CDSView, Band, Range1d, LinearAxis, BoxAnnotation, Span
from bokeh.models import HoverTool,WheelZoomTool, PanTool, ResetTool, CrosshairTool, BoxSelectTool, BoxZoomTool, SaveTool
from bokeh.io import show, output_notebook, curdoc, export_png
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row, column, layout
from bokeh.models.formatters import PrintfTickFormatter, NumeralTickFormatter, DatetimeTickFormatter
from bokeh.palettes import Blues, Reds, Purples, Oranges, Greens, Greys, YlGn, RdPu, Category10, Category20, Category20b, Set1, Set2, Set3

def setJupyterBokehEnable():
    from bokeh.resources import INLINE
    output_notebook(resources=INLINE)

tools = [PanTool(), WheelZoomTool(), ResetTool(), CrosshairTool(), BoxSelectTool(), BoxZoomTool(), SaveTool()]

def showBokeh(fig: figure):
    show(fig)

def showAsRows(plots: List[figure], sync_axis: str = "xy", width: int = None):
    for plot1 in plots:
        if width is not None:
            plot1.width = width
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

def getBokehDataSource(df: pd.DataFrame) -> ColumnDataSource:
    return ColumnDataSource(df)

def getBokehFigure(width: int, height: int, title: str):
    fig = figure(plot_width=width, plot_height=height, title=title, tools=tools, toolbar_location="above")
    
    return fig

def setBokehFigureStyle(fig: figure, tooltips: List = None, formatters: tuple = None, base_plot: Any = None, mode: str = "vline", **options):
    fig.title.text_font_size = options.get("title_font_size", "12pt")
    fig.grid.grid_line_alpha = options.get("grid_line_alpha", 0.5)
    fig.yaxis.formatter = NumeralTickFormatter(format="0,0[.]00")
    fig.xaxis.formatter = DatetimeTickFormatter(years=["%Y-%m-%d"], months=["%Y-%m-%d"], days=["%Y-%m-%d"])

    fig.legend.border_line_alpha = 0
    fig.legend.background_fill_alpha = 0
    fig.legend.padding = options.get("legend_padding", -5)
    fig.legend.spacing = options.get("legend_spacing", -4)
    fig.legend.click_policy = "mute"
    fig.legend.location = options.get("legend_location", "top_left")
    fig.legend.label_text_font_size = options.get("legend_font_size", "9pt")
    
    if tooltips and formatters and base_plot:
        fig.add_tools(HoverTool(
            tooltips=tooltips,
            formatters=formatters,
            mode="vline",
            renderers=[base_plot]
        ))

def setBokehLine(fig: figure, src: Union[ColumnDataSource, pd.DataFrame], x: str, y: str, color: str, width: int = 1.2, legend_label: str = None, alpha: int = 0.7, muted_alpha: int = 0.05, y_ref: int = None, y_range: tuple = None, extra_y_name: str = None, extra_y_range: tuple = None):
    if isinstance(src, pd.DataFrame):
        src = ColumnDataSource(df)
    
    if legend_label is None:
        legend_label = y
    
    if extra_y_name is not None:
        line = fig.line(source=src, x=x, y=y, color=color, line_width=width, legend_label=legend_label, alpha=alpha, muted_alpha=muted_alpha, y_range_name=extra_y_name)
        fig.circle(x=x, y=y, source=src, radius=0, y_range_name=extra_y_name)
        if extra_y_range is not None:
            fig.extra_y_ranges.update({extra_y_name: Range1d(*extra_y_range)})
            fig.add_layout(LinearAxis(y_range_name=extra_y_name), "right")
        if y_ref is not None:
            fig.renderers.extend([Span(location=y_ref, dimension='width', line_color="slategray", line_width=1, y_range_name=extra_y_name)])
    else:
        line = fig.line(source=src, x=x, y=y, color=color, line_width=width, legend_label=legend_label, alpha=alpha, muted_alpha=muted_alpha)
        fig.circle(x=x, y=y, source=src, radius=0)
        if y_ref is not None:
            fig.renderers.extend([Span(location=y_ref, dimension='width', line_color="slategray", line_width=1)])
    if y_range:
        fig.y_range = Range1d(*y_range)
    
    return line

def setBokehMarke(fig: figure, src: Union[ColumnDataSource, pd.DataFrame], x: str, y: str, color: str, size: int = 10, marker: str = "triangle", legend_label: str = None, alpha: int = 0.5, muted_alpha: int = 0.05):
    if isinstance(src, pd.DataFrame):
        src = ColumnDataSource(df)
    
    if legend_label is None:
        legend_label = y
    
    fig.scatter(x=x, y=y, source=src, size=size, color=color, marker=marker, legend_label=legend_label, alpha=alpha, muted_alpha=muted_alpha)
    
    return fig

def showPandas(df: pd.DataFrame, xlist: Union[str, List[str]], ylist: List[Tuple[str, str]], typeList: Union[str, List[List[str]]] = "line", width: int = 1500, height: int = 400, col_dir: bool = True, sync_axis: str = "xy",
               graph_widths: Union[int, List[int]] = 1, line_colors: List[str] = None, hover=True, **options):
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
        fig.title.text_font_size = title_size
        fig.grid.grid_line_alpha = 0.3
        fig.legend.border_line_alpha = 0
        fig.legend.background_fill_alpha = 0
        fig.legend.click_policy = "mute"
        fig.legend.location = legend_location
        if isinstance(cds.data[xname][0], datetime.date) or isinstance(cds.data[xname][0], np.datetime64):
            fig.xaxis.formatter = DatetimeTickFormatter(years=[format_datetime], months=[format_datetime], days=[format_datetime])

        plot_figures.append(fig)
        
        if hover:
            fig.add_tools(HoverTool(
                tooltips=tooltips,
                mode="vline",
                renderers=[fig_base]
            ))
    
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