import time
import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary

URL="https://www.facebook.com/login.php?skip_api_login=1&api_key=179279322170193&signed_next=1&next=https%3A%2F%2Fwww.facebook.com%2Fv2.10%2Fdialog%2Foauth%3Fchannel%3Dhttps%253A%252F%252Fstaticxx.facebook.com%252Fconnect%252Fxd_arbiter%252Fr%252FlY4eZXm_YWu.js%253Fversion%253D42%2523cb%253Df24f95f5dc5eb8%2526domain%253Dwww.omiai-jp.com%2526origin%253Dhttps%25253A%25252F%25252Fwww.omiai-jp.com%25252Ff38e8febe3de2f4%2526relation%253Dopener%26redirect_uri%3Dhttps%253A%252F%252Fstaticxx.facebook.com%252Fconnect%252Fxd_arbiter%252Fr%252FlY4eZXm_YWu.js%253Fversion%253D42%2523cb%253Df19e5d3bebfa7b8%2526domain%253Dwww.omiai-jp.com%2526origin%253Dhttps%25253A%25252F%25252Fwww.omiai-jp.com%25252Ff38e8febe3de2f4%2526relation%253Dopener%2526frame%253Df2c96967c5d9a68%26display%3Dpopup%26scope%3Duser_relationships%252Cuser_birthday%252Cemail%252Cuser_location%252Cuser_friends%26response_type%3Dtoken%252Csigned_request%26domain%3Dwww.omiai-jp.com%26auth_type%3Drerequest%26origin%3D1%26client_id%3D179279322170193%26ret%3Dlogin%26sdk%3Djoey%26logger_id%3D2bbef1ce-9c45-f9f6-b201-3ee83135b3d4&cancel_url=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter%2Fr%2FlY4eZXm_YWu.js%3Fversion%3D42%23cb%3Df19e5d3bebfa7b8%26domain%3Dwww.omiai-jp.com%26origin%3Dhttps%253A%252F%252Fwww.omiai-jp.com%252Ff38e8febe3de2f4%26relation%3Dopener%26frame%3Df2c96967c5d9a68%26error%3Daccess_denied%26error_code%3D200%26error_description%3DPermissions%2Berror%26error_reason%3Duser_denied%26e2e%3D%257B%257D&display=popup&locale=ja_JP&logger_id=2bbef1ce-9c45-f9f6-b201-3ee83135b3d4"
OMIAIURL = "https://www.omiai-jp.com/mypage/to"
EMAIL = ""
PASSWORD = ""

USERCLASS = "om-list-item-row clearfix"

def main():
    options = Options()
    # ヘッドレスモードで実行する場合
    # options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    try:
        # フェイスブックにログイン
        facebookLogin(driver)

        # お見合いのログイン
        omiaiLogin(driver)

        # お見合いのスクレイピング開始
        startScraping(driver)

    except:
        traceback.print_exc()
    finally:
        # エラーが起きても起きなくてもブラウザを閉じる
        driver.quit()

def facebookLogin(driver):
    driver.get(URL)
    time.sleep(2)

    # メールアドレス入力
    driver.find_element_by_id('email').send_keys(EMAIL)
    # パスワード
    driver.find_element_by_id('pass').send_keys(PASSWORD)
    # 適当にクリック
    driver.find_element_by_xpath('//*[@id="email_container"]/div/label').click()
    time.sleep(2)

    # ログインボタン
    driver.find_element_by_id('u_0_0').click()
    time.sleep(2)


def omiaiLogin(driver):
    driver.get(OMIAIURL)
    # 簡易的にJSが評価されるまで秒数で待つ
    time.sleep(5)

    # すでに登録されている方はこちら
    driver.find_element_by_id('om-button-phone-number-login').click()
    time.sleep(2)
    
    # Facebookでログイン
    driver.find_element_by_id('om-button-fb-login').click()
    time.sleep(5)


def startScraping(driver):
    driver.get(OMIAIURL)
    time.sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            break
        else:
            last_height = new_height

    list_df = pd.DataFrame(columns=['名前', 'ユーザの状態', 'マッチング％', '年齢、居住地', 'いいねした日', '身長、仕事'])
    userList = driver.find_elements_by_class_name("om-list-item-row")

    count = 0
    for user in userList:
        count = count + 1
        name = user.get_attribute("data-nickname")  # ユーザ名
        isScession = user.get_attribute("data-secession-flag")  # ユーザの状態　0:退会していない/1:退会済み

        if(isScession == "0"):
            percentTag = user.find_element_by_class_name("fill")
            percent = percentTag.get_attribute("stroke-dasharray")  # マッチング％

            age = user.find_element_by_class_name("om-list-primary-info-text").text    # 年齢、居住地

            iineDate = user.find_element_by_class_name("om-list-datetime").text    # いいねした日

            work = user.find_element_by_class_name("om-list-sub-info").text    # 身長、仕事
        else:
            percent = ""
            age = ""
            iineDate = ""
            work = ""

        tmp_se = pd.Series([name, isScession, percent, age, iineDate, work], index=list_df.columns)
        list_df = list_df.append( tmp_se, ignore_index=True )

    list_df.to_csv('name.csv')

if __name__ == '__main__':
    main()