def read_data(data):
    # Reading in links
    input_data_file = "20170901.as-rel2.txt"
    with open(input_data_file) as f:
        for line in f:
            partitions = line.split('|')  # Format: as | as_link | link_type
            if partitions[0] not in data:
                data[partitions[0]] = {'as_links': {'p2c': [],
                                                    'p2p': []},
                                       'prefix': 'None',
                                       'prefix_length': 'None'}
            if partitions[2] == '-1':
                data[partitions[0]]['as_links']['p2c'].append(partitions[1])
            elif partitions[2] == '0':
                data[partitions[0]]['as_links']['p2p'].append(partitions[1])
    f.close()
    input_data_file = "routeviews-rv2-20171105-1200.txt"
    with open(input_data_file) as f:
        for line in f:
            partitions = line.split()  # Format: IP_prefix  prefix_length  as
            prefix_as = partitions[2].split('_')
            for a_s in prefix_as:
                if ',' in a_s:
                    set_as = a_s.split(',')
                    for sub_as in set_as:
                        if sub_as in data:
                            data[sub_as]['prefix'] = partitions[0]
                            data[sub_as]['prefix_length'] = partitions[1]
                elif a_s in data:
                    data[a_s]['prefix'] = partitions[0]
                    data[a_s]['prefix_length'] = partitions[1]
    f.close()


def print_data(data, t1):
    output_data_file = "as_statistics.txt"
    with open(output_data_file, "w+") as w:
        for a_s in data:
            print('AS: {}, node_degree: {}, IP_prefix: {}'.format(a_s, data[a_s]['degree'], data[a_s]['prefix'] + '/' + data[a_s]['prefix_length']), file=w)
    w.close()
    output_data_file = "as_t1.txt"
    with open(output_data_file, "w+") as w:
        for a_s in range(10):
            if t1[a_s]:
                print('{},{}'.format(a_s + 1, t1[a_s]), file=w)
        print('{}'.format(len(t1)), file=w)
    w.close()


def calc_degree(data):
    for a_s in data:
        data[a_s]['degree'] = len(data[a_s]['as_links']['p2c']) + len(data[a_s]['as_links']['p2p'])


def degree_sort(data):
    as_list = list(data.keys())
    sorted_as = []
    while as_list:
        maximum = as_list[0]  # arbitrary number in list
        for a_s in as_list:
            if data[a_s]['degree'] > data[maximum]['degree']:
                maximum = a_s
        sorted_as.append(maximum)
        as_list.remove(maximum)
    return sorted_as


def infer_t1(data):
    R = degree_sort(data)
    S = [R[0]]
    next_as = 1
    connected = True
    while connected:
        for a_s in S:
            if (R[next_as] not in data[a_s]['as_links']['p2p']) and (R[next_as] not in data[a_s]['as_links']['p2c'] and (a_s not in data[R[next_as]]['as_links']['p2p']) and (a_s not in data[R[next_as]]['as_links']['p2c'])):
                connected = False
                break
        if connected:
            S.append(R[next_as])
            next_as += 1
    return S


def calc_cone(all_data):
    def dfs(data, cur_node, cone_size):
        if cur_node in data:
            for child in data[cur_node]['as_links']['p2c']:
                dfs(data, child, cone_size)
        return cone_size + 1
    for a_s in all_data:
        total_cone = 0
        total_cone = dfs(all_data, a_s, total_cone)
        all_data[a_s]['cone_size'] = total_cone

print("hello")
all_data = {}
read_data(all_data)
calc_degree(all_data)
t1_as = infer_t1(all_data)
calc_cone(all_data)
print_data(all_data, t1_as)
