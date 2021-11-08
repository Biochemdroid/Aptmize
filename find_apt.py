#Notes:

### After getting every possible sequence:
#### -Run through quickfold and extract lowest energy sequences
#### -Then manually go through and start cutting out extraneous seqeuences
#### -Rerun and take lowest energy again.

## Must use Chrome for this set up! 
### Go to: https://chromedriver.chromium.org/downloads and download correct v. of chromedriver.
### Import that .exe file into path
### pip install selenium
#### Download Selectors hub to get CSS of submit button.


#Import modules:

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import requests
from bs4 import BeautifulSoup
import warnings




from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless")
chrome_options.headless = True # also works




pd.set_option('display.max_colwidth',1)

#Annoying, got rid of error message.
warnings.filterwarnings("ignore", category=DeprecationWarning) 


aptamerset = pd.read_excel('aptamer_examples.xlsx', sheet_name=0)

aptamerset = aptamerset[['Unnamed: 1','Unnamed: 2']]
aptamerset.rename(columns = {'Unnamed: 1':'apt_num', 'Unnamed: 2':'sequence'}, inplace = True)

seq = aptamerset['sequence']
n = 0

#Here is where all the aptamer possibilities will be stored:
aptamers = {}

for line in seq:
    line = seq[n]
    n += 1
    
    apt_number = [str(seq[n-1])]
    for base_pair in range(len(seq[0])):


        if line[base_pair] != 'A' and line[base_pair] != 'G' and line[base_pair] != 'C' and line[base_pair] != 'T':

        

            #X could be any base pair
            if line[base_pair] == 'X':
                _list = []
                for possibility in apt_number:

                    _list.append(possibility[0:base_pair] + 'A' + possibility[base_pair + 1:])
                    _list.append(possibility[0:base_pair] + 'G' + possibility[base_pair + 1:])
                    _list.append(possibility[0:base_pair] + 'T' + possibility[base_pair + 1:])
                    _list.append(possibility[0:base_pair] + 'C' + possibility[base_pair + 1:])
                for apt in _list:
                        apt_number.append(apt)
            else:
                raise ('Base pair not expected!')

    bp_remove = []
    for nuc in range(len(apt_number)):

        if 'X' in apt_number[nuc]:
            bp_remove.append(apt_number[nuc])
        elif 'Y' in apt_number[nuc]:
            bp_remove.append(apt_number[nuc])
       
        else:
            pass        


    for line in bp_remove:
        apt_number.remove(str(line))


    print(range(len(apt_number)))

    aptamers['Sequence_{}'.format(n)] = apt_number
#Note: range = number of possibilities for sequences 1,2,etc.


# Total Number of aptamer sequences:
num = 0
for i in aptamers:
    num = num + len(aptamers[i])
print(num)

### Save every possible aptamer solution to .txt file:
with open('possible_apt.txt', 'w') as possibility:
    for i in aptamers:
        possibility.write(str(i) + '\n')
        for apt in aptamers[i]:
            possibility.write(apt)
            possibility.write('\n')

 ## Code below tests every possible aptamer solution and returns the ΔG:

delta_g_apt = {}


from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


n = -1

for apt in aptamers.values():
    n += 1
    
    inter_dict = {}
    
    index = -1
    for nuc_seq in apt:
        
        index += 1
        
        #set chromodriver.exe path

        #Note: Comment out below unless running on terminal. Normally use executable_path instead.
        driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Chrome(executable_path="chromedriver.exe")

        driver.implicitly_wait(0.5)

        #launch URL
        driver.get("http://www.unafold.org/Dinamelt/applications/quickfold.php")

        #identify text box
        seq = driver.find_element_by_class_name("mfold")
        # #send input
        seq.send_keys(nuc_seq)

        #Change temp to 20 C
        temp = driver.find_element_by_id("temp")
        temp.clear()
        temp.send_keys(20)

        #Change sodium conc. to 0.15 M
        Na = driver.find_element_by_id("Sodium")
        Na.clear()
        Na.send_keys(0.15)

        #Change [Mg] to 0.005 M
        Mg = driver.find_element_by_id("Magnesium")
        Mg.clear()
        Mg.send_keys(0.005)

        #Change suboptimal to 50%:
        optimal = driver.find_element_by_id("p")
        optimal.clear()
        optimal.send_keys(50)

        #Server Break
        time.sleep(2)

        driver.find_element_by_css_selector("input[value='Submit']").click()

        new_url = driver.current_url
        page = requests.get(new_url)
        page

        page.content

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page.content, 'html.parser')
        
        delt_G = []

        lowest_E = soup.find_all('p')[1].get_text().split(',')[4].split(':')[0]
        sep_three = 0
        sep_three = [lowest_E.split('\n')]

        delta_G = [float(sep_three[n][4].split('=')[1][1:]) for n in range(len(sep_three))]
        _list.append(delta_G)

        driver.quit()
        
        #To not crash the server:
        time.sleep(6)

        inter_dict['{}'.format(index)] = delta_G
        
    delta_g_apt["{}".format(list(aptamers.keys())[n])] = inter_dict
    
    
with open('Delta_G_list.txt', 'w') as final:
    final.write(str(delta_g_apt))
    
delta_g_apt

#Orders the best thermodynamic number with its respective sequence:
combine_seq_G = []
n = -1

for seq in delta_g_apt:
    
    n+=1
    
    sort_orders = sorted(delta_g_apt[seq].items(), key=lambda aptamer: aptamer[1], reverse=False)
    
    inter = -1
    for i in sort_orders:
        inter += 1
        indexing = (sort_orders[inter][0])
        
        combine_seq_G.append((list(aptamers.values())[n][int(indexing)], sort_orders[inter][1]))

final_guess = []

def sorts(combine_seq_G): 
    combine_seq_G.sort(key = lambda x: x[1]) 
    return combine_seq_G 

sorts(combine_seq_G)

for num in range(10):
    final_guess.append(combine_seq_G[num])
        
        
### Write final output of the 10 most thermodyamically favorable sequences to work with those
with open('final_optimized_apt.txt', 'w') as final:
    for a in final_guess:
        final.write(str(a) + '\n')

