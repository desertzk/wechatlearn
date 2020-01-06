import matplotlib.pyplot as plt

import pandas as pd
# dates = ['2015-09-12','2015-09-22','2015-12-10','2015-12-20','2015-12-22']
# PM_25 = [80, 55,100,45,56]
# dates = [pd.to_datetime(d) for d in dates]
#
# plt.plot(dates, PM_25)
# plt.show()

def drawlinegraph(dates,value,xaxis,yaxis,imgname):
    fig = plt.figure()
    dates = [pd.to_datetime(d) for d in dates]
    # Plot a line graph
    plt.plot(dates,value)

    # Add labels and title
    # plt.title("Interactive Plot")
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)

    fig.savefig('../resources/'+imgname)


