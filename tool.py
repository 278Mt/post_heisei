import re
import os
import random
import urllib.parse
from time import sleep
from bs4 import BeautifulSoup
import requests
import tkinter
import tkinter.filedialog
import subprocess
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
nowdir = os.getcwd()+"\\"

def replaceurl(url):
    url = url.replace(" ", "+")
    url = url.replace("#", "%23")
    url = url.replace("+&+", "+%26+")
    return url


def get_soup(target_url):
    target_html = requests.get(target_url).text
    with open("test.html", mode="w", encoding="utf-8") as file:
        file.write(target_html)

    soup = BeautifulSoup(target_html, "html.parser")

    while soup.find("form", action="/errors/validateCaptcha") is not None or soup.find("body", bgcolor="#FFFFFF") is not None:
        print("ページを再取得します")
        with open("log.txt", mode="a", encoding="sjis") as file:
            file.write("ページを再取得します")
        sleep(random.uniform(10, 15))

        target_html = requests.get(target_url).text
        with open("test.html", mode="w", encoding="utf-8") as file:
            file.write(target_html)
        soup = BeautifulSoup(target_html, "html.parser")
                
    return soup


class AmazonInfoGetter(object):

    def __init__(self, init=True):
        self.init = init


    def info(self, seller="", fname="", brands="未選択", word=""):
        #options = Options()
        #options.add_argument('--headless')
        #driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
        print("取得を開始します。")
        with open("log.txt", mode="w", encoding="sjis") as file:
            file.write("取得を開始します。")

        target_csv = fname
        
        url = "https://www.amazon.co.jp/gp/search/other?pickerToList=brandtextbin&me="+seller
        soup = get_soup(url)
        ul = soup.find("div", id="refinementList")
        if ul is None:
            lis = []
        else:
            lis = ul.find_all("li")

        brand_urls = []

        for li in lis:
            if re.sub("\([0-9]+\)$", "", li.text) in brands:
                print(re.sub("\([0-9]+\)$", "", li.text))
                brand_urls.append(li.find("a")["href"])
        print(brand_urls) 

        if self.init:
            with open(target_csv, mode="w", encoding="sjis") as file:
                file.write(seller+",ASIN,ブランド,コンディション,価格,送料,新品出品数,中古出品数,FBAか否か\n")

        for brand_url in brand_urls:

            soup = get_soup("https://www.amazon.co.jp"+brand_url)

            target_div = soup.find("div", id="pagn")
            target_spans = target_div.find_all("span")
            pages = 1
            for target_span in target_spans:
                target_text = re.search("[0-9]+", target_span.text)
                if target_text is not None:
                    pages = int(target_text.group(0))

            print("出品者ID", seller, "の以下ブランドのURL","を取得します。ページ数は", pages, "です。")
            print(brand_url)
            with open("log.txt", mode="a", encoding="sjis") as file:
                file.write("\n出品者ID"+seller+"の出品者は"+str(pages)+"ページあります。")

            target_urls = []

            for page in range(1, pages+1):
                target_url = "https://www.amazon.co.jp/s?me="+seller+"&page="+str(page)
                target_url = replaceurl(target_url)
                soup = get_soup(target_url)

                target_ul = soup.find("ul", id="s-results-list-atf")
                target_lis = target_ul.find_all("li")
    
                for target_li in target_lis:
                    target_urls.append(target_li.find("a")["href"])

            for target_url in target_urls:
                target_url = urllib.parse.unquote(target_url)
                with open("log.txt", mode="a", encoding="sjis") as file:
                    target_url_sjis = target_url
                    target_url_sjis = target_url_sjis.replace(u'\uff3c',u'\u005c')
                    target_url_sjis = target_url_sjis.replace(u'\uff5e',u'\u301c')
                    target_url_sjis = target_url_sjis.replace(u'\u2225',u'\u2016')
                    target_url_sjis = target_url_sjis.replace(u'\uff0d',u'\u2212')
                    target_url_sjis = target_url_sjis.replace(u'\uffe0',u'\u00a2')
                    target_url_sjis = target_url_sjis.replace(u'\uffe1',u'\u00a3')
                    target_url_sjis = target_url_sjis.replace(u'\uffe2',u'\u00ac')

                    file.write("\n"+target_url_sjis)
                
                soup = get_soup(target_url)

                target_title = self._get_title(soup)
                target_asin = self._get_asin(target_url)
                target_cheap_cond, target_cheap_cost, target_postage, target_new, target_used, target_fba = self._get_stock(target_asin)
                try:
                    target_brand = soup.find("a", id="bylineInfo").text
                except:
                    target_brand = ""

                if word != "":
                    if word not in target_title:
                        continue

                print(target_url)

                print("タイトル      :", target_title)
                print("ASINコード    :", target_asin)
                print("ブランド      :", target_brand)
                print("コンディション:", target_cheap_cond)
                print("価格          :", target_cheap_cost)
                print("送料          :", target_postage)
                print("新品出荷数    :", target_new)
                print("中古出荷数    :", target_used)
                print("FBAか否か     :", target_fba)


                target_title = target_title.replace(u'\uff3c',u'\u005c')
                target_title = target_title.replace(u'\uff5e',u'\u301c')
                target_title = target_title.replace(u'\u2225',u'\u2016')
                target_title = target_title.replace(u'\uff0d',u'\u2212')
                target_title = target_title.replace(u'\uffe0',u'\u00a2')
                target_title = target_title.replace(u'\uffe1',u'\u00a3')
                target_title = target_title.replace(u'\uffe2',u'\u00ac')

                target_brand = target_brand.replace(u'\uff3c',u'\u005c')
                target_brand = target_brand.replace(u'\uff5e',u'\u301c')
                target_brand = target_brand.replace(u'\u2225',u'\u2016')
                target_brand = target_brand.replace(u'\uff0d',u'\u2212')
                target_brand = target_brand.replace(u'\uffe0',u'\u00a2')
                target_brand = target_brand.replace(u'\uffe1',u'\u00a3')
                target_brand = target_brand.replace(u'\uffe2',u'\u00ac')

                with open("log.txt", mode="a", encoding="sjis") as file:
                    file.write("\nタイトル      :"+target_title)
                    file.write("\nASINコード    :"+target_asin)
                    file.write("\nブランド      :"+target_brand)
                    file.write("\nコンディション:"+target_cheap_cond)
                    file.write("\n価格          :"+target_cheap_cost)
                    file.write("\n送料          :"+target_postage)
                    file.write("\n新品出荷数    :"+target_new)
                    file.write("\n中古出荷数    :"+target_used)
                    file.write("\nFBAか否か     :"+target_fba)
            
                with open(target_csv, mode="a", encoding="sjis") as file:
                    file.write("\""+target_title+"\",\""+target_asin+"\",\""+target_brand+"\",\""+target_cheap_cond+"\",\""+target_cheap_cost+"\",\""+target_postage+"\",\""+target_new+"\",\""+target_used+"\",\""+target_fba+"\"\n")

                sleep(random.uniform(3, 10))
        print("データ取得終了")

    def _get_title(self, soup):
        target_h1 = soup.find("h1", id="title")
        target_span = target_h1.find("span", id="productTitle")
        target_title = re.sub("\s*", "", target_span.text)

        return target_title

    def _get_asin(self, url):
        target_asin = url.split("/")[-1]
        return target_asin

    def _get_stock(self, asin):
        target_url = "https://www.amazon.co.jp/gp/offer-listing/"+asin+"/ref=dp_olp_all_mbc?condition=all"
        soup = get_soup(target_url)

        target_div = soup.find("div", class_="a-section a-padding-small")

        target_divs = target_div.find_all("div", class_="a-row a-spacing-mini olpOffer")

        target_new = 0
        target_used = 0

        target_span = target_divs[0].find("span", class_="a-size-large a-color-price olpOfferPrice a-text-bold")
        target_cheap_cost = re.sub("[^0-9]", "", target_span.text)

        target_span = target_div.find("span", class_="a-size-medium olpCondition a-text-bold")
        target_cheap_cond = re.sub("\s", "", target_span.text)

        target_p = target_divs[0].find("p", class_="olpShippingInfo").text

        target_div = target_divs[0].find("div", class_="olpBadgeContainer")
        if target_div is None:
            target_fba = "FBAでない"
        else:
            target_fba = "FBAである"

        if "無料" in target_p:
            target_postage = 0
        else:
            target_postage = re.sub("[^0-9]", "", target_p)

        for target_div in target_divs:
            target_span = target_div.find("span", class_="a-size-large a-color-price olpOfferPrice a-text-bold")
            target_cost = re.sub("[^0-9]", "", target_span.text)

            target_span = target_div.find("span", class_="a-size-medium olpCondition a-text-bold")
            target_cond = re.sub("\s", "", target_span.text)

            if "新品" in target_cond:
                target_new += 1
            elif "中古品" in target_cond:
                target_used += 1

        return target_cheap_cond, target_cheap_cost, str(target_postage), str(target_new), str(target_used), target_fba

class GraphicUserInterface(object):

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("アマゾン検索データーの取得")
        self.root.geometry("400x600")

        self.EntryFnames = []

        self._frame_seller()
        self._frame_narrow()
        self._frame_output()
        self._frame_save_property()
        self._frame_after_end()
        self._frame_get_button()
        self._frame_dialog()

        self.root.mainloop()

    def _frame_seller(self):
        # set label and entry of seller id
        FrameSeller = tkinter.Frame(self.root, pady=10)
        FrameSeller.pack()
        LabelSeller = tkinter.Label(FrameSeller, font=("",14), text="出品者ID")
        LabelSeller.pack(side="left")

        # make combo box of seller id
        self.Combo = ttk.Combobox(FrameSeller, state="readonly", font=("", 14), width=13)
        listc = []
        with open(nowdir+"combo.csv", encoding="utf-8") as file:
            listc.extend(file.read().split("\n"))
            print(listc[:-1])
        self.Combo["values"] = listc[:-1]
        self.Combo.current(0)
        self.Combo.pack()

    def _check_narrow(self):
        if self.VarNarrow.get():
            self.EditBoxNarrow.configure(state="normal", background="#ffffff")
        else:
            self.EditBoxNarrow.configure(state="disabled", background="#a0a0a0")

    def _frame_narrow(self):
        FrameNarrow = tkinter.Frame(self.root, pady=10)
        FrameNarrow.pack()

        # set check box for narrowing using word
        FrameCheckNarrow = tkinter.Frame(FrameNarrow, pady=10)
        FrameCheckNarrow.pack()
        self.VarNarrow = tkinter.BooleanVar()
        self.VarNarrow.set(False)

        CheckNarrow = tkinter.Checkbutton(FrameCheckNarrow, text="ワードによる絞込みをする。", variable=self.VarNarrow, command=self._check_narrow)
        CheckNarrow.pack()

        FrameEntryNarrow = tkinter.Frame(FrameNarrow, pady=0)
        FrameEntryNarrow.pack()

        self.EditBoxNarrow = tkinter.Entry(FrameEntryNarrow, width=30, state="disabled", background="#a0a0a0")
        self.EditBoxNarrow.pack()

    # if NOT windows pc, it will raise abortion trap.
    def _callback_output(self):
        self.VarSubCheckbox = []
        self.subroot = tkinter.Toplevel()
        self.subroot.title("選択ウィンドウ")
        self.subroot.geometry("400x600")

        self._frame_sub_cancel()
        self._frame_sub_radiobox()
        self._frame_sub_label()
        self._frame_sub_checkbox()
        self._frame_sub_execute()

        self.subroot.mainloop()

    def _frame_sub_cancel(self):
        FrameSubCancel = tkinter.Frame(self.subroot, pady=10)
        FrameSubCancel.pack()

        ButtonSubCancel = tkinter.Button(FrameSubCancel, font=("",14), text="キャンセル", command=self.subroot.destroy, width=40, height=2)
        ButtonSubCancel.pack()

    def _sub_change_state(self):
        checked = self.VarRadio.get()

        values = [1,2,3]
        values.remove(checked)

        for i in values:
            if checked == i:
                self.SubRadios[i].configure(state="disabled")

    def _frame_sub_radiobox(self):
        # set sub radiobox
        FrameSubRadio = tkinter.Frame(self.subroot, pady=10)
        FrameSubRadio.pack()

        # make the group of radio button
        self.VarRadio = tkinter.IntVar()
        self.VarRadio.set(0)

        texts = {
            1:"ブランド別に取得しない。",
            2:"ブランド別に取得し、全てのASINを取得する。",
            3:"ブランド別に取得するが、チェックボックスから選択する。"
        }

        SubRadio1 = tkinter.Radiobutton(FrameSubRadio, text=texts[1], variable=self.VarRadio, value=1, command=self._sub_change_state)
        SubRadio1.pack()
        SubRadio2 = tkinter.Radiobutton(FrameSubRadio, text=texts[2], variable=self.VarRadio, value=2, command=self._sub_change_state)
        SubRadio2.pack()
        SubRadio3 = tkinter.Radiobutton(FrameSubRadio, text=texts[3], variable=self.VarRadio, value=3, command=self._sub_change_state)
        SubRadio3.pack()

        self.SubRadios = {
            1:SubRadio1,
            2:SubRadio2,
            3:SubRadio3
        }

    def _frame_sub_label(self):
        # set sub label
        FrameSubLabel = tkinter.Frame(self.subroot, pady=10)
        FrameSubLabel.pack()

        # make label
        text = "選択する場合は、以下のチェックボックスから選択してください\nなお、選択されなかった場合、キャンセルします。　　　　　　"
        LabelSub = tkinter.Label(FrameSubLabel, font=("",10), text=text)
        LabelSub.pack()

    def _frame_sub_checkbox(self):
        # set sub checkbox
        FrameCheckbox = tkinter.Frame(self.subroot, pady=10)
        FrameCheckbox.pack()

        Scrollbar = tkinter.Scrollbar(FrameCheckbox, orient="vertical")
        Text = tkinter.Text(FrameCheckbox, yscrollcommand=Scrollbar.set, height=20)
        Scrollbar.config(command=Text.yview)
        Scrollbar.pack(side="right", fill="y")
        Text.pack(side="left", fill="both", expand=True)

        seller_id = self.Combo.get()
        
        url = "https://www.amazon.co.jp/gp/search/other?pickerToList=brandtextbin&me="+seller_id
        
        soup = get_soup(url)

        ul = soup.find("div", id="refinementList")
        if ul is None:
            lis = []
        else:
            lis = ul.find_all("li")

        brand_names = []

        for li in lis:
            brand_names.append(re.sub("\([0-9]+\)$", "", li.text))
            
        brand_names.sort()
        self.ExecuteFnames = brand_names

        self.VarSubCheckbox = ["" for i in range(len(self.ExecuteFnames))]
        # make checkbox
        for i in range(len(self.ExecuteFnames)):
            self.VarSubCheckbox[i] = tkinter.BooleanVar()
            self.VarSubCheckbox[i].set(False)

            Checkbutton = tkinter.Checkbutton(FrameCheckbox, text=self.ExecuteFnames[i], variable=self.VarSubCheckbox[i], bg="white")
            Text.window_create("end", window=Checkbutton)
            Text.insert("end", "\n")

    def _frame_sub_execute(self):
        FrameSubExecute = tkinter.Frame(self.subroot, pady=10)
        FrameSubExecute.pack()

        ButtonSubExecute = tkinter.Button(FrameSubExecute, font=("",14), text="選択して実行", command=self._execute, width=40, height=2)
        ButtonSubExecute.pack()

    def _execute(self):
        for i in range(len(self.VarSubCheckbox)):
            if self.VarSubCheckbox[i].get():
                self.EntryFnames.append(self.ExecuteFnames[i])
        seller_id = self.Combo.get()
        mode = self.VarRadio.get()
        fname = self.EditBoxOutput.get()
        word = self.EditBoxNarrow.get()
        self.subroot.destroy()
        
        print(self.EntryFnames, seller_id, mode, fname, word)
        if mode==2:
            aig = AmazonInfoGetter()
            aig.info(seller_id, fname, self.ExecuteFnames, word=word)

        elif mode==3:
            aig = AmazonInfoGetter()
            aig.info(seller_id, fname, self.EntryFnames, word=word)

        else:
            aig = AmazonInfoGetter()
            aig.info(seller_id, fname, self.ExecuteFnames, word=word)
        if self.VarAfterEnd.get():
            subprocess.Popen([r'C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE', fname])

        # to amazon

    def _frame_output(self):
        # set entry form for output folder
        text = "CSVの出力フォルダーを指定してください。"
        FrameOutput=tkinter.LabelFrame(self.root, text=text, labelanchor=tkinter.NW)
        FrameOutput.pack()

        self.EditBoxOutput = tkinter.Entry(FrameOutput, state="normal", width=25)
        self.EditBoxOutput.insert(tkinter.END, nowdir+"output.csv")
        self.EditBoxOutput.pack(side="left")
        ButtonOutput = tkinter.Button(FrameOutput, font=("",14), text="参照", command=self._ref)
        ButtonOutput.pack(side="right")
        
    def _ref(self):
        ftyp = [("","*")]
        idir = os.path.abspath(os.path.dirname(__file__))
        output_file = tkinter.filedialog.askopenfilename(filetypes=ftyp, initialdir=idir)
        
        if output_file != "":
            self.EditBoxOutput.delete(0, tkinter.END)
            self.EditBoxOutput.insert(tkinter.END, output_file)

    def _frame_save_property(self):
        FrameSaveProperty = tkinter.Frame(self.root, pady=10)
        FrameSaveProperty.pack()
        self.VarSaveProperty = tkinter.BooleanVar()
        self.VarSaveProperty.set(True)

        text = "実行時にデータの出力先や取得\n間隔のプロパティを保存する。"
        CheckSaveProperty = tkinter.Checkbutton(FrameSaveProperty, text=text, variable=self.VarSaveProperty)
        CheckSaveProperty.pack(side="left")

    def _frame_after_end(self):
        FrameAfterEnd = tkinter.Frame(self.root, pady=10)
        FrameAfterEnd.pack()
        self.VarAfterEnd = tkinter.BooleanVar()
        self.VarAfterEnd.set(True)

        text = "終了後自動で開く。　　　　　"
        self.CheckAfterEnd = tkinter.Checkbutton(FrameAfterEnd, text=text, variable=self.VarAfterEnd)
        self.CheckAfterEnd.pack(side="left")
        
    def _frame_get_button(self):
        FrameGetButton = tkinter.Frame(self.root, pady=10)
        FrameGetButton.pack()
        
        ButtonSubCancel = tkinter.Button(FrameGetButton, font=("",14), text="データ取得", width=10, height=1, command=self._callback_output)
        ButtonSubCancel.pack()


    def _frame_dialog(self):
        FrameDialog = tkinter.Frame(self.root, pady=50)
        FrameDialog.pack()

        text = "ダイアログを待機しています…"
        self.LabelDialog = tkinter.Label(FrameDialog, font=("",14), text=text)
        self.LabelDialog.pack(side="left")
        
def main():

    gui = GraphicUserInterface()
    #aig = AmazonInfoGetter()
    #target_seller = "A2F5KZFVL838MF"
    #aig.info(target_seller)

if __name__ == "__main__":
    main()
