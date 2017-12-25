import navegador5 as nv
import navegador5.url_tool as nvurl
import navegador5.head as nvhead
import navegador5.body as nvbody
import navegador5.cookie
import navegador5.cookie.cookie as nvcookie
import navegador5.cookie.rfc6265 as nvrfc6265
import navegador5.jq as nvjq
import navegador5.js_random as nvjr
import navegador5.file_toolset as nvft
import navegador5.shell_cmd as nvsh
import navegador5.html_tool as nvhtml
import navegador5.solicitud as nvsoli
import navegador5.content_parser
import navegador5.content_parser.amf0_decode as nvamf0
import navegador5.content_parser.amf3_decode as nvamf3

from lxml import etree
import lxml.html
import collections
import copy
import re
import urllib
import os
import json
import sys
import time

from xdict.jprint import  pdir
from xdict.jprint import  pobj
from xdict.jprint import  print_j_str
from xdict import cmdline
import hashlib
import xdict.utils


nudipix_base_url = 'http://www.nudipixel.net'
taxonomy_url = 'http://www.nudipixel.net/taxonomy/'

#taxonomy_init
def taxonomy_init(base_url='http://www.nudipixel.net/'):
    info_container = nvsoli.new_info_container()
    info_container['base_url'] = base_url
    info_container['method'] = 'GET'
    req_head_str = '''Accept: application/json\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36\r\nAccept-Encoding: gzip,deflate,sdch\r\nAccept-Language: en;q=1.0, zh-CN;q=0.8'''
    info_container['req_head'] = nvhead.build_headers_dict_from_str(req_head_str,'\r\n')
    info_container['req_head']['Connection'] = 'close'
    #### init records_container
    records_container = nvsoli.new_records_container()
    return((info_container,records_container))




def get_etree_root(info_container,**kwargs):
    if('coding' in kwargs):
        coding = kwargs['coding']
    else:
        coding = 'utf-8'
    html_text = info_container['resp_body_bytes'].decode(coding)
    root = etree.HTML(html_text)
    return(root)

#
#taxon_xpath = sys.argv[2]
#-taxon_xpath = '//div[@id="taxonomy"]/ul/ul/li/a[@href="/subclass/opisthobranchia/"]'


def get_sp_urls(taxonomy_url,taxon_xpath='//div[@id="taxonomy"]/ul/ul/li/a[@href="/subclass/opisthobranchia/"]'):
    info_container,records_container = taxonomy_init()
    info_container['url'] = taxonomy_url
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    info_container = nvsoli.auto_redireced(info_container,records_container)
    root = get_etree_root(info_container)
    eles_taxon = root.xpath(taxon_xpath)
    ul = eles_taxon[0].getparent().getnext()
    sps = ul.xpath('.//li/a')
    nsps = []
    sp_urls = []
    for i in range(0,sps.__len__()):
        sp = sps[i]
        if('species' in sp.attrib['href']):
            nsps.append(sp)
            sp_urls.append(nudipix_base_url + sp.attrib['href'])
    return(sp_urls)


def get_EXIF(EXIF_url):
    info_container,records_container = taxonomy_init()
    info_container['url'] = EXIF_url
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    info_container = nvsoli.auto_redireced(info_container,records_container)
    root = get_etree_root(info_container)
    eles = root.xpath('//table[@class="exif"]/tr')
    EXIF = {}
    for i in range(0,eles.__len__()):
        key = eles[i].xpath('td')[0].text.rstrip(':')
        EXIF[key] = eles[i].xpath('td')[1].text
    return(EXIF)


def init_KPCOFGS(rsltin='path',**kwargs):
    if('names' in kwargs):
        kpcofgs_names = kwargs['names']
    else:
        kpcofgs_names = ['Kingdom','Phylum','Class','Subclass','Infraclass','Order','Superfamily','Family','Genus','Species']
    pobj(kpcofgs_names)
    if(rsltin == 'path'):
        rslt = ''
        for i in range(1,kpcofgs_names.__len__()):
            rslt = rslt + '/' 
        return(rslt)      
    else:
        rslt = {}
        for each in kpcofgs_names:
            rslt[each] = ''
        return(rslt)


def get_KPCOFGS(tbodys,**kwargs):
    if('names' in kwargs):
        kpcofgs_name = kwargs['names']
    else:
        kpcofgs_names = ['Kingdom','Phylum','Class','Subclass','Infraclass','Order','Superfamily','Family','Genus','Species']    
    kpcofgs = tbodys[1].getchildren()
    ks = init_KPCOFGS(rsltin='dict',names=kpcofgs_names)
    for i in range(0,kpcofgs.__len__()):
        ks[kpcofgs[i].xpath('td')[0].text.rstrip(':')] = kpcofgs[i].xpath('td/a')[0].text
    if('rsltin' in kwargs):
        rsltin = kwargs['rsltin']
    else:
        rsltin = 'path'
    if(rsltin == 'path'):
        path = ks[kpcofgs_names[0]]
        for i in range(1,kpcofgs_names.__len__()):
            path = path + '/' + ks[kpcofgs_names[i]]
        return(path)  
    else:
        return(ks)


def get_img_info(ele,sp_name,base_url = nudipix_base_url):
    thumbnail_url = nudipix_base_url + ele.xpath('div/a/img')[0].attrib['src']
    img_url = nudipix_base_url + ele.xpath('div/a')[0].attrib['href']
    info_container,records_container = taxonomy_init()
    info_container['url'] = img_url
    ####
    print(img_url)
    ####
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    info_container = nvsoli.auto_redireced(info_container,records_container)
    img_root = get_etree_root(info_container)
    tbodys = img_root.xpath('//table')
    info_raw = tbodys[0].getchildren()
    info = {}
    for i in range(0,info_raw.__len__()):
        key = info_raw[i].xpath('td')[0].text.rstrip(':')
        if(key == 'Camera'):
            info[key] = info_raw[i].xpath('td')[1].text
            EXIF_url = nudipix_base_url + info_raw[i].xpath('td/span/a')[0].attrib['href']
            info['EXIF'] = get_EXIF(EXIF_url)
        elif(key == 'Taken on'):
            info[key] = info_raw[i].xpath('td')[1].text
        elif(key == 'Viewed'):
            info[key] = info_raw[i].xpath('td')[1].text
        elif(key == 'Posted'):
            info[key] = info_raw[i].xpath('td')[1].text
        elif(key == 'Updated'):
            info[key] = info_raw[i].xpath('td')[1].text
        else:
            info[key] = info_raw[i].xpath('td/a')[0].text
    kpcofgs = get_KPCOFGS(tbodys,rsltin='dict')
    info['kpcofgs'] = kpcofgs
    img_real_url = nudipix_base_url + img_root.xpath('//div/img')[0].attrib['src']
    try:
        img_verifier = img_root.xpath('//div/img')[1].attrib['title']
    except:
        img_verifier = ''
    else:
        pass
    sha1 = hashlib.sha1(img_real_url.encode('utf-8')).hexdigest()
    img_suffix = os.path.basename(img_real_url).split('.')[-1]
    img_name = sp_name + '_' + sha1 + '.' + img_suffix
    thumbnail_suffix = os.path.basename(thumbnail_url).split('.')[-1]
    thumbnail_name = sp_name + '_' + sha1 + '.thumbnail.' + thumbnail_suffix
    info_name = sp_name + '_' + sha1 + '.dict'
    info['img_url'] = img_real_url
    info['verifier'] =  img_verifier
    info['img_name'] = '../Images/' + img_name
    info['index'] = sha1
    info['thumbnail_url'] = thumbnail_url
    info['thumbnail_name'] = '../Thumbs/' + thumbnail_name
    info['info_name'] = '../Infos/' + info_name
    return(info)



#####################

try:
    content = nvft.read_file_content(fn = '../seq.record',op='r')
except:
    istart = 0
    jstart = 0
    kstart = 0
else:
    istart = json.loads(content)['istart']
    jstart = json.loads(content)['jstart']
    kstart = json.loads(content)['kstart']


info_container,records_container = taxonomy_init()
info_container['url'] = taxonomy_url
info_container = nvsoli.walkon(info_container,records_container=records_container)
info_container = nvsoli.auto_redireced(info_container,records_container)
sp_urls = get_sp_urls(taxonomy_url) 
#http://www.nudipixel.net/species/philinopsis_gardineri/


#####
sys.stdout.flush()
print(sp_urls.__len__())
sys.stdout.flush()
##### 
for i in range(istart,sp_urls.__len__()):
    info_container,records_container = taxonomy_init()
    info_container['url'] = sp_urls[i]
    ####
    sys.stdout.flush()
    print(sp_urls[i])
    sys.stdout.flush()
    print(i)
    sys.stdout.flush()
    ####
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    info_container = nvsoli.auto_redireced(info_container,records_container)
    root = get_etree_root(info_container)
    eles = root.xpath('//div[@class="thumbnail"]')
    eleses = []
    eleses.append(eles)
    sp_name = os.path.basename(sp_urls[i].rstrip('/')).replace('_',' ')
    pages = root.xpath('//p[@class="nav"]/a')
    for j in range(0,pages.__len__()):
        page_url = nudipix_base_url + pages[j].attrib['href']
        info_container,records_container = taxonomy_init()
        info_container['url'] = page_url
        info_container = nvsoli.walkon(info_container,records_container=records_container)
        info_container = nvsoli.auto_redireced(info_container,records_container)
        root = get_etree_root(info_container)
        eles = root.xpath('//div[@class="thumbnail"]')
        eleses.append(eles)
    ####
    for j in range(jstart,eleses.__len__()):
        ####
        sys.stdout.flush()
        print(j)
        sys.stdout.flush()
        ####
        eles = eleses[j]
    ####
        for k in range(kstart,eles.__len__()):
            ####
            sys.stdout.flush()
            print(k)
            sys.stdout.flush()
            ####
            ele = eles[k]
            if('photo' in ele.xpath('div/a')[0].attrib['href']):
                info = get_img_info(ele,sp_name,base_url = nudipix_base_url)
                nvft.write_to_file(fn=info['info_name'],content=json.dumps(info),op='w+')
                info_container,records_container = taxonomy_init()
                info_container['url'] = info['img_url']
                info_container = nvsoli.walkon(info_container,records_container=records_container)
                info_container = nvsoli.auto_redireced(info_container,records_container)
                nvft.write_to_file(fn=info['img_name'],content=info_container['resp_body_bytes'],op='wb+')
                info_container,records_container = taxonomy_init()
                info_container['url'] = info['thumbnail_url']
                info_container = nvsoli.walkon(info_container,records_container=records_container)
                info_container = nvsoli.auto_redireced(info_container,records_container)
                nvft.write_to_file(fn=info['thumbnail_name'],content=info_container['resp_body_bytes'],op='wb+')
            else:
                pass
            nvft.write_to_file(fn='../seq.record',content=json.dumps({'istart':i,'jstart':j,'kstart':k}),op='w+')
            





