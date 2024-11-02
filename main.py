import csv
import json
import logging
import os

NETRUNNER_EN_DATA = 'data/en/pack'
NETRUNNER_CN_DATA = 'data/cn/json/translations/zh-hans/pack'
NETRUNNER_PACK_LIST = 'data/en/packs.json'


def collect_schema(code: str, collector: set[str]):
    filename: str = os.path.join(NETRUNNER_EN_DATA, f'{code}.json')
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            cards: list[dict] = json.load(f)
            for c in cards:
                for k in c:
                    collector.add(k)

    filename: str = os.path.join(NETRUNNER_CN_DATA, f'{code}.zh-hans.json')
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            cards: list[dict] = json.load(f)
            for c in cards:
                for k in c:
                    collector.add(f'cn_{k}')


def create_schema(bundles: list[str]) -> list[str]:
    collector: set[str] = set()
    for b in bundles:
        collect_schema(b, collector)

    result: list[str] = list(collector)
    result.sort()
    logging.info(f'read schema: {len(result)}!')
    logging.info(f'schema: {result}')
    return result


def read_bundle() -> list[str]:
    count = 0
    result: list[str] = list()
    with open(NETRUNNER_PACK_LIST, 'r', encoding='utf-8') as f:
        bundles: list[dict] = json.load(f)
        for b in bundles:
            result.append(b['code'])
            if isinstance(b['size'], int):
                count += b['size']

    logging.info(f'count cards: {count}!')
    logging.info(f'read bundles: {len(result)}!')
    logging.info(f'bundles: {result}')
    return result


def collect_card(code: str, schema: list[str], collector: dict[str, dict[str, str]]):
    filename: str = os.path.join(NETRUNNER_EN_DATA, f'{code}.json')
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            cards: list[dict] = json.load(f)
            for c in cards:
                item: dict[str, str] = dict()
                for k in schema:
                    if k in c:
                        item[k] = str(c[k])
                    else:
                        item[k] = ''

                collector[item['code']] = item


def read_card(bundles: list[str], schema: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = dict()
    for b in bundles:
        collect_card(b, schema, result)

    logging.info(f'read cards: {len(result)}!')
    return result


def collect_translation(code: str, collector: dict[str, dict[str, str]]):
    filename: str = os.path.join(NETRUNNER_CN_DATA, f'{code}.zh-hans.json')
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            cards: list[dict] = json.load(f)
            for c in cards:
                if 'code' not in c:
                    continue

                item = collector[c['code']]
                for k in c:
                    item[f'cn_{k}'] = str(c[k])


def read_translation(bundles: list[str], collector: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    for b in bundles:
        collect_translation(b, collector)

    result: list[dict[str, str]] = list()
    for k, v in collector.items():
        result.append(v)

    return result


def run():
    logging.basicConfig(level=logging.INFO, encoding='utf-8')

    bundles: list[str] = read_bundle()
    schema: list[str] = create_schema(bundles)
    cards: dict[str, dict[str, str]] = read_card(bundles, schema)
    result: list[dict[str, str]] = read_translation(bundles, cards)

    with open('cards.json', 'w', encoding='utf-8') as f:
        text = json.dumps(result, ensure_ascii=False)
        f.write(text)


if __name__ == '__main__':
    run()
