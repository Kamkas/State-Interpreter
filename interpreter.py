import json
import csv
import math


class StateInterpreter:
    def __init__(self):
        self.graph = None
        self.matrix = None

        self.states = []
        self.states_code = {}

        self.in_values = []
        self.uniq_in_values = []

        self.out_values = []
        self.uniq_out_values = {}

        self.condition_values = []
        self.func_iter = []

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

        self.__generate_states_codes()

    def __generate_states_codes(self):
        if 2**(math.floor(math.log2(len(self.states)))) < len(self.states):
            bin_length = math.floor(math.log2(len(self.states))) + 1
        else:
            bin_length = math.floor(math.log2(len(self.states)))

        bin_format = '0{}b'.format(bin_length)
        for code, state in enumerate(self.states):
            self.states_code.update({state: format((code ^ (code>>1)), bin_format)})

    def read_matrix(self, filename):
        with open(filename, 'r') as f:
            self.matrix = json.loads(f.read())
            f.close()

        scheme = self.matrix["scheme"]
        self.condition_values = self.matrix["condition_code"]

        for key, value in scheme.items():
            if key not in self.out_values:
                self.out_values.append(key)
            for item in value:
                cur_state_code, cond_code, next_state_code = item.split(";")
                if cur_state_code not in self.states:
                    self.states.append(cur_state_code)
                if next_state_code not in self.states:
                    self.states.append(next_state_code)

        self.__pack_states_from_matrix()

    def __pack_states_from_matrix(self):
        for state_code in self.states:
            matches = []
            for item in (item for l in self.matrix['scheme'].values() for item in l):
                cur_s, cond_code, next_s = item.split(";")
                if state_code == cur_s and item not in matches:
                    matches.append(item)

            self.states_code.update({state_code: matches})

    def __get_condition_varification(self, cond_code):
        check = False
        is_step = 1
        if list(cond_code).count('.') == len(cond_code):
            check = True
        for in1, in2 in zip(cond_code, self.condition_values):
            if in1 is not '.':
                if in1 != str(in2):
                    is_step *= 0
        if is_step == 1:
            return True
        else:
            return False

    def __form_func_initiation(self, path):
        self.func_iter = []
        if self.graph:
            for index in range(1, len(path)):
                tmp = []
                cur_state, next_state = self.states_code[path[index - 1]], self.states_code[path[index]]
                for index, (alp1, alp2) in enumerate(zip(cur_state, next_state)):
                    if alp1 is "0" and alp2 is "1":
                        tmp.append("w{}".format(index + 1))
                    elif alp1 is "1" and alp2 is "0":
                        tmp.append("v{}".format(index + 1))
                self.func_iter.append(tmp)
        elif self.matrix:
            for node in path:
                tmp = []
                cur_state, _, next_state = node.split(';')
                for index, (alp1, alp2) in enumerate(zip(cur_state, next_state)):
                    if alp1 is "0" and alp2 is "1":
                        tmp.append("w{}".format(index + 1))
                    elif alp1 is "1" and alp2 is "0":
                        tmp.append("v{}".format(index + 1))
                self.func_iter.append(tmp)

    def set_condition(self, string):
        uniq_in_val_dict = {}
        self.condition_values = [int(i) for i in string]
        for index, x_val in enumerate(self.uniq_in_values):
            uniq_in_val_dict.update({x_val: self.condition_values[index]})
        self.uniq_in_values = uniq_in_val_dict

    def __get_state_from_graph(self, state_name):
        for state in self.graph:
            if state["state"] == state_name:
                return state

    def __get_output_vals(self, path):
        for out_val in self.out_values:
            self.uniq_out_values.update({out_val: 0})

        if self.graph:
            for state_name in path:
                state = self.__get_state_from_graph(state_name)
                for o_vals in state['output']:
                    self.uniq_out_values[o_vals] = 1
        elif self.matrix:
           for k, v in self.matrix["scheme"].items():
                for node in path:
                    if node in v:
                        self.uniq_out_values[k] = 1
                        break

    def run_graph(self, start_state="S1"):
        path = []
        cycle = True
        next_state = start_state
        path.append(next_state)
        while cycle:
            cur_state = self.__get_state_from_graph(next_state)
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
        self.__form_func_initiation(path)
        return path

    def run_matrix(self):
        path = []
        next_state = self.matrix["start_state_code"]
        while True:
            res = [self.__get_condition_varification(item.split(";")[1]) for item in self.states_code[next_state]]
            if res.count(True) == 1:
                path.append(self.states_code[next_state][res.index(True)])
                next_state = self.states_code[next_state][res.index(True)].split(";")[2]
                if next_state == self.matrix["start_state_code"]:
                    break
                if path.count(path[-1:][0]) > 5:
                    break
            if res.count(True) == 0:
                break
            if res.count(True) > 1:
                break

        self.__get_output_vals(path)
        self.__form_func_initiation(path)
        return path


if __name__ == '__main__':
    s = StateInterpreter()
    s.read_matrix("matrix_format.json")
    s.set_condition('1111')
    path = s.run_matrix()
    pass