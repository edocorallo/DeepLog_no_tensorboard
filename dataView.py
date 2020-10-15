import argparse
parser=argparse.ArgumentParser(prog='dataView')
parser.add_argument("log_file",type=str,help="Name of the file you want to view.")
args=parser.parse_args()
# This is just a data viewing to see there are how many templates, training data and so on.
if __name__ == '__main__':
    hdfs_train = []
    hdfs_test_normal = []
    hdfs_test_abnormal = []
    h1 = set()
    h2 = set()
    h3 = set()
    with open('data/{}_train'.format(args.log_file), 'r') as f:
        for line in f.readlines():
            line = tuple(map(lambda n: n - 1, map(int, line.strip().split())))
            hdfs_train.append(line)
    for line in hdfs_train:
        for c in line:
            h1.add(c)

    with open('data/{}_test_normal'.format(args.log_file), 'r') as f:
        for line in f.readlines():
            line = tuple(map(lambda n: n - 1, map(int, line.strip().split())))
            hdfs_test_normal.append(line)
    for line in hdfs_test_normal:
        for c in line:
            h2.add(c)

    with open('data/{}_test_abnormal'.format(args.log_file), 'r') as f:
        for line in f.readlines():
            line = tuple(map(lambda n: n - 1, map(int, line.strip().split())))
            hdfs_test_abnormal.append(line)
    for line in hdfs_test_abnormal:
        for c in line:
            h3.add(c)
    print('train length: %d, template length: %d, template: %s' % (len(hdfs_train), len(h1), h1))
    print('test_normal length: %d, template length: %d, template: %s' % (len(hdfs_test_normal), len(h2), h2))
    print('test_abnormal length: %d, template length: %d, template: %s' % (len(hdfs_test_abnormal), len(h3), h3))
