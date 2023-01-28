import os
import pyparsing
from pyparsing import pyparsing_common
from pyparsing import Word, alphas, Suppress, Forward, ZeroOrMore, oneOf, Group, Keyword
from pyparsing.results import ParseResults
import locale

locale.setlocale(locale.LC_ALL, '')

class Expression:
    def __init__(self, tokens):
        self.tokens = tokens
    def eval(self, state, entities):
        res = 0
        multiplier = 1
        for token in self.tokens:
            if token == '+':
                multiplier = 1
            elif token == '-':
                multiplier = -1
            else:
                res += multiplier * token.eval(state, entities)
        return res

class Term:
    def __init__(self, tokens):
        self.tokens = tokens
    def eval(self, state, entities):
        res = 1
        divide = False
        for token in self.tokens:
            if token == '*':
                divide = False
            elif token == '/':
                divide = True
            else:
                if divide:
                    res /= token.eval(state, entities)
                else:
                    res *= token.eval(state, entities)
        return res

class Factor:
    def __init__(self, tokens):
        self.tokens = tokens
    def eval(self, state, entities):
        if type(self.tokens[0]) == ParseResults:
            return self.tokens[0][0].eval(state, entities)
        return self.tokens[0].eval(state, entities)

class Operand:
    def __init__(self, tokens):
        self.tokens = tokens
    def eval(self, state, entities):
        if type(self.tokens[0]) in {int, float}:
            return self.tokens[0]
        if self.tokens[0] not in state:
            print('Error: state does not contain ' + self.tokens[0])
            os._exit(0)
        return state[self.tokens[0]]

class Entity:
    def __init__(self, tokens):
        self.tokens = tokens
    def add_balance(self, entities, amount):
        entities[self.tokens[0]] += amount

class Fee:
    def __init__(self, tokens):
        self.tokens = tokens
    def eval(self, state, entities):
        value = self.tokens[1].eval(state, entities)
        self.tokens[3].add_balance(entities, -value)
        self.tokens[5].add_balance(entities, value)
        return value

class Define:
    def __init__(self, tokens):
        self.tokens = tokens
    def eval(self, state, entities):
        term = self.tokens[1]
        value = self.tokens[3].eval(state, entities)
        state[term] = value
        return value

class SizeParameter:
    def __init__(self, tokens):
        self.tokens = tokens
    def apply(self, config):
        data = {}
        if self.tokens[1] == 'all':
            data['mode'] = 'all'
        else:
            data['mode'] = self.tokens[2]
            data['num'] = self.tokens[1]
        config[self.tokens[0]] = data

class External:
    def __init__(self, tokens):
        self.tokens = tokens
    def validate(self, externals):
        if self.tokens[0] not in externals:
            print('Error: I don\'t know what ' + self.tokens[0] + ' is, valid externals include ' + ', '.join(externals))
            os._exit(0)
    def eval(self):
        return self.tokens[0]

class SimulatorConfig:
    def __init__(self):
        self.section_parser = Suppress('section') + Word(alphas + '_')
        self.config_parser = self.generate_config_parser()
        self.expression_parser = self.generate_expression_parser()
        self.financial_parser = self.generate_financial_parser()
        self.externals_parser = self.generate_externals_parser()
        self.externals = {'order_price', 'order_distance'}
        self.state = {}
        self.entities = {'government' : 0, 'consumer' : 0, 'restaurant' : 0, 'driver' : 0, 'company' : 0, 'gas' : 0}
        self.config = {}
        self.config_commands = []
        self.externals_commands = []
        self.financial_commands = []
        self.required_externals = set()
        self.run_count = 0
    def generate_externals_parser(self):
        externals_parser = Suppress('require') + Word(alphas + '_')
        externals_parser.add_parse_action(External)
        return externals_parser
    def generate_config_parser(self):
        groups = Keyword('drivers') | Keyword('orders') | Keyword('restaurants')
        distribution = pyparsing_common.integer + (Keyword('sequential') | Keyword('randomized'))
        size_parameter_parser = groups + (distribution | 'all')
        size_parameter_parser.add_parse_action(SizeParameter)
        return size_parameter_parser
    def generate_expression_parser(self):
        expr = Forward()
        LPAR, RPAR = map(Suppress, '()')
        operand = pyparsing_common.real | pyparsing_common.integer | Word(alphas + '_')
        operand.add_parse_action(Operand)
        factor = operand | Group(LPAR + expr + RPAR)
        factor.add_parse_action(Factor)
        term = factor + ZeroOrMore(oneOf('* /') + factor)
        term.add_parse_action(Term)
        expr <<= term + ZeroOrMore(oneOf('+ -') + term)
        expr.add_parse_action(Expression)
        return expr
    def generate_financial_parser(self):
        entity = Word(alphas + '_')
        entity.add_parse_action(Entity)
        fee = 'fee' + self.expression_parser + 'from' + entity + 'to' + entity
        fee.add_parse_action(Fee)
        define = 'define' + Word(alphas + '_') + 'as' + (fee | self.expression_parser)
        define.add_parse_action(Define)
        financial_parser = fee | define
        return financial_parser
    def parse_sections(self, lines):
        sections = {}
        current_section_name = ''
        current_section = []
        for line in lines:
            if line.startswith('section'):
                if len(current_section) > 0:
                    sections[current_section_name] = current_section
                    current_section = []
                current_section_name = self.section_parser.parseString(line)[0]
            elif len(line.strip()) > 0:
                current_section.append(line)
        if len(current_section) > 0:
            sections[current_section_name] = current_section
        return sections
    def parse(self, content):
        lines = list(map(lambda x: x.strip(), content.split('\n')))
        sections = self.parse_sections(lines)
        if 'params' in sections:
            for line in sections['params']:
                self.config_commands.append(self.config_parser.parse_string(line, parse_all = True)[0])
        if 'externals' in sections:
            for line in sections['externals']:
                command = self.externals_parser.parse_string(line, parse_all = True)[0]
                command.validate(self.externals)
                self.externals_commands.append(command)
        if 'finance' in sections:
            for line in sections['finance']:
                self.financial_commands.append(self.financial_parser.parse_string(line, parse_all = True)[0])
        self.init()
    def init(self):
        for command in self.config_commands:
            command.apply(self.config)
        for command in self.externals_commands:
            self.required_externals.add(command.eval())
    def run(self, externals):
        self.run_count += 1
        state_dict = dict(self.state, **{k : v for k, v in externals.items() if k in self.required_externals})
        for command in self.financial_commands:
            command.eval(state_dict, self.entities)
    def print_stats(self):
        print('Number of orders: ' + str(self.run_count))
        padding = max(len(x) for x in self.entities.keys()) + 5
        print('')
        print('Total revenue:')
        for k, v in self.entities.items():
            print('\t' + k + ' ' * (padding - len(k)) + locale.currency(v))
        print('')
        print('Orderly revenue:')
        for k, v in self.entities.items():
            print('\t' + k + ' ' * (padding - len(k)) + locale.currency(v / self.run_count))