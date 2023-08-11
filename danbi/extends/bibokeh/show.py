import pandas as pd
import numpy as np
import datetime
from typing import List, Tuple, Any, Union

from bokeh.io import curdoc, show
from bokeh.plotting import figure, show, curdoc
from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource, HoverTool, CrosshairTool, Span
from bokeh.models.formatters import DatetimeTickFormatter

from .plot_chart import tools, COLORSET


def showBokeh(fig: figure):
    show(fig)


def showPandas(df: pd.DataFrame, xlist: Union[str, List[str]], ylist: Union[str, List[Union[str, List[str]]]], typeList: Union[str, List[List[str]]] = "line", width: int = 1500, height: int = 400, col_dir: bool = True, sync_axis: str = "xy",
               graph_widths: Union[int, List[int]] = 1, line_colors: List[str] = None, hover=True, **options):
    cds = ColumnDataSource(df)
    """
    example: showPandas(df, "a", ["b", ["c", "d", "e"]], col_dir=False)
    """
    toolbar_location = options.get("toolbar_location", "above")
    legend_location = options.get("legend_location", "top_right")
    local_tools = options.get("tools", tools)
    title = options.get("title", "Learning History")
    title_size = options.get("title_size", "11pt")
    format_datetime = options.get("format_datetime", "%Y-%m-%d")
    
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
        fig = figure(width=width, height=height, title=" & ".join(ynames), tools=local_tools, toolbar_location=toolbar_location)

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
                fig_each = fig.line(x=xname, y=name, source=cds, line_width=graph_widths[idx], color=COLORSET[idx % 53], legend_label=name, alpha=0.8, muted_alpha=0.02)
            elif types[idx] == "scatter":
                fig_each = fig.scatter(x=xname, y=name, source=cds, size=graph_widths[idx], color=COLORSET[idx % 53], legend_label=name, alpha=0.8, muted_alpha=0.02)
            
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


def showAsRows(plots: List[figure], sync_axis: str = None, width: int = None):
    wHair = Span(dimension="width", line_dash="dotted", line_width=0.8)
    hHair = Span(dimension="height", line_dash="dotted", line_width=0.8)
    
    if sync_axis is not None:
        for plot1 in plots:
            plot1.add_tools(CrosshairTool(overlay=[wHair, hHair], line_alpha=0.5))
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


def showAsGrid(plots: List[List[Union[figure, List[figure]]]], sync_axis: str = None, width: int = None):
    wHair = Span(dimension="width", line_dash="dotted", line_width=0.8)
    hHair = Span(dimension="height", line_dash="dotted", line_width=0.8)
    
    if sync_axis is not None:
        plots_flat = []
        for items in sum(plots, []):
            if isinstance(items, list):
                for item in items:
                    plots_flat.append(item)
            else:
                plots_flat.append(items)
        for plot1 in plots_flat:
            plot1.add_tools(CrosshairTool(overlay=[wHair, hHair], line_alpha=0.3))
            if width is not None:
                plot1.width = width
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



