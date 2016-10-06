from string import strip
import yaml

def left_blank_count(line):
    count = 0
    for i in line:
        if i != '':
            return count
        else:
            count += 1
    return count


get_back = lambda x: ' '.join(x)


def line_key(line, ident_blank_count):
    return get_back(map(lambda x: x.replace(':', ''), line[ident_blank_count: ident_blank_count+1]))


def pop_stack(stack, length):
    while length>0:
        stack.pop()
        length -= 1

def seperate_yaml(to_move, file_location):
    origin_yaml, detached_yaml = [], []
    previous_old = True
    stack = []
    prev_blank_count, blanks_per_ident = 0, 2
    for line in open(file_location):
        line = line.rstrip().split(' ')
        ident_blank_count = left_blank_count(line)
        if ident_blank_count == len(line):
            prev_blank_count = 0
            if previous_old:
                origin_yaml.append(get_back(line))
            else:
                detached_yaml.append(get_back(line))
                previous_old = True
            continue
        if ident_blank_count == 0:
            key = get_back(line)
            stack = [key]
        if prev_blank_count > ident_blank_count:
            pop_count = (prev_blank_count-ident_blank_count)/blanks_per_ident+1
            pop_stack(stack, pop_count)
            stack.append(line_key(line, ident_blank_count))

        if prev_blank_count < ident_blank_count:
            if prev_blank_count == 0:
                blanks_per_ident = ident_blank_count-prev_blank_count

            stack.append(line_key(line, ident_blank_count))

        if prev_blank_count == ident_blank_count:
            stack.pop()
            stack.append(line_key(line, ident_blank_count))

        #seperate
        top_key = stack[0]
        if top_key in to_move:
            previous_old = False
            detached_yaml.append(get_back(line))
        else:
            origin_yaml.append(get_back(line))

        prev_blank_count = ident_blank_count
    return origin_yaml, detached_yaml


def update_yaml(to_update, file_location):
    new_yaml = []
    stack = []
    prev_blank_count, blanks_per_ident = 0, 2
    for line in open(file_location):
        line = line.rstrip().split(' ')
        ident_blank_count = left_blank_count(line)
        if ident_blank_count == len(line):
            prev_blank_count = 0
            new_yaml.append(get_back(line))
            continue
        if ident_blank_count == 0:
            key = get_back(line)
            stack = [key]
        if prev_blank_count > ident_blank_count:
            pop_count = (prev_blank_count-ident_blank_count)/blanks_per_ident+1
            pop_stack(stack, pop_count)
            stack.append(line_key(line, ident_blank_count))

        if prev_blank_count < ident_blank_count:
            if prev_blank_count == 0:
                blanks_per_ident = ident_blank_count-prev_blank_count

            stack.append(line_key(line, ident_blank_count))

        if prev_blank_count == ident_blank_count:
            stack.pop()
            stack.append(line_key(line, ident_blank_count))
        #update
        current_key = '.'.join(stack)
        if current_key in to_update:
            line[-1] = to_update[current_key]            

        new_yaml.append(get_back(line))

        prev_blank_count = ident_blank_count
    return new_yaml


def move_task():
    to_move = {'key_one', 'key_two'}
    origin_file_location = 'test.yml'
    updated_origin_yaml, detached_yaml = seperate_yaml(to_move, origin_file_location)

    with open('detached_origin.yml', 'w') as f:
        f.write('\n'.join(updated_origin_yaml))

    with open('detached.yml', 'w') as f:
        f.write('\n'.join(detached_yaml))

    origin = yaml.load(open(origin_file_location))
    new_origin = yaml.load('\n'.join(updated_origin_yaml))
    detached = yaml.load('\n'.join(detached_yaml))
    check_yaml(origin, new_origin, detached, to_move)


def update_task():
    to_update = {'key_one.second_key': 'new_value', 'key_two.second_key.third_key': 'new_value'}
    origin_file_location = 'test.yml'
    updated_origin_yaml = update_yaml(to_update, origin_file_location)

    with open('updated_origin.yml', 'w') as f:
        f.write('\n'.join(updated_origin_yaml))


def check_yaml(origin, new_origin, detached, detached_keys):
    all_key_exists_in_detached  = any(map(lambda x: x in detached, detached_keys))
    assert all_key_exists_in_detached
    all_key_in_new_origin = any(map(lambda x: x in new_origin, detached_keys))
    assert not all_key_in_new_origin
    all_value_the_same = lambda z: any(map(lambda x: x in origin and origin[x] == z[x], z))
    all_value_the_same_in_new_origin = all_value_the_same(new_origin)
    all_value_the_same_in_detached = all_value_the_same(detached)
    assert all_value_the_same_in_new_origin
    assert all_value_the_same_in_detached
    missing_keys = set(origin.keys()) - set(new_origin.keys()+detached.keys())
    assert not missing_keys

def main():
    move_task()
    update_task()

if __name__ == "__main__":
    main()
