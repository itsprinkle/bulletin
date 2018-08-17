import datetime

def datechange():
    start = '20170101'
    end = '20170201'

    datestart = datetime.datetime.strptime(start, '%Y%m%d')
    dateend = datetime.datetime.strptime(end, '%Y%m%d')
    #时间加一天
    datestart += datetime.timedelta(days=1)
    return datestart.strftime('%Y%m%d')