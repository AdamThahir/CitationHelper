import json
import regex
import time

from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

INITIAL = True # Initially, should load scholar.google.com
LOST = False   # Incase we get lost. Load scholar.google.com

LIMIT = 3

def FindSingleCitation (driver, citeType='bibtex'):
    # pass
    print (f'Getting all links...')
    allLinks = driver.find_elements (by=By.TAG_NAME, value='a')
    
    print (f'Iterating through found link elements to find Bibtex...')
    for link in allLinks:
        if link.text.lower() == 'bibtex':
            link.click ()
            break

    print (f'Link clicked. Extracing BibTeX')
    context = driver.find_element (by=By.TAG_NAME, value='pre')
    citation = context.text

    return citation

def openCitationReferences (sectionElement, citationIndex=1):
    status = False

    try:
        svgTags = sectionElement.find_elements (by=By.TAG_NAME, value='svg')
        svgTags[citationIndex].click()
        status = True
    except Exception as err:
        print (f'Could not find SVG element.')
        print (f'[ERR] \n{err}')
        status = False

    return status

def SearchCitation (driver, searchContent):
    global INITIAL, LOST
    if INITIAL or LOST:
        driver.get("https://scholar.google.com/")
        INITIAL = False
        LOST    = False
        
    status = False
    bodySection = None

    try:
        searchElement = driver.find_element(by=By.NAME, value='q')
        searchElement.send_keys(searchContent)
        searchElement.send_keys(Keys.RETURN)
        status = True
    except Exception as err:
        print (f'Could not find search bar.')
        print (f'[ERR] \n{err}')
        status = False
    else:
        time.sleep (5) ## TODO -- Remove. Rather make selenium wait.
        bodySection = driver.find_element(By.ID, 'gs_bdy_ccl')

    return status, bodySection

if __name__ == '__main__':
    # REGEX to find all characters we need. Seperate find by citation
    singleStringExpression = r"(?<=\[.\])(.*?)(?=(\[)|$)"

    # Extract lines. Copy paste from Paper
    with open ('citations.txt', 'r') as f:
        lines = f.readlines ()

    # Converts multi-line entry of citations into a single line. 
    # Basically parsing for the above tested REGEX to work
    singleLine = " ".join ([val.replace('\n', ' ') for val in lines])

    allMatches = regex.findall (singleStringExpression, singleLine)

    localCitations = []

    LIMIT = len (allMatches) if LIMIT == None else LIMIT

    ## Define Selenium driver
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    driver.maximize_window()
    ##

    # Do the work, for each match
    for index, match in tqdm (enumerate (allMatches), total=LIMIT):
        if index >= LIMIT:
            break
        
        # Search the given matched string (citation)
        ## Oh no, GoLang is leaking.
        isValid, section = SearchCitation (driver, match)
        if not isValid:
            LOST = True
            continue
        
        # If it's valid, click on the very first 'Cite' to open the modal
        isValid = openCitationReferences (section)
        if not isValid:
            LOST = True
            continue
        
        citation = FindSingleCitation (driver)
        localCitations.append (citation)
    
    print (f'all done. Final index: {index} | limit: {"None" if LIMIT == None else LIMIT}')
    print (f'found citations/matches. [{len(localCitations)}/{len(allMatches)}]')


        

