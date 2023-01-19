import json
import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_all_pages():
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    r = requests.get(url="https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/", headers=headers)

    # если нет такой папки то создать
    if not os.path.exists("data"):
        os.mkdir("data")

    # сохраняем код html сайта
    with open("data/page_1.html", "w") as file:
        file.write(r.text)

    with open("data/page_1.html") as file:
        src = file.read()

    # объект супа
    soup = BeautifulSoup(src, "lxml")
    # забираем к-во погинаций из дива (берем последнюю)
    pages_count = int(soup.find("div", class_="bx-pagination-container").find_all("a")[-2].text)

    for i in range(1, pages_count + 1):
        url = f"https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/?PAGEN_1={i}"

        r = requests.get(url=url, headers=headers)

        # записываем все 5 страниц в html
        with open(f"data/page_{i}.html", "w") as file:
            file.write(r.text)

        time.sleep(2)  # пауза

    return pages_count + 1  # возвращаем к-во страниц


def collect_data(pages_count):
    cur_date = datetime.now().strftime("%d_%m_%Y")  # текущая дата в формате 

    with open(f"data_{cur_date}.csv", "w") as file:
        # наш писатель в фай
        writer = csv.writer(file)
        # заголовки 
        writer.writerow(
            (
                "Артикул",
                "Ссылка",
                "Цена"
            )
        )

    data = []
    for page in range(1, pages_count):
        # открываем
        with open(f"data/page_{page}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        # все карточки часов в теге по классу
        items_cards = soup.find_all("a", class_="product-item__link")

        for item in items_cards:
            # в каждой забираем
            product_article = item.find("p", class_="product-item__articul").text.strip()
            # обрежем с лева строку 
            product_price = item.find("p", class_="product-item__price").text.lstrip("руб. ")
            product_url = f'https://shop.casio.ru{item.get("href")}'

            print(f"Article: {product_article} - Price: {product_price} - URL: {product_url}")

            data.append(
                {
                    "product_article": product_article,
                    "product_url": product_url,
                    "product_price": product_price
                }
            )
            # заполняем список словарями 

            with open(f"data_{cur_date}.csv", "a") as file:
                writer = csv.writer(file)
                # добавляем строки 
                writer.writerow(
                    (
                        product_article,
                        product_url,
                        product_price
                    )
                )

        print(f"[INFO] Обработана страница {page}/5")  # какая страница сейчас

    # список в json 
    with open(f"data_{cur_date}.json", "a") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    pages_count = get_all_pages()
    collect_data(pages_count=pages_count)


if __name__ == '__main__':
    main()
