import json
import csv


class StateInterpreter:
    def __init__(self):
        self.graph = None
        self.matrix = None
        self.states = []
        self.in_values = []
        self.uniq_in_values = []
        self.out_values = []
        self.uniq_out_values = {}
        self.condition_values = []

    def read_graph(self, filename):
        with open(filename, 'r') as f:
            self.graph = json.loads(f.read())
            f.close()

        for state in self.graph:
            if state['state'] not in self.states:
                self.states.append(state['state'])
            else:
                raise Exception('{} is already in defined!'.format(state['state']))
            for out_vals in state['output']:
                if out_vals not in self.out_values:
                    self.out_values.append(out_vals)
            for in_vals in state['conditions'].keys():
                if in_vals not in self.in_values and in_vals is not "1":
                    self.in_values.append(in_vals)

        for index, val in enumerate(self.in_values):
            s_vals = val.split(" ")
            for item in s_vals:
                if not item.startswith('!', 0) and item not in self.uniq_in_values:
                    self.uniq_in_values.append(item)
            self.in_values[index] = s_vals

    def read_matrix(self, filename):
        self.graph = []
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            tmp = [row for row in reader]

        for el in tmp[0][1:-1]:
            if el not in self.states:
                self.states.append(el)
        for index in range(1, len(tmp)):
            if tmp[index][0] not in self.states:
                raise Exception('{} state is not defined in matrix format'.format(tmp[index][0]))

        for row in tmp[1:]:
            state = {"state": row[0], "output": [], "conditions": {}}
            for o_vals in row[-1:][0].split(','):
                if o_vals is not '':
                    state["output"].append(o_vals)
                    if o_vals not in self.out_values:
                        self.out_values.append(o_vals)
            for idx, el in enumerate(row[1:-1]):
                if el is not '':
                    state["conditions"].update({el: self.states[idx]})
                    if el is not '1':
                        s_vals = el.split(" ")
                        for item in s_vals:
                            if not item.startswith('!', 0) and item not in self.uniq_in_values:
                                self.uniq_in_values.append(item)
                        self.in_values.append(s_vals)
            self.graph.append(state)

    def set_condition(self, string):
        uniq_in_val_dict = {}
        self.condition_values = [int(val) for val in string]
        for index, x_val in enumerate(self.uniq_in_values):
            uniq_in_val_dict.update({x_val: self.condition_values[index]})
        self.uniq_in_values = uniq_in_val_dict

    def __get_state(self, state_name):
        for state in self.graph:
            if state["state"] == state_name:
                return state

    def __get_output_vals(self, path):
        for out_val in self.out_values:
            self.uniq_out_values.update({out_val: 0})

        for state_name in path:
            state = self.__get_state(state_name)
            for o_vals in state['output']:
                self.uniq_out_values[o_vals] = 1

    def run(self, start_state="S1"):
        path = []
        cycle = True
        next_state = start_state
        path.append(next_state)
        while cycle:
            cur_state = self.__get_state(next_state)
            if list(cur_state['conditions'].keys())[0] is '1':
                next_state = cur_state['conditions']['1']
                path.append(next_state)
                if next_state == start_state:
                    break
                if path.count(next_state) > 10:
                    break
            else:
                jmps = []
                for k, v in cur_state['conditions'].items():
                    cond_list = k.split(' ')
                    jmp = 1
                    for item in cond_list:
                        if item.startswith('!', 0):
                            jmp *= self.uniq_in_values[item[1:]] ^ 1
                        else:
                            jmp *= self.uniq_in_values[item]
                    jmps.append(jmp)
                if jmps.count(1) == 1:
                    next_state = list(cur_state['conditions'].values())[jmps.index(1)]
                    path.append(next_state)
                    if next_state == start_state:
                        break
                    if path.count(next_state) > 10:
                        break
                elif jmps.count(1) == 0:
                    break
                elif jmps.count(1) >= 1:
                    break
        self.__get_output_vals(path)
        return path


if __name__ == '__main__':
    s1 = StateInterpreter()
    s2 = StateInterpreter()
    s1.read_matrix('var1.csv')
    s2.read_graph('graph_format.json')
    s1.set_condition('1111')
    s2.set_condition('1111')
    p1 = s1.run()
    p2 = s2.run()
    pass
