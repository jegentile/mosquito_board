__author__ = 'jgentile'

import argparse
import csv
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-f','--mosquito-population-file')
parser.add_argument('-a','--board-a',required=False)
parser.add_argument('-b','--board-b',required=False)
parser.add_argument('-y','--year',type=int)
parser.add_argument('--prefix')
parser.add_argument('--all-boards',required=False,action='store_true')

class MosquitoBoard:
    def __init__(self,board_id,resolution):
        self._board_id = board_id
        self._resolution = resolution
        self._counts = []

    def add_record(self,time,count):
        self._counts.append((time,count))

    def resolution(self):
        return self._resolution

    def board_id(self):
        return self._board_id

    def report_number_of_records_by_year(self,year=None):
        counts_by_year = {}
        for c in self._counts:
            year = int(c[0])
            if not counts_by_year.has_key(year):
                counts_by_year[year] = 0
            counts_by_year[year]+= 1
        return counts_by_year

    def get_year(self,year,resolution='daily',start=0.4,end=0.75):
        data = []
        for c in self._counts:
            if int(c[0]) == year:
                data.append(c)
        return data

    def get_first_and_late_date(self,year):
        c = self.get_year(year)
        if len(c):
            return (c[0][0],c[-1][0])

    def get_count_on_date(self,date):
        try:
            for i,c in enumerate(self._counts):

                if c[0] == date:
                    return c[1]

                if c[0] < date and self._counts[i+1][0] > date:
                        (x1,y1) = (c[0],c[1])
                        p2 = self._counts[i+1]
                        (x2,y2) = (p2[0],p2[1])
                        m = (y1-y2)/(x1-x2)
                        b = y1-m*x1
                        return m*date+b

        except IndexError:
            return None



def correlate(board_a,board_b,year):
    first = 0.0
    last = 1.0

    for b in [board_a,board_b]:
        a = b.get_first_and_late_date(year)

        if a[0]-year > first:
            first = a[0]-year
        if a[1]-year < last:
            last = a[1]-year

    data_a = []
    data_b = []

    dates = []

    for a in board_a.get_year(year):
        if a[0] >= year+first and a[0] <= year+last:
            data_a.append(a)
            dates.append(a[0])

    for a in board_b.get_year(year):
        if a[0] >= year+first and a[0] <= year+last:
            data_b.append(a)
            dates.append(a[0])

    dates.sort()

    time_series_a,time_series_b = [],[]

    for d in dates:
        time_series_a.append(board_a.get_count_on_date(d))
        time_series_b.append(board_b.get_count_on_date(d))


    print len(time_series_a)
    print '--------------'
    print len(time_series_b)


    return np.corrcoef(time_series_a,time_series_b)

    """

    data_b = board_b.get_year(year)

    print len(data_a)
    print len(data_b)
    print dates

    print first,last
    """



def main():
    args = parser.parse_args()
    boards = {}

    try:
        with open(args.mosquito_population_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                #print row
                b_id =  row['BoardID']
                date =  float(row['Date.decimal'])
                count = float(row['Abundance'])

                if not boards.has_key(b_id):
                    boards[b_id] = MosquitoBoard(b_id,row['Resolution'])

                boards[b_id].add_record(date,count)

    except IOError as e:
        print 'Something opening {0}:{1}'.format(args.mosquito_population_file,e)

    for year in xrange(2009,2017):
        print year,'\t',
    print ''

    for b in boards:
        boards[b].resolution()
        a = boards[b].report_number_of_records_by_year()
        for year in xrange(2009,2017):
            if a.has_key(year):
                print a[year],'\t',
            else:
                print 'NaN','\t',
        print boards[b].resolution(),boards[b].board_id()




    if args.board_a and args.board_b:
        print correlate(boards[args.board_a],boards[args.board_b],args.year)[0][1]

    if args.all_boards:
        generate_all_correlations(boards,xrange(2009,2017),args.prefix)

def generate_all_correlations(boards,years,prefix):

    keys = boards.keys()

    print keys

    for y in years:

        file = open('{0}/{1}.csv'.format(prefix,y),'w')

        line = ','
        for b1 in boards:
            line = line+b1+','

        line = line[:-1] + '\n'

        file.write(line)


        for i,b1 in enumerate(boards):
            line = b1+','
            for j,b2 in enumerate(boards):
                try:
                    value = correlate(boards[b1],boards[b2],y)[0][1]
                except TypeError as e:
                    value = 'Nan'
                line = line+'{},'.format(value)

            line = line[:-1]+'\n'

            file.write(line)

        file.close()





if __name__ == '__main__':
    main()
