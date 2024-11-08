options = webdriver.ChromeOptions()
options.add_argument("--headless")  

# Initialize the headless Chrome driver
driver = webdriver.Chrome(options=options)

details = []

for i in range(len(df)):
    curr_url = 'https://'+df['Link'][i]
    print('curr_url:', curr_url)
    driver.get(curr_url)
    
    data = {}
    
    try:
        email = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, ".//a[@class='email-business']"))
        ).get_attribute('href').split('mailto:')[1]
        data['email'] = email
    except (NoSuchElementException, TimeoutException, IndexError):
        data['email'] = ''
    
    try:
        regular_hours = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="aside-hours"]/dd/div/table'))
        ).text.replace('\n', ' | ')
        data['regular_hours'] = regular_hours
    except (NoSuchElementException, TimeoutException):
        data['regular_hours'] = ''
    
    try:
        claimed = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='claimed']"))
        ).text
        data['claimed'] = claimed
    except (NoSuchElementException, TimeoutException):
        data['claimed'] = 'Unclaimed'

    try:
        general_info = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='general-info']"))
        ).text
        data['general_info'] = general_info
    except (NoSuchElementException, TimeoutException):
        data['general_info'] = ''

    try:
        services_products = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='features-services']"))
        ).text
        data['services_products'] = services_products
    except (NoSuchElementException, TimeoutException):
        data['services_products'] = ''

    try:
        neighborhoods = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='neighborhoods']"))
        ).text
        data['neighborhoods'] = neighborhoods
    except (NoSuchElementException, TimeoutException):
        data['neighborhoods'] = ''

    try:
        amenities = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='amenities']"))
        ).text
        data['amenities'] = amenities
    except (NoSuchElementException, TimeoutException):
        data['amenities'] = ''

    try:
        languages = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='languages']"))
        ).text
        data['languages'] = languages
    except (NoSuchElementException, TimeoutException):
        data['languages'] = ''

    try:
        aka = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='aka']//p[1]"))
        ).text
        data['aka'] = aka
    except (NoSuchElementException, TimeoutException):
        data['aka'] = ''

    try:
        social_links = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='social-links']"))
        ).text
        data['social_links'] = social_links
    except (NoSuchElementException, TimeoutException):
        data['social_links'] = ''

    try:
        categories = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='categories']//div[@class='categories']"))
        ).text
        data['categories'] = categories
    except (NoSuchElementException, TimeoutException):
        data['categories'] = ''

    try:
        # Locate the <a> tag within the <h2> element with class 'section-title'
        section_title = driver.find_element(By.CLASS_NAME, 'section-title')
        link_element = section_title.find_element(By.TAG_NAME, 'a')
        href_value = link_element.get_attribute('href')
        data['photos_url'] = href_value
        # print('photos_url:', href_value)
    except (NoSuchElementException, TimeoutException):
        data['photos_url'] = 'NA'
        # print('photos_url: NA')
        
    try:
        other_info = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='other-information']"))
        ).text.replace('\n', ' | ')
        data['other_info'] = other_info
    except (NoSuchElementException, TimeoutException):
        data['other_info'] = ''

    try:
        other_links = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//dd[@class='weblinks']"))
        ).text.replace('\n', ' | ')
        data['other_links'] = other_links
    except (NoSuchElementException, TimeoutException):
        data['other_links'] = ''

    details.append(data)
    print(data)

driver.quit()
# print(details)