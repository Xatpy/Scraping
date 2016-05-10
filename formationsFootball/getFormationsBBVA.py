from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Match:
  date = ''
  competition = ''
  teams = ''
  local = True
  link = ''


def isLocalTeam(teams):
    defaultTeam = u'Atl\xe9tico'
    teamsArr = teams.split("-")
    return True if (teamsArr[0] == defaultTeam) else False

def getMatches():
    driver.implicitly_wait(5)
    driver.set_page_load_timeout(11)
    
    url = "http://www.marca.com/deporte/futbol/equipos/atletico/resultados-temporada.html"
    try:
        driver.get(url)
    except:
        print "Time out because of ads... but trying to go ahead!"

    table_id = driver.find_element_by_id('resultadosCompletos');
    rows = table_id.find_elements_by_tag_name("tr") # get all of the rows in the table
    for row in rows:
        # Get the columns (all the column 2)
        if row.get_attribute("class") == "encabezado":
            continue

        cols = row.find_elements_by_tag_name("td")

        match = Match()
        match.date = cols[0].text
        match.competition = cols[1].text
        match.teams = cols[2].text
        match.local = isLocalTeam(match.teams)
        match.link = cols[3].find_element_by_tag_name("a").get_attribute("href")

        listMatches.append(match)

    driver.quit()

def saveScreenshot(element, namePNG, driver):
    location = element.location
    size = element.size
    driver.save_screenshot(namePNG) # saves screenshot of entire page
    driver.quit()

    im = Image.open(namePNG) # uses PIL library to open image in memory

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    im = im.crop((left, top, right, bottom)) # defines crop points
    im.save(namePNG) # saves new cropped image

def getMatchInfo(match, current_match, raw):
    time.sleep(1)

    driver = webdriver.Firefox()
    driver.set_window_position(0,0)
    driver.delete_all_cookies()

    #url = "http://www.marca.com/eventos/marcador/futbol/2015_16/champions/semifinal/ida/atm_bay/"
    driver.get(match.link)

    time.sleep(10)

    if driver.find_element_by_xpath("//*[contains(text(), 'O. INICIALES')]"):
        oncesIniciales = driver.find_element_by_xpath("//*[contains(text(), 'O. INICIALES')]");

        if oncesIniciales:
            oncesIniciales.click()
            print "clicked onces iniciales"

            raw += match.teams + ","

            # Local team = lTeamAlign
            # Visitant team = vTeamAlign
            teamElement = "lTeamAlign" if (match.local) else "vTeamAlign"
            #atletiElem = driver.find_element_by_class_name("lTeamAlign");
            atletiElem = driver.find_elements_by_class_name("green")[0].find_element_by_class_name("iniciales").find_element_by_class_name(teamElement)

            alignmentText = None
            alineacionElem = "alignment" if (match.local) else "vAlignment"
            if atletiElem.find_element_by_class_name(alineacionElem):
                alignment = atletiElem.find_element_by_class_name(alineacionElem).text
                raw += alignment + ","

            lines = atletiElem.find_elements_by_class_name("plLine");
            for line in lines:
                players = line.find_elements_by_class_name("player");
                for player in players:
                    name = player.find_element_by_class_name("pl-name").text.encode("utf-8");
                    #print name
                    raw += name.encode('utf-8') + "\t"

            raw += "\n"
            saveScreenshot(atletiElem, str(current_match) + "_" + match.teams + ".png", driver);

            print raw

    #driver.quit()


if __name__ == "__main__":

    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.delete_all_cookies()

    raw = ""

    listMatches = []
    getMatches()
    i = 1
    for match in listMatches:
        current_match = len(listMatches) - i
        getMatchInfo(match, current_match, raw)
        i += 1
    print "end"

