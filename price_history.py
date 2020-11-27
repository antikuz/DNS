from DNSsql import SQLdb
# import matplotlib.pyplot as plt

with SQLdb() as db:
    print('обращение к базе')
    name, price_history = db.price_history('1296799')
    print(name, price_history)

def reverse_date(date):
    '''
    reverse date 20.02.14 to 14.02.20
    '''
    new_date = date.split('.')
    new_date = f'{new_date[2]}.{new_date[1]}.{new_date[0]}'
    return new_date

# price_hist = [(17999, '20.02.14'), (15999, '20.03.03'), (16199, '20.03.10'), (20199, '20.03.11'), (15999, '20.03.12')]
price_history_new = [(x[0], reverse_date(x[1])) for x in price_history]
print(price_history)
# plt.plot([x[1] for x in price_history_new], [x[0] for x in price_history_new])

# N = len(price_history_new)*1.3
# plt.gca().margins(x=0.05)
# plt.gcf().canvas.draw()
# tl = plt.gca().get_xticklabels()
# maxsize = max([t.get_window_extent().width for t in tl])
# m = 0.5 # inch margin
# s = maxsize/plt.gcf().dpi*N+2*m
# margin = m/plt.gcf().get_size_inches()[0]
# plt.gcf().subplots_adjust(left=margin, right=1.-margin)
# plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

# plt.suptitle(name)
# for count, point in enumerate(price_history_new):
#     if count == 0:
#         plt.annotate(
#         point[0], 
#         (point[1], point[0]),
#         ha='center',
#         xytext = (0, 15), 
#         textcoords='offset points'
#     )
#     else:
#         plt.annotate(
#             point[0], 
#             (point[1], point[0]),
#             ha='right',
#             xytext = (-10, -10), 
#             textcoords='offset points'
#         )
# plt.show()