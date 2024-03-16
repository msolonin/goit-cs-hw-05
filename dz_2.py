# -*- coding: utf-8 -*-
"""
Напишіть Python-скрипт, який завантажує текст із заданої URL-адреси, аналізує частоту використання слів у
тексті за допомогою парадигми MapReduce і візуалізує топ-слова з найвищою частотою використання у тексті.
"""
import argparse
import string
import asyncio
from collections import defaultdict, Counter

import httpx
from matplotlib import pyplot as plt


parser = argparse.ArgumentParser(description="Calculate word frequency")
parser.add_argument("--url", "-u", required=False, help="url with text")
args = vars(parser.parse_args())

URL = args["url"] or "https://gutenberg.net.au/ebooks01/0100021.txt"


async def get_text(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None


# Функція для видалення знаків пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


async def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


async def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


# Виконання MapReduce
async def map_reduce(url):
    text = await get_text(url)
    text = remove_punctuation(text)
    words = text.split()
    mapped_result = await asyncio.gather(*[map_function(word) for word in words])
    shuffled_values = shuffle_function(mapped_result)
    reduced_result = await asyncio.gather(
        *[reduce_function(values) for values in shuffled_values]
    )
    return dict(reduced_result)


def visualize_top_words(result, top_n=10):
    top_words = Counter(result).most_common(top_n)
    words, counts = zip(*top_words)
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Top {} Most Frequent Words'.format(top_n))
    plt.show()


if __name__ == '__main__':
    result = asyncio.run(map_reduce(URL))
    visualize_top_words(result)
