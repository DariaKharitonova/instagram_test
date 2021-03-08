import argparse


def arg_parse():
    parser = argparse.ArgumentParser(description='get inst posts')
    parser.add_argument('username', type=str)
    parser.add_argument('password', type=str)
    parser.add_argument('target', type=str)
    return parser
