import datetime as dt
import pandas as pd
import calendar


class IndexModel:
    def __init__(self) -> None:
        self.source_location = 'data_sources/stock_prices.csv'
        self.df = pd.read_csv(self.source_location)

# IndexModel class methods

    def top_n(self, values: list, n: int) -> list:

        '''
        Lists the top 'n' values from a given list
        :param values: values given as a list
        :param n: the top number it must be an integer
        :return: returns the top values in a list
        '''

        vals = values.copy()        # a copy is needed in order to not to modify the given list
        vals.sort(reverse=True)     # sorts the list values in descending order
        x = vals[:n]                # selects the first n values
        del vals                    # deletes the the copied list to free the memory

        return x

    def top3_list_index(self, vals: list) -> tuple:

        '''
        Calculates the top 3 values of the given list, and returns their position (index) in the list
        :param vals: values given as a list
        :return: returns a tuple with three integers
        '''

        tops = self.top_n(vals, 3)
        x, y, z = vals.index(tops[0]), vals.index(tops[1]), vals.index(tops[2])

        return x, y, z

    def calc_portfolio_value(self, prices: tuple) -> float:

        '''
        Calculates the Value of the Index Portfolio, based on the pre-defined rules and weights
        :param prices: prices given as a tuple
        :return: returns a float with the value
        '''

        x, y, z = prices

        return 0.5 * float(x) + 0.25 * float(y) + 0.25 * float(z)

    def split_date(self, date: str) -> tuple:

        '''
        splits the date into three variables: year, month and day
        :param date: accepts date in DD/MM/YYYY format
        :return: a tuple with (year, month, day)
        '''

        year, month, day = int(date[6:]), int(date[3:5]), int(date[:2])

        return year, month, day

    def month_last_day(self, dates: str) -> dt.date:

        '''
        Calculates the last day of the current month of a given date
        :param dates: accepts date in DD/MM/YYYY format string
        :return: last day of the month as datetime object
        '''

        year, month, day = self.split_date(dates)
        last_day = calendar.monthrange(year, month)[1]

        return dt.date(year, month, last_day)

    def last_working_day(self, dates: str) -> dt.date:

        '''
        Calculates the last working day of the current month of a given date
        by checking if the day value is not Sunday or Saturday (Monday = 0, Sunday = 6)
        ATTENTION! This function omits other Holydays.
        :param dates: accepts date in DD/MM/YYYY format string
        :return: the last working day of the given month as datetime object
        '''

        last_day = self.month_last_day(dates)
        day = calendar.weekday(last_day.year, last_day.month, last_day.day)

        if day == 5:                        # day is Saturday
            l_day = last_day.day - 1        # last working day must be the previous day: Friday
        elif day == 6:                      # day is Sunday
            l_day = last_day.day - 2        # last working day must be the day 2 days before: Friday
        else:
            l_day = last_day.day            # the month's last day is a working day

        return dt.date(last_day.year, last_day.month, l_day)

    def first_working_day(self, dates: str) -> dt.date:

        '''
        Calculates the first working day of the month
        :param dates: accepts date in DD/MM/YYYY format
        :return: returns a datatime.date object with the first working day of the month
        '''

        year, month, day = self.split_date(dates)
        f_day = calendar.weekday(year, month, 1)    # sets the first day of the month

        if f_day == 5:                              # it is Saturday
            day = 3                                 # then fist working day is two day later Monday, 3rd
        elif f_day == 6:                            # it is Sunday
            day = 2                                 # then fist working day is two day later Monday, 2nd
        else:
            day = 1

        return dt.date(year, month, day)

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:

        top_1, top_2, top_3 = 1, 1, 1
        old_tops = [top_1, top_2, top_3]
        portfolio_value = []
        index_level = []
        divisor = 1
        old_portfolio_value = 100

        for index, row in self.df.iterrows():
            year, month, day = self.split_date(row['Date'])  # gets values of the 'Date' column splited
            prices = (row[top_1], row[top_2], row[top_3])
            portfolio_value.append(self.calc_portfolio_value(prices))

            if dt.date(year, month, day) == self.last_working_day(row['Date']):
                price_list = list(row[1:12])
                old_tops = [top_1, top_2, top_3]
                top_1, top_2, top_3 = self.top3_list_index(price_list)
                top_1 += 1
                top_2 += 1
                top_3 += 1
            elif dt.date(year, month, day) == self.first_working_day(row['Date']):
                if index > 3:  # ensures that the initial index value is 100 as defined above
                    old_prices = (row[old_tops[0]], row[old_tops[1]], row[old_tops[2]])
                    old_portfolio_value = self.calc_portfolio_value(old_prices)
                new_portfolio_value = self.calc_portfolio_value(prices)
                divisor = new_portfolio_value / old_portfolio_value * divisor
            else:
                pass

            index_level.append(self.calc_portfolio_value(prices) / divisor)

        self.df['Index_Portfolio_Value'] = portfolio_value
        self.df['Index_Level'] = index_level

    def export_values(self, file_name: str) -> None:
        exp_df = self.df.iloc[2:, [0, 12]]
        exp_df.to_csv(file_name, index=False)


