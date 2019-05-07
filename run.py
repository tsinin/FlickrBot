#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import app


def parse_args():
    parser = argparse.ArgumentParser(description="Simple telegram bot",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--token-path", default="./token")

    parser.add_argument("--flickr-api-path", default="./flickr_api")

    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.token_path, "r") as token_file:
        token = token_file.read()
    with open(args.flickr_api_path, "r") as flickr_api_file:
        flickr_keys = flickr_api_file.read().split('\n')
    app.init_bot(token, flickr_keys)
    app.BOT.polling(none_stop=True, interval=1)


if __name__ == "__main__":
    main()
