import json


class StateInterpreter:
    def __init__(self):
        self.graph = None
        self.matrix = None
        self.states = []
        self.in_values = []
        self.uniq_in_values = []
        self.out_values = []
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
        with open(filename, 'r') as f:
            string = f.read()
            f.close()

        self.matrix = [[int(val) for val in l.split(',')] for l in string.split('\n')]

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
                elif jmps.count(1) == 0:
                    break
                elif jmps.count(1) >= 1:
                    break
        return path


if __name__ == '__main__':
    s = StateInterpreter()
    s.read_graph('graph_format.json')
    s.set_condition('1111')
    p = s.run()
    pass
