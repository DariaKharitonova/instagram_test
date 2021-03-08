from get_inst_posts.cli import arg_parse
from get_inst_posts.get_posts import get_posts


def main():
    args = arg_parse().parse_args()
    result = get_posts(args.username, args.password, args.target)
    print(result)


if __name__ == '__main__':
    main()
