from math import pow


def read_data(data, prefixes):
    # Reading in links
    input_data_file = "20170901.as-rel2.txt"
    with open(input_data_file) as f:
        for line in f:
            partitions = line.split('|')  # Format: as | as_link | link_type
            if partitions[0] not in data:
                data[partitions[0]] = {'as_links': {'p2c': [],
                                                    'p2p': []},
                                       'degree': 0,
                                       'class': 'unclassified',
                                       'prefixes': []}
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
                set_as = a_s.split(',')
                for sub_as in set_as:
                    if sub_as not in data:
                        data[sub_as] = {'as_links': {'p2c': [],
                                                     'p2p': []},
                                        'degree': 0,
                                        'class': 'unclassified',
                                        'prefixes': []}
                    if not data[sub_as]['prefixes'].count(partitions[0] + '/' + partitions[1]):
                        data[sub_as]['prefixes'].append(partitions[0] + '/' + partitions[1])
                        prefixes.add(partitions[0] + '/' + partitions[1])
    f.close()


def print_data(data, t1, all_pref):
    output_data_file = "as_statistics.txt"
    with open(output_data_file, "w+") as w:
        print('AS, node_degree, IP_prefix_count, class', file=w)
        for a_s in data:
            print('{}, {}, {}, {}'.format(a_s, data[a_s]['degree'], len(data[a_s]['prefixes']), data[a_s]['class']), file=w)
    w.close()
    output_data_file = "as_t1.txt"
    with open(output_data_file, "w+") as w:
        for a_s in t1:
            if t1.index(a_s) == 10:
                break
            print('{},{}'.format(t1.index(a_s) + 1, a_s), file=w)
        print('{}'.format(len(t1)), file=w)
    w.close()
    output_data_file = "as_cone.txt"
    with open(output_data_file, "w+") as w:
        print('size rank table', file=w)
        # Table 1 Sort by cone size in number of ases
        size_rank = sorted(data, key=lambda k: data[k]['customer_cone']['cone_size'], reverse=True)
        ip_rank = sorted(data, key=lambda k: data[k]['customer_cone']['ip_percentage'], reverse=True)
        for a_s in size_rank[:15]:
            print('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(size_rank.index(a_s) + 1, a_s, 'name', data[a_s]['degree'],
                                                                  data[a_s]['customer_cone']['cone_size'],
                                                                  len(data[a_s]['customer_cone']['prefixes']),
                                                                  data[a_s]['customer_cone']['ips'],
                                                                  data[a_s]['customer_cone']['as_percentage'],
                                                                  data[a_s]['customer_cone']['prefix_percentage'],
                                                                  data[a_s]['customer_cone']['ip_percentage']), file=w)
        print('\nip_percent rank table', file=w)
        for a_s in ip_rank[:15]:
            print('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(ip_rank.index(a_s) + 1, a_s, 'name', data[a_s]['degree'],
                                                                  data[a_s]['customer_cone']['cone_size'],
                                                                  len(data[a_s]['customer_cone']['prefixes']),
                                                                  data[a_s]['customer_cone']['ips'],
                                                                  data[a_s]['customer_cone']['as_percentage'],
                                                                  data[a_s]['customer_cone']['prefix_percentage'],
                                                                  data[a_s]['customer_cone']['ip_percentage']), file=w)
        w.close()


def calc_degree(data):
    for a_s in data:
        data[a_s]['degree'] = len(data[a_s]['as_links']['p2c']) + len(data[a_s]['as_links']['p2p'])
        if data[a_s]['degree'] < 2 and len(data[a_s]['as_links']['p2c']) == 0 and len(data[a_s]['as_links']['p2p']) == 0:
            data[a_s]['class'] = 'Enterprise'
        elif len(data[a_s]['as_links']['p2c']) == 0 and len(data[a_s]['as_links']['p2p']) > 1:
            data[a_s]['class'] = 'Content'
        elif len(data[a_s]['as_links']['p2c']) > 0:
            data[a_s]['class'] = 'Transit'


def infer_t1(data):
    R = sorted(data, key=lambda k: data[k]['degree'], reverse=True)
    S = [R[0]]
    for node in R[1:]:
        connected = True
        for a_s in S:
            if (node not in data[a_s]['as_links']['p2p']) and (node not in data[a_s]['as_links']['p2c'] and (a_s not in data[node]['as_links']['p2p']) and (a_s not in data[node]['as_links']['p2c'])):
                connected = False
                break
        if connected:
            S.append(node)
    return S


def calc_cone(all_data, total_ip, total_pref):
    def dfs(data, cur_node, visited=None):
        if cur_node in data:
            for child in data[cur_node]['as_links']['p2c']:
                dfs(data, child, visited)
        return visited.add(cur_node)
    for a_s in all_data:
        print("dfs-ing a_s: {}".format(a_s))
        total_cone = set()
        total_prefixes = set()
        dfs(all_data, a_s, visited=total_cone)
        all_data[a_s]['customer_cone'] = {}
        all_data[a_s]['customer_cone']['cone'] = total_cone
        all_data[a_s]['customer_cone']['cone_size'] = len(total_cone)
        for cone_a_s in all_data[a_s]['customer_cone']['cone']:
            if cone_a_s in all_data:
                for x in all_data[cone_a_s]['prefixes']:
                    total_prefixes.add(x)
        all_data[a_s]['customer_cone']['prefixes'] = total_prefixes
        ips = 0
        for pref in all_data[a_s]['customer_cone']['prefixes']:
            sub_bits = int(pref.split('/')[1])
            ips += pow(2, 32 - sub_bits)
        all_data[a_s]['customer_cone']['ips'] = ips
        all_data[a_s]['customer_cone']['as_percentage'] = len(all_data[a_s]['customer_cone']['cone']) / len(all_data)
        all_data[a_s]['customer_cone']['prefix_percentage'] = len(all_data[a_s]['customer_cone']['prefixes']) / len(total_pref)
        all_data[a_s]['customer_cone']['ip_percentage'] = all_data[a_s]['customer_cone']['ips'] / total_ip


all_data = {}
all_prefixes = set()
read_data(all_data, all_prefixes)

# Calculate all IP's
total_ips = 0
for pref in all_prefixes:
    sub_bits = int(pref.split('/')[1])
    total_ips += pow(2, 32 - sub_bits)

calc_degree(all_data)
t1_as = infer_t1(all_data)
calc_cone(all_data, total_ips, all_prefixes)
print_data(all_data, t1_as, total_ips)
