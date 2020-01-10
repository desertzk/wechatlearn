# coding:utf-8
import random
from io import BytesIO
import io
import matplotlib.pyplot as plt
import logging
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG

from matplotlib.figure import Figure

# dates = ['2015-09-12','2015-09-22','2015-12-10','2015-12-20','2015-12-22']
# PM_25 = [80, 55,100,45,56]
# dates = [pd.to_datetime(d) for d in dates]
#
# plt.plot(dates, PM_25)
# plt.show()

def drawlinegraph1(dates,value,xaxis,yaxis):
    try:
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        dates = [pd.to_datetime(d) for d in dates]
        axis.plot(dates, value)
        # axis.xlabel(xaxis)
        # axis.ylabel(yaxis)
        output = io.BytesIO()
        FigureCanvasAgg(fig).print_png(output)


        return output
    except Exception as ex:
        logging.info(" failed "+ex)

def drawlinegraph(dates,value,xaxis,yaxis):
    try:
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        x_points = range(80)
        axis.plot(x_points, [random.randint(1, 30) for x in x_points])

        output = io.BytesIO()
        FigureCanvasAgg(fig).print_png(output)


        return output
    except Exception as ex:
        logging.info(" failed "+ex)
