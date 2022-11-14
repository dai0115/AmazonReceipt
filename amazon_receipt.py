import os
import argparse
import sys
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

URL = 'https://www.amazon.co.jp/'


def parse_args():
    '''コマンドラインから引数を受け付ける'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count',
                        action='store',
                        default=10,
                        help='set num of invoice you want to download',
                        type=int)
    parser.add_argument('-b', '--browser',
                        action='store',
                        default='chromedriver',
                        help='choose which browser to use.\
                        default is google chrome',
                        type=str)
    parser.add_argument('-y', '--year',
                        action='store',
                        help='choose which year receipt you need',
                        type=str)
    parser.add_argument('--headless',
                        action='store_true',
                        help='default is False(not headless mode)')
    args = parser.parse_args()
    # --yearが設定されなかった場合は現在の年を設定する
    if args.year is None:
        args.year = str(datetime.date.today().year)
    return args


def create_driver(headless, browser_type):
    '''
    オプションを設定した上でドライバーを作成
    # headless True -> ヘッドレスモードで起動
    # browser_type -> ブラウザのタイプを選択。デフォルトはchrome
    '''
    driver_path = os.getcwd() + '/' + browser_type
    service = Service(executable_path=driver_path)
    options = Options()
    # 現環境では設定変更できない(jamfproによって設定の変更ができないため)
    # options.add_experimental_option('prefs', {
    #     'download.default_directory': os.getcwd() + '/invoice',
    #     "download.directory_upgrade": True,
    #     "download.prompt_for_download": False,
    # })
    options.add_argument('--kiosk-printing')
    options.add_experimental_option('detach', True)
    # ヘッドレスモードにするのは引数で指定された時だけ
    if headless:
        options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def has_sec_alert() -> bool:
    try:
        return driver.find_element(
            By.ID, 'channelDetailsWithImprovedLayout'
        ) is not None
    except NoSuchElementException:
        return False


def login():
    '''amazonサイトにログイン'''
    driver.get(URL)
    driver.implicitly_wait(2)
    driver.find_element(By.ID, 'nav-link-accountList').click()
    driver.implicitly_wait(2)
    driver.find_element(By.ID, 'ap_email').send_keys(os.getenv('EMAIL'))
    driver.implicitly_wait(2)
    driver.find_element(By.ID, 'continue').click()
    driver.implicitly_wait(2)
    driver.find_element(By.ID, 'ap_password').send_keys(os.getenv('PASS'))
    driver.implicitly_wait(2)
    driver.find_element(By.ID, 'signInSubmit').click()
    driver.implicitly_wait(2)
    if has_sec_alert():
        # セキュリティ通知アラートが発生した場合、それ以上処理の継続不可
        print('セキュリティ通知を承認した跡で再度お試しください')
        sys.exit()


def disp_order_history(year):
    '''注文履歴画面への遷移と指定された年の購入情報を表示'''
    driver.find_element(By.ID, 'nav-orders').click()
    driver.implicitly_wait(2)
    dropdown = driver.find_element(By.ID, 'time-filter')
    select = Select(dropdown)
    select.select_by_value('year-' + year)
    driver.implicitly_wait(2)


def get_receipt(count):
    '''レシートのダウンロードを実行'''
    inner_text = driver.find_element(By.CLASS_NAME, 'num-orders').text
    num_orders = int(inner_text.strip('件'))
    print(f"全{num_orders}件の中から{count}件をダウンロードします。")
    for i in range(count):
        # orderの合計件数以上になったら処理終了
        if i >= num_orders:
            break
        # 商品を10件参照したら次のページに遷移する
        if (i + 1) % 10 == 0:
            # 次のページへ
            driver.find_element(By.LINK_TEXT, '次へ→').click()
            driver.implicitly_wait(2)
        orders = driver.find_elements(By.LINK_TEXT, '領収書等')
        # 2ページ目以降でインデックス番号をリセットする必要があるためiの値から再作成する
        index = i % 10
        orders[index].click()
        driver.implicitly_wait(2)
        driver.find_element(By.LINK_TEXT, '領収書／購入明細書').click()
        driver.implicitly_wait(2)
        driver.execute_script('window.print();')
        driver.implicitly_wait(2)
        driver.back()
        driver.implicitly_wait(2)


if __name__ == '__main__':
    args = parse_args()
    driver = create_driver(args.headless, args.browser)
    login()
    disp_order_history(args.year)
    get_receipt(args.count)
