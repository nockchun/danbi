import numpy as np
from matplotlib import pyplot, ticker, get_backend, rc, font_manager
from functools import wraps
import re

class EduPlotConf(object):
    def __init__(
        self, dpi=100, figSize=2, figScale=1, lineWidth=1, axisWidth=0.7, markerSize=4,
        font="serif", fontSize=10, textFontSize=11, tickFontSize=9,
        gridParams   = {"linewidth": 0.6, "alpha": 0.3},
        quiverParams = {"angles": "xy", "scale_units": "xy", "scale": 1, "width": 0.007, "headwidth":5, "headaxislength":3},
        axisParam    = {"titlesize":12, "titleweight":"bold", "unicode_minus":False}
    ):
        self.font = font
        self.fontSize = fontSize
        self.textFontSize = textFontSize
        self.dpi = dpi
        self.figSize = np.array([figSize, figSize]) * figScale * 2
        self.lineWidth = lineWidth
        self.axisWidth = axisWidth
        self.markerSize = markerSize
        self.gridParams = gridParams
        self.quiverParams = quiverParams
        self.axisParam = axisParam
        self.tickFontSize = tickFontSize
        
    def set(self):
        rc("font", family=self.font, size=self.fontSize)
        rc("figure", dpi=self.dpi)
        rc("lines", linewidth=self.lineWidth, markersize=self.markerSize)
        rc("axes", titlesize=self.axisParam["titlesize"], titleweight=self.axisParam["titleweight"], unicode_minus=self.axisParam["unicode_minus"])
        rc('xtick', labelsize=self.tickFontSize)
        rc('ytick', labelsize=self.tickFontSize)

    def getFontsList(self, hintRegex=""):
        regex = re.compile(hintRegex, re.IGNORECASE)
        return [{f.name: f.fname} for f in font_manager.fontManager.ttflist if regex.search(f.fname)]


class EduPlot2D(object):
    def __init__(self, conf=EduPlotConf()):
        self._conf = conf
        conf.set()
        self._items = {}
        self.clear()
    
    def _baseSpace(self):
        xticks = self._axis.get_xticks()
        yticks = self._axis.get_yticks()
        dx = xticks[1] - xticks[0]
        dy = yticks[1] - yticks[0]
        base = max(int(min(dx, dy)), 1)   # grid interval is always an integer
        loc = ticker.MultipleLocator(base=base)
        self._axis.xaxis.set_major_locator(loc)
        self._axis.yaxis.set_major_locator(loc)
        self._axis.grid(True, **self._conf.gridParams)
        self._axis.spines["left"].set_linewidth(self._conf.axisWidth)
        self._axis.spines["bottom"].set_linewidth(self._conf.axisWidth)
    
    def _transSpace(self, transMatrix):
        grid_range = 20
        x = np.arange(-grid_range, grid_range+1)
        X_, Y_ = np.meshgrid(x,x)
        I = transMatrix[:,0]
        J = transMatrix[:,1]
        X = I[0]*X_ + J[0]*Y_
        Y = I[1]*X_ + J[1]*Y_
        origin = np.zeros(1)

        # draw grid lines
        for i in range(x.size):
            self._axis.plot(X[:,i], Y[:,i], c="#3D076A", **self._conf.gridParams)
            self._axis.plot(X[i,:], Y[i,:], c="#EAB529", **self._conf.gridParams)
            
        self._axis.spines["left"].set_color("#3D076A")
        self._axis.spines["bottom"].set_color("#EAB529")
        self._axis.spines["left"].set_linewidth(0.3)
        self._axis.spines["bottom"].set_linewidth(0.3)
    
    def _transVector(self, transMatrix, arrays):
        if transMatrix is None:
            return arrays
        result = []
        for item in arrays:
            result.append(transMatrix.dot(item))
        return np.array(result)

    def genSpaceFigure(self, xLim, yLim=None, title=None, transMatrix=None):
        self.genSpace(xLim, yLim, title, transMatrix, False)
        return self._figure

    def genSpace(self, xLim, yLim=None, title=None, transMatrix=None, show=True):
        # input check
        if isinstance(xLim, int): xLim = [-xLim, xLim]
        else: assert len(xLim) == 2, "xLim should have 2 elements list. [-2, 4]"
        if yLim is None: yLim = xLim
        else:
            if isinstance(yLim, int): yLim = [-yLim, yLim]
            else: assert len(yLim) == 2, "xLim should have 2 elements list. [-2, 4]"
        assert xLim[0] <= 0 <= xLim[1], "xLim range should contain 0 elements"
        assert yLim[0] <= 0 <= yLim[1], "yLim range should contain 0 elements"
            
        # create panal with limit
        self._figure, self._axis = pyplot.subplots(figsize=self._conf.figSize)
        if title is not None: self._axis.set_title(title)
        self._axis.set_xlim(xLim)
        self._axis.set_ylim(yLim)
        self._axis.set_aspect("equal")
        
        # generate grid
        if transMatrix is None: self._baseSpace()
        else:
            transMatrix = np.array(transMatrix)
            assert transMatrix.shape == (2,2), "the input matrix must have a shape of (2,2)"
            self._transSpace(transMatrix)
        
        # show x-y axis in the center, hide frames
        self._axis.spines["left"].set_position(("data", 0))
        self._axis.spines["bottom"].set_position(("data", 0))
        self._axis.spines["right"].set_color("none")
        self._axis.spines["top"].set_color("none")
        
        # draw plot
        item = self._items["vectors"]
        for name in item:
            vectors = self._transVector(transMatrix, item[name]["vectors"])
            origins = self._transVector(transMatrix, item[name]["origins"])
            self._axis.quiver(origins[:,0], origins[:,1], vectors[:,0], vectors[:,1],
                              color=item[name]["color"], **self._conf.quiverParams)
            
        item = self._items["functions"]
        for name in item:
            x = np.linspace(xLim[0], xLim[1], item[name]["linespace"])
            y = eval(item[name]["expression"])
            array = self._transVector(transMatrix, [ (i, j) for i, j in zip(x, y)])
            array = np.array(array)
            pyplot.plot(array[:,0], array[:,1], item[name]["color"])
        
        item = self._items["xydata"]
        for name in item:
            pyplot.plot(item[name]["x"], item[name]["y"], item[name]["color"])
        
        item = self._items["markers"]
        for name in item:
            positions = self._transVector(transMatrix, item[name]["positions"])
            pyplot.plot(positions[:,0], positions[:,1], marker=item[name]["marker"], linewidth=0, color=item[name]["color"])
        
        item = self._items["texts"]
        for name in item:
            positions = self._transVector(transMatrix, item[name]["positions"])
            for idx, position in enumerate(positions):
                pyplot.text(position[0], position[1], item[name]["texts"][idx], color=item[name]["color"],
                            horizontalalignment=item[name]["hAlign"], verticalalignment=item[name]["vAlign"], wrap=True, fontsize=self._conf.textFontSize)
        if show: pyplot.show()
        pyplot.close()
    
    def addVector(self, vectors, origins=None, name="vector", color="#0000FF"):
        vectors = np.array(vectors)
        assert vectors.shape[1] == 2, "Each vector should have 2 elements."  
        if origins is not None:
            origins = np.array(origins)
            assert origins.shape[1] == 2, "Each tail should have 2 elements."
        else:
            origins = np.zeros_like(vectors)
        
        nvectors = vectors.shape[0]
        norigins = origins.shape[0]
        if nvectors == 1 and norigins > 1:
            vectors = np.tile(vectors, (norigins, 1))
        elif norigins == 1 and nvectors > 1:
            origins = np.tile(origins, (nvectors, 1))
        else:
            assert origins.shape == vectors.shape, "vectors and tail must have a same shape"
            
        self._items["vectors"][name] = {"vectors":vectors, "origins":origins, "color":color}
    
    def addFunction(self, expX_ForY="x**2", linespace=100, name="function", color="#FF0000"):
        self._items["functions"][name] = {"expression":expX_ForY, "linespace":linespace, "color":color}
        
    def addXYData(self, x, y, name="xydata", color="#0000FF"):
        self._items["xydata"][name] = {"x":x, "y":y, "color":color}
        
    def addMarker(self, positions, marker=".", name="marker", color="#00FF00"):
        positions = np.array(positions)
        self._items["markers"][name] = {"positions":positions, "marker":marker, "color":color}
        
    def addText(self, positions, texts, name="text", color="#000000", hAlign="center", vAlign="bottom"):
        assert len(positions) == len(texts), "positions and texts must have a same size."
        self._items["texts"][name] = {"positions":positions, "texts":texts, "color":color, "hAlign":hAlign, "vAlign":vAlign}
        
    def setConf(self, conf):
        self._conf = conf
        conf.set()
    
    def getConf(self):
        return self._conf
    
    def getFigure(self):
        return self._figure
    
    def clear(self):
        self._items["vectors"] = {}
        self._items["functions"] = {}
        self._items["xydata"] = {}
        self._items["markers"] = {}
        self._items["texts"] = {}