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

# plt.plot(dates, PM_25)
# plt.show()


fig = Figure()
# axis = fig.add_subplot(1, 1, 1)
dates = [pd.to_datetime(d) for d in ["2019-01-01","2019-02-01","2019-03-01","2019-04-01","2019-10-01"]]
plt.plot(dates, [67,68,69,70,79])
# plt.savefig(fig, format='png')
plt.xlabel("xaxis")
plt.ylabel("yaxis")
plt.xticks(rotation=15)

plt.show()


def drawlinegraph(dates,value,xaxis,yaxis):
    # try:
    dates = [pd.to_datetime(d) for d in ["2019-01-01", "2019-02-01", "2019-03-01", "2019-04-01", "2019-10-01"]]
    plt.plot(dates, [67, 68, 69, 70, 79])
    # plt.savefig(fig, format='png')
    plt.xlabel("xaxis")
    plt.ylabel("yaxis")
    plt.xticks(rotation=15)
    output = io.BytesIO()

    plt.savefig(output, format='png')


    return output
    # except Exception as ex:
    #     logging.info(" failed "+str(ex))


def drawlinegraph2(dates,value,xaxis,yaxis):
    # try:
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    dates = [pd.to_datetime(d) for d in dates]
    axis.plot(dates, value)

    # axis.xlabel(xaxis)
    # axis.ylabel(yaxis)
    # axis.xticks(rotation=15)
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)


    return output
    # except Exception as ex:
    #     logging.info(" failed "+str(ex))

def drawlinegraph2(dates,value,xaxis,yaxis):
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
