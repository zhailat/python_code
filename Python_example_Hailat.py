#!/usr/bin/env python
##-----------------------------------------------
# This code Implements the following task:
##-----------------------------------------------
#
# Web scraping
# ASNs (Autonomous System Numbers) are one of the building blocks of the
# Internet. This project is to create a mapping from each ASN in use to the
# company that owns it. For example, ASN 36375 is used by the University of
# Michigan - http://bgp.he.net/AS36375
# 
# The site http://bgp.he.net/ has lots of useful information about ASNs. 
# Starting at http://bgp.he.net/report/world crawl and scrape the linked country
# reports to make a structure mapping each ASN to info about that ASN.
# Sample structure:
#   {3320: {'Country': 'DE',
#     'Name': 'Deutsche Telekom AG',
#     'Routes v4': 13547,
#     'Routes v6': 268},
#    36375: {'Country': 'US',
#     'Name': 'University of Michigan',
#     'Routes v4': 14,
#     'Routes v6': 1}}
#
# The output will collect data to a json file.
#
##-----------------------------------------------
#     Dec 9, 2017: Developed by Zeyad Hailat
#     XXXX  ?, ????: Revision 1. by 
##-----------------------------------------------
##-----------------------------------------------
# All used packages and libraries.
# Before running the code, make sure all of the following packages are installed.
# Get beautifulsoup4 with: pip install beautifulsoup4
##-----------------------------------------------
import urllib2
import bs4
import re
import json
import time
##-----------------------------------------------
##----------------------------------------------- 
#  url_to_soup
# 		A function to fetch and parse a page.
# 		Return soup.
#  Parameters:
#		url: string, a webpage url.
##-----------------------------------------------
def url_to_soup(url):
    try:
        req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
        html = urllib2.urlopen(req).read()
        soup = bs4.BeautifulSoup(html)
        return soup
    except ValueError:
        print ('ERROR 03: cannot open URL ' + url)
##-----------------------------------------------
##----------------------------------------------- 
#  find_all_countries_recursively
#		Finds the webpage for each country
#		A recursive version of the method 'find_all_countries' to find all countries, in case you expect to have nested countries (nested pages.)
#		This use of this method may slow down the system as it double checks all pages.
#		Returns the list of webpages in a local_countries_list dictionary.
#  Parameters:
#		countries_webpage: string, the page that includes links to all of the countries webpages.
# 		main_website: string, the root website URL.
#  		visited_links: dictionary, keeps the visited links to avoid duplication. Avoid infinite loop: To make sure that one page is not visited for more than once.
#		local_countries_list: dictionary, keeps the list of countries.
#  Others:
# 		The first if-structure is to avoid following any external link.
# 		We regExpression '^/country/??' to make sure that the link starts with /country/ then two characters e.g., /country/US
# 		Verify that the country is not added twice by using a dictionary. local_countries_list is dictionary to make lookup faster.
##-----------------------------------------------
def find_all_countries_recursively(countries_webpage, main_website, visited_links={}, local_countries_list={}):
    if not str.startswith(countries_webpage, 'http://bgp.he.net'):
        return local_countries_list
        
    if countries_webpage in visited_links:
        return local_countries_list        
    else:
        visited_links[countries_webpage]=1
        
    soup = url_to_soup(countries_webpage )
    for link in soup.find_all('a'):
        href_txt = link.get('href').lower()
        country_url = main_website + href_txt
        if re.match('^/country/??', href_txt):            
            if country_url not in local_countries_list:
                local_countries_list[country_url]=1
                find_all_countries_recursively(main_website + href_txt, main_website,visited_links,  local_countries_list)
            #else:
            #    print ('ERROR 05: DUPLICATION ' + country_url + '. The URL already exists in the list.')
##----------------------------------------------- 
##----------------------------------------------- 
#  find_all_countries
#		Finds the webpage for each country
#		Returns the list of webpages in a local_countries_list dictionary.
#		local_countries_list dictionary is used to facilitate direct access when check for duplication, it is faster than regular list.
#  Parameters:
#		countries_webpage: string, the page that includes links to all of the countries webpages.
# 		main_website: string, the root website URL.
#  Others:
# 		The first if-structure is to avoid following any external link.
# 		We regExpression '^/country/??' to make sure that the link starts with /country/ then two characters e.g., /country/US
# 		Verify that the country is not added twice by using a dictionary. local_countries_list is dictionary to make lookup faster.
##----------------------------------------------- 
def find_all_countries(countries_webpage, main_website): 
    local_countries_list = {}
    if not str.startswith(countries_webpage, 'http://bgp.he.net'):
        print('WARNING 01: This is an external link. It will not be followed.')
        return local_countries_list
    soup = url_to_soup(countries_webpage)
    for link in soup.find_all('a'):
        href_txt = link.get('href').lower()
        if re.match('^/country/??', href_txt):
            country_url = main_website + href_txt
            if country_url not in local_countries_list:
                local_countries_list[country_url]=1                
            else:
                print ('ERROR 02: DUPLICATION ' + country_url + '. The URL already exists in the list.')
        #else: Not valid link.
        #    print('NONE.1 ' + href_txt)
            #if not str.startswith(href_txt, 'http'):
            #    return find_all_countries(main_website + href_txt, main_website)    
    return local_countries_list  
##----------------------------------------------- 
##----------------------------------------------- 
#  get_ASN_mapping 
#		Parse every country webpage and get a JSON object with a structural mapping for each ASN to info 
#		Returns the output_dict, a dictionary containing all countries ASN info.
#  Parameters:
#		country_webpage: string, the country webpage full URL
#		min_no_cols: integer, the minimum number of columns in the ASN table.
#  Others:
# 		The regular expression to make sure that the webpage link ends with two letters (e.g., ..../US).
#		country_name: Substring that extract last two letters in the URL as country_name (e.g., US)
##-----------------------------------------------
def get_ASN_mapping(country_webpage, min_no_cols):
    output_dict={}
    if re.match('.*\w{2}$', country_webpage):
		print('Processing ' + country_webpage + ' ...')
		soup = url_to_soup(country_webpage)
		country_name = country_webpage[len(country_webpage)-2:]
		output_dict = get_JSON_object(soup, country_name, min_no_cols)
    else:
		print('ERROR 01: ' + country_webpage + ' is not a valid country page.')
    return output_dict
##-----------------------------------------------
##----------------------------------------------- 
#  get_JSON_object 
#       Parse the HTML soup object and get the basic information for each country and then save it to the dictionary output_dict.
#       Returns the basic information for the countries in the output_dict  dictionary.
#  Parameters:
#       soup: object with all page HTML code.
#       country_name: country name to be added to country tuple.
#		min_no_cols: integer, the minimum number of columns in the ASN table.
#  Others:
# 		The page is structured in table. This code divides the HTML code into table rows and then identify all columns in each row.
##-----------------------------------------------
def get_JSON_object(soup, country_name, min_no_cols):    
    output_dict={}
    trs = soup.find_all('tr')
    for tr in trs:
        tds =tr.find_all('td')
        # make sure it is full row with 6 or more cells.
        if len(tds) >= min_no_cols :   
            output_dict[tds[0].getText() [2:]] = {"Country":  country_name.upper(), \
            "Name" : tds[1].getText(), \
            "Routes v4" : tds[3].getText(),\
            "Routes v6":  tds[5].getText()}
    return output_dict
##-----------------------------------------------
##----------------------------------------------- 
#   write_JSON_file_to_disk
#       Writes the results into a JSON file.
#   Parameters:
#       output_JSON_file_name: string, the full output file name with path.
#       output_dict: dictionary, all countries information.
##-----------------------------------------------
def write_JSON_file_to_disk(output_JSON_file_name, output_dict):
	try:
		with open(output_JSON_file_name, 'w') as outfile:
			json.dump(output_dict, outfile)
	except ValueError:
		print ('ERROR 04: cannot write the Json file: ' + output_JSON_file_name + 
        '. please verify that the file name and path are correct, your program has write permission, or the disk is not full.')
##-----------------------------------------------
##----------------------------------------------- 
#  main
# 		The main method of the system. It calls other methods.
#  Parameters:
#      website_url: string, a URL which contains the root of the website address.
#      output_JSON_file_name: string, the output file, JSON format. Make sure to specify output file name and 
#				full path, otherwise it will be save in the local directory by defauls.
#	   recursive: boolean, if you want to search all pages in the website recursively. It might be slow.
#				TRUE - recursive function that finds all subpages. Slow because it will parse all webpages.
#				FALSE - it follows only the provided link and then extract all data.
#		min_no_cols: integer, the minimum number of columns in the ASN table.
##-----------------------------------------------
def main(website_url, output_JSON_file_name='ASN_data_Json.txt', recursive= False, min_no_cols=6):    
	countries_list = {}
	if recursive:
		print ('WARNING 02: The recursive version of the application is running!\nThis may slow down the application.')
		visited_links = {}
		#countries_list2= {}
		find_all_countries_recursively(website_url + '/report/world', website_url, visited_links, countries_list)
	else:
		countries_list = find_all_countries(website_url + '/report/world', website_url)
	
	output_dict= {}
	for country_link in countries_list:
		output_dict = get_ASN_mapping(country_link, min_no_cols)
    
	write_JSON_file_to_disk(output_JSON_file_name, output_dict)
	
	print ('Countries with ASNs: ' + str(len(countries_list)))
	print ('Processing is done, please check outputfile ... ' + output_JSON_file_name)
##-----------------------------------------------
##----------------------------------------------- 
# The execution of the system starts here starts here.
# Set the following variables before you run the code:
#	website_root_url: string, the url to the website. E.g., 'http://bgp.he.net'
#	output_json_file: string, the output JSON file name with a full path where you want to save the file. E.g., '/Users/Zeyad/Documents/ASN_data_Json.txt'
#                     use the file name only without the full path to save the file in the local directory.
#   recursive: boolean, if you want to search all pages in the website recursively. It might be slow.
#	min_no_cols: integer, the minimum number of columns in the ASN table.
##-----------------------------------------------
if __name__ == "__main__":
	timeStr = time.strftime("%Y-%m-%d_%H-%M-%S")
	output_json_file = 'ASN_data_Json_' + timeStr + '.txt'
	website_root_url = 'http://bgp.he.net'	
	recursive = False
	min_no_cols = 6
	main(website_root_url, output_json_file, recursive, min_no_cols)
