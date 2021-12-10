import os, readchar
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import argparse 
from lxml import html
#from IPython import embed

CONTROL_XPATH = "//h1" 
CONST_PROFILE = '/home/pp/.mozilla/firefox/g2gf3r19.selen'
CONST_DRIVER =  r'/home/pp/Projects/geckodriver'
CONST_DELIMITER = '/'

def initDriver():
    print('Starting Firefox with Selenium...')
    myprofile = webdriver.FirefoxProfile(CONST_PROFILE)
    driver = webdriver.Firefox(firefox_profile=myprofile, executable_path=CONST_DRIVER)    
    driver.set_window_size(800, 600)
    driver.set_window_position(0, 0)
    return driver
 
def initParser():
    parser = argparse.ArgumentParser(description='Saves the full DOM of all URLs listed in the input file to the specified output directory as HTML files.', epilog= 'Finished HTML files will be named with a serial number. For example: 01.html, 02.html, 03.html, ... 09.htm, 10.html. Or: 0001.html, 0002.html, ... 1234.html. The serial number is the same as the position in the list file.') 
    parser.add_argument("list", help="List file name that contains url-s. – For input.")
    parser.add_argument("dir", default='', help="Output directory where the htlm-s will saved with full DOM.")
    parser.add_argument("--resume", "-r", action='store_true', help="Resume an aborted processing.")        
    parser.add_argument("--xpath", "-x", help="Control XPATH. If it does not exist in the HTML tree, it beeps.")  
    return parser    
    
class pgClass:   # for testing without selenium 
    def get(self, url):
        self.content = self.url = url
        
class pagerClass(pgClass):
    def __init__(self):
        self.drv = initDriver()
    def get(self, url):
        super().get(url)
        self.drv.get(self.url)
        ss = '<!DOCTYPE html>\n' + self.drv.execute_script("return document.documentElement.outerHTML")
        root = html.fromstring(ss)
        #embed()
        if len(root.xpath(CONTROL_XPATH)) == 0:
            os.system("beep -f 555 -l 1600") # Linux only, beep sys func must be installend. Like: apt get install beep   
        self.content = ss
        
def skipCalc(thedir):
    lsd = os.listdir(thedir)
    maxi = int(max(lsd)[:-5])  # 5 == len('.html')
    if maxi != len(lsd):
        print('Warning! The number of files does not match the maximum serial number.')
    return maxi
    
#main('quotes.urls', 'ddd')      # for testing without selenium 
def main(listFile, outDir, pager = pgClass(), skip=0):
    with open(listFile) as f:
        urls = f.readlines()
    frms = outDir + CONST_DELIMITER + '{:0' + str(len(str(len(urls)))) +'d}.html'
    i = 1
    for url in urls:
        if i <= skip:
            i += 1
            continue
            
        pager.get(url)
        
        while True:
            print("Save & next <Enter>, sKip, Quit: ", end='', flush=True)
            c = readchar.readchar()
            if c.upper() in 'KQ':
                print(c)
                break
            elif c == '\r':
                print('Enter')
                break
            else:
                print('\n')
        
        if c == '\r': # Enter            
            with open(frms.format(i), 'x') as f:
                f.write(pager.content)
                print(frms.format(i) + ' saved.')            
        elif c.upper() == 'K':
            print('{:d}. skipped...'.format(i))
        elif c.upper() == 'Q':
            print('I interrupt processing. You can continue later with the -r option.')            
            break        
        i += 1

if __name__ == '__main__':
    parser = initParser()
    args = parser.parse_args()
    if args.list:
        try:
            if args.xpath:
                CONTROL_XPATH = args.xpath
            pager = pagerClass() 
            # pager = pgClass() # for testing without Selenium
            if args.resume:
                skip=skipCalc(args.dir)
                print('I will continue processing from page {}...'.format(skip+1))
                main(args.list, args.dir, pager, skip)
            else:
                main(args.list, args.dir, pager)
            
        finally: 
            print("I'm closing things...")
            pager.drv.quit()
            del pager


            
